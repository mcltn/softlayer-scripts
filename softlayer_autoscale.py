import SoftLayer
from SoftLayer import Client
import os, sys, time, simplejson
from datetime import timedelta, datetime

username = os.environ.get('SOFTLAYER_USERNAME', '')
api_key = os.environ.get('SOFTLAYER_APIKEY','')

endpoint_url = SoftLayer.API_PUBLIC_ENDPOINT
client = Client(username=username, api_key=api_key, endpoint_url=endpoint_url)


def getDatacenterKeyName(name):
    datacenters = getDatacenters()
    for datacenter in datacenters:
        if datacenter['name'] == name:
            print simplejson.dumps(datacenter, sort_keys=True, indent=4 * ' ')
            return datacenter['regions'][0]['keyname']
    return None

def getDatacenterRegionDescription(name):
    regions = getRegionalGroups()
    for region in regions:
        for location in region['locations']:
            if location['name'] == name:
                print simplejson.dumps(location, sort_keys=True, indent=4 * ' ')
                return region['id'], region['description']
    return None

def getDatacenters():
    object_mask = 'regions'
    datacenters = client['SoftLayer_Location'].getDatacenters(mask=object_mask)
    #print simplejson.dumps(datacenters, sort_keys=True, indent=4 * ' ')
    return datacenters

def getPackagePrices():
    prices = client['SoftLayer_Product_Package'].getItemPrices(id=194)
    print simplejson.dumps(prices, sort_keys=True, indent=4 * ' ')

def getBlockDeviceTemplateGroups():
    imgs = client['SoftLayer_Account'].getBlockDeviceTemplateGroups()
    print simplejson.dumps(imgs, sort_keys=True, indent=4 * ' ')



def orderLoadBalancer(location, price_id, place_order):
    orderData = {
        'prices': [
            {
                'id': price_id
            }
        ],
        'packageId': 194,
        'location': location
    }
    orderId = 0
    if place_order:
        load_balancer = client['SoftLayer_Product_Order'].placeOrder(orderData)
    else:
        load_balancer = client['SoftLayer_Product_Order'].verifyOrder(orderData)

    print simplejson.dumps(load_balancer, sort_keys=True, indent=4 * ' ')
    return load_balancer

def getBillingOrderDetail(id):
    mask = 'id,status,items'
    order = client['SoftLayer_Billing_Order'].getObject(id=id,mask=mask)
    print simplejson.dumps(order, sort_keys=True, indent=4 * ' ')
    return order

def getBillingOrderItem(id):
    mask = 'billingItem,order'
    order = client['SoftLayer_Billing_Order_Item'].getObject(id=id,mask=mask)
    print simplejson.dumps(order, sort_keys=True, indent=4 * ' ')
    return order

def getVirtualServer(id):
    server = client['SoftLayer_Virtual_Guest'].getObject(id=id)
    print simplejson.dumps(server, sort_keys=True, indent=4 * ' ')
    return server


def getLoadBalancers():
    object_mask = 'loadBalancerHardware,virtualServers,ipAddress,billingItem, billingItem[orderItem]'
    load_balancers = client['Account'].getAdcLoadBalancers(mask=object_mask)
    #print simplejson.dumps(load_balancers, sort_keys=True, indent=4 * ' ')
    return load_balancers

def findLoadBalancer(order_item_id):
    load_balancers = getLoadBalancers()
    for load_balancer in load_balancers: #reversed(load_balancers)
        #print '\n LOAD BALANCERS \n'
        #print simplejson.dumps(load_balancer, sort_keys=True, indent=4 * ' ')
        if load_balancer['billingItem']['orderItemId'] == order_item_id:
            #print simplejson.dumps(load_balancer, sort_keys=True, indent=4 * ' ')
            return load_balancer
    return None

def getLoadBalancer(id):
    mask = 'virtualServers[serviceGroups[services[groupReferences]]],billingItem'
    load_balancer = client['Network_Application_Delivery_Controller_LoadBalancer_VirtualIpAddress'].getObject(id=id, mask=mask)
    print simplejson.dumps(load_balancer, sort_keys=True, indent=4 * ' ')
    return load_balancer

def getRoutingMethods():
    methods = client['Network_Application_Delivery_Controller_LoadBalancer_Routing_Method'].getAllObjects()
    print simplejson.dumps(methods, sort_keys=True, indent=4 * ' ')
    return methods

def getRoutingTypes():
    types = client['Network_Application_Delivery_Controller_LoadBalancer_Routing_Type'].getAllObjects()
    print simplejson.dumps(types, sort_keys=True, indent=4 * ' ')
    return types

def addLoadBalancerServiceGroup(id,port,allocation,routing_type,routing_method):
    mask = 'virtualServers[serviceGroups[services[groupReferences]]]'
    load_balancer = client['Network_Application_Delivery_Controller_LoadBalancer_VirtualIpAddress'].getObject(id=id, mask=mask)
    service_template = {
        'port': port,
        'allocation': allocation,
        'serviceGroups': [
            {
                'routingTypeId': routing_type,
                'routingMethodId': routing_method
            }
        ]
    }
    load_balancer['virtualServers'].append(service_template)
    return client['Network_Application_Delivery_Controller_LoadBalancer_VirtualIpAddress'].editObject(load_balancer, id=id)



## Scale

def getTerminationPolicies():
    items = client['SoftLayer_Scale_Termination_Policy'].getAllObjects()
    print simplejson.dumps(items, sort_keys=True, indent=4 * ' ')
    return items

def getRegionalGroups():
    mask = 'locations'
    items = client['SoftLayer_Location_Group_Regional'].getAllObjects(mask=mask)
    #print simplejson.dumps(items, sort_keys=True, indent=4 * ' ')
    return items

def getScaleActionTypes():
    items = client['SoftLayer_Scale_Policy_Action'].getAllObjects()
    print simplejson.dumps(items, sort_keys=True, indent=4 * ' ')
    return items

def createScaleGroup(vip_id, regional_group_id, scale_group_name, hostname, domain, datacenter, cpu, memory, img, port, desiredcount, mincount, maxcount):

    group = {
        'name': scale_group_name,
        'desiredMemberCount': desiredcount,
        'minimumMemberCount': mincount,
        'maximumMemberCount': maxcount,
        'cooldown': 120,
        'terminationPolicyId': 1,
        'regionalGroupId': regional_group_id,
        'suspendedFlag': False,
        'virtualGuestMemberTemplate': {
             'hostname': hostname,
             'domain': domain,
             'startCpus': cpu,
             'maxMemory': memory,
             'hourlyBillingFlag': True,
             'localDiskFlag': True,
             'blockDeviceTemplateGroup': {
                'globalIdentifier': img
            },
            'datacenter': {
                'name': datacenter
            }
        },
        'loadBalancers':[
            {
                'healthCheck': {
                    'healthCheckTypeId': 21
                },
                'port': port,
                'virtualServerId': vip_id #252313
                
            }
        ]
    }
    #print simplejson.dumps(group, sort_keys=True, indent=4 * ' ')
    order = client['SoftLayer_Scale_Group'].createObject(group)
    print simplejson.dumps(order, sort_keys=True, indent=4 * ' ')
    return order

def createScaleUpPolicy(scale_group_id, scale_name, scale_amount):
    policy = {
        'name': scale_name,
        'scaleGroupId': scale_group_id,
        'scaleActions': [
            {
                'amount': scale_amount,
                'deleteFlag': '',
                'scaleType': 'RELATIVE',
                'typeId': 1
            }
        ],
        'resourceUseTriggers': [
            {
                'typeId': 3,
                'watches': [
                    {
                        'algorithm': 'EWMA',
                        'metric': 'host.cpu.percent',
                        'modifyDate': '',
                        'operator': '>',
                        'period': 120,
                        'value': '60'
                    }
                ]
            }
        ]
    }
    order = client['SoftLayer_Scale_Policy'].createObject(policy)
    print simplejson.dumps(order, sort_keys=True, indent=4 * ' ')
    return order

def createScaleDownPolicy(scale_group_id, scale_name, scale_amount):
    policy = {
        'name': scale_name,
        'scaleGroupId': scale_group_id,
        'scaleActions': [
            {
                'amount': scale_amount,
                'deleteFlag': '',
                'scaleType': 'RELATIVE',
                'typeId': 1
            }
        ],
        'resourceUseTriggers': [
            {
                'typeId': 3,
                'watches': [
                    {
                        'algorithm': 'EWMA',
                        'metric': 'host.cpu.percent',
                        'modifyDate': '',
                        'operator': '<',
                        'period': 120,
                        'value': '40'
                    }
                ]
            }
        ]
    }
    order = client['SoftLayer_Scale_Policy'].createObject(policy)
    print simplejson.dumps(order, sort_keys=True, indent=4 * ' ')
    return order

def getScaleGroups():
    mask = 'loadBalancers,loadBalancers[healthCheck[attributes]],loadBalancers[healthCheck[services]],loadBalancers[healthCheck[type]],policies,policies[resourceUseTriggers],policies[triggers],policies[triggers[type]],policies[actions]'
    groups = client['SoftLayer_Account'].getScaleGroups(mask=mask)
    print simplejson.dumps(groups, sort_keys=True, indent=4 * ' ')
    return groups

def getScaleGroup(id):
    mask = 'loadBalancers,loadBalancers[healthCheck[attributes]],loadBalancers[healthCheck[services]],loadBalancers[healthCheck[type]],policies,policies[resourceUseTriggers],policies[triggers],policies[triggers[type]],policies[resourceUseTriggers[watches]],policies[actions]'
    group = client['SoftLayer_Scale_Group'].getObject(id=id,mask=mask)
    print simplejson.dumps(group, sort_keys=True, indent=4 * ' ')
    return group
#SoftLayer_Scale_Policy_Trigger_ResourceUse_Watch

def getScaleLoadBalancer(id):
    load_balancers = client['SoftLayer_Scale_LoadBalancer'].getObject(id=id)
    print simplejson.dumps(load_balancers, sort_keys=True, indent=4 * ' ')
    return load_balancers

def scale(id, amount):
    client['SoftLayer_Scale_Group'].scale(amount,id=id)

# Setup Params
# --------------------------
scale_group_name = 'scale-mcltn-1'
datacenter = 'sjc03'
hostname = 'scale'
domain = 'colton.cc'
cpu = 1
memory = 1024
img = '4df4c463-5e29-4773-9ddb-fdda6ea5b2d8'

lb_price_id = 2079 # 250 VIP Connections

mincount = 0
desiredcount = 0
maxcount = 3


port = 8080
allocation = 100
routing_type = 2
routing_method = 10


# GET INFO CALLS
# ----------------------------------
#getDatacenters()
#getRegionalGroups()
#getBlockDeviceTemplateGroups()
#getPackagePrices()
#getLoadBalancers()
#getRoutingMethods()
#getRoutingTypes()
# #getTerminationPolicies()
# #getScaleActionTypes()
# #getScaleLoadBalancer(55458)
# #getScaleGroups()
# #getScaleGroup(990877)





#scale_group_id = 1012657
#getScaleGroup(scale_group_id)
#createScaleUpPolicy(scale_group_id,'xx-scale-cpu-up',1)
#createScaleDownPolicy(scale_group_id,'xx-scale-cpu-down',-1)

#scale(scale_group_id,-1)

def setup_autoscale():
    # PLACE ORDER
    # ----------------------------------------------------
    # order = orderLoadBalancer(region_keyname, lb_price_id, True)
    # order_id = order['orderId']
    # print 'Order Id: ' + str(order_id)
    # time.sleep(10)
    order_id = 8432665 #8478513

    order_details = getBillingOrderDetail(order_id)
    billing_item_order_item_id = order_details['items'][0]['id']
    print 'Billing Item Order Item Id: ' + str(billing_item_order_item_id)

    load_balancer = findLoadBalancer(billing_item_order_item_id)
    lb_id = load_balancer['id']
    print 'Load Balancer Id: ' + str(lb_id)

    # addLoadBalancerServiceGroup(lb_id, port, allocation, routing_type, routing_method)
    # time.sleep(10)
    load_balancer = getLoadBalancer(lb_id)
    vip_id = load_balancer['virtualServers'][0]['id']
    print 'Virtual Server Id: ' + str(vip_id)

    time.sleep(1)
    region_keyname = getDatacenterKeyName(datacenter)
    regional_group_id, regional_group_description = getDatacenterRegionDescription(datacenter)
    #print region_keyname
    #print regional_group_id
    #print regional_group_description


    scale_group = createScaleGroup(vip_id, regional_group_id, scale_group_name, hostname, domain, datacenter, cpu, memory, img, port, desiredcount, mincount, maxcount)
    scale_group_id = scale_group['id']
    print 'Scale Group Id: ' + str(scale_group_id)
    # time.sleep(10)

def scale_autoscale(scale_group_id):
    getScaleGroup(scale_group_id)
    createScaleUpPolicy(scale_group_id,'xx-scale-cpu-up',1)
    time.sleep(5)
    createScaleDownPolicy(scale_group_id,'xx-scale-cpu-down',-1)
    time.sleep(5)



#setup_autoscale()
#scale_autoscale(1015461)

#scale_group_id = 1015461
#scale(scale_group_id,2)
#scale(scale_group_id,-1)

# sudo apt-get install stress
# stress -c 1
# stress -c 1 -m 1 --vm-bytes 300M
# stress -c 2 -t 240s &
# top