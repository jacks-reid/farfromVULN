# farfromVULN

`farfromVULN` is a tool to help quickly spin up an AWS private cloud with Vulnhub machines and a Kali box for pentesting training. `farfromVULN` helps eliminate the need for local hardware to host Vulnhub boxes on your home network. The script creates an environment where the Vulnhub boxes cannot access the Internet, only other machines within the virtual private cloud.

## Using `farfromVULN`

The script can be split into 3 different parts:

- `./farfromVULN deploy`: build cloud lab environment with Vulnhub machines
- `./farfromVULN status`: check status of cloud lab environment
- `./farfromVULN destroy`: destroy the cloud lab environment

## Set-Up

You'll need to create your own AWS account and get API access tokens. Store those tokens in your `~/.aws/credentials` file and `farfromVULN` will automatically detect and use them. You will also need to subscribe to the Kali Linux AMI in the AWS Marketplace (free of charge).

`farfromVULN` does its best to stay within AWS's free tier requirements. Throughout all the testing, I have never been charged more than $5 a month. Set up billing alerts, learn about free tier limits, and save yourself from an unpleasant bill.

In addition, you will need to subscribe to Offensive Security's custom Kali Linux image.

- https://aws.amazon.com/marketplace/pp/Kali-Linux-Kali-Linux/B01M26MMTT

## Usage

Run the `./farfromVULN` start script and choose the correct options to set up the Vulnhub box of your choice. Once completed, visit the public IP of the VPN on port 7894 to get the VPN webpage. Visit http://my_vpn_ip:7984/some_name_here to download a VPN profile and connect to the virtual lab network. From here you will be able to connect to cloud lab environment and access the private IPs of the machines.

Note that all reverse shell/call back exploits need to be done to the Kali box in the lab. The Vulnhub machines can NOT reach your local machine that is connected through the VPN.

## References

Resources used extensively in this project:

- https://github.com/3ndG4me/Offensive-Security-Engineering-Udemy
- https://medium.com/@mitesh_shamra/manage-aws-vpc-with-terraform-d477d0b5c9c5
- https://docs.amazonaws.cn/en_us/vm-import/latest/userguide/vm-import-ug.pdf