#!/usr/bin/python
#
# Filename : ec2-backup.py
# Author   : Kun Yao
#            Dainong Ma
#            Zhe Wang

import sys, getopt, os, commands

#=======================
#Print the usage message
#=======================
def usage():
    print 'Usage:'
    print '  ec2-backup [-h] [-m method] [-v volume-id] dir'
    sys.exit()

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

#===============================
#TODO: Create EC2 instance and 
#        set up connection
#===============================
def lanuchec2():
    command =      'aws ec2 run-instances'
    key =          '--key ec2backup-keypair'
    group =        '--groups ec2backup-security-group'
    instancetype = '--instance-type t1.micro'
    imageid =      '--image-id ami-2f726546'
    flags = os.environ.get('EC2_BACKUP_FLAGS_AWS')
    sshflags = os.environ.get('EC2_BACKUP_FLAGS_SSH')
    
    #parse aws flags
    if(flags != None):
        try:
            opts, args = getopt.getopt(flags.split(),"i:",["instance-type="])
        except getopt.GetoptError:
            usage()
        for opt,arg in opts:
            if opt == '-i':
                key = '--key '+ arg
            elif opt == '--instance-type':
                instancetype = '--instance-type '+arg
        if(len(arg)s>=1)
            print "unknow option detected in $EC2_BACKUP_FLAGS_SSH:", args
    
    #TODO:parse ssh flags

    #key and group gen
    keygen()
    securitygroupgen()

    #run ec2
    ec2command = command + key + group + instancetype + imageid
    
       
#========================
#TODO: Key pair gen SSH FLAGS HANDLE
# Defult key name: ec2backup-keypair
#=======================
def keygen():
    checkcommand = '''aws ec2 describe-key-pairs | grep '"KeyName": "ec2backup-keypair",'|wc -l'''
    out = commands.getstatusoutput(checkcommand)
    print out
    if(out[1] == '0'):#no key exist
        genkeycommand = '''aws ec2 create-key-pair --key-name ec2backup-keypair --query 'KeyMaterial' --output text > ~/.ssh/ec2backup-keypair.pem''' 
        out = commands.getstatusoutput(genkeycommand)
        print out

#=======================
#Delete key
#TODO: handle key name
#======================
def delkey(keyname = 'ec2backup-keypair'):
    deletekeycommand = '''aws ec2 delete-key-pair --key-name ec2backup-keypair'''
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

#================
#Delete security group
# TODO: handle groupname
#================
def delsecuritygroup(groupname = 'ec2backup-security-group'):
    deletegroupcommand = '''aws ec2 delete-security-group --group-name ec2backup-security-group'''
    out = commands.getstatusoutput(deletegroupcommand)
    print out

#==============================
#TODO: use 'dd' or 'rsync' backup
#==============================
def dobackup(method):
    pass

#=============
#
#=============
def main(argv):
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
    for opt,arg in opts:
        if opt == '-h':
            usage()
        elif opt in ("-m", "--method"):
            if(arg!='dd' and arg!='rsync'):
                print "Unknow methods:",arg
                usage()
            method = arg
        elif opt in ("-v", "--volumeid"):
            volumeid = arg

    if(len(args)==1):
        directory = args[0]
    else:
        print "Need one directory"
        usage()
    
    #==================
    #
    #==================
    print "methods=", method
    print "volumeid=", volumeid
    print "Directory=", directory
    print "full path=", full_path(directory)
    print "path exist=", checkdir(directory)
    

if __name__ == "__main__":
    main(sys.argv[1:])
