#!/bin/bash

# Text constants
MAGENTA='\e[95m'
NC='\033[0m'
BOLD='\e[1m'
NORMAL='\e[21m'
RED='\e[91m'
EXIT='echo -e \e[91m\e[1m'

upload_image() {
    # Get function arguments
    FILE_NAME=$1
    FILE_TYPE=$2
    NOOVA_NAME=$3

    # Upload process begins here
    # Get file type
    if [[ $FILE_TYPE == "" ]]; then
	FILE_TYPE=$(echo $FILE_NAME | cut -d'.' -f 2)
    fi
    echo "File type detected: $FILE_TYPE"


    echo "Enter AWS profile with S3 Bucket permissions: "
    echo -n "> "
    read S3_USER </dev/tty
    

    echo "Uploading to AWS..."
    aws s3 cp vulnhub_ovas/$FILE_NAME s3://vmstorage/ --profile $S3_USER

    # Check if upload cancelled, and if so, exit program
    if [[ $? -eq 1 ]]
    then
	clean_up
	echo "Upload failed. Exiting now..."
	exit 1
    fi

    echo "Enter AWS profile with Image Upload permissions: "
    echo -n "> "
    read IMG_UPLOAD_USER </dev/tty
    
    # Import image based on type of file it is
    # TODO: Add name tags
    aws ec2 import-image --disk-containers Format=$FILE_TYPE,UserBucket="{S3Bucket=vmstorage,S3Key=$FILE_NAME}" --profile $IMG_UPLOAD_USER --region us-east-2 > import_ami_task.txt

    # Get the AMI ID of the image
    AMI=$(grep import import_ami_task.txt | cut -d'"' -f 4)
    AMI_ID=$(grep ImageId | cut -d'"' -f 4)
    echo "AMI Name of the uploaded image: $AMI"
    echo "AMI ID of the uploaded image: $AMI_ID"    

    # Loop and check when the upload process has completed
    # TODO: Check if upload failed and exit script
    FLAG=false
    START=$SECONDS
    while [ $FLAG != true ]
    do
	DURATION=$(( SECONDS - START ))
	echo "Checking for completion on image upload...  [ $DURATION seconds elapsed ]" 
	sleep 30

	aws ec2 describe-import-image-tasks --import-task-ids $AMI > import_ami_task.txt
	
	# Check for failure
	FAILURE=$(grep deleting ./import_ami_task.txt | wc -l)
	if [[ $FAILURE > 0 ]]
	then
	    FAILURE_MSG=$(grep StatusMessage ./import_ami_task.txt)	    
	    clean_up
	    echo "Image is not compatible for the AWS Image Import process. Exiting now..."
	    echo "$FAILUREMSG"
	    echo "Removing downloaded file..."
	    rm ./vulnhub_ovas/$FILE_NAME
	    exit 1
	fi
	
	# Check for success
	check=$(grep completed ./import_ami_task.txt | wc -l)
	if [[ $check == 2 ]]
	then
	    FLAG=true
	    echo "Process has completed!"
	fi
    done

    # Apply to Terraform, should also build a .tf file with the new AMI uploaded
    if [[ $FILE_NAME =~ "." ]]
    then
	FILE_NAME=$NOOVA_NAME
    fi
    
    VULN_PATH="./vulnerable_machines/$FILE_NAME"    
    SUFFIX=".tf"
    FINAL_PATH="$VULN_PATH$SUFFIX"
    echo -n """
# A Vulnhub machine on the network
resource \"aws_instance\" \"$FILE_NAME\" {
  ami                    = \"$AMI_ID\" # Custom AMI, uploaded using https://docs.amazonaws.cn/en_us/vm-import/latest/userguide/vm-import-ug.pdf
  instance_type          = var.instance_type
  key_name               = \"primary\"
  subnet_id              = aws_subnet.my_subnet.id
  vpc_security_group_ids = [aws_security_group.allow_vuln.id]

  tags = {
    Name = \"$FILE_NAME\"
  }
}
# Don't change the name of the output, will break Webapp :)
output \"$FILE_NAME\" {
  value = aws_instance.$FILE_NAME.private_ip
}

""" > $FINAL_PATH

    # Copy to main directory to be part of Terraform deploy
    cp $FINAL_PATH .

    echo "Vulnhub image successfully uploaded to AWS and ready for deployment!"
    
}

clean_up() {
    ${EXIT}
    # Clean up all the files we create
    rm machine_choices.txt 2> /dev/null
    rm checksum.txt 2> /dev/null
    import_ami_task.txt 2> /dev/null
}

clean_up

clear

echo -e "${MAGENTA}${BOLD}Welcome to farfromVULN"

cat farfromVULN.logo

# Pick a vulnhub machine to deploy
COUNTER=0
MACHINES=$(find ./vulnerable_machines/ | cut -d'/' -f 3)
echo "Pick a Vulnhub machine to deploy:"
for MACHINE in $MACHINES
do
    MACHINE=$(echo $MACHINE | cut -d'.' -f 1)
    COUNTER=$((COUNTER+1))
    echo "($COUNTER) $MACHINE"
    echo "$COUNTER.$MACHINE" >> machine_choices.txt
done
COUNTER=$((COUNTER+1))
echo "($COUNTER) Search remotely for Vulnhub machine *UNSTABLE*"
echo "$COUNTER.Search" >> machine_choices.txt

COUNTER=$((COUNTER+1))
echo "($COUNTER) Import local Vulnhub image"
echo "$COUNTER.Import" >> machine_choices.txt

# Default color and font
echo -e "${NORMAL}${NC}"

# read in the choice
echo -n "> "
read VULN_CHOICE

# Loop through and find the machine the user selected
while IFS= read -r line;
do
    NUM=$(echo $line | cut -d'.' -f 1)
    if [[ $VULN_CHOICE =~ $NUM ]]
    then
	SELECTED_MACHINE=$(echo $line | cut -d'.' -f 2)

	# TODO: Add import functionality
	# To import an image, store the image in ./vulnhub_ovas/ directory
	if [[ $SELECTED_MACHINE =~ "Import" ]]
	then
	    echo "What file do you want to import?"
	    echo -n "> "
	    read IMPORT_FILE </dev/tty
	    IMPORT_NAME=$(echo $IMPORT_FILE | cut -d'.' -f 1)	    
	    IMPORT_FILE_TYPE=$(echo $IMPORT_FILE | cut -d'.' -f 2)
	    upload_image $IMPORT_FILE $IMPORT_FILE_TYPE $IMPORT_NAME
	    
	    # If the user chose to search, then begin search functionality
	elif [[ $SELECTED_MACHINE =~ "Search" ]]
	then
	    echo -n "Vulnhub machine to search for: "
	    read SEARCH_MACHINE </dev/tty
	    wget -q https://download.vulnhub.com/checksum.txt
	    VAL=$(grep -i -m 1 $SEARCH_MACHINE checksum.txt | cut -d' ' -f 3)
	    CHECKSUM=$(grep -i -m 1 $SEARCH_MACHINE checksum.txt | cut -d' ' -f 1)	    
	    FILE_NAME=$(echo "$VAL" | rev | cut -d'/' -f 1 | rev)
	    VAL2="https://download.vulnhub.com/"
	    VAL3="$VAL2$VAL"
	    echo "Found file at $VAL3"

	    wget --spider $VAL3
	    echo "Are you sure you want to download this file? (y/n)"
	    echo -n "> "
	    read confirm </dev/tty
	    if [[ $confirm = "y" ]]
	    then
		rm checksum.txt
		echo "Retrieving file..."
		wget --directory-prefix=./vulnhub_ovas/ $VAL3

		# Confirm successful download with checksum		
		COMPARE=$(md5sum ./vulnhub_ovas/$FILE_NAME | cut -d' ' -f 1)		
		echo "COMPARE: $COMPARE"
		echo "CHECKSUM: $CHECKSUM"

		if [[ $COMPARE != $CHECKSUM ]]
		then
		    echo "ERROR: Downloaded file did not match download checksum. Exiting now and removing the downloaded file."
		    rm ./vulnhub_ovas/$FILE_NAME
		    clean_up
		    exit 1
		fi
		
		# TODO: Account for different compression file types
		# Regex check to see if its a zip file
		if [[ $FILE_NAME =~ "zip" ]];
		then
		    unzip ./vulnhub_ovas/$FILE_NAME -d ./vulnhub_ovas/
		    # From here we need to regex and find a compatible file type,
		    # then set that file type as the new file name for upload
		    FILE_NAME=$(find ./vulnhub_ovas | grep -E "ova|vmdk" -m 1)

		    # If no ova or vmdk file is found, then exit the importation process
		    if [[ $FILE_NAME == "./vulnhub_ovas" ]]
		    then
			clean_up			
			echo "The file is not in a compatible file format and cannot be imported in AWS. Exiting now."
			exit 1
		    fi
		    FILE_TYPE=$(echo $FILE_NAME | cut -d'.' -f 3)	    
		fi
	    elif [[ $confirm = "n" ]]
	    then
		clean_up
		echo "bye!"
		exit 1
	    fi

	    # upload the image to AWS
	    upload_image $FILE_NAME $FILE_TYPE 

	else
	    cp vulnerable_machines/$SELECTED_MACHINE.tf .
	    echo "Adding $SELECTED_MACHINE to lab build..."
	fi
    fi
done < machine_choices.txt

# Select the SSH keypair to use with this lab
# First check to see if the ssh keypair has been declared as an environmental variable
if [[ -z $FFV_PRIV_KEY || -z $FFV_PUB_KEY ]] # if either private or public has not been declared...
then
    # Then the keypair needs to be declared...
    echo "What is the absolute path to the SSH private key to use with this lab?"
    echo -n "> "
    read SSH_PRIV_KEY_PATH

    # Test to see if that file exists and is a valid SSH key
    ssh-keygen -l -f $SSH_PRIV_KEY_PATH
    if [[ $? -ne 0 ]]
    then
	clean_up
	echo "Exiting now..."
	exit 1
    fi


    echo "What is the absolute path to the SSH public key to use with this lab?"
    echo -n "> "
    read SSH_PUB_KEY_PATH

    # Test to see if that file exists and is a valid SSH key
    ssh-keygen -l -f $SSH_PUB_KEY_PATH
    if [[ $? -ne 0 ]]
    then
	clean_up
	echo "Exiting now..."
	exit 1
    fi
else
    SSH_PRIV_KEY_PATH=$FFV_PRIV_KEY
    SSH_PUB_KEY_PATH=$FFV_PUB_KEY    
fi

echo "Building machine now..."

terraform apply -var="private_key_path=$SSH_PRIV_KEY_PATH" -var="public_key_path=$SSH_PUB_KEY_PATH"

if [[ $? -eq 0 ]]
then
    terraform output -json > instance_ips.txt
    
    # Get the public IP of the PiVPN server
    VPN_PUB_IP=$(grep -A 3 PiVPN instance_ips.txt | grep value | cut -d"\"" -f 4)
    # Give the web app the correct VPC private ips
    
    echo yes | scp  -i "~/.ssh/labs-key.pem" instance_ips.txt ubuntu@$VPN_PUB_IP:/home/ubuntu/

    # Start the web app! Hosted on port 7894
    echo "Now starting web application..."
    ssh -i "~/.ssh/labs-key.pem" ubuntu@$VPN_PUB_IP "export FLASK_APP=/home/ubuntu/app.py && flask run -h 0.0.0.0 -p 7894"
else
    clean_up
    echo "Terraform deployment failed. Now exiting..."
    exit 1
fi

