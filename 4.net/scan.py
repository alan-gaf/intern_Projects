import scapy.all as scapy
import socket
import threading
from queue import Queue
import ipaddress


def scan(ip,result_q):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet= broadcast/arp_request
    answer = scapy.srp(packet,timeout=1,verbose = False)[0]

    clients = []
    for client in answer:
        client_info = {'IP':client[1].psrc,'MAC':client[1].hwsrc}
        try:
            hostname = socket.gethostbyaddr(client_info['IP'])[0]
            client_info['Hostname']= hostname
        except socket.herror:
            client_info['Hostname'] = 'Unknown'
        except Exception as e:
            print("error",e)
        clients.append(client_info)
    result_q.put(clients)

def print_result(result):
    print('IP'+" "*20+'MAC'+" "*20+'Hostname')
    print('-'*80)
    for client in result:
        print(client['IP']+'\t\t'+client['MAC']+'\t\t'+client['Hostname'])


def main(cidr):
    result_q = Queue()
    threads=[]
    network = ipaddress.ip_network(cidr, strict = False) 

    for ip in network.hosts():
        thread = threading.Thread(target = scan ,args =(str(ip),result_q))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    
    all_clients = []
    while not result_q.empty():
        all_clients.extend(result_q.get())

    print_result(all_clients)

if __name__ == "__main__":
    cidr = input("Enter network ip address:")
    main(cidr) 