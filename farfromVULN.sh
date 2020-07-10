#!/bin/bash

clear

echo "Welcome to farfromVULN"

cat farfromVULN.logo

# Pick a vulnhub machine to deploy
# NOTE: AMI image must already be uploaded
echo "Pick a Vulnhub machine to deploy:"
echo "(1) Fristileaks 1.3"
echo "(2) Mr Robot"
echo "(3) Stapler"
echo "(4) Search for machine"
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
    cp vulnerable_machines/stapler.tf .
    
elif
    [[ $vuln_choice -eq 4 ]]
then
    echo -n "Vulnhub machine to search for: "
    read search_machine
    wget -q https://download.vulnhub.com/checksum.txt
    VAL=$(grep -i -m 1 $search_machine checksum.txt | cut -d' ' -f 3)
    file_name=$(echo "$VAL" | rev | cut -d'/' -f 1 | rev)
    VAL2="https://download.vulnhub.com/"
    VAL3="$VAL2$VAL"
    echo "Found file at $VAL3"

    wget --spider $VAL3
    echo "Are you sure you want to download this file? (y/n)"
    echo -n "> "
    read confirm
    
    if [[ $confirm = "y" ]]
    then
	rm checksum.txt
	echo "Retrieving file..."
	wget --directory-prefix=./vulnhub_ovas/ $VAL3

	# Regex check to see if its a zip file
	if [[ $file_name =~ "zip" ]];
	then
	    unzip ./vulnhub_ovas/$file_name;
	    # From here we need to regex and find a compatible file type,
	    # then set that file type as the new file name for upload
	    $file_name=$(find ./vulnhub_ovas | grep -E "ova|vmdk" -m 1)
	    file_type=$(echo $file_name | cut -d'.' -f 3)	    
	fi

    elif [[ $confirm = "n" ]]
    then
	rm checksum.txt
	echo "bye!"
	exit
    fi

    # Get file type
    # TO DO: fix the
    if [[ $file_type == "" ]]; then
	file_type=$(echo $file_name | cut -d'.' -f 2)
    fi
    echo "File type detected: $file_type"	

    echo "Uploading to AWS..."
    aws s3 cp vulnhub_ovas/$file_name s3://vmstorage/ --profile superadmin

    # Import image based on type of file it is
    # TODO: Add name tags
    aws ec2 import-image --disk-containers Format=$file_type,UserBucket="{S3Bucket=vmstorage,S3Key=$file_name}" --profile superadmin --region us-east-2 > import_ami_task.txt

    # Get the AMI ID of the image
    ami=$(grep import import_ami_task.txt | cut -d'"' -f 4)
    echo "AMI ID of the uploaded image: $ami"

    echo "aws ec2 describe-import-image-tasks --import-task-ids $task_id"

    # Loop and check when the upload process has completed
    # TODO: Check if upload failed and exit script
    flag=false
    start=$SECONDS
    while [ $flag != true ]
    do
	duration=$(( SECONDS - start ))
	echo "Checking for completion on image upload...  [ $duration seconds elapsed ]" # TODO: Add more informative message
	sleep 30
	aws ec2 describe-import-image-tasks --import-task-ids $ami > import_ami_task.txt	
	check=$(grep completed ./import_ami_task.txt | wc -l)
	# echo "check: $check" # TODO: Remove me
	if [[ $check == 2 ]]
	then
            flag=true
	    echo "Process has completed!"
	fi
    done

    # # Apply to Terraform, should also build a .tf file with the new AMI uploaded
    vuln_path="./vulnerable_machines/$search_machine"
    suffix=".tf"
    final_path="$vuln_path$suffix"
    echo -n """
# First Vulnhub machine on the network
resource \"aws_instance\" \"$search_machine\" {
  ami                    = \"$ami\" # Custom AMI, uploaded using https://docs.amazonaws.cn/en_us/vm-import/latest/userguide/vm-import-ug.pdf
  instance_type          = var.instance_type
  key_name               = \"primary\"
  subnet_id              = aws_subnet.my_subnet.id
  vpc_security_group_ids = [aws_security_group.allow_vuln.id]

  tags = {
    Name = \"$search_machine\"
  }
}
""" > $final_path

    # Copy to main directory to be part of Terraform deploy
    cp $final_path .

    echo "Vulnhub image successfully uploaded to AWS and ready for deployment!"

    # clean up
    rm import_ami_task.txt
    
else
    echo "Invalid input -- exiting now."
fi

echo "Building machine now..."
# echo yes | terraform apply # TODO: add me?

terraform plan # TODO: remove me!










