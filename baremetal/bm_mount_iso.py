from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import SoftLayer
import simplejson, re, time, argparse
from itertools import repeat

import pexpect
import subprocess

############################################################
############################################################
### USAGE:
### python kickstart.py --serverId 442802
### python kickstart.py --serverId 442802 --unmount
###
###
### This script uses the CLI tools provided by each
### manufacturer. Download the appropriate version for
### your OS.
###
### Lenovo
### https://support.lenovo.com/us/en/solutions/lnvo-asu
### http://support.lenovo.com/us/en/downloads/ds118233
### http://support.lenovo.com/us/en/downloads/ds118237
###
### SuperMicro
### https://www.supermicro.com/solutions/SMS_IPMI.cfm
### ftp://ftp.supermicro.com/utility/SMCIPMItool/SMCIPMITool_User_Guide.pdf
###
###
### This script also uses the SoftLayer client library
### to gather information about the baremetal server. 
### Be sure to have environment variables saved via the
### Softlayer CLI (> slcli setup)
############################################################
############################################################


############################################################
### Setup command line arguments to use
###
### --serverId : Pass in an existing Server ID
### --iso : Pass in the path to the ISO file
### --unmount : Optional, is False by default. Do not provide if mounting
parser = argparse.ArgumentParser(description="Mount or Unmount an ISO to a Bare Metal server.")
parser.add_argument("--serverId", help="Server ID", default=0)
parser.add_argument("--iso", help="ISO File location path", default="")
parser.add_argument("--unmount", action="store_false", help="Unmount ISO")

args = parser.parse_args()

client = SoftLayer.create_client_from_env()


#########################################################
### Set path locations of the Lenovo and SuperMicro CLI
### tools. These will be used to interact with the server.
### Also set the path to the local location of the ISO
### image that will be mounted. 
lenovo_rdmount_path = '/root/rdcli-x86_64/rdmount'
lenovo_rdumount_path = '/root/rdcli-x86_64/rdumount'
supermicro_smcipmitool_path = '/root/SMCIPMITool/SMCIPMITool'

hardware_id = args.serverId
iso_file_path = args.iso #'/root/rdcli-x86_64/ubuntu-16.04.2-server-amd64.iso'
mount = args.unmount

ipmiIpAddress = ''
ipmiUsername = ''
ipmiPassword = ''
privateIpAddress = ''
publicIpAddress = ''
motherboard = ''
#########################################################
#########################################################



#########################################################
### Order Baremetal Server if no ID provided
### You could put code here to place an order then poll
### till available for use. Capture the hardware Id.
#########################################################



#########################################################
### Collect the assigned IP Addresses 
### (Public,Private,IPMI) and IPMI Credentials
mask = 'id,hostname,components.hardwareComponentModel.hardwareGenericComponentModel.hardwareComponentType,components.hardwareComponentModel.manufacturer,networkComponents,remoteManagementAccounts.username,remoteManagementAccounts.password'
bm_server = client['Hardware'].getObject(id=hardware_id, mask=mask)
print (simplejson.dumps(bm_server, sort_keys=True, indent=4 * ' '))

### Get Motherboard info
for component in bm_server['components']:
	if component['hardwareComponentModel']['hardwareGenericComponentModel']['hardwareComponentType']['keyName'] == 'MOTHERBOARD':
		motherboard = component['hardwareComponentModel']['manufacturer']

### Get IP and IPMI info
for component in bm_server['networkComponents']:
	if component['name'] == 'mgmt':
		ipmiIpAddress = component['ipmiIpAddress']
	elif component['name'] == 'eth' and component['status'] == 'ACTIVE' and 'primaryIpAddress' in component:
		if component['primaryIpAddress'].startswith('10.'):
			privateIpAddress = component['primaryIpAddress']
		else:
			publicIpAddress = component['primaryIpAddress']

ipmiUsername = bm_server['remoteManagementAccounts'][0]['username']
ipmiPassword = bm_server['remoteManagementAccounts'][0]['password']
#########################################################
print (ipmiIpAddress)
print (ipmiUsername)
print (ipmiPassword)
print (motherboard)
################################################################


####################################################
### Unmount ISO Functions
def unmount_Lenovo():
	### Query for current mount status
	cmd = [lenovo_rdmount_path, '-s ' + ipmiIpAddress, '-l ' + ipmiUsername, '-p ' + ipmiPassword, '-q']
	print ('### CHECK MOUNT STATUS ###')
	q = subprocess.check_output(cmd)
	print (q)
	time.sleep(2)
	if 'Token ' in q: # If Token found, unmount
		result = re.search('Token (.+?):', q)
		token = result.group(1)
		print (token)
		cmd = lenovo_rdumount_path + ' ' + token + ' -s ' + ipmiIpAddress
		print ('### UNMOUNT ###')
		um = subprocess.call(cmd, shell=True)
		time.sleep(2)

def unmount_SuperMicro():
	cmd = supermicro_smcipmitool_path + ' ' + ipmiIpAddress + ' ' + ipmiUsername + ' ' + ipmiPassword + ' shell'
	############################
	proc = pexpect.spawnu(cmd)
	proc.expect('.*ASPD.*')
	print (proc.after)
	proc.sendline('vmwa stop 2')
	proc.expect('.*ASPD.*')
	print (proc.after)

################################################################
### Configure IPMI
### Will choose the tools to use based on motherboard

if mount == True and motherboard == 'Lenovo':
	print ("### LENOVO ###")
	unmount_Lenovo()

	cmd = lenovo_rdmount_path + ' -s ' + ipmiIpAddress + ' -d ' + iso_file_path + ' -l ' + ipmiUsername + ' -p ' + ipmiPassword
	print ('### MOUNTING ###')
	m = subprocess.call(cmd, shell=True)
	print (m)

elif mount == True and motherboard == 'SuperMicro':
	print ("### SUPERMICRO ###")
	cmd = supermicro_smcipmitool_path + ' ' + ipmiIpAddress + ' ' + ipmiUsername + ' ' + ipmiPassword + ' shell'
	print (cmd)

	############################
	proc = pexpect.spawnu(cmd)
	#time.sleep(3)
	proc.expect('.*ASPD.*')
	#print (proc.before)
	print (proc.after)
	proc.sendline('vmwa status')
	proc.expect('.*ASPD.*')
	print (proc.after)

	iso_cmd = 'vmwa dev2iso ' + iso_file_path
	proc.sendline(iso_cmd)
	proc.expect('.*ASPD.*')
	print (proc.after)

	proc.sendline('ipmi power cycle')
	proc.expect('.*ASPD.*')
	print (proc.after)

	print ('sleeping 3 minutes')
	time.sleep(180)
	proc.sendline('exit')

################################################################


################################################################
### Reboot Server using SoftLayer API
if mount == True and motherboard == 'Lenovo':
	print ('### Rebooting ###')
	bm_reboot = client['Hardware'].rebootHard(id=hardware_id)
	print (bm_reboot)
################################################################

################################################################
### Ubmount the ISO from the server
if mount == False and motherboard == 'Lenovo':
	### Use rdumount to Unmount the ISO
	print ('### Unmounting ###')
	unmount_Lenovo()

elif mount == False and motherboard == 'SuperMicro':
	print ('### Unmounting ###')
	unmount_SuperMicro()

################################################################

