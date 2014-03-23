#!/usr/bin/python
#
# Filename : ec2-backup.py
# Author   : Kun Yao
#            Dainong Ma
#            Zhe Wang
#            Yufei Li

import sys, getopt

#=======================
#Print the usage message
#=======================
def usage():
    print 'Usage:'
    print '  ec2-backup [-h] [-m method] [-v volume-id] dir'
    sys.exit()

#================================
#TODO: Check the validlity of directory
#================================
def checkdir(directory):
    return True

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

if __name__ == "__main__":
    main(sys.argv[1:])
