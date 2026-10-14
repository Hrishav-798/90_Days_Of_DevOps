# DevOps Winter Arc — Day 13: Docker Security & Optimization

> **90 Days of DevOps Challenge | Containers Week | Learn • Scan • Fix • Prove**  
> **Topic: Trivy vulnerability scanning, slim images, secrets hygiene, non-root containers, multi-stage builds, and runtime hardening**

---

## 🎯 Goal for Today

Today I took an intentionally unsafe Flask image and rebuilt it as a smaller, hardened v2. I scanned both images with Trivy, removed unsafe patterns, ran the application as a non-root user, and validated runtime restrictions with Docker.

### 🗺️ Today's Mission Blueprint

1. Build and inspect an intentionally vulnerable image.
2. Save a Trivy baseline report and identify the risks.
3. Build a slim multi-stage image that runs as a non-root user.
4. Scan the new image and compare size and vulnerability findings.
5. Run the image with resource limits and least-privilege restrictions.
6. Prove the application still works under those restrictions.

---

## 📖 Key Concepts

### 1. Why container security matters

A container image includes the application code, language runtime, operating-system packages, and dependencies. Every unnecessary package increases the attack surface and patching work. Security must include the image build process and the way the container runs.

### 2. Docker image security principles

| Risk | Why it matters | Remediation used in this lab |
| :--- | :--- | :--- |
| Floating image tag | `latest` can change between builds | Used `python:3.12-slim` |
| Root user | A compromised process has unnecessary privileges | Created and used the `app` user |
| Secret in image | Values in `ENV`, `ARG`, or layers can be extracted | Passed the fake token only at runtime |
| Large image | More packages mean more CVEs and slower pulls | Used a slim multi-stage build |
| No vulnerability scan | Known CVEs can go unnoticed | Scanned before and after with Trivy |
| Unrestricted runtime | A process can consume host resources or persist files | Applied resource and privilege restrictions |

### 3. Multi-stage build pattern

Multi-stage builds separate dependency installation from the runtime image. Only the installed Python dependencies and application code are copied into the final stage; build tooling is not shipped.

```dockerfile
FROM python:3.12-slim AS build
WORKDIR /w
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
COPY --from=build /install /usr/local
COPY app.py .
CMD ["python", "app.py"]
```

### 4. Runtime hardening controls

| Flag | Purpose |
| :--- | :--- |
| `--memory 256m` | Caps memory use at 256 MB |
| `--cpus 0.5` | Limits the process to half a CPU |
| `--pids-limit 100` | Helps protect against fork bombs |
| `--read-only` | Prevents writes to the root filesystem |
| `--tmpfs /tmp` | Provides an approved temporary writable path |
| `--cap-drop ALL` | Removes Linux capabilities not needed by the app |
| `--security-opt no-new-privileges` | Prevents privilege escalation through setuid/setgid binaries |

---

## 🛠️ Hands-On Lab: What I Did

The completed project is stored in [day6-security](day6-security/README.md).

### Step 1: Created the Flask application

The project includes a small Flask application with a root endpoint and a health endpoint.

```python
@app.get("/")
def home():
    return jsonify(message="Docker security lab",
                   environment=os.getenv("APP_ENV", "dev"))

@app.get("/health")
def health():
    return "ok", 200
```

The `.dockerignore` excludes local secrets, reports, Python caches, and virtual environments from the image build context.

### Step 2: Built the intentionally unsafe image

The first image deliberately used `python:latest`, ran as root, installed unnecessary packages, embedded a fake token, and used shell-form `CMD`.

```dockerfile
FROM python:latest
ENV API_TOKEN=abc123-super-secret
RUN apt-get update && apt-get install -y build-essential git curl vim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD python app.py
```

```bash
docker build -f Dockerfile.bad -t my-app:bad .
docker images my-app
docker history --no-trunc my-app:bad
```

Actual result:

```text
my-app:bad   0bd362ab476f   1.76GB disk usage   458MB content
```

`docker history --no-trunc my-app:bad` exposed the deliberately fake `API_TOKEN` value. This demonstrates why secrets must never be placed in a Dockerfile.

### Step 3: Scanned the vulnerable image

```bash
trivy image --severity HIGH,CRITICAL -f json -o reports/before.json my-app:bad
trivy image --severity HIGH,CRITICAL my-app:bad
trivy config .
```

Actual Trivy baseline:

| Scan target | HIGH | CRITICAL |
| :--- | ---: | ---: |
| Debian packages | 397 | 16 |
| Python packages | 4 | 0 |
| **Total** | **401** | **16** |

Trivy configuration scanning found five issues in `Dockerfile.bad`:

- Floating `python:latest` tag
- No non-root `USER`
- No Docker `HEALTHCHECK`
- `apt-get install` without `--no-install-recommends`
- Fake `API_TOKEN` exposed through `ENV`

### Step 4: Created the hardened image

```dockerfile
FROM python:3.12-slim AS build
WORKDIR /w
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
RUN useradd -r -u 10001 app
WORKDIR /app
COPY --from=build /install /usr/local
COPY --chown=app:app app.py .
USER app
EXPOSE 5000
CMD ["python", "app.py"]
```

The fake token was written to a local `token.txt` file, protected with `chmod 600`, and excluded from both Git and the Docker build context.

```bash
printf '%s' 'training-token-only' > token.txt
chmod 600 token.txt
docker build --pull --no-cache -f Dockerfile.good -t my-app:v2 .
```

### Step 5: Compared the images and rescanned v2

```bash
docker images my-app
docker history --no-trunc my-app:v2
trivy image --severity HIGH,CRITICAL -f json -o reports/after.json my-app:v2
trivy image --severity HIGH,CRITICAL my-app:v2
trivy image --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed my-app:v2
trivy config .
```

| Measure | `my-app:bad` | `my-app:v2` | Improvement |
| :--- | ---: | ---: | :--- |
| Disk usage | 1.76 GB | 185 MB | **89.5% smaller** |
| HIGH findings | 401 | 44 | **89.0% reduction** |
| CRITICAL findings | 16 | 0 | **100% reduction** |
| Runtime user | root | `app` (UID 10001) | Non-root |
| Hard-coded secret | Present in image history | Not present | Removed |
| Build tools in runtime | Present | Not present | Removed |

The normal v2 scan reported 44 HIGH findings and no CRITICAL findings. Running Trivy with `--ignore-unfixed` reported zero policy violations, meaning no fix was available for the remaining HIGH findings at scan time.

`Dockerfile.good` has one LOW Trivy configuration finding: no Docker `HEALTHCHECK`. I accepted this for the lab because the application health endpoint was validated during runtime. In production, the deployment platform should have an explicit health or readiness check.

---

## 🔒 Runtime Hardening Validation

### Confirmed non-root execution

```bash
docker run --rm --entrypoint id my-app:v2
docker image inspect my-app:v2 --format '{{.Config.User}}'
```

```text
uid=10001(app) gid=999(app) groups=999(app)
app
```

### Ran the container with restrictions

Port `5000` was already allocated on the host, so I mapped host port `5001` to the application's port `5000`. The service remained accessible only from localhost.

```bash
docker run -d --name safe -p 127.0.0.1:5001:5000 \
  --memory 256m --cpus 0.5 --pids-limit 100 \
  --read-only --tmpfs /tmp \
  --cap-drop ALL --security-opt no-new-privileges \
  -e APP_ENV=lab -e API_TOKEN="$(cat token.txt)" my-app:v2
```

### Validated the application and Docker settings

```text
GET /        → 200 {"environment":"lab","message":"Docker security lab"}
GET /health  → 200 ok

ReadonlyRootfs: true
Memory:          268435456 bytes (256 MB)
NanoCpus:        500000000 (0.5 CPU)
CapDrop:         [ALL]
SecurityOpt:     [no-new-privileges]
```

`docker stats --no-stream safe` showed `23.64MiB / 256MiB` memory usage and one process. The logs showed successful `GET /` and `GET /health` requests with HTTP 200 responses.

After validation, I removed the test container and the local token:

```bash
docker rm -f safe
rm -f token.txt
```

---

## 🚨 Troubleshooting Notes

### Port 5000 already allocated

Another process already owned host port 5000. I used `-p 127.0.0.1:5001:5000`; only the host-side port changed.

### Trivy still reports HIGH findings after hardening

This does not automatically mean the lab failed. Check whether a fixed version exists with `--ignore-unfixed`, record the result, and rebuild regularly when the base image receives security updates.

### Why removing a secret from the Dockerfile is not enough

Old image layers, local caches, CI artifacts, and registries can retain it. A real exposed secret must be rotated immediately.

---

## 🎤 Interview Questions

### How do you secure a Docker image?

Use a maintained minimal base image, remove unnecessary packages, use multi-stage builds, run as a non-root user, never bake secrets into layers, scan continuously, and apply runtime restrictions.

### Why use `--cap-drop ALL`?

Containers receive Linux capabilities by default. Dropping them reduces the kernel-level privileges available to a compromised application. Add back only the specific capability an application requires.

### What does `--read-only` protect against?

It makes the container root filesystem immutable. A compromised process cannot alter binaries, configuration, or create normal filesystem persistence; writable paths should be explicitly mounted only where needed.

### Why use a slim image?

A slim image contains fewer packages, which reduces image size, pull time, attack surface, and the number of dependencies that need security patching.

---

[← Day 12](Day12.md) | [Home](README.md)
