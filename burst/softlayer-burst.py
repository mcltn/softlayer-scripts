#!/usr/bin/env python

import os, sys, time, argparse, simplejson
import ConfigParser
import SoftLayer
from SoftLayer import VSManager, ImageManager, Client
from datetime import datetime

argParser = argparse.ArgumentParser()

argParser.add_argument("--username", default="")
argParser.add_argument("--apiKey", default="")

argParser.add_argument("--action", default="CREATE", choices=['GET', 'GET_USERDATA', 'LIST', 'LIST_IMAGES', 'CREATE', 'CAPTURE', 'CANCEL'])

argParser.add_argument("--configFile")


argParser.add_argument("--serverId", type=int)
argParser.add_argument("--tag", default="poc-burst")


argParser.add_argument("--hostname", default="poc")
argParser.add_argument("--domain", default="poc.softlayer.com")
argParser.add_argument("--datacenter", default="dal09")

argParser.add_argument("--hourly", action="store_true")
argParser.add_argument("--private", action="store_true")
argParser.add_argument("--dedicated", action="store_true")

argParser.add_argument("--cpus", default=1, type=int, choices=[1,2,4,8,12,16])
argParser.add_argument("--memory", default=1024, type=int, choices=[1024,2048,4096,6144,8192,12288,16384,32768,49152,65536])
argParser.add_argument("--localDisk", action="store_true")
argParser.add_argument("--localDisk1Size", default=25, type=int, choices=[25,100])
argParser.add_argument("--localDisk2Size", type=int, choices=[25,100,150,200,300])
argParser.add_argument("--sanDisk1Size", type=int, default=25, choices=[25,100])
argParser.add_argument("--sanDisk2Size", type=int, choices=[10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000])
argParser.add_argument("--sanDisk3Size", type=int, choices=[10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000])
argParser.add_argument("--sanDisk4Size", type=int, choices=[10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000])
argParser.add_argument("--sanDisk5Size", type=int, choices=[10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000])

argParser.add_argument("--osCode")
argParser.add_argument("--templateGuid")
argParser.add_argument("--templateName")   # Used when capturing an image
argParser.add_argument("--templateNotes")  # Used when capturing an image

argParser.add_argument("--privateVlan")
argParser.add_argument("--publicVlan")
argParser.add_argument("--nicSpeed", type=int, default=100, choices=[10,100,1000])

argParser.add_argument("--sshKey", default="")
argParser.add_argument("--postInstallUrl", default="")

argParser.add_argument("--verbose", action="store_true")
argParser.add_argument("--logFileName", default="")
argParser.add_argument("--waitForCompletion", action="store_true")

args = argParser.parse_args()


endpoint_url = SoftLayer.API_PUBLIC_ENDPOINT

#############################################################################
#############################################################################

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
    print simplejson.dumps(instance, sort_keys=True, indent=4 * ' ')
    return instance


def getInstances(tag):
    vsManager = VSManager(client)
    instances = vsManager.list_instances(tags = [tag])
    print simplejson.dumps(instances, sort_keys=True, indent=4 * ' ')
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


def orderServer(hostname, domain, cpus, memory, disk, osCode, useLocalDisk, datacenter, private, dedicated, hourly, tag, privateVlan, nicSpeed, sshKey, userData, postInstallUrl):

    disks = []
    disks.append(disk)

    templateGuid = ''
    if (osCode != None and osCode != ''):
        templateGuid = ''
    else:
        osCode = ''
        disks = [] # Blank out disks since it will use the template

    sshKeys = []
    if (sshKey != None and sshKey != ''):
        sshKeys.append(sshKey)

    vsManager = VSManager(client)
    instance = vsManager.create_instance(
        hostname = hostname,
        domain = domain,
        cpus = cpus,
        memory = memory,
        hourly = hourly,
        datacenter = datacenter,
        os_code = osCode,
        image_id = templateGuid,
        local_disk = useLocalDisk,
        disks = disks,
        ssh_keys = sshKeys,
        nic_speed = nicSpeed,
        private = private,
        private_vlan = privateVlan,
        dedicated = dedicated,
        post_uri = postInstallUrl,
        userdata = userData,
        tags = tag)

    return instance


def provisionServersFromConfig():
    print 'Begin: ' + time.strftime('%Y-%m-%d %I:%M:%S %Z')
    
    jsonFile = open(args.configFile).read()
    configJson = simplejson.loads(jsonFile)
    print simplejson.dumps(configJson, sort_keys=True, indent=4 * ' ')

    for host in configJson['hosts']:

        hostname = host.get('hostname')
        domain = host.get('domain', configJson['domain'])
        cpus = host.get('cpus', configJson['cpus'])
        memory = host.get('memory', configJson['memory'])
        disk = host.get('disk', configJson['disk'])
        osCode = host.get('osCode', configJson['osCode'])
        useLocalDisk = host.get('localDisk', configJson['localDisk'])
        datacenter = host.get('datacenter', configJson['datacenter'])
        private = host.get('private', configJson['private'])
        dedicated = host.get('dedicated', configJson['dedicated'])
        hourly = host.get('hourly', configJson['hourly'])
        tag = host.get('tag', configJson['tag'])
        privateVlan = host.get('privateVlan', configJson['privateVlan'])
        nicSpeed = host.get('nicSpeed', configJson['nicSpeed'])
        sshKey = host.get('sshKey', configJson['sshKey'])
        postInstallUrl = host.get('postInstallUrl', configJson['postInstallUrl'])

        privateIPAddress = host.get('privateIPAddress')

        userData = '{"hostname": "' + str(hostname) + '", "privateIPAddress": "' + str(privateIPAddress) + '"}'

        createdInstance = orderServer(hostname, domain, cpus, memory, disk, osCode, useLocalDisk, datacenter, private, dedicated, hourly, tag, privateVlan, nicSpeed, sshKey, userData, postInstallUrl)
        createdId = createdInstance['id']
        if (args.verbose):
            print 'Built Server: ' + str(createdId)

    print 'Completed: ' + time.strftime('%Y-%m-%d %I:%M:%S %Z')


def getVirtualGuestUserData(id):
    print 'Getting user data'
    userdata = client['SoftLayer_Virtual_Guest'].getUserData(id=id)
    json = simplejson.loads(userdata[0]['value'])
    print json['hostname']
    print json['privateIPAddress']
    return userdata


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
    client = Client(username=username, api_key=apiKey, endpoint_url=endpoint_url)

    if (args.action == 'GET'):
        print 'Getting server...'
        getInstance(args.serverId)
    elif (args.action == 'GET_USERDATA'):
        print 'Getting server metadata...'
        getVirtualGuestUserData(args.serverId)
    elif (args.action == 'LIST'):
        print 'Listing servers...'
        getInstances(args.tag)
    elif (args.action == 'CREATE'):
        print 'Creating servers...'
        provisionServersFromConfig()
    elif (args.action == 'LIST_IMAGES'):
        print 'Listing images...'
        listImages()
    elif (args.action == 'CAPTURE'):
        print 'Capturing server...'
        #captureImage()
    elif (args.action == 'CANCEL'):
        print 'Canceling servers...'
        if (args.tag != None and args.tag != ''):
            cancelServers(args.tag)
        if (args.serverId != None):
            cancelInstance(args.serverId)
