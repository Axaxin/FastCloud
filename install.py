# -*- coding: utf-8 -
import subprocess as sp
import re
import time
import json



def createConfig(content):
    mykeys = ['YOUR_DOMAIN', 'YOUR_EMAIL', 'UPLOAD_SIZE']
    mydict = dict(zip(mykeys, content))
    myjson = json.dumps(mydict)
    with open('./info.json', 'w') as f:
        f.write(myjson)


def getUserInfo():
    domain = input('请输入申请证书的域名：')
    email = input('请输入电子邮箱地址：')
    uploadsize = input('请输入文件上传限制（默认 100M）:') or '100M'
    return [domain, email, uploadsize]


def userPickYN():
    while True:
        answ = input('输入[y/n]:') or 'y'
        if answ != '' and re.match(r'^[y|Y]+', answ):
            answ = True
            break
        elif answ != '' and re.match(r'^[n|N]+', answ):
            answ = False
            break
        else:
            print('无效选择，请重新输入')
    return answ


def checkConfigExist():
    try:
        with open('./info.json', 'r') as f:
            content = f.read()
        return 0, content
    except:
        return 1, ''


def checkConfigisJson(content):
    try:
        readdict = json.loads(content)
        return 0, readdict
    except:
        return 1, ''


def checkConfigLegal(readdict):
    mydict = {'YOUR_DOMAIN': '', 'YOUR_EMAIL': '', 'UPLOAD_SIZE': ''}
    if readdict.keys() == mydict.keys():
        testDomain = re.match(r'\w+\.\w+', readdict['YOUR_DOMAIN'])
        testEmail = re.match(r'\w+\@+\w+\.\w+', readdict['YOUR_EMAIL'])
        testUpload = re.match(r'\d{1,4}[g|G|m|M]', readdict['UPLOAD_SIZE'])
        if testDomain and testEmail and testUpload and testUpload:
            return 0,readdict
        else:
            return 1,''
    else:
        return 1,''


def loadInfoConf():
    while True:
        ret, out = checkConfigExist()
        if ret == 0:
            ret, out = checkConfigisJson(out)
            if ret == 0:
                ret,out= checkConfigLegal(out)
                if ret == 0:
                    print('读取配置文件有效...')
                    print('-'*30)
                    print('【配置文件内容】')
                    print('需要注册证书的域名：'+out['YOUR_DOMAIN'])
                    print('你的邮箱：'+out['YOUR_EMAIL'])
                    print('文件上传限制：'+out['UPLOAD_SIZE'])
                    print('-'*30)
                    info=out
                    break
        print('配置信息有误，是否重写配置？')
        res = userPickYN()
        if res == True:
            info = getUserInfo()
            createConfig(info)
        elif res == False:
            print('没有有效配置信息，退出.')
            exit()
    return 0,info


def checkDNS(domain):
    print('正在检测DNS...')
    dns = getDNS(domain)
    ip = getIP()
    print('-'*30)
    print('你输入的域名为：'+domain)
    print("DNS解析为："+dns)
    print('你的IP是：'+ip)
    print('-'*30)
    time.sleep(2)
    if dns == ip:
        print('DNS解析和本地ip相符，可以继续')
        return True
    else:
        print('域名解析与本地ip不相符，请检查DNS再试。')
        return False


def getDNS(userDomain):
    stmt = 'ping ' + userDomain+' -c 1'
    pattern_1 = re.compile(userDomain+'\s\(\d+.\d+.\d+.\d+\)')
    pattern_2 = r'\d+.\d+.\d+.\d'
    out, err = sp.getstatusoutput(stmt)
    if out == 0:
        filterRes = re.findall(pattern_1, err)
        res = re.findall(pattern_2, filterRes[0])
        return res[0]
    else:
        res = 'None'
        return res


def getIP():
    stmt = 'curl https://api-ipv4.ip.sb/ip'
    out, err = sp.getstatusoutput(stmt)
    pattern = r'\d+.\d+.\d+.\d'
    if out == 0:
        res = re.findall(pattern, err)
        return res[0]
    else:
        res = 'none'
        return res


def checkDocker():
    print('正在检测Docker...')
    stmt = 'docker -v'
    retcode, output = sp.getstatusoutput(stmt)
    if retcode == 0:
        docker_version = re.split(r'[\s\,]+', output)[-1]
        print('Docker已经存在，版本为：'+docker_version)
    else:
        print('未检测到docker版本...')
        docker_version = 'None'
    return docker_version


def checkDCompose():
    print('正在检测docker-compose...')
    stmt = 'docker-compose -v'
    retcode, output = sp.getstatusoutput(stmt)
    if retcode == 0:
        dcompose_version = re.split(r'[\s\,]+', output)[-1]
        print('Docker-compose已经存在，版本为：'+dcompose_version)
    else:
        print('未检测到docker-compose版本...')
        dcompose_version = 'None'
    return dcompose_version


def installDocker():
    print('正在准备安装Docker...')
    downloadDockerScrpit = 'curl -fsSL https://get.docker.com -o get-docker.sh'
    execDockerScript = 'sh get-docker.sh'
    retcode, output = sp.getstatusoutput(downloadDockerScrpit)
    if retcode == 0:
        try:
            sp.run(execDockerScript, shell=True, check=True)
            print('Docker 安装成功！')
            return True
        except:
            print('Docker 安装失败，请检查你的网络连接.')
            return False


def installDCompose():
    print('正在准备安装docker-compose...')
    installDockerCompsoe = 'apt-get install docker-compose'
    try:
        sp.run(installDockerCompsoe, shell=True,
               input='y', encoding='utf-8', check=True)
        print('Docker-compose 安装完成！')
        return True
    except:
        print('Docker-compose 安装失败，请检查你的网络连接.')
        return False


def modifyEnvFile(domain, email):
    print('正在设置docker-compose变量...')
    temp = ''
    content = 'YOUR_DOMAIN='+domain+'\nYOUR_EMAIL='+email
    try:
        with open('./.env.fastcloud', 'w+') as f:
            f.write(content)
    except:
        print('配置文件路径有误...')
        return False
    try:
        with open('./.env.fastcloud', 'r') as f:
            temp = f.read()
    except:
        print('配置文件路径有误...')
        return False
    if temp == content:
        print('docker-compose环境变量设置成功！')
        return True
    else:
        print('docker-compose坏境变量设置失败...')
        return False


def deployCloud():
    print('正在部署fastcloud套件...')
    dcomposeUp = 'docker-compose --env-file .env.fastcloud up -d'
    try:
        sp.run(dcomposeUp, shell=True, check=True)
        print('fastcloud套件部署成功！')
        return True
    except sp.CalledProcessError as e:
        print(e)
        print('fastcloud套件部署失败...')
        return False


def addNginxConf(size):
    print('正在配置Nginx文件上传限制为'+size+'...')
    content = 'client_max_body_size '+size+';'
    try:
        with open('./nginx/conf/uploadsize.conf', 'w+') as f:
            f.write(content)
    except:
        print('配置文件有误...')
        return False
    try:
        with open('./nginx/conf/uploadsize.conf', 'r') as f:
            temp = f.read()
    except:
        print('配置文件有误...')
        return False
    if temp == content:
        res = reloadNginx()
        if res == True:
            print('Nginx上传文件限制设置成功，大小为：'+size)
            return True


def reloadNginx():
    print('正在重载Nginx...')
    stmt = 'docker exec nginx nginx -s reload'
    ret, res = sp.getstatusoutput(stmt)
    pat = r'[0-9a-zA-Z\s\[\]\:\#\s\/]*signal\sprocess\sstarted'
    if ret == 0 and re.match(pat, res):
        print('Nginx配置重载成功...')
        return True
    else:
        print('Nginx重载失败...')
        return False


if __name__ == "__main__":
    print('')
    print('')
    print('      Fastcloud 部署脚本')
    print('   ---authored by Axaxxin---')
    print('   https://github.com/Axaxxin')
    print('')
    toInstall=False
    while True:
        ret,out=loadInfoConf()
        if ret ==0:
            print('是否使用此配置？')
            answ=userPickYN()
            if answ==True:
                toInstall=True
                info=out
                break
            else:
                info=getUserInfo()
                createConfig(info)

    while toInstall==True:
        YOUR_DOMAIN=info['YOUR_DOMAIN']
        YOUR_EMAIL=info['YOUR_EMAIL']
        UPLOAD_SIZE=info['UPLOAD_SIZE']

        res = checkDNS(YOUR_DOMAIN)
        if res == False:
            break
        
        # print('测试中断点，是否继续？')
        # while True:
        #     answ=input('输入[y/n]:') or 'n'
        #     if answ and re.match(r'^[y|Y]+',answ):
        #         print('继续')
        #         break
        #     elif answ and re.match(r'^[n|N]+',answ):
        #         exit()
        #     else:
        #         print('无效输入，请重新输入')


        res = checkDocker()
        if res == 'None':
            res = installDocker()
            if res != True:
                break
        res = checkDCompose()
        if res == 'None':
            res = installDCompose()
            if res != True:
                break
        res = modifyEnvFile(YOUR_DOMAIN, YOUR_EMAIL)
        if res == False:
            break
        res = deployCloud()
        if res == False:
            break
        print('等待acme生成ssl证书...')
        waittime = 16
        for i in range(waittime)[-1::-1]:
            print('等待剩余 '+str(i)+'秒...', end='\r')
            time.sleep(1)
        res = addNginxConf(UPLOAD_SIZE)
        if res != True:
            break
        else:
            print('已完成所有配置安装，请登陆你的域名查看是否生效')
            print('退出安装脚本...')
            time.sleep(1)
            print('Bye，have a good time.')
            exit()

    print('安装失败，请检查配置文件信息或脚本完整性之后再尝试。')
