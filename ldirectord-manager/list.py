#!/usr/bin/python
# -*- coding: utf-8 -*-

#yum install perl-Mail* perl-Socket6 perl-IO-Socket-INET6 ipvsadm -y

import json
import re
import os

import pprint
pp = pprint.PrettyPrinter(indent=4)

#Porta para busca (regex)
port = '12345|30105'

path = 'json'
dirs = os.listdir( path )


for ffile in dirs:
	filepath=path+'/'+str(ffile)

	with open(filepath, 'r') as jsonfile:
		data = json.load(jsonfile)

	for line in data:
		for info in data[line]:
			if 'porta' in info and re.search(port,info['porta']):
				print(info['porta'])
				pp.pprint(data[line])

