import socket
import time
import csv
from colorama import init, Fore
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# Initialize Colorama
init(autoreset=True)

lock = Lock()

print("=" * 50)
print("Port Scanner v4.1")
print("=" * 50)

target = input("Enter Hostname, IPv4, or IPv6 Address: ").strip()
start_port = int(input("Enter Start Port: "))
end_port = int(input("Enter End Port: "))

start_time = time.time()

results = []
open_ports = 0
closed_ports = 0


def grab_banner(target, port):
    try:
        addr_info = socket.getaddrinfo(
            target,
            port,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM
        )

        family, socktype, proto, canonname, sockaddr = addr_info[0]

        sock = socket.socket(family, socktype, proto)
        sock.settimeout(1)

        sock.connect(sockaddr)

        try:
            banner = sock.recv(1024).decode(
                errors="ignore"
            ).strip()

            if not banner:
                banner = "No Banner"

        except:
            banner = "No Banner"

        sock.close()

        return banner

    except:
        return "No Banner"


def scan_port(port):
    global open_ports, closed_ports

    try:
        addr_info = socket.getaddrinfo(
            target,
            port,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM
        )

        for info in addr_info:

            family, socktype, proto, canonname, sockaddr = info

            sock = socket.socket(
                family,
                socktype,
                proto
            )

            sock.settimeout(0.1)

            result = sock.connect_ex(sockaddr)

            sock.close()

            if result == 0:

                try:
                    service = socket.getservbyport(port)
                except:
                    service = "Unknown"

                banner = grab_banner(target, port)

                output = [
                    port,
                    service,
                    banner
                ]

                with lock:
                    open_ports += 1
                    results.append(output)

                print(
                    Fore.GREEN +
                    f"[OPEN] Port {port} "
                    f"({service}) | "
                    f"Banner: {banner}"
                )

                return

        with lock:
            closed_ports += 1

        print(
            Fore.RED +
            f"[CLOSED] Port {port}"
        )

    except:
        with lock:
            closed_ports += 1


print("\n" + "=" * 40)
print(f"Scanning {target}")
print("=" * 40 + "\n")

with ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(
        scan_port,
        range(start_port, end_port + 1)
    )

# TXT Export
with open(
    "scan_results.txt",
    "w",
    encoding="utf-8"
) as file:

    for result in results:
        file.write(
            f"Port {result[0]} "
            f"({result[1]}) | "
            f"Banner: {result[2]}\n"
        )

# CSV Export
with open(
    "scan_results.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Port",
        "Service",
        "Banner"
    ])

    writer.writerows(results)

end_time = time.time()

print("\n" + "=" * 40)
print("Scan Complete")
print("=" * 40)
print(f"Open Ports   : {open_ports}")
print(f"Closed Ports : {closed_ports}")
print(
    f"Scan Time    : "
    f"{end_time - start_time:.2f} seconds"
)
print("TXT Report   : scan_results.txt")
print("CSV Report   : scan_results.csv")
print("=" * 40)