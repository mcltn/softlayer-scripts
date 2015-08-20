#!/bin/bash

#################################
# MOUNT DISK
#################################

#echo -e "n p 1 \n \n t c a 1 w" | fdisk /dev/xvdc
(echo n; echo p; echo 1; echo ; echo; echo t; echo c; echo a; echo 1;echo w) | sudo fdisk /dev/xvdc

mkfs.ext3 /dev/xvdc1
mkdir /mongodb

sed -i '$ a /dev/xvdc1\t/mongodb\text3\tdefaults\t0\t0' /etc/fstab
#echo -e "/dev/xvdc1\t/mongodb\text3\tdefaults\t0\t0" >> /etc/fstab

#echo -e "/dev/xvdc1" >> /etc/fstab
#echo -e -n "\t" >> /etc/fstab    #INSERT TAB
#echo -n "/mongodb" >> /etc/fstab
#echo -e -n "\t" >> /etc/fstab    #INSERT TAB
#echo -n "ext3" >> /etc/fstab
#echo -e -n "\t" >> /etc/fstab    #INSERT TAB
#echo -n "defaults" >> /etc/fstab
#echo -e -n "\t" >> /etc/fstab    #INSERT TAB
#echo -n "0" >> /etc/fstab
#echo -e -n "\t" >> /etc/fstab    #INSERT TAB
#echo -n "0" >> /etc/fstab

mount /dev/xvdc1 /mongodb


####################################
# INSTALL MONGO / MONGO ENTERPRISE
####################################

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10

#echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
echo "deb http://repo.mongodb.com/apt/ubuntu "$(lsb_release -sc)"/mongodb-enterprise/stable multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-enterprise.list

sudo apt-get update

#sudo apt-get install -y mongodb-org
sudo apt-get install -y mongodb-enterprise

mkdir /mongodb/data

sed -i 's/dbpath=\/var\/lib\/mongodb/dbpath=\/mongodb\/data/' /etc/mongod.conf
sed -i 's/bind_ip/#bind_ip/' /etc/mongod.conf
sed -i 's/#auth = true/auth = true/' /etc/mongod.conf

sudo chown mongodb -R /mongodb
sudo chown mongodb -R /mongodb/data

sudo service mongod restart
