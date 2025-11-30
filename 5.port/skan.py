import socket
import concurrent.futures
import sys

red="\033[91m"
green = "\033[92m"
reset = "\033[0m"

def get_banner(sock):
    try:
        sock.settimeout(1)
        banner = sock.recv(1024).decode().strip()
        return banner
    except:
        return " "

def scan_port(target_ip,port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target_ip,port))
        if not result:
            try:
                service = socket.getservbyport(port,'tcp')
            except:
                service = 'Unknown'
            banner = get_banner(sock)
            return port,service,banner,True
        else:
            return port, "","",False
    except:
        print("error")
        return port, "","",False
    finally:
        sock.close()

def scan(target_host,start,end):
    target_ip = socket.gethostbyname(target_host)
    print("starting scan on host: ",target_ip)

    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5000) as exe:
        futures = {exe.submit(scan_port,target_ip,port):port for port in range(start,end+1)}
        total_ports = end-start+1
        for i,future in enumerate(concurrent.futures.as_completed(futures),start =1):
            port, service,banner,status = future.result()
            results.append((port,service,banner,status))
            sys.stdout.write(f"\rProgress: {i}/{total_ports} ports scanned")
            sys.stdout.flush()

    return results

if __name__=="__main__":

    target_host = input("enter your target ip : ")
    start_port = int(input("enter start port: "))
    end_port = int(input("enter end port: "))

    results = scan(target_host,start_port,end_port)

    sys.stdout.write("\n")

    formatted_results = "Port Scan Results:\n"
    formatted_results+= "{:<8} {:<15} {:<10}\n".format("Port","Service","Status")
    formatted_results+= '-' *85 +"\n"
    for port ,service ,banner ,status in results:
        if status:
            formatted_results = f"{red}{port:<8}{service:<15}{'Open':<10}{reset}\n"
            if banner:
                banner_lines = banner.split('\n')
                for line in banner_lines:
                    formatted_results +=f"{green}{'':<8}{line}{reset}\n"
    print(formatted_results)