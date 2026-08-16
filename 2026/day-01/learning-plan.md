# 90 Days of DevOps – Learning Plan

## Current Level *(Starting Point — Day 1)*

3rd year B.Tech Computer Science student.

| Skill | Prior Experience | Goal After 90 Days |
|---|---|---|
| Linux commands | Comfortable | Deep troubleshooting fluency |
| AWS (EC2, IAM, S3, VPC, CloudFront) | Hands-on | Add EKS, IAM roles for services, cost control |
| Git / GitHub | Intermediate | GitOps workflows, advanced branching |
| Docker | Done real projects with it | Cement internals: networking, layers, Compose |
| CI/CD pipelines | Beginner | Build full pipelines from scratch |
| Kubernetes | Not started | Deploy, debug, and scale production workloads |
| Terraform / IaC | Not started | Provision EKS + VPC with reusable modules |
| Ansible | Not started | Automate server configuration |
| Observability | Not started | Prometheus + Grafana + Loki stack |

> **Starting from Day 1 deliberately.** Even though I've worked with Docker,
> Git, and Linux before, going through the full curriculum builds the structured
> depth that real-world tinkering alone doesn't give. The goal is to do every
> day properly — not to rush past things I think I know.

---

## My Understanding of DevOps & Cloud Engineering

DevOps is the practice of breaking down the wall between development and
operations — automating build, test, and deployment pipelines so software
ships faster and more reliably. Cloud engineering is about designing and
running the infrastructure (compute, storage, networking) that applications
run on, in a scalable and cost-efficient way.

Together, they're about **owning software from code to production** — not
just writing it.

---

## Why I'm Doing This

I want to move beyond just writing code and understand how real systems
are deployed, scaled, and kept reliable at scale.

That requires practical, demonstrable skills — not just certifications.

---

## Where I Want to Be by Day 90

- [ ] Deploy and manage a production-grade multi-service app on Kubernetes
- [ ] Build a complete CI/CD pipeline: code → build → test → Docker push → deploy to K8s
- [ ] Provision cloud infrastructure with Terraform (EKS cluster included)
- [ ] Set up observability: Prometheus + Grafana dashboards for a real app
- [ ] Have a GitOps-based deployment live (ArgoCD + GitHub Actions)
- [ ] A single end-to-end project I can walk through confidently in any interview

---

## 3 Core Goals (Full 90 Days)

1. **CI/CD mastery** — Build a real, multi-stage pipeline (GitHub Actions)
   that builds Docker images, runs tests, and deploys to Kubernetes automatically
2. **Kubernetes in production** — Go beyond `kubectl apply`. Understand
   namespaces, services, HPA, PVCs, ConfigMaps, Secrets, and Helm charts
3. **Infrastructure as Code** — Write Terraform modules that provision
   real AWS infrastructure (VPC, EKS) and can be reused across environments

---

## 3 Skills That Will Differentiate Me in Interviews

1. **End-to-end CI/CD** — most candidates only know one piece; I want to explain
   the whole pipeline from push to production
2. **Kubernetes debugging** — being able to read logs, describe pods, identify
   crash loops, and fix issues independently (not just run `kubectl apply`)
3. **Terraform + GitOps** — knowing how infrastructure is provisioned AND
   how app deployments are managed declaratively (ArgoCD)

---

## Phase Breakdown (All 90 Days)

### Phase 1 — DevOps Intro + Linux + Networking + Scripting (Days 1–21) 🟡 In Progress
- What DevOps actually is — not just a buzzword, but a culture and toolchain
- Core Linux internals: processes, systemd, file systems, user/group management
- Shell scripting for automation: log rotation, backup scripts, cron jobs
- Networking: DNS, ports, subnets — enough to troubleshoot production incidents

**Goal:** Be comfortable SSHing into a broken server and diagnosing what's wrong
without Googling every command.

### Phase 2 — Git Deep Dive (Days 22–28)
- Branching strategies (GitFlow, trunk-based)
- Advanced Git: rebase, stash, cherry-pick, reset vs revert
- GitHub CLI — manage PRs and repos from the terminal

**Goal:** Be the person on a team who can resolve messy merge conflicts and
explain branching strategies clearly.

### Phase 3 — Docker (Days 29–37)
- Container fundamentals from first principles: image layers, the union filesystem
- Dockerfile best practices: multi-stage builds, `.dockerignore`, non-root users
- Docker volumes, networking (bridge, host, overlay)
- Docker Compose for local multi-service dev environments
- Push to DockerHub / ECR; understand image tagging and versioning

**Goal:** Even with prior Docker experience, use this phase to understand *why*
things work — not just *how* to run commands. Write a Dockerfile from memory,
explain layer caching, and debug a broken container without hints.

### Phase 4 — CI/CD with GitHub Actions (Days 38–49) 
- YAML syntax, triggers, matrix builds, secrets management
- Build → test → push Docker image to DockerHub / ECR in a single workflow
- Self-hosted runners, reusable workflows
- **DevSecOps:** Add Trivy image scanning to the pipeline

**Goal:** By Day 48, have a GitHub Actions pipeline that automatically builds,
tests, scans, and deploys a containerised app. This is resume-worthy.

### Phase 5 — Kubernetes (Days 50–60) 
- Architecture: control plane, etcd, kubelet, kube-proxy
- Core objects: Pods, Deployments, Services, ConfigMaps, Secrets, PVCs
- StatefulSets, resource limits, liveness/readiness probes, HPA
- Helm package manager

**Goal:** Deploy the same multi-service app I Dockerized, now on Kubernetes,
with proper health checks, resource limits, and a Helm chart.

### Phase 6 — Terraform (Days 61–67)
- HCL syntax, providers, state management, remote backends (S3 + DynamoDB)
- Modules: write reusable infrastructure code
- Provision an EKS cluster end-to-end with Terraform

**Goal:** Never click through the AWS console to create infrastructure again.
Everything should be code-reviewable, version-controlled, and repeatable.

### Phase 7 — Ansible (Days 68–72)
- Inventory, playbooks, roles, Vault for secrets
- Automate Docker and Nginx deployment across servers

**Goal:** Understand configuration management well enough to explain why it
exists alongside Terraform (provisioning vs. configuration).

### Phase 8 — Observability (Days 73–77)
- Prometheus metrics, Node Exporter, cAdvisor
- Grafana dashboards from scratch
- Loki + Promtail for log aggregation
- OpenTelemetry basics, alerting rules

**Goal:** Build a Grafana dashboard that monitors a live app — CPU, memory,
request rate, error rate. Make it look good. Screenshot it for your resume.

### Phase 9 — Helm + EKS + GitOps (Days 78–86)
- Custom Helm chart for a real multi-service app
- EKS with Terraform: networking, Gateway API, persistent storage
- ArgoCD: GitOps-based continuous delivery, sync strategies, rollbacks
- End-to-end: code push → GitHub Actions → Docker image → ArgoCD → EKS

**Goal:** Have a GitOps pipeline live on EKS that redeploys automatically on
every push to `main`. This is the capstone.

### Phase 10 — Agentic AI for DevOps (Days 87–89)
- LangChain agents for DevOps automation
- MCP (Model Context Protocol) in real workflows
- KubeHealer: AI-driven Kubernetes incident response

**Goal:** Understand where AI fits in the DevOps lifecycle. This is a future
differentiator — know it early.

---

## Weekly Time Budget

| Day type | Hours |
|---|---|
| Weekdays | 2–2.5 hrs (mornings or after class) |
| Weekends | 4–6 hrs (project work, catching up) |
| **Total** | **~20 hrs/week** |

---

## Accountability System

- **Daily commit** to my fork before the day ends — even if it's notes only
- **Weekly LinkedIn post** documenting what I actually built (not just learned)
- **One project screenshot / demo** per phase posted publicly
- **Interview prep rule:** After each phase, write 3 questions an interviewer
  might ask about that phase — and answer them in writing

---

## Interview Prep Targets (By End of 90 Days)

| Role | Must be able to explain |
|---|---|
| DevOps Intern | Docker, GitHub Actions, basic Linux troubleshooting, Git |
| DevOps Engineer (entry) | Full CI/CD pipeline, Kubernetes fundamentals, Terraform basics |
| SRE (junior) | Observability stack, incident response, SLOs/SLIs concept |

---

## Lessons Learned So Far

- Docker multi-stage builds matter more than `docker pull` and `docker run`
- The `ENTRYPOINT` vs `CMD` distinction bites everyone — I've fixed it in real code
- Non-root users in containers are a security non-negotiable in production
- Reading Dockerfiles from real open-source projects is the fastest way to level up
- When stuck, `docker logs`, `docker inspect`, and `docker exec -it` solve 80% of issues

---

