import scapy.all as scapy
import socket
from scapy.all import ARP, Ether, srp





def scan_network(cidr):

    
    ans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.1.0/24"), timeout=2, verbose=True)[0]

    print("Count:", len(ans))
    for s, r in ans:
        print(r.psrc, r.hwsrc)
    
    arp_request = scapy.ARP(pdst=cidr)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request

    answered = scapy.srp(packet, timeout=2, verbose=False)[0]

    hosts = []
    for _, response in answered:
        ip = response.psrc
        mac = response.hwsrc
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = "Unknown"

        hosts.append({
            "IP": ip,
            "MAC": mac,
            "Hostname": hostname
        })

    return hosts


def print_hosts(hosts):
    print(f"{'IP':20} {'MAC':20} Hostname")
    print("-" * 60)
    for h in hosts:
        print(f"{h['IP']:20} {h['MAC']:20} {h['Hostname']}")


if __name__ == "__main__":
    #print(scapy.conf.iface)
    #scapy.show_interfaces()
    scapy.conf.iface = "Realtek PCIe GbE Family Controller"
    cidr = input("Enter network CIDR: ")
    hosts = scan_network(cidr)
    print_hosts(hosts)
