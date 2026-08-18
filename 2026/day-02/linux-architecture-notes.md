# 90_Days_Of_DevOps - Day 02 : Linux Architecture Notes

## What is Linux?

Linux is an open-source OS created by Linus Torvalds in 1991.
It's used in servers, supercomputers, and most of the cloud infrastructure we work with.
The kernel is maintained by a global open-source community and comes in many distros (Ubuntu, CentOS, Arch, etc.).

---

## Why Linux?

**Versatility:** Linux can run on anything — from tiny IoT devices to large-scale cloud apps.
It's open-source, so you're never locked into one vendor's ecosystem.

**Security:** Every part of the OS can be monitored and controlled.
SELinux (built into the kernel since 2003) gives admins fine-grained control over user and app permissions.

**Community:** A huge global community means you'll always find help, docs, or an open-source tool for whatever problem you're solving.

---

## What does Linux include?

**Kernel:** The core of the OS — manages memory, processes, files, and hardware communication. Without it, nothing works.

**System User Space:** The layer where you interact with the system — shell (command line), daemons (background services), and the desktop environment.

**Applications:** Programs that run on top of the OS — editors, web servers, Docker, programming tools, etc.

**Shell:** The command-line interpreter that lets you talk to the kernel. Common shells: Bash, Zsh, Fish.

**Daemons:** Background services that run continuously. Examples: `sshd` (SSH), `nginx` (web server), `crond` (cron jobs).

**init/systemd:** The first process Linux starts after the kernel loads (PID 1).
It starts and manages all other services and processes on the system.

---

## How Processes Are Created and Managed

A process is a running instance of a program. Every process in Linux starts from another process — this is called **forking**.
When you run a command, the shell forks itself to create a child process that runs it.
Each process gets a unique **PID** (Process ID).

**Process States:**

| State | What it means |
|---|---|
| Created | Process launched; data structures being set up |
| Ready | Waiting for its turn on the CPU |
| Running (R) | Actively executing on the processor |
| Sleeping (S) | Waiting for input or a resource |
| Stopped (T) | Paused, usually by Ctrl+Z |
| Zombie (Z) | Finished, but parent hasn't read its exit status yet |
| Orphan | Parent terminated; re-parented to init (PID 1) |
| Terminated | Fully finished; all resources cleaned up |


Use `ps aux` to list all processes, or `top` to watch them live.

---

## What systemd Does and Why It Matters

**systemd** is the init system — it's the first thing that runs after the kernel, and it manages every service on the machine.

Key systemd commands:
- `systemctl start/stop/restart <service>` — control a service
- `systemctl enable <service>` — start it automatically on boot
- `systemctl status <service>` — check if it's running
- `journalctl -u <service>` — read its logs

Why it matters: if a service crashes in production, `systemctl status` and `journalctl` are the first two commands you run.

---

## 5 Commands I'll Use Daily

| Command | What it does |
|---|---|
| `ps aux` | List all running processes with CPU/memory usage |
| `top` | Live view of system resource usage |
| `systemctl status <service>` | Check if a service is running or failed |
| `journalctl -u <service>` | Read logs for a specific service |
| `kill <PID>` | Stop a process by its Process ID |