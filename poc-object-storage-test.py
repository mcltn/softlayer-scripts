import object_storage
import time

parser = argparse.ArgumentParser()

parser.add_argument("--objectStorageAccount", default="")
parser.add_argument("--username", default="")
parser.add_argument("--apiKey", default="")
parser.add_argument("--datacenter", default="dal05")

args = parser.parse_args()

username = args.objectStorageAccount + ":" + args.username
apiKey = args.apiKey

sl_storage = object_storage.get_client(username= username, password=apiKey, datacenter=datacenter)

names = ['testContainer99']

#Create containers in array at root level
def createContainers():
	for name in names:
		sl_storage[name].create()

#Get all top level containers
def getContainers():
	containers = sl_storage.containers()

	#List containers at root level
	print ("containers:")
	for container in containers:
		properties = container.properties
		print ("\tname: " + properties['name'])  


#Create items in the containers
def createItems():
	for name in names:
		#Create files
		sl_storage[name]["sample1.txt"].create()
		print ("Created sample1.txt")
		sl_storage[name]["sample2.txt"].create()
		print ("Created sample2.txt")

		#Place content in the files
		sl_storage[name]['sample1.txt'].send('this is a test')
		sl_storage[name]['sample2.txt'].send('this is a test')


#Delete containers created in this example
def deleteContainers():
	for name in names:
		files = sl_storage[name].objects()
	
		#Must empty container before deleting
		for file in files:
			properties = file.properties
			sl_storage[name][properties['name']].delete()
			print ("Deleted " + properties['name'])

	#remove container
	sl_storage[name].delete()
	print ("Deleted " + name)


getContainers()
createContainers()
getContainers()
createItems()
deleteContainers()

