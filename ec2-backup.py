#!/usr/bin/python
#
# Filename : ec2-backup.py
# Author   : Kun Yao
#            Dainong Ma
#            Zhe Wang
#iijiji

import sys, getopt, os

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
#TODO: Estimate total storage for dir
#==============================
def estimatedir(directory):
    pass

#===============================
#TODO: Create EC2 instance and 
#        set up connection
#===============================
def lanuchec2():
    pass

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
