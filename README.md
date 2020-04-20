Rest Application (view Weather)
========================================

This is Flask and Cassandra RESTful application.
It has a feature like:
1.  Hash-based user authentication.
2.  Dynamically generated REST API.
3.  API for Weather (openweathermap.org/api).

I. structure
============
could-computing module  ├──
                          ├── main.py                   # the application code
                          ├── auth.db
                          ├──requirements.txt
                          ├── config.py           
                          ├── instance              
                        │   ├── config-keys.py          # Change API key here
                        ├── templates              # icludes all the html pages
                      │   ├── login_form.html

                         └── ...


II. Installation of python3 and the requirements
===============================================

   For Linux, Mac and Windows users:
  -------------------------------

 sudo apt updat
 sudo apt install python3 -pip
 pip3 install -r requirements.txt



III. Cassandra Installation Guide (Linux)
========================================


To use cqlsh ( the Cassandra query language shell) you need to install cassandra-driver:


pip install cassandra-driver

........................................................................
for not linux users you may need to install cqlsh and cassandra by run the following commands:

install cql
install Cassandra
brew install cassandra
..........................................................................


Starting/Stopping Cassandra
=============================
Use this command to start Cassandra:
-----------------------------------

sudo service cassandra start

Use this command to stop Cassandra:
-----------------------------------
sudo service cassandra stop

use this command to check the cassandra status:
----------------------------------------------

sudo service cassandra status


IV. Things you have to change in order to the service work well:
===================================================
Get a new API from (openweathermap.org/api) website and sign up (select free option).
Then replaced in config-keys.py file inside the instance.


 V. Running
===========

To run the server use the following command:

      $ python3 main.py
      Running on http://0.0.0.0:8080/


VI. Licence
============
  This project is open-sourced

**********************************************************

V. To run the sevice in the cloud:
==================================
1. log in to the cloud service, I have used AWS Educate
2. Create a new instance with type t2.medium scroll and select OS Ubuntu “Ubuntu Server16.04 LTS (HVM), SSD Volume Type”, with “64-bit (x86)”.  
3. from your command line connect to the instance using the follow command:
 ssh -i "key_name.pem" ubuntu@DNS_NAME.compute-1.amazonaws.com
4. install python3 and all the requirements:
   sudo apt update
   sudo apt install docker.io
   sudo apt install python3-pip
   pip3 install -r requirements.txt
   to upload the folder to the EC2 instance:
   scp -i path/to/pem path/to/file username@PublicDNS/home/username
   example(scp -i key-1.pem /home/latifah/cloud-computing-module/* ubuntu@ec2-3-93-238-47.compute-1.amazonaws.com:/home/ubuntu/cloud-module)

   You have to edit the following line:
   cluster = Cluster(IP address of your container, port)
   you can find it using the following command:
   sudo docker inspect app_weather (container name)
   to pull the cassandra Docker image:
   ----------------------------------

   sudo docker pull cassandra:latest

   To run a cassandra instance within docker:
   -----------------------------------------
  sudo docker run --name app_weather -d cassandra:latest

  To check that is running correctly:
  -----------------------------------
  sudo docker ps

  To calls the cql command line shell in the cassandra-test docker container:
  ---------------------------------------------------------------------------
  sudo docker exec -it app_weather cqlsh

 Create the KEYSPACE and required table(s):
 -----------------------------------------
  CREATE KEYSPACE  app_weather WITH REPLICATION ={'class' : 'SimpleStrategy', 'replication_factor' : 1};
  use app_weather;
  CREATE TABLE user_list (username text,city_name text, PRIMARY KEY (username, city_name)) ;

To run the application:
python3 main.py
..........
