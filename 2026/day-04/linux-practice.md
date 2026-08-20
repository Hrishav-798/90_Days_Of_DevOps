# 🐧 Linux Practice — Day 04

> **Date:** 2026-08-20
> **Goal:** Hands-on practice with essential Linux commands for DevOps

---

## 📁 File & Directory Operations

```bash
# List files with details
ls -lah

# Create nested directories at once
mkdir -p projects/devops/scripts

# Copy a directory recursively
cp -r source/ destination/

# Move / rename a file
mv oldname.txt newname.txt

# Remove a directory and its contents
rm -rf foldername/
```

---

## 🔍 Searching & Finding Files

```bash
# Find files by name
find /home -name "*.log"

# Find files modified in last 7 days
find /var/log -mtime -7

# Search text inside files (grep)
grep -rn "error" /var/log/
```

---

## 📊 Disk & Memory Usage

```bash
# Check disk space usage
df -h

# Check directory size
du -sh /var/log/

# Check memory usage
free -h
```

---

## 🔐 File Permissions

```bash
# Give owner execute permission
chmod u+x script.sh

# Change file owner
chown user:group file.txt

# View file permissions
ls -l filename
```

---

## 📝 Key Takeaways

- `find` is more powerful than `locate` for real-time searches
- Always use `-h` (human-readable) flag with `df` and `du`
- `grep -rn` is your best friend for debugging log files
- `rm -rf` is irreversible — double-check before running!

---

*Part of the [90 Days of DevOps](../../README.md) challenge — 2026*
