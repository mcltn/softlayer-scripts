import os, sys, argparse, requests, simplejson

base_url = 'https://api.softlayer.com/rest/v3'
username = os.environ.get('SOFTLAYER_USERNAME', '')
api_key = os.environ.get('SOFTLAYER_APIKEY','')

placeOrder = False

qty = 1
hostname = "aa-mcltn"
domain = "colton.cc"

datacenter = 'wdc04'
privateVlan = 1354937 #911


cores = 8
cpu_name = '8 x 2.0 GHz Cores'
ram_name = '16 GB'
disk_name = '100 GB (SAN)'
os_name = 'Ubuntu Linux 14.04 LTS Trusty Tahr - Minimal Install (64 bit)'
#'Windows Server 2012 R2 Standard Edition (64 bit)'
#'Windows Server 2012 Standard Edition (64 bit)'
bandwidth_name = '0 GB Bandwidth'
nic_name = '100 Mbps Private Network Uplink'
#virusscan_name = 'McAfee VirusScan Enterprise'


# Get Active Package For Cloud
cloud_package_id = 0
url = base_url + '/SoftLayer_Account/getActivePackages'
r = requests.get(url, auth=(username, api_key))
packages = r.json()
print simplejson.dumps(packages, sort_keys=True, indent=4 * ' ')
for package in packages:
	if package['name'] == 'Cloud Server':
		cloud_package_id = package['id']
#print cloud_package_id

# Get Datacenter
dc_id = 0
url = base_url + '/SoftLayer_Product_Package/'+ str(cloud_package_id) +'/getLocations'
r = requests.get(url, auth=(username, api_key))
dcs = r.json()
for dc in dcs:
	if dc['name'] == datacenter:
		dc_id = dc['id']
#print dc_id

# Configurations
url = base_url + '/SoftLayer_Product_Package/'+ str(cloud_package_id) +'/getConfiguration'
url += '?objectMask=mask[isRequired,itemCategory]'
r = requests.get(url, auth=(username, api_key))
configs = r.json()
#print '\n'
#print simplejson.dumps(configs, sort_keys=True, indent=4 * ' ')
#for config in configs:
#	print simplejson.dumps(config, sort_keys=True, indent=4 * ' ')

#Prices
url = base_url + '/SoftLayer_Product_Package/'+ str(cloud_package_id) +'/getItemPrices'
url += '?objectMask=mask[id,item.description,categories.id,attributes,locationGroupId,pricingLocationGroup[locations[id, name, longName]]]'
#url += '&objectFilter={"itemPrices":{"pricingLocationGroup":{"locations":{"id":{"operation":"'+ str(dc_id) +'"}}}}}'

r = requests.get(url, auth=(username, api_key))
item_prices = r.json()
print '\n'
print simplejson.dumps(item_prices, sort_keys=True, indent=4 * ' ')
print '\n\n\n\n'


data = {"parameters":[{"packageId": cloud_package_id,"location":dc_id,"quantity":qty,"hardware":[{"hostname":hostname,"domain":domain}],"prices":[]}]}

complete_categories = []

# Loop through Configs and get a Price
for config in configs:
	if config['isRequired'] == 1: #or config['itemCategory']['categoryCode'] == 'av_spyware_protection':
		for item_price in item_prices:
			if 'categories' in item_price:
				if any(d['id'] == config['itemCategory']['id'] for d in item_price['categories']):
					if not config['itemCategory']['name'] in complete_categories:

						if (item_price['locationGroupId'] == None or any(d['id'] == dc_id for d in item_price['pricingLocationGroup']['locations'])):

							print str(item_price['id']) +' \t ' + item_price['item']['description']
							
							#CPU
							if item_price['item']['description'] == cpu_name :
								data['parameters'][0]['prices'].append({'id':item_price['id']})
								complete_categories.append(config['itemCategory']['name'])

							#RAM
							elif item_price['item']['description'] == ram_name :
								data['parameters'][0]['prices'].append({'id':item_price['id']})
								complete_categories.append(config['itemCategory']['name'])
							
							#DISK
							elif item_price['item']['description'] == disk_name :
								data['parameters'][0]['prices'].append({'id':item_price['id']})
								complete_categories.append(config['itemCategory']['name'])

							#OS
							elif item_price['item']['description'] == os_name :
								print '\nOS Name: %s' % item_price['item']['description']
								item_price_valid = True

								# Need to filter license by cpu if required
								item_attributes = item_price['attributes']
								for item_attribute in item_attributes:
									if int(item_attribute['itemPriceAttributeTypeId']) == 21:
										if int(item_attribute['value']) > cores:
											item_price_valid = False
									if int(item_attribute['itemPriceAttributeTypeId']) == 22:
										if int(item_attribute['value']) < cores:
											item_price_valid = False

								if item_price_valid:
									data['parameters'][0]['prices'].append({'id':item_price['id']})
									complete_categories.append(config['itemCategory']['name'])

							#BANDWIDTH
							elif item_price['item']['description'] == bandwidth_name :
								data['parameters'][0]['prices'].append({'id':item_price['id']})
								complete_categories.append(config['itemCategory']['name'])

							#NIC
							elif item_price['item']['description'] == nic_name :
								data['parameters'][0]['prices'].append({'id':item_price['id']})
								complete_categories.append(config['itemCategory']['name'])

							#Virus Scan							
							#elif item_price['item']['description'] == virusscan_name :
							#	data['parameters'][0]['prices'].append({'id':item_price['id']})
							#	complete_categories.append(config['itemCategory']['name'])
						
		
		# Add other required
		for item_price in item_prices:
			if 'categories' in item_price:
				if any(d['id'] == config['itemCategory']['id'] and d['id'] for d in item_price['categories']):
					if not config['itemCategory']['name'] in complete_categories:
						if (item_price['locationGroupId'] == None or any(d['id'] == dc_id for d in item_price['pricingLocationGroup']['locations'])):
							data['parameters'][0]['prices'].append({'id':item_price['id']})
							complete_categories.append(config['itemCategory']['name'])


data['parameters'][0]['useHourlyPricing'] = True
vlan = {'networkVlanId': privateVlan}
data['parameters'][0]['hardware'][0]['primaryBackendNetworkComponent'] = vlan


print simplejson.dumps(data, sort_keys=True, indent=4 * ' ')

# Verify Order
url = base_url + '/SoftLayer_Product_Order/verifyOrder'
headers = {'Accept':'application/json','Content-Type':'application/json'}
r = requests.post(url, data=simplejson.dumps(data), headers=headers, auth=(username, api_key))
if r.status_code == 200:
	print simplejson.dumps(r.json(), sort_keys=True, indent=4 * ' ')
else:
	print r.text


# Place Order
if placeOrder:
	url = base_url + '/SoftLayer_Product_Order/placeOrder'
	headers = {'Accept':'application/json','Content-Type':'application/json'}
	r = requests.post(url, data=simplejson.dumps(data), headers=headers, auth=(username, api_key))
	if r.status_code == 200:
		print simplejson.dumps(r.json(), sort_keys=True, indent=4 * ' ')
	else:
		print r.text


