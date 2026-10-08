# DevOps Winter Arc — Day 04: Networking + SSH Practical Assignment

> **90 Days of DevOps Challenge | Linux Week | Learn • Practice • Build**  
> **Topic: Network Interfaces, Ports, Connectivity Testing, SSH Key Auth, Local DNS & Reachability Troubleshooting**

---

## 🎯 Mission

Day 04 of my DevOps Winter Arc challenge!

Today’s mission moved beyond files, directories, and local shell scripting into **Linux networking and secure remote access**. In modern DevOps, applications rarely run in isolation—they communicate over internal subnets, bind to network sockets, sit behind reverse proxies, and are managed remotely via SSH.

### The Objectives:
1. **Identify Network Identity:** Inspect local network interfaces, discover private IP addresses, and identify the default gateway.
2. **Understand & Inspect Ports:** List active TCP/UDP listening sockets, analyze what services are attached, and master the concept of network ports.
3. **Test Network Connectivity:** Perform HTTP requests via `curl`, inspect response headers, and dissect the client-to-server lifecycle.
4. **SSH Key-Based Authentication:** Generate modern Ed25519 key pairs, understand the public/private key trust model, and verify secure authentication.
5. **Local DNS Mapping via `/etc/hosts`:** Override DNS locally by mapping custom domain names directly to loopback IP addresses.
6. **Troubleshoot a Reachability Problem:** Methodically diagnose an unreachable network service using the **Problem ➔ Evidence ➔ Root Cause ➔ Fix** framework.
7. **Bonus Challenge:** Construct a standardized, 6-step network troubleshooting checklist.

---

## Task 1: Identify Your Network

Before deploying services or diagnosing connectivity, an engineer must know the machine’s network identity: which interfaces exist, what IP is assigned, and where traffic exits the network.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `ip addr` | Displays all network interfaces (loopback, Ethernet, Wi-Fi, Docker bridges) and their assigned IPv4/IPv6 addresses and subnet masks. |
| `ip route` | Displays the kernel routing table, specifically identifying the default gateway used to route packets outside the local subnet. |
| `ip -brief addr` | Quick condensed overview showing interface names, operational state (`UP`/`DOWN`), and assigned IP addresses. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ ip route
default via 10.53.224.21 dev wlp8s0 proto dhcp src 10.53.224.181 metric 600 
10.53.224.0/24 dev wlp8s0 proto kernel scope link src 10.53.224.181 metric 600 
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown 

hrishav@hrishav-LOQ-15IAX9:~$ ip addr show wlp8s0
3: wlp8s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether c0:35:32:23:84:e7 brd ff:ff:ff:ff:ff:ff
    inet 10.53.224.181/24 brd 10.53.224.255 scope global dynamic noprefixroute wlp8s0
       valid_lft 3439sec preferred_lft 3439sec
    inet6 fe80::3bbb:30cd:39be:60a2/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
```

### 🔍 What I Observed on My System
- **Active Interface:** `wlp8s0` (PCIe Wi-Fi interface) is in the `UP` state with MTU 1500.
- **Private IP Address:** `10.53.224.181/24` (a Class A private address within a `/24` subnet, meaning valid local host IPs range from `10.53.224.1` to `10.53.224.254`).
- **Default Gateway:** `10.53.224.21`. Any traffic destined for public internet IPs (like `8.8.8.8` or `1.1.1.1`) is forwarded to this router IP via `wlp8s0`.
- **Virtual Interfaces:** `docker0` (`172.17.0.1/16`) exists as a bridge network for containerized workloads.

---

## Task 2: Understand & Check Ports

An IP address locates a physical or virtual machine on a network; a **Port** identifies a specific process or service listening for connections on that machine.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `ss -tuln` | Lists listening (**l**) sockets for **T**CP (`-t`) and **U**DP (`-u`), with numeric (**-n**) ports instead of protocol names. |
| `ss -lntp` | Shows listening TCP sockets along with the specific **P**rocess ID (`PID`) and program name holding the socket open (requires `sudo` for system daemons). |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ ss -tuln
Netid  State   Recv-Q  Send-Q   Local Address:Port    Peer Address:Port Process 
udp    UNCONN  0       0           127.0.0.53%lo:53           0.0.0.0:*            
tcp    LISTEN  0       511            0.0.0.0:80            0.0.0.0:*            
tcp    LISTEN  0       4096         127.0.0.1:3306          0.0.0.0:*            
tcp    LISTEN  0       4096         127.0.0.1:27017         0.0.0.0:*            
tcp    LISTEN  0       511               [::]:80               [::]:*            
```

### 🔍 Identified Listening Ports & Explanation:
1. **Port 80 (`0.0.0.0:80`):**
   - **Service:** Nginx HTTP Web Server.
   - **Bind Address:** `0.0.0.0` means the server listens on **all** available IPv4 network interfaces (both localhost `127.0.0.1` and local Wi-Fi `10.53.224.181`).
2. **Port 3306 (`127.0.0.1:3306`):**
   - **Service:** MySQL Relational Database.
   - **Bind Address:** `127.0.0.1` (loopback only). This is a crucial security practice: the database only accepts connections from the local host and is shielded from external network exposure.
3. **Port 53 (`127.0.0.53:53`):**
   - **Service:** `systemd-resolved` local DNS stub resolver.

### 💡 Core Concept: IP Address vs. Port
> **The Apartment Metaphor:**  
> - **IP Address:** The building's street address (tells network packets which machine to reach).  
> - **Port Number:** The apartment room number (tells the operating system kernel which application process should receive the data).

---

## Task 3: Test Network Connectivity

`curl` (Client URL) is the Swiss Army knife for testing web services, API endpoints, and raw HTTP response headers directly from the terminal.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `curl http://example.com` | Sends an HTTP `GET` request to the target URL and prints the raw HTML response body to standard output. |
| `curl -I https://example.com` | Sends an HTTP `HEAD` request (or displays headers only) showing status code, content type, server software, and cache directives without body content. |
| `curl -v http://example.com` | Verbose mode: reveals DNS resolution, IP connection, TLS handshake details, request headers, and response headers. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ curl -I https://example.com
HTTP/2 200 
content-encoding: gzip
accept-ranges: bytes
age: 468494
cache-control: max-age=604800
content-type: text/html
date: Thu, 08 Oct 2026 17:10:15 GMT
etag: "3147526947"
expires: Thu, 15 Oct 2026 17:10:15 GMT
last-modified: Thu, 17 Oct 2019 07:18:26 GMT
server: ECAcc (iad/0142)
x-cache: HIT
content-length: 648
```

### 🔍 What Happens Between Terminal and Server?
1. **DNS Lookup:** The system resolves `example.com` to an IP address (e.g., `93.184.215.14`) using `/etc/resolv.conf` and `systemd-resolved`.
2. **TCP 3-Way Handshake:** The kernel initiates a TCP connection to `93.184.215.14:443` (`SYN` ➔ `SYN-ACK` ➔ `ACK`).
3. **TLS Negotiation:** Since HTTPS was queried, client and server negotiate cryptographic ciphers and verify the server's SSL certificate.
4. **HTTP Request:** `curl` transmits the HTTP request: `HEAD / HTTP/2`, specifying headers like `User-Agent` and `Host`.
5. **HTTP Response:** The web server processes the request and returns status `HTTP/2 200 OK` alongside headers.

---

## Task 4: SSH Key-Based Access

Password authentication is slow, vulnerable to brute-force attacks, and unsuited for CI/CD automation. DevOps relies on **Asymmetric Public-Key Cryptography**.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `ssh-keygen -t ed25519 -C "hrishav@devops-lab"` | Generates an elliptic curve Ed25519 key pair (vastly more secure and faster than legacy RSA). |
| `cat ~/.ssh/id_ed25519.pub` | Displays the **Public Key** intended for distribution to remote servers. |
| `chmod 600 ~/.ssh/id_ed25519` | Ensures strict file permissions: only the owner can read/write the private key (SSH aborts if permissions are too loose). |
| `ssh -i ~/.ssh/id_ed25519 user@server-ip` | Initiates an SSH session using the specified identity key. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ ssh-keygen -t ed25519 -C "hrishav-devops"
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/hrishav/.ssh/id_ed25519): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/hrishav/.ssh/id_ed25519
Your public key has been saved in /home/hrishav/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:H1Z9q7V4eK8uX1xRkLwOp0mNpQtR8wVuY1bNqPxKm4s hrishav-devops
The key's randomart image is:
+--[ED25519 256]--+
|      .o.        |
|     .. =        |
|    .  + * .     |
|   .    B * .    |
|  . .  + S o     |
|   o +  * O .    |
|    = o. B =     |
|   . =..+ =      |
|    E.=+oo       |
+----[SHA256]-----+

hrishav@hrishav-LOQ-15IAX9:~$ ls -la ~/.ssh/
total 24
drwx------  2 hrishav hrishav 4096 Oct  8 22:40 .
drwxr-x--- 67 hrishav hrishav 4096 Oct  8 22:38 ..
-rw-------  1 hrishav hrishav  464 Oct  8 22:40 id_ed25519
-rw-r--r--  1 hrishav hrishav  102 Oct  8 22:40 id_ed25519.pub
-rw-------  1 hrishav hrishav 1956 Oct  8 22:30 known_hosts

hrishav@hrishav-LOQ-15IAX9:~$ cat ~/.ssh/id_ed25519.pub
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExamplePublicKeyStringHrishavLOQ15IAX9== hrishav-devops
```

### 🔒 Public Key vs. Private Key Security Model:
- **`id_ed25519` (Private Key):** Stored strictly on the local client. **Must NEVER be shared, committed to Git, or exposed.** It proves identity by decrypting cryptographic challenges.
- **`id_ed25519.pub` (Public Key):** The lock installed on remote servers in `~/.ssh/authorized_keys`. It can be shared publicly without compromising security.

---

## Task 5: Hostname Resolution with `/etc/hosts`

Before public DNS servers existed, `/etc/hosts` was the original internet host directory. Today, it remains the first place a Linux OS looks to map names to IP addresses locally.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `cat /etc/hosts` | Inspects current static hostname mappings. |
| `echo "127.0.0.1 day4.local" \| sudo tee -a /etc/hosts` | Safely appends a local hostname mapping for `day4.local` pointing to loopback `127.0.0.1`. |
| `getent hosts day4.local` | Queries the system Name Service Switch (`nsswitch.conf`) to verify resolution. |
| `curl -I http://day4.local` | Tests HTTP connectivity using the newly mapped local domain. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ cat /etc/hosts
127.0.0.1 localhost
127.0.1.1 hrishav-LOQ-15IAX9
::1       ip6-localhost ip6-loopback

hrishav@hrishav-LOQ-15IAX9:~$ echo "127.0.0.1 day4.local" | sudo tee -a /etc/hosts
127.0.0.1 day4.local

hrishav@hrishav-LOQ-15IAX9:~$ getent hosts day4.local
127.0.0.1       day4.local

hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://day4.local
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Date: Thu, 08 Oct 2026 17:15:22 GMT
Content-Type: text/html
Content-Length: 612
```

### 🔍 What I Observed on My System
- The OS resolver checks `/etc/hosts` **before** consulting upstream DNS servers (`/etc/nsswitch.conf` defines: `hosts: files mdns4_minimal [NOTFOUND=return] dns`).
- By mapping `day4.local` to `127.0.0.1`, `curl` instantly resolved the domain locally and reached my local Nginx server on port 80 without any external network traffic.

---

## Task 6: Troubleshoot a Reachability Problem

In DevOps, when a service is unreachable, jumping straight to `sudo reboot` or blindly restarting services is poor practice. An engineer gathers evidence first.

### Scenario:
A developer reports: *"Our backend service running on port 8080 is down! curl returns an error!"*

---

### Step 1: Confirm the Symptom
```bash
hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://127.0.0.1:8080
curl: (7) Failed to connect to 127.0.0.1 port 8080: Connection refused
```

### Step 2: Collect Evidence (Is Port 8080 Listening?)
```bash
hrishav@hrishav-LOQ-15IAX9:~$ ss -lntp | grep 8080
# Output: (Empty - nothing is listening on TCP port 8080)
```
- **Evidence:** The operating system kernel returned `Connection refused` (TCP RST packet) because no active process has opened a listening socket on port 8080.

### Step 3: Check Running Services & System Processes
```bash
hrishav@hrishav-LOQ-15IAX9:~$ ps aux | grep -E "python|node|app"
# Output shows a backend script was launched with PORT=3000 instead of 8080!
hrishav    14820  0.0  0.1  24500 12300 pts/1    S+   22:30   0:00 node server.js --port 3000

hrishav@hrishav-LOQ-15IAX9:~$ ss -lntp | grep 3000
LISTEN 0      511        127.0.0.1:3000       0.0.0.0:*    users:(("node",pid=14820,fd=19))
```

### Step 4: Root Cause Identification
- The backend application is running normally, but it was bound to **Port 3000**, while clients and configuration scripts were attempting to reach **Port 8080**.

### Step 5: Implement Fix & Verification
```bash
# Test reachability on actual active port:
hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://127.0.0.1:3000
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: text/plain; charset=utf-8
Content-Length: 15
Date: Thu, 08 Oct 2026 17:18:40 GMT

# Alternatively, reconfigure application environment to listen on 8080:
# export PORT=8080 && node server.js
```

### 📋 Post-Incident Summary:
| Stage | Investigation Finding |
| :--- | :--- |
| **Problem** | `curl: (7) Failed to connect to 127.0.0.1 port 8080: Connection refused`. |
| **Evidence** | `ss -lntp` confirmed nothing listening on port 8080. `ps aux` showed node process listening on 3000. |
| **Root Cause** | Port mismatch between client request and application bind configuration. |
| **Fix** | Route request to correct active port (or update app configuration port). |

---

## 🧠 Core Networking Concepts Explained

| Concept | Explanation |
| :--- | :--- |
| **IP Address vs. Port** | IP routes data to the correct host machine; Port directs data to the specific software process inside that host. |
| **Private IP vs. Public IP** | Private IPs (RFC 1918: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) are non-routable on the public internet. Public IPs are globally unique and routable across internet backbones. |
| **TCP vs. UDP** | **TCP** is connection-oriented, guarantees ordered packet delivery, and handles retransmissions (HTTP, SSH, DBs). **UDP** is connectionless, fast, and does not retry lost packets (DNS queries, live video streaming). |
| **Listening Port** | A network socket bound by a running application in state `LISTEN`, waiting to accept incoming connection handshakes. |
| **SSH Key Architecture** | Uses asymmetric cryptography: the **public key** is shared to the server (`authorized_keys`), while the **private key** never leaves the client. Authentication occurs via signed cryptographic challenges. |
| **`/etc/hosts` Mechanism** | Local static lookup table that overrides DNS queries by mapping hostnames directly to IP addresses. |

---

## ⚡ Bonus Challenge: The Standardized Network Troubleshooting Flow

When a network service fails in production, following a disciplined, bottom-up order isolates root causes in minutes:

```
  ┌─────────────────────────────────────────────────────────────┐
  │         1. IP & Interface (Is the network link UP?)         │
  │                  ip addr show / ip link                     │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │       2. Routing & Gateway (Can traffic leave the host?)    │
  │                  ip route / ping <gateway>                  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │        3. Port Listening (Is a process bound to socket?)    │
  │                     ss -lntp | grep <port>                  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │    4. Service Health (Is the application process running?)  │
  │          systemctl status <service> / journalctl -u         │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │     5. Local Loopback Test (Does it respond internally?)    │
  │                curl -I http://127.0.0.1:<port>              │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │   6. Firewall & Network Path (Are ports filtered remotely?) │
  │                 ufw status / iptables -L / nc -zv           │
  └─────────────────────────────────────────────────────────────┘
```

### Why This Order Matters:
- Checking the firewall before confirming whether the service is even listening wastes time on security rules when the software isn't running.
- Checking external connectivity before verifying IP configuration leads to false assumptions about internet outages when the local interface is simply down.
- **Always verify the local socket first, then verify the local process, then verify the network path.**

---

## 📝 Key Takeaways & Reflection

1. **`ss` is faster and more accurate than `netstat`:** `ss` directly queries Linux kernel netlink sockets.
2. **Ed25519 is the modern standard:** Generate `ssh-keygen -t ed25519` for smaller key footprints and stronger cryptographic guarantees.
3. **`Connection refused` vs. `Timeout`:**
   - `Connection refused`: The target host was reached, but no process was listening on the requested port (kernel sent TCP RST).
   - `Timeout`: Packets were dropped silently along the way (usually a firewall or routing failure).
4. **Evidence-Based Debugging:** Check interfaces, ports, and logs before changing code or rebooting servers.

---

[← Day 03](Day03.md) | [Home](README.md) | [Day 05 →](Day05.md)
