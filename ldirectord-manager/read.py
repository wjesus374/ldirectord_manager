#!/usr/bin/python
# -*- coding: utf-8 -*-

#yum install perl-Mail* perl-Socket6 perl-IO-Socket-INET6 ipvsadm -y

import json
import re
import os

import pprint
pp = pprint.PrettyPrinter(indent=4)

#Definir o serviço master
#masterservice='pingpong_master'

configregex = '^checktimeout|^checkinterval|^autoreload|^logfile|^quiescent'
dataregex = '^real|^service|^protocol|^negotiatetimeout|^checkcommand|^scheduler'

path = 'conf'
dirs = os.listdir( path )

with open('config.json', 'r') as jsonfile:
	configdata = json.load(jsonfile)
	for config in configdata['data']:
		if 'masterservice' in config:
			masterservice = config['masterservice']
		else:
			masterservice = 'pingpong_master'
			#masterservice = 'pingpong_master|check_sonda_fd'


for ffile in dirs:
	filepath=path+'/'+str(ffile)

	data = {}
	data['config'] = []
	data['masterservice'] = []
	data['servers'] = []
	servers = {}


	with open(filepath, 'r') as ldirectordfile:
		for info in ldirectordfile:
			#linha = linha.replace("\t", "")
			#linha = re.sub('[\n]|^[ ]*|\t','', info)
			linha = info.strip()

			#Encontrar configurações
			ldregex = re.search(configregex,linha)
			#Encontrar configurações do host virtual
			ldregex2 = re.search(dataregex,linha)

			if ldregex:
				config = linha
				config = re.sub('^.*=','',config)

				key = ldregex.string[ldregex.start():ldregex.end()]
				data['config'].append({key:config})
			
			#Encontrar os host's virtuais
			if re.search('^virtual',linha):

				virtual = linha
				virtual = re.sub('virtual=','',virtual)
				servers[virtual] = []
				try:
					ip, porta = virtual.split(':')
					servers[virtual].append({'ip': ip})
					servers[virtual].append({'porta': porta})
					#data['servers'].append({virtual : {'porta': porta, 'ip': ip}})
				except:
					pass
			if ldregex2:
				config = linha
				config = re.sub('^.*=','',config)

				key = ldregex2.string[ldregex2.start():ldregex2.end()]

				#Se for um serviço "master", adicionar na key masterservice				
				if re.search(masterservice,config):
					data['masterservice'].append({'service' : config})
					data['masterservice'].append({'virtual' : virtual})

				servers[virtual].append({key:config})
				#data['servers'].append({virtual : w})


		data['servers'] = servers
		del servers
		#Criar uma chave com o serviço Master coletado no loop de organização
		for master in data['masterservice']:
			if 'virtual' in master:
				print(master['virtual'])
				for info in data['servers'][master['virtual']]:
					#print(info)
					if 'real' in info:
						data['masterservice'].append({'real': info['real']})
					if 'protocol' in info:
						data['masterservice'].append({'protocol': info['protocol']})
					if 'negotiatetimeout' in info:
						data['masterservice'].append({'negotiatetimeout': info['negotiatetimeout']})
					if 'scheduler' in info:
						data['masterservice'].append({'scheduler': info['scheduler']})
				#Deletar o master do data, para não duplicar entre os arquivos de configuração
				del data['servers'][master['virtual']]
		
		with open('json/'+ffile+'_data.json', 'w') as outfile:
			#pp.pprint(data['masterservice'])
			#pp.pprint(data)
			#pp.pprint(data['servers'])
			json.dump(data, outfile)



