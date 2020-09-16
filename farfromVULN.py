import logging
import argparse
import sys
import tqdm
from termcolor import colored
from python_terraform import *
from os import listdir
from os import remove
from jinja2 import *
import boto3
import time
import shutil
import paramiko
import scp
import json


logging.basicConfig(level=logging.DEBUG)
logging.disable()

# function to handle any AMI requests
def interact_amis():
    ec2_client = get_ec2_client()

    logging.debug('Destroy AMi')

    flag = True
    while flag is True:
        amis_dict = get_self_ami_dictionary(ec2_client)        
        print('Would you like to destroy any AMIs? (y/n)')
        user_input = input('> ')

        if user_input == 'n':
            exit(0)
        elif user_input == 'y':
            print('Which AMI would you like to destroy?')

            # error handle for non-number input
            try:
                user_input = int(input('> '))
            except ValueError:
                print('Please select a valid number')
                continue

            # error handle for invalid AMI number
            try:
                # get the AMI ID to deregister
                deregister_ami_id = amis_dict['Images'][user_input-1]['ImageId']
            except IndexError:
                print('Invalid AMI!')
                continue

            # safely find the correct index of Ebs
            BlockDeviceMappings = amis_dict['Images'][user_input-1]['BlockDeviceMappings']
            for dict in BlockDeviceMappings:
                if dict.get('Ebs') is not None:
                    ebs_dict = dict.get('Ebs')
                    # get the snapshot block to destroy
                    snapshot_id = ebs_dict.get('SnapshotId')
                
                    # deregister the AMI ID and destroy the snapshot
                    ec2_client.deregister_image(ImageId=deregister_ami_id)
                    ec2_client.delete_snapshot(SnapshotId=snapshot_id)

                    # TODO: confirm deletion completion
                    print('AMI and associated snapshot have been deleted')
        else:
            print('Please choose either "y" or "n"')
                

# function that creates a dictionary of AMIs the profile owns
# ands prints out the available AMIs
def get_self_ami_dictionary(ec2_client):
    # first list the AMIs that you own
    amis_dict = ec2_client.describe_images(Owners=['self'])
    print('='*10)

    # check if the dictionary is empty
    if len(amis_dict['Images']) == 0:
        print('No AMIs found!')
        print('='*10)        
    
    counter = 1
    for ami in amis_dict['Images']:
        print('%s.' % counter)                            
        try:
            # parse through and find the name tag
            for dict in ami['Tags']:
                if dict.get('Key') == 'Name':
                    print('Name: %s' % dict.get('Value'))
                    print('AMI ID: %s' % ami['ImageId'])
                    print('='*10)
        except KeyError:
            print('No name tagged')
            print('AMI ID: %s' % ami['ImageId'])
            print('='*10)
        counter += 1

    return amis_dict

# function that handles the main deployment options
def deploy(terraform, cloud_name):
    # create a session to be used during deployment commands
    profile = set_aws_profile()
    session = boto3.session.Session(profile_name=profile)    

    flag = True
    while flag is True:
        # print a welcome banner
        print('='*50)
        print('DEPLOYMENT COMMANDS')
        print('='*50)
        
        # List available vulnerable machines
        mylist = []
        found_flag = False
        counter = 1

        # List of additional options outside of available machines
        additional_options = ['Import local machine image to AWS S3 bucket',
                              'Build an AMI from a machine image in a AWS S3 bucket',
                              'Use previously uploaded AMI from AWS to build a Terraform file',
                              'View Terraform files ready for deployment in the cloud',
                              'Deploy the cloud with created Terraform files',
                              'Quit']

        for option in additional_options:
            print('%s. %s' % (counter, option))
            mylist.append((counter, option))
            counter += 1

        # Get user choice
        try:
            user_input = int(input('Select a choice: '))
        except ValueError:
            print('Please enter a number')
            continue

        # Get the file that will be used from the list of options
        for pair in mylist:
            logging.debug(pair[0])
            if user_input == pair[0]:
                user_input = pair[1]
                found_flag = True
                break

        # Check if a valid option
        if found_flag is False:
            print('Please try a different option')
            break

        # Execute option
        if 'local' in user_input:
            import_local_vulnhub(session)
        elif 'Build' in user_input:
            import_s3_vulnhub(cloud_name, session)
        elif 'previously' in user_input:
            import_ami_image(cloud_name, session)
        elif 'View' in user_input:
            view_terraform_files(cloud_name)
        elif 'Deploy' in user_input:
            deploy_terraform_files(cloud_name, terraform, session)            
        elif 'Quit' in user_input:
            flag = False
        else:
            import_vuln_template(terraform, cloud_name, user_input)

# function that sets the private and public key to be used
# for Terraform deployment
def set_labs_keys():
    # if environment variable is available, use that value
    env_priv_key = os.environ.get('FFV_PRIV_KEY')
    env_pub_key = os.environ.get('FFV_PUB_KEY')

    # otherwise get the path from the user
    if env_priv_key is None:
        print('What is the path to the private key to use with this labs?')
        priv_key = input('> ')
    else:
        priv_key = env_priv_key

    if env_pub_key is None:
        print('What is the path to the public key to use with this labs?')
        pub_key = input('> ')
    else:
        pub_key = env_pub_key
        
    return priv_key, pub_key
    
# this function uses Terraform apply as well as starts the
# Flask web app
def deploy_terraform_files(cloud_name, terraform, session):
    # TODO: add region var to template
    env_dictionary = {'cloud_name' : cloud_name}
    broad_render_template(cloud_name, 'env.template', env_dictionary)

    # render main Terraform file
    main_dictionary = {'cloud_name' : cloud_name}
    broad_render_template(cloud_name, 'main.template', main_dictionary)

    # render provider Terraform file
    provider_dictionary = {'region' : session.region_name}
    broad_render_template(cloud_name, 'provider.template', provider_dictionary)

    # render vars template
    priv_key, pub_key = set_labs_keys()
    vars_dictionary = {'priv_key' : priv_key, 'pub_key' : pub_key}
    broad_render_template(cloud_name, 'vars.template', vars_dictionary)

    # render VPN template
    vpn_dictionary = {'cloud_name' : cloud_name}
    broad_render_template(cloud_name, 'vpn.template', vpn_dictionary)

    # now apply!
    return_code, stdout, stderr = terraform.apply(capture_output=False, no_color=None)

    # check for error and exit if occurred
    if return_code != 0:
        print('TERRAFORM APPLY FAILED')
        print(stderr)
        exit(1)

    # run post-apply commands!
    # output() returns a dictionary
    instance_ips = terraform.output()

    # write the instance IPs to a file for transfer
    with open('instance_ips.txt', 'w') as ip_txt:
        json.dump(instance_ips, ip_txt)
        ip_txt.close()

    vpn_ip = instance_ips.get('PiVPN').get('value')
    
    # get the lab private ky
    k = paramiko.RSAKey.from_private_key_file(priv_key)

    # create an SSH connection
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(vpn_ip, username='ubuntu', pkey=k, allow_agent=False, look_for_keys=False)

    # transfer the instances IPs file
    scp_client = scp.SCPClient(ssh_client.get_transport())
    scp_client.put('instance_ips.txt', remote_path='/home/ubuntu/')
    scp_client.close()

    # TODO: Provide better post-deployment messages
    print('Deployment complete!')

    
    
# function to generate templates regardless of
# the number of variables supplied
def broad_render_template(cloud_name, template_file, vars_dictionary):
    new_tf_file = template_file.split('.')[0] + '.tf'
    templateLoader = FileSystemLoader(searchpath="./templates/")
    templateEnv = Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file)
    output = template.render(vars_dictionary)

    # write to a new Terraform file
    with open('./' + cloud_name + '/' + new_tf_file, 'w') as f:
        f.write(output)
        f.close()
    
    
# this function lists the current machines that will be deployed in
# the cloud
def view_terraform_files(cloud_name):
    # List available deploy options
    vulns = os.listdir(cloud_name)

    # theatrics
    print()
    print('Now listing machines that are ready to be deployed in %s!' % cloud_name)
    print('='*20)
    tf_file_list = []
    for box in vulns:
        counter = len(tf_file_list) + 1
        print('%s. %s' % (counter, box))
        tf_file_list.append((counter,box))

    if len(vulns) == 0:
        print('No machines found')
        print('Please create some using available AMIs')
    print('='*20)
    print()    

            
# Similar to import_vuln_template(), this function creates .tf files based off a simpler template
def render_template(ami_name, ami_id, cloud_name):
    tf_file_name = ami_name + '.tf'    
    templateLoader = FileSystemLoader(searchpath="./templates/")
    templateEnv = Environment(loader=templateLoader)
    template = templateEnv.get_template('base.template')
    output = template.render(keypair=cloud_name, machine_name=ami_name, ami_id=ami_id)

    # write to a new Terraform file
    with open('./' + cloud_name + '/' + tf_file_name, 'w') as f:
        f.write(output)
        f.close()
        

# Take a template and import it to the deployment
def import_vuln_template(terraform, cloud_name, choice):
    machine_name = choice.split('.template')[0] 
    tf_file_name = choice.split('.template')[0] + '.tf'    
    logging.debug('Now creating template for vulnerable machine')
    templateLoader = FileSystemLoader(searchpath="./templates/")
    templateEnv = Environment(loader=templateLoader)
    template = templateEnv.get_template(choice)
    output = template.render(keypair=cloud_name, machine_name=machine_name)

    # write to a new Terraform file
    with open('./' + cloud_name + '/' + tf_file_name, 'w') as f:
        f.write(output)
        f.close()

# function that takes images from vulnerable_images and
# uploads them to the vmstorage bucket in AWS S3
def import_local_vulnhub(session):
    logging.debug('Importing local image from vulnerable_images')

    # list available images in vulnerable_images
    files = os.listdir('vulnerable_images')
    files.remove('.gitignore')

    local_dict = {}
    counter = 1
    for file in files:
        file_ext = os.path.splitext(file)[1]
        if file_ext == '.ova' or file_ext == '.vmdk':
            print('%s. %s' % (counter, file))
            local_dict.update({counter:file})
            counter += 1
            

    # get the user choice
    flag = False
    while flag is False:
        try:
            print('Which image would you like to upload to the AWS S3 vmstorage bucket?')
            user_input = int(input('> '))
            image_to_upload = local_dict.get(user_input)
            flag = True

        except Exception as e:
            print(e)
            print('Please choose a number')

    # upload the image to the vmstorage bucket
    # get an S3 client from the session
    print('Now uploading. This may take a while...')
    s3_client = session.client('s3')
    s3_client.upload_file('./vulnerable_images/' + image_to_upload, 'vmstorage', image_to_upload)

    print('Uploaded %s to the vmstorage S3 bucket!' % image_to_upload)
    
def upload_image(cloud_name, session, image_name, image_name_no_ext, image_filetype):
    # Import the image
    logging.debug('Now attempt to import image')
    logging.debug('%s %s' % (image_name, image_filetype))
    
    ec2_client = session.client('ec2')
    import_response = ec2_client.import_image(
        Description=image_name,
        DiskContainers=[
            {'Format':image_filetype,
             'UserBucket': {
                 'S3Bucket':'vmstorage',
                 'S3Key':image_name
             }
            }
        ],
        TagSpecifications=[
            {
                'ResourceType':'import-image-task',
                'Tags': [
                    {
                        'Key':'Name',
                        'Value':image_name
                    }
                ]
            }
        ]
    )

    # monitor to see when the image is done importing
    flag = False
    results = ec2_client.describe_import_image_tasks()

    import_task_id = import_response['ImportTaskId']

    print('Import started as task ID: %s' % import_task_id)

    # TODO: Handle error detection
    # check if import completed
    with tqdm.tqdm(total=60) as pbar:
        old_prog = 0
        while flag is False:
            logging.debug('Now checking')
            # sleep so we are not bombarding the API
            time.sleep(10)                                
            results = ec2_client.describe_import_image_tasks()        
            for response in results['ImportImageTasks']:
                # this tags check is safe because we set the tags for the import task
                # But it is not safe because there might be other import tasks going on besides FFV
                try:
                    if response['ImportTaskId'] == import_task_id and response['Status'] != 'deleting':
                        if response['Status'] == 'completed':
                            pbar.reset()
                            pbar.update(60)
                            pbar.close()
                            print('Import process completed!')
                            ami_id = response['ImageId']
                            flag = True
                        else:
                            new_prog = int(response['Progress'])
                            pbar.update(new_prog - old_prog)
                            old_prog = new_prog


                except IndexError:
                    continue

    
    # create tags after creation of the AMI
    print('Now creating tags for the newly created AMI...')
    ec2_client.create_tags(Resources=[ami_id],Tags=[{'Key':'Name','Value':image_name},{'Key':'Created by','Value':'farfromVULN'}])

    # create a machine template with the newly created AMI
    print('Now creating a template from the newly created AMI...')
    render_template(cloud_name=cloud_name, ami_id=ami_id, ami_name=image_name_no_ext)

    
    
    
def import_s3_vulnhub(cloud_name, session):
    logging.debug('Importing image from S3')
    
    # session creation and set up
    s3_client = session.client('s3')

    # listv available s3 buckets
    response_dict = s3_client.list_objects(Bucket='vmstorage')

    # list each image file in the vmstorage bucket
    counter = 1
    for image in response_dict['Contents']:
        print('%s. %s' % (counter, image['Key']))
        counter += 1

    # Select an AMI
    image_choice = int(input('Which image file would you like to use?: '))
    image_name = response_dict['Contents'][image_choice-1]['Key']

    # get the filetype and strip the leading period
    image_filetype = os.path.splitext(image_name)[1].lstrip('.')
    image_name_no_ext = os.path.splitext(image_name)[0]

    # upload the image
    upload_image(cloud_name=cloud_name, session=session, image_name=image_name, image_name_no_ext=image_name_no_ext, image_filetype=image_filetype)

# function to set the AWS profile
def set_aws_profile():
    # Get the profile for the session
    env_profile = os.environ.get('FFV_AWS_PROFILE')
    if env_profile is None:
        print('What profile will you use to access AMI images?')
        profile = input('> ')
    else:
        profile = env_profile

    # return profile name
    return profile

# profile to get an ec2 client
def get_ec2_client():
    profile = set_aws_profile()
    session = boto3.session.Session(profile_name=profile)
    ec2_client = session.client('ec2')

    return ec2_client

# function to import AMI images that are already uploaded
def import_ami_image(cloud_name, session):
    logging.debug('importing ami image')

    # ec2_client = get_ec2_client()
    ec2_client = session.client('ec2')

    images_dict = get_self_ami_dictionary(ec2_client)

    # Select an AMI
    print('Which AMI would you like to use?')

    # error handling for AMI selection
    selection_check = False
    while selection_check is False:
        try:
            ami_choice = int(input('> '))
            if ami_choice-1 > len(images_dict['Images']) or ami_choice-1 < 0:
                print('Invalid number. Please choose a number:')
            else:
                selection_check = True                
        except ValueError:
            print('Please choose a number:')
            continue

    # Get the ID and the name of the AMI
    ami_id = images_dict['Images'][ami_choice-1]['ImageId']

    # safely find the name tag in the tags
    ami_name = ''    
    try:
        tags = images_dict['Images'][ami_choice-1]['Tags']
        for tag in tags:
            if tag.get('Key') == 'Name':
                ami_name = tag.get('Value')
    except KeyError:
       pass
        
    # if no name tag could be found, name unnamed
    if ami_name == '':
        ami_name = 'Unnamed'
        
    logging.debug(ami_name + '' + ami_id)

    # get a name without file extension
    image_name_no_ext = os.path.splitext(ami_name)[0]    

    # render templates with value
    render_template(ami_name=image_name_no_ext, ami_id=ami_id, cloud_name=cloud_name)

    print('%s added to deployment!' % image_name_no_ext)

# Function that takes in a terraform object and checks the status of the cloud
def status(terraform):
    logging.debug('Entered status...')
    return_code, stdout, stderr = terraform.cmd('show')
    print(stdout)

# Function that destroys clouds and their respective directories
def destroy(terraform, cloud_name):
    logging.debug('Now entering destroy function')

    # loop to get user input
    flag = False
    while flag is False:
        print('Are you sure you want to delete the cloud: %s?' % cloud_name)
        user_input = input('(y/n) > ')        
        if user_input == 'y':
            return_code, stdout, stderr  = terraform.destroy(capture_output=False, no_color=None)
            if return_code == 0:
                shutil.rmtree(cloud_name)
            flag = True
        
        elif user_input == 'n':
            print('Destruction process cancelled.')
            flag = True
        
        else:
            print('Please choose a valid option')


# Function that prints a banner and welcome text
def banner():
    print(colored('farfromVULN', 'magenta', attrs=['bold']))

    # Open and print ASCII art
    with open('logo.txt', 'r') as logo:
        r = logo.read()
        print(colored(r, 'magenta', attrs=['bold']))


def parse_arguments():
    # get command line arguments
    parser = argparse.ArgumentParser(description='A tool to quickly spin up a virtual private cloud with Vulnhub machines for pentesting training')
    
    subparsers = parser.add_subparsers(title='main actions', description='valid actions to execute', metavar='action')
    subparser_deploy = subparsers.add_parser('deploy', help='deploy a private cloud')
    subparser_deploy.add_argument('deploy', help='name of the private cloud to be deployed', metavar='name')
    
    subparser_status = subparsers.add_parser('status', help='get the status of the private cloud')
    subparser_status.add_argument('status', help='name of the private cloud to check status of', metavar='name')
    
    subparser_destroy = subparsers.add_parser('destroy', help='destroy a private cloud')
    subparser_destroy.add_argument('destroy', help='name of the private cloud to destroy', metavar='name')

    subparser_amis = subparsers.add_parser('amis', help='get the available AMIs or destroy them')

    args = parser.parse_args()

    # print the banner
    banner()

    # if no arguments, print help
    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)

    return args

# Remov Terraform files from directory to allow for fresh deploy
def clean_up(cloud_name):
    path = './' + cloud_name + '/'
    old_files = os.listdir(path)
    for file in old_files:
        try:
            os.remove(path + file)
        except IsADirectoryError:
            continue

# set the Terraform working directory based on the
# name of the cloud 
def set_terraform_directory(cloud_name, action):
    # try and set the Terraform working directory
    # note this directory may not exist if deploying a new
    # virtual private cloud
    
    # Create a Terraform object, does not check if working
    # directory exists
    t = Terraform(working_dir=cloud_name)

    directory_exists = os.path.exists(cloud_name)

    if directory_exists is False and action == 'deploy':
        os.mkdir(cloud_name)
        with open(cloud_name + '/provider.tf', 'w') as pf:
            pf.write('provider "aws" { }')
            pf.close()

    try:
        # Initialize directory
        return_code, stdout, stderr = t.cmd('init')
        try:
            if action == 'deploy':
                os.remove(cloud_name + '/provider.tf')
        except:
            pass
    except FileNotFoundError:
        print('There is no cloud that was created with that name')
        print('Please deploy a cloud with that name before running this command again')
        exit(1)
    
    return t


# Main function        
def main():
    args = vars(parse_arguments())

    logging.debug(args)

    # Check action
    if 'deploy' in args:
        t = set_terraform_directory(args['deploy'], 'deploy')
        clean_up(args['deploy'])
        deploy(t, args['deploy'])
    elif 'status' in args:
        t = set_terraform_directory(args['status'], 'status')        
        logging.debug('status found')        
        status(t)
    elif 'destroy' in args:
        t = set_terraform_directory(args['destroy'], 'destroy')
        destroy(t, args['destroy'])
    else:
        # interact with AMIs
        interact_amis()
        

    
if __name__ == '__main__':
    main()

