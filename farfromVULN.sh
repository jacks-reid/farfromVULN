#!/bin/bash

clear

echo "Welcome to farfromVULN"

cat farfromVULN.logo

# Pick a vulnhub machine to deploy
# NOTE: AMI image must already be uploaded
echo "Pick a Vulnhub machine to deploy:"
echo "(1) Fristileaks 1.3"
echo "(2) Mr Robot"
echo "(3) Search for machine"
echo -n "> "
read vuln_choice

if [[ $vuln_choice -eq 1 ]]
then
    cp vulnerable_machines/fristileaks.tf .
elif
    [[ $vuln_choice -eq 2 ]]
then
    cp vulnerable_machines/mrrobot.tf .
elif
    [[ $vuln_choice -eq 3 ]]
then
    echo -n "Vulnhub machine to search for: "
    read search_machine
    wget -q https://download.vulnhub.com/checksum.txt
    VAL=$(grep -m 1 $search_machine checksum.txt | cut -d' ' -f 3)
    file_name=$(echo "$VAL" | rev | cut -d'/' -f 1 | rev)
    VAL2="https://download.vulnhub.com/"
    VAL3="$VAL2$VAL"
    echo "Found file at $VAL3"

    wget --spider $VAL3
    echo "Are you sure you want to download this file? (y/n)"
    read confirm
    
    if [[ $confirm = "y" ]]
    then
	rm checksum.txt
	echo "Retrieving file..."
	wget --directory-prefix=./vulnhub_ovas/ $VAL3 
    elif [[ $confirm = "n" ]]
    then
	rm checksum.txt
	echo "bye!"
	exit
    fi

    echo "Uploading to AWS..."
    aws s3 cp vulnhub_ovas/$file_name s3://vmstorage/ --profile superadmin

    aws ec2 import-image --disk-containers Format=ova,UserBucket="{S3Bucket=vmstorage,S3Key=$file_name}" --profile superadmin --region us-east-2

    echo "This is going to take a while..."
    echo "What is the task-id for the import-ami task?"
    echo -n "> "
    read task_id

    aws ec2 describe-import-image-tasks --import-task-ids $task_id

    echo "aws ec2 describe-import-image-tasks --import-task-ids $task_id"

    
else
    echo "Invalid input -- exiting now."
fi

# Apply to Terraform
echo "Building machine now..."
echo yes | terraform apply









