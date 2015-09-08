# softlayer-scripts


## poc-create-image-from-vm.py
 This script shows how to build an Image from a virtual server and also deploy a new instance using the image. This example utilizes the SoftLayer Python library and various Managers.

## poc-object-storage-test.py
 This script shows how to interact with Object Storage via the Object Storage Python Library. The script will list containers, create new containers, get a new list of containers, create items in containers, then delete the items before then deleting the containers.

## poc-rest-examples.py
 This script shows many of the available calls utilizing the REST interface to the SoftLayer API. The script will need to be modified to execute the requested methods to work with, but some examples can be uncommented to execute.

## poc-virtual-servers.py
 This script was created as an alternative to the existing Python SoftLayer CLI to quickly deploy multiple servers via command line. This script can take many parameters, and also uses default values. This script also has the ability to capture metrics on how long each transaction takes during provisioning, by specifying verbose mode and exporting to a file.

> To see available parameters
> poc-vertual-servers.py --help
```
python poc-virtual-servers.py --action CREATE --serverCount 2 --uniqueId aa --tag aa-mcltn --hostname mcltn --domain colton.cc --datacenter dal09 --hourly --cpus 1 --memory 1024 --localDisk --localDisk1Size 25 --localDisk2Size 200 --osCode UBUNTU_LATEST --privateVlan 12345 --nicSpeed 1000 --sshKey 175267 --postInstallUrl https://dal05.objectstorage.service.networklayer.com/v1/AUTH_xyz/container/script.sh --verbose --waitForCompletion
```


## ubuntu-mongo-install.sh
 Sample shell script to format and attach additional disk, and install mongodb. This sccript acn be called during post-provisioning

