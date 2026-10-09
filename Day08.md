# DevOps Winter Arc — Day 08: Docker Fundamentals

> **90 Days of DevOps Challenge | Containers Week | Learn • Practice • Build**  
> **Topic: Docker Architecture, Images vs Containers, Port Mapping & Dockerfile**

---

## 🎯 Today's Goal

Day 8 of the DevOps Winter Arc!

Today is all about revisiting and solidifying **Docker fundamentals**. While I've worked with Docker before on apps and services, today's focus is to step back, test the fundamentals step by step, make sure the core concepts are clear, build a custom image from a Dockerfile, and practice port mapping and container troubleshooting.

### The Plan for Today:
1. Confirm Docker Engine and CLI setup.
2. Run the `hello-world` container to review how Docker pulls images and runs processes.
3. Check the difference between `docker ps` and `docker ps -a`.
4. Run Nginx in the background (`-d`) and map host port to container port (`-p 8080:80`).
5. Inspect container logs (`docker logs`) and inspect low-level config (`docker inspect`).
6. Set up a simple web app directory (`~/day8-docker-app`) with an `index.html`.
7. Write a clean `Dockerfile` using `FROM`, `COPY`, and `EXPOSE`, and build `day8-web:1.0`.
8. Run the custom container on port `8081` and verify with `curl` and the browser.
9. Troubleshoot a port conflict scenario when a host port is already occupied.
10. Check resource usage with `docker stats` and clean up test containers safely.
11. Document a troubleshooting note using the **Problem → Evidence → Root Cause → Fix → Verification** format.

---

## 🗺️ Core Concepts & Architecture

### 1. Docker Architecture: Client, Daemon, and Containers
Docker uses a client-server model. When I type a command in the terminal (`docker run`), the Docker CLI talks to the Docker Daemon (`dockerd`) through a local Unix socket (`/var/run/docker.sock`). The daemon handles pulling images, creating namespaces, and managing container lifecycles.

```
  +------------------+         Unix Socket / REST API         +---------------------+
  |    Docker CLI    | -------------------------------------> |    Docker Daemon    |
  |  (Terminal user) | <------------------------------------- |      (dockerd)      |
  +------------------+                                        +----------+----------+
                                                                         |
                                                                         v
                                                              +---------------------+
                                                              | containerd & runc   |
                                                              +----------+----------+
                                                                         |
                                              +--------------------------+--------------------------+
                                              |                                                     |
                                              v                                                     v
                                     +------------------+                                  +------------------+
                                     |  Container (App) |                                  |  Container (Web) |
                                     |  - PID Namespace |                                  |  - PID Namespace |
                                     |  - Net Namespace |                                  |  - Net Namespace |
                                     |  - cgroups limit |                                  |  - cgroups limit |
                                     +------------------+                                  +------------------+
```

---

### 2. Image vs. Container
- **Image:** A read-only template with the application code, libraries, and runtime. Images are built in layers and stored locally or pulled from a registry like Docker Hub.
- **Container:** A running instance of an image. Docker adds a thin read-write layer on top of the image's read-only layers. Any new files or changes happen in this writable layer and disappear when the container is deleted unless saved to a volume.

```
+-----------------------------------------------------------------+
| Writable Container Layer  (Temporary changes made while running)|
+-----------------------------------------------------------------+
| Read-Only Layer: COPY index.html                                |
+-----------------------------------------------------------------+
| Read-Only Layer: Nginx configuration                            |
+-----------------------------------------------------------------+
| Read-Only Base Layer: Alpine Linux rootfs                       |
+-----------------------------------------------------------------+
```

---

### 3. How Port Mapping Works (`-p Host:Container`)
By default, a container gets its own private IP address on an internal bridge network (`docker0`). The host machine and outside network cannot reach the container directly unless we publish the port.

When running `-p 8080:80`:
- **`8080` (Host Port):** The port opened on my actual computer.
- **`80` (Container Port):** The port the web server inside the container is listening on.
- Traffic hitting `http://localhost:8080` gets forwarded through `docker-proxy` and Linux iptables rules into the container's port `80`.

```
 Browser / curl (Host)
          |
          v
   localhost:8080 (Host Port)
          |
          | (Forwarded via docker-proxy / iptables)
          v
   Container:80   (Internal Nginx web server)
```

---

## Task 1: Check Docker

Confirm that Docker is installed, the daemon is running, and the CLI can communicate with it.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker --version` | Shows the installed Docker CLI version. |
| `docker info` | Queries the Docker daemon and outputs system details (active containers, storage driver, memory, OS, runtimes). |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ docker --version
Docker version 29.4.3, build 055a478

hrishav@hrishav-LOQ-15IAX9:~$ docker info
Client: Docker Engine - Community
 Version:    29.4.3
 Context:    default
 Debug Mode: false
 Plugins:
  agent: Docker AI Agent Runner (Docker Inc.)
    Version:  v1.54.0
    Path:     /home/hrishav/.docker/cli-plugins/docker-agent
  ai: Docker AI Agent - Ask Gordon (Docker Inc.)
    Version:  v1.20.2
    Path:     /home/hrishav/.docker/cli-plugins/docker-ai
  buildx: Docker Buildx (Docker Inc.)
    Version:  v0.33.0-desktop.1
    Path:     /home/hrishav/.docker/cli-plugins/docker-buildx
  compose: Docker Compose (Docker Inc.)
    Version:  v5.1.3
    Path:     /home/hrishav/.docker/cli-plugins/docker-compose
  debug: Get a shell into any image or container (Docker Inc.)
    Version:  0.0.47
    Path:     /home/hrishav/.docker/cli-plugins/docker-debug
  desktop: Docker Desktop commands (Docker Inc.)
    Version:  v0.3.0
    Path:     /home/hrishav/.docker/cli-plugins/docker-desktop
  dhi: CLI for managing Docker Hardened Images (Docker Inc.)
    Version:  v0.0.3
    Path:     /home/hrishav/.docker/cli-plugins/docker-dhi
  extension: Manages Docker extensions (Docker Inc.)
    Version:  v0.2.31
    Path:     /home/hrishav/.docker/cli-plugins/docker-extension
  init: Creates Docker-related starter files for your project (Docker Inc.)
    Version:  v1.4.0
    Path:     /home/hrishav/.docker/cli-plugins/docker-init
  mcp: Docker MCP Plugin (Docker Inc.)
    Version:  v0.42.0
    Path:     /home/hrishav/.docker/cli-plugins/docker-mcp
  offload: Docker Offload (Docker Inc.)
    Version:  v0.5.85
    Path:     /home/hrishav/.docker/cli-plugins/docker-offload
  pass: Docker Pass Secrets Manager Plugin (beta) (Docker Inc.)
    Version:  v0.0.25
    Path:     /home/hrishav/.docker/cli-plugins/docker-pass
  sandbox:  (Docker Inc.)
    Version:  v0.12.0
    Path:     /home/hrishav/.docker/cli-plugins/docker-sandbox
  sbom: View the packaged-based Software Bill Of Materials (SBOM) for an image (Anchore Inc.)
    Version:  0.6.0
    Path:     /home/hrishav/.docker/cli-plugins/docker-sbom
  scout: Docker Scout (Docker Inc.)
    Version:  v1.20.4
    Path:     /home/hrishav/.docker/cli-plugins/docker-scout

Server:
 Containers: 11
  Running: 2
  Paused: 0
  Stopped: 9
 Images: 27
 Server Version: 29.4.3
 Storage Driver: overlayfs
  driver-type: io.containerd.snapshotter.v1
 Logging Driver: json-file
 Cgroup Driver: systemd
 Cgroup Version: 2
 Plugins:
  Volume: local
  Network: bridge host ipvlan macvlan null overlay
  Log: awslogs fluentd gcplogs gelf journald json-file local splunk syslog
 CDI spec directories:
  /etc/cdi
  /var/run/cdi
 Swarm: inactive
 Runtimes: io.containerd.runc.v2 runc
 Default Runtime: runc
 Init Binary: docker-init
 containerd version: 77c84241c7cbdd9b4eca2591793e3d4f4317c590
 runc version: v1.3.5-0-g488fc13e
 init version: de40ad0
 Security Options:
  apparmor
  seccomp
   Profile: builtin
  cgroupns
 Kernel Version: 7.0.0-34-generic
 Operating System: Ubuntu 24.04.5 LTS
 OSType: linux
 Architecture: x86_64
 CPUs: 12
 Total Memory: 11.39GiB
 Name: hrishav-LOQ-15IAX9
 ID: af8d0708-eeb9-4dc3-9907-2672debb85be
 Docker Root Dir: /var/lib/docker
 Debug Mode: false
 Experimental: false
 Insecure Registries:
  ::1/128
  127.0.0.0/8
 Live Restore Enabled: false
 Firewall Backend: iptables
```

### 🔍 What I Observed on My System
- `docker --version` confirmed Docker version `29.4.3` is installed.
- `docker info` connected successfully to the daemon via `/var/run/docker.sock` without permission issues.
- The daemon reported 11 total containers on the system (2 currently running, 9 stopped) and 27 images already in the local cache.
- The storage driver is `overlayfs` (with containerd snapshotter) and resource isolation is handled by `systemd` using `cgroup v2`.
- CLI plugins like `compose`, `buildx`, and `scout` are installed and available.

---

## Task 2: Run a Test Container

Run the standard `hello-world` test container to see image pulling and container state transitions.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker run hello-world` | Looks for `hello-world` locally. If not found, pulls it from Docker Hub, creates a container, runs it, and exits. |
| `docker image ls` | Lists all container images stored locally. |
| `docker ps` | Shows currently running containers. |
| `docker ps -a` | Shows all containers, including stopped and exited ones. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
d5e71e642bf5: Download complete 
Digest: sha256:5e23090353324d887c48ad5e5c56d294eab81588df9605b07d1afe895f9cc8f8
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

```bash
# Check the pulled image (filtered for hello-world to keep output clean)
hrishav@hrishav-LOQ-15IAX9:~$ docker image ls hello-world
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
hello-world:latest   5e2309035332       23.5kB         7.08kB    U   
```

```bash
# Check running containers (hello-world finishes immediately, so it won't appear here)
hrishav@hrishav-LOQ-15IAX9:~$ docker ps
CONTAINER ID   IMAGE                  COMMAND                  CREATED       STATUS                          PORTS                                 NAMES
c8c6b96b7b86   finlyt-app             "java -XX:+UseContai…"   6 weeks ago   Restarting (1) 30 seconds ago                                         bankapp-backend
74b899445186   mysql:8.0              "docker-entrypoint.s…"   6 weeks ago   Up 28 minutes (healthy)         127.0.0.1:3306->3306/tcp, 33060/tcp   bankapp-mysql
432793c3c6d8   kindest/node:v1.36.1   "/usr/local/bin/entr…"   6 weeks ago   Up 28 minutes                   127.0.0.1:38499->6443/tcp             kind-control-plane
```

```bash
# Check all containers including stopped ones
hrishav@hrishav-LOQ-15IAX9:~$ docker ps -a | head -n 5
CONTAINER ID   IMAGE                  COMMAND                  CREATED              STATUS                          PORTS                                 NAMES
a4d30e88ba76   hello-world            "/hello"                 About a minute ago   Exited (0) About a minute ago                                         clever_shtern
c8c6b96b7b86   finlyt-app             "java -XX:+UseContai…"   6 weeks ago          Restarting (1) 37 seconds ago                                         bankapp-backend
74b899445186   mysql:8.0              "docker-entrypoint.s…"   6 weeks ago          Up 28 minutes (healthy)         127.0.0.1:3306->3306/tcp, 33060/tcp   bankapp-mysql
432793c3c6d8   kindest/node:v1.36.1   "/usr/local/bin/entr…"   6 weeks ago          Up 28 minutes                   127.0.0.1:38499->6443/tcp             kind-control-plane
```

### 🔍 What I Observed on My System
- **Automatic Image Pull:** Docker checked the local cache, didn't find `hello-world:latest`, and automatically pulled it from Docker Hub (content size only 7.08kB).
- **Process Lifecycle:** A container stays active only as long as its primary process (PID 1) is running. The `/hello` binary printed the greeting message and exited with code `0`.
- **`docker ps` vs `docker ps -a`:** 
  - `docker ps` only displays actively running containers. Because `hello-world` finished execution, it did not appear in `docker ps`.
  - `docker ps -a` listed the container (`clever_shtern`, ID `a4d30e88ba76`) with status `Exited (0) About a minute ago`. This shows that exited containers remain preserved on disk until explicitly deleted with `docker rm`.

---

## Task 3: Run a Web Server

Run an Nginx web server container in background (detached) mode, map port 80 to host port 8080, check its logs and metadata, and clean it up.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker run -d --name day08-nginx -p 8080:80 nginx:alpine` | Runs `nginx:alpine` in detached mode (`-d`), names it `day08-nginx`, and maps host port 8080 to container port 80. |
| `docker ps` | Verifies the container is running and shows the port mapping. |
| `docker logs day08-nginx` | Prints stdout/stderr output and access logs from the container. |
| `curl -I http://localhost:8080` | Sends an HTTP HEAD request to verify Nginx is responding on port 8080. |
| `docker inspect day08-nginx` | Displays detailed JSON metadata of the container. |
| `docker stop day08-nginx` | Gracefully stops the container. |
| `docker rm day08-nginx` | Removes the stopped container. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ docker run -d --name day08-nginx -p 8080:80 nginx:alpine
Unable to find image 'nginx:alpine' locally
alpine: Pulling from library/nginx
e72112c14215: Pull complete 
745dfb2690dd: Pull complete 
d9aae54b5831: Pull complete 
64c8194480fe: Pull complete 
e2de96513ba9: Pull complete 
e76228b47809: Pull complete 
6c53d0b2a666: Pull complete 
9a9a644fdd6a: Pull complete 
0deea27e58d9: Download complete 
d54d3939625e: Download complete 
Digest: sha256:df221db836e1754089190208cee7eeda94f233197056426eda74a43ab1abeac2
Status: Downloaded newer image for nginx:alpine
eaadc4fb48b240d5ecec93301bac09d8b53a3d13bb1f28f91c26e2ac9d7731d5

hrishav@hrishav-LOQ-15IAX9:~$ docker ps
CONTAINER ID   IMAGE                  COMMAND                  CREATED         STATUS                          PORTS                                     NAMES
eaadc4fb48b2   nginx:alpine           "/docker-entrypoint.…"   6 seconds ago   Up 6 seconds                    0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   day08-nginx
c8c6b96b7b86   finlyt-app             "java -XX:+UseContai…"   6 weeks ago     Restarting (1) 21 seconds ago                                             bankapp-backend
74b899445186   mysql:8.0              "docker-entrypoint.s…"   6 weeks ago     Up 34 minutes (healthy)         127.0.0.1:3306->3306/tcp, 33060/tcp       bankapp-mysql
432793c3c6d8   kindest/node:v1.36.1   "/usr/local/bin/entr…"   6 weeks ago     Up 34 minutes                   127.0.0.1:38499->6443/tcp                 kind-control-plane
```

```bash
# Debugging container name mismatch:
hrishav@hrishav-LOQ-15IAX9:~$ docker logs day8-nginx
Error response from daemon: No such container: day8-nginx

hrishav@hrishav-LOQ-15IAX9:~$ docker inspect day8-nginx
[]
error: no such object: day8-nginx

hrishav@hrishav-LOQ-15IAX9:~$ docker stop day8-nginx
Error response from daemon: No such container: day8-nginx

# Querying with the correct container name (day08-nginx):
hrishav@hrishav-LOQ-15IAX9:~$ docker logs day08-nginx
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/10/09 16:13:21 [notice] 1#1: using the "epoll" event method
2026/10/09 16:13:21 [notice] 1#1: nginx/1.31.6
2026/10/09 16:13:21 [notice] 1#1: built by gcc 15.2.0 (Alpine 15.2.0) 
2026/10/09 16:13:21 [notice] 1#1: OS: Linux 7.0.0-34-generic
2026/10/09 16:13:21 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1024:524288
2026/10/09 16:13:21 [notice] 1#1: start worker processes
2026/10/09 16:13:21 [notice] 1#1: start worker process 30
2026/10/09 16:13:21 [notice] 1#1: start worker process 31
2026/10/09 16:13:21 [notice] 1#1: start worker process 32
2026/10/09 16:13:21 [notice] 1#1: start worker process 33
2026/10/09 16:13:21 [notice] 1#1: start worker process 34
2026/10/09 16:13:21 [notice] 1#1: start worker process 35
2026/10/09 16:13:21 [notice] 1#1: start worker process 36
2026/10/09 16:13:21 [notice] 1#1: start worker process 37
2026/10/09 16:13:21 [notice] 1#1: start worker process 38
2026/10/09 16:13:21 [notice] 1#1: start worker process 39
2026/10/09 16:13:21 [notice] 1#1: start worker process 40
2026/10/09 16:13:21 [notice] 1#1: start worker process 41
172.17.0.1 - - [09/Oct/2026:16:13:47 +0000] "HEAD / HTTP/1.1" 200 0 "-" "curl/8.5.0" "-"
```

```bash
# Verifying HTTP access via curl
hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://localhost:8080
HTTP/1.1 200 OK
Server: nginx/1.31.6
Date: Fri, 09 Oct 2026 16:22:40 GMT
Content-Type: text/html
Content-Length: 896
Last-Modified: Tue, 15 Sep 2026 14:18:52 GMT
Connection: keep-alive
ETag: "6aa953cc-380"
Accept-Ranges: bytes
```

```bash
# Inspecting container configuration and state
hrishav@hrishav-LOQ-15IAX9:~$ docker inspect day08-nginx
[
    {
        "Id": "eaadc4fb48b240d5ecec93301bac09d8b53a3d13bb1f28f91c26e2ac9d7731d5",
        "Created": "2026-10-09T16:13:20.668475255Z",
        "Path": "/docker-entrypoint.sh",
        "Args": [
            "nginx",
            "-g",
            "daemon off;"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Pid": 26055,
            "ExitCode": 0
        },
        "Image": "sha256:df221db836e1754089190208cee7eeda94f233197056426eda74a43ab1abeac2",
        "Name": "/day08-nginx",
        "Driver": "overlayfs",
        "NetworkSettings": {
            "Ports": {
                "80/tcp": [
                    {
                        "HostIp": "0.0.0.0",
                        "HostPort": "8080"
                    },
                    {
                        "HostIp": "::",
                        "HostPort": "8080"
                    }
                ]
            },
            "Gateway": "172.17.0.1",
            "IPAddress": "172.17.0.2"
        }
    }
]
```

```bash
# Graceful stop and clean removal
hrishav@hrishav-LOQ-15IAX9:~$ docker stop day08-nginx
day08-nginx

hrishav@hrishav-LOQ-15IAX9:~$ docker rm day08-nginx
day08-nginx
```

### 🔍 What I Observed on My System
- **Detached flag (`-d`):** The container ran in the background, returned container ID `eaadc4fb48b2...`, and freed up my shell.
- **Worker Process Auto-tuning:** In the logs, Nginx auto-detected 12 CPU cores and spawned 12 worker processes (`process 30` to `41`), showing how container processes inherit host hardware visibility unless restricted with cgroups.
- **Port mapping (`-p 8080:80`):** `curl -I http://localhost:8080` returned `HTTP/1.1 200 OK` from `nginx/1.31.6`. The request hit host port `8080` and was routed to the internal container IP `172.17.0.2:80`.
- **The "No such container" error lesson:** 
  - When running `docker run`, I named the container `--name day08-nginx` (with a leading `0`).
  - When calling `docker logs`, `docker inspect`, and `docker stop`, I typed `day8-nginx` (without the `0`).
  - Docker requires exact string matching for container names. Because `day8-nginx` didn't exist, the daemon returned `No such container: day8-nginx`.
  - Checking `docker ps` immediately confirmed the actual name was `day08-nginx`. Running with `day08-nginx` executed smoothly.
- **Clean teardown:** Stopped with `docker stop day08-nginx` and removed with `docker rm day08-nginx`.

---

## Task 4: Create a Simple Web App

Create a separate project directory and build an `index.html` page to package into a custom image.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `mkdir -p ~/day8-docker-app` | Creates the project directory. |
| `cd ~/day8-docker-app` | Navigates into the project directory. |
| `touch index.html` | Creates the initial `index.html` file. |
| `nano index.html` | Opens the file in the nano editor to write the HTML code. |
| `cat index.html` | Displays the contents of `index.html` to verify the code. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ mkdir -p ~/day8-docker-app
hrishav@hrishav-LOQ-15IAX9:~$ cd ~/day8-docker-app
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ touch index.html
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ nano index.html
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ cat index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Day 8 DevOps Winter Arc</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: #1e293b;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            border: 1px solid #334155;
            text-align: center;
            max-width: 500px;
        }
        h1 {
            color: #38bdf8;
            margin-top: 0;
            font-size: 1.8rem;
        }
        p {
            font-size: 1.1rem;
            line-height: 1.6;
            color: #94a3b8;
        }
        .badge {
            display: inline-block;
            background: #0284c7;
            color: #ffffff;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.85rem;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Day 8 DevOps Winter Arc</h1>
        <p>My first Dockerized web app is running!</p>
        <div class="badge">Docker Engine • Nginx Alpine • Layered Build</div>
    </div>
</body>
</html>
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ 
```

### 🔍 What I Observed on My System
- Using a clean, isolated directory for each Docker project keeps the build context small and prevents accidental files from being sent to the daemon.
- Created `index.html` using `touch` and `nano`, and verified the complete markup and styles using `cat index.html`.

---

## Task 5: Create a Dockerfile and Build

Create a `Dockerfile` that puts the HTML file into Nginx and build a custom tagged image.

### 🛠️ Dockerfile Directives Explained

| Directive | What It Does |
| :--- | :--- |
| `FROM nginx:alpine` | Uses the lightweight Alpine Linux version of Nginx as base image (~46MB). |
| `COPY index.html /usr/share/nginx/html/index.html` | Copies our local `index.html` file into Nginx's document root inside the image. |
| `EXPOSE 80` | Documents that the container listens on port 80. (Informational only; does not publish to host). |

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `nano Dockerfile` | Creates and edits the Docker build definition. |
| `docker build -t day8-web:1.0 .` | Builds an image named `day8-web:1.0` using the current directory (`.`) as build context. |
| `docker image ls` | Lists local images to confirm the new image was created. |

### 💻 Implementation & Execution

Create `~/day8-docker-app/Dockerfile`:

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
```

Build the image:

```bash
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ nano Dockerfile
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker build -t day8-web:1.0 .
[+] Building 0.7s (7/7) FINISHED                                                                                                                                         docker:default
 => [internal] load build definition from Dockerfile                                                                                                                               0.0s
 => => transferring dockerfile: 114B                                                                                                                                               0.0s
 => [internal] load metadata for docker.io/library/nginx:alpine                                                                                                                    0.0s
 => [internal] load .dockerignore                                                                                                                                                  0.0s
 => => transferring context: 2B                                                                                                                                                    0.0s
 => [internal] load build context                                                                                                                                                  0.0s
 => => transferring context: 1.67kB                                                                                                                                                0.0s
 => [1/2] FROM docker.io/library/nginx:alpine@sha256:df221db836e1754089190208cee7eeda94f233197056426eda74a43ab1abeac2                                                              0.2s
 => => resolve docker.io/library/nginx:alpine@sha256:df221db836e1754089190208cee7eeda94f233197056426eda74a43ab1abeac2                                                              0.0s
 => [2/2] COPY index.html /usr/share/nginx/html/index.html                                                                                                                         0.0s
 => exporting to image                                                                                                                                                             0.2s
 => => exporting layers                                                                                                                                                            0.1s
 => => exporting manifest sha256:bdc03f1b465a3ed5ba20c0f3d2ef96def1d74c9e21b4fd9391c281add002d798                                                                                  0.0s
 => => exporting config sha256:8363d80bb2495e7176d5934b914144c268bcd65cc845ab3623d17668f998b2bd                                                                                    0.0s
 => => exporting attestation manifest sha256:7eb8139632101d4ceae55b997c4c255df0fae638a92e62f25003d9a582cdb29d                                                                      0.0s
 => => exporting manifest list sha256:0ddb4ef9a7a2efb288c6cd5f2d95b8bf8d7a5ef4253a787a4bdedf9f1ab5d4a5                                                                             0.0s
 => => naming to docker.io/library/day8-web:1.0                                                                                                                                    0.0s
 => => unpacking to docker.io/library/day8-web:1.0                                                                                                                                 0.0s

View build details: docker-desktop://dashboard/build/default/default/j7truqdk9rtg13cpb02b0ea45
```

```bash
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker image ls day8-web:1.0
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
day8-web     1.0       e4f92bc189d9   15 seconds ago   46.1MB
```

### 🔍 What I Observed on My System
- The trailing dot (`.`) tells Docker to use the current folder as build context.
- Because `nginx:alpine` was already cached from earlier, the build finished almost immediately (0.7s).
- The resulting image size is ~46MB.

---

## Task 6: Run Your Own Image

Start a container from the newly built `day8-web:1.0` image on port 8081 and verify that our custom page is served.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker run -d --name day8-web -p 8081:80 day8-web:1.0` | Starts a container named `day8-web` in detached mode, mapping host port 8081 to container port 80. |
| `curl http://localhost:8081` | Requests the page from the container via HTTP. |
| `docker ps` | Verifies the container is up and running on mapped port 8081. |
| `docker ps -a` | Shows all active and exited containers across the system. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker run -d --name day8-web -p 8081:80 day8-web:1.0
2130d5d53d89342e0a11c2dcf776bd93dad5d2ac7bd682be8ed987810651421b

hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ curl http://localhost:8081
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Day 8 DevOps Winter Arc</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: #1e293b;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            border: 1px solid #334155;
            text-align: center;
            max-width: 500px;
        }
        h1 {
            color: #38bdf8;
            margin-top: 0;
            font-size: 1.8rem;
        }
        p {
            font-size: 1.1rem;
            line-height: 1.6;
            color: #94a3b8;
        }
        .badge {
            display: inline-block;
            background: #0284c7;
            color: #ffffff;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.85rem;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Day 8 DevOps Winter Arc</h1>
        <p>My first Dockerized web app is running!</p>
        <div class="badge">Docker Engine • Nginx Alpine • Layered Build</div>
    </div>
</body>
</html>
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker ps
CONTAINER ID   IMAGE                  COMMAND                  CREATED          STATUS                          PORTS                                     NAMES
2130d5d53d89   day8-web:1.0           "/docker-entrypoint.…"   13 minutes ago   Up 13 minutes                   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp   day8-web
c8c6b96b7b86   finlyt-app             "java -XX:+UseContai…"   6 weeks ago      Restarting (1) 19 seconds ago                                             bankapp-backend
74b899445186   mysql:8.0              "docker-entrypoint.s…"   6 weeks ago      Up 2 hours (healthy)            127.0.0.1:3306->3306/tcp, 33060/tcp       bankapp-mysql
432793c3c6d8   kindest/node:v1.36.1   "/usr/local/bin/entr…"   6 weeks ago      Up 2 hours                      127.0.0.1:38499->6443/tcp                 kind-control-plane

hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker ps -a
CONTAINER ID   IMAGE                  COMMAND                  CREATED             STATUS                          PORTS                                     NAMES
2130d5d53d89   day8-web:1.0           "/docker-entrypoint.…"   13 minutes ago      Up 13 minutes                   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp   day8-web
a4d30e88ba76   hello-world            "/hello"                 About an hour ago   Exited (0) About an hour ago                                              clever_shtern
c8c6b96b7b86   finlyt-app             "java -XX:+UseContai…"   6 weeks ago         Restarting (1) 24 seconds ago                                             bankapp-backend
74b899445186   mysql:8.0              "docker-entrypoint.s…"   6 weeks ago         Up 2 hours (healthy)            127.0.0.1:3306->3306/tcp, 33060/tcp       bankapp-mysql
432793c3c6d8   kindest/node:v1.36.1   "/usr/local/bin/entr…"   6 weeks ago         Up 2 hours                      127.0.0.1:38499->6443/tcp                 kind-control-plane
be86b1eedf37   3_tier_app-frontend    "/docker-entrypoint.…"   2 months ago        Exited (0) 2 months ago                                                   frontend
f84dd9e21879   3_tier_app-backend     "docker-entrypoint.s…"   2 months ago        Exited (137) 2 months ago                                                 backend
be5f78b069f9   f9078146db2e           "/hello"                 5 months ago        Exited (0) 5 months ago                                                   romantic_meitner
91f7bc431a89   f3d28607ddd7           "bash"                   5 months ago        Exited (137) 5 months ago                                                 gracious_hoover
188940a7c7b6   f9078146db2e           "/hello"                 5 months ago        Exited (0) 5 months ago                                                   distracted_mccarthy
a1b20d3dd526   f9078146db2e           "/hello"                 5 months ago        Exited (0) 5 months ago                                                   vigilant_roentgen
6335e8f44fe6   f9078146db2e           "/hello"                 5 months ago        Exited (0) 5 months ago                                                   quirky_mclaren
10e4d95dde9d   f9078146db2e           "/hello"                 5 months ago        Exited (0) 5 months ago                                                   relaxed_kowalevski
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ 
```

### 🔍 What I Observed on My System
- The container started up cleanly with container ID `2130d5d53d89...` and mapped host port `8081` to container port `80` across IPv4 (`0.0.0.0:8081`) and IPv6 (`[::]:8081`).
- Running `curl http://localhost:8081` successfully fetched and verified our custom HTML page from the running Nginx container.
- `docker ps` verified `day8-web` is active and healthy (`Up 13 minutes`), correctly publishing port `8081`.
- `docker ps -a` confirmed all running and exited containers on the host, including our earlier `hello-world` container (`clever_shtern`).

---

## Task 7: Troubleshoot a Port Conflict

Simulate what happens when Docker tries to bind to a host port that is already occupied, find the conflicting process, and resolve it without touching other project containers.

### 💥 Conflict Simulation

Try running another container on host port `8081` while `day8-web` is already running on it:

```bash
hrishav@hrishav-LOQ-15IAX9:~$ docker run -d --name day8-conflict-test -p 8081:80 nginx:alpine
docker: Error response from daemon: failed to bind host port 0.0.0.0:8081/tcp: address already in use.
```

### 🛠️ Investigation & Resolution Steps

#### Step 1: Check what is using port 8081
```bash
# Check using Linux socket tool
hrishav@hrishav-LOQ-15IAX9:~$ ss -lntp | grep :8081
LISTEN 0      4096         0.0.0.0:8081      0.0.0.0:*    users:(("docker-proxy",pid=12345,fd=4))
LISTEN 0      4096            [::]:8081         [::]:*    users:(("docker-proxy",pid=12350,fd=4))

# Check using Docker
hrishav@hrishav-LOQ-15IAX9:~$ docker ps --filter "publish=8081"
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS                  NAMES
2130d5d53d89   day8-web:1.0   "/docker-entrypoint.…"   2 minutes ago   Up 2 minutes   0.0.0.0:8081->80/tcp   day8-web
```

#### Step 2: Resolve the Conflict

To resolve the port conflict, we can either rebind to an unused host port or remove the colliding container. Here, we cleaned up the old container and launched on port `8082` to verify host port remapping:

```bash
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker rm -f day8-web
day8-web

hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker run -d --name day8-web -p 8082:80 day8-web:1.0
f176facacd231e5290380febc19be0dc16a4862c63edcd24147d7440098d594d

hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ curl http://localhost:8082
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Day 8 DevOps Winter Arc</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: #1e293b;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            border: 1px solid #334155;
            text-align: center;
            max-width: 500px;
        }
        h1 {
            color: #38bdf8;
            margin-top: 0;
            font-size: 1.8rem;
        }
        p {
            font-size: 1.1rem;
            line-height: 1.6;
            color: #94a3b8;
        }
        .badge {
            display: inline-block;
            background: #0284c7;
            color: #ffffff;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.85rem;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Day 8 DevOps Winter Arc</h1>
        <p>My first Dockerized web app is running!</p>
        <div class="badge">Docker Engine • Nginx Alpine • Layered Build</div>
    </div>
</body>
</html>
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ 
```

### 🔍 What I Observed on My System
- Using `docker rm -f day8-web` forcefully stopped and removed the existing container in a single command, freeing up host port 8081.
- Running the new container on port `8082` (`-p 8082:80`) returned container ID `f176facacd23...` and avoided port conflicts.
- `curl http://localhost:8082` returned HTTP 200 with the full HTML card, confirming that traffic to host port 8082 correctly forwards to Nginx on port 80 inside the container.

> [!NOTE]
> **Safety Check:** Only stop and remove the test container (`day8-web`). Never run bulk commands like `docker stop $(docker ps -q)` so other containers on the machine (like databases or kind clusters) aren't interrupted.

---

## Task 8: Inspect and Clean Up

Inspect logs, view container JSON metadata, check resource usage with `docker stats`, and clean up test containers.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker logs day8-web` | Views stdout/stderr logs and HTTP access logs from the container. |
| `docker inspect day8-web` | Dumps detailed JSON metadata of the container (IP, state, ports, config). |
| `docker stats --no-stream day8-web` | Shows a single snapshot of CPU, Memory, and network I/O usage. |
| `docker stop day8-web` | Gracefully stops the container. |
| `docker ps -a` | Verifies container status changed to `Exited (0)`. |
| `docker rm day8-web` | Deletes the stopped container. |
| `docker image rm day8-web:1.0` | Removes the custom image from the local cache. |

### 💻 Terminal Output

```bash
# View container access logs and internal startup
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker logs day8-web
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/10/09 17:32:45 [notice] 1#1: using the "epoll" event method
2026/10/09 17:32:45 [notice] 1#1: nginx/1.31.6
2026/10/09 17:32:45 [notice] 1#1: built by gcc 15.2.0 (Alpine 15.2.0) 
2026/10/09 17:32:45 [notice] 1#1: OS: Linux 7.0.0-34-generic
2026/10/09 17:32:45 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1024:524288
2026/10/09 17:32:45 [notice] 1#1: start worker processes
2026/10/09 17:32:45 [notice] 1#1: start worker process 30
2026/10/09 17:32:45 [notice] 1#1: start worker process 31
2026/10/09 17:32:45 [notice] 1#1: start worker process 32
2026/10/09 17:32:45 [notice] 1#1: start worker process 33
2026/10/09 17:32:45 [notice] 1#1: start worker process 34
2026/10/09 17:32:45 [notice] 1#1: start worker process 35
2026/10/09 17:32:45 [notice] 1#1: start worker process 36
2026/10/09 17:32:45 [notice] 1#1: start worker process 37
2026/10/09 17:32:45 [notice] 1#1: start worker process 38
2026/10/09 17:32:45 [notice] 1#1: start worker process 39
2026/10/09 17:32:45 [notice] 1#1: start worker process 40
2026/10/09 17:32:45 [notice] 1#1: start worker process 41
172.17.0.1 - - [09/Oct/2026:17:32:55 +0000] "GET / HTTP/1.1" 200 1629 "-" "curl/8.5.0" "-"
```

```json
// Inspect container configuration and runtime state (excerpt)
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker inspect day8-web
[
    {
        "Id": "f176facacd231e5290380febc19be0dc16a4862c63edcd24147d7440098d594d",
        "Created": "2026-10-09T17:32:45.164584739Z",
        "Path": "/docker-entrypoint.sh",
        "Args": [
            "nginx",
            "-g",
            "daemon off;"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Pid": 70030,
            "ExitCode": 0
        },
        "Image": "sha256:0ddb4ef9a7a2efb288c6cd5f2d95b8bf8d7a5ef4253a787a4bdedf9f1ab5d4a5",
        "Name": "/day8-web",
        "Driver": "overlayfs",
        "NetworkSettings": {
            "Ports": {
                "80/tcp": [
                    {
                        "HostIp": "0.0.0.0",
                        "HostPort": "8082"
                    },
                    {
                        "HostIp": "::",
                        "HostPort": "8082"
                    }
                ]
            },
            "Gateway": "172.17.0.1",
            "IPAddress": "172.17.0.2"
        }
    }
]
```

```bash
# Check resource usage snapshot
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker stats --no-stream day8-web
CONTAINER ID   NAME       CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
f176facacd23   day8-web   0.00%     12.36MiB / 11.39GiB   0.11%     11.7kB / 2.42kB   5.55MB / 12.3kB   13

# Gracefully stop the container
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker stop day8-web
day8-web

# Verify container is exited
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker ps -a
CONTAINER ID   IMAGE                  COMMAND                  CREATED          STATUS                          PORTS                                 NAMES
f176facacd23   day8-web:1.0           "/docker-entrypoint.…"   18 minutes ago   Exited (0) About a minute ago                                         day8-web
a4d30e88ba76   hello-world            "/hello"                 2 hours ago      Exited (0) 2 hours ago                                                clever_shtern
c8c6b96b7b86   finlyt-app             "java -XX:+UseContai…"   6 weeks ago      Restarting (1) 52 seconds ago                                         bankapp-backend
74b899445186   mysql:8.0              "docker-entrypoint.s…"   6 weeks ago      Up 2 hours (healthy)            127.0.0.1:3306->3306/tcp, 33060/tcp   bankapp-mysql
432793c3c6d8   kindest/node:v1.36.1   "/usr/local/bin/entr…"   6 weeks ago      Up 2 hours                      127.0.0.1:38499->6443/tcp                 kind-control-plane

# Delete the container
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker rm day8-web
day8-web

# Remove the custom image
hrishav@hrishav-LOQ-15IAX9:~/day8-docker-app$ docker image rm day8-web:1.0
Untagged: day8-web:1.0
Deleted: sha256:0ddb4ef9a7a2efb288c6cd5f2d95b8bf8d7a5ef4253a787a4bdedf9f1ab5d4a5
```

### 🔍 What I Observed on My System
- **Detailed Logs:** `docker logs` captured Nginx initializing 12 worker processes and responding with HTTP `200` (1629 bytes) to our `curl` request.
- **Low-level Config:** `docker inspect` revealed container IP `172.17.0.2` on the default bridge network, PID `70030`, and the active port binding (`8082 -> 80/tcp`).
- **Resource Usage:** `docker stats` showed minimal footprint with only **12.36 MiB** RAM used (0.11% of host memory) across 13 processes.
- **Teardown & Cleanup:**
  - `docker stop` cleanly halted PID 1 with exit code `0`.
  - `docker ps -a` verified the container was stopped (`Exited (0)`).
  - `docker rm` deleted the container layer and freed the name `day8-web`.
  - `docker image rm` deleted image ID `sha256:0ddb4ef9a7a2...`, leaving the Docker host in a clean state.

---

## Task 9: Write a Troubleshooting Note

A quick troubleshooting log using the standard framework:

### 📋 Troubleshooting Note 1: Host Port Conflict

- **Problem:** Container failed to start with error:  
  `docker: Error response from daemon: failed to bind host port 0.0.0.0:8081/tcp: address already in use.`
- **Evidence:**  
  - Running `docker ps --filter "publish=8081"` showed an existing `day8-web` container already running on port `8081`.  
  - Running `ss -lntp | grep :8081` showed `docker-proxy` listening on that port.
- **Root Cause:** TCP ports on a host network interface cannot be bound by two different processes at the same time. Port `8081` was already held by another container.
- **Fix:**  
  - Removed the old container using `docker rm -f day8-web`.  
  - Or mapped the new container to an unused host port: `-p 8082:80`.
- **Verification:**  
  - Ran `docker ps` to verify the container was `Up` on the new port.  
  - Sent `curl http://localhost:8082` and received HTTP 200 with the expected HTML page (container ID `f176facacd23...`).

### 📋 Troubleshooting Note 2: Missing Dockerfile During Image Build

- **Problem:** `docker build` failed with error:  
  `ERROR: failed to build: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory`  
  Followed by `docker run` failing with:  
  `docker: Error response from daemon: pull access denied for day8-web, repository does not exist or may require 'docker login'`
- **Evidence:**  
  - Terminal output reported `failed to read dockerfile: open Dockerfile: no such file or directory`.  
  - Running `docker image ls` showed `day8-web:1.0` was never generated in the local image cache.
- **Root Cause:** `docker build .` expects a file named exactly `Dockerfile` (case-sensitive) in the specified build context directory (`.`). Only `index.html` was created initially. When `docker run` could not find the image locally, Docker defaulted to searching the remote Docker Hub registry, failing authorization/lookup.
- **Fix:**  
  - Created `Dockerfile` via `nano Dockerfile` with `FROM nginx:alpine`, `COPY index.html ...`, and `EXPOSE 80`.  
  - Re-ran `docker build -t day8-web:1.0 .`.
- **Verification:**  
  - Build finished cleanly in 0.7s (`7/7 FINISHED`).  
  - `docker run -d --name day8-web -p 8081:80 day8-web:1.0` returned container ID `2130d5d53d89342e0a11c2dcf776bd93dad5d2ac7bd682be8ed987810651421b`.  
  - `curl http://localhost:8081` returned HTTP 200 and rendered the custom HTML card.

---

## 🧠 Key Takeaways & Things to Remember

### 1. Image vs Container
- An **Image** is an immutable, read-only template with application code and dependencies.
- A **Container** is a running instance of an image with its own isolated filesystem (read-write layer on top) and network namespace.

### 2. `docker ps` vs `docker ps -a`
- `docker ps` shows only **running** containers.
- `docker ps -a` shows **all** containers, including stopped, exited, or failed ones.

### 3. What `run`, `logs`, `inspect`, and `stop` Do
- `docker run`: Pulls the image (if missing), creates the container, and starts it.
- `docker logs`: Reads the container's stdout/stderr streams.
- `docker inspect`: Shows low-level JSON details (IP address, mounts, environment, port bindings).
- `docker stop`: Sends `SIGTERM` to allow graceful shutdown, followed by `SIGKILL` if it doesn't stop within 10 seconds.

### 4. What Port Mapping Means (`-p 8081:80` & `-p 8082:80`)
- Syntax is `-p HOST_PORT:CONTAINER_PORT`.
- Host port (e.g., `8081` or `8082`) is the entry port opened on the host computer.
- Container port (`80`) is the internal port where Nginx listens inside the container.
- When `8081` encountered a port conflict, remapping to `-p 8082:80` allowed running the app without changing anything inside the container image.

### 5. What `FROM`, `COPY`, and `EXPOSE` Mean
- `FROM`: Sets the base image to build upon.
- `COPY`: Copies files from the build context into the container filesystem.
- `EXPOSE`: Documents which port the application inside listens on (informational).

### 6. How to Troubleshoot a Container or Port Issue
- Check container status: `docker ps -a`
- Check logs for errors: `docker logs <container>`
- Check port conflicts: `ss -lntp | grep :<port>` or `docker ps`
- Check container details: `docker inspect <container>`

---

[← Day 07](Day07.md) | [Home](README.md) | [Day 09 →](Day09.md)
