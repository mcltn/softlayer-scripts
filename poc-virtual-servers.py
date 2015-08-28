#!/usr/bin/env python

import os, sys, time, argparse, simplejson
import SoftLayer
from SoftLayer import VSManager, ISCSIManager, ImageManager, Client
from datetime import datetime

parser = argparse.ArgumentParser()

parser.add_argument("--username", default="")
parser.add_argument("--apiKey", default="")

parser.add_argument("--action", default="CREATE", choices=['LIST','CREATE','CAPTURE','CANCEL'])

parser.add_argument("--serverId", type=int)

parser.add_argument("--serverCount", default=1)
parser.add_argument("--uniqueId", default="")
parser.add_argument("--tag", default="poc-swat")

parser.add_argument("--hostname", default="poc")
parser.add_argument("--domain", default="poc.softlayer.com")
parser.add_argument("--datacenter", default="dal09")

parser.add_argument("--hourly", action="store_true")
parser.add_argument("--private", action="store_true")
parser.add_argument("--dedicated", action="store_true")

parser.add_argument("--cpus", default=1, type=int, choices=[1,2,4,8,12,16])
parser.add_argument("--memory", default=1024, type=int, choices=[1024,2048,4096,6144,8192,12288,16384,32768,49152,65536])
parser.add_argument("--localDisk", action="store_true")
parser.add_argument("--localDisk1Size", default=25, type=int, choices=[25,100])
parser.add_argument("--localDisk2Size", type=int, choices=[25,100,150,200,300])
parser.add_argument("--sanDisk1Size", type=int, default=25, choices=[25,100])
parser.add_argument("--sanDisk2Size", type=int, choices=[10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000])
parser.add_argument("--sanDisk3Size", type=int, choices=[10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000])
parser.add_argument("--sanDisk4Size", type=int, choices=[10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000])
parser.add_argument("--sanDisk5Size", type=int, choices=[10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000])

parser.add_argument("--osCode")
parser.add_argument("--templateGuid")
parser.add_argument("--templateName")	# Used when capturing an image
parser.add_argument("--templateNotes")	# Used when capturing an image

parser.add_argument("--privateVlan")
parser.add_argument("--publicVlan")
parser.add_argument("--nicSpeed", type=int, default=100, choices=[10,100,1000])

parser.add_argument("--sshKey", default="")
parser.add_argument("--postInstallUrl", default="")

parser.add_argument("--verbose", action="store_true")
parser.add_argument("--reportFileName", default="")
parser.add_argument("--waitForCompletion", action="store_true")

args = parser.parse_args()


#############################################################################
#############################################################################

def dateDiff(t1,t2):
	tdelta = t2 - t1
	return tdelta


def listImages():
	imgManager = ImageManager(client)
	imgs = imgManager.list_private_images()
	return imgs


def getCreateOptions():
	vsManager = VSManager(client)
	options = vsManager.get_create_options()
	return options


def getInstance(id):
	vsManager = VSManager(client)
	instance = vsManager.get_instance(id)
	return instance


def getInstances(tag):
	vsManager = VSManager(client)
	instances = vsManager.list_instances(tags = [tag])
	return instances


def cancelInstance(id):
	vsManager = VSManager(client)
	vsManager.cancel_instance(id)
	print 'Canceling: ' + str(id)


def cancelServers(tag):
	instances = getInstances(tag)
	for instance in instances:
		try:
			if instance['id'] != 0:
				cancelInstance(instance['id'])
		except:
			print 'Skipping: ' + str(instance['id'])


def captureImage(instanceId, name, additional_disks, notes):
	vsManager = VSManager(client)
	image = vsManager.capture(instanceId, name, additional_disks, notes)
	print 'Creating Image: ' + name
	return image.id # Returns just a transaction Id / Not the actual Image Id ??


def orderServer(counter):

	uniqueHostname = ''
	if (args.uniqueId != ''):
		uniqueHostname = args.uniqueId + "-"
	uniqueHostname += args.hostname + "-" + str(counter)

	if (args.verbose):
		print 'Building: ' + uniqueHostname

	disks = []
	if (args.localDisk):
		disks.append(args.localDisk1Size)
		if (args.localDisk and args.localDisk2Size != None):
			disks.append(args.localDisk2Size)
	else:
		disks.append(args.sanDisk1Size)
		if (args.sanDisk2Size != None):
			disks.append(args.sanDisk2Size)
		if (args.sanDisk3Size != None):
			disks.append(args.sanDisk3Size)
		if (args.sanDisk4Size != None):
			disks.append(args.sanDisk4Size)
		if (args.sanDisk5Size != None):
			disks.append(args.sanDisk5Size)

	osCode = ''
	templateGuid = ''
	if (args.osCode != None and args.osCode != ''):
		osCode = args.osCode
		templateGuid = ''
	else:
		osCode = ''
		templateGuid = args.templateGuid
		disks = [] # Blank out disks since it will use the template


	sshKeys = []
	if (args.sshKey != None and args.sshKey != ''):
		sshKeys.append(args.sshKey)

	vsManager = VSManager(client)
	instance = vsManager.create_instance(
		hostname = uniqueHostname,
		domain = args.domain,
		cpus = args.cpus,
		memory = args.memory,
		hourly = args.hourly,
		datacenter = args.datacenter,
		os_code = osCode,
		image_id = templateGuid,
		local_disk = args.localDisk,
		disks = disks,
		ssh_keys = sshKeys,
		nic_speed = args.nicSpeed,
		private = args.private,
		private_vlan = args.privateVlan,
		dedicated = args.dedicated,
		post_uri = args.postInstallUrl,
		tags = args.tag)

	return instance


def provisionServers():
	if (args.verbose):
		print 'Begin: ' + time.strftime('%Y-%m-%d %I:%M:%S %Z')
	
	completed = False
	totalServers = args.serverCount
	counter = 1

	while completed == False:

		if (counter <= totalServers):
			createdInstance = orderServer(counter)
			createdId = createdInstance['id']
			if (args.verbose):
				print 'Built Server: ' + str(createdId)
				print simplejson.dumps(createdInstance, sort_keys=True, indent=4 * ' ')
			results[createdId] = {'createDate': createdInstance['createDate'], 'provisionState': 'BUILDING', 'status':[] }
			counter += 1
		elif (args.waitForCompletion == False):
			completed = True

		if (completed == False):
			if (args.verbose):
				print '.'
			time.sleep(1)

			instances = getInstances(args.tag)

			for instance in instances:
				instanceId = instance['id']
				if results[instanceId]['provisionState'] == 'BUILDING':
					if 'activeTransaction' in instance.keys():
						activeTransaction = instance['activeTransaction']['transactionStatus']['name']
						if not any(ss.get('name', None) == activeTransaction for ss in results[instanceId]['status']):
							results[instanceId]['status'].append({'name': activeTransaction, 'modifiedDate': time.strftime('%Y-%m-%d %I:%M:%S %Z') })

							if (args.verbose):
								print '\n' + activeTransaction
								print results
							if activeTransaction == 'SERVICE_SETUP':
								results[instanceId]['provisionState'] = 'COMPLETED'

			# Check all servers for provisionState
			exit = True
			for server in results:
				if results[server]['provisionState'] == 'BUILDING':
					exit = False

			if exit == True:
				completed = True

			if exit == False:
				runningTime = dateDiff(startTime, datetime.now())
				if runningTime.total_seconds > 5400: # 1 1/2 hour
					exit == True


	if (args.waitForCompletion and args.verbose):
		print 'Completed: ' + time.strftime('%Y-%m-%d %I:%M:%S %Z')
		print simplejson.dumps(results, sort_keys=True, indent=4 * ' ')

	if(args.waitForCompletion and args.reportFileName != ''):
		with open(args.reportFileName, "w") as result_file:
			result_file.write(str(results))


#############################################################################
#############################################################################

username = ''
apiKey = ''

if (args.username != ''):
	username = args.username
	apiKey = args.apiKey
else:
	username = os.environ.get('SOFTLAYER_USERNAME', '')
	apiKey = os.environ.get('SOFTLAYER_APIKEY','')

if (username == '' or apiKey == ''):
	print 'Please specify a username and apiKey\n'
else:
	endpoint_url = SoftLayer.API_PUBLIC_ENDPOINT
	client = Client(username=username, api_key=apiKey, endpoint_url=endpoint_url)

	startTime = datetime.now()
	results = {}

	if (args.action == 'LIST'):
		print 'Listing servers...'
		#listImages(args.tag)
	elif (args.action == 'CREATE'):
		print 'Creating servers...'
		provisionServers()
	elif (args.action == 'CAPTURE'):
		print 'Capturing server...'
		#captureImage()
	elif (args.action == 'CANCEL'):
		print 'Canceling servers...'
		if (args.tag != None):
			cancelServers(args.tag)
		if (args.serverId != None):
			cancelInstance(args.serverId)
