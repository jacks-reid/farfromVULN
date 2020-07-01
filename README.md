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

## TO DO:

- Add in VPN capabilities to the VPC
- Allow traffic to Kali only from VPN
- Add in pwnable machines in the cloud
- Add in beginner CTFd platform to mess around with

## References

Resources used extensively in this project:

- https://github.com/3ndG4me/Offensive-Security-Engineering-Udemy
- https://medium.com/@mitesh_shamra/manage-aws-vpc-with-terraform-d477d0b5c9c5