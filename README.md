# farfromVULN

image:https://img.shields.io/github/license/earnivore/farfromVULN?style=plastic

`farfromVULN` is a tool to help quickly spin up an AWS private cloud with Vulnerable machines and a Kali box for pentesting training. `farfromVULN` helps eliminate the need for local hardware to host vulnerable boxes on your home network. The script creates an environment where the vulnerable boxes cannot access the Internet, only other machines within the virtual private cloud.

```
farfromVULN
  __            __                     _   _ _   _ _      _   _ 
 / _|          / _|                   | | | | | | | |    | \ | |
| |_ __ _ _ __| |_ _ __ ___  _ __ ___ | | | | | | | |    |  \| |
|  _/ _` | '__|  _| '__/ _ \| '_ ` _ \| | | | | | | |    | . ` |
| || (_| | |  | | | | | (_) | | | | | \ \_/ / |_| | |____| |\  |
|_| \__,_|_|  |_| |_|  \___/|_| |_| |_|\___/ \___/\_____/\_| \_/


usage: farfromVULN.py [-h] action ...

A tool to quickly spin up a virtual private cloud with vulnerable machines for pentesting training

optional arguments:
  -h, --help  show this help message and exit

main actions:
  valid actions to execute

  action
    deploy    deploy a private cloud
    status    get the status of the private cloud
    destroy   destroy a private cloud
    amis      get the available AMIs or destroy them
```

## Set-Up

- Download the `awscli` package
- Download Terraform and move the binary onto your system path ( https://www.terraform.io/downloads.html )
- Run `terraform init` within the `farfromVULN` repository
- Create a service role within AWS with the access levels specified at https://docs.aws.amazon.com/vm-import/latest/userguide/vmie_prereqs.html#iam-permissions-image
  - Note that creating a service role is different than a traditional AWS IAM user. An administrator user would be unable to perform the same duties as the AWS service role
- `aws configure` to specify access keys and region
- Subscribe to Kali Linux official AMI at https://aws.amazon.com/marketplace/pp/B01M26MMTT (free!)
- Create an AWS S3 bucket named `vmstorage`
- Use the farfromVULN AMI Builder to create a custom AMI for deployment: https://github.com/earnivore/farfromVULN-AMI-Builders
- Assign environmental variables:
  - `export FFV_PRIV_KEY`: The private key that will be used to SSH into the lab machines
  - `export FFV_PUB_KEY`: The public key that will be assigned with the lab machines
  - `export FFV_AWS_PROFILE`: The AWS profile configured with `aws configure` with sufficient access to EC2 instances and S3 buckets. Available profiles can be found in `~/.aws/config`

## Usage

- Use `python farfromVULN.py deploy mycloudnamehere` to create a new directory and VPC called `mycloudnamehere`
```
==================================================
DEPLOYMENT COMMANDS
==================================================
1. Import local machine image to AWS S3 bucket
2. Build an AMI from a machine image in a AWS S3 bucket
3. Use previously uploaded AMI from AWS to build a Terraform file
4. View Terraform files ready for deployment in the cloud
5. Deploy the cloud with created Terraform files
6. Quit
```
- Select a deployment command that best fits your use case. If you have a vulnerable machine image locally, move it into the `vulnerable_images` directory and follow commands 1-5 to upload the image to S3, create an AMI out of that image, create a Terraform file with the newly created AMI, and deploy that AMI into the farfromVULN lab.
  - These steps do not have to be followed sequentially. If you already have vulnerable images in S3, move them to your `vmstorage` bucket and you can start from step 3.
  - When in doubt, select command 3 to see the available AMIs that you can deploy
- When the script is uploading a new vulnerable machine image, the process may take upwards of 30 minutes
  - The script will automatically detect when the upload process is completed
- Download a VPN profile from `http://vpn_ip:7894/<vpn_profile_name>` where `vpn_profile_name` is any string you choose
  - Use `sudo openvpn vpn_profile_name.ovpn` to connect to the virtual private cloud network
  - You will now be able to access the Kali Linux and Vulnerable machines through their private IP addresses
- When you are done, use `python farfromVULN.py destroy mycloudnamehere` to remove the lab environment

Note that all reverse shell/call back exploits need to reach back to the Kali box in the lab. This means if I want to send an exploit from my local machine to the Vulnerable box, I need to send the reverse shell to the cloud Kali machine in order for it to work. The Vulnerable machines can NOT reach your local machine that is connected through the VPN.

## Disclaimer

`farfromVULN` does its best to stay within AWS's free tier requirements. Throughout testing, I have never been charged more than $5 a month. Delete volumes you no longer need and monitor your costs carefully. Use the `farfromVULN.py ami` command to view and delete unused AMIs and their associated storage volumes.

Set up billing alerts, learn about free tier limits, and save yourself from an unpleasant bill.

## License

This project is licensed under the terms of the GNU General Public License.

## Working boxes

`farfromVULN` has some limitations, notably that AWS only supports specific operating systems. A list of tested Vulnhub boxes can be found at `working_machines.txt`.

## References

Great resources used in this project:

- https://github.com/3ndG4me/Offensive-Security-Engineering-Udemy
- https://docs.amazonaws.cn/en_us/vm-import/latest/userguide/vm-import-ug.pdf
- https://www.vulnhub.com/
- https://www.kali.org/
- https://medium.com/@mitesh_shamra/manage-aws-vpc-with-terraform-d477d0b5c9c5
