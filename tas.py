from io import BytesIO
from os import system
from urllib.request import urlopen
import requests, zipfile
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
def hosts_entry(domain_name):
	f=open("/etc/hosts","r+")
	dom=f.readlines()
	for dmn in dom:
		if domain_name in dmn:
			print ("Domain name already exist in /etc/hosts, proceeding further...")
			con=True
			break
		else:
			con=False
	if not con:
		f.seek(0,2)
		seq=[localhost_ip +' '+ domain_name]
		f.writelines(seq)
		print ("Domain name entry in /etc/hosts file is done.")
	f.close()
def nginx_configuration(domain_name):
	if os.path.isfile("/etc/nginx/sitesavailable/%s"%domain_name):
		f=open("/etc/nginx/sites-available/%s"%(domain_name),"r+")		
		f.write("""sever{
	server_name %s *.%s;
	access_log   /var/log/nginx/%s.access.log;
	error_log    /var/log/nginx/%s.error.log;
	index index.php;
        root /var/www/%s/htdocs;
        location / {
                try_files \$uri \$uri/ /index.php?\$args; 
        }
        location ~ \.php$ {
                include fastcgi_params;
		#fastcgi_pass unix:/var/run/php5-fpm.sock;
		fastcgi_pass 127.0.0.1:9000;
        }
}"""%(domain_name,domain_name,domain_name,domain_name,domain_name))
		try:
			os.symlink("/etc/nginx/sites-available/%s"%domain_name, "/etc/nginx/sites-enabled/%s"%domain_name)
		except OSError as e:
			if e.errno !=17:
				raise
			pass
	else:
		print("nginx already configured for this domain")
def wordpress(domain_name):
	if os.path.isfile("/var/www/%s/wordpress/"): 
		print("Downloading and extracting wordpress into %s Document root.."%domain_name)
		request=requests.get("http://wordpress.org/latest.zip")
		zp=zipfile.ZipFile(BytesIO(request.content))
		zp.extractall("/var/www/%s/"%domain_name)
		print ("Done..")
	else:
		print("wordpress already present in %s Document root"%domain_name)
def mysqldb(domain_name):
	y=domain_name.replace(".", "")
	p="".join((y,"_db"))
	print ("Password for the Database")
	try:
		os.system("mysql -u root -p -e 'CREATE DATABASE %s'"%p)
	except OSError as e:
		if e.errno !=1007:
			raise
		pass	
	print ("Database created")
	'''
	salt = requests.get("https://api.wordpress.org/secret-key/1.1/salt/")
	with open("/var/www/"+domain_name+"/wordpress/wp-config-sample.php", "r") as sample:
		lines = sample.readlines()
		with open("/var/www/"+domain_name+"/wordpress/wp-config.php", "w") as config:
			for line in lines:
				config.write(re.sub(r'database_name_here', p , line))
	with open("/var/www/%s/wordpress/wp-config.php"%domain_name, "r") as config:
		lines = config.readlines()
		with open("/var/www/%s/wordpress/wp-config.php"%domain_name, "w") as config:
			for line in lines:
				config.write(re.sub(r'username_here', 'root' , line))
	with open("/var/www/%s/wordpress/wp-config.php"%domain_name, "r") as config:
		lines = config.readlines()
		with open("/var/www/%s/wordpress/wp-config.php"%domain_name, "w") as config:
			for line in lines:
				config.write(re.sub(r'password_here', '\n' , line))
	with open("/var/www/%s/wordpress/wp-config.php"%domain_name, "r") as config:
		block = config.read()
		with open("/var/www/%s/wordpress/wp-config.php"%domain_name, "w") as config:
			config.write(re.sub(r'/\*\*\#@\+.*?\#@-\*/', salt.read(), block,flags=re.DOTALL))
	os.system("chown -R www-data:www-data /var/www/%s"%domain_name)
'''
def main():
	usercheck()
	phpcheck()
	mysqlcheck()
	nginxcheck()
	print("Enter the Domain Name")
	domain_name = str(input(">>"))
	localhost_ip=str([(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])
	print("your localhost ip is:\n%s"%localhost_ip)
	hosts_entry(domain_name)
	nginx_configuration(domain_name)
	wordpress(domain_name)
	mysqldb(domain_name)
	print("OPEN %s IN BROWSER"%domain_name)
main()
