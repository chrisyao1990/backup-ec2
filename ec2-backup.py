#!/usr/bin/python
#
# Filename : ec2-backup.py
# Author   : Kun Yao
#            Dainong Ma
#            Zhe Wang

import sys, getopt, os, commands, time
#======================
#global attributes
#======================

EC2_INSTANCE_ID = ""  #instance id generated
EC2_HOST = "" #instance public DNS is generated
KEYPAIR_LOCATION = "" #keypair for login instance needed from yaokun
SECURITY_GROUP = "" #securty group for running instance needed from yaokun
AMI_ID = "" # needed or default
INSTANCE_LOGIN_USR = "ec2-user" #generated or default
MOUNT_DEV_LOCATION = "/dev/sdb" #default or create by us all
MOUNT_DIR_LOCATION = "/mnt/data-store" # create by us all
SOURCE_DIR = "" # the dir needed to backup
SOURCE_DIR_SIZE = 0 #the dir size needed by yaokun
VOLUME_SIZE = 0 #calculated by wangzhe
VOLUME_ID = "" #given by usr or generated by def createvolume
AVA_ZONE="us-east-1b" # if the colume id is given, need to know this form volume id, if not, we define it same for create instance
VERBOSE = 0



#=======================
#Print the usage message
#=======================
def usage():
    print 'Usage:'
    print '  ec2-backup [-h] [-m method] [-v volume-id] dir'

#================================
#Check the validlity of directory
#
# @param dir_ given directory
# @return bool dir exists or not
#================================
def checkdir(dir_):
    return os.path.exists(full_path(dir_))

#===============================
#try to convert given directory into abs dir
#
# @param dir_ given directory
# @return string abslute path
#===============================
def full_path(dir_):
    if dir_[0] == '~' and not os.path.exists(dir_):
        dir_ = os.path.expanduser(dir_)
    return os.path.abspath(dir_)

#==============================
#Print error massage and exit
#
# @param error_message string 
#==============================
def error(error_message):
    sys.stderr.write("Error: " + error_message + "\n")
    clean()
    sys.exit(1)

#==============================
#Print message if VERBOSE
#
# @param msg_str string message will be print
#==============================
def message(msg_str):
    global VERBOSE
    if(VERBOSE):
        print "Message: ",msg_str,"\n"

#==============================
#Error check for output from commands.outputstatus
#
# @param output len 2 tuple output[0] is return status and ouput[1]
#                           is return message
#==============================
def err_check(output):
    if(output[0] != 0):
        error(output[1])

#==============================
#Size of giving dirctory
# @param  string start dirctory
# @return int    total number of bytes of giving dir
#==============================
def getdirsize(start_dir = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size
#==============================
#calculate 
#
#
#
#==============================
def calculate():
	global SOURCE_DIR_SIZE, VOLUME_SIZE
	print SOURCE_DIR_SIZE
	y = SOURCE_DIR_SIZE/1024/1024/1024
	VOLUME_SIZE = 2 * (int(y) + 1)
	print(VOLUME_SIZE)

#===============================
#TODO: Create EC2 instance and 
#        set up connection
#===============================
def launchec2():
    global AMI_ID,KEYPAIR_LOCATION,SECURITY_GROUP,EC2_INSTANCE_ID,\
            EC2_HOST,AVA_ZONE
    commandhead =  'aws ec2 run-instances '
    key =          ' --key ec2backup-keypair '
    group =        ' --security-groups ec2backup-security-group '
    instancetype = ' --instance-type t1.micro '
    imageid =      ' --image-id ami-2f726546 '
    avazone =      ' --availability-zone us-east-1b '
    grepinsID =    ' | grep InstanceId | head -1 '
    flags = os.environ.get('EC2_BACKUP_FLAGS_AWS')
    sshflags = os.environ.get('EC2_BACKUP_FLAGS_SSH')
    AMI_ID = 'ami-2f726546'
    
    #parse aws flags
    if(flags != None):
        try:
            opts, args = getopt.getopt(flags.split(),"",\
                    ["instance-type=","security-groups=","image-id=",\
                    "availability-zone="])
        except getopt.GetoptError:
            error("Unknow option detected in EC2_BACKUP_FLAGS_AWS,"+\
                    "\n    We only accept change of instance-type "+\
                    "security-groups "+"image-id "+ "availability-zone ")
        for opt,arg in opts:
            if opt == '--security-groups':
                group = ' --security-groups ' + arg
                SECURITY_GROUP = arg
            elif opt == '--image-id':
                imageid =' --image-id ' + arg
                AMI_ID = arg
            elif opt == '--availability-zone':
                avazone =' --availability-zone '+arg
                AVA_ZONE = arg
            elif opt == '--instance-type':
                instancetype = ' --instance-type '+arg
            if(len(args)>=1):
                error("Unknow option detected in EC2_BACKUP_FLAGS_AWS,"+\
                        "\n    We only accept change of instance-type "+\
                        "security-groups "+"image-id "+ "availability-zone ")
    #TODO:parse ssh flags
    if(sshflags != None):
        try:
            opts, args = getopt.getopt(sshflags.split(),"i:",[])
        except getopt.GetoptError:
            error("Unknow option detected in EC2_BACKUP_FLAGS_SSH,"+"\n\
                    We only accept change of -i key-pair")
        for opt,arg in opts: 
            if opt == '-i':
                KEYPAIR_LOCATION = arg 
            else:
                error("Unknow option detected in EC2_BACKUP_FLAGS_SSH,"+\
                        "\n    We only accept change of -i key-pair")
        
    #key and group gen
    if(len(KEYPAIR_LOCATION)>0):
        KEYPAIR_LOCATION = keygen()
    if(len(SECURITY_GROUP)>0):
        SECURITY_GROUP = securitygroupgen()

    #run ec2
    ec2command = commandhead + key + group + instancetype + \
            imageid + avazone + grepinsID
    out = commands.getstatusoutput(ec2command)
    EC2_INSTANCE_ID = out[1][-13:-3]
    print out
    print EC2_INSTANCE_ID

    time.sleep(5)
    statecheckcommand = '''aws ec2 describe-instances --instance-ids '''+\
            EC2_INSTANCE_ID + ''' | grep '"Name": "running"' | wc -l '''
    out = commands.getstatusoutput(statecheckcommand)
    while(out[1] != '1'):
        time.sleep(5)
        out = commands.getstatusoutput(statecheckcommand)
    time.sleep(10)

    out = commands.getstatusoutput(statecheckcommand)
    fatchDNScommand = '''aws ec2 describe-instances --instance-id '''+\
                        EC2_INSTANCE_ID+ ''' | grep PublicDnsName | head -1 '''
    print fatchDNScommand
    out = commands.getstatusoutput(fatchDNScommand)
    EC2_HOST = out[1][38:-3]
    print 'EC2_HOST',EC2_HOST

       
#========================
#TODO: Key pair gen SSH FLAGS HANDLE
# Defult key name: ec2backup-keypair
#=======================
def keygen():
    checkcommand = '''aws ec2 describe-key-pairs | grep '"KeyName": "ec2backup-keypair",'|wc -l'''
    out = commands.getstatusoutput(checkcommand)
    print out
    if(out[1] == '0'):#no key exist
        genkeycommand = '''aws ec2 create-key-pair --key-name ec2backup-keypair --query 'KeyMaterial' --output text > ~/.ssh/ec2backup-keypair.pem && chmod 600 ~/.ssh/ec2backup-keypair.pem''' 
        out = commands.getstatusoutput(genkeycommand)
        print out
    return '~/.ssh/ec2backup-keypair.pem'

#=======================
#Delete key
#TODO: handle key name del local key
#======================
def delkey(keyname = 'ec2backup-keypair'):
    deletekeycommand = '''aws ec2 delete-key-pair --key-name ec2backup-keypair '''\
            +'''&& rm ~/.ssh/ec2backup-keypair.pem'''
    out = commands.getstatusoutput(deletekeycommand)
    print out


#=======================
#TODO:security group gen
#Default security group name: ec2backup-security-group
#=======================
def securitygroupgen():
    checkcommand = '''aws ec2 describe-security-groups | grep '"GroupName": "ec2backup-security-group",'| wc -l '''
    out = commands.getstatusoutput(checkcommand)
    if (out[1] == '0'):#no group exist
        gensecuritycommand = '''aws ec2 create-security-group --group-name ec2backup-security-group --description "My ec2backup-security-group"'''
        addrulecommand = '''aws ec2 authorize-security-group-ingress --group-name ec2backup-security-group --protocol tcp --port 22 --cidr 0.0.0.0/0'''
        out = commands.getstatusoutput(gensecuritycommand)
        print out
        out = commands.getstatusoutput(addrulecommand)
        print out
    return 'ec2backup-security-group'
#==============================
#Delete sec group ec2backup-security-group
#=============================
def delsecgroup():
    delgroupcommand = "aws ec2 delete-security-group --group-name ec2backup-security-group"
    out = commands.getstatusoutput(delgroupcommand)

#==============================
#Shutdown or del key or del sec group if needed
#==============================
def clean():
    global KEYPAIR_LOCATION, SECURITY_GROUP, EC2_INSTANCE_ID
    if (len(EC2_INSTANCE_ID)>1):
        terminatecommand = "aws ec2 terminate-instances --instance-ids "\
                +EC2_INSTANCE_ID
        out = commands.getstatusoutput(terminatecommand)
    if(KEYPAIR_LOCATION == "~/.ssh/ec2backup-keypair.pem"):
        delkey()
    if(SECURITY_GROUP == "ec2backup-security-group"):
        delsecgroup()

#==============================
#TODO: use 'dd' or 'rsync' backup
#==============================
def dobackup(method):
	global SOURCE_DIR,KEYPAIR_LOCATION,INSTANCE_LOGIN_USR,EC2_HOST,MOUNT_DIR_LOCATION
	if (method == 'dd'):
		command = "tar -zcvf  %s_backup.tar.gz %s"%(SOURCE_DIR,SOURCE_DIR)
		output = commands.getstatusoutput(command)
		command =" dd if=%s_backup.tar.gz \" ssh -i %s %s@%s \" dd of=%s/backup.tar.gz"%(SOURCE_DIR,KEYPAIR_LOCATION,INSTANCE_LOGIN_USR,EC2_HOST,MOUNT_DIR_LOCATION)
		output = commands.getstatusoutput(command)
		command = "rm -rf %s_backup.tar.gz"%(SOURCE_DIR)
		output = commands.getstatusoutput(command)
	else:
		command = "rsync -e \"ssh -i %s\" -az %s %s@%s:%s/ >out.txt"%(KEYPAIR_LOCATION, SOURCE_DIR, INSTANCE_LOGIN_USR, EC2_HOST, MOUNT_DIR_LOCATION)


#================================
# create volume and output the
#  volumeid
#================================

def createvolumes():
    global VOLUME_SIZE,AVA_ZONE,VOLUME_ID
    command="aws ec2 create-volume --size %d --availability-zone %s | grep VolumeId"%(VOLUME_SIZE,AVA_ZONE)
    print command
    out = commands.getstatusoutput(command)
    VOLUME_ID=out[1][-15:-3]
    print "volume id",VOLUME_ID
    time.sleep(5)
    print "createvolume",out

#================================
#attach volume to running instance
#===============================
def attach():
    global VOLUME_ID,EC2_INSTANCE_ID,MOUNT_DEV_LOCATION
    command="aws ec2 attach-volume --volume-id %s --instance-id %s --device %s"%(VOLUME_ID,EC2_INSTANCE_ID,MOUNT_DEV_LOCATION)
    print command
    out = commands.getstatusoutput(command)
    print "attach",out

#===============================
#mount dir to instance
#===============================
def mountvolume():
	global KEYPAIR_LOCATION, INSTANCE_LOGIN_USR, EC2_HOST, MOUNT_DEV_LOCATION, MOUNT_DEV_LOCATION, MOUNT_DIR_LOCATION
        time.sleep(30)
	command=""
	if(MOUNT_DIR_LOCATION == ''):
		command = "ssh -i %s %s@%s \"sudo mkfs -t ext3 %s && mkdir /mnt/data-store && mount %s %s && exit\" "%(KEYPAIR_LOCATION, INSTANCE_LOGIN_USR, EC2_HOST, MOUNT_DEV_LOCATION, MOUNT_DEV_LOCATION, MOUNT_DIR_LOCATION)
		
	else:
		command = "ssh -t -i %s -o StrictHostKeyChecking=no %s@%s \" sudo sleep 5; sudo mkfs -F %s; sudo sleep 5;sudo mkdir %s;sudo mount %s %s; exit\""%(KEYPAIR_LOCATION, INSTANCE_LOGIN_USR, EC2_HOST,MOUNT_DEV_LOCATION,MOUNT_DIR_LOCATION,MOUNT_DEV_LOCATION,MOUNT_DIR_LOCATION)
		print command
        	out=commands.getstatusoutput(command)
        	print "mountvolume",out
#================
#Delete security group
# TODO: handle groupname
#================
def delsecuritygroup(groupname = 'ec2backup-security-group'):
    deletegroupcommand = '''aws ec2 delete-security-group --group-name ec2backup-security-group'''
    out = commands.getstatusoutput(deletegroupcommand)
    print out


#=============
#
#=============
def main(argv):
    global KEYPAIR_LOCATION, INSTANCE_LOGIN_USR, EC2_HOST ,VERBOSE
    global VOLUME_ID, SOURCE_DIR, SOURCE_DIR_SIZE
    method='dd'
    volumeid = ''
    directory = ''
    #================
    #Parse Argument
    #================
    try:
        opts, args = getopt.getopt(argv,"hm:v:",["method=","volumeid="])
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    for opt,arg in opts:
        if opt == '-h':
            usage()
            sys.exit(0)
        elif opt in ("-m", "--method"):
            if(arg!='dd' and arg!='rsync'):
                print "Error: Unknow methods:",arg
                usage()
                error("Unknow methods "+arg)
            method = arg
        elif opt in ("-v", "--volumeid"):
            VOLUME_ID = arg
            volumeid = arg

    if(len(args)==1):
        directory = args[0]
    else:
        usage()
        error("Need one directory")
    
    print "methods=", method
    print "volumeid=", volumeid
    print "Directory=", directory
    print "full path=", full_path(directory)
    print "path exist=", checkdir(directory)

    if(os.environ.get('VERBOSE')!=None):
    	VERBOSE = 1
        print "VERBOSE detected"
    if(checkdir(directory) == False):
        error ("directory not exist")
    SOURCE_DIR = full_path(directory)
    SOURCE_DIR_SIZE = getdirsize(SOURCE_DIR)
    calculate()#calculate VOL size 
    message(" launch ec2 instance")
    launchec2()
    createvolumes()
    attach()
    mountvolume()
    dobackup(method)
    clean()#delkey delgroup shutdown instances

if __name__ == "__main__":
    main(sys.argv[1:])
