# DevOps Winter Arc — Day 11: Docker Storage & Custom Networking

> **90 Days of DevOps Challenge | Containers Week | Learn • Practice • Build**  
> **Topic: Data Persistence (Volumes vs Bind Mounts vs tmpfs), User-Defined Bridge Networks, Embedded DNS, Volume Backup/Restore, Port Conflict Troubleshooting**

---

## 🎯 Today's Goal

Welcome to **Day 11** of the DevOps Winter Arc!

Containers are designed by default to be ephemeral and disposable. In a stateless microservices world, if a container crashes or is deleted, its writable layer vanishes with it. But real-world infrastructure powers stateful workloads: relational databases (PostgreSQL, MySQL), key-value stores (Redis), message queues (RabbitMQ), and persistent storage volumes. 

Today's mission is twofold:
1. **Master Container Storage:** Guarantee that mission-critical application data survives container destruction and recreation using Docker **named volumes**.
2. **Master Container Networking:** Connect multiple independent containers on a private, isolated **user-defined bridge network** so they can discover and communicate with each other securely by name via Docker's embedded DNS—without exposing internal databases to the public host or internet.

---

### Production Scenario:
In our company's staging environment, a database container (`db`) was terminated during a rolling update, resulting in the total loss of development database records because the database was writing to the container's ephemeral writable layer. Concurrently, an API microservice failed to connect to the database because it attempted to use `localhost`, unaware that each container has its own network namespace and loopback adapter. Furthermore, a rogue deployment attempted to bind to port `8080` while another process had already claimed it, causing an immediate outage.

As a DevOps Engineer, our job today is to implement production-grade container storage and networking patterns, verify zero data loss across container deletions, validate embedded DNS resolution, perform volume disaster recovery (backup & restore), and troubleshoot host port conflicts.

---

### The Plan for Today:
1. **Deep Dive into Storage Mechanics:** Understand the architectural differences between Named Volumes, Bind Mounts, and `tmpfs`.
2. **Deep Dive into Docker Networking:** Compare Docker network drivers (`bridge`, `host`, `none`, `overlay`) and discover how Docker's embedded DNS resolver functions on user-defined bridges.
3. **Task 1: Infrastructure Setup:** Create the isolated custom bridge network (`app-net`) and named storage volume (`pgdata`).
4. **Task 2: Launch Stateful Service (PostgreSQL):** Run PostgreSQL attached to both the network and volume with secure runtime credentials.
5. **Task 3: Seed Data & The Destruction Test:** Insert database records into a `shop` database and violently destroy the container with `docker rm -f`.
6. **Task 4: Zero Data Loss Verification:** Recreate the database container with the original volume and prove the data survived intact.
7. **Task 5: Multi-Container Networking & DNS Scoping:** Connect a second container (`psql` / Alpine) to `app-net` and query the database using its container name (`db`), then demonstrate why the default bridge fails.
8. **Task 6: Volume Backup & Disaster Recovery:** Back up `pgdata` into a compressed `.tgz` archive using an ephemeral throw-away container, and restore it into a fresh volume (`pgdata2`).
9. **Task 7: Port Conflict & Troubleshooting Drill:** Intentionally trigger a host port collision (`0.0.0.0:8080`), diagnose the owning process with `ss -tulpn`, and resolve the bind error.
10. **Production Troubleshooting Matrix & Interview Readiness:** Document real-world failure patterns and review senior DevOps interview questions.

---

## 🗺️ Core Concepts & Architecture Deep Dive

### 1. Containers Are Disposable: Ephemeral vs Persistent Storage

When Docker runs a container from an image, it mounts the image's immutable read-only layers and stacks a thin **writable container layer** on top using an overlay filesystem (`overlay2`).

```
+-------------------------------------------------------+
| Container Writable Layer (Ephemeral - destroyed on rm) |  <-- All writes go here by default
+-------------------------------------------------------+
| Image Layer 3 (Read-Only)                             |
+-------------------------------------------------------+
| Image Layer 2 (Read-Only)                             |
+-------------------------------------------------------+
| Image Layer 1: Base OS (Read-Only)                    |
+-------------------------------------------------------+
```

If a database writes to `/var/lib/postgresql/data` inside this container layer, running `docker rm -f` deletes the container and permanently destroys the database files.

---

### 2. Storage Options: Named Volume vs Bind Mount vs tmpfs

Docker provides three mechanisms to mount data into a container:

```
+-----------------------------------------------------------------------------------------+
|                                    HOST LINUX SYSTEM                                    |
|                                                                                         |
|  +---------------------------+  +----------------------+  +--------------------------+  |
|  |   /var/lib/docker/volumes |  |   Any Host Path      |  |        Host RAM          |  |
|  |     (Docker Managed)      |  | (e.g. $(pwd)/code)   |  |     (Kernel Memory)      |  |
|  +-------------+-------------+  +----------+-----------+  +------------+-------------+  |
|                |                           |                           |                |
|         [ Named Volume ]             [ Bind Mount ]                [ tmpfs ]            |
|                |                           |                           |                |
|                v                           v                           v                |
|  +-----------------------------------------------------------------------------------+  |
|  |                                  CONTAINER                                        |  |
|  |     /var/lib/postgresql/data            /app/src                      /tmp/cache          |  |
|  +-----------------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------------+
```

| Dimension | Named Volume | Bind Mount | tmpfs Mount |
| :--- | :--- | :--- | :--- |
| **Storage Location** | `/var/lib/docker/volumes/<name>/_data` | Any path on the host filesystem (e.g., `$(pwd)`) | Host RAM memory only |
| **Lifecycle & Management** | Managed entirely by Docker CLI & daemon | Managed by host OS user / permissions | Erased when container stops |
| **Survives `docker rm`?** | **Yes** (independent lifecycle) | **Yes** (it is a standard host directory) | **No** (cleared from RAM) |
| **Portability** | High (decoupled from host paths) | Low (relies on host directory structure) | High (temporary RAM) |
| **Performance** | Native Linux I/O speed | Fast on Linux; slower on macOS/Windows VM | Maximum memory speed |
| **Best Used For** | Production databases, uploads, stateful data | Development live-reloading, mounting config files | Sensitive tokens, scratch buffers, in-memory caches |
| **Syntax Example** | `-v pgdata:/var/lib/postgresql/data` | `-v $(pwd)/html:/usr/share/nginx/html:ro` | `--tmpfs /tmp` |

---

### 3. Docker Network Drivers

Docker uses Linux network namespaces, virtual ethernet pairs (`veth`), and `iptables` / `nftables` to manage network isolation:

| Driver | Architecture & Mechanics | When to Use in Production |
| :--- | :--- | :--- |
| **`bridge` (Default)** | Creates `docker0` virtual bridge. Containers get `172.17.0.x` IPs and reach external networks via NAT (IP masquerade). **No automatic DNS resolution by container name.** | Quick one-off testing; legacy single-container setups. |
| **`bridge` (User-Defined)** | Dedicated virtual bridge per network. Containers get isolated subnet IPs and **automatic DNS resolution by container name**. | **Production default** for multi-container apps on a single Docker host. |
| **`host`** | Strips container network namespace isolation; container shares host network stack directly. No port publishing (`-p`) required. | Maximum throughput, low latency (e.g., network analyzers, high-frequency trade systems). Linux only. |
| **`none`** | Disables all networking. Container receives only a loopback interface (`127.0.0.1`). | Batch jobs, cryptographic signing, security-isolated offline processing. |
| **`overlay`** | Multi-host network fabric spanning multiple Docker hosts using VXLAN encapsulation. | Docker Swarm clusters (largely superseded by Kubernetes CNI plugins like Calico/Cilium). |

---

### 4. How Containers Communicate: Architecture & Embedded DNS

On a user-defined bridge network (such as `app-net`), Docker runs an embedded DNS server listening at `127.0.0.11` inside each container's `/etc/resolv.conf`. When container `api` queries `http://db:5432`, Docker DNS automatically resolves hostname `db` to the internal IP address of the `db` container.

```
========================================================================================
                          CUSTOM BRIDGE NETWORK: app-net (172.20.0.0/16)
========================================================================================

  HOST (Browser / Curl)
        |
        |  Host Port 8080 (Published: -p 8080:80)
        v
  +----------------------------------------------------------------------------------+
  |  CONTAINER: api (e.g., Python / Node / Client)                                   |
  |  IP: 172.20.0.3                                                                  |
  |                                                                                  |
  |  Resolves "db" -> 172.20.0.2 via 127.0.0.11 (Docker Embedded DNS)                |
  +----------------------------------------------------------------------------------+
        |
        |  Internal Communication: http://db:5432 (Port 5432 NOT published to Host!)
        v
  +----------------------------------------------------------------------------------+
  |  CONTAINER: db (PostgreSQL 16)                                                   |
  |  IP: 172.20.0.2                                                                  |
  |  Listening on internal port: 5432                                                |
  +----------------------------------------------------------------------------------+
        |
        |  Mounts persistent storage: /var/lib/postgresql/data
        v
  +----------------------------------------------------------------------------------+
  |  NAMED VOLUME: pgdata (/var/lib/docker/volumes/pgdata/_data)                     |
  |  Survives container removal (`docker rm -f db`)                                  |
  +----------------------------------------------------------------------------------+
========================================================================================
```

> [!IMPORTANT]
> **Network Security Best Practice:** Never publish internal database ports (`-p 5432:5432`) to the host or internet unless external direct access is strictly required. By keeping the database accessible **only** within `app-net`, the database is completely shielded from external port scans and brute force attacks.

---

### 5. Common DevOps Networking Pitfalls

1. **The `localhost` Misconception:** `localhost` inside a container refers to the container's *own* loopback network namespace, NOT the Docker host, and NOT sibling containers. To reach another container, use its container name (DNS).
2. **Default Bridge DNS Limitation:** Containers connected to the default `bridge` (`docker0`) cannot resolve each other by container name. Only user-defined bridge networks provide automatic DNS.
3. **Application Listening Address:** An application inside a container must listen on `0.0.0.0` (all interfaces), not `127.0.0.1`. If it listens on `127.0.0.1`, external traffic from the host or bridge network will be rejected.
4. **Port Binding Collisions:** Two containers cannot publish to the same host port on the same interface (e.g., two containers cannot both bind `-p 8080:80` on `0.0.0.0`).

---

## 🛠️ Command Reference Guide

### 💽 Volume Management
| Command | Purpose | Production Use Case |
| :--- | :--- | :--- |
| `docker volume create <name>` | Explicitly initializes a named volume | Pre-provision storage before launching database services. |
| `docker volume ls` | Lists all volumes on the host | Audit disk utilization and identify orphaned storage. |
| `docker volume inspect <name>` | Displays metadata, driver, and exact host mount point | Locate raw files under `/var/lib/docker/volumes/`. |
| `docker volume rm <name>` | Permanently deletes a named volume (**irreversible**) | Decommission retired workloads and clean disks. |
| `docker volume prune` | Deletes all volumes not mounted by any container | Reclaim host disk capacity after maintenance. |
| `docker run -v <name>:<path> <image>` | Mounts a named volume inside a container | Attach persistent storage to containers. |
| `docker run -v $(pwd):<path> <image>` | Mounts a host directory (bind mount) | Live application code development. |
| `docker run -v $(pwd)/conf:<path>:ro <image>` | Mounts host folder read-only (`:ro`) | Enforce immutability on configuration files. |

### 🌐 Network Management
| Command | Purpose | Production Use Case |
| :--- | :--- | :--- |
| `docker network ls` | Lists all local and custom networks | Check configured network drivers and scopes. |
| `docker network create <name>` | Creates an isolated user-defined bridge network | Establish security and DNS boundaries per application. |
| `docker network inspect <name>` | Shows subnet, gateway, and attached container IPs | Verify container IP allocations and connectivity. |
| `docker run --network <name> ...` | Spawns a container directly attached to a network | Place services into dedicated microservice tiers. |
| `docker network connect <net> <c>` | Attaches a running container to another network | Multi-homed containers (e.g., reverse proxy bridging tiers). |
| `docker network disconnect <net> <c>` | Detaches a container from a network | Isolate a compromised or misbehaving container. |
| `docker port <container>` | Displays active host-to-container port mappings | Verify published ports and interface bindings. |
| `docker network rm <name>` | Removes an empty custom network | Clean up temporary staging networks. |

### 🔍 Troubleshooting & Connectivity
| Command | Purpose | Production Use Case |
| :--- | :--- | :--- |
| `ss -tulpn \| grep <port>` | Identifies host PID and process owning a port | Troubleshoot `port is already allocated` errors. |
| `docker exec <c> ping -c 2 <target>` | Tests ICMP reachability and DNS resolution | Validate inter-container network paths. |
| `docker exec <c> nslookup <name>` | Queries embedded DNS (`127.0.0.11`) | Inspect container IP records returned by Docker. |
| `docker exec <c> curl -I <url>` | Tests HTTP connection and status headers | Verify microservice API reachability. |
| `docker exec <db> pg_isready -U <user>` | Checks if PostgreSQL is accepting queries | Readiness checks in CI/CD and deployment scripts. |
| `docker logs <container> --tail 50` | Streams container standard output and error | Diagnose crash loops and connection errors. |

---

## 🏗️ Hands-On Workspace Setup

Our dedicated lab workspace for Day 11 is located at:
```bash
~/day11-storage-network
```

```
day11-storage-network/
├── README.md               # Hands-on notes and verification logs
└── pgdata-backup.tgz       # Compressed backup archive of the PostgreSQL volume
```

---

## 📋 Step-by-Step Task Execution

### Task 1: Create Custom Bridge Network & Named Volume

Before launching containers, we create our isolated virtual network and storage volume.

#### Instructions:
1. Create the dedicated workspace directory `~/day11-storage-network`.
2. Create the user-defined bridge network named `app-net`.
3. Create the named volume named `pgdata`.
4. Inspect both resources to observe Docker's allocated subnet and host filesystem mount point.

#### Commands:
```bash
mkdir -p ~/day11-storage-network && cd ~/day11-storage-network
docker network create app-net
docker volume create pgdata
docker network ls
docker volume ls
docker volume inspect pgdata
```

#### Terminal Output:
```bash
# Paste your terminal output here
```

#### Student Observations:
- What driver is used by `app-net`?
- What is the host mount point path returned by `docker volume inspect pgdata`?

---

### Task 2: Launch Stateful Service (PostgreSQL 16) with Volume & Network

Launch a PostgreSQL container connected to `app-net` with `pgdata` mounted to `/var/lib/postgresql/data`.

#### Instructions:
1. Run `postgres:16-alpine` in detached mode named `db`.
2. Connect it to `app-net`.
3. Pass environment variables `POSTGRES_PASSWORD=changeme` and `POSTGRES_DB=shop`.
4. Mount volume `pgdata` at `/var/lib/postgresql/data`.
5. Check logs to confirm PostgreSQL initialized database cluster and is accepting connections.

#### Commands:
```bash
docker run -d --name db --network app-net \
  -e POSTGRES_PASSWORD=changeme -e POSTGRES_DB=shop \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine

# Verify container is running and healthy
docker ps --filter "name=db"
docker logs db --tail 20
docker exec db pg_isready -U postgres
```

#### Terminal Output:
```bash
# Paste your terminal output here
```

#### Student Observations:
- Did PostgreSQL report "database system is ready to accept connections"?
- Notice we did NOT use `-p 5432:5432`. Can processes on the host access port 5432 directly?

---

### Task 3: Insert Seed Data & Execute Container Annihilation Test

Simulate a production application inserting persistent records, then forcefully destroy the container.

#### Instructions:
1. Execute `psql` inside `db` to create a table `notes` in database `shop`.
2. Insert a record: `'I survive!'`.
3. Query the table to verify row insertion.
4. Execute `docker rm -f db` to violently kill and remove the running container.

#### Commands:
```bash
# Create table and insert record
docker exec -it db psql -U postgres -d shop -c \
  "CREATE TABLE notes(id serial, msg text); INSERT INTO notes(msg) VALUES ('I survive!');"

# Query record
docker exec db psql -U postgres -d shop -c "SELECT * FROM notes;"

# Destroy the container
docker rm -f db
docker ps -a --filter "name=db"
```

#### Terminal Output:
```bash
# Paste your terminal output here
```

#### Student Observations:
- Is container `db` present in `docker ps -a`?
- Did the named volume `pgdata` get deleted when the container was removed? Verify with `docker volume ls`.

---

### Task 4: Re-create Container with Volume & Verify Zero Data Loss

Re-create the PostgreSQL container attaching the same `pgdata` volume to prove data persistence.

#### Instructions:
1. Launch a brand-new container named `db` attaching to `app-net` and mounting `pgdata`.
2. Wait a few seconds for PostgreSQL to start.
3. Query the `notes` table in database `shop`—the row must still be present!

#### Commands:
```bash
docker run -d --name db --network app-net \
  -e POSTGRES_PASSWORD=changeme \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine

# Give Postgres 2-3 seconds to start, then verify readiness
sleep 3
docker exec db pg_isready -U postgres

# Query table to verify data survived
docker exec db psql -U postgres -d shop -c "SELECT * FROM notes;"
```

#### Terminal Output:
```bash
# Paste your terminal output here
```

#### Student Observations:
- Why did we not need to specify `-e POSTGRES_DB=shop` when re-creating the container? (Hint: See how Postgres initialization works with existing volumes).
- Did the row `'I survive!'` return intact?

---

### Task 5: Multi-Container Networking & DNS Scoping Drill

Prove that containers on the same user-defined network resolve each other by container name, while containers on other networks fail.

#### Instructions:
1. Run an ephemeral client container on `app-net` using `postgres:16-alpine` and connect to hostname `db` via `psql`.
2. Run a container on the default bridge network attempting to ping `db` (expected: DNS resolution failure).
3. Run a container on `app-net` pinging `db` (expected: success).

#### Commands:
```bash
# 1. Connect from client container on app-net using hostname 'db'
docker run --rm -it --network app-net -e PGPASSWORD=changeme postgres:16-alpine \
  psql -h db -U postgres -d shop -c "SELECT count(*) FROM notes;"

# 2. Test DNS resolution on default bridge (fails)
docker run --rm alpine ping -c 1 db

# 3. Test DNS resolution on user-defined bridge (succeeds)
docker run --rm --network app-net alpine ping -c 1 db
```

#### Terminal Output:
```bash
# Paste your terminal output here
```

#### Student Observations:
- What exact error does `docker run --rm alpine ping -c 1 db` return?
- Why does the second ping resolve instantly to the internal IP of container `db`?

---

### Task 6: Volume Backup & Disaster Recovery via Throwaway Container

In DevOps, named volumes live inside `/var/lib/docker/volumes`, which typically requires root privileges to browse. Learn the industry-standard pattern: attach an ephemeral container that mounts both the volume and the host current directory to create a tar archive.

#### Instructions:
1. Run an ephemeral Alpine container that mounts `pgdata` at `/data` and current host folder `$(pwd)` at `/backup`.
2. Tar and gzip `/data` into `/backup/pgdata-backup.tgz`.
3. Create a fresh volume `pgdata2`.
4. Restore the backup archive into `pgdata2`.
5. Launch a test database container using `pgdata2` to verify data recovery.

#### Commands:
```bash
# 1. Backup volume to compressed tar archive
docker run --rm -v pgdata:/data -v $(pwd):/backup alpine \
  tar czf /backup/pgdata-backup.tgz -C /data .

# 2. Inspect generated backup file
ls -lh pgdata-backup.tgz

# 3. Create fresh target volume
docker volume create pgdata2

# 4. Restore archive into new volume
docker run --rm -v pgdata2:/data -v $(pwd):/backup alpine \
  tar xzf /backup/pgdata-backup.tgz -C /data

# 5. Launch test container with restored volume to confirm integrity
docker run --rm -d --name db-restore --network app-net \
  -e POSTGRES_PASSWORD=changeme -v pgdata2:/var/lib/postgresql/data postgres:16-alpine
sleep 3
docker exec db-restore psql -U postgres -d shop -c "SELECT * FROM notes;"
docker rm -f db-restore
```

#### Terminal Output:
```bash
# Paste your terminal output here
```

#### Student Observations:
- What is the size of `pgdata-backup.tgz`?
- Did the restored volume `pgdata2` successfully serve the `notes` table?

---

### Task 7: Host Port Conflict & Connectivity Troubleshooting Drill

Simulate one of the most common production issues: attempting to bind to an already allocated host port.

#### Instructions:
1. Run container `w1` mapping host port `8080` to container port `80`.
2. Run container `w2` attempting to bind to the same host port `8080` (observe the bind error).
3. Identify the process/container holding port `8080` using `ss -tulpn` and `docker ps`.
4. Fix the collision by mapping `w2` to port `8081`.
5. Clean up the web containers.

#### Commands:
```bash
# 1. Run first web server on port 8080
docker run -d --name w1 -p 8080:80 nginx:1.27-alpine

# 2. Attempt to run second web server on same host port 8080 (fails)
docker run -d --name w2 -p 8080:80 nginx:1.27-alpine

# 3. Diagnose the conflict on the host
ss -tulpn | grep 8080
docker ps --filter "publish=8080"

# 4. Fix by choosing alternative available host port (8081)
docker rm -f w2 2>/dev/null || true
docker run -d --name w2 -p 8081:80 nginx:1.27-alpine

# 5. Verify both servers are reachable on the host
curl -s -I http://localhost:8080 | head -n 1
curl -s -I http://localhost:8081 | head -n 1

# Clean up web test containers
docker rm -f w1 w2
```

#### Terminal Output:
```bash
# Paste your terminal output here
```

#### Student Observations:
- What was the exact Docker error message when running `w2` on port `8080`?
- What process name appeared in `ss -tulpn`? (Hint: `docker-proxy`).

---

## 📋 Production Troubleshooting Matrix

| Issue / Error | Symptoms & Evidence | Root Cause | Fix / Solution | Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Data vanished after `docker rm`** | Database empty after re-running container. | Postgres data was written to container writable layer because `-v pgdata:...` was missing or path was misspelled. | Mount named volume to exact path `/var/lib/postgresql/data`. | Check `docker volume inspect pgdata` and query rows after container deletion. |
| **`could not translate host name "db"`** | Client fails with DNS resolution error. | Containers are on different networks or on the default bridge (`docker0`), which lacks embedded DNS. | Connect both containers to the same user-defined bridge (`--network app-net`). | Run `docker exec <client> nslookup db` or ping. |
| **`Bind for 0.0.0.0:8080 failed: port is already allocated`** | Container fails to start with bind error. | Another container or host process (Apache, Nginx, another app) is already listening on host port 8080. | Find owner with `ss -tulpn \| grep 8080` and `docker ps`. Remap to another port (e.g., `-p 8081:80`) or stop conflicting process. | Check `docker ps` and test with `curl http://localhost:8081`. |
| **Connection refused immediately after container start** | Client reports `Connection to db:5432 failed: Connection refused`. | Database process takes 2–5 seconds to perform internal initialization and start socket listener. | Add readiness loop using `pg_isready -U postgres` before executing application queries. | Run `docker exec db pg_isready -U postgres`. |
| **Environment variables ignored on existing volume** | Changing `POSTGRES_PASSWORD` or `POSTGRES_DB` does not affect database. | PostgreSQL initialization scripts in `/docker-entrypoint-initdb.d/` only execute once when the data directory is completely empty. | If schema/credential changes are needed, run SQL migration scripts via `psql` or wipe volume if in development. | Connect via `psql` and verify user/password. |

---

## 🧠 Senior DevOps Interview Questions & Architecture Answers

### 1. What is the fundamental difference between a Docker Volume and a Bind Mount?
- **Answer:** A **named volume** is created, managed, and isolated entirely within Docker's managed storage area (`/var/lib/docker/volumes/` on Linux). It has a lifecycle completely decoupled from any single container, works consistently across different host OS environments, and is the production standard for databases and persistent application state. A **bind mount** maps an arbitrary file or folder from the host filesystem directly into the container. It depends strictly on host paths and permissions, making it ideal for local development environments (live-reloading code) and mounting host configuration files (like `/etc/nginx/nginx.conf`).

### 2. Why can containers resolve each other by name on a custom bridge network, but fail on the default bridge?
- **Answer:** User-defined bridge networks instantiate Docker's built-in **embedded DNS server** (listening at IP `127.0.0.11` inside container namespaces). This DNS server dynamically maps container names and aliases to their assigned container IP addresses on that specific network. The legacy default `bridge` (`docker0`) was designed before embedded DNS was introduced; it relies only on static `/etc/hosts` entries linked via deprecated `--link` flags, and does not provide automatic dynamic name resolution.

### 3. What does `-p 8080:80` actually do under the hood in Linux?
- **Answer:** Under the hood, Docker performs two operations:
  1. It configures Linux **iptables / nftables** NAT rules in the `PREROUTING` and `DOCKER` chains to perform Destination NAT (DNAT), translating incoming packets on host port `8080` to the container's private IP on port `80`.
  2. It spawns a user-space daemon called `docker-proxy` bound to host port `8080` as a fallback mechanism to route traffic between host loopback and container namespaces.

### 4. Why is publishing an internal database port (`-p 5432:5432`) considered a serious security risk in production?
- **Answer:** Publishing port `5432` binds the database socket to all network interfaces (`0.0.0.0`), exposing it directly to the host's public IP address, VPC, and potentially the internet. This exposes the database to automated port scanning, brute-force attacks, and network-level denial of service. The secure production pattern is to attach the database exclusively to an internal custom network (`app-net`) without publishing ports (`-p`). Only trusted application services residing on the same network can reach the database port via internal DNS.

### 5. How do you back up and restore data stored in a Docker named volume without root access to `/var/lib/docker/volumes`?
- **Answer:** By launching an ephemeral throwaway container (e.g. `alpine`) that mounts both the source volume and a host directory, executes a tar backup, and exits:
  ```bash
  docker run --rm -v pgdata:/data -v $(pwd):/backup alpine tar czf /backup/pgdata.tgz -C /data .
  ```
  To restore, create a target volume and reverse the process using `tar xzf`:
  ```bash
  docker run --rm -v pgdata_new:/data -v $(pwd):/backup alpine tar xzf /backup/pgdata.tgz -C /data
  ```

---

## 💭 Reflection Questions (DevOps Engineer Perspective)

### 1. What proved that the PostgreSQL data survived container deletion?
- **Answer:** Running `docker rm -f db` completely destroyed the container, verified by `docker ps -a`. When a new container was created mounting the same `pgdata` volume, querying `SELECT * FROM notes;` immediately returned the row `'I survive!'`, proving the state was safely stored on the host's volume filesystem rather than the ephemeral container layer.

### 2. What happened when we tried to reach `db` from a container on the default bridge?
- **Answer:** `ping -c 1 db` failed with `ping: bad address 'db'`. Because the default bridge has no embedded DNS service, the container could not resolve the name `db` to an IP address.

### 3. How did we diagnose and resolve the host port conflict?
- **Answer:** Running `w2` on port `8080` failed with `Bind for 0.0.0.0:8080 failed: port is already allocated`. Running `ss -tulpn | grep 8080` revealed that `docker-proxy` owned port 8080 on behalf of container `w1`. We resolved the conflict by deleting the failed container and mapping `w2` to an unallocated host port (`-p 8081:80`).

---

## 📦 Required Deliverables & Verification Checklist

- [ ] Isolated user-defined bridge network `app-net` created.
- [ ] Persistent named volume `pgdata` created.
- [ ] PostgreSQL container `db` launched with volume and network.
- [ ] Table `notes` created and seeded with test record `'I survive!'`.
- [ ] Container `db` forcefully destroyed (`docker rm -f db`).
- [ ] Container re-created with volume and data persistence verified via SQL query.
- [ ] Inter-container DNS resolution verified using `psql` client container on `app-net`.
- [ ] DNS resolution failure verified on default bridge network.
- [ ] Volume backup archive `pgdata-backup.tgz` created via throwaway Alpine container.
- [ ] Backup restored into new volume `pgdata2` and verified.
- [ ] Host port conflict drill executed, diagnosed via `ss -tulpn`, and resolved with port `8081`.
- [ ] Final environment cleaned up.

---

[← Day 10](Day10.md) | [Home](README.md) | [Day 12 →](Day12.md)
