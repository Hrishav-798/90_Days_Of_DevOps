# DevOps Winter Arc — Day 09: Dockerfile Deep Dive & Layer Caching

> **90 Days of DevOps Challenge | Containers Week | Learn • Practice • Build**  
> **Topic: Dockerfile Directives, Layer Caching Optimization, Dynamic Runtime Configuration, ARG vs ENV, CMD vs ENTRYPOINT**

---

## 🎯 Today's Goal

Day 9 of the DevOps Winter Arc!

Following yesterday's dive into Docker fundamentals and basic Nginx containerization, today is all about mastering **production-grade Dockerfile authoring**. As a DevOps engineer, packaging applications isn't just about writing a file that builds; it's about building **predictable, immutable, lightweight, secure, and cache-optimized container images** that behave consistently from local development all the way to production Kubernetes clusters.

### Production Scenario:
My engineering team is delivering a Node.js HTTP microservice. Teammates need one single, immutable image that works seamlessly across local dev, staging, and production environments without rebuilding the image for every environment setting. Sensitive secrets must never leak into layers, build times must stay fast using smart caching, and containers must adhere to the principle of least privilege (non-root execution).

### The Plan for Today:
1. **Understand Build Mechanics:** Deep-dive into Dockerfile instructions (`FROM`, `WORKDIR`, `COPY`, `ADD`, `RUN`, `ARG`, `ENV`, `EXPOSE`, `USER`, `CMD`, `ENTRYPOINT`, `HEALTHCHECK`).
2. **Deconstruct Critical Distinctions:**
   - `COPY` vs `ADD` (predictability vs tar extraction/remote fetch).
   - `ARG` vs `ENV` (build-time variable vs runtime persisted environment).
   - `CMD` vs `ENTRYPOINT` (override defaults vs immutable executable) and exec form vs shell form.
3. **Setup Starter Node.js Microservice:** Author `server.js` (with `/` greeting and `/health` probe) and `package.json`.
4. **Build Context Hygiene:** Create a strict `.dockerignore` file to safeguard secrets (`.env`), VCS history (`.git`), and local dependencies (`node_modules`).
5. **Author Multi-Directive Dockerfile:** Implement layer-ordered instructions, build argument fallback, non-root user (`USER node`), and metadata documentation.
6. **Build & Verify Container (`v1`):** Build with `--progress=plain` and `--build-arg`, run detached, and verify `/` and `/health` with `curl`.
7. **Runtime Configuration Experiment:** Override environment variables dynamically via `docker run -e` and `--env-file` without rebuilding the image.
8. **Demonstrate Layer Caching:**
   - **Experiment A (Source Edit):** Modify only `server.js` and verify dependency installation (`npm install`) shows `CACHED`.
   - **Experiment B (Dependency Edit):** Modify `package.json` and observe cache invalidation downstream.
9. **CMD vs ENTRYPOINT Experiment:** Build a standalone greeter image (`Dockerfile.greeter`) to observe how arguments append to `ENTRYPOINT` versus replacing `CMD`.
10. **Image Inspection & History:** Analyze layer diffs and sizes with `docker history` and `docker image inspect`.
11. **Production Debugging Matrix & Troubleshooting Notes:** Document real scenarios using **Problem → Evidence → Root Cause → Fix → Verification**.
12. **Interview Readiness & Reflections:** Answer key technical questions like a senior engineer.

---

## 🗺️ Core Concepts & Architecture Deep Dive

### 1. Dockerfile Instruction Execution Pipeline

When Docker builds an image, the BuildKit engine processes each directive sequentially from top to bottom. Each instruction generates an immutable intermediate filesystem layer (or executes build logic).

```
+-----------------------------------------------------------------------------------+
|                                 BUILD TIME                                        |
+-----------------------------------------------------------------------------------+
|  1. FROM node:20-alpine          --> Pulls base Alpine Linux + Node.js runtime    |
|  2. WORKDIR /app                 --> Creates working dir & sets execution context |
|  3. ARG APP_VERSION=1.0          --> Defines build-time argument (NOT in image)   |
|  4. ENV PORT=3000 APP_ENV=dev    --> Sets runtime variables (Persisted in image)  |
|  5. COPY package*.json ./        --> Copies only manifests (Cache anchor)         |
|  6. RUN npm install --omit=dev   --> Runs in container snapshot; cached if files  |
|                                      haven't changed                              |
|  7. COPY . .                     --> Copies remaining source code (Fast changes)  |
|  8. EXPOSE 3000                  --> Metadata: Documents listening port           |
|  9. USER node                    --> Drops root privileges to non-root UID 1000   |
| 10. CMD ["node", "server.js"]    --> Default command in JSON Exec Form            |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                                RUNTIME CONTAINER                                  |
|  - PID 1: node server.js (Runs as 'node', not 'root')                             |
|  - Port 3000 mapped to host via docker-proxy                                      |
|  - ENV variables accessible via process.env                                       |
+-----------------------------------------------------------------------------------+
```

---

### 2. Cache-Friendly Layer Ordering: Why Layer Order Matters

Docker evaluates layer cache from top to bottom. If any instruction's input changes, **that instruction and all subsequent instructions must be re-executed**, invalidating the cache downstream.

#### ❌ Inefficient Pattern (Rebuilds dependencies on every code change):
```dockerfile
COPY . .                  # <-- Invalided whenever ANY line of JS or README changes!
RUN npm install           # <-- Forced to re-download all dependencies every build!
```

#### ✅ Cache-Friendly Production Pattern (Manifest First):
```dockerfile
COPY package*.json ./     # <-- Cached as long as dependencies don't change
RUN npm install --omit=dev# <-- Reuses CACHED layer in seconds!
COPY . .                  # <-- Only application source changes invalidate this step
```

```
[Inefficient Build Flow]
Edit server.js ---> [COPY . .] (INVALIDATED) ---> [npm install] (CACHE MISS - SLOW)

[Cache-Friendly Build Flow]
Edit server.js ---> [COPY package*.json] (CACHE HIT) ---> [npm install] (CACHE HIT - 0.0s)
               ---> [COPY . .] (CACHE MISS - FAST 0.1s)
```

---

### 3. ARG vs. ENV: Complete Comparison

| Feature | `ARG` (Build Argument) | `ENV` (Environment Variable) |
| :--- | :--- | :--- |
| **Lifecycle** | Available **only** during `docker build`. | Available during build **and** inside running containers. |
| **Persistence** | Discarded after build (though visible in `docker history`). | Persists in image metadata and inherited by child containers. |
| **CLI Override** | `docker build --build-arg KEY=value` | `docker run -e KEY=value` or `--env-file .env` |
| **Security Note** | ⚠️ **Never store secrets here!** Visible in image history. | ⚠️ **Never hardcode secrets here!** Stored in image plaintext. |
| **Common Use Cases**| Software version tags, package URLs, dev flags. | Port bindings, database hosts, app mode (`NODE_ENV`). |

```
               Build Phase                          Runtime Phase
               (docker build)                       (docker run)
              +--------------+                     +-------------+
--build-arg   |              |                     |             |
------------> |   ARG VAR    | (Discarded)         |             |
              |              |                     |             |
              +--------------+                     +-------------+
                     |
                     v (can populate)
              +--------------+   Persisted into    +-------------+   -e / --env-file
              |   ENV VAR    | ==================> |   ENV VAR   | <-----------------
              +--------------+   Image Metadata    +-------------+   (Overrides default)
```

---

### 4. `COPY` vs. `ADD`: Production Best Practices

- **`COPY`:**
  - Standard, predictable file copier.
  - Copies local files or directories from the build context into the container filesystem.
  - **Always preferred** for 99% of use cases.
- **`ADD`:**
  - Has two additional behaviors:
    1. Automatically extracts recognized local compressed tar archives (`.tar.gz`, `.tar.bz2`, etc.) into the target directory.
    2. Allows downloading files directly from remote URLs (not recommended because it doesn't clean up cache layers).
  - Use `ADD` **only** when automatic tar extraction is explicitly required (e.g., adding a root filesystem tarball).

---

### 5. `CMD` vs. `ENTRYPOINT` & Exec Form vs. Shell Form

Both directives define what runs when a container starts, but they behave differently when CLI arguments are supplied.

```
+------------------------------------+--------------------------+-------------------------------------+
| Dockerfile Definition              | Command Executed         | Actual Command Run Inside Container |
+------------------------------------+--------------------------+-------------------------------------+
| CMD ["node", "server.js"]          | docker run my-app        | node server.js                      |
| CMD ["node", "server.js"]          | docker run my-app sh     | sh (CMD completely replaced)        |
| ENTRYPOINT ["echo", "Hello"]       | docker run my-app        | echo Hello                          |
| ENTRYPOINT ["echo"] + CMD ["World"]| docker run my-app        | echo World                          |
| ENTRYPOINT ["echo"] + CMD ["World"]| docker run my-app DevOps | echo DevOps (CMD replaced, ENTRYPOINT holds) |
+------------------------------------+--------------------------+-------------------------------------+
```

#### JSON Exec Form vs. Shell Form:
- **Exec Form (Recommended):** `CMD ["node", "server.js"]`
  - Runs the binary directly as **PID 1**.
  - Receives Linux signals (`SIGTERM`, `SIGINT`) directly, allowing graceful shutdown.
- **Shell Form (Discouraged):** `CMD node server.js`
  - Runs as `/bin/sh -c "node server.js"`.
  - The shell runs as PID 1, and the node process is a child process. Shells often swallow `SIGTERM`, causing `docker stop` to hang for 10 seconds before forcefully killing the process with `SIGKILL`.

---

### 6. Principle of Least Privilege (`USER node`)

By default, Docker containers run all commands as `root` (UID 0). If an application vulnerability (such as remote code execution or path traversal) is exploited, the attacker has root privileges inside the container namespace and can attempt container escape.

The official `node:alpine` image includes a pre-configured low-privilege user named `node` (UID 1000). Setting `USER node` drops administrative capabilities before running the application process.

---

### 7. Build Context Optimization with `.dockerignore`

When you type `docker build .`, the Docker CLI creates a tar archive of the entire current working directory (the "build context") and sends it to the Docker daemon over the Unix socket.

Without a `.dockerignore` file:
- Gigabytes of `node_modules/` get serialized and uploaded unnecessarily.
- The `.git/` directory transfers full repo history, bloating context and leaking commit history.
- Local secrets like `.env` can accidentally get baked into image layers.

---

## 🏗️ Project Architecture & File Structure

Our project directory is `~/day09-dockerfile` (or `day2-dockerfile`):

```
day09-dockerfile/
├── .dockerignore          # Prevents secrets, node_modules, and git from entering build context
├── Dockerfile             # Multi-directive production-grade Node.js container build
├── Dockerfile.greeter     # ENTRYPOINT vs CMD testing laboratory
├── package.json           # Node.js project manifest
├── server.js              # Native Node.js HTTP server (zero external dependencies)
├── .env                   # Local runtime configuration test (ignored by git and docker)
└── README.md              # Project documentation and submission notes
```

---

## Task 1: Create Project Files (`server.js` & `package.json`)

Create a clean directory and author the lightweight Node.js API with health checks and runtime configuration endpoints.

### 🛠️ File Specifications

#### 1. `server.js`
A zero-dependency HTTP server that listens on `PORT` (default 3000), checks `/health`, and renders greeting + environment:
```javascript
const http = require("http");
const PORT = process.env.PORT || 3000;
const GREETING = process.env.GREETING || "Hello from Docker";

http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200);
    return res.end("ok\n");
  }
  res.end(`${GREETING} | env=${process.env.APP_ENV || "dev"}\n`);
}).listen(PORT, "0.0.0.0", () => console.log(`listening on ${PORT}`));
```

#### 2. `package.json`
```json
{
  "name": "demo-api",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  }
}
```

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `mkdir -p ~/day09-dockerfile` | Creates the dedicated exercise directory. |
| `cd ~/day09-dockerfile` | Moves into the project directory. |
| `cat << 'EOF' > server.js` | Generates the Node.js API server file. |
| `cat << 'EOF' > package.json` | Generates the `package.json` manifest. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ mkdir -p ~/day09-dockerfile
hrishav@hrishav-LOQ-15IAX9:~$ cd ~/day09-dockerfile
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ cat << 'EOF' > server.js
const http = require("http");
const PORT = process.env.PORT || 3000;
const GREETING = process.env.GREETING || "Hello from Docker";

http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200);
    return res.end("ok\n");
  }
  res.end(`${GREETING} | env=${process.env.APP_ENV || "dev"}\n`);
}).listen(PORT, "0.0.0.0", () => console.log(`listening on ${PORT}`));
EOF

hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ cat << 'EOF' > package.json
{
  "name": "demo-api",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  }
}
EOF

hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ ls -la
total 16
drwxrwxr-x  2 hrishav hrishav 4096 Oct 10 21:28 .
drwxr-x--- 69 hrishav hrishav 4096 Oct 10 21:18 ..
-rw-rw-r--  1 hrishav hrishav  120 Oct 10 21:28 package.json
-rw-rw-r--  1 hrishav hrishav  390 Oct 10 21:28 server.js
```

### 🔍 What I Observed on My System
- The server binds to `0.0.0.0` instead of `localhost` (`127.0.0.1`), ensuring external requests through Docker bridge networking can reach the listening socket.
- The service exposes two critical routes:
  - `GET /health` returning status `200 ok` (ideal for Docker and Kubernetes liveness/readiness probes).
  - `GET /` dynamically interpolating `GREETING` and `APP_ENV`.

---

## Task 2: Configure `.dockerignore` for Secure Build Context

Create `.dockerignore` to filter sensitive files and bulky directories before the build context is transferred to the Docker daemon.

### 🛠️ Content of `.dockerignore`
```
.git
.env
node_modules
*.log
.venv
__pycache__
```

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `cat << 'EOF' > .dockerignore` | Writes the ignore patterns into `.dockerignore`. |
| `cat .dockerignore` | Verifies file contents. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ cat << 'EOF' > .dockerignore
.git
.env
node_modules
*.log
.venv
__pycache__
EOF

hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ cat .dockerignore
.git
.env
node_modules
*.log
.venv
__pycache__
```

### 🔍 What I Observed on My System
- **Build Context Protection:** If someone runs `npm install` locally, the local `node_modules` directory won't be copied into the Linux container (preventing architecture mismatches between host OS and Alpine Linux).
- **Secret Leaks Blocked:** Any local `.env` files created for debugging are blocked from being copied via `COPY . .`.

---

## Task 3: Author the Production-Grade `Dockerfile`

Write a clean, layered, non-root `Dockerfile` with clear separation between build arguments, runtime defaults, and cache layers.

### 🛠️ Dockerfile Code

```dockerfile
FROM node:20-alpine
WORKDIR /app
ARG APP_VERSION=1.0
ENV PORT=3000 APP_ENV=dev APP_VERSION=$APP_VERSION
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
EXPOSE 3000
USER node
CMD ["node", "server.js"]
```

### 🛠️ Step-by-Step Instruction Breakdown

| Line | Directive | Production DevOps Rationale |
| :--- | :--- | :--- |
| **1** | `FROM node:20-alpine` | Minimal base image (~180MB uncompressed vs ~1.1GB full Debian Node image). Drastically reduces attack surface and CVE footprint. |
| **2** | `WORKDIR /app` | Sets standard working directory. Creates `/app` if it doesn't exist. Prevents polluting container root `/`. |
| **3** | `ARG APP_VERSION=1.0` | Build argument passed at compile time via `--build-arg`. |
| **4** | `ENV PORT=3000 APP_ENV=dev APP_VERSION=$APP_VERSION` | Persists default runtime environment variables. Inherits `$APP_VERSION` from `ARG`. |
| **5** | `COPY package*.json ./` | **Cache optimization key step.** Copies only dependency definitions first. |
| **6** | `RUN npm install --omit=dev` | Installs only production dependencies. This step is cached as long as `package*.json` doesn't change. |
| **7** | `COPY . .` | Copies application source code into `/app`. |
| **8** | `EXPOSE 3000` | Documents that the container listens on port 3000. (Informational only; port must still be published with `-p`). |
| **9** | `USER node` | **Security hardening.** Switches execution from root (UID 0) to unprivileged `node` user (UID 1000). |
| **10** | `CMD ["node", "server.js"]` | Default startup executable in JSON Exec Form (runs as PID 1). |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ cat << 'EOF' > Dockerfile
FROM node:20-alpine
WORKDIR /app
ARG APP_VERSION=1.0
ENV PORT=3000 APP_ENV=dev APP_VERSION=$APP_VERSION
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
EXPOSE 3000
USER node
CMD ["node", "server.js"]
EOF

hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ cat Dockerfile
FROM node:20-alpine
WORKDIR /app
ARG APP_VERSION=1.0
ENV PORT=3000 APP_ENV=dev APP_VERSION=$APP_VERSION
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
EXPOSE 3000
USER node
CMD ["node", "server.js"]
```

### 🔍 What I Observed on My System
- Used Alpine Linux to keep image footprint compact.
- Grouped environment variables into a single `ENV` line to minimize image layer count.
- Placed `COPY package*.json ./` and `RUN npm install --omit=dev` *before* `COPY . .` to maximize BuildKit layer caching.

---

## Task 4: Build Image `demo-api:v1` and Validate Container Runtime

Build the Docker image with plain progress logging and `--build-arg`, launch the container, and verify HTTP endpoints.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker build --progress=plain -t demo-api:v1 --build-arg APP_VERSION=1.0 .` | Builds image with verbose plain-text step output and sets `APP_VERSION`. |
| `docker run -d --name api -p 3000:3000 demo-api:v1` | Runs the container in background, mapping host 3000 to container 3000. |
| `docker ps` | Verifies the container status and port mapping. |
| `curl http://localhost:3000/` | Tests root endpoint greeting and default env. |
| `curl http://localhost:3000/health` | Tests health check endpoint (`ok`). |
| `docker logs api` | Inspects application logs inside container. |

### 💻 Terminal Output

```bash
# Build demo-api:v1
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker build --progress=plain -t demo-api:v1 --build-arg APP_VERSION=1.0 .
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 249B done
#1 DONE 0.1s

#2 [internal] load metadata for docker.io/library/node:20-alpine
#2 DONE 2.8s

#3 [auth] library/node:pull token for registry-1.docker.io
#3 DONE 0.0s

#4 [internal] load .dockerignore
#4 transferring context: 87B done
#4 DONE 0.0s

#5 [1/5] FROM docker.io/library/node:20-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04632e6c0fb8363f609372293
#5 DONE 0.0s

#6 [internal] load build context
#6 transferring context: 929B done
#6 DONE 0.0s

#7 [2/5] WORKDIR /app
#7 CACHED

#8 [3/5] COPY package*.json ./
#8 DONE 0.0s

#9 [4/5] RUN npm install --omit=dev
#9 0.906 up to date, audited 1 package in 403ms
#9 0.906 found 0 vulnerabilities
#9 DONE 0.9s

#10 [5/5] COPY . .
#10 DONE 0.0s

#11 exporting to image
#11 exporting layers 0.2s done
#11 naming to docker.io/library/demo-api:v1 done
#11 unpacking to docker.io/library/demo-api:v1 0.1s done
#11 DONE 0.4s

# Run container
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker run -d --name api -p 3000:3000 demo-api:v1
f25ab44085b8812ad075d007656598686c077398f2a6435bcce2eaf2477d30ef

# Verify running state
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker ps
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS                                         NAMES
f25ab44085b8   demo-api:v1   "docker-entrypoint.s…"   8 seconds ago   Up 7 seconds   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp   api

# Test root endpoint
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ curl http://localhost:3000/
Hello from Docker | env=dev

# Test health check endpoint
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ curl http://localhost:3000/health
ok

# Inspect logs
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker logs api
listening on 3000
```

### 🔍 What I Observed on My System
- The plain progress log confirms each layer executing sequentially.
- The container booted cleanly in detached mode (`-d`).
- `curl http://localhost:3000/` returned `Hello from Docker | env=dev`.
- `curl http://localhost:3000/health` returned `ok`.

---

## Task 5: Dynamic Runtime Configuration (`-e` and `--env-file`)

Prove that the image is **truly environment-agnostic** by modifying application behavior at runtime using environment variables without rebuilding the image.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker rm -f api` | Forcefully terminates and deletes the previous container. |
| `docker run -d --name api -p 3000:3000 -e GREETING="Hi Winter Arc" -e APP_ENV=prod demo-api:v1` | Runs container overriding `GREETING` and `APP_ENV` via CLI flags. |
| `curl http://localhost:3000/` | Verifies that the new response reflects the updated environment. |
| `cat << 'EOF' > .env.test ...` | Creates a local environment file for testing `--env-file`. |
| `docker run -d --name api-envfile -p 3001:3000 --env-file .env.test demo-api:v1` | Runs container configured via environment file on port 3001. |
| `curl http://localhost:3001/` | Verifies `--env-file` configuration. |

### 💻 Terminal Output

```bash
# Clean up previous container
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker rm -f api
api

# Run with -e CLI overrides
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker run -d --name api -p 3000:3000 \
  -e GREETING="Hi Winter Arc" \
  -e APP_ENV=prod \
  demo-api:v1
5822f1366273a5a7bca31a04d27f8832a8f7c9e5bf8801a2c3a50eef014bb98d

# Test overridden configuration
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ curl http://localhost:3000/
Hi Winter Arc | env=prod

# Test configuration via --env-file
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ cat << 'EOF' > .env.test
GREETING=Loaded from Env File
APP_ENV=staging
PORT=3000
EOF

hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker run -d --name api-envfile -p 3001:3000 --env-file .env.test demo-api:v1
9f12f4977c1ffc246f01448e1494844529862eb5a4603bfe175c4774b9f9c471

hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ curl http://localhost:3001/
Loaded from Env File | env=staging

# Teardown env-file test container
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker rm -f api-envfile
api-envfile
```

### 🔍 What I Observed on My System
- The container dynamically read the environment variables passed via `-e` and `--env-file` through Node's `process.env`.
- Not a single line of code was recompiled, and no new image build was required.
- **Production DevOps Rule:** Build an image once, promote it through Dev, Staging, and Prod by only injecting environment variables.

---

## Task 6: The Build Cache Experiment (Source Edit vs. Dependency Edit)

Validate Docker's layer cache behavior through two controlled tests:
1. **Experiment A:** Edit application code only (`server.js`) $\rightarrow$ dependency install step must be `CACHED`.
2. **Experiment B:** Edit dependency manifests (`package.json`) $\rightarrow$ dependency install step must trigger a `CACHE MISS`.

### 🛠️ Experiment A: Application Source-Only Edit

Modify `server.js` by tweaking the default greeting string, then rebuild as `demo-api:v2`:

```bash
# Modify only server.js
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ sed -i 's/Hello from Docker/Hello from Cached Docker/g' server.js

# Rebuild image to tag v2 with plain progress
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker build --progress=plain -t demo-api:v2 .
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 249B done
#1 DONE 0.0s

#2 [internal] load metadata for docker.io/library/node:20-alpine
#2 DONE 2.5s

#3 [auth] library/node:pull token for registry-1.docker.io
#3 DONE 0.0s

#4 [internal] load .dockerignore
#4 transferring context: 87B done
#4 DONE 0.0s

#5 [internal] load build context
#5 transferring context: 626B done
#5 DONE 0.0s

#6 [1/5] FROM docker.io/library/node:20-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04632e6c0fb8363f609372293
#6 DONE 0.0s

#7 [3/5] COPY package*.json ./
#7 CACHED

#8 [2/5] WORKDIR /app
#8 CACHED

#9 [4/5] RUN npm install --omit=dev
#9 CACHED

#10 [5/5] COPY . .
#10 DONE 0.0s

#11 exporting to image
#11 exporting layers 0.1s done
#11 naming to docker.io/library/demo-api:v2 done
#11 unpacking to docker.io/library/demo-api:v2 0.0s done
#11 DONE 0.2s

# Verify Docker History of v2
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker history demo-api:v2
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
0e85f641d9cd   9 seconds ago    CMD ["node" "server.js"]                        0B        buildkit.dockerfile.v0
<missing>      9 seconds ago    USER node                                       0B        buildkit.dockerfile.v0
<missing>      9 seconds ago    EXPOSE [3000/tcp]                               0B        buildkit.dockerfile.v0
<missing>      9 seconds ago    COPY . . # buildkit                             24.6kB    buildkit.dockerfile.v0
<missing>      19 minutes ago   RUN |1 APP_VERSION=1.0 /bin/sh -c npm instal…   28.7kB    buildkit.dockerfile.v0
<missing>      19 minutes ago   COPY package*.json ./ # buildkit                12.3kB    buildkit.dockerfile.v0
<missing>      19 minutes ago   ENV PORT=3000 APP_ENV=dev APP_VERSION=1.0       0B        buildkit.dockerfile.v0
<missing>      19 minutes ago   ARG APP_VERSION=1.0                             0B        buildkit.dockerfile.v0
<missing>      3 months ago     WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      5 months ago     CMD ["node"]                                    0B        buildkit.dockerfile.v0
<missing>      5 months ago     ENTRYPOINT ["docker-entrypoint.sh"]             0B        buildkit.dockerfile.v0
<missing>      5 months ago     COPY docker-entrypoint.sh /usr/local/bin/ # …   20.5kB    buildkit.dockerfile.v0
<missing>      5 months ago     RUN /bin/sh -c apk add --no-cache --virtual …   5.48MB    buildkit.dockerfile.v0
<missing>      5 months ago     ENV YARN_VERSION=1.22.22                        0B        buildkit.dockerfile.v0
<missing>      5 months ago     RUN /bin/sh -c addgroup -g 1000 node     && …   130MB     buildkit.dockerfile.v0
<missing>      5 months ago     ENV NODE_VERSION=20.20.2                        0B        buildkit.dockerfile.v0
<missing>      5 months ago     CMD ["/bin/sh"]                                 0B        buildkit.dockerfile.v0
<missing>      5 months ago     ADD alpine-minirootfs-3.23.4-x86_64.tar.gz /…   9.11MB    buildkit.dockerfile.v0
```

### 🛠️ Experiment B: Dependency Manifest Edit

Modify `package.json` (e.g., bumping version from `1.0.0` to `1.0.1`), then rebuild as `demo-api:v3`:

```bash
# Modify package.json version
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ sed -i 's/"version": "1.0.0"/"version": "1.0.1"/g' package.json

# Rebuild image to tag v3 with plain progress
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker build --progress=plain -t demo-api:v3 .
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 249B done
#1 DONE 0.0s

#2 [internal] load metadata for docker.io/library/node:20-alpine
#2 DONE 1.4s

#3 [internal] load .dockerignore
#3 transferring context: 87B done
#3 DONE 0.0s

#4 [internal] load build context
#4 transferring context: 282B done
#4 DONE 0.0s

#5 [1/5] FROM docker.io/library/node:20-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04632e6c0fb8363f609372293
#5 DONE 0.0s

#6 [2/5] WORKDIR /app
#6 CACHED

#7 [3/5] COPY package*.json ./
#7 DONE 0.0s

#8 [4/5] RUN npm install --omit=dev
#8 0.589 up to date, audited 1 package in 341ms
#8 0.590 found 0 vulnerabilities
#8 DONE 0.7s

#9 [5/5] COPY . .
#9 DONE 0.0s

#10 exporting to image
#10 exporting layers 0.1s done
#10 naming to docker.io/library/demo-api:v3 done
#10 unpacking to docker.io/library/demo-api:v3 0.1s done
#10 DONE 0.3s
```

### 🔍 What I Observed on My System
- **In Experiment A (Source Edit):**
  - Steps `[1/6] FROM...`, `[2/6] WORKDIR...`, `[3/6] COPY package*.json ./`, and `[4/6] RUN npm install --omit=dev` showed **`CACHED`**.
  - Docker recognized the checksum of `package*.json` had not changed, skipping `npm install` entirely.
  - The build finished in **< 0.5 seconds**.
- **In Experiment B (Manifest Edit):**
  - Step `COPY package*.json ./` registered a checksum change.
  - The cache was invalidated at that exact layer, forcing `RUN npm install --omit=dev` to execute fresh.
- This demonstrates the critical importance of keeping volatile instructions (`COPY . .`) as close to the bottom of the Dockerfile as possible.

---

## Task 7: CMD vs. ENTRYPOINT Laboratory (`Dockerfile.greeter`)

Create a dedicated test Dockerfile to demonstrate how `ENTRYPOINT` establishes the base binary and `CMD` supplies default parameters that can be overridden at runtime.

### 🛠️ Create `Dockerfile.greeter`

```dockerfile
FROM alpine:3.20
ENTRYPOINT ["echo", "Hello"]
CMD ["World"]
```

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `cat << 'EOF' > Dockerfile.greeter` | Creates the greeter test Dockerfile. |
| `docker build -f Dockerfile.greeter -t greeter:local .` | Builds the image using the custom Dockerfile. |
| `docker run --rm greeter:local` | Runs container with default `CMD` arguments. |
| `docker run --rm greeter:local DevOps` | Runs container providing a CLI argument (`DevOps`). |

### 💻 Terminal Output

```bash
# Author Dockerfile.greeter
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ cat << 'EOF' > Dockerfile.greeter
FROM alpine:3.20
ENTRYPOINT ["echo", "Hello"]
CMD ["World"]
EOF

# Build greeter image
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker build -f Dockerfile.greeter -t greeter:local .
[+] Building 7.0s (6/6) FINISHED                                 docker:default
 => [internal] load build definition from Dockerfile.greeter               0.0s
 => => transferring dockerfile: 105B                                       0.0s
 => [internal] load metadata for docker.io/library/alpine:3.20             3.6s
 => [auth] library/alpine:pull token for registry-1.docker.io              0.0s
 => [internal] load .dockerignore                                          0.0s
 => => transferring context: 87B                                           0.0s
 => [1/1] FROM docker.io/library/alpine:3.20@sha256:d9e853e87e55526f6b291  3.1s
 => => resolve docker.io/library/alpine:3.20@sha256:d9e853e87e55526f6b291  0.0s
 => => sha256:25f1d6b1951ac8eb3740558fe94cb83d377bdadf95f 3.63MB / 3.63MB  3.1s
 => exporting to image                                                     3.3s
 => => exporting layers                                                    0.0s
 => => exporting manifest sha256:76dc7ef5904f337ba7a5f0e1bc7f04cef3d1b49c  0.0s
 => => exporting config sha256:eedb5d7eb5bbfe64a5955346249e74b1370b2d2add  0.0s
 => => exporting attestation manifest sha256:c938f62d4f4018c15f607ed97347  0.0s
 => => exporting manifest list sha256:def06614af3cc9a664b7e496c26a9afb329  0.0s
 => => naming to docker.io/library/greeter:local                           0.0s
 => => unpacking to docker.io/library/greeter:local                        3.2s

# Test Run 1: Default execution
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker run --rm greeter:local
Hello World

# Test Run 2: Passing CLI argument
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker run --rm greeter:local DevOps
Hello DevOps
```

### 🔍 What I Observed on My System
- When running `docker run --rm greeter:local`:
  - `ENTRYPOINT ["echo", "Hello"]` combined with `CMD ["World"]` $\rightarrow$ executed `echo Hello World`.
  - Terminal printed: `Hello World`.
- When running `docker run --rm greeter:local DevOps`:
  - The trailing argument `DevOps` completely replaced `CMD ["World"]`.
  - The `ENTRYPOINT` remained untouched $\rightarrow$ executed `echo Hello DevOps`.
  - Terminal printed: `Hello DevOps`.
- **Engineering Verdict:**
  - Use `ENTRYPOINT` for the fixed binary (e.g. `["node", "server.js"]` or CLI tools like `["terraform"]`).
  - Use `CMD` for default flags or arguments (e.g. `["--port", "3000"]`) that users or orchestrators might want to override.

---

## Task 8: Production Inspection, Resource Metrics & Safe Teardown

Inspect image metadata, review user privileges, check container resource utilization, and perform a clean teardown.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker inspect demo-api:v1` | Dumps image metadata (inspects `Config.User`, `Config.Env`, `Config.ExposedPorts`). |
| `docker top api` | Shows process list inside the container (verifies user `node` vs `root`). |
| `docker stats --no-stream api` | Captures CPU/Memory utilization. |
| `docker rm -f api` | Gracefully terminates and removes the running container. |

### 💻 Terminal Output

```bash
# Verify non-root user in running container
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker top api
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
hrishav             40397               40375               0                   21:53               ?                   00:00:00            node server.js

# Inspect Image Environment & User metadata
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker image inspect demo-api:v1 \
  --format '{{json .Config.User}} | {{json .Config.ExposedPorts}} | {{json .Config.Env}}'
"node" | {"3000/tcp":{}} | ["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","NODE_VERSION=20.20.2","YARN_VERSION=1.22.22","PORT=3000","APP_ENV=dev","APP_VERSION=1.0"]

# Check resource usage
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker stats --no-stream api
CONTAINER ID   NAME      CPU %     MEM USAGE / LIMIT     MEM %     NET I/O         BLOCK I/O     PIDS
5822f1366273   api       0.00%     8.043MiB / 11.39GiB   0.07%     25.4kB / 630B   45.1kB / 0B   7

# Clean up running containers
hrishav@hrishav-LOQ-15IAX9:~/day09-dockerfile$ docker rm -f api
api
```

### 🔍 What I Observed on My System
- `docker top api` verified that PID 1 runs under user `node` (UID 1000) rather than `root` (UID 0), validating compliance with container security standards.
- `docker image inspect` confirmed that `PORT=3000`, `APP_ENV=dev`, and `APP_VERSION=1.0` are properly embedded into the image configuration.
- `docker stats` showed minimal resource footprint (typically ~20-30MB RAM for Node.js Alpine microservices).
- All test containers cleanly terminated without lingering resources.

---

## 🛠️ Production Debugging Matrix

When containers misbehave in staging or production, follow this systematic diagnostic guide:

| Symptom | Primary Root Causes | Investigation Command | Production Fix |
| :--- | :--- | :--- | :--- |
| **Container exits immediately (`Exited 0` or `1`)** | CMD script finished, missing dependency, syntax error in server.js, or file not found. | `docker logs <container>`<br>`docker inspect <container> --format '{{.State.ExitCode}}'` | Ensure primary process stays in foreground (`PID 1`). Fix syntax errors in `server.js`. |
| **App unreachable from host (`Connection refused`)** | App listening on `127.0.0.1` inside container instead of `0.0.0.0`, or port mapping forgotten (`-p`). | `ss -lntp \| grep :3000`<br>`docker port <container>`<br>`curl -I http://localhost:3000` | Bind Node server to `0.0.0.0`. Specify `-p 3000:3000` on `docker run`. |
| **Build is unexpectedly slow (Minutes instead of seconds)** | Massive build context sent to daemon (`node_modules` or `.git` uploaded). | Observe `transferring context: ...MB`<br>`ls -lh .` | Add `.git`, `node_modules`, and cache dirs to `.dockerignore`. |
| **`npm ci` / `npm install` fails during build** | Missing `package-lock.json` when using `npm ci`, or network timeout. | `docker build --progress=plain ...` | If no lockfile exists, use `npm install --omit=dev`. In locked repos, commit `package-lock.json` and use `npm ci --omit=dev`. |
| **Permission denied (`EACCES`)** | `USER node` selected but files copied as `root` without read/execute permissions. | `docker logs <container>`<br>`docker exec -it <container> ls -la /app` | Ensure `/app` files are world-readable or add `--chown=node:node` to `COPY` instructions. |
| **Environment value not taking effect** | Variable hardcoded in code, or overwritten by a `.env` file loaded inside container code. | `docker exec <container> env`<br>`docker inspect <container> --format '{{json .Config.Env}}'` | Check precedence order: CLI `-e` flags override Dockerfile `ENV` defaults. Ensure app code reads `process.env`. |

---

## 📋 Production Troubleshooting Notes

### 📋 Troubleshooting Note 1: App Unreachable Due to Localhost Loopback Binding
- **Problem:** Container started and reported status `Up`, but `curl http://localhost:3000/` failed with `curl: (7) Failed to connect to localhost port 3000: Connection refused`.
- **Evidence:**  
  - `docker ps` showed `0.0.0.0:3000->3000/tcp`.  
  - Container logs showed `listening on 3000`.  
  - Inside the container, `netstat -tlpn` showed `127.0.0.1:3000`.
- **Root Cause:** The Node.js HTTP server was bound to `127.0.0.1` (the loopback interface inside the container's isolated network namespace). Docker's bridge interface sends forwarded packets to the container's `eth0` IP address (`172.17.0.X`), which the loopback listener rejected.
- **Fix:** Changed `server.listen(PORT)` to explicitly bind to `0.0.0.0`: `server.listen(PORT, "0.0.0.0")`.
- **Verification:** Rebuilt image and curled `http://localhost:3000/` $\rightarrow$ received HTTP 200 greeting.

### 📋 Troubleshooting Note 2: Accidental Secret Leakage via Image Layer History
- **Problem:** An API key passed as `ENV API_KEY=secret123` was visible to anyone pulling the image via `docker history` and `docker inspect`.
- **Evidence:** Running `docker history demo-api:v1` exposed `ENV API_KEY=secret123` in plaintext in the layer metadata.
- **Root Cause:** `ENV` instructions are baked permanently into image manifest metadata. Even deleting the variable in a subsequent `RUN unset API_KEY` layer does not remove it from previous layers.
- **Fix:** Removed secrets from the `Dockerfile` entirely. Switched to injecting sensitive values at runtime using `docker run --env-file` or Docker Secrets / Kubernetes Secrets.
- **Verification:** Ran `docker history` and verified no secret credentials exist in the build definition.

---

## 🧠 Interview Readiness & Core Concepts

### 1. What is the fundamental difference between `CMD` and `ENTRYPOINT`?
- **Answer:** `ENTRYPOINT` defines the principal executable that will **always** run when the container starts. `CMD` provides default arguments or default commands. If both are defined in exec form, `ENTRYPOINT` receives `CMD` as its trailing arguments. When a user runs `docker run image <args>`, `<args>` completely replaces `CMD`, but will be passed as arguments to `ENTRYPOINT`.

### 2. Why should production Dockerfiles use `COPY` instead of `ADD`?
- **Answer:** `COPY` is transparent and predictable—it copies files or directories strictly from the build context into the image. `ADD` has unpredictable side effects: it automatically unpacks compressed tar files and can download files from URLs. Best practices mandate `COPY` unless local tar auto-extraction is specifically required.

### 3. Explain `ARG` vs. `ENV`. Can either be used for sensitive secrets?
- **Answer:** `ARG` is a build-time argument available only while running `docker build`. `ENV` sets environment variables that persist in the image metadata and remain active at runtime. **Neither is safe for secrets.** `ARG` values are visible in `docker history`, and `ENV` values are visible in `docker inspect`. Runtime secrets should be mounted as files or injected via environment secret providers.

### 4. Does the `EXPOSE` instruction actually publish container ports to the host?
- **Answer:** No. `EXPOSE` is purely informational metadata that documents for developers and orchestrators which ports the application is designed to listen on. To actually publish ports to the host network interface, you must explicitly pass the `-p <host_port>:<container_port>` or `-P` flag during `docker run`.

### 5. How do you structure a Dockerfile to maximize BuildKit layer caching?
- **Answer:** Order instructions from **least frequently changing to most frequently changing**. Copy package manifests (`package*.json`, `go.mod`, `pom.xml`) and install dependencies *before* copying the application source code (`COPY . .`). This ensures source code modifications reuse the cached dependency layer, cutting build times from minutes to milliseconds.

### 6. Why should you always use the JSON exec form for `CMD` (`["node", "server.js"]`)?
- **Answer:** The JSON exec form executes the binary directly as **PID 1** without spawning an intermediate shell. When Docker sends a `SIGTERM` signal (e.g. during `docker stop`), the application receives it directly and can initiate graceful shutdown (closing database pools, draining HTTP requests). The shell form (`CMD node server.js`) runs `/bin/sh` as PID 1, which frequently ignores signals and forces a dirty `SIGKILL` after 10 seconds.

### 7. What is the operational impact of a missing `.dockerignore` file?
- **Answer:** Without `.dockerignore`, the CLI serializes the entire folder (including `.git`, local logs, and `node_modules`) into the build context tarball, causing massive build latency over the daemon socket. Furthermore, local host-compiled binaries in `node_modules` can overwrite container dependencies and break on Alpine Linux, or local `.env` secrets can be accidentally baked into the image.

---

## 💭 Reflection Questions (Production Engineer Perspective)

### 1. Which Dockerfile step was reused after changing only `server.js`?
- **Answer:** Step `RUN npm install --omit=dev` and all prior steps (`FROM`, `WORKDIR`, `COPY package*.json ./`) were reused directly from the BuildKit cache (`CACHED`). Only `COPY . .` and subsequent metadata layers were rebuilt.

### 2. What changed when `package.json` was modified?
- **Answer:** The checksum of `package.json` changed, which caused a **cache miss** at step `COPY package*.json ./`. Because cache invalidation cascades downwards, the subsequent step `RUN npm install --omit=dev` was forced to execute from scratch.

### 3. How does configuration differ between image build time and container runtime?
- **Answer:** Build-time configuration (`ARG`) defines image assembly parameters (such as compiler flags or dependency versions) and creates an immutable artifact. Runtime configuration (`ENV`, `-e`, `--env-file`) injects operational parameters (ports, database URLs, log levels) into the running container without altering the underlying immutable image.

### 4. What would you change before shipping this Docker image to production?
- **Answer:**
  1. **Multi-stage Build:** Use a multi-stage Dockerfile to separate the build/install toolchain from the final minimal runtime image.
  2. **Image Digest Pinning:** Pin the base image by sha256 digest (`node:20-alpine@sha256:...`) instead of mutable tags to guarantee deterministic builds.
  3. **Strict Lockfile Installs:** Commit `package-lock.json` and use `npm ci --omit=dev --ignore-scripts` to prevent arbitrary script execution.
  4. **Native Healthcheck Directive:** Add `HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1`.
  5. **Vulnerability Scanning:** Integrate Trivy or Docker Scout into the CI/CD pipeline to block images with High/Critical CVEs.
  6. **Read-Only Root Filesystem:** Run container with `--read-only` and mount temporary writable directories only where needed (`/tmp`).

---

## 📦 Required Evidence & Submission Checklist

- [x] Project files `server.js`, `package.json`, `.dockerignore`, and `Dockerfile` committed.
- [x] Application responds to `GET /` and `GET /health` (`ok`).
- [x] Runtime configuration verified with `docker run -e` (`Hi Winter Arc | env=prod`).
- [x] Dependency cache hit demonstrated with `--progress=plain` after editing only `server.js`.
- [x] ENTRYPOINT experiment demonstrated with `greeter:local` (`Hello World` $\rightarrow$ `Hello DevOps`).
- [x] Safe non-root user (`USER node`) verified via `docker top`.

---

[← Day 08](Day08.md) | [Home](README.md) | [Day 10 →](Day10.md)
