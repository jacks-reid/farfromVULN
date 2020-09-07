import logging
import argparse
import sys
from termcolor import colored
from python_terraform import *
from os import listdir
from os import remove
from jinja2 import Template
import jinja2


logging.basicConfig(level=logging.DEBUG)

def deploy(terraform, cloud_name):
    # List available deploy options
    vulns = os.listdir('templates')
    vulns.remove('.gitignore')

    # List available vulnerable machines
    mylist = []
    found_flag = False
    counter = 1
    for box in vulns:
        name = box.split('.template')[0]
        print('%s. %s' % (counter, name))
        mylist.append((counter,box))        
        counter += 1

    logging.debug(mylist)

    # List of additional options outside of available machines
    additional_options = ['Import local Vulnhub image',
                          'Import remote Vulnhub image from AWS S3 bucket',
                          'Use previously uploaded AMI from AWS']

    for option in additional_options:
        print('%s. %s' % (counter, option))
        mylist.append((counter, option))
        counter += 1

    # Get user choice
    user_input = int(input('Select a choice: '))

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
        exit(1)


    # Execute option
    if 'local' in user_input:
        import_local_vulnhub()
    elif 'S3' in user_input:
        import_s3_vulnhub()
    elif 'previously' in user_input:
        import_ami_image()
    else:
        import_vuln_template(terraform, cloud_name, user_input)

        
def import_vuln_template(terraform, name, choice):
    machine_name = choice.split('.template')[0] 
    tf_file_name = choice.split('.template')[0] + '.tf'    
    logging.debug('Now creating template for vulnerable machine')
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(choice)
    output = template.render(keypair=name, machine_name=machine_name)

    with open('./tf_files/' + tf_file_name, 'w') as f:
        f.write(output)
        f.close()
    

def import_local_vulnhub():
    logging.debug('Importing local image from vulnhub')
    
def import_s3_vulnhub():
    logging.debug('Importing image from S3')
    
def import_ami_image():
    logging.debug('importing ami image')    
    

# Function that takes in a terraform object and checks the status of the cloud
def status(terraform, name):
    logging.debug('Entered status...')
    return_code, stdout, stderr = terraform.cmd('show')
    print(stdout)


# def destroy():
#     # TODO: Add me


# Function that prints a banner and welcome text
def banner():
    print(colored('farfromVULN', 'magenta', attrs=['bold']))

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

    
    args = parser.parse_args()

    # print the banner
    banner()

    # if no arguments, print help
    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)


    return args

def clean_up():
    path = './tf_files/'
    old_files = os.listdir(path)
    for file in old_files:
        os.remove(path + file)

# Main function        
def main():
    args = vars(parse_arguments())

    logging.debug(args)

    t = Terraform()
    return_code, stdout, stderr = t.cmd('init')


    if 'deploy' in args:
        clean_up()
        deploy(t, args['deploy'])
    elif 'status' in args:
        logging.debug('status found')        
        status(t, args['status'])
    elif 'destroy' in args:
        destroy(t)

    
    

    
if __name__ == '__main__':
    main()

