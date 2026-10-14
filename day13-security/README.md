# Day 13 — Docker Security & Optimization

This lab hardens a deliberately unsafe Flask image and records the evidence before and after remediation.

## Results

| Measure | `my-app:bad` | `my-app:v2` | Improvement |
| :--- | ---: | ---: | :--- |
| Disk usage | 1.76 GB | 185 MB | 89.5% smaller |
| HIGH findings | 401 | 44 | 89.0% fewer |
| CRITICAL findings | 16 | 0 | 100% fewer |
| Runtime user | root | `app` (UID 10001) | Non-root |

The normal v2 scan still reports 44 HIGH findings. The policy scan with `--ignore-unfixed` reports zero findings, so no fix is currently available for those remaining findings.

## Remediations

- Replaced `python:latest` with `python:3.12-slim`.
- Used a multi-stage build so only runtime dependencies reach the final image.
- Removed build tools, editors, and the hard-coded API token from the final image.
- Added a dedicated non-root user (`app`, UID 10001).
- Used exec-form `CMD`.
- Passed the fake API token at runtime only.
- Applied memory, CPU, PID, read-only filesystem, capability-drop, and no-new-privileges restrictions.

## Evidence

- [`reports/before.json`](reports/before.json): Trivy baseline report.
- [`reports/after.json`](reports/after.json): Trivy report for the hardened v2 image.
- `docker history --no-trunc my-app:bad` exposed the deliberately fake `API_TOKEN` in the bad image.
- `docker run --rm --entrypoint id my-app:v2` returned `uid=10001(app)`.
- The hardened container served `/` and `/health` successfully through `127.0.0.1:5001`.
- `docker inspect` confirmed `ReadonlyRootfs=true`, a 256 MB memory limit, 0.5 CPU, `CapDrop=[ALL]`, and `no-new-privileges`.

## Run the Lab

```bash
docker build -f Dockerfile.bad -t my-app:bad .
trivy image --severity HIGH,CRITICAL -f json -o reports/before.json my-app:bad

docker build --pull --no-cache -f Dockerfile.good -t my-app:v2 .
trivy image --severity HIGH,CRITICAL -f json -o reports/after.json my-app:v2
```

`token.txt` is ignored by Git and must never contain a real credential.
