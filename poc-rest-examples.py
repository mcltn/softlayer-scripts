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
	url += '?objectFilter={"sshKeys":{"createDate":{"operation":"betweenDate","options":[{"name":"startDate","value":["1/1/2015 00:00:00"]},{"name":"endDate","value":["4/1/2015 23:59:59"]}]}}}'

	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getEventLog():
	url = baseURL + '/SoftLayer_Event_Log/getAllObjects?resultLimit=0,10'
	#url += '&objectFilter={"objectId":{"operation":277800}}'
	#url += '&objectFilter={"objectId": {"operation": "in", "options": [{"name":"data", "value":[10368543]},{"name":"data", "value":[9956723]}] }}'
	url += '?objectFilter={"Log":{"eventCreateDate":{"operation":"betweenDate","options":[{"name":"startDate","value":["4/1/2015 00:00:00"]},{"name":"endDate","value":["4/1/2015 23:59:59"]}]}}}}'
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


def getActivePackages():
	url = baseURL + '/SoftLayer_Account/getActivePackages'
	print url
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


def getProductPackageItemPrices():
	url = baseURL + '/SoftLayer_Product_Package/142/getItemPrices'
	print url
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')

	
def getPrivateImages():
	url = baseURL + '/SoftLayer_Account/getBlockDeviceTemplateGroups'
	r = requests.get(url, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


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


def getServer(serverId):
	url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId)
	r = requests.get(url, auth=(username, apiKey))
	if (r.status_code == 200):
		result = r.json()
		print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')
		return result
	else:
		return None

def updateServer(serverId, server):
	url = baseURL + '/SoftLayer_Virtual_Guest/' + str(serverId)
	headers = {'Accept':'application/json','Content-Type':'application/json'}
	r = requests.put(url, data=simplejson.dumps(server), headers=headers, auth=(username, apiKey))
	result = r.json()
	print simplejson.dumps(result, sort_keys=True, indent=4 * ' ')


#############################################################################
#############################################################################


#getAccount()
#getAccountHardware()
#getAccountSSHKey()
#getAccountVirtualServers()
#getEventLog()
#getServerPassword()
#getHubNetworkStorage()
#getActivePackages()
#getProductPackageItemPrices()
#getPrivateImages()
#createImageTemplate(11495057)

server = getServer(11581401)
server['notes'] = 'Testing notes'
updateServer(server['id'],server)


