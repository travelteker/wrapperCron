#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Wrapper para invocar ejecución proceso cron, creando un log donde se recoge la salida del proceso de ejecución para procesarlo en ELK5

#capturar parametros del script y hacer la funcionalidad -h ó --help
from argparse import ArgumentParser
import os
import sys
import hashlib
from datetime import *
import subprocess


import time
import fcntl
import logging

import string
import math
import random


FICHERO_LOG = "/var/local/newlogs/CORTO/wrapperCron.log"
LOCK_LOG =  "/var/local/newlogs/CORTO/wrapperCronLock.log"
PATHLOCKFILE = "/var/local/media/sincopia/";


#Obtener la fecha hora actual
def tiempoActual():
	#Devolver una lista con 2 formatos de fecha, el ISO y el epoch (numero de segundos transcurridos)
	my_time = [datetime.today().strftime("%d/%m/%Y %H:%M:%S.%f"),datetime.today().strftime("%s"),datetime.today().strftime("%d/%m/%Y"),datetime.today().strftime("%H:%M:%S")]
	return my_time


#Comprobar que existe el path en el sistema
def checkPath(path):
	return os.path.isfile(path)


#Genera un uniqid para etiquetar un proceso
def uniqid(prefix='', more_entropy=False):
    m = time.time()
    uniqid = '%8x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
    if more_entropy:
        valid_chars = list(set(string.hexdigits.lower()))
        entropy_string = ''
        for i in range(0,10,1):
            entropy_string += random.choice(valid_chars)
        uniqid = uniqid + entropy_string
    uniqid = prefix + uniqid
    return uniqid


#Devolver un hash MD5 de un string dado
def hashMD5(value):
	_hash = hashlib.md5()
	_hash.update(value)
	return _hash.hexdigest()


#Devolver el nombre del fichero desde un path
def getFileOfPath(path):
	segmentar = os.path.split(path)
	return segmentar[1]


#Registrar marca de tiempo en fichero log
def timing(fecha,epoch,onlyFecha,onlyHour,idproceso,lenguaje,path,nameFile,argumentos,duracion,salida,error):
	log = open(FICHERO_LOG,"a")
	if argumentos == None:
		argumentos = "---"
	log.write(fecha + '|' + str(epoch) + "|" + onlyFecha + "|" + onlyHour + "|" + idproceso + "|" + lenguaje + '|' + path + '|' + nameFile + '|' + argumentos + '|' +  str(duracion) + '|' + salida + '|' + error + '\n')
	log.close()



#Preformatear la salida de la duración del proceso con precisión hasta el segundo
def duration(endEpoch,startEpoch):
	totalSegundos = int(endEpoch) - int(startEpoch)
	if(totalSegundos < 60):
		salida = "0|0|" + str(totalSegundos)
	elif(totalSegundos>=60 and totalSegundos < 3600):
		#Configurar valor para minutos y segundos
		minutos = totalSegundos // 60
		segundos = totalSegundos % 60
		salida = "0|" + str(minutos) + "|" + str(segundos)
	elif(totalSegundos >= 3600):
		horas = totalSegundos // 3600
		minutos = totalSegundos % 3600
		segundos = minutos % 60
		salida = str(horas) + "|" + str(minutos) + "|" + str(segundos)

	#SALIDA SE DEVUELVE EN FORMATO HORAS|MINUTOS|SEGUNDOS
	return salida


#Ejecutar linea de comandos desde consola o interprete de comandos directamente como su fuera el crontab
def executor(lenguaje,paht,argumentos):

	if(argumentos == None):
		comando = lenguaje + " " + path
	else:
		#argumentos es un string, obtener los parámetros desde el string
		listArgumentos = argumentos.split(";")
		params = ' '.join([str(x) for x in listArgumentos])
		comando = lenguaje + " " + path + " " + params


	proc = subprocess.Popen(comando,
	                        shell=True,
	                        stdin=subprocess.PIPE,
	                        stdout=subprocess.PIPE,
	                        stderr=subprocess.STDOUT,
	                        )
	stdout_value, stderr_value = proc.communicate('through stdin to stdout\n')

	#Creamos un diccionario para recoger salida y error
	msg = {}
	if stdout_value != "":
		if stderr_value == None:
			msg["error"] = "---"
			msg["salida"] = repr(stdout_value)
		else:
			msg["salida"] = repr(stdout_value)
			msg["error"] = repr(stderr_value)
	else:
		if stderr_value == None:
			msg["salida"] = "---"
			msg["error"] = "---"
		else:
			msg["error"] = repr(stderr_value)
			msg["salida"] = "---"


	return msg


#Función principal para la ejecución del proceso
def runner(lenguaje,path,nameFile,argumentos):
	
	idproceso = uniqid()

	start = tiempoActual()
	startFecha = start[0]
	startEpoch = start[1]
	startOnlyFecha = start[2]
	startOnlyHour = start[3]


	if not checkPath(path):
		salida = "---"
		error = "Ruta no válida o fichero no existe"
		#Python no puede concatenar objetos de distintos tipo por ejemplo str+int tienen que ser todos str
		# 0 horas | 0 minutos | 0 segundos ---> 0|0|0
		timing(startFecha,startEpoch,startOnlyFecha,startOnlyHour,idproceso,lenguaje,path,nameFile,argumentos,"0|0|0",salida,error)
		return 0

	#Llamar a la funcion que ejecutará el cron pasandole los argumentos necesarios
	descripcion = executor(lenguaje,path,argumentos)
	salida = descripcion["salida"]
	error = descripcion["error"]
	#Llamar a la funcion de finalizacion de proceso para volver a grabar los datos
	end = tiempoActual()
	endFecha = end[0]
	endEpoch = end[1]
	endOnlyFecha = end[2]
	endOnlyHour = end[3]

	#Formateamos la salida de duracion del proceso hasta precision del segundo
	duracion = duration(endEpoch,startEpoch)

	#Vamos a loguear una única linea por evento, donde se pondrán las fechas y tiempos de inicio del proceso y los datos de duración se obtendrán al finalizar el proceso
	timing(startFecha,startEpoch,startOnlyFecha,startOnlyHour,idproceso,lenguaje,path,nameFile,argumentos,duracion,salida,error)



if __name__ == '__main__':


	parser = ArgumentParser()
	parser.add_argument("-l","--language",dest="language",help="Lenguaje con el que se va a ejecutar el script",metavar="FILE", required=True)
	parser.add_argument("-p","--path",dest="path",help="Path absoluto donde se encuentra el script a ejecutar",metavar="PATH", required=True)
	parser.add_argument("-a","--argumentos",dest="arg",help="Argumentos opcionales a ejecutar con el script, se especificaran en formato 'arg1|arg2|...|argN'. Los argumentos no pueden contener espacios en blanco.",metavar="ARG")
	args = parser.parse_args()
	
	
	lenguaje = args.language
	path = args.path
	#Obtener un identificador para este path, por ejemplo MD5 CHECKSUM
	#identificador = hashMD5(path)
	#Obtener el nombre del fichero a ejecutar
	nameFile = getFileOfPath(path)

	argumentos = args.arg

	#Cada cron que ejecuta un fichero debe tener un fichero *.PID propio, para llevar el control de proceso activo
	LOCKFILE = PATHLOCKFILE+"/cronLock"+nameFile+".pid";
	

	#Preparamos nuestro objeto logger
	logging.basicConfig(filename = LOCK_LOG, format = '%(asctime)s|%(levelname)s|%(message)s', level = logging.DEBUG)

	#Iniciamos el bloque de fichero para identificar que el proceso se está ejecutando
	#Modo apertura fichero para lectura "+", trunca el fichero en cada operación
	try:
		fileLock = open(LOCKFILE,'w+')
		fcntl.flock(fileLock,fcntl.LOCK_EX | fcntl.LOCK_NB)
	
		#Ejecutamos el proceso en cuestión
		runner(lenguaje,path,nameFile,argumentos)

		#Al finalizar el script liberamos el bloqueo
		fcntl.flock(fileLock, fcntl.LOCK_UN)

	except IOError as e:
		logging.debug("I/O error({0}): {1}".format(e.errno, e.strerror))


	sys.exit(0)
