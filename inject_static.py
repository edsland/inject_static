import requests
import json
import getpass
import argparse
from pprint import pprint

""" The goal of this script is to remove a set of unwanted static routes and inject a new static route within a vrf """
#
# This function uses argpase to enable user to supply --username, --password, --hostfile and --nexthop as arguments to run script
def parse_args():
    parser = argparse.ArgumentParser(
                                    description = 'Delete and Inject static routes')
    parser.add_argument('--verbose', action='store_true',
                       help='provide additional output for verification')
    parser.add_argument('--username', help='username for SSH connections')
    parser.add_argument('--password', help='password for SSH username')
    parser.add_argument('--hostfile', help='source file for list of hosts',
                        required = True)
    parser.add_argument('--nexthop', help='nexthop for static route',
                        required = True)
    args = parser.parse_args()

    if args.verbose:
        global_verbose = True
    else:
        global_verbose = False

    if args.username:
        ssh_username = args.username
    else:
        ssh_username = raw_input("Enter Username: ")
    if args.password:
        ssh_password = args.password
    else:
        ssh_password = getpass.getpass("Enter Password: ")
    if args.nexthop:
        nexthop = args.nexthop
    else:
        nexthop = raw_input("Enter Next-Hop IP: ")

    try:
        with open(args.hostfile, 'r') as f:
            host_list = f.read().splitlines()
    except:
        quit("host file cannot be found")

    host_list = [x for x in host_list if x[0] != "#"]

    return global_verbose, ssh_username, ssh_password, host_list, nexthop
#
# This function will either interact with nxapi to either get or push info
def go_configure(host, user, passwd, cmd, cmd_type):
    myheaders = {'content-type': 'application/json'}
    url = "http://"+host+"/ins"
    username = user
    password = passwd        
    payload= {"ins_api": {"version": "1.0", "type": cmd_type, "chunk": "0", "sid": "1", "input": cmd, "output_format": "json"}}         
    response = requests.post(url,data=json.dumps(payload),headers=myheaders,auth=(username,password)).json()
    mydict = response
    #
    #Error checking block
    #this if statement catches errors in group of commands
    mylen = len(mydict['ins_api']['outputs']['output'])
    for i in range(mylen):
        if mydict['ins_api']['outputs']['output'][i]['code'] == '200' and mydict['ins_api']['outputs']['output'][i]['msg'] == 'Success':
            return "SUCCESS"
        elif mydict['ins_api']['outputs']['output'][i]['code'] == '400' and mydict['ins_api']['outputs']['output'][i]['clierror'] == '% Route not deleted, it does not exist\n':
            return "SUCCESS"
        else:
            print mydict['ins_api']['outputs']['output']
            return "FAIL"

#Main code block
#
def main():
    #get arguments
    global_verbose, ssh_username, ssh_password, host_list, nexthop = parse_args()
    #global variables
    display = "*"*60
    display2 = "-"*30
    new_route = 'ip route 99.0.0.0/8 ' + nexthop.strip()
    cmd_string1 = ("vrf context access  ;no ip route 99.0.0.0/8 10.30.1.222", 
                   "vrf context access  ;no ip route 99.0.0.0/8 10.30.1.223", 
                   "vrf context access  ;no ip route 99.0.0.0/8 10.30.1.22", 
                   "vrf context access  ;no ip route 99.0.0.0/8 10.30.1.23")
    cmd_string2 = "vrf context access ;"+ new_route
    cmd_type = ("cli_show", "cli_conf")

    print display
    print "Welcome to Static Route Injector"
    print display + '\n'
    #
    for host in host_list:
        host = host.strip()
        #
        print 'Working on Host: {}'.format(host)
        print "VRF: access" 
        print display2
        #
        for cmd in cmd_string1:
            if go_configure(host, ssh_username, ssh_password, cmd, cmd_type[1]) == "SUCCESS":
                print "Deleting routes: {} ----- SUCCESS".format(cmd.split(";")[1])
                #for i in cmd_string1.split(";")[1:]:
                #    print i                
            else:
                print "Command {} ----- FAIL".format(cmd)
        #
        print "" + '\n'

        if go_configure(host, ssh_username, ssh_password, cmd_string2, cmd_type[1]) == "SUCCESS":
            print "Injecting route : {} ----- SUCCESS".format(new_route)
        else:
            print "Command {} ----- FAIL".format(new_route)
        #
        print "" + '\n'
    #
    print "------------------ Script execution completed ------------------" + '\n'       

#__main__
if __name__ == '__main__':
    main()


