# inject_static

This is a program that automate deletion and injection of a static routes on Cisco Nexus switches using Python to interact with NXAPI.

To run this program you'll need the following:
Host file - you can edit the host.txt file in this repo.
A common credential for accessing the host devices in the host file

Run as# python inject_static.py --username <username> --password <password> --hostfile host.txt --nexthop <nexthop ip>

The expected behaviour of this script is as follows:
Upon execution this script will jump on each device listed in the host file and sequentially delete a set of ip routes with a vrf (access) and then inject a new route with nexthop argument appended.

I'll appreciate your feedback on this script and please feel free to branch out and make improvements as necessary.
