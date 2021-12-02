# -*- coding: utf-8 -
import re
from pkgs.fastcloud import *



def menu():
    with open('./pkgs/author.txt', 'r') as f:
        print(f.read())
    f.close()
    while True:
        userInput=''
        with open('./pkgs/menu.txt', 'r') as f:
            d = f.read()
            print(d)
        f.close()
        while userInput=='':
            userInput=input('请输入菜单选项：')
            if re.match(r'^[+]{0,1}(\d+)$',userInput) and int(userInput) in range(len(cmds)):
                exec(cmds[int(userInput)]+'()')
                break
            else:
                print('Warning：输入有误！')
            userInput=''
            

if __name__ == "__main__":
    cmds = Cmds
    menu()