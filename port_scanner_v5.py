import socket
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from concurrent.futures import ThreadPoolExecutor

root = tk.Tk()
root.title("PORT SCANNER v5.1")
root.geometry("900x650")


def scan():

    target = target_entry.get().strip()

    try:
        start_port = int(start_port_entry.get())
        end_port = int(end_port_entry.get())
    except ValueError:
        messagebox.showerror(
            "Error",
            "Ports must be numbers!"
        )
        return

    results_box.delete(1.0, tk.END)

    start_time = time.time()

    open_ports = []

    def scan_port(port):

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

                    output = (
                        f"[OPEN] Port {port} "
                        f"({service})\n"
                    )

                    open_ports.append(output)

                    root.after(
                        0,
                        lambda msg=output:
                        results_box.insert(
                            tk.END,
                            msg
                        )
                    )

                    return

        except:
            pass

    with ThreadPoolExecutor(max_workers=100) as executor:

        executor.map(
            scan_port,
            range(start_port, end_port + 1)
        )

    with open(
        "scan_results.txt",
        "w",
        encoding="utf-8"
    ) as file:

        for item in open_ports:
            file.write(item)

    scan_time = (
        time.time() - start_time
    )

    root.after(
        0,
        lambda:
        results_box.insert(
            tk.END,
            "\n"
            + "=" * 40
            + f"\nScan Complete\n"
            + f"\nOpen Ports Found: {len(open_ports)}"
            + f"\nScan Time: {scan_time:.2f} seconds"
            + "\nResults saved to scan_results.txt\n"
            + "=" * 40
            + "\n"
        )
    )


def start_scan():
    threading.Thread(
        target=scan,
        daemon=True
    ).start()


title = tk.Label(
    root,
    text="PORT SCANNER v5.1",
    font=("Arial", 18, "bold")
)

title.pack(pady=10)

tk.Label(
    root,
    text="Hostname / IPv4 / IPv6"
).pack()

target_entry = tk.Entry(
    root,
    width=40
)

target_entry.pack(pady=5)

tk.Label(
    root,
    text="Start Port"
).pack()

start_port_entry = tk.Entry(
    root,
    width=20
)

start_port_entry.pack(pady=5)

tk.Label(
    root,
    text="End Port"
).pack()

end_port_entry = tk.Entry(
    root,
    width=20
)

end_port_entry.pack(pady=5)

scan_button = tk.Button(
    root,
    text="Start Scan",
    command=start_scan,
    width=20
)

scan_button.pack(pady=10)

results_box = scrolledtext.ScrolledText(
    root,
    width=100,
    height=30
)

results_box.pack(
    padx=10,
    pady=10
)

root.mainloop()