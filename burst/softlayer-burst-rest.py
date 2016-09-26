#!/usr/bin/env python

import os, sys, time, argparse, json, requests
import ConfigParser
from datetime import datetime


#################################################
#################################################
### Requirements:
###
### SoftLayer Python Library
### https://softlayer-api-python-client.readthedocs.io/en/latest/
###
###
### Examples:
###
### Create from Config File
### python softlayer-burst.py --username myusername --apiKey myapikey --action CREATE --configFile config-dal09p6.json
###
### Cancel by tag
### python softlayer-burst.py --username myusername --apiKey myapikey --action CANCEL --tag poc-burst
###
### Get Server UserData
### python softlayer-burst.py --username myusername --apiKey myapikey --action GET_USERDATA --serverId 24110049
###
###
#################################################
#################################################


argParser = argparse.ArgumentParser()

argParser.add_argument("--username", default="")
argParser.add_argument("--apiKey", default="")

argParser.add_argument("--action", default="CREATE", choices=['GET', 'GET_USERDATA', 'LIST', 'LIST_IMAGES', 'LIST_VLANS', 'CREATE', 'CAPTURE', 'CANCEL'])

argParser.add_argument("--configFile")


argParser.add_argument("--serverId", type=int)
argParser.add_argument("--tag", default="")


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

baseURL = 'https://api.softlayer.com/rest/v3'
username = args.username
apiKey = args.apiKey


#############################################################################
#############################################################################

def listImages():
    url = baseURL + '/SoftLayer_Account/getBlockDeviceTemplateGroups?objectMask=mask[datacenter]'
    r = requests.get(url, auth=(username, apiKey))
    imgs = r.json()
    print json.dumps(imgs, sort_keys=True, indent=4)
    return imgs


def listVlans():
    url = baseURL + '/SoftLayer_Account/getNetworkVlans'
    r = requests.get(url, auth=(username, apiKey))
    vlans = r.json()
    print json.dumps(vlans, sort_keys=True, indent=4)
    return vlans


def getInstance(serverId):
    url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId)

    url += '?objectMask=mask[id, hostname, host, primaryBackendNetworkComponent[router], serverRoom, location]'

    r = requests.get(url, auth=(username, apiKey))
    if (r.status_code == 200):
        result = r.json()
        print json.dumps(result, sort_keys=True, indent=4)
        return result
    else:
        return None


def getInstances(tag):
    if (tag == None or tag == ''):
        print 'Getting all virtual servers'
        url = baseURL + '/SoftLayer_Account/getVirtualGuests'
    else:
        print 'Getting servers by tag'
        url = baseURL + '/SoftLayer_Account/getVirtualGuests?objectFilter={"virtualGuests":{"tagReferences":{"tag":{"name":{"operation":"in","options":[{"name": "data", "value": ["'+ tag +'"]}]}}}}}'
    r = requests.get(url, auth=(username, apiKey))
    result = r.json()
    print json.dumps(result, sort_keys=True, indent=4)
    return result


def cancelInstance(serverId):
    url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId)
    r = requests.delete(url, auth=(username, apiKey))
    if (r.status_code == 200):
        print 'Cancelled: ' + str(serverId)
        return True
    else:
        return False


def cancelServers(tag):
    instances = getInstances(tag)
    for instance in instances:
        try:
            if instance['id'] != 0:
                cancelInstance(instance['id'])
        except:
            print 'Skipping: ' + str(instance['id'])


def captureImage(instanceId, name, additional_disks, notes):
    url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId) + '/getBlockDevices?objectMask=mask[diskImage]'
    r = requests.get(url, auth=(username, apiKey))
    result = r.json()
    print json.dumps(result, sort_keys=True, indent=4)

    blockId = result[0]['id']
    print str(blockId)

    url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId) + '/createArchiveTransaction'
    data = {'parameters':['given-image-name',[{'id': blockId}],'given-notes-info']}
    headers = {'Accept':'application/json','Content-Type':'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers, auth=(username, apiKey))
    result = r.json()
    print json.dumps(result, sort_keys=True, indent=4)


def orderServer(hostname, domain, cpus, memory, disk, osCode, templateGuid, useLocalDisk, datacenter, private, dedicated, hourly, tag, privateVlan, nicSpeed, sshKey, userData, postInstallUrl):

    disks = []
    disks.append(disk)

    if (osCode != None and osCode != ''):
        templateGuid = ''
    else:
        osCode = ''
        disks = [] # Blank out disks since it will use the template

    sshKeys = []
    if (sshKey != None and sshKey != ''):
        sshKeys.append(sshKey)

    url = baseURL + '/SoftLayer_Virtual_Guest'
    data = {"parameters": [ {"hostname": hostname, "domain": domain, "startCpus": cpus, "maxMemory": memory, "localDiskFlag": useLocalDisk, "privateNetworkOnlyFlag": private, "hourlyBillingFlag": hourly, "datacenter":{"name":datacenter}} ]}

    if len(sshKeys) > 0:
        keys = []
        for key in sshKeys:
            keys.append({"id": key})
        data['parameters'][0]['sshKeys'] = keys

    if privateVlan is not None:
        vlan = {'networkVlan': {'id':privateVlan}}
        data['parameters'][0]['primaryBackendNetworkComponent'] = vlan

    if osCode != "":
        data['parameters'][0]['blockDevices'] = [{"device":0, "diskImage": {"capacity":disk}}]
        data['parameters'][0]['operatingSystemReferenceCode'] = osCode

    if templateGuid != "" and osCode == "":
        data['parameters'][0]['blockDeviceTemplateGroup'] = {"globalIdentifier": templateGuid}

    data['parameters'][0]['networkComponents'] = [{"maxSpeed":nicSpeed}]

    print json.dumps(data, sort_keys=True, indent=4)
    headers = {'Accept':'application/json','Content-Type':'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers, auth=(username, apiKey))
    #print r.status_code
    #print r.json()
    #print '\n\n'
    if (r.status_code == 201):
        return r.json()
    else:
        print r.status_code
        print r.text
        return None


def provisionServersFromConfig():
    print 'Begin: ' + time.strftime('%Y-%m-%d %I:%M:%S %Z')
    
    jsonFile = open(args.configFile).read()
    configJson = json.loads(jsonFile)
    print json.dumps(configJson, sort_keys=True, indent=4)

    for host in configJson['hosts']:

        hostname = host.get('hostname')
        privateIPAddress = host.get('privateIPAddress')

        domain = host.get('domain', configJson.get('domain','domain.com'))
        cpus = host.get('cpus', configJson.get('cpus',1))
        memory = host.get('memory', configJson.get('memory',1024))
        disk = host.get('disk', configJson.get('disk',25))
        osCode = host.get('osCode', configJson.get('osCode',''))
        templateGuid = host.get('templateGuid', configJson.get('templateGuid',''))
        useLocalDisk = host.get('localDisk', configJson.get('localDisk', True))
        datacenter = host.get('datacenter', configJson.get('datacenter', 'dal10'))
        private = host.get('private', configJson.get('private', False))
        dedicated = host.get('dedicated', configJson.get('dedicated', False))
        hourly = host.get('hourly', configJson.get('hourly', True))
        tag = host.get('tag', configJson.get('tag',''))
        privateVlan = host.get('privateVlan', configJson.get('privateVlan',''))
        nicSpeed = host.get('nicSpeed', configJson.get('nicSpeed',100))
        sshKey = host.get('sshKey', configJson.get('sshKey',''))
        postInstallUrl = host.get('postInstallUrl', configJson.get('postInstallUrl',''))

        userData = '{"hostname": "' + str(hostname) + '", "privateIPAddress": "' + str(privateIPAddress) + '"}'

        createdInstance = orderServer(hostname, domain, cpus, memory, disk, osCode, templateGuid, useLocalDisk, datacenter, private, dedicated, hourly, tag, privateVlan, nicSpeed, sshKey, userData, postInstallUrl)
        createdId = createdInstance['id']
        if (args.verbose):
            print 'Built Server: ' + str(createdId)

    print 'Completed: ' + time.strftime('%Y-%m-%d %I:%M:%S %Z')


def getVirtualGuestUserData(id):
    print 'Getting user data'
    url = baseURL + '/SoftLayer_Virtual_Guest/' + str(id) +'/getUserData'
    r = requests.get(url, auth=(username, apiKey))
    result = r.json()
    print json.dumps(result, sort_keys=True, indent=4)
    return result


#############################################################################
#############################################################################


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
elif (args.action == 'LIST_VLANS'):
    print 'Listing VLANs...'
    listVlans()
elif (args.action == 'CAPTURE'):
    print 'Capturing server...'
    #captureImage()
elif (args.action == 'CANCEL'):
    print 'Canceling servers...'
    if (args.tag != None and args.tag != ''):
        cancelServers(args.tag)
    if (args.serverId != None):
        cancelInstance(args.serverId)
