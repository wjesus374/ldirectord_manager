#!/usr/bin/python
# -*- coding: utf-8 -*-

#yum install perl-Mail* perl-Socket6 perl-IO-Socket-INET6 ipvsadm -y

import json
import re
import os

import pprint
pp = pprint.PrettyPrinter(indent=4)

path = 'json'
dirs = os.listdir( path )


with open('config.json', 'r') as jsonfile:
	configdata = json.load(jsonfile)
	#print(configdata['data'])
	for config in configdata['data']:
		if 'maxvirtalinfile' in config:
			#print(config['maxvirtalinfile'])
			maxvirtalinfile = config['maxvirtalinfile']
		else:
			maxvirtalinfile = 150

		if 'masterservice' in config:
			masterservice = config['masterservice']
		else:
			masterservice = 'pingpong_master'

		if 'perlbin' in config:
			perlbin = config['perlbin']
		else:
			perlbin = '/usr/bin/perl'

	#Limpar configurações antigas, para definir as novas configurações
	configdata['config'] = []


for ffile in dirs:
	filepath=path+'/'+str(ffile)
	with open(filepath, 'r') as jsonfile:
		data = json.load(jsonfile)

	#pp.pprint(data)
	print "Servidores virtuais: %s" %(len(data))
	print "Arquivo: %s" %(filepath)

	#Valores iniciais para armazenar nos arquivos
	numconfigfile = 0
	virtualservers = 1

	configfile = 'final/'+ffile+'_final.cf'+str(numconfigfile)
	#Criar arquivo em branco antes do Append
	with open(configfile, 'w') as outfile:
		outfile.write('')
	
	for virtual in data['servers']:
		if virtualservers >= maxvirtalinfile:
			#Gravar no config.json as configurações antes de mudar de arquivo de conf
			configdata['config'].append({   'configfile': configfile,
							'jsonfile' : filepath,
							'ldirectordbin' : '/usr/sbin/ldirectord-gprs',
							'perlbin' : perlbin,
							'virtualservers': virtualservers
							})

			virtualservers = 1
			numconfigfile += 1
			configfile = 'final/'+ffile+'_final.cf'+str(numconfigfile)


		if virtualservers == 1:
			#Criar um arquivo em branco
			with open(configfile, 'w') as outfile:
				outfile.write('')

			with open(configfile, 'a') as outfile:

				for config in data['config']:
					if 'checktimeout' in config:
						outfile.write("checktimeout="+config['checktimeout']+"\n")

					if 'checkinterval' in config:
						outfile.write("checkinterval="+config['checkinterval']+"\n")

					if 'autoreload' in config:
						outfile.write("autoreload="+config['autoreload']+"\n")

					if 'logfile' in config:
						outfile.write("logfile="+config['logfile']+"\n")

					if 'quiescent' in config:
						outfile.write("quiescent="+config['quiescent']+"\n")
				
				x = 1
				info = {}

				#Colocar no inicio do arquivo o pingpong-master
				for master in data['masterservice']:
					if 'virtual' in master:
						x = 0
						info[x] = []
						info[x].append("virtual="+master['virtual'])

					if 'real' in master:
						x += 1
						info[x] = []
						info[x].append("    real="+master['real'])

					if 'service' in master:
						x = 10
						info[x] = []
						info[x].append("    service="+master['service'])

					if 'protocol' in master:
						x = 12
						info[x] = []
						info[x].append("    protocol="+master['protocol'])

					if 'negotiatetimeout' in master:
						x = 13
						info[x] = []
						info[x].append("    negotiatetimeout="+master['negotiatetimeout'])

					if 'checktype' in master:
						x = 14
						info[x] = []
						info[x].append("    checktype="+master['checktype'])

					if 'checkcommand' in master:
						x = 15
						info[x] = []
						info[x].append("    checkcommand="+master['checkcommand'])

					if 'scheduler' in master:
						x = 11
						info[x] = []
						info[x].append("    scheduler="+master['scheduler'])

				#Gravar no arquivo na ordem correta
				for value in info:
					outfile.write(info[value][0]+"\n")


		with open(configfile, 'a') as outfile:
			#Gravar no arquivo somente as variaveis 'virtuais' que se pareçam um um IP
			if re.search('[0-9]{1,3}\.*', virtual):
				outfile.write("virtual="+virtual+"\n")
			for info in data['servers'][virtual]:
				if 'real' in info:
					outfile.write("    real="+info['real']+"\n")

				if 'service' in info:
					outfile.write("    service="+info['service']+"\n")

				if 'protocol' in info:
					outfile.write("    protocol="+info['protocol']+"\n")

				if 'negotiatetimeout' in info:
					outfile.write("    negotiatetimeout="+info['negotiatetimeout']+"\n")

				if 'checktype' in info:
					outfile.write("    checktype="+info['checktype']+"\n")

				if 'checkcommand' in info:
					outfile.write("    checkcommand="+info['checkcommand']+"\n")

				if 'scheduler' in info:
					outfile.write("    scheduler="+info['scheduler']+"\n")

			virtualservers += 1


	#Gravar no config.json as configurações no final do loop
	configdata['config'].append({   'configfile': configfile, 
					'jsonfile' : filepath,
					'ldirectordbin' : '/usr/sbin/ldirectord-gprs',
					'perlbin' : perlbin,
					'virtualservers': virtualservers
					})




#Gravar arquivo de configuração principal
with open('config.json', 'w') as outfile:
	json.dump(configdata, outfile, indent = 2)
