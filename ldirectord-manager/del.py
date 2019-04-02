#!/usr/bin/python
# -*- coding: utf-8 -*-

#yum install perl-Mail* perl-Socket6 perl-IO-Socket-INET6 ipvsadm -y

import json
import re
import os

import pprint
pp = pprint.PrettyPrinter(indent=4)

service='gprs'
port='12345'

path = 'json'
dirs = os.listdir( path )

#Status para registrar ou não a nova porta
delvirtual = ''

with open('config.json', 'r') as jsonfile:
	configdata = json.load(jsonfile)
	for config in configdata['services']:
		if 'name' in config and config['name'] == service:
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

for ffile in dirs:
	filepath=path+'/'+str(ffile)

	with open(filepath, 'r') as jsonfile:
		data = json.load(jsonfile)

	for line in data:
		for info in data[line]:
			if 'porta' in info and re.search(port,info['porta']):
				print "Porta %s será deletada no arquivo %s" %(str(info['porta']),str(filepath))
				delvirtual = line

	if delvirtual:
		del data[delvirtual]
		delvirtual = ''

	with open(filepath, 'w') as jsonfile:
		json.dump(data, jsonfile)


