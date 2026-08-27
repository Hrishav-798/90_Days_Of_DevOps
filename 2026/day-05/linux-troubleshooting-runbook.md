# Linux Troubleshooting Drill – Day 05

**Target:** `ssh` / `sshd`  
**Date:** 2026-08-27  
**Performed by:** Hrishav  

---

## 1. Environment

```bash
uname -a
```

*Result:* Ubuntu 24.04, kernel 7.0.0 – the system is up‑to‑date.

---

## 2. Verify we can write to disk

```bash
mkdir -p /tmp/runbook-demo
cp /etc/hosts /tmp/runbook-demo/hosts-copy
ls -l /tmp/runbook-demo
```

*Result:* `hosts-copy` appears in `/tmp`, confirming the filesystem is writable.

---

## 3. CPU & Memory

```bash
free -h
```

*Result:* ~11 GiB RAM, ~5 GiB available, no swap usage – memory pressure is low.

```bash
ps aux | grep ssh
```

*Result:* Only the SSH agent is running; the main `sshd` service is managed by `systemd`.

---

## 4. Disk usage

```bash
df -h /
```

*Result:* Root partition is 25 % full (≈110 GiB used of 469 GiB).

```bash
du -sh /var/log
```

*Result:* Log directory totals ~570 MiB (some sub‑folders require elevated permissions).

---

## 5. Network

```bash
ss -tulpn | head -n 10
```

*Result:* No entry for port 22, indicating the SSH daemon is not listening.

```bash
ping -c 3 8.8.8.8
```

*Result:* All three packets returned, latency between 90 ms and 170 ms – network connectivity is fine.

---

## 6. Service logs

```bash
journalctl -u ssh -n --no-pager
```

*Result:* No recent entries for the SSH service.

---

## 7. Summary

- The host’s hardware resources (CPU, memory, disk, network) are healthy.
- The SSH daemon is currently inactive; no log data is available.
- Filesystem permissions are correct for temporary work.

---

## 8. Next steps if the situation worsens

1. **Check service status** – `systemctl status ssh` to see whether the service is disabled or has failed.
2. **Start or restart** – `sudo systemctl start ssh` (or `restart`) and verify the port appears with `ss -tulpn`.
3. **Enable on boot** – `sudo systemctl enable ssh` so it starts automatically.
4. **Increase log detail** – set `LogLevel DEBUG3` in `/etc/ssh/sshd_config` and reload the daemon.
5. **Deep debugging** – if connections still fail, attach `strace -p <PID>` to the `sshd` process.

---

## 9. Checklist

- [x] Runbook written and saved as `linux-troubleshooting-runbook.md`.
- [x] Changes committed and pushed to the fork.
- [ ] (Optional) Share a short LinkedIn update describing the drill.

---

*End of runbook.*
