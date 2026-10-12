# DevOps Winter Arc — Day 11: Docker Volumes & Custom Networking

> **90 Days of DevOps Challenge | Containers Week | Learn • Practice • Build**  
> **Topic: Persisting Container Data with Volumes, User-Defined Bridge Networks, Embedded DNS, Backup & Restore, Port Conflict Troubleshooting**

---

## 🎯 Goal for Today

Day 11 of my DevOps Winter Arc!

By default, Docker containers are disposable. Anything written inside a container lives in a temporary writable layer that gets completely deleted when you run `docker rm`. If you run a database inside a container without a volume, the moment the container dies, all your data is gone with it.

Today, I'm tackling two core problems:
1. **Keeping data alive after a container is destroyed** using Docker named volumes.
2. **Making containers talk to each other by name** using a custom bridge network and Docker's built-in DNS (without exposing database ports to the host or internet).

### Today's Tasks
- [x] Persist application data using a named volume (`pgdata`)
- [x] Connect two containers using a custom network (`app-net`)
- [x] Prove data survives container deletion (`docker rm -f`)
- [x] Test container DNS resolution vs default bridge failure
- [x] Back up and restore a volume using a throwaway container
- [x] Troubleshoot port conflicts (`port is already allocated`)

---

## 📖 Key Concepts (The Core 30%)

### 1. Containers Are Disposable
Every container gets a thin writable layer on top of read-only image layers. When the container is deleted, that writable layer is wiped out. To keep state (like database records, logs, or user uploads), data has to be stored outside the container lifecycle.

### 2. Volume vs Bind Mount vs tmpfs

| Type | Where it lives | Managed by | Survives `docker rm`? | Best for | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Named Volume** | Docker storage area (`/var/lib/docker/volumes`) | Docker | **Yes** | Databases, production data | `-v pgdata:/var/lib/postgresql/data` |
| **Bind Mount** | Any host path you choose | You / OS | **Yes** (it's your folder) | Development code, live reload, configs | `-v $(pwd):/app` |
| **tmpfs** | Host RAM only | Linux kernel | **No** (cleared on stop) | Sensitive tokens, scratch data | `--tmpfs /tmp` |

### 3. Docker Network Drivers

| Driver | What it does | When to use |
| :--- | :--- | :--- |
| **bridge (default)** | Default private network on host. Containers reach outside via NAT, but **no DNS names by default**. | Quick tests only |
| **bridge (user-defined)** | Same as bridge, but has **automatic DNS by container name** and better isolation. | Almost every multi-container app |
| **host** | Container shares the host network stack directly. No port mapping needed. | Max network speed, special tools (Linux only) |
| **none** | No network interface except loopback. | Fully isolated batch jobs |
| **overlay** | Spans multiple Docker hosts. | Docker Swarm (Kubernetes replaces this) |

### 4. How Containers Talk

```
                      Custom Network: app-net
  Browser   +-------------------------------------------+
    |       |   +----------+   http://db:5432   +------+ |
    +-8080->|   |   api    | -----------------> |  db  | |
   (host)   |   | (app)    |   DNS: "db" -> IP  |(pg)  | |
            |   +----------+                    +---+--+ |
            +-------------------------------------|-----+
                                                  |
                                          Volume: pgdata

  Only the API port is published to host (-p 8080:80).
  The database is accessible ONLY inside app-net.
```

> **Important Rule:** `localhost` inside a container means the container itself, not my host machine and not another container. To talk to another container, they must be on the same custom network and talk using container names (e.g. `db`). Publishing database ports (`-p 5432:5432`) to the host is a security risk—keep it internal!

---

## 🛠️ Quick Command Reference

### Volumes
| Command | What it does | Why I use it |
| :--- | :--- | :--- |
| `docker volume create pgdata` | Creates a named volume | Prepare storage before running a database |
| `docker volume ls` | Lists all volumes | See what storage exists on the host |
| `docker volume inspect pgdata` | Shows mountpoint and driver | Find where files actually live on disk |
| `docker volume rm pgdata` | Deletes a volume | Cleanup (permanent data loss!) |
| `docker run -v pgdata:/var/lib/postgresql/data ...` | Mounts named volume at container path | Run a persistent database |
| `docker run -v $(pwd):/app ...` | Bind mounts current folder | Code editing with live reload |

### Networks
| Command | What it does | Why I use it |
| :--- | :--- | :--- |
| `docker network ls` | Lists all networks | See bridge, host, none, and custom networks |
| `docker network create app-net` | Creates custom bridge network | Isolate services with built-in DNS |
| `docker network inspect app-net` | Shows subnet & attached containers | Check connected IPs and containers |
| `docker run --network app-net --name db ...` | Starts container on network | Put app and database together |
| `docker network connect app-net web` | Connects running container to network | Add container without restarting |
| `docker port web` | Shows published port mappings | Check which host port maps to container |

### Troubleshooting
| Command | What it does | Why I use it |
| :--- | :--- | :--- |
| `ss -tulpn \| grep 8080` | Finds process listening on port 8080 | Fix "port is already allocated" errors |
| `docker exec api ping -c 2 db` | Pings container by name | Test if container DNS is resolving |
| `docker exec db pg_isready -U postgres` | Checks if Postgres is accepting queries | Wait for database readiness |
| `docker logs db --tail 30` | Shows recent database log lines | Spot startup or authentication errors |

---

## 🏗️ Hands-On Tasks & Lab Execution

My workspace directory: `~/day11-storage-network`

---

### Task 1: Create Custom Network & Named Volume

First step is setting up our isolated network and storage volume before running any containers.

#### Commands:
```bash
mkdir -p ~/day11-storage-network && cd ~/day11-storage-network
docker network create app-net
docker volume create pgdata
docker network ls
docker volume inspect pgdata
```

#### Terminal Output:
```bash
hrishav@hrishav-LOQ-15IAX9:~$ mkdir -p ~/day11-storage-network && cd ~/day11-storage-network
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker network create app-net
a5e8ab025bf3db948330964239d0d7393f009a5bdaa085dacb123713129ab41b
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker volume create pgdata
pgdata
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker network ls
NETWORK ID     NAME                   DRIVER    SCOPE
cb737e212955   3_tier_app_mynet       bridge    local
a5e8ab025bf3   app-net                bridge    local
d09fa4ed7c97   bridge                 bridge    local
5945cfd82ba5   finlyt_bankapp-net     bridge    local
adf369198225   host                   host      local
a1aee713e03d   kind                   bridge    local
2ac230e00bcc   none                   null      local
0265aee3ab4f   task-tracker_default   bridge    local
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker volume inspect pgdata
[
    {
        "CreatedAt": "2026-10-12T19:09:10+05:30",
        "Driver": "local",
        "Labels": null,
        "Mountpoint": "/var/lib/docker/volumes/pgdata/_data",
        "Name": "pgdata",
        "Options": null,
        "Scope": "local"
    }
]
```

#### My Observations:
- `docker network create app-net` created a bridge network with scope `local`. Unlike the default `bridge`, this user-defined network enables Docker's embedded DNS server (`127.0.0.11`).
- `docker volume inspect pgdata` shows that Docker manages the storage under `/var/lib/docker/volumes/pgdata/_data` on the host. This lives independently of any container lifecycle. 

---

### Task 2: Launch PostgreSQL with Persistent Storage

Now run PostgreSQL 16 on `app-net` with `pgdata` mounted to `/var/lib/postgresql/data`. Notice I am not publishing port 5432 to the host—it only lives on `app-net`.

#### Commands:
```bash
docker run -d --name db --network app-net \
  -e POSTGRES_PASSWORD=changeme -e POSTGRES_DB=shop \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine

# Wait a second and verify it's ready
docker exec db pg_isready -U postgres
```

#### Terminal Output:
```bash
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker run -d --name db --network app-net \
  -e POSTGRES_PASSWORD=changeme -e POSTGRES_DB=shop \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine
Unable to find image 'postgres:16-alpine' locally
16-alpine: Pulling from library/postgres
509688edf37b: Pull complete 
a88782f92806: Pull complete 
81717818649a: Pull complete 
25b77f59fd95: Pull complete 
1b7f9cd581ee: Pull complete 
6117bd39f23f: Pull complete 
210b280f9556: Pull complete 
3ae6141cfd99: Pull complete 
d8d21be4bf02: Pull complete 
6c25da34e03f: Pull complete 
e6b147246a89: Download complete 
021b01ea4cc2: Download complete 
Digest: sha256:721873c34ceb9f8d8fc265984940dc982404c105f19ad51be9fdc5970a6080ea
Status: Downloaded newer image for postgres:16-alpine
bddef2b4ae476ea25562f80861bac06cf7e96cc1985dbd520baaabe33f6d91ab
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ sleep 3
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker exec db pg_isready -U postgres
/var/run/postgresql:5432 - accepting connections
```

#### My Observations:
- Docker pulled `postgres:16-alpine`, which is ultra-lightweight compared to the standard Debian-based Postgres image.
- `pg_isready -U postgres` returned `/var/run/postgresql:5432 - accepting connections`, confirming the database cluster initialized properly in our `pgdata` volume and is listening for queries.
- Port 5432 is not exposed on the host, meaning it is strictly reachable only by containers connected to `app-net`. 

---

### Task 3: Insert Data and Destroy the Container

Insert test records into database `shop`, verify they exist, and then violently delete the container using `docker rm -f`.

#### Commands:
```bash
# Create table and insert row
docker exec -it db psql -U postgres -d shop -c \
  "CREATE TABLE notes(id serial, msg text); INSERT INTO notes(msg) VALUES ('I survive');"

# Check row
docker exec db psql -U postgres -d shop -c "SELECT * FROM notes;"

# Delete the container
docker rm -f db
docker ps -a --filter "name=db"
```

#### Terminal Output:
```bash
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker exec -it db psql -U postgres -d shop -c \
  "CREATE TABLE notes(id serial, msg text); INSERT INTO notes(msg) VALUES ('I survive');"
CREATE TABLE
INSERT 0 1
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker exec db psql -U postgres -d shop -c "SELECT * FROM notes;"
 id |    msg    
----+-----------
  1 | I survive
(1 row)

hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker rm -f db
db
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker ps -a --filter "name=db"
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

#### My Observations:
- In Bash, single quotes `'I survive'` were needed because an unescaped exclamation mark inside double quotes triggers Bash history expansion (`event not found`).
- The `notes` table was created and the row `1 | I survive` was successfully committed to the database.
- Running `docker rm -f db` completely destroyed the container, PID namespaces, and its writable layer.
- `docker ps -a` confirms that the container is 100% gone, but the named volume `pgdata` remains intact on the host disk. 

---

### Task 4: Re-create Container and Verify Zero Data Loss

Re-create the `db` container with the same named volume `pgdata`. Query the table—the row must still be there.

#### Commands:
```bash
docker run -d --name db --network app-net \
  -e POSTGRES_PASSWORD=changeme \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine

# Give it 2 seconds to initialize
sleep 2
docker exec db pg_isready -U postgres

# Check if data survived
docker exec db psql -U postgres -d shop -c "SELECT * FROM notes;"
```

#### Terminal Output:
```bash
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker run -d --name db --network app-net \
  -e POSTGRES_PASSWORD=changeme \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine
a1764e1c795cfc51b289d218b4b99e73960ea5b3fbfc1691c68da65cb3ce1e55
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ sleep 2
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker exec db pg_isready -U postgres
/var/run/postgresql:5432 - accepting connections
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker exec db psql -U postgres -d shop -c "SELECT * FROM notes;"
 id |    msg    
----+-----------
  1 | I survive
(1 row)
```

#### My Observations:
- Re-running a container with `-v pgdata:/var/lib/postgresql/data` reattached the existing storage volume seamlessly.
- I didn't need to specify `-e POSTGRES_DB=shop` because PostgreSQL automatically detects existing catalog files in the volume and mounts the existing `shop` database.
- The SQL query returned `1 | I survive`, proving zero data loss despite the previous container being forcefully deleted. Volume persistence works as intended! 

---

### Task 5: Connect Second Container & Test DNS Resolution

Prove that a second container on `app-net` can query the database by the hostname `db`, and prove that a container on the default bridge fails.

#### Commands:
```bash
# 1. Connect client on app-net by name 'db'
docker run --rm -it --network app-net -e PGPASSWORD=changeme postgres:16-alpine \
  psql -h db -U postgres -d shop -c "SELECT count(*) FROM notes;"

# 2. Try pinging 'db' from default bridge (should fail)
docker run --rm alpine ping -c 1 db

# 3. Try pinging 'db' from app-net (should succeed)
docker run --rm --network app-net alpine ping -c 1 db
```

#### Terminal Output:
```bash
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker run --rm -it --network app-net -e PGPASSWORD=changeme postgres:16-alpine \
  psql -h db -U postgres -d shop -c "SELECT count(*) FROM notes;"
 count 
-------
     1
(1 row)

hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker run --rm alpine ping -c 1 db
Unable to find image 'alpine:latest' locally
latest: Pulling from library/alpine
797dd00a0fc7: Download complete 
6d0606d1815c: Download complete 
Digest: sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6
Status: Downloaded newer image for alpine:latest
ping: bad address 'db'

hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker run --rm --network app-net alpine ping -c 1 db
PING db (172.22.0.2): 56 data bytes
64 bytes from 172.22.0.2: seq=0 ttl=64 time=0.157 ms

--- db ping statistics ---
1 packets transmitted, 1 packets received, 0% packet loss
round-trip min/avg/max = 0.157/0.157/0.157 ms
```

#### My Observations:
- A client container connected to `app-net` easily queried the database using hostname `db` (`-h db`), receiving `count: 1`.
- When running `alpine ping -c 1 db` without specifying a network, the container defaulted to the standard `bridge` network (`docker0`) and failed with `ping: bad address 'db'`. This confirms that the default bridge network does NOT support automatic DNS name resolution.
- Running the exact same ping command with `--network app-net` resolved `db` to `172.22.0.2` in `0.157 ms`. This proves that user-defined bridge networks provide automatic service discovery via Docker's embedded DNS server (`127.0.0.11`). 

---

### Task 6: Backup & Restore Volume Using a Throwaway Container

To back up Docker volumes without needing root access to `/var/lib/docker/volumes`, I can run a temporary Alpine container that mounts both the volume and my current folder, creating a `.tgz` archive.

#### Commands:
```bash
# 1. Backup pgdata to tar archive
docker run --rm -v pgdata:/data -v $(pwd):/backup alpine \
  tar czf /backup/pgdata-backup.tgz -C /data .

ls -lh pgdata-backup.tgz

# 2. Restore into a new volume pgdata2
docker volume create pgdata2
docker run --rm -v pgdata2:/data -v $(pwd):/backup alpine \
  tar xzf /backup/pgdata-backup.tgz -C /data

# 3. Test restored volume
docker run --rm -d --name db2 --network app-net \
  -e POSTGRES_PASSWORD=changeme -v pgdata2:/var/lib/postgresql/data postgres:16-alpine

sleep 2
docker exec db2 psql -U postgres -d shop -c "SELECT * FROM notes;"
docker rm -f db2
```

#### Terminal Output:
```bash
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker run --rm -v pgdata:/data -v $(pwd):/backup alpine \
  tar czf /backup/pgdata-backup.tgz -C /data .
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ ls -lh pgdata-backup.tgz
-rw-r--r-- 1 root root 6.5M Oct 12 19:29 pgdata-backup.tgz
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker volume create pgdata2
pgdata2
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker run --rm -v pgdata2:/data -v $(pwd):/backup alpine \
  tar xzf /backup/pgdata-backup.tgz -C /data
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker run --rm -d --name db2 --network app-net \
  -e POSTGRES_PASSWORD=changeme -v pgdata2:/var/lib/postgresql/data postgres:16-alpine
7de65fd63f7b83059a9f47dcd65feb40855ebf29229a750f8b9e28d86fe63a41
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ sleep 3
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker exec db2 psql -U postgres -d shop -c "SELECT * FROM notes;"
 id |    msg    
----+-----------
  1 | I survive
(1 row)

hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker rm -f db2
db2
```

#### My Observations:
- Using a throwaway Alpine container allowed me to bypass host permission limits on `/var/lib/docker/volumes` and generate a `6.5 MB` compressed `.tgz` backup archive directly into my current directory.
- Restoring into a fresh named volume `pgdata2` via `tar xzf` and running test container `db2` proved 100% data fidelity (`1 | I survive`).
- This pattern provides a clean, portable backup/restore workflow for Docker volumes without needing direct root access to the host daemon storage directory. 

---

### Task 7: Port Conflict Drill

Simulate what happens when two containers try to bind to the same host port (`8080:80`), troubleshoot the error, and fix it.

#### Commands:
```bash
# Start first container on 8080
docker run -d --name w1 -p 8080:80 nginx:1.27-alpine

# Try to start second container on 8080 (fails)
docker run -d --name w2 -p 8080:80 nginx:1.27-alpine

# Check what owns port 8080
ss -tulpn | grep 8080

# Fix by remapping to port 8081
docker rm -f w2 2>/dev/null || true
docker run -d --name w2 -p 8081:80 nginx:1.27-alpine

# Verify both respond
curl -I http://localhost:8080 | head -n 1
curl -I http://localhost:8081 | head -n 1

# Cleanup web containers
docker rm -f w1 w2
```

#### Terminal Output:
```bash
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker run -d --name w1 -p 8080:80 nginx:1.27-alpine
Unable to find image 'nginx:1.27-alpine' locally
1.27-alpine: Pulling from library/nginx
34a64644b756: Pull complete 
39c2ddfd6010: Pull complete 
f18232174bc9: Pull complete 
197eb75867ef: Pull complete 
b464cfdf2a63: Pull complete 
81bd8ed7ec67: Pull complete 
61ca4f733c80: Pull complete 
d7e507024086: Pull complete 
2a84448aca9c: Download complete 
9261b9aff737: Download complete 
Digest: sha256:65645c7bb6a0661892a8b03b89d0743208a18dd2f3f17a54ef4b76fb8e2f2a10
Status: Downloaded newer image for nginx:1.27-alpine
610c4385fb283d0092ec3a80f63048db42984a011e05169f27a214a8c99cb158

hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker run -d --name w2 -p 8080:80 nginx:1.27-alpine
5df75cd3ca91b56823c18b8be943bd62e67297d40502d1eb7775771d473b9a41
docker: Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint w2 (27bd9c3100d8760cf7c19d3eb368f75c41b168c265af00b8787ddb31d3b5080c): Bind for 0.0.0.0:8080 failed: port is already allocated

hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ ss -tulpn | grep 8080
tcp   LISTEN 0      4096                                       0.0.0.0:8080       0.0.0.0:*                                               
tcp   LISTEN 0      4096                                          [::]:8080          [::]:*                                               

hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker rm -f w2 2>/dev/null || true
docker run -d --name w2 -p 8081:80 nginx:1.27-alpine
w2
bc3a594f5fc0ce639dd77ae53d5ae3127fef6f71cb98533b5d40b2a2164eb179

hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ curl -I http://localhost:8080 | head -n 1
HTTP/1.1 200 OK
hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ curl -I http://localhost:8081 | head -n 1
HTTP/1.1 200 OK

hrishav@hrishav-LOQ-15IAX9:~/day11-storage-network$ docker rm -f w1 w2
w1
w2
```

#### My Observations:
- Attempting to run `w2` on port `8080` triggered an immediate error: `driver failed programming external connectivity ... Bind for 0.0.0.0:8080 failed: port is already allocated`.
- Running `ss -tulpn | grep 8080` showed the host sockets in `LISTEN` state on IPv4 (`0.0.0.0:8080`) and IPv6 (`[::]:8080`).
- To fix the port collision, I removed the dead `w2` container and remapped it to host port `8081:80`.
- Both `curl -I http://localhost:8080` and `curl -I http://localhost:8081` returned `HTTP/1.1 200 OK`, proving two independent containers running the same service can coexist seamlessly by publishing to distinct host ports. 

---

## 🚨 Troubleshooting Notes

### 1. "could not translate host name 'db'"
- **Cause:** The client container is on the default bridge or a different network.
- **Fix:** Both containers must be on the same user-defined network (`--network app-net`).

### 2. "Bind for 0.0.0.0:8080 failed: port is already allocated"
- **Cause:** Another container or host process is already listening on port 8080.
- **Fix:** Run `ss -tulpn | grep 8080` or `docker ps` to find what owns it. Map to an unused port like `8081`.

### 3. Connection refused right after starting Postgres
- **Cause:** PostgreSQL takes 2-4 seconds to spin up and create its listening socket.
- **Fix:** Use `docker exec db pg_isready -U postgres` to verify readiness before running queries.

### 4. Changing `POSTGRES_PASSWORD` or `POSTGRES_DB` had no effect
- **Cause:** Postgres initialization scripts only run the first time a volume is empty. If data already exists, env vars are ignored.
- **Fix:** Run SQL queries directly with `psql` to alter passwords or databases on existing volumes.

---

## 🎤 Interview Questions & Key Takeaways

### Q1: What is the difference between a Volume and a Bind Mount?
- **Answer:** A named volume is completely managed by Docker inside `/var/lib/docker/volumes` and is best for databases and persistent production data. A bind mount maps an exact host folder into the container, which is best for local code development and mounting config files.

### Q2: Why can containers reach each other by name on a custom bridge, but not on the default bridge?
- **Answer:** User-defined bridge networks have Docker's built-in embedded DNS server enabled (listening on `127.0.0.11`), which automatically resolves container names to IP addresses. The default bridge (`docker0`) is legacy and does not provide automatic DNS resolution.

### Q3: What does `-p 8080:80` do under the hood?
- **Answer:** Docker configures Linux `iptables` NAT rules to forward incoming traffic from host port 8080 to the container IP on port 80, and runs `docker-proxy` on the host to route loopback traffic.

### Q4: What happens to data when you delete a container that used a named volume?
- **Answer:** The container and its writable layer are deleted, but the volume and all its stored data remain on the host until explicitly removed using `docker volume rm`.

### Q5: How do you troubleshoot "port is already allocated"?
- **Answer:** Run `ss -tulpn | grep <port>` or `docker ps` to find the process or container holding the port. Either stop the conflicting process or map your container to a free host port.

---

[← Day 10](Day10.md) | [Home](README.md)
