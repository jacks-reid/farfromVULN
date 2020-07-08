# scs-labs-aws

This repository contains Terraform files to automate the creation of a lab environment in AWS. Currently, Terraform will create a virtual private cloud and create an EC2 instance with a Kali Linux on it. A setup file then downloads the Metasploit Framework onto Kali.

To make it work for you, you will need to change the ssh keys used in the `main.tf` file.

## Using Terraform

Terraform can be split into 3 different commands.

- `terraform init`: load provider modules
- `terraform plan`: plan the deploy, check syntax, etc
- `terraform apply`: deploy

### Resources
- https://www.terraform.io/intro/index.html
- https://www.terraform.io/docs/providers/aws/index.html

## Set-Up

You'll need to create your own AWS account and get API access tokens. Store those tokens in your `~/.aws/credentials` file and Terraform will automatically detect and use them. You will also need to subscribe to the Kali Linux AMI in the AWS Marketplace (free of charge).

- https://www.terraform.io/intro/index.html

I did my best to stay within AWS's free tier requirements. Based on my experience it is free of charge, but don't take my word for it. Set up billing alerts, learn about free tier limits, and save yourself from an unpleasant bill.

In addition, you will need to subscribe to Offensive Security's custom Kali Linux image.

- https://aws.amazon.com/marketplace/pp/Kali-Linux-Kali-Linux/B01M26MMTT

## Usage

Run the `./farfromVULN` start script and choose the correct options to set up the Vulnhub box of your choice.

## TO DO:

- ~~Add in VPN capabilities to the VPC~~
  - ~~Add in PiVPN installation automation~~
  - ~~Add in PiVPN VPN profile creation and distribution automation~~
  - Allow Kali ssh server password logins
- Automate the creation of Kali profiles when a VPN profile is created
  - With appropriate shell, homedir, etc
- Allow traffic to Kali only from VPN
- ~~Add in pwnable machines in the cloud~~
  - Configure appropriate level of traffic outwards from vulnerable machines
  - ~~Automate the Vulnhub image AMI upload process~~
    - Have automatic detection of Vulnhub tf files in `vulnerable_machines` directory to be added as options in start script
    - Refine AMI upload process
- Clean up Flask server
  - Possibly use uWSGI server for long term solution
  - Improve Flask security
- Add in beginner CTFd platform to mess around with
  - Using a separate cloud in DigitalOcean?

## References

Resources used extensively in this project:

- https://github.com/3ndG4me/Offensive-Security-Engineering-Udemy
- https://medium.com/@mitesh_shamra/manage-aws-vpc-with-terraform-d477d0b5c9c5
- https://docs.amazonaws.cn/en_us/vm-import/latest/userguide/vm-import-ug.pdf