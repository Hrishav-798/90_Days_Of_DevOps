# DevOps Winter Arc — Day 05: DNS + HTTP/HTTPS + NGINX

> **90 Days of DevOps Challenge | Linux Week | Learn • Practice • Build**  
> **Topic:** Networking Basics, Web Servers & Reverse Proxy Troubleshooting

---

## 🎯 Mission
Today's mission focuses on core networking protocols and web server mechanics in a Linux environment:
1. Understand how a domain name turns into an IP address using DNS tools.
2. Inspect the HTTP request/response lifecycle and understand HTTPS/TLS encryption.
3. Install and configure Nginx as a reverse proxy in front of a backend microservice.
4. Intentionally simulate a **502 Bad Gateway** error, diagnose it using Linux tools and Nginx error logs, and resolve it systematically.
5. Bonus challenge: migrate the backend application to another port with zero client downtime.

---

## Task 1: DNS — From Hostname to IP

DNS (Domain Name System) translates human-readable hostnames into routable numerical IP addresses.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `dig google.com` | Queries DNS servers for full DNS records (header flags, question section, answers, query time, resolver IP). |
| `dig +short google.com` | Quick lookup that outputs **only** the resolved IP address(es). |
| `getent hosts google.com` | Queries the system's Name Service Switch (`/etc/nsswitch.conf` -> `/etc/hosts` + DNS) to resolve the hostname. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ dig google.com

; <<>> DiG 9.18.39-0ubuntu0.24.04.7-Ubuntu <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 28866
;; flags: qr rd ra; QUERY: 1, ANSWER: 6, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		179	IN	A	192.178.177.102
google.com.		179	IN	A	192.178.177.113
google.com.		179	IN	A	192.178.177.100
google.com.		179	IN	A	192.178.177.101
google.com.		179	IN	A	192.178.177.139
google.com.		179	IN	A	192.178.177.138

;; Query time: 0 msec
;; SERVER: 127.0.0.53#53(127.0.0.53) (UDP)
;; WHEN: Tue Oct 06 21:20:59 IST 2026
;; MSG SIZE  rcvd: 135

hrishav@hrishav-LOQ-15IAX9:~$ dig +short google.com
192.178.177.138
192.178.177.102
192.178.177.139
192.178.177.101
192.178.177.100
192.178.177.113

hrishav@hrishav-LOQ-15IAX9:~$ getent hosts google.com
2404:6800:4013:807::8b google.com
2404:6800:4013:807::71 google.com
2404:6800:4013:807::8a google.com
2404:6800:4013:807::66 google.com
```

### 📝 Notes & Key Takeaways
- **What is DNS?** The internet's phonebook. It translates human-friendly domain names (`google.com`) into machine-routable IP addresses (`192.178.177.102`).
- **What is a DNS Resolver?** A client-side or ISP-level server (such as local `systemd-resolved` on `127.0.0.53` or upstream `8.8.8.8`) that performs recursive lookups across Root, TLD, and Authoritative nameservers on behalf of the client.
- **Hostname vs IP Address:**
  - *Hostname/Domain:* Human-friendly string label (`google.com`).
  - *IP Address:* Numerical network address used by routers and sockets (IPv4 `192.178.177.102` or IPv6 `2404:6800:...`).

---

## Task 2: HTTP Request + Response

HTTP (HyperText Transfer Protocol) is the application-layer foundation of web communication.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `curl http://google.com` | Sends an HTTP GET request to port 80 and prints the response body. |
| `curl -I http://google.com` | (`--head`) Fetches and displays **only the HTTP response headers**. |
| `curl -v http://google.com` | (`--verbose`) Detailed trace showing DNS lookup, TCP connection, request headers (`>`), and response headers (`<`). |
| `curl -L http://google.com` | Follows HTTP redirects (`301/302`) specified in the `Location:` header. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ curl http://google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>

hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://google.com
HTTP/1.1 301 Moved Permanently
Location: http://www.google.com/
Content-Type: text/html; charset=UTF-8
Content-Security-Policy-Report-Only: object-src 'none';base-uri 'self';script-src 'nonce-TfL90jZOE65PyK2RPmQzZw' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp
Date: Tue, 06 Oct 2026 16:08:58 GMT
Expires: Thu, 05 Nov 2026 16:08:58 GMT
Cache-Control: public, max-age=2592000
Server: gws
Content-Length: 219
X-XSS-Protection: 0
X-Frame-Options: SAMEORIGIN

hrishav@hrishav-LOQ-15IAX9:~$ curl -v google.com
* Host google.com:80 was resolved.
* IPv6: 2404:6800:4002:828::200e
* IPv4: 192.178.177.139, 192.178.177.100, 192.178.177.113, 192.178.177.101, 192.178.177.138, 192.178.177.102
*   Trying [2404:6800:4002:828::200e]:80...
*   Trying 192.178.177.139:80...
* Connected to google.com (2404:6800:4002:828::200e) port 80
> GET / HTTP/1.1
> Host: google.com
> User-Agent: curl/8.5.0
> Accept: */*
> 
< HTTP/1.1 301 Moved Permanently
< Location: http://www.google.com/
< Content-Type: text/html; charset=UTF-8
< Content-Security-Policy-Report-Only: object-src 'none';base-uri 'self';script-src 'nonce-ffZM2_6u0ygVgRBS-p_7_g' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp
< Date: Tue, 06 Oct 2026 16:09:09 GMT
< Expires: Thu, 05 Nov 2026 16:09:09 GMT
< Cache-Control: public, max-age=2592000
< Server: gws
< Content-Length: 219
< X-XSS-Protection: 0
< X-Frame-Options: SAMEORIGIN
< 
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>
* Connection #0 to host google.com left intact
```

### 🔍 Headers Breakdown & Observations
- **Status Code `301 Moved Permanently`:** Indicates a permanent redirection. Google redirects naked domain `google.com` to `http://www.google.com/`.
- **`Location: http://www.google.com/`:** Points to the redirection destination URL. By default, `curl` does not follow redirects unless passed `-L`.
- **`Server: gws`:** Identifies Google Web Server.
- **`>` vs `<` in `curl -v`:** `>` represents request headers sent from the client; `<` represents response headers returned by the server.
- **IPv6 Connection:** Curl automatically attempted and established a connection over IPv6 (`2404:6800:4002:828::200e:80`).

### 📝 Request Lifecycle (curl to Server Response)
1. **URL Parsing:** `curl` extracts scheme (`http`), host (`google.com`), and default port `80`.
2. **DNS Resolution:** Resolves `google.com` to its IPv6/IPv4 addresses.
3. **TCP 3-Way Handshake:** Establishes connection on port 80 (`SYN` → `SYN-ACK` → `ACK`).
4. **HTTP Request:** Client transmits `GET / HTTP/1.1` along with `Host` and `User-Agent`.
5. **Server Processing:** Server parses headers and evaluates rewrite/redirect rules.
6. **HTTP Response:** Server sends status line (`301 Moved Permanently`), response headers, and HTML body.
7. **Connection Teardown:** TCP connection closes or stays alive for reuse.

---

## Task 3: HTTPS + TLS Basics

HTTPS is HTTP transported over an encrypted TLS (Transport Layer Security) session.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `curl -I https://facebook.com` | Requests headers over secure HTTPS (TLS, port 443). Displays HTTP/2 protocol and HSTS headers. |
| `curl -v https://amazon.com` | Traces the full TLS 1.3 cryptographic handshake (Client Hello, Server Hello, Cert verification, Cipher suite). |
| `openssl s_client -connect google.com:443 -servername google.com` | Directly connects via OpenSSL to inspect Google's multi-level certificate chain, issuer CAs, and cipher details. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ curl -I https://facebook.com
HTTP/2 301 
location: https://www.facebook.com/
strict-transport-security: max-age=15552000; preload
content-type: text/html; charset="utf-8"
x-fb-debug: nB2fksFsl+erzzzKXYTKvQcIb5OHpkN1q8NPEYNHr/Rr2YQPZIAzsTLVZFvmef5fZul5G61DOZ3lyJHRVH9/Ew==
content-length: 0
date: Tue, 06 Oct 2026 16:21:01 GMT
x-fb-connection-quality: MODERATE; q=0.3, rtt=250, rtx=0, c=10, mss=1288, tbw=3586, tp=-1, tpl=-1, uplat=247, ullat=0
alt-svc: h3=":443"; ma=86400

hrishav@hrishav-LOQ-15IAX9:~$ curl -v https://amazon.com
* Host amazon.com:443 was resolved.
* IPv6: 64:ff9b::6257:aa4a, 64:ff9b::6252:a1b9, 64:ff9b::6257:aa47
* IPv4: 98.87.170.74, 98.82.161.185, 98.87.170.71
*   Trying [64:ff9b::6257:aa4a]:443...
*   Trying 98.87.170.74:443...
* Connected to amazon.com (64:ff9b::6257:aa4a) port 443
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
*  CAfile: /etc/ssl/certs/ca-certificates.crt
*  CApath: /etc/ssl/certs
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / RSASSA-PSS
* ALPN: server accepted http/1.1
* Server certificate:
*  subject: CN=*.peg.a2z.com
*  start date: Sep 20 00:00:00 2026 GMT
*  expire date: Apr  5 23:59:59 2027 GMT
*  subjectAltName: host "amazon.com" matched cert's "amazon.com"
*  issuer: C=US; O=DigiCert Inc; OU=www.digicert.com; CN=GeoTrust TLS RSA CA G1
*  SSL certificate verify ok.
* using HTTP/1.x
> GET / HTTP/1.1
> Host: amazon.com
> User-Agent: curl/8.5.0
> Accept: */*
> 
< HTTP/1.1 301 Moved Permanently
< Location: https://www.amazon.com/
* Connection #0 to host amazon.com left intact

hrishav@hrishav-LOQ-15IAX9:~$ openssl s_client -connect google.com:443 -servername google.com
CONNECTED(00000003)
depth=2 C = US, O = Google Trust Services LLC, CN = GTS Root R1
verify return:1
depth=1 C = US, O = Google Trust Services, CN = WR2
verify return:1
depth=0 CN = *.google.com
verify return:1
---
Certificate chain
 0 s:CN = *.google.com
   i:C = US, O = Google Trust Services, CN = WR2
 1 s:C = US, O = Google Trust Services, CN = WR2
   i:C = US, O = Google Trust Services LLC, CN = GTS Root R1
 2 s:C = US, O = Google Trust Services LLC, CN = GTS Root R1
   i:C = BE, O = GlobalSign nv-sa, OU = Root CA, CN = GlobalSign Root CA
---
Server certificate
subject=CN = *.google.com
issuer=C = US, O = Google Trust Services, CN = WR2
---
SSL handshake has read 5129 bytes and written 392 bytes
Verification: OK
Verify return code: 0 (ok)
---
```

### 🔍 Key Observations (HTTPS & TLS)
- **HTTP/2 Protocol:** Facebook returned `HTTP/2 301` — modern HTTPS connections automatically negotiate multiplexed HTTP/2.
- **HSTS Header:** `strict-transport-security: max-age=15552000; preload` forces browsers never to connect over unencrypted HTTP for 180 days.
- **TLS 1.3 Handshake:** Amazon negotiated `TLSv1.3` using modern cipher `TLS_AES_128_GCM_SHA256` and elliptic-curve key exchange (`X25519`).
- **Certificate Chain of Trust:**
  - `depth=0 (Leaf Cert)`: `*.google.com`
  - `depth=1 (Intermediate CA)`: `WR2`
  - `depth=2 (Root CA)`: `GTS Root R1` / `GlobalSign Root CA`
  - `Verify return code: 0 (ok)`: Local system CA bundle validated all digital signatures.

### 📝 Concepts & Q&A
- **Why is HTTPS preferred over HTTP?**
  - *Encryption:* Confidentially protects passwords, tokens, and sensitive data from packet sniffers.
  - *Integrity:* Guarantees data cannot be modified or injected with malicious code in transit.
  - *Authentication:* Proves the server is genuine using trusted digital certificates.
- **What is TLS used for?** It is the cryptographic protocol that encrypts traffic between TCP (transport) and HTTP (application).
- **What is the role of a Certificate?** A digitally signed identity document binding a domain name to a public key, issued and signed by a trusted Certificate Authority (CA).
- **Why does HTTPS use port 443?** It is the standard port designated to distinguish encrypted TLS traffic from unencrypted HTTP traffic on port 80.

---

## Task 4: Install and Inspect Nginx

Nginx is an event-driven, high-performance web server and reverse proxy.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `sudo apt update && sudo apt install nginx -y` | Updates package lists and installs Nginx. |
| `sudo systemctl status nginx` | Checks if the Nginx systemd service is active and running. |
| `sudo ss -lntp \| grep nginx` | Inspects open TCP sockets in `LISTEN` state filtered by process name. |
| `curl -I http://127.0.0.1` | Sends an HTTP request to localhost port 80 to verify Nginx is answering. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo apt install nginx -y
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following NEW packages will be installed:
  nginx nginx-common
Setting up nginx-common (1.24.0-2ubuntu7.18)...
Setting up nginx (1.24.0-2ubuntu7.18)...
Processing triggers for ufw (0.36.2-6)...

hrishav@hrishav-LOQ-15IAX9:~$ sudo systemctl status nginx
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; preset: enabled)
     Active: active (running) since Tue 2026-10-06 21:56:45 IST; 1min 6s ago
   Main PID: 41433 (nginx)
      Tasks: 13 (limit: 12089)
     CGroup: /system.slice/nginx.service
             ├─41433 "nginx: master process /usr/sbin/nginx -g daemon on; master_process on;"
             ├─41436 "nginx: worker process"
             ... (12 worker processes)

hrishav@hrishav-LOQ-15IAX9:~$ ss -lntp | grep nginx
# (Empty without sudo! Explained below)

hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://127.0.0.1
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Date: Tue, 06 Oct 2026 16:28:40 GMT
Content-Type: text/html
Content-Length: 615
Connection: keep-alive
```

### 🔍 Observations & Concepts
1. **Why `ss -lntp | grep nginx` was empty without sudo:**
   - The `-p` flag displays process names and PIDs. In Linux, unprivileged users **cannot inspect processes owned by root or other users (`www-data`)**.
   - Running `sudo ss -lntp | grep nginx` or `ss -lnt | grep :80` displays `LISTEN 0.0.0.0:80`.
2. **Master & Worker Architecture:**
   - Nginx spawned 1 **master process** (`PID 41433`) and 12 **worker processes** (`PID 41436-41447`) matching available CPU cores.
3. **What a Listening Port Means:**
   - Nginx opened a TCP socket bound to `0.0.0.0:80` in the `LISTEN` state, actively waiting for incoming client connections.
4. **Verification:**
   - `curl -I http://127.0.0.1` returned `HTTP/1.1 200 OK` from `Server: nginx/1.24.0 (Ubuntu)`.

---

## Task 5: Run a Simple Application on Port 3000

Before setting up the reverse proxy, create a standalone backend application to test that it works independently.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `mkdir -p ~/day5-app && cd ~/day5-app` | Creates and navigates to the app working directory. |
| `echo 'Hello from Day 5 App' > index.html` | Creates the test webpage. |
| `python3 -m http.server 3000` | Starts a lightweight Python web server on port 3000. |
| `curl http://127.0.0.1:3000` | Tests if the application answers directly on port 3000. |
| `ss -lntp \| grep :3000` | Checks if socket 3000 is open in the `LISTEN` state. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ mkdir -p ~/day5-app
hrishav@hrishav-LOQ-15IAX9:~$ cd ~/day5-app
hrishav@hrishav-LOQ-15IAX9:~/day5-app$ echo 'Hello from Day 5 App' > index.html
hrishav@hrishav-LOQ-15IAX9:~/day5-app$ python3 -m http.server 3000
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...

# Tested from second terminal:
hrishav@hrishav-LOQ-15IAX9:~/day5-app$ curl http://127.0.0.1:3000
Hello from Day 5 App

hrishav@hrishav-LOQ-15IAX9:~/day5-app$ ss -lntp | grep :3000
LISTEN 0      5            0.0.0.0:3000       0.0.0.0:*    users:(("python3",pid=47614,fd=3))
```

### 🔍 Verification Checkpoint
- **Process Visibility:** `ss -lntp` displayed the process name and PID (`python3, pid=47614`) **without `sudo`** because the process was launched under the regular user account.
- **Direct Access Confirmed:** The app returned `Hello from Day 5 App` on `127.0.0.1:3000`, proving the backend works independently before placing Nginx in front.

---

## Task 6: Configure Nginx as a Reverse Proxy

Configure Nginx to listen on port 80 for `server_name day5.local` and proxy incoming requests to `127.0.0.1:3000`.

### ⚙️ Reverse Proxy Configuration (`/etc/nginx/sites-available/day5`)

```nginx
server {
    listen 80;
    server_name day5.local;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 🛠️ Directives & Commands Breakdown

| Directive / Command | What It Does |
| :--- | :--- |
| `proxy_pass http://127.0.0.1:3000;` | Forwards client requests to the upstream Python backend application. |
| `proxy_set_header Host $host;` | Passes the original request hostname (`day5.local`) to the backend. |
| `proxy_set_header X-Real-IP $remote_addr;` | Forwards the client's real IP address to the backend. |
| `proxy_set_header X-Forwarded-For ...` | Appends client IP to the proxy chain for traceability. |
| `sudo ln -s ... /etc/nginx/sites-enabled/` | Creates a symbolic link to activate the site configuration. |
| `sudo nginx -t` | Validates configuration files for syntax errors before reloading. |
| `sudo systemctl reload nginx` | Re-reads configuration without downtime or closing active connections. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo nano /etc/nginx/sites-available/day5
hrishav@hrishav-LOQ-15IAX9:~$ sudo ln -s /etc/nginx/sites-available/day5 /etc/nginx/sites-enabled/

hrishav@hrishav-LOQ-15IAX9:~$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

hrishav@hrishav-LOQ-15IAX9:~$ sudo systemctl reload nginx

hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://127.0.0.1
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Date: Tue, 06 Oct 2026 16:51:43 GMT
Content-Type: text/html
Content-Length: 615
Connection: keep-alive
```

### 🔍 Key Observations
- **`nginx -t` Validation:** Always test syntax before reloading in production to prevent service outages.
- **Virtual Host Routing:** When querying `curl -I http://127.0.0.1`, Nginx routed to its default server block because the `Host` header was `127.0.0.1` instead of `day5.local`. Routing to the reverse proxy requires hostname mapping via `/etc/hosts` (Task 7).

---

## Task 7: Hostname Mapping with `/etc/hosts`

Map `day5.local` to `127.0.0.1` locally to simulate DNS without configuring an external domain.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `echo "127.0.0.1 day5.local" \| sudo tee -a /etc/hosts` | Appends static mapping between `day5.local` and loopback IP `127.0.0.1`. |
| `getent hosts day5.local` | Queries the system resolver to verify `day5.local` resolves to `127.0.0.1`. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ echo "127.0.0.1 day5.local" | sudo tee -a /etc/hosts
127.0.0.1 day5.local

hrishav@hrishav-LOQ-15IAX9:~$ getent hosts day5.local
127.0.0.1       day5.local
```

### 🧠 /etc/hosts vs Public DNS
- `/etc/hosts` is a **static local file** read only by the local machine's OS resolver (`/etc/nsswitch.conf`). It does not propagate to the internet.
- **Debugging Lesson:** Querying `curl -I http://day5.local` before adding this line produced:
  `curl: (6) Could not resolve host: day5.local`  
  This demonstrates that if hostname resolution fails, the request never leaves the client, and Nginx is never reached!

---

## Task 8: Intentionally Create and Troubleshoot a 502

A **502 Bad Gateway** occurs when Nginx acting as a reverse proxy receives an invalid or nonexistent response from the upstream backend.

### 💻 Triggering the 502 Bad Gateway

```bash
# 1. Kill the Python backend application on port 3000
hrishav@hrishav-LOQ-15IAX9:~$ fuser -k 3000/tcp
3000/tcp:            47614

# 2. Request the site through Nginx reverse proxy
hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://day5.local
HTTP/1.1 502 Bad Gateway
Server: nginx/1.24.0 (Ubuntu)
Date: Tue, 06 Oct 2026 16:58:40 GMT
Content-Type: text/html
Content-Length: 166
Connection: keep-alive

hrishav@hrishav-LOQ-15IAX9:~$ curl http://day5.local
<html>
<head><title>502 Bad Gateway</title></head>
<body>
<center><h1>502 Bad Gateway</h1></center>
<hr><center>nginx/1.24.0 (Ubuntu)</center>
</body>
</html>
```

---

### 🩺 Step-by-Step Diagnostic Framework

#### 🛠️ Diagnostic Commands & What They Prove

| Diagnostic Command | What It Proves | Real Result |
| :--- | :--- | :--- |
| `ss -lntp \| grep :3000` | Checks if upstream port 3000 is listening. | **Empty!** Backend process is down. |
| `sudo nginx -t` | Checks if Nginx configuration has syntax errors. | **Syntax ok, test successful.** Nginx config is fine. |
| `sudo tail -n 30 /var/log/nginx/error.log` | Reveals why Nginx returned 502. | **`connect() failed (111: Connection refused)`** on `127.0.0.1:3000`. |

#### 💻 Diagnostic Logs & Evidence

```bash
# 1. Port check (Empty output proves backend is dead)
hrishav@hrishav-LOQ-15IAX9:~$ ss -lntp | grep :3000

# 2. Proxy config test (Proves Nginx is not broken)
hrishav@hrishav-LOQ-15IAX9:~$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

# 3. Nginx error log (The smoking gun: Connection Refused on upstream socket!)
hrishav@hrishav-LOQ-15IAX9:~$ sudo tail -n 30 /var/log/nginx/error.log
2026/10/06 22:27:43 [error] 53119#53119: *3 connect() failed (111: Connection refused) while connecting to upstream, client: 127.0.0.1, server: day5.local, request: "HEAD / HTTP/1.1", upstream: "http://127.0.0.1:3000/", host: "day5.local"
2026/10/06 22:28:40 [error] 53120#53120: *5 connect() failed (111: Connection refused) while connecting to upstream, client: 127.0.0.1, server: day5.local, request: "HEAD / HTTP/1.1", upstream: "http://127.0.0.1:3000/", host: "day5.local"
2026/10/06 22:28:40 [error] 53121#53121: *7 connect() failed (111: Connection refused) while connecting to upstream, client: 127.0.0.1, server: day5.local, request: "GET / HTTP/1.1", upstream: "http://127.0.0.1:3000/", host: "day5.local"
```

---

### 🛠️ Root Cause, Fix & Verification

```bash
# 1. Restart the Python backend app in the background
hrishav@hrishav-LOQ-15IAX9:~$ cd ~/day5-app
hrishav@hrishav-LOQ-15IAX9:~/day5-app$ python3 -m http.server 3000 &
[1] 61354
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...

# 2. Confirm socket 3000 is listening again
hrishav@hrishav-LOQ-15IAX9:~/day5-app$ ss -lntp | grep :3000
LISTEN 0      5            0.0.0.0:3000       0.0.0.0:*    users:(("python3",pid=61354,fd=3))

# 3. Test through Nginx reverse proxy
hrishav@hrishav-LOQ-15IAX9:~/day5-app$ curl -I http://day5.local
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Date: Tue, 06 Oct 2026 17:03:07 GMT
Content-Type: text/html
Content-Length: 21
Connection: keep-alive

hrishav@hrishav-LOQ-15IAX9:~/day5-app$ curl http://day5.local
Hello from Day 5 App
```

### 📋 Post-Mortem Table

| Stage | Detail |
| :--- | :--- |
| **Problem** | Client received `HTTP 502 Bad Gateway` when requesting `http://day5.local`. |
| **Evidence** | `ss -lntp` showed port 3000 closed; Nginx error logs reported `connect() failed (111: Connection refused) while connecting to upstream http://127.0.0.1:3000/`. |
| **Root Cause** | The upstream backend process was stopped, so Nginx could not establish a TCP handshake on port 3000. |
| **Fix** | Restarted the Python application on port 3000 (`PID 61354`). |
| **Verification** | `curl -I http://day5.local` returned `HTTP/1.1 200 OK` and payload `Hello from Day 5 App`. |

---

## Task 9: Complete Request Flow

### 🗺️ Request Flow Architecture

```
[Client: curl / Browser]
          │
          │ 1. Lookup "day5.local"
          ▼
   [/etc/hosts] ───────► Resolves to 127.0.0.1
          │
          │ 2. TCP SYN: 127.0.0.1:80
          ▼
  [Nginx (Reverse Proxy)]
   - Matches: server_name day5.local
   - Rule: location /
   - Action: proxy_pass http://127.0.0.1:3000
          │
          │ 3. Internal TCP SYN: 127.0.0.1:3000
          ▼
[Python HTTP Server (Upstream App)]
   - Reads: index.html
   - Returns: 200 OK ("Hello from Day 5 App")
          │
          │ 4. Upstream response passed to Nginx
          ▼
  [Nginx (Reverse Proxy)]
   - Attaches proxy response headers
          │
          │ 5. Final HTTP 200 OK response sent
          ▼
       [Client]
```

### 🌐 What Changes If the App Were on Another Server?
1. **Network Layer:** Instead of connecting to loopback (`127.0.0.1`), Nginx connects over private LAN/VPC IP (e.g., `10.0.1.50:3000`).
2. **Security & Firewalls:** Security groups or firewall rules (`ufw`, AWS Security Groups) must allow ingress on port 3000 only from the Nginx proxy's IP.
3. **Nginx Config:** `proxy_pass http://127.0.0.1:3000;` changes to `proxy_pass http://10.0.1.50:3000;`.
4. **Latency & Timeouts:** Introduces network transit latency and potential network timeouts (`504 Gateway Timeout`) if the network fails.

---

## 🌟 Bonus Challenge: Migrating Backend Port to 4000

Migrated the backend application to port 4000 with zero client downtime.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `fuser -k 3000/tcp` | Stops the previous Python application on port 3000. |
| `python3 -m http.server 4000 &` | Starts a new backend service listening on port 4000 in background. |
| `sudo sed -i 's/127.0.0.1:3000/127.0.0.1:4000/' ...` | Uses `sed` to update the upstream port in `/etc/nginx/sites-available/day5`. |
| `sudo nginx -t && sudo systemctl reload nginx` | Tests syntax and gracefully reloads Nginx configuration. |
| `curl -I http://day5.local && curl http://day5.local` | Proves the application is still reachable on `day5.local`. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day5-app$ fuser -k 3000/tcp 2>/dev/null || true
 61354

hrishav@hrishav-LOQ-15IAX9:~/day5-app$ cd ~/day5-app
hrishav@hrishav-LOQ-15IAX9:~/day5-app$ python3 -m http.server 4000 &
[1] 68476
Serving HTTP on 0.0.0.0 port 4000 (http://0.0.0.0:4000/) ...

hrishav@hrishav-LOQ-15IAX9:~/day5-app$ sudo sed -i 's/127.0.0.1:3000/127.0.0.1:4000/' /etc/nginx/sites-available/day5

hrishav@hrishav-LOQ-15IAX9:~/day5-app$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

hrishav@hrishav-LOQ-15IAX9:~/day5-app$ sudo systemctl reload nginx

hrishav@hrishav-LOQ-15IAX9:~/day5-app$ curl -I http://day5.local
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Date: Tue, 06 Oct 2026 17:10:14 GMT
Content-Type: text/html
Content-Length: 21
Connection: keep-alive
Last-Modified: Tue, 06 Oct 2026 16:35:43 GMT

hrishav@hrishav-LOQ-15IAX9:~/day5-app$ curl http://day5.local
Hello from Day 5 App
```

### ✅ Verification
Nginx cleanly re-routed traffic to port 4000 with zero client disruption! Clients continued accessing `http://day5.local` without needing any knowledge of backend port changes.

---

## 🧠 What You Should Be Able to Explain (Interview & Concept Recap)

1. **What DNS does & why domain names resolve to IP addresses:**
   - DNS maps human-readable names (`google.com`) to routable numerical IP addresses (`192.178.177.102`), because routers and the TCP/IP stack communicate via IP addresses, not strings.

2. **What an HTTP request and HTTP response contain:**
   - **Request:** Method (`GET`, `POST`), URI (`/`), protocol version (`HTTP/1.1`), headers (`Host`, `User-Agent`), and optional body.
   - **Response:** Status line (`HTTP/1.1 200 OK`), response headers (`Content-Type`, `Server`, `Location`), and payload body.

3. **Common HTTP Status Codes:**
   - `200 OK`: Request succeeded.
   - `301/302 Redirect`: Resource moved permanently / temporarily.
   - `400 Bad Request`: Malformed client syntax.
   - `403 Forbidden`: Authenticated but unauthorized.
   - `404 Not Found`: Target resource does not exist.
   - `500 Internal Server Error`: Backend application crashed.
   - `502 Bad Gateway`: Reverse proxy failed to connect to upstream service.

4. **Difference between HTTP and HTTPS & Purpose of TLS:**
   - HTTP sends data in plaintext (vulnerable to packet sniffing).
   - HTTPS wraps HTTP inside TLS to provide **confidentiality** (encryption), **integrity** (tamper detection), and **authentication** (digital certificates).

5. **Why HTTP uses Port 80 and HTTPS uses Port 443:**
   - Standard IANA port conventions allowing firewalls and web software to separate plaintext traffic (80) from encrypted TLS traffic (443).

6. **What Nginx is & why it is used as a Reverse Proxy:**
   - Nginx is an asynchronous event-driven server. Acting as a reverse proxy, it sits in front of backend applications to handle SSL termination, rate limiting, static asset caching, and request routing.

7. **What an Upstream Application means:**
   - The backend service (e.g., Python app on `127.0.0.1:3000` or `4000`) that sits behind the reverse proxy and processes business logic.

8. **How `/etc/hosts` differs from DNS:**
   - `/etc/hosts` is a local static file consulted only by the local OS resolver (`/etc/nsswitch.conf`).
   - DNS is a globally distributed, hierarchical public directory queried over the network.

9. **Why a 502 Bad Gateway happens when upstream is down:**
   - Nginx receives the client request, attempts a TCP handshake with `proxy_pass http://127.0.0.1:3000`, receives `Connection refused` (error 111) because no process is listening, and returns `502 Bad Gateway` to the client.

10. **Troubleshooting Hierarchy:**
    $$\text{DNS/Hostname} \longrightarrow \text{Port Listening} \longrightarrow \text{Service Status} \longrightarrow \text{Proxy Config} \longrightarrow \text{Logs} \longrightarrow \text{Response}$$
    - `dig` / `getent` → `ss -lntp` → `systemctl status` → `nginx -t` → `tail -f /var/log/nginx/error.log` → `curl -I`.

---

[← Day 04](Day04.md) | [Home](README.md) | [Day 06 →](Day06.md)
