import requests
#import threading
from concurrent.futures import ThreadPoolExecutor

domain = 'youtube.com'

with open('subdomains10000.txt') as file:
    subdomains = file.read().splitlines()

discovered_subdomains = []

#lock = threading.Lock()

def check_subdomain(subdomain):
    url = f'http://{subdomain}.{domain}'
    try:
        requests.head(url,timeout=3)
        return url
    except requests.RequestException:
        return None
    
with ThreadPoolExecutor(max_workers=200) as exe:
    for result in exe.map(check_subdomain, subdomains):
        if result:
            print("[+]Discovered Subdomain: ",result)
            discovered_subdomains.append(result)

with open("discovered_subdomains.txt","w") as f:
    f.write("\n".join(discovered_subdomains))




    '''
    else:
        print("[+]Discovered Subdomain: ",url)
        with lock:
            discovered_subdomains.append(url)
    '''

'''

threads=[]
for subdomain in subdomains:
    thread = threading.Thread(target=check_subdomain,args=(subdomain,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

with open("discovered_subdomains.txt",'w') as f:
    for subdomain in discovered_subdomains:
        print(subdomain,file=f)
'''