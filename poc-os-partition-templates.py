import os, sys, argparse, requests, simplejson

base_url = 'https://api.softlayer.com/rest/v3'
username = os.environ.get('SOFTLAYER_USERNAME', '')
api_key = os.environ.get('SOFTLAYER_APIKEY','')

obj_id = 0
os_type = 'linux'

# Get OS Partition Templates
url = base_url + '/SoftLayer_Hardware_Component_Partition_OperatingSystem/getAllObjects'
r = requests.get(url, auth=(username, api_key))
objects = r.json()
print simplejson.dumps(objects, sort_keys=True, indent=4 * ' ')
for obj in objects:
	if obj['description'] == os_type:
		obj_id = obj['id']
print obj_id


# Get OS Partition Templates
url = base_url + '/SoftLayer_Hardware_Component_Partition_OperatingSystem/'+ str(obj_id) +'/getPartitionTemplates'
url += '?objectMask=mask[id,description,templateType,data,partitionTemplatePartition]'

r = requests.get(url, auth=(username, api_key))
templates = r.json()
print simplejson.dumps(templates, sort_keys=True, indent=4 * ' ')
