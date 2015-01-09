from os import system
import os
import socket
import sys
import subprocess

def usercheck():
	if os.geteuid() !=0:
		sys.exit("you need to have root privileges to run this script.\n Kindly run using sudo.\n Exiting...")

def phpcheck():
	phpstatus=system('php --version')
	if phpstatus != 0:
		print ("PHP missing: Installing PHP.....")
		subprocess.Popen("sudo apt-get install php5-cli", shell=True).wait()

def mysqlcheck():
	mysqlstatus= system('mysql --version')
	if mysqlstatus != 0:
		print ("MYSQL missing: Installing MYSQL.....")
		subprocess.Popen("sudo apt-get install mysql-server",shell=True).wait()

def nginxcheck():
	nginxstatus= system('nginx -v')
	if nginxstatus != 0:
		print ("Nginx Missing: Installing Nginx")
		subprocess.Popen("sudo add-apt-repository ppa:nginx/stable",shell=True).wait()
		subprocess.Popen("sudo apt-get update",shell=True).wait()
		subprocess.Popen("sudo apt-get install nginx-full",shell=True).wait()
