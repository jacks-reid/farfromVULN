# scs-labs-aws

This repository contains Terraform files to automate the creation of a lab environment in AWS. Currently, Terraform will create a virtual private cloud and create an EC2 instance with a Kali Linux on it. A setup file then downloads the Metasploit Framework onto Kali.

To make it work for you, you will need to change the ssh keys used in the `main.tf` file.

## TO DO:

- Add in VPN capabilities to the VPC
- Allow traffic to Kali only from VPN
- Add in pwnable machines in the cloud
- Add in beginner CTFd platform to mess around with

## References

Resources used extensively in this project:

- https://github.com/3ndG4me/Offensive-Security-Engineering-Udemy
- https://medium.com/@mitesh_shamra/manage-aws-vpc-with-terraform-d477d0b5c9c5