import SoftLayer
from SoftLayer import VSManager, ISCSIManager, ImageManager, SshKeyManager, Client
import os, argparse, sys, time, simplejson
from datetime import datetime


parser = argparse.ArgumentParser()

parser.add_argument("--username", default="")
parser.add_argument("--apiKey", default="")

parser.add_argument("--hostname")
parser.add_argument("--domain")
parser.add_argument("--sshKeyName")


args = parser.parse_args()

username = args.username
apiKey = args.apiKey

if (args.username != ''):
	username = args.username
	apiKey = args.apiKey
else:
	username = os.environ.get('SOFTLAYER_USERNAME', '')
	apiKey = os.environ.get('SOFTLAYER_APIKEY','')


endpoint_url = SoftLayer.API_PUBLIC_ENDPOINT
client = Client(username=username, api_key=apiKey, endpoint_url=endpoint_url)


#############################################################################
#############################################################################

tag = 'poc-image-test'
datacenter = 'mex01'

#############################################################################
#############################################################################


def listSSHKeys(label=None):
	sshManager = SshKeyManager(client)
	sshKeys = sshManager.list_keys(label=label)
	return sshKeys

def createImage(id, name, notes):
	vsManager = VSManager(client)
	image = vsManager.capture(instance_id=id,name=name,additional_disks=True,notes=notes)
	return image

def deleteImage(id):
	imgManager = ImageManager(client)
	imgManager.delete_image(image_id=id)

def listImages(name=None):
	imgManager = ImageManager(client)
	imgs = imgManager.list_private_images(name=name)
	return imgs

def getInstance(id):
	try:
		vsManager = VSManager(client)
		instance = vsManager.get_instance(id)
		return instance
	except:
		return None

def getInstances():
	vsManager = VSManager(client)
	instances = vsManager.list_instances(tags=tags,datacenter=datacenter)
	return instances

def cancelInstance(id):
	vsManager = VSManager(client)
	vsManager.cancel_instance(id)
	print 'Canceling : ' + str(id)

def orderServer(hostname,domain,datacenter,cpus,memory,hourly,os_code,image_id,local_disk,disks,nic_speed,post_uri,ssh_keys,private,dedicated,private_vlan,tags):
	vsManager = VSManager(client)
	instance = vsManager.create_instance(
		hostname = hostname,
		domain = domain,
		datacenter = datacenter,
		cpus = cpus,
		memory = memory,
		hourly = hourly,
		os_code = os_code,
		image_id = image_id,
		local_disk = local_disk,
		disks = disks, # [] if image
		nic_speed = nic_speed,
		post_uri = post_uri,
		ssh_keys = ssh_keys,
		private = private,
		dedicated = dedicated,
		private_vlan = private_vlan,
		tags = tags)

	#print simplejson.dumps(instance, sort_keys=True, indent=4 * ' ')
	return instance


######################
######################
######################



# Get SSH Keys
keys = []
if (sshKeyName != None):
	for k in listSSHKeys(sshKeyName):
		keys.append(k['id'])

# Create an instance
instance1 = orderServer(hostname=hostname,domain=domain,datacenter=datacenter,cpus=1,memory=1024,hourly=True,os_code='UBUNTU_LATEST',image_id='',local_disk=True,disks=[25],nic_speed=1000,post_uri='',ssh_keys=keys,private=False,dedicated=False,private_vlan=0,tags=tag)
instance1Id = instance1['id']
instance1Name = instance1['hostname']
print simplejson.dumps(instance1, sort_keys=True, indent=4 * ' ')

# Wait till provisioned
completed = False
while completed == False:
	time.sleep(60)
	print '.'
	instance = getInstance(instance1Id)
	if instance != None and instance.has_key('provisionDate') and instance['provisionDate'] != '':
		completed = True

#	(This works also if looking in a shorter timeout, but activeTransaction isn't always available)
# 	if instance != None and 'activeTransaction' in instance.keys():
# 		activeTransaction = instance['activeTransaction']['transactionStatus']['name']
# 		if activeTransaction == 'SERVICE_SETUP':
# 			completed = True


# Pause for 5 minutes to stabilize vm
print 'Pause for 5 minutes'
time.sleep(300)


# Create an Image
print 'Creating Image'
imageName = 'img-' + instance1Name
image = createImage(instance1Id,imageName, None)
print simplejson.dumps(image, sort_keys=True, indent=4 * ' ')


# Pause for 5 minutes for Image creation
print 'Pause for 5 minutes'
time.sleep(300)


# Get created Image by Name
images = listImages(imageName)
print simplejson.dumps(images, sort_keys=True, indent=4 * ' ')
imageId = images[0]['id']
imageGuid = images[0]['globalIdentifier']


# Deploy new instance from image
# When deployign from Image, specify Image Id, but do not include OS or disk sizes as this will come from the Image
hostname2 = hostname + 'b'
instance2 = orderServer(hostname=hostname2,domain=domain,datacenter=datacenter,cpus=1,memory=1024,hourly=True,os_code=None,image_id=imageGuid,local_disk=True,disks=None,nic_speed=1000,post_uri='',ssh_keys=keys,private=False,dedicated=False,private_vlan=0,tags=tag)
print simplejson.dumps(instance2, sort_keys=True, indent=4 * ' ')
instance2Id = instance2['id']
instance2Name = instance2['hostname']

completed = False
while completed == False:
	time.sleep(60)
	completed = True
	print '.'
	instances = getInstances()
	for instance in instances:
		if instance != None and instance.has_key('provisionDate') and instance['provisionDate'] != '':
			completed = True


# Cancel Both Instances
print 'Pause for 2 minutes'
time.sleep(1200)
instances = getInstances(tag)
for instance in instances:
	try:
		if instance['id'] != 0:
			cancelInstance(instance['id'])
	except:
		print 'Skipping: ' + str(instance['id'])

# Remove Image
deleteImage(imageId)


#[id,hostname,domain,fullyQualifiedDomainName,datacenter,powerState,status,primaryIpAddress]
#object_mask = 'mask[backendNetworkComponents,tagReferences[id,tag[name,id]]]'
#instances = vs.list_instances(mask=object_mask)
#print simplejson.dumps(instances, sort_keys=True, indent=4 * ' ')	



