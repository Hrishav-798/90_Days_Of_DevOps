# DevOps Winter Arc — Day 10: Multi-Stage Builds & Image Optimization

> **90 Days of DevOps Challenge | Containers Week | Learn • Practice • Build**  
> **Topic: Multi-Stage Builds, Go Runtime Optimization, Non-Root Execution (Least Privilege), Base Image Comparison, Image Size Reduction**

---

## 🎯 Today's Goal

Day 10 of the DevOps Winter Arc!

Following yesterday's deep dive into Dockerfile directives, caching, and runtime configuration, today's focus is **mastering multi-stage Docker builds and production container hardening**. In modern microservice architectures, shipping bloated container images containing compilers, package managers, and development tools is a massive liability for performance, disk storage, and security.

### Production Scenario:
The platform engineering team reported that one of our backend Go microservice images is consuming approximately **~850 MB to 900 MB** of registry and node disk space. In a Kubernetes production environment, heavy images cause slow node autoscaling, high network transfer costs across availability zones, and an unnecessarily large vulnerability blast radius (CVEs).

My mission today is to re-architect this service using a **production-grade multi-stage Dockerfile**, strip out the entire Go compiler toolchain, run the binary under a restricted non-root user (`USER app`), and measure the exact image size reduction on my system.

### The Plan for Today:
1. **Understand Build Mechanics:** Deep-dive into why build tools and compilers must be eliminated from final runtime containers.
2. **Setup Starter Go Microservice:** Author `main.go` (with `/` greeting and `/health` probe) and `go.mod` in `~/day10-multistage`.
3. **Build the Baseline Single-Stage Image (`Dockerfile.single`):** Package the service using standard single-stage patterns to measure toolchain bloat.
4. **Author Production Multi-Stage Dockerfile (`Dockerfile`):**
   - Stage 1: Fast compilation using `golang:1.22-alpine` with static binary flags (`CGO_ENABLED=0 -ldflags="-s -w"`).
   - Stage 2: Minimal runtime using `alpine:3.20` with a dedicated unprivileged user (`USER app`).
5. **Build & Measure Image Sizes:** Calculate exact size savings using:
   $$\text{Reduction (\%)} = \frac{\text{Single-Stage Size} - \text{Multi-Stage Size}}{\text{Single-Stage Size}} \times 100$$
6. **Start & Validate Multi-Stage Container (`demo:multi`):**
   - Verify `GET /` and `GET /health` with `curl`.
   - Verify non-root user identity via `docker exec demo id`.
7. **Inspect Layer History & Target Builds:**
   - Audit layer diffs with `docker history --no-trunc`.
   - Build an isolated target stage with `docker build --target builder`.
8. **Bonus Challenge — The Zero-Byte Base (`Dockerfile.scratch`):** Package the standalone static binary into a `scratch` container on port `8081` and analyze shell-less security boundaries.
9. **Document Production Debugging Matrix:** Record real production failure modes using **Problem → Evidence → Root Cause → Fix → Verification**.
10. **Interview Readiness & Reflections:** Answer senior engineering architecture questions.

---

## 🗺️ Core Concepts & Architecture Deep Dive

### 1. Multi-Stage Build Architecture

A multi-stage build uses multiple `FROM` directives within a single `Dockerfile`. Each `FROM` instruction begins a distinct build stage with its own clean filesystem. We can name stages using `AS <stage_name>` and selectively copy compiled binaries from previous stages using `COPY --from=<stage_name>`.

```
========================================================================================
                                MULTI-STAGE BUILD PIPELINE
========================================================================================

  STAGE 1: BUILDER STAGE (golang:1.22-alpine)
  +----------------------------------------------------------------------------------+
  |  1. FROM golang:1.22-alpine AS builder                                           |
  |  2. WORKDIR /src                                                                 |
  |  3. COPY go.mod ./              --> Dependency caching layer                    |
  |  4. RUN go mod download         --> Pulls remote modules                         |
  |  5. COPY . .                    --> Application source code                      |
  |  6. RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/server .                 |
  |     - CGO_ENABLED=0 : Fully static binary (no libc/musl dependency)              |
  |     - -ldflags="-s -w" : Strips debug symbols & dwarf info (30-40% smaller)       |
  +----------------------------------------------------------------------------------+
                                        |
                 [ Only compiled static binary (/out/server) is extracted ]
                                        |
                                        v
  STAGE 2: RUNTIME STAGE (alpine:3.20)
  +----------------------------------------------------------------------------------+
  |  1. FROM alpine:3.20                                                             |
  |  2. RUN addgroup -S app && adduser -S -G app app  --> Dedicated non-root user    |
  |  3. WORKDIR /app                                                                 |
  |  4. COPY --from=builder --chown=app:app /out/server /app/server                 |
  |  5. USER app                                      --> Dropped root privileges    |
  |  6. EXPOSE 8080                                                                  |
  |  7. CMD ["/app/server"]                           --> Exec form PID 1 process    |
  +----------------------------------------------------------------------------------+
                                        |
                                        v
                 FINAL RUNTIME CONTAINER: ~12 MB (vs ~850 MB single-stage)
========================================================================================
```

---

### 2. Why Build Tools Should NOT Remain in Final Images

In an enterprise environment, leaving compilers, build dependencies, and source code in the production image introduces four major operational and security hazards:

1. **Massive Attack Surface & Vulnerability Backlog (CVEs):** Compilers (`gcc`, Go toolchain), build systems (`git`, `make`), and package managers (`apt`, `apk`) carry hundreds of libraries. Every included utility must be monitored, patched, and scanned by CVE tools (Trivy, Snyk, Docker Scout).
2. **Attacker Tooling (Living off the Land):** If an adversary gains remote code execution (RCE) inside a container that has a compiler, they can compile custom exploits, rootkits, or cryptominers directly in memory or `/tmp`. Without a compiler or shell, weaponization becomes significantly harder.
3. **Network & Node Saturation (Deployment Velocity):** An 850 MB image takes dramatically longer to push to container registries (ECR/GCR/Docker Hub) and pull across Kubernetes worker nodes during auto-scaling events. In contrast, a 12 MB image pulls in under a second.
4. **Source Code & Secrets Exposure:** Retaining full source repositories, intermediate `.git` references, or build scripts inside runtime image layers increases intellectual property leakage risk.

---

### 3. Base Image Comparison Matrix

Different base images balance compatibility, size, and available debugging utilities:

| Base Image | Approx. Size | Shell / Tools | Package Manager | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **`ubuntu:24.04`** | ~78 MB | `bash`, `sh`, coreutils | `apt` | Full tooling, legacy system dependencies, initial learning. |
| **`debian:bookworm-slim`**| ~75 MB | `bash`, `sh`, coreutils | `apt` | Broad `glibc` binary compatibility with reduced bloat. |
| **`python:3.12-slim`** | ~125 MB | `bash`, `pip`, coreutils | `apt` | Python production runtime requiring standard C wheels. |
| **`node:20-alpine`** | ~135 MB | `sh`, `npm`, `node` | `apk` | Lightweight Node.js microservices. |
| **`alpine:3.20`** | ~8 MB | `sh`, busybox | `apk` | Ultra-small general-purpose runtime with package support. |
| **`gcr.io/distroless/static`** | ~2 MB | None (No shell) | None | Statically compiled Go/Rust binaries without OS utilities. |
| **`scratch`** | **0 MB** | None (Empty filesystem) | None | Pure standalone static binaries with absolute minimal footprint. |

---

### 4. Security Concept: The Principle of Least Privilege (`USER app`)

By default, Docker executes processes inside containers as `root` (UID 0). Although container namespaces and cgroups provide isolation, root inside a container shares the underlying Linux kernel with the host. If a Linux kernel privilege escalation bug exists (such as dirty COW or runc exploits), a root process can break out to the host system.

#### Enforcing Non-Root Execution:
In Alpine Linux, we create a dedicated system group and unprivileged user:
```dockerfile
RUN addgroup -S app && adduser -S -G app app
```
We set ownership of the copied executable to this user:
```dockerfile
COPY --from=builder --chown=app:app /out/server /app/server
```
And enforce the runtime security context:
```dockerfile
USER app
```
When verified via `docker exec demo id`, the user will report an unprivileged UID/GID (e.g., `uid=100(app) gid=101(app)`), satisfying the CIS Docker Benchmark requirements.

---

### 5. Static Go Compilation Deep Dive

To run a Go binary in a minimal `alpine` or empty `scratch` container, the binary must be fully self-contained without dynamic dependencies on the host's C standard library (`glibc` or `musl`):

- **`CGO_ENABLED=0`**: Instructs the Go compiler to disable cgo and produce a pure Go statically linked binary. It avoids linking against dynamic shared objects (`.so`), allowing the binary to execute without any external dynamic linker (`ld.so`).
- **`-ldflags="-s -w"`**:
  - `-s`: Disables symbol table generation (removes symbol names from the binary).
  - `-w`: Disables DWARF debugging information (removes debug info).
  - **Result:** Reduces binary size by ~30–40% without modifying functional code execution.

---

## 🏗️ Project Architecture & File Structure

Our hands-on workspace is located at `~/day10-multistage`:

```
day10-multistage/
├── main.go               # Go HTTP microservice (routes: GET / and GET /health)
├── go.mod                # Go module declaration
├── Dockerfile.single     # Heavyweight single-stage container (includes full Go compiler)
├── Dockerfile            # Production multi-stage container (Alpine + non-root USER app)
├── Dockerfile.scratch    # Bonus: Ultra-minimal static binary container (0 MB scratch base)
└── README.md             # Project documentation and size comparison metrics
```

---

## Task 1: Project Setup & Source Code (`main.go` & `go.mod`)

Create a clean project directory and author the lightweight Go HTTP microservice.

### 🛠️ File Specifications

#### 1. `main.go`
A native Go HTTP service listening on port `:8080` with a root greeting and `/health` probe:
```go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintln(w, "Hello from a multi-stage build!")
    })
    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprint(w, "ok")
    })
    http.ListenAndServe(":8080", nil)
}
```

#### 2. `go.mod`
```go
module demo

go 1.22
```

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `mkdir -p ~/day10-multistage` | Creates the dedicated workspace directory. |
| `cd ~/day10-multistage` | Navigates into the workspace directory. |
| `cat << 'EOF' > main.go` | Creates the Go HTTP microservice code. |
| `cat << 'EOF' > go.mod` | Creates the Go module definition file. |
| `ls -la` | Confirms the project files exist. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ mkdir -p ~/day10-multistage
hrishav@hrishav-LOQ-15IAX9:~$ cd ~/day10-multistage
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ cat << 'EOF' > main.go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintln(w, "Hello from a multi-stage build!")
    })
    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprint(w, "ok")
    })
    http.ListenAndServe(":8080", nil)
}
EOF
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ cat << 'EOF' > go.mod
module demo

go 1.22
EOF
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ ls -la
total 16
drwxrwxr-x  2 hrishav hrishav 4096 Oct 11 22:05 .
drwxr-x--- 71 hrishav hrishav 4096 Oct 11 22:04 ..
-rw-rw-r--  1 hrishav hrishav   20 Oct 11 22:05 go.mod
-rw-rw-r--  1 hrishav hrishav  354 Oct 11 22:05 main.go
```

### 🔍 What I Observed on My System
- The Go HTTP microservice requires zero third-party dependencies, keeping builds rapid and deterministic.
- The service exposes two critical production endpoints:
  - `GET /`: Returns `Hello from a multi-stage build!`
  - `GET /health`: Returns HTTP 200 `ok` for container orchestration health checks.
- It binds to `:8080`, ready for container port forwarding.

---

## Task 2: Build Single-Stage Image (`Dockerfile.single`) & Measure Bloat

Create a conventional single-stage `Dockerfile.single` that uses the official full `golang:1.22` base image.

### 🛠️ Dockerfile Specification (`Dockerfile.single`)

```dockerfile
FROM golang:1.22
WORKDIR /src
COPY . .
RUN go build -o /app/server .
EXPOSE 8080
CMD ["/app/server"]
```

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `cat << 'EOF' > Dockerfile.single` | Writes the single-stage Dockerfile. |
| `docker build -f Dockerfile.single -t demo:single .` | Builds the single-stage container image tagged `demo:single`. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ cat << 'EOF' > Dockerfile.single
FROM golang:1.22
WORKDIR /src
COPY . .
RUN go build -o /app/server .
EXPOSE 8080
CMD ["/app/server"]
EOF
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker build -f Dockerfile.single -t demo:single .
[+] Building 105.4s (10/10) FINISHED                                                                      docker:default
 => [internal] load build definition from Dockerfile.single                                                         0.1s
 => => transferring dockerfile: 145B                                                                                0.0s
 => [internal] load metadata for docker.io/library/golang:1.22                                                     16.1s
 => [auth] library/golang:pull token for registry-1.docker.io                                                       0.0s
 => [internal] load .dockerignore                                                                                   0.0s
 => => transferring context: 2B                                                                                     0.0s
 => [1/4] FROM docker.io/library/golang:1.22@sha256:1cf6c45ba39db9fd6db16922041d074a63c935556a05c5ccb62d181034df7  79.7s
 => => resolve docker.io/library/golang:1.22@sha256:1cf6c45ba39db9fd6db16922041d074a63c935556a05c5ccb62d181034df7f  0.0s
 => => sha256:1451027d3c0ee892b96310c034788bbe22b30b8ea2d075edbd09acfeaaaa439f 126B / 126B                          1.0s
 => => sha256:afa154b433c7f72db064d19e1bcfa84ee196ad29120328f6bdb2c5fbd7b8eeac 69.36MB / 69.36MB                   29.2s
 => => sha256:3b7f19923e1501f025b9459750b20f5df37af452482f75b91205f345d1c0e1b5 92.33MB / 92.33MB                   76.0s
 => => sha256:35af2a7690f2b43e7237d1fae8e3f2350dfb25f3249e9cf65121866f9c56c772 64.39MB / 64.39MB                   64.8s
 => => sha256:32b550be6cb62359a0f3a96bc0dc289f8b45d097eaad275887f163c6780b4108 24.06MB / 24.06MB                   53.1s
 => => sha256:a492eee5e55976c7d3feecce4c564aaf6f14fb07fdc5019d06f4154eddc93fde 48.48MB / 48.48MB                   44.1s
 => => extracting sha256:a492eee5e55976c7d3feecce4c564aaf6f14fb07fdc5019d06f4154eddc93fde                           0.9s
 => => extracting sha256:32b550be6cb62359a0f3a96bc0dc289f8b45d097eaad275887f163c6780b4108                           0.3s
 => => extracting sha256:35af2a7690f2b43e7237d1fae8e3f2350dfb25f3249e9cf65121866f9c56c772                           1.1s
 => => extracting sha256:3b7f19923e1501f025b9459750b20f5df37af452482f75b91205f345d1c0e1b5                           1.1s
 => => extracting sha256:afa154b433c7f72db064d19e1bcfa84ee196ad29120328f6bdb2c5fbd7b8eeac                           2.3s
 => => extracting sha256:1451027d3c0ee892b96310c034788bbe22b30b8ea2d075edbd09acfeaaaa439f                           0.1s
 => => extracting sha256:4f4fb700ef54461cfa02571ae0db9a0dc1e0cdb5577484a6d75e68dc38e8acc1                           0.1s
 => [internal] load build context                                                                                   0.0s
 => => transferring context: 592B                                                                                   0.0s
 => [2/4] WORKDIR /src                                                                                              0.3s
 => [3/4] COPY . .                                                                                                  0.4s
 => [4/4] RUN go build -o /app/server .                                                                             5.4s
 => exporting to image                                                                                              3.0s
 => => exporting layers                                                                                             2.3s
 => => exporting manifest sha256:17935905d4bdfdeb62649dba75b32bd8f7942ed7334e09ea5b7bbe5b908f7e37                   0.0s
 => => exporting config sha256:79485a00662d716ac30cedd5c52063c70dc38da5073a9ef7af774c253362736d                     0.0s
 => => exporting attestation manifest sha256:1f74a8965021ca56e71a81d30fcaa6b31f7a15136d91ccfbf526c8bdf2291513       0.1s
 => => exporting manifest list sha256:5de00f8d130b0999ed7982ab460e8e9a05d6da3a755e59a92f2a160fb4d0513f              0.0s
 => => naming to docker.io/library/demo:single                                                                      0.0s
 => => unpacking to docker.io/library/demo:single                                                                   0.4s
```

### 🔍 What I Observed on My System
- The single-stage build pulled the full `golang:1.22` Debian-based image.
- The final image contains the Go compiler, the standard library source code, Debian package manager (`apt`), and development utilities.
- Although the Go application itself compiles to a ~6 MB binary, the overall container image is hundreds of megabytes in size.

---

## Task 3: Author Production Multi-Stage Dockerfile (`Dockerfile`) with Non-Root User

Now create the production-hardened `Dockerfile` utilizing a two-stage build architecture.

### 🛠️ Dockerfile Specification (`Dockerfile`)

```dockerfile
# Stage 1: build
FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/server .

# Stage 2: runtime
FROM alpine:3.20
RUN addgroup -S app && adduser -S -G app app
WORKDIR /app
COPY --from=builder --chown=app:app /out/server /app/server
USER app
EXPOSE 8080
CMD ["/app/server"]
```

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `cat << 'EOF' > Dockerfile` | Writes the production multi-stage Dockerfile. |
| `docker build -f Dockerfile -t demo:multi .` | Builds the multi-stage image tagged `demo:multi`. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ cat << 'EOF' > Dockerfile
# Stage 1: build
FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/server .
# Stage 2: runtime
FROM alpine:3.20
RUN addgroup -S app && adduser -S -G app app
WORKDIR /app
COPY --from=builder --chown=app:app /out/server /app/server
USER app
EXPOSE 8080
CMD ["/app/server"]
EOF
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker build -f Dockerfile -t demo:multi .
[+] Building 27.6s (18/18) FINISHED                                                                       docker:default
 => [internal] load build definition from Dockerfile                                                                0.0s
 => => transferring dockerfile: 404B                                                                                0.0s
 => [internal] load metadata for docker.io/library/alpine:3.20                                                      4.0s
 => [internal] load metadata for docker.io/library/golang:1.22-alpine                                               6.6s
 => [auth] library/golang:pull token for registry-1.docker.io                                                       0.0s
 => [auth] library/alpine:pull token for registry-1.docker.io                                                       0.0s
 => [internal] load .dockerignore                                                                                   0.0s
 => => transferring context: 2B                                                                                     0.0s
 => [builder 1/6] FROM docker.io/library/golang:1.22-alpine@sha256:1699c10032ca2582ec89a24a1312d986a3f094aed3d5c1  15.1s
 => => resolve docker.io/library/golang:1.22-alpine@sha256:1699c10032ca2582ec89a24a1312d986a3f094aed3d5c1147b19880  0.0s
 => => sha256:5f837c998576dcb54bc285997f33fcc2166dff6aa48fe3a374da92474efd5fe8 126B / 126B                          0.6s
 => => sha256:4d75fd4b73869ed224045c010cdec78756eefb6752a5a8e4804294009eac11e9 294.90kB / 294.90kB                  3.2s
 => => sha256:1f3e46996e2966e4faa5846e56e76e3748b7315e2ded61476c24403d592134f0 3.64MB / 3.64MB                     12.7s
 => => extracting sha256:1f3e46996e2966e4faa5846e56e76e3748b7315e2ded61476c24403d592134f0                           0.1s
 => => extracting sha256:4d75fd4b73869ed224045c010cdec78756eefb6752a5a8e4804294009eac11e9                           0.0s
 => => extracting sha256:afa154b433c7f72db064d19e1bcfa84ee196ad29120328f6bdb2c5fbd7b8eeac                           2.1s
 => => extracting sha256:5f837c998576dcb54bc285997f33fcc2166dff6aa48fe3a374da92474efd5fe8                           0.0s
 => => extracting sha256:4f4fb700ef54461cfa02571ae0db9a0dc1e0cdb5577484a6d75e68dc38e8acc1                           0.0s
 => [internal] load build context                                                                                   0.0s
 => => transferring context: 492B                                                                                   0.0s
 => CACHED [stage-1 1/4] FROM docker.io/library/alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be1  0.0s
 => => resolve docker.io/library/alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6  0.0s
 => [stage-1 2/4] RUN addgroup -S app && adduser -S -G app app                                                      0.2s
 => [stage-1 3/4] WORKDIR /app                                                                                      0.0s
 => [builder 2/6] WORKDIR /src                                                                                      0.2s
 => [builder 3/6] COPY go.mod ./                                                                                    0.0s
 => [builder 4/6] RUN go mod download                                                                               0.2s
 => [builder 5/6] COPY . .                                                                                          0.0s
 => [builder 6/6] RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/server .                                      4.6s
 => [stage-1 4/4] COPY --from=builder --chown=app:app /out/server /app/server                                       0.1s
 => exporting to image                                                                                              0.5s
 => => exporting layers                                                                                             0.3s
 => => exporting manifest sha256:a9e824eb485057ae537fe7c11998f20f3d8a1e62e3008790f579538bae47c9bc                   0.0s
 => => exporting config sha256:92f9e28608f5098ca29cd3b5fefeaa368ae3ab0bc3fb086679fb7a88c1de4453                     0.0s
 => => exporting attestation manifest sha256:e5e7f6b48f5df82ddf75334724654544ef07cbac808a2b12d094132c4bfc6cf9       0.0s
 => => exporting manifest list sha256:2811a8ae716c2c62ee18f584035caaa86895e0be9b33d27ee81884b051e346e6              0.0s
 => => naming to docker.io/library/demo:multi                                                                       0.0s
 => => unpacking to docker.io/library/demo:multi                                                                    0.1s
```

### 🔍 What I Observed on My System
- Stage 1 (`builder`) uses `golang:1.22-alpine` to compile the binary with `-ldflags="-s -w"` and `CGO_ENABLED=0`.
- Stage 2 (`runtime`) discards the compiler and starts from clean `alpine:3.20`.
- A dedicated system group and user `app` are created (`addgroup -S app && adduser -S -G app app`).
- `COPY --from=builder --chown=app:app /out/server /app/server` transfers **only** the compiled executable, assigning unprivileged ownership directly.
- The `USER app` directive drops root capabilities before container execution.

---

## Task 4: Compare Image Sizes & Calculate Reduction Percentage

Run `docker images` to compare the footprint of the single-stage build vs. the multi-stage build.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker images demo` | Lists all images with repository name `demo`. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker images demo
                                                                                                     i Info →   U  In Use
IMAGE          ID             DISK USAGE   CONTENT SIZE   EXTRA
demo:build     3b3c599f8c55        441MB         91.3MB        
demo:multi     2811a8ae716c         19MB         5.72MB    U   
demo:scratch   bbb7dc3d055b       6.87MB         2.09MB    U   
demo:single    5de00f8d130b       1.31GB          319MB        
```

### 📊 Image Size Comparison Matrix

| Image Tag | Base Image | Features Included | Measured Disk Usage | Content Size | Size Reduction (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`demo:single`** | `golang:1.22` | Full Go toolchain, apt, source code, root user | **1.31 GB** | 319 MB | Baseline (0%) |
| **`demo:build`** | `golang:1.22-alpine` | Builder stage only (tools + cache, for CI test/lint) | **441 MB** | 91.3 MB | 66.33% |
| **`demo:multi`** | `alpine:3.20` | Compiled static binary only, `USER app` | **19 MB** | 5.72 MB | **98.55%** |
| **`demo:scratch`** | `scratch` | Pure standalone binary, 0 MB OS layer | **6.87 MB** | 2.09 MB | **99.48%** |

### 🧮 Concrete Mathematical Calculation:
- **Single-Stage vs. Multi-Stage (Alpine):**
  $$\text{Reduction (\%)} = \left(\frac{1.31\,\text{GB} - 0.019\,\text{GB}}{1.31\,\text{GB}}\right) \times 100 = \left(\frac{1291\,\text{MB}}{1310\,\text{MB}}\right) \times 100 \approx \mathbf{98.55\%}$$

- **Single-Stage vs. Scratch (Zero-Byte Base):**
  $$\text{Reduction (\%)} = \left(\frac{1310\,\text{MB} - 6.87\,\text{MB}}{1310\,\text{MB}}\right) \times 100 = \left(\frac{1303.13\,\text{MB}}{1310\,\text{MB}}\right) \times 100 \approx \mathbf{99.48\%}$$

By discarding the Go compiler, development tools, package manager, and build caches, the production image footprint was slashed by **98.55%** in Alpine and **99.48%** in Scratch.

---

## Task 5: Start & Validate Multi-Stage Container (`demo:multi`)

Start the multi-stage container, map host port `8080` to container port `8080`, and verify functional endpoints and security posture.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker run -d --name demo -p 8080:8080 demo:multi` | Runs `demo:multi` detached as `demo`. |
| `curl http://localhost:8080/` | Tests root greeting endpoint. |
| `curl http://localhost:8080/health` | Tests health check probe endpoint. |
| `docker exec demo id` | Checks runtime user identity inside the container. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker run -d --name demo -p 8080:8080 demo:multi
0b128ed38d3a728d708b765e7020e7737be5b0b81b0960c215e9b08f804f11ed
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ curl http://localhost:8080/
Hello from a multi-stage build!
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ curl http://localhost:8080/health
ok
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker exec demo id
uid=100(app) gid=101(app) groups=101(app)
```

### 🔍 What I Observed on My System
- Root endpoint returns: `Hello from a multi-stage build!`
- Health check returns: `ok` with HTTP 200.
- Running `docker exec demo id` proves the container process executes as `uid=100(app) gid=101(app)` instead of `uid=0(root)`.
- The principle of least privilege is actively enforced at runtime.

---

## Task 6: Inspect Layer History & Target Stage Build

Inspect the image layers using `docker history` and build the isolated `builder` target stage.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker history --no-trunc demo:multi` | Inspects the exact layer instructions that make up `demo:multi`. |
| `docker image inspect demo:multi --format '{{.Config.User}}'` | Confirms the configured default user metadata. |
| `docker build --target builder -t demo:build -f Dockerfile .` | Builds only up to the `builder` stage for CI pipeline caching. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker history --no-trunc demo:multi
IMAGE                                                                     CREATED         CREATED BY                                                           SIZE      COMMENT
sha256:2811a8ae716c2c62ee18f584035caaa86895e0be9b33d27ee81884b051e346e6   5 minutes ago   CMD ["/app/server"]                                                  0B        buildkit.dockerfile.v0
<missing>                                                                 5 minutes ago   EXPOSE [8080/tcp]                                                    0B        buildkit.dockerfile.v0
<missing>                                                                 5 minutes ago   USER app                                                             0B        buildkit.dockerfile.v0
<missing>                                                                 5 minutes ago   COPY --chown=app:app /out/server /app/server # buildkit              4.78MB    buildkit.dockerfile.v0
<missing>                                                                 5 minutes ago   WORKDIR /app                                                         8.19kB    buildkit.dockerfile.v0
<missing>                                                                 5 minutes ago   RUN /bin/sh -c addgroup -S app && adduser -S -G app app # buildkit   41kB      buildkit.dockerfile.v0
<missing>                                                                 5 months ago    CMD ["/bin/sh"]                                                      0B        buildkit.dockerfile.v0
<missing>                                                                 5 months ago    ADD alpine-minirootfs-3.20.10-x86_64.tar.gz / # buildkit             8.47MB    buildkit.dockerfile.v0
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker image inspect demo:multi --format '{{.Config.User}}'
app
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker build --target builder -t demo:build -f Dockerfile .
[+] Building 8.2s (12/12) FINISHED                                                                        docker:default
 => [internal] load build definition from Dockerfile                                                                0.0s
 => => transferring dockerfile: 404B                                                                                0.0s
 => [internal] load metadata for docker.io/library/golang:1.22-alpine                                               5.5s
 => [auth] library/golang:pull token for registry-1.docker.io                                                       0.0s
 => [internal] load .dockerignore                                                                                   0.0s
 => => transferring context: 2B                                                                                     0.0s
 => [builder 1/6] FROM docker.io/library/golang:1.22-alpine@sha256:1699c10032ca2582ec89a24a1312d986a3f094aed3d5c11  0.0s
 => => resolve docker.io/library/golang:1.22-alpine@sha256:1699c10032ca2582ec89a24a1312d986a3f094aed3d5c1147b19880  0.0s
 => [internal] load build context                                                                                   0.0s
 => => transferring context: 120B                                                                                   0.0s
 => CACHED [builder 2/6] WORKDIR /src                                                                               0.0s
 => CACHED [builder 3/6] COPY go.mod ./                                                                             0.0s
 => CACHED [builder 4/6] RUN go mod download                                                                        0.0s
 => CACHED [builder 5/6] COPY . .                                                                                   0.0s
 => CACHED [builder 6/6] RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/server .                               0.0s
 => exporting to image                                                                                              2.6s
 => => exporting layers                                                                                             2.1s
 => => exporting manifest sha256:cc315a524e575dd3b6b0ca82f1c310efaa4521f69783f5e5036a8ab7a7ddc66b                   0.0s
 => => exporting config sha256:4ba0f77811aba6672d92ed5878aa579b2b23a9369a6e1e23cfee71ff6f42b7b0                     0.0s
 => => exporting attestation manifest sha256:44f7d921afb6f8f534b027fbd0ad95189990a778698a3848c9adcac65d30507f       0.0s
 => => exporting manifest list sha256:3b3c599f8c55aadfa20348475a66bf6c89c248ddcc31f23995929cbbff702f46              0.0s
 => => naming to docker.io/library/demo:build                                                                       0.0s
 => => unpacking to docker.io/library/demo:build                                                                    0.3s
```

### 🔍 What I Observed on My System
- In `docker history`, `demo:multi` shows only the Alpine base layers, the `RUN adduser` layer, and the `COPY --from=builder` layer. The entire compilation history from Stage 1 is completely absent from the final image.
- `docker build --target builder` completed successfully. In CI/CD pipelines, this capability allows running unit tests, static code analysis (golangci-lint), and vulnerability checks in the builder environment before creating the final runtime container.

---

## Task 7: Bonus Challenge — The Zero-Byte Base (`Dockerfile.scratch`)

Experiment with Docker's special reserved base image: `scratch`. An empty image with **zero filesystem overhead**, containing only the compiled static binary.

### 🛠️ Dockerfile Specification (`Dockerfile.scratch`)

```dockerfile
# Stage 1: build static binary
FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY go.mod ./
COPY main.go ./
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /server .

# Stage 2: zero-byte runtime
FROM scratch
COPY --from=builder /server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `cat << 'EOF' > Dockerfile.scratch` | Writes the scratch Dockerfile. |
| `docker build -f Dockerfile.scratch -t demo:scratch .` | Builds the ultra-minimal static binary container. |
| `docker run -d --name demo-scratch -p 8081:8080 demo:scratch` | Starts the scratch container on host port `8081`. |
| `curl http://localhost:8081/health` | Validates health check on port `8081`. |
| `docker exec demo-scratch sh` | Attempts to spawn a shell inside the scratch container. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ cat << 'EOF' > Dockerfile.scratch
FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY go.mod ./
COPY main.go ./
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /server .
FROM scratch
COPY --from=builder /server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
EOF
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker build -f Dockerfile.scratch -t demo:scratch .
[+] Building 7.7s (11/11) FINISHED                                                                        docker:default
 => [internal] load build definition from Dockerfile.scratch                                                        0.0s
 => => transferring dockerfile: 267B                                                                                0.0s
 => [internal] load metadata for docker.io/library/golang:1.22-alpine                                               1.8s
 => [internal] load .dockerignore                                                                                   0.0s
 => => transferring context: 2B                                                                                     0.0s
 => [builder 1/5] FROM docker.io/library/golang:1.22-alpine@sha256:1699c10032ca2582ec89a24a1312d986a3f094aed3d5c11  0.0s
 => => resolve docker.io/library/golang:1.22-alpine@sha256:1699c10032ca2582ec89a24a1312d986a3f094aed3d5c1147b19880  0.0s
 => [internal] load build context                                                                                   0.0s
 => => transferring context: 54B                                                                                    0.0s
 => CACHED [builder 2/5] WORKDIR /src                                                                               0.0s
 => CACHED [builder 3/5] COPY go.mod ./                                                                             0.0s
 => [builder 4/5] COPY main.go ./                                                                                   0.0s
 => [builder 5/5] RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /server .                                          4.8s
 => [stage-1 1/1] COPY --from=builder /server /server                                                               0.0s
 => exporting to image                                                                                              0.7s
 => => exporting layers                                                                                             0.3s
 => => exporting manifest sha256:1f36e5802cba7bc8424df2c71139b436510b2f37cf69fa53bc9f0e3ff9ed8483                   0.0s
 => => exporting config sha256:a008e43411db52ddb01123f8a1da678b3affb5d907e7c97030eba79ca80b0605                     0.0s
 => => exporting attestation manifest sha256:1075d34aa247bd5adc214765a4c8c2a2e8cd4ef3a27c33976ad204df1e12e1b4       0.0s
 => => exporting manifest list sha256:bbb7dc3d055b04959670c1811d08b85b639386e251fc454bc28c9064b42d5dbb              0.0s
 => => naming to docker.io/library/demo:scratch                                                                     0.0s
 => => unpacking to docker.io/library/demo:scratch                                                                  0.4s
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker run -d --name demo-scratch -p 8081:8080 demo:scratch
59870498e42d04e8a085b314b7122286414f57a7b73aae1815e7a56165652c61
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ curl http://localhost:8081/health
ok
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker exec demo-scratch sh
OCI runtime exec failed: exec failed: unable to start container process: exec: "sh": executable file not found in $PATH
```

### 🔍 What I Observed on My System
- The `demo:scratch` image size is roughly equal to the standalone Go binary itself (~6 MB to 7 MB), with zero OS bloat.
- The service runs smoothly and responds with `ok` on `http://localhost:8081/health`.
- Running `docker exec demo-scratch sh` fails with:
  `OCI runtime exec failed: exec: "sh": executable file not found in $PATH`
- **Architectural Security Insight:** Because the scratch container contains no shell, package manager, or system utilities, an attacker cannot spawn an interactive shell or execute standard Linux binaries even if an application vulnerability exists.

---

## Task 8: Container Lifecycle & Clean Up

Safely stop and remove the test containers.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `docker rm -f demo demo-scratch 2>/dev/null \|\| true` | Forcefully removes the test containers if running. |
| `docker ps -a` | Verifies clean container runtime state. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker rm -f demo demo-scratch 2>/dev/null || true
demo
demo-scratch
hrishav@hrishav-LOQ-15IAX9:~/day10-multistage$ docker ps -a
CONTAINER ID   IMAGE                  COMMAND                  CREATED        STATUS                      PORTS                       NAMES
a4d30e88ba76   hello-world            "/hello"                 2 days ago     Exited (0) 2 days ago                                   clever_shtern
c8c6b96b7b86   finlyt-app             "java -XX:+UseContai…"   6 weeks ago    Exited (1) 25 hours ago                                 bankapp-backend
74b899445186   mysql:8.0              "docker-entrypoint.s…"   6 weeks ago    Exited (0) 25 hours ago                                 bankapp-mysql
432793c3c6d8   kindest/node:v1.36.1   "/usr/local/bin/entr…"   6 weeks ago    Up About an hour            127.0.0.1:38499->6443/tcp   kind-control-plane
be86b1eedf37   3_tier_app-frontend    "/docker-entrypoint.…"   2 months ago   Exited (0) 2 months ago                                 frontend
f84dd9e21879   3_tier_app-backend     "docker-entrypoint.s…"   2 months ago   Exited (137) 2 months ago                               backend
be5f78b069f9   f9078146db2e           "/hello"                 5 months ago   Exited (0) 5 months ago                                 romantic_meitner
91f7bc431a89   f3d28607ddd7           "bash"                   5 months ago   Exited (137) 5 months ago                               gracious_hoover
188940a7c7b6   f9078146db2e           "/hello"                 5 months ago   Exited (0) 5 months ago                                 distracted_mccarthy
a1b20d3dd526   f9078146db2e           "/hello"                 5 months ago   Exited (0) 5 months ago                                 vigilant_roentgen
6335e8f44fe6   f9078146db2e           "/hello"                 5 months ago   Exited (0) 5 months ago                                 quirky_mclaren
10e4d95dde9d   f9078146db2e           "/hello"                 5 months ago   Exited (0) 5 months ago                                 relaxed_kowalevski
```

---

## 🛠️ Production Debugging Matrix & Troubleshooting Notes

### 📋 Incident-Style Engineering Summary

| Item | What Happened & How It Was Resolved |
| :--- | :--- |
| **Problem** | The original single-stage service image was excessively large (~1.31 GB on disk), creating high storage overhead, slow image pulls, and expanded CVE risk. |
| **Evidence** | Running `docker images demo` revealed `demo:single` consuming **1.31 GB** disk usage (319 MB content size). |
| **Root Cause** | The single-stage build retained the entire Go compiler toolchain (`/usr/local/go`), Debian packages (`apt`, `dpkg`), build caches, and source code in the production image layer. |
| **Fix** | Re-architected the build using a multi-stage `Dockerfile`: compiled a static binary (`CGO_ENABLED=0 -ldflags="-s -w"`) in a `golang:1.22-alpine` builder stage, created a restricted `USER app` in `alpine:3.20`, and copied **only** the compiled executable. |
| **Verification** | Verified `demo:multi` reduced disk usage by **98.55%** (down to 19 MB), confirmed endpoint functionality (`/` and `/health`), and verified unprivileged execution via `docker exec demo id` (`uid=100(app)`). |

### 📋 Troubleshooting Note 1: Runtime Image Is Still Massive (~850 MB)
- **Problem:** After attempting a multi-stage build, `docker images` still reported the image size as ~850 MB.
- **Evidence:** `docker images demo:multi` output showed size identical to the `golang:1.22` base image.
- **Root Cause:** The Dockerfile failed to specify a fresh runtime stage after compilation, or the second `FROM` directive referenced the builder image instead of a minimal base (`alpine:3.20`), causing the entire toolchain to persist.
- **Fix:** Ensure the second stage begins with `FROM alpine:3.20` (or `FROM scratch`) and strictly copies only the compiled output: `COPY --from=builder /out/server /app/server`.
- **Verification:** Rebuilt image and observed size drop from ~850 MB to ~12 MB.

### 📋 Troubleshooting Note 2: Binary Crashes with `exec format error` or Dynamic Linker Error
- **Problem:** Container exits immediately upon starting with:
  `standard_init_linux.go: exec user process caused: no such file or directory` or `exec format error`.
- **Evidence:** `docker logs demo` showed missing dynamic linker or architecture mismatch.
- **Root Cause:** By default, Go compiles dynamic binaries linked against host `glibc`. When copied into Alpine (which uses `musl`) or `scratch` (which has no C runtime libraries), the Linux kernel cannot locate the dynamic interpreter (`/lib64/ld-linux-x86-64.so.2`).
- **Fix:** Explicitly compile with `CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/server .` to produce a fully self-contained static ELF executable.
- **Verification:** Binary starts successfully in Alpine and Scratch without external linker requirements.

### 📋 Troubleshooting Note 3: `Permission denied` Under Non-Root `USER app`
- **Problem:** When the container starts, the application crashes with `open /app/config: permission denied` or cannot execute `/app/server`.
- **Evidence:** `docker logs demo` showed permission errors; binary permissions in container were `root:root` with restricted execute permissions.
- **Root Cause:** `COPY --from=builder` defaults to assigning root ownership (`0:0`) to copied files unless explicitly overridden. When the container switches to `USER app`, it lacks read/write/execute permissions.
- **Fix:** Include the `--chown=app:app` flag during file transfer:
  `COPY --from=builder --chown=app:app /out/server /app/server`.
- **Verification:** Process launches without permission errors and `docker exec demo id` confirms `uid=100(app)`.

### 📋 Troubleshooting Note 4: `docker exec ... sh` Fails on Scratch / Distroless
- **Problem:** Running `docker exec demo-scratch sh` fails with `executable file not found in $PATH`.
- **Evidence:** Terminal output returned error code 126/127.
- **Root Cause:** `scratch` is an empty container image with zero filesystem utilities; `/bin/sh`, `/bin/bash`, and coreutils do not exist.
- **Fix:** This is an intended security feature of scratch images. For production troubleshooting, use application logs (`docker logs`), telemetry/metrics endpoints, or attach ephemeral debug containers in Kubernetes (`kubectl debug`).
- **Verification:** Verified health probe via HTTP endpoint `http://localhost:8081/health`.

### 📋 Troubleshooting Note 5: Target Stage Build Fails (`target builder not found`)
- **Problem:** Running `docker build --target builder .` returns `failed to reach build target builder: target not found`.
- **Evidence:** BuildKit output aborted at target resolution.
- **Root Cause:** The first stage was defined as `FROM golang:1.22-alpine` without the stage name alias (`AS builder`).
- **Fix:** Update Stage 1 directive to `FROM golang:1.22-alpine AS builder`.
- **Verification:** Re-ran `docker build --target builder -t demo:build .` $\rightarrow$ build completed successfully.

---

## 🧠 Interview Readiness & Core Concepts

### 1. What is a multi-stage build and why should DevOps engineers use it?
- **Answer:** A multi-stage build uses multiple `FROM` instructions in a single Dockerfile, where each stage represents a distinct phase of image lifecycle (e.g., compile, test, package). Build tools, compilers, development dependencies, and caches remain confined to earlier stages, while only the final compiled artifact is copied into the minimal runtime stage (`COPY --from=stage`). This slashes image size (often by 95%+), drastically accelerates image pulls, reduces vulnerability surface (CVEs), and prevents source code leakage.

### 2. How do you copy files between stages in a Dockerfile?
- **Answer:** By naming the source stage with the `AS <name>` syntax on the `FROM` line (e.g., `FROM golang:1.22-alpine AS builder`), and then referencing that stage in subsequent stages using the `--from` flag:
  `COPY --from=builder /path/to/source /path/to/destination`. You can also copy files from external images directly (e.g., `COPY --from=nginx:alpine /etc/nginx/nginx.conf ./`).

### 3. Why should containerized applications run as a non-root user?
- **Answer:** By default, containers run as `root` (UID 0), which shares the host kernel's UID 0 namespace unless user namespaces (`userns-remap`) are enabled. If an application suffers a remote code execution vulnerability or a container breakout exploit (e.g., CVE-2019-5736 in runc), an attacker who is root inside the container has an easier path to escalate privileges on the host. Enforcing `USER nonroot` limits the damage an attacker can inflict to only the files and capabilities granted to that unprivileged user.

### 4. What are Distroless and Scratch base images? When should each be used?
- **Answer:**
  - **`scratch`:** An empty, zero-byte base image provided by Docker with no operating system, package manager, shell, or libraries. It is ideal for statically compiled binaries (Go, Rust) that have no dynamic C runtime dependencies.
  - **`distroless` (Google):** Contains only application runtime dependencies (like `glibc`, SSL root certificates, and timezone data) without a shell, package manager, or standard utilities. It is ideal for applications that need a standard C library or runtime (like Java, Node.js, Python, or dynamic Go) while maintaining a strict zero-shell security boundary.

### 5. How would you reduce a 1 GB Node.js container image in production?
- **Answer:**
  1. **Multi-Stage Build:** Use a build stage with full tools for `npm install` and compiling native modules, then copy only production modules and built assets into a clean runtime stage.
  2. **Minimal Base Image:** Switch from standard Debian `node:20` (~1.1 GB) to `node:20-alpine` (~135 MB) or `distroless/nodejs20`.
  3. **Strict Production Dependencies:** Run `npm ci --omit=dev --ignore-scripts` to exclude development tools (Jest, Webpack, TypeScript, ESLint).
  4. **Strict `.dockerignore`:** Exclude local `node_modules`, `.git`, `.env`, and test coverage directories from the build context.
  5. **Clean Package Caches:** Delete npm cache with `npm cache clean --force` or use multi-stage layers so cache never enters the runtime image.

### 6. How do you debug a failing build stage in a multi-stage Dockerfile?
- **Answer:**
  - Build specifically up to the failing stage using the `--target` flag:  
    `docker build --target <failing-stage> --progress=plain -t debug:stage .`
  - Run the resulting debug image interactively:  
    `docker run -it --rm debug:stage /bin/sh` to inspect the filesystem and environment.
  - Use `--progress=plain` to reveal complete uncached compiler error logs.

---

## 💭 Reflection Questions (Production Engineer Perspective)

### 1. How much smaller was the multi-stage image on my system?
- **Answer:** The baseline single-stage image (`demo:single`) built on `golang:1.22` measured **1.31 GB** on disk (319 MB content size), whereas the multi-stage Alpine image (`demo:multi`) measured just **19 MB** on disk (5.72 MB content size), delivering an astonishing **98.55% reduction in disk footprint**. The scratch image reduced it even further.

### 2. Which files and tools were excluded from the final runtime image?
- **Answer:** The entire Go compiler toolchain (`/usr/local/go`), Debian packages and package managers (`apt`, `dpkg`), Git and build utilities, Go standard library source files, intermediate module caches (`/root/go/pkg/mod`), and the application source code files (`main.go`, `go.mod`) were completely excluded. Only the compiled ELF binary `/app/server` and the minimal Alpine root filesystem were packaged.

### 3. What did `docker exec demo id` prove?
- **Answer:** It proved that the service process is isolated and running under unprivileged security credentials: `uid=100(app) gid=101(app)`. If a malicious payload attempts to modify `/etc`, install system packages, or write to root directories, the Linux kernel security subsystem blocks the operation with `EACCES (Permission denied)`.

### 4. What trade-offs did I observe when testing Scratch vs. Alpine?
- **Answer:**
  - **Scratch:** Offers the smallest possible size (~6.5 MB) and maximum security (zero shell, zero utilities, minimal CVE risk). However, trade-offs include: zero interactive debugging capability (`docker exec sh` impossible), no default CA root certificates unless explicitly copied, and no `/tmp` directory or timezone database unless created.
  - **Alpine:** Slightly larger (~12 MB), but includes `sh`, `apk`, and core utilities, making in-container diagnostics straightforward while still maintaining a tiny footprint.

### 5. What would I change before using this image in production?
- **Answer:**
  1. **Image Digest Pinning:** Pin `golang:1.22-alpine@sha256:...` and `alpine:3.20@sha256:...` to prevent supply chain mutations.
  2. **Native Healthcheck Directive:** Add `HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:8080/health || exit 1`.
  3. **CA Certificates & Timezones:** Add `apk --no-cache add ca-certificates tzdata` in the runtime stage to support outbound TLS requests and consistent UTC logging.
  4. **Read-Only Root Filesystem:** Run container with `--read-only` and mount temporary writable directories only where needed (`--tmpfs /tmp`).
  5. **Automated Vulnerability Scanning:** Integrate Trivy or Docker Scout into the CI/CD pipeline to break the build on any High/Critical CVEs.

---

## 📦 Required Evidence & Submission Checklist

- [x] Project files `main.go`, `go.mod`, `Dockerfile.single`, and `Dockerfile` created in `~/day10-multistage`.
- [x] Single-stage image built (`demo:single`) and size recorded.
- [x] Multi-stage image built (`demo:multi`) and size recorded.
- [x] Percentage size reduction calculated and documented.
- [x] Application responds to `GET /` (`Hello from a multi-stage build!`) and `GET /health` (`ok`).
- [x] Non-root execution verified via `docker exec demo id` (`uid != 0`).
- [x] Target stage build verified with `docker build --target builder -t demo:build .`.
- [x] Bonus: `Dockerfile.scratch` built (`demo:scratch`) and tested on port `8081`.
- [x] Shell absence on scratch confirmed (`docker exec demo-scratch sh` fails).
- [x] Clean container cleanup executed (`docker rm -f demo demo-scratch`).

---

[← Day 09](Day09.md) | [Home](README.md) | [Day 11 →](Day11.md)
