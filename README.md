# FastCloud
Nextcloud with auto SSL configuration fast deploy, all based on docker
Nextcloud开源网盘+SSL全自动部署，全docker方案

### Docker image in used:
- jwilder/nginx-proxy
- nginxproxy/acme-companion
- nextcloud:20.0.14

### Requirement
1. Any x86 platform with the latest docker-ce(not being tested on old versions,but mostlikely compatible if yours is close to the recent)
2. python3 with basic modules
3. Your host must be publicly reachable on both port 80 and 443
4. The (sub)domains you want to issue certificates for must correctly resolve to the host

### Usage
1. Download the repo by:

```bash
git clone https://github.com/Axaxin/FastCloud.git
```
or 

```
wget https://github.com/Axaxin/FastCloud/releases/download/fastcloud/fastcloud.zip
```
then 

```
unzip fastcloud.zip
```

2. change directory into FastCloud folder and run the python3 script
```bash
cd FastCloud
python3 install.py
```

3. If it's a fresh start up, it will ask to rewrite/create a new json config, you will need to provide:
- the (sub)domain you want to use for visit your nextcloud and it's for register SSL certificate
- your email
- upload size limitation that you prefer(original nginx setting is limited, default of this script set to 100M)


### Caution
- you shouldn't use this script if there are other web services already running on your host since this installation requires/occupies port 80/443
- this installtion only suits for one user with light-weight use since it doesn't come with independent database along for massive use
- nginx configs are stored in /FastCloud/nginx/conf and CA certificates are /FastCloud/nginx/certs, all nextcloud data are under /FastCloud/nextcloud
