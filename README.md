# AInterviewer Services
This project contains the API and backend for the AInterviewer application

## Build application

### To build Docker images for the api
- Build docker image
`docker build -t ainterviewer/ainterviewer-services:<version> -f platform/Dockerfile .`

- Push image
`docker push ainterviewer/ainterviewer-services:<version>`


### To build Docker images for cron tasks
- Build docker image
`docker build -t ainterviewer/ainterviewer-services-tasks:<version> -f platform/Dockerfile-tasks .`

- Push image
`docker push ainterviewer/ainterviewer-services-tasks:<version>`


## Copy files to server

`scp -r * <user>@<ip_address>:/app`

## Installation
After install docker in the server:

Create a folder called `grafana` then run the application `docker-compose up -d`
* Check that the folder grafana is in `/root/app/` if not change the path in `docker-compose.yml`


### Generate a random key string
`openssl rand -base64 32`


### Create read only user in mongodb
`use admin`

`db.createUser({user: "<user>", pwd: "<pass_in_plain_text>", roles: [{role: "read", db: "ainterviewer"}]})`