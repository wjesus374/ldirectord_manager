#!/usr/bin/python
# -*- coding: utf-8 -*-

#yum install perl-Mail* perl-Socket6 perl-IO-Socket-INET6 ipvsadm -y

import json
import re
import os
import sys

import pprint
pp = pprint.PrettyPrinter(indent=4)


def readldconf(path,jsonconfigdir):

	configregex = '^checktimeout|^checkinterval|^autoreload|^logfile|^quiescent'
	dataregex = '^real|^service|^protocol|^negotiatetimeout|^checkcommand|^scheduler|^checktype'

	#path = 'conf'
	path = path
	dirs = os.listdir( path )

	with open('config.json', 'r') as jsonfile:
		configdata = json.load(jsonfile)
		for config in configdata['data']:
			if 'masterservice' in config:
				masterservice = config['masterservice']
			else:
				masterservice = 'pingpong_master'
				#masterservice = 'pingpong_master|check_sonda_fd'

			if 'masterservicetype' in config:
				masterservicetype = config['masterservicetype']
			else:
				masterservicetype = 'gprs'


	for ffile in dirs:
		filepath=path+'/'+str(ffile)

		data = {}
		data['config'] = []
		data['masterservice'] = []
		data['servers'] = []
		servers = {}

		with open(filepath, 'r') as ldirectordfile:
			for info in ldirectordfile:

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
						data['masterservice'].append({'servicetype' : masterservicetype})
					servers[virtual].append({key:config})


			data['servers'] = servers
			del servers
			#Criar uma chave com o serviço Master coletado no loop de organização
			for master in data['masterservice']:
				if 'virtual' in master:
					#print(master['virtual'])
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

		
			with open(jsonconfigdir+'/'+ffile+'.json', 'w') as outfile:
				#pp.pprint(data['masterservice'])
				#pp.pprint(data)
				#pp.pprint(data['servers'])
				json.dump(data, outfile)


def loadjsonconf(path,ldnewdir):
	#path = 'json'
	path = path
	ldnewdir = ldnewdir

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


	dirs = os.listdir( path )

	for ffile in dirs:
		filepath=path+'/'+str(ffile)
		with open(filepath, 'r') as jsonfile:
			data = json.load(jsonfile)

		#pp.pprint(data)
		#print "Servidores virtuais: %s" %(len(data))
		#print "Arquivo: %s" %(filepath)

		#Valores iniciais para armazenar nos arquivos
		numconfigfile = 0
		virtualservers = 1

		configfile = ldnewdir+'/'+ffile+str(numconfigfile)+'.cf'
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
								'servicetype' : servicetype,
								'virtualservers': virtualservers
								})

				virtualservers = 1
				numconfigfile += 1
				configfile = ldnewdir+'/'+ffile+str(numconfigfile)+'.cf'


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
						if 'servicetype' in master:
							servicetype = master['servicetype']
		

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
						###Servicetype == external fixado pro Radius
						if info['checktype'] == 'external':
							servicetype = 'radius'


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
						'servicetype' : servicetype,
						'virtualservers': virtualservers
						})

	#Gravar arquivo de configuração principal
	with open('config.json', 'w') as outfile:
		json.dump(configdata, outfile, indent = 2)

def addnewport(lyraservice,port,path):
	lyraservice = lyraservice
	port = port
	path = path
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

			#if 'masterservicetype' in config:
			#	masterservicetype = config['masterservicetype']

		for config in configdata['config']:
			if 'servicetype' in config:
				#print(config['servicetype'])
				servicetype = config['servicetype']

			if 'virtualservers' in config:			
				virtualservers = config['virtualservers']
				configfile = config['configfile']
				jsonconfigfile = config['jsonfile']

				if virtualservers < maxvirtalinfile and name == servicetype:
					print "As novas configurações serão gravas no arquivo: %s" %(str(configfile))
					print "Virtualservers no arquivo: %s" %(str(virtualservers))
					#sys.exit(0)

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

		print "A porta será gravada no arquivo: %s" %(str(jsonconfigfile))
		lddata = {}
		with open(jsonconfigfile, 'r') as jsonfile:
			data = json.load(jsonfile)
			virtualport=str(virtual)+':'+str(port)
			lddata[virtualport] = []
			for real in reals:
				lddata[virtualport].append({'real' : real+':'+str(port)+' '+realmasq})
		
			lddata[virtualport].append({"ip": str(virtual)})
			lddata[virtualport].append({"porta": port})
			lddata[virtualport].append({"scheduler": scheduler})
			lddata[virtualport].append({"protocol": protocol})
			lddata[virtualport].append({"negotiatetimeout": negotiatetimeout})
			lddata[virtualport].append({"service" : ldservice})

			print(lddata)
			print(data['servers'])
			data['servers'].update(lddata)
			#del lddata

		with open(jsonconfigfile, 'w') as jsonfile:
			json.dump(data, jsonfile)

if __name__ == "__main__":
	#Definir na função a pasta com os arquivos de configuração do ldirectord
	#ldconfigdir jsonconfigdir
#OK	readldconf('conf','json')
	readldconf('conf','json')
	#Definir na função a pasta para ler os json
	#jsonconfigdir ldnewdir
#OK	loadjsonconf('json','final')
	loadjsonconf('json','final')

	#Criar novos json's com base nos arquivos 'finais' criados
#OK	readldconf('final','json2')
	readldconf('final','json2')
	#Criar novos arquivos ld com base nos novos json's
#OK	loadjsonconf('json2','final2')
	loadjsonconf('json2','final2')

	#Add nova porta
	#lyraservice #port #jsonconfigdir
	addnewport('gprs','12345','json2')
	#addnewport('radius','12345','json2')

	#Recarregar configurações do json para ldfile
	loadjsonconf('json2','final2')

