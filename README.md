# farfromVULN

`farfromVULN` is a tool to help quickly spin up an AWS private cloud with Vulnhub machines and a Kali box for pentesting training. `farfromVULN` helps eliminate the need for local hardware to host Vulnhub boxes on your home network. The script creates an environment where the Vulnhub boxes cannot access the Internet, only other machines within the virtual private cloud.

## Using `farfromVULN`

The script can be split into 3 different parts:

- `./farfromVULN deploy`: build cloud lab environment with Vulnhub machines
- `./farfromVULN status`: check status of cloud lab environment
- `./farfromVULN destroy`: destroy the cloud lab environment

## Set-Up

- Download the `awscli` package
- Download Terraform and move the binary onto your system path ( https://www.terraform.io/downloads.html )
- Run `terraform init` within the `farfromVULN` repository
- Create a user within AWS with either administrator access or the access levels specified at https://docs.aws.amazon.com/vm-import/latest/userguide/vmie_prereqs.html#iam-permissions-image
- `aws configure` to specify access keys and region
- Subscribe to Kali Linux official AMI at https://aws.amazon.com/marketplace/pp/B01M26MMTT (free!)
- Create an AWS S3 bucket named `vmstorage`
- Download a Vulnhub image to the `vulnhub_ovas` directory
  - Check that the Vulnhub machine uses DHCP to get its IP and that its disk format is either `ova` or `vmdk`
  - Rename the file so the only period in the filename is the file extension
- Export environmental variables
  - `export FFV_PRIV_KEY`: the absolute path to the private key to be used to access lab machines
  - `export FFV_PUB_KEY`: the absolute path to the public key to be used to access lab machines
  - `export FFV_REGION`: the AWS region to deploy lab machines in (make sure this is the same as the region specified for the Kali Linux AMI)
  - `export FFV_S3_PROFILE`: the AWS profile that has access to S3 bucket permissions
  - `export FFV_AMI_PROFILE`: the AWS profile that has access to AWS AMI uploading permissions
  - If these variables are not specified they will be asked during deployment
- When the script is uploading a new Vulnhub image, the process may take upwards of 30 minutes
  - The script will automatically detect when the upload process is completed
- Download a VPN profile from http://vpn_ip:7894/<vpn_profile_name> where `vpn_profile_name` is any string you choose
  - Use `sudo openvpn vpn_profile_name.ovpn` to connect to the virtual private cloud network
  - You will now be able to access the Kali Linux and Vulnhub machines through their private IP addresses
- When you are done, use `./farfromVULN destroy` to remove the lab environment

## Usage

Note that all reverse shell/call back exploits need to reach back to the Kali box in the lab. This means if I want to send an exploit from my local machine to the Vulnhub box, I need to send the reverse shell to the cloud Kali machine in order for it to work. The Vulnhub machines can NOT reach your local machine that is connected through the VPN.

## Disclaimer

`farfromVULN` does its best to stay within AWS's free tier requirements. Throughout testing, I have never been charged more than $5 a month. Delete volumes you no longer need and monitor your costs carefully.

Set up billing alerts, learn about free tier limits, and save yourself from an unpleasant bill.

