import subprocess
import time
import re


# 菜单选项映射
_Cmds = [
    'update_script',
    'checkDocker',
    'checkDNS',
    'install_fastcloud',
    'myquit'
]

# 菜单选项函数
def checkDocker():
    docker_version, dcompose_version = checkDDC()
    checker1 = docker_version == 'not installed' and dcompose_version == 'not installed'
    checker2 = docker_version == 'not installed' or dcompose_version == 'not installed'
    if checker1 or checker2:
        print('-'*30)
        print('未检测到所需的必要组件：')
        print('Docker-CE')
        print('docker-compose')
        print('-'*30)
        userChoice = ''
        while userChoice == '':
            userChoice = input('是否先安装必要组件(y/n)：')
            if re.match(r'[y|Y]', userChoice) or re.match(r'[y|Y][e|E][s|S]', userChoice):
                install_docker()
                install_docker_compose()
                return 'done'
            elif userChoice == 'n' or userChoice == 'N':
                print('缺少必要组件，无法安装')
                return 'back'
            else:
                userChoice = ''
                print("输入正确选择")
    else:
        print('检测到已经安装docker和docker-compose，可以直接安装fastcloud')
        return 'ok'


def install_fastcloud():
    res=checkDocker()
    if res == 'ok':
        userDomain, userEmail = getUserInput()
        print('确认你的信息')
        print('-'*30)
        print('申请证书域名：' + userDomain)
        print('你的邮箱：'+userEmail)
        print('-'*30)
        print('【回车/y】确认，【n/N】重新输入,【b/back】返回上级，【ctrl+c/exit】退出')
        userChoice = input('输入：')
        if userChoice == 'y' or userChoice == '' or userChoice == 'Y':
            dns = getDNS(userDomain)
            ip = getIP()
            if dns == ip:
                modifyEnvFile(userDomain, userEmail)
                time.sleep(2)
                deploy_fastcloud()
                return 'back'
            else:
                print('域名解析的IP地址与本机IP不相符，请检查你的DNS服务之后再尝试运行本脚本')
                return 'back'
        elif userChoice == 'n' or userChoice == 'N':
            userDomain, userEmail = getUserInput()
        elif userChoice == 'b' or userChoice == 'B' or userChoice == 'back':
            return 'back'
        elif userChoice == 'e' or userChoice == 'E' or userChoice == 'exit':
            return 'exit'
    return 'back'

def checkDNS():
    while True:
        userDomain=input('请输入查询的域名：')
        print('确认你的信息')
        print('-'*30)
        print('申请证书域名：' + userDomain)
        print('-'*30)
        print('【回车/y】确认，【n/N】重新输入,【b/back】返回上级，【ctrl+c/exit】退出')
        userChoice = input('输入：')
        if re.match(r'[y|Y]',userChoice) or userChoice == '':
            dns = getDNS(userDomain)
            ip = getIP()
            print('-'*30)
            print("域名解析的IP是："+dns)
            print("你的IP是："+ip)
            print("-"*30)
            if dns == ip:
                print("域名解析和本地ip相符，可以申请证书")
                break
            else:
                print("域名解析和本地IP不相符，请检查DNS解析服务")
                break
        elif re.match(r'[n|N]',userChoice):
            pass
        elif re.match(r'[b|B]',userChoice) or re.match(r'[b|B]ack',userChoice):
            break
        elif re.match(r'[e|E]',userChoice) or re.match(r'[e|E]xit',userChoice):
            myquit()
    return 'back'

def myquit():
    print('Bye，have a good time!')
    exit()

# 脚本相关
def update_script():
    print('update script...')
    return 'back'


# Docker相关
def install_docker():
    downloadDockerScrpit = 'curl -fsSL https://get.docker.com -o get-docker.sh'
    execDockerScript = 'sh get-docker.sh'
    retcode, output = subprocess.getstatusoutput(downloadDockerScrpit)
    if retcode == 0:
        try:
            subprocess.run(execDockerScript, shell=True,
                       input='y', encoding='utf-8', check=True)
        except subprocess.CalledProcessError as e:
            print(e)

        else:
            print('Docker 安装成功！')
            return 'ok'
    else:
        print('Docker 安装失败，请检查你的网络连接.')
        return 'error'


def install_docker_compose():
    installDockerCompsoe = 'apt-get install docker-compose'
    try:
        subprocess.run(installDockerCompsoe, shell=True,
                       input='y', encoding='utf-8', check=True)
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'
    else:
        print('Docker-compose 安装完成！')
        return 'ok'


def checkDDC():
    ddc_stat = []
    stmt = ['docker -v', 'docker-compose -v']
    for i in stmt:
        retcode, output = subprocess.getstatusoutput(i)
        if retcode == 0:
            version = re.split(r'[\s\,]+', output)
            ddc_stat.append(version)
        else:
            ddc_stat.append('not installed')
    return ddc_stat[0:]


# fastcloud
def getDNS(userDomain):
    stmt = 'ping ' + userDomain+' -c 1'
    pattern_1 = re.compile(userDomain+'\s\(\d+.\d+.\d+.\d+\)')
    pattern_2 = r'\d+.\d+.\d+.\d'
    out,err = subprocess.getstatusoutput(stmt)
    if out == 0:
        filterRes=re.findall(pattern_1,err)
        res = re.findall(pattern_2, filterRes[0])
        return res[0]
    else:
        res='None'    
        return res


def getIP():
    stmt = 'curl https://api-ipv4.ip.sb/ip'
    out,err= subprocess.getstatusoutput(stmt)
    pattern=r'\d+.\d+.\d+.\d'
    if out == 0:
        res = re.findall(pattern,err)
        return res[0]
    else:
        res = 'none'
        return res


def modifyEnvFile(domain, email):
    with open('./.env.fastcloud', 'w') as f:
        f.write('YOUR_DOMAIN='+domain+'\nYOUR_EMAIL='+email)
    f.close()


def getUserInput():
    userDomain = ''
    userEmail = ''
    while userDomain == '':
        userDomain = input('Please enter your domain: ')
    while userEmail == '':
        userEmail = input('Please enter an email: ')
    return userDomain, userEmail


def deploy_fastcloud():
    dcomposeUp = 'docker-compose --env-file .env.fastcloud up -d'
    try:
        subprocess.run(dcomposeUp, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'
    else:
        print('fastcloud deploy done')
        return 'ok'


def modifyNginxConf(domain):
    sample_dir='./pkgs/nginx_sample.conf'
    with open(sample_dir,'r') as sample:
        sample_data=sample.read()
    sample.close()
    with open('./pkgs/proxy.conf','w') as f:
        pattern = r'{YOUR_DOMAIN}'
        res =re.sub(pattern,domain,sample_data)
        f.write(res)
    f.close()


def updateNginxConf():
    pass
