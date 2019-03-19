#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json

def readldconf(ldfile='ld.cf'):

	servers = {}
	servers = []

	dataregex = '^real|^service|^protocol|^negotiatetimeout|^checkcommand|^scheduler|^checktype'


	with open(ldfile, 'r') as ldirectordfile:
		for info in ldirectordfile:
			linha = info.strip()

			#Encontrar configurações do host virtual
			ldregex = re.search(dataregex,linha)

			if ldregex:
				config = linha
				config = re.sub('^.*=','',config)

				if re.search('real',linha):
					#Se for coletar somente o IP/Porta, utilizar esse try
					try:
						real = re.search('(real=)([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}):([0-9]{2,}).(masq.*)',linha)
						if real:
							#print("IP: [%s]" %real.group(2))
							ip = real.group(2)
							#print("Porta: [%s]" %real.group(3))
							porta = real.group(3)
							#Se for utilizar o dataregex, comentar essa linha
							servers.append({ip:porta})
					except Exception as e:
						print("Erro: [%s]" %e)

				#Se for armazenar todas as opções "virtuais", descomentar as linhas
				#key = ldregex2.string[ldregex2.start():ldregex2.end()]
				#servers.append({key:config})

	#Se for gerar um output externo (JSON) com todas as opções, descomentar as linhas
	#with open(ldfile+'.json', 'w') as outfile:
	#	json.dump(servers, outfile)
	return servers


if __name__ == "__main__":
	ldfile = 'ld.cf'
	returndata = readldconf(ldfile)

	#print(returndata)

	for data in returndata:
		for ip,port in data.items():
			print("IP: [%s] - Porta: [%s]" %(ip,port))
