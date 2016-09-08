import os, sys, argparse, requests, simplejson

parser = argparse.ArgumentParser()

parser.add_argument("--username", default="")
parser.add_argument("--apiKey", default="")

args = parser.parse_args()

baseURL = 'https://api.softlayer.com/rest/v3'
username = args.username
apiKey = args.apiKey

if (args.username != ''):
	username = args.username
	apiKey = args.apiKey
else:
	username = os.environ.get('SOFTLAYER_USERNAME', '')
	apiKey = os.environ.get('SOFTLAYER_APIKEY','')


#############################################################################
#############################################################################

def getAccount():
	url = baseURL + '/SoftLayer_Account'
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getAccountHardware():
	url = baseURL + '/SoftLayer_Account/getHardware'
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getAccountSSHKey():
	url = baseURL + '/SoftLayer_Account/SshKeys'

	#Filter
	#url += '?objectFilter={"sshKeys":{"label":{"operation":"mac1mbp"}}}'
	#url += '?objectFilter={"sshKeys":{"label":{"operation":"*= m"}}}'

	#?url += '?objectFilter={"sshKeys":{"createDate":{"operation":">= 04/14/15"}}}'
	#url += '?objectFilter={"sshKeys":{"createDate":{"operation":"betweenDate","options":[{"name":"startDate","value":["1/1/2015 00:00:00"]},{"name":"endDate","value":["4/1/2015 23:59:59"]}]}}}'

	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def addSSHKeys(label, key):
	url = baseURL + '/SoftLayer_Account/SshKeys'
	data = {"parameters": [ {"key": key, "label": label} ]}
	headers = {'Accept':'application/json','Content-Type':'application/json'}
	r = requests.post(url, data=simplejson.dumps(data), headers=headers, auth=(username, apiKey))
	if (r.status_code == 200):
		return True
	else:
		return False


def getEventLog():
	url = baseURL + '/SoftLayer_Event_Log/getAllObjects?resultLimit=0,10'
	#url += '&objectFilter={"objectId":{"operation":277800}}'
	#url += '&objectFilter={"objectId": {"operation": "in", "options": [{"name":"data", "value":[10368543]},{"name":"data", "value":[9956723]}] }}'
	url += '?objectFilter={"Log":{"eventCreateDate":{"operation":"betweenDate","options":[{"name":"startDate","value":["10/28/2015 00:00:00"]},{"name":"endDate","value":["10/28/2015 23:59:59"]}]}}}}'
	print url
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')



def getTransactionHistory(instanceId):
	url = baseURL + '/SoftLayer_Hardware_Server/' + str(instanceId) + '/getTransactionHistory'
	print url
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')
	

def getAccountVirtualServers():
	url = baseURL + '/SoftLayer_Account/getVirtualGuests'

	#Mask
	#url += '?objectMask=mask[datacenter[name,longName]]&objectFilter={"virtualGuests":{"datacenter":{"name":{"operation":"^=dal09"}}}}'
	url += '?objectMask=mask[id, hostname, primaryNetworkComponent[router]]'

	#Filter
	#url += '?objectFilter={"virtualGuests":{"datacenter":{"name":{"operation":"^=dal09"}}}}'
	#url += '?objectFilter={"virtualGuests":{"domain":{"operation":"!= lavu.softlayer.com"}}}'

	#url += '?objectFilter={"virtualGuests":{"maxCpu":{"operation": ">= 4"}}}'
	#url += '?objectFilter={"virtualGuests":{"createDate":{"operation":"betweenDate","options":[{"name":"startDate","value":["6/20/2015"]},{"name":"endDate","value":["6/25/2015"]}]}}}'

	#?url += '?objectFilter={"virtualGuests":{"createDate":{"operation":"isDate", "options":[{"name":"date","value":["6/24/2015 1:30:34"]}]}}}'
	#url += '?objectFilter={"virtualGuests":{"createDate":{"operation":"greaterThanDate","options":[{"name":"date","value":["6/25/2015"]}]}}}'



	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getServerPassword():
	url = baseURL + '/SoftLayer_Virtual_Guest/9891833?objectMask=mask.operatingSystem.passwords.password'
	print url
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getHubNetworkStorage():
	url = baseURL + '/SoftLayer_Account/getHubNetworkStorage'
	print url
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getDataCenters():
	url = baseURL + '/SoftLayer_Location/Datacenters'
	r = requests.get(url, auth=(username, apiKey))
	if (r.status_code == 200):
		return r.json()
	else:
		return []


def getOSes():
	url = baseURL + '/SoftLayer_Software_Description/AllObjects'
	r = requests.get(url, auth=(username, apiKey))
	oses = []
	for os in r.json():
		if os['virtualizationPlatform'] == 0 and os['operatingSystem'] == 1:
			oses.append(os)
			print os['referenceCode']
	return oses


def getProductPackageItemPrices(packageId):
	url = baseURL + '/SoftLayer_Product_Package/'+ str(packageId) +'/getItemPrices'
	print url
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getProductPackageItems(packageId, mask='N'):
	url = baseURL + '/SoftLayer_Product_Package/' + str(packageId) + '/getItems'

	if mask == 'Y':
		url = url + "?objectMask='mask[capacity,description,units,prices[id],categories[name]]'"

	r = requests.get(url, auth=(username, apiKey))
	print '*************'
	print r.status_code
	print simplejson.dumps(r.json(), sort_keys=True, indent=4 * ' ')
	print '*************'
	if (r.status_code == 200):
		return r.json()
	else:
		return None


def checkItemAvailability(itemPrice):
	url = baseURL + '/SoftLayer_Product_Order/checkItemAvailability'
	url += '?objectFilter={"itemPrices":['+ str(itemPrice) +']'
	print url	
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getPrivateImages():
	url = baseURL + '/SoftLayer_Account/getBlockDeviceTemplateGroups?objectMask=mask[datacenter]'
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	return result


def createImageTemplate(serverId):
	url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId) + '/getBlockDevices?objectMask=mask[diskImage]'
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')

	blockId = result[0]['id']
	print str(blockId)

	url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId) + '/createArchiveTransaction'
	data = {'parameters':['given-image-name',[{'id': blockId}],'given-notes-info']}
	headers = {'Accept':'application/json','Content-Type':'application/json'}
	r = requests.post(url, data=simplejson.dumps(data), headers=headers, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getImageLocations(imageId):
	url = baseURL + '/SoftLayer_Virtual_Guest_Block_Device_Template_Group/' + str(imageId) + '/getStorageLocations'
	r = requests.get(url, auth=(username, apiKey))
	return r.json()


def copyImageToLocation(imageId, datacenterId):
	url = baseURL + '/SoftLayer_Virtual_Guest_Block_Device_Template_Group/' + str(imageId) + '/setAvailableLocations'
	data = {'parameters':[[{'id':datacenterId}]]}
	headers = {'Accept':'application/json','Content-Type':'application/json'}
	r = requests.post(url, data=simplejson.dumps(data), headers=headers, auth=(username, apiKey))
	print r.status_code
	print r.json()


def getServer(serverId):
	url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId)

	url += '?objectMask=mask[id, hostname, host, primaryBackendNetworkComponent[router], serverRoom, location]'

	r = requests.get(url, auth=(username, apiKey))
	if (r.status_code == 200):
		result = r.json()
		print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')
		return result
	else:
		return None

# Needs validation
def updateServer(serverId, server):
	url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId)
	headers = {'Accept':'application/json','Content-Type':'application/json'}
	r = requests.put(url, data=simplejson.dumps(server), headers=headers, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def createServer(hostname, domain, startCpus, maxMemory, useLocalDisk, usePrivateNetworkOnly, useHourlyBilling, datacenter, operatingSystemReferenceCode, sshKeys, privateVlan, imageId):
	url = baseURL + '/SoftLayer_Virtual_Guest'
	data = {"parameters": [ {"hostname": hostname, "domain": domain, "startCpus": startCpus, "maxMemory": maxMemory, "localDiskFlag": useLocalDisk, "privateNetworkOnlyFlag": usePrivateNetworkOnly, "hourlyBillingFlag": useHourlyBilling, "datacenter":{"name":datacenter}} ]}

	if len(sshKeys) > 0:
		keys = []
		for key in sshKeys:
			keys.append({"id": key})
		data['parameters'][0]['sshKeys'] = keys

	if privateVlan is not None:
		vlan = {"networkVlan":{"id": privateVlan}}
		data['parameters'][0]['primaryBackendNetworkComponent'] = vlan

	if operatingSystemReferenceCode != "":
		data['parameters'][0]['blockDevices'] = [{"device":0, "diskImage": {"capacity":100}}]
		data['parameters'][0]['operatingSystemReferenceCode'] = operatingSystemReferenceCode

	if imageId != "" and operatingSystemReferenceCode == "":
		data['parameters'][0]['blockDeviceTemplateGroup'] = {"globalIdentifier": imageId}

	data['parameters'][0]['networkComponents'] = [{"maxSpeed":1000}]

	print simplejson.dumps(data, sort_keys=True, indent=4 * ' ')
	headers = {'Accept':'application/json','Content-Type':'application/json'}
	r = requests.post(url, data=simplejson.dumps(data), headers=headers, auth=(username, apiKey))
	#print r.status_code
	#print r.json()
	#print '\n\n'
	if (r.status_code == 201):
		return r.json()
	else:
		print r.status_code
		print r.text
		return None


def deleteServer(serverId):
	url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId)
	r = requests.delete(url, auth=(username, apiKey))
	if (r.status_code == 200):
		return True
	else:
		return False



def getActivePackages():
	url = baseURL + '/SoftLayer_Account/getActivePackages'
	print url
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getProductPackageCategories(packageId):
	url = baseURL + '/SoftLayer_Product_Package/' + str(packageId) + '/getCategories'
	r = requests.get(url, auth=(username, apiKey))
	print '*************'
	print r.status_code
	print simplejson.dumps(r.json(), sort_keys=True, indent=4 * ' ')
	print '*************'
	if (r.status_code == 200):
		return r.json()
	else:
		return None


def placeProductOrder(locationId, priceId):
	url = baseURL + '/SoftLayer_Product_Order/placeOrder'

	data = {"parameters":[{"complexType":"SoftLayer_Container_Product_Order","location":locationId,"packageId":0,"prices":[{"id": priceId}]}]}

	headers = {'Accept':'application/json','Content-Type':'application/json'}
	r = requests.post(url, data=simplejson.dumps(data), headers=headers, auth=(username, apiKey))
	print '*************'
	print r.status_code
	print simplejson.dumps(r.json(), sort_keys=True, indent=4 * ' ')
	print '*************'
	print '\n\n'
	if (r.status_code == 201):
		return r.json()
	else:
		print r.status_code
		print r.text
		return None



def createTicket():
	url = baseURL + '/SoftLayer_Ticket/createStandardTicket'


	data = {'parameters':[{'accountId': 330544,'assignedUserId': 324830, 'subjectId':1021, 'attachedAdditionalEmails': [{'email': 'mcolton@us.ibm.com'}], 'attachedVirtualGuests': [{'id': 13659123}], 'notifyUserOnUpdateFlag': True, 'title': 'Just Testing','userEditableFlag': True}, 'Ignore, Just Testing API.']}

	#data = {'parameters':[{'assignedUserId':324830, 'title':'Testing', 'contents':'Ignore, just testing API'}]}

	
	headers = {'Accept':'application/json','Content-Type':'application/json'}
	r = requests.post(url, data=simplejson.dumps(data), headers=headers, auth=(username, apiKey))
	print r.status_code
	print r.text
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


##Tickets
def getClosedTickets(sinceDate):
	url = baseURL + '/SoftLayer_Ticket/TicketsClosedSinceDate/' + sinceDate
	
	#url += '?objectMask=mask[attachedHardware,attachedVirtualGuests,cancellationRequest[items],firstUpdate]'
	url += '?objectMask=mask[firstUpdate]'

	r = requests.get(url, auth=(username, apiKey))
	print '*************'
	print simplejson.dumps(r.json(), sort_keys=True, indent=4 * ' ')

## Antivirus Software
def getVirtualServerAntivirusSoftware(serverId):
	url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId) + '/getAntivirusSpywareSoftwareComponent'
	r = requests.get(url, auth=(username, apiKey))
	print simplejson.dumps(r.json(), sort_keys=True, indent=4 * ' ')
	return r.json()

def getAntivirusSoftwareComponent(softwareId):
	url = baseURL + '/SoftLayer_Software_Component_AntivirusSpyware/' + str(softwareId) + '/getObject'
	r = requests.get(url, auth=(username, apiKey))
	print simplejson.dumps(r.json(), sort_keys=True, indent=4 * ' ')
	return r.json()

def updateAntivirusSoftwareComponent(softwareId, policy):
	url = baseURL + '/SoftLayer_Software_Component_AntivirusSpyware/' + str(softwareId) + '/updateAntivirusSpywarePolicy'
	data = {'parameters':[policy,True]}
	headers = {'Accept':'application/json','Content-Type':'application/json'}
	r = requests.post(url, data=simplejson.dumps(data), headers=headers, auth=(username, apiKey))
	print r.status_code
	print r.text
	

	print simplejson.dumps(r.json(), sort_keys=True, indent=4 * ' ')
	return r.json()




# Invoices

def getAccountInvoices():
	url = baseURL + '/SoftLayer_Account/getInvoices?resultLimit=0,2&objectMask=mask[id]'
	r = requests.get(url, auth=(username, apiKey))
	print simplejson.dumps(r.json(), sort_keys=True, indent=4 * ' ')
	return r.json()


#############################################################################
#############################################################################



#getAccount()
#getAccountHardware()
#getAccountSSHKey()
#getAccountVirtualServers()
#getEventLog()

#getTransactionHistory(514575)

#getServer(13640131)
#getTransactionHistory(13640131)

#getServerPassword()
#getHubNetworkStorage()
#getActivePackages()
#getProductPackageItemPrices()
#createImageTemplate(11495057)

#getOSes()


getAccountInvoices()


# Antivirus
serverId = 17561395 #17904879
#a = getVirtualServerAntivirusSoftware(serverId)
##b = getAntivirusSoftwareComponent(a['id'])
#c = updateAntivirusSoftwareComponent(a['id'],'1')



hostprefix = 'aa-std-'
domain = 'colton.cc'
startCpus = 8
maxMemory = 16384
useLocalDisk = False
usePrivateNetworkOnly = True
useHourlyBilling = True
datacenter = 'mex01'
operatingSystemReferenceCode = ''
sshKeys = []
privateVlan = 1222747
imageId = 'af7b162b-e277-4424-aed4-fe004067d9e5'
#imageId = 'fbfc7eba-6585-4880-b4bc-79f6953769e7'

i = 1
#while i <= 20:
#	hostname = hostprefix + str(i)
#	createServer(hostname, domain, startCpus, maxMemory, useLocalDisk, usePrivateNetworkOnly, useHourlyBilling, datacenter, operatingSystemReferenceCode, sshKeys, privateVlan, imageId)
#	i += 1



#getProductPackageItems(46)
# 899 - 1 Gbps private


#groupId 1012
#22830457
#getClosedTickets('2015-10-9T00:00:00')
#getServer(13208749)


#server = getServer(11581401)
#server['notes'] = 'Testing notes'
#updateServer(server['id'],server)

#dcs = getDataCenters()
#print simplejson.dumps(dcs, sort_keys=True, indent=4 * ' ')

#imgs = getPrivateImages()
#print simplejson.dumps(imgs, sort_keys=True, indent=4 * ' ')

#locs = getImageLocations(498987)
#print simplejson.dumps(locs, sort_keys=True, indent=4 * ' ')

#copyImageToLocation(498987, 37473) #wdc01
#copyImageToLocation(498987, 449612) #syd01

#copyImageToLocation(876941, 168642) #sjc01

#createTicket()

#getProductPackageItemPrices(46)
#checkItemAvailability(471)

