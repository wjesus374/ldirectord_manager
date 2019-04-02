#!/usr/bin/python
# -*- coding: utf-8 -*-

#yum install perl-Mail* perl-Socket6 perl-IO-Socket-INET6 ipvsadm -y

import json
import re
import os
import sys

import pprint
pp = pprint.PrettyPrinter(indent=4)

lyraservice='gprs'
port='12365'

path = 'newjson'
dirs = os.listdir( path )

#Status para registrar ou não a nova porta
status = 0

with open('config.json', 'r') as jsonfile:
	configdata = json.load(jsonfile)
	for config in configdata['services']:
		if 'name' in config and config['name'] == lyraservice:
			name = config['name']
			perlbin = config['perlbin']
			ldirectordbin = config['ldirectordbin']
			defaultconfigfile = config['defaultconfigfile']
			virtual = config['virtual']
			reals = config['reals']
			realmasq = config['realmasq']
			scheduler = config['scheduler']
			protocol = config['protocol']
			negotiatetimeout = config['negotiatetimeout']
			ldservice = config['ldservice']

	for config in configdata['data']:
		if 'maxvirtalinfile' in config:
			maxvirtalinfile = config['maxvirtalinfile']

	for config in configdata['config']:
		if 'virtualservers' in config:			
			virtualservers = config['virtualservers']
			if virtualservers < maxvirtalinfile:
				print "As novas configurações serão lidas do arquivo: %s" %(str(config['configfile']))
				sys.exit(0)

for ffile in dirs:
	filepath=path+'/'+str(ffile)

	with open(filepath, 'r') as jsonfile:
		data = json.load(jsonfile)

	for line in data:
		for info in data[line]:
			if 'porta' in info and re.search(port,info['porta']):
				print "Porta %s já registrada no arquivo %s" %(str(info['porta']),str(filepath))
				status = 1


if status == 0:
	print "Registrar a nova porta: %s" %(str(port))
	defaultconfigfile = 'json/add_novo.json'
	print "A porta será gravada no arquivo: %s" %(str(defaultconfigfile))
	with open(defaultconfigfile, 'r') as jsonfile:
		data = json.load(jsonfile)
		virtualport=str(virtual)+':'+str(port)
		lddata = []
		for real in reals:
			lddata.append({'real' : real+':'+str(port)+' '+realmasq})
		
		lddata.append({"ip": str(virtual)})
		lddata.append({"porta": port})
		lddata.append({"scheduler": scheduler})
		lddata.append({"protocol": protocol})
		lddata.append({"negotiatetimeout": negotiatetimeout})
		lddata.append({"service" : ldservice})

		#print(lddata)
		data[str(virtualport)] = lddata

	with open(defaultconfigfile, 'w') as jsonfile:
		json.dump(data, jsonfile)

