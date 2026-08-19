# 90_Days_Of_DevOps - Day 03 : Linux Commands Cheatsheet

---

## 1. Basic / Navigation Commands

| Command | Description |
|---|---|
| `ls` | List files and directories |
| `ls -la` | List all files (including hidden) with details |
| `cd <dir>` | Change directory |
| `cd ..` | Go one directory up |
| `cd ~` | Go to home directory |
| `pwd` | Print current working directory |
| `clear` | Clear the terminal screen |
| `man <cmd>` | Show manual/help page for a command |
| `<cmd> --help` | Show quick help for a command |
| `history` | Show command history |
| `echo <text>` | Print text to terminal |
| `whoami` | Show current logged-in user |
| `date` | Show current date and time |
| `ncal` | Show calendar in the terminal |
| `uptime` | Show how long the system has been running |

---

## 2. File Management Commands

| Command | Description |
|---|---|
| `touch <file>` | Create an empty file |
| `mkdir <dir>` | Create a new directory |
| `mkdir -p a/b/c` | Create nested directories |
| `rm <file>` | Remove a file |
| `rm -r <dir>` | Remove a directory and its contents |
| `rm -rf <dir>` | Force remove (no prompt) — use carefully! |
| `rmdir <dir>` | Remove an empty directory |
| `cp <src> <dst>` | Copy a file |
| `cp -r <src> <dst>` | Copy a directory recursively |
| `mv <src> <dst>` | Move or rename a file/directory |
| `cat <file>` | Display file contents |
| `less <file>` | View file page by page |
| `head <file>` | Show first 10 lines of a file |
| `tail <file>` | Show last 10 lines of a file |
| `tail -f <file>` | Follow file in real-time (great for logs) |
| `nano <file>` | Open file in nano text editor |
| `vim <file>` | Open file in vim editor |
| `find / -name <file>` | Find a file by name |
| `locate <file>` | Quickly find a file (uses index) |
| `wc -l <file>` | Count lines in a file |
| `diff <f1> <f2>` | Compare two files |
| `ln -s <target> <link>` | Create a symbolic link |
| `stat <file>` | Display detailed file status (size, permissions, timestamps) |
| `file <file>` | Detect and display the file type (text, binary, etc.) |
| `echo "text" > file` | Create/overwrite a file with text (stdout redirect) |
| `echo "text" >> file` | Append text to a file without overwriting |
| `sort <file> > output` | Sort file contents and save to another file |
| `vi <file>` | Open file in vi editor |

---

## 3. File Permissions Commands

| Command | Description |
|---|---|
| `ls -l` | View file permissions |
| `chmod +x <file>` | Make a file executable (e.g. scripts) |
| `chmod 755 <file>` | rwx for owner, rx for others — common for dirs/scripts |
| `chmod 644 <file>` | rw for owner, r for others — common for config files |
| `chmod -R 755 <dir>` | Recursively set permissions on a directory |
| `chown user:group <file>` | Change file owner and group |
| `sudo <command>` | Run a command with root privileges |
| `su <user>` | Switch to another user |
| `stat <file>` | Show file permissions, owner, and timestamps |
| `umask` | Show default permission mask |

### Permission Number Reference  

| Number | Permission | Meaning |
|---|---|---|
| `7` | `rwx` | Read + Write + Execute |
| `6` | `rw-` | Read + Write |
| `5` | `r-x` | Read + Execute |
| `4` | `r--` | Read only |
| `0` | `---` | No permissions |

> Example: `chmod 755` → owner=7(rwx), group=5(r-x), others=5(r-x)

---

## 4. Process Management Commands

| Command | Description |
|---|---|
| `ps aux` | Show all running processes with details (user, PID, CPU%, MEM%) |
| `ps aux \| grep <name>` | Filter processes by name |
| `top` | Live view of processes sorted by CPU usage |
| `htop` | Interactive process viewer — navigate, kill, renice (install separately) |
| `pgrep <name>` | Find PID(s) of a process by name |
| `kill <PID>` | Gracefully terminate a process (SIGTERM) |
| `kill -9 <PID>` | Force kill a process (SIGKILL — use when graceful fails) |
| `pkill <name>` | Kill all processes matching a name/pattern |
| `killall <name>` | Kill all processes with an exact name |
| `nohup <cmd> &` | Run a command that persists after logout (immune to HUP signal) |
| `nice -n 10 <cmd>` | Start a command with lower CPU priority (range: -20 high to 19 low) |
| `renice -n 5 -p <PID>` | Change priority of an already-running process |
| `watch -n 2 <cmd>` | Re-run a command every 2 seconds (e.g., `watch -n 2 df -h`) |
| `timeout 30 <cmd>` | Run a command and auto-kill it after 30 seconds |
| `lsof -p <PID>` | List all files/sockets opened by a process |
| `lsof -i :<port>` | Find which process is using a specific port |
| `strace -p <PID>` | Trace system calls of a running process (useful for debugging) |
| `systemctl start <svc>` | Start a systemd service |
| `systemctl stop <svc>` | Stop a systemd service |
| `systemctl restart <svc>` | Restart a service (stop + start) |
| `systemctl reload <svc>` | Reload config without restarting (e.g., nginx) |
| `systemctl status <svc>` | Check service status and recent logs |
| `systemctl enable <svc>` | Enable service to auto-start on boot |
| `systemctl disable <svc>` | Disable service from auto-starting on boot |
| `systemctl list-units --type=service` | List all active/loaded services |
| `journalctl -u <svc>` | View logs for a specific service |
| `journalctl -u <svc> -f` | Follow (tail) live logs for a service |
| `journalctl -u <svc> --since "1 hour ago"` | View logs from the last hour |

---

## 5. Network Commands

| Command | Description |
|---|---|
| `ping -c 4 <host>` | Test connectivity with 4 packets |
| `curl -I <url>` | Fetch HTTP response headers only |
| `curl -o <file> <url>` | Download a file using curl |
| `curl -X POST -d '{...}' <url>` | Send a POST request (API testing) |
| `wget <url>` | Download a file from the internet |
| `ip a` | Show all network interfaces and IP addresses |
| `ip r` | Show routing table |
| `ip link set <iface> up/down` | Bring a network interface up or down |
| `ss -tuln` | Show all open ports and listening services (modern) |
| `ss -tulnp` | Same but also shows the process using each port |
| `traceroute <host>` | Trace the network path to a host |
| `dig <domain>` | Detailed DNS lookup (preferred over nslookup) |
| `dig <domain> +short` | Quick DNS lookup — just the IP |
| `nmap -sV <host>` | Scan open ports and service versions on a host |
| `ssh user@host` | Connect to a remote server via SSH |
| `ssh -i <key.pem> user@host` | SSH with a private key file (e.g., AWS EC2) |
| `scp <file> user@host:/path` | Securely copy a file to a remote server |
| `rsync -avz <src> <dst>` | Sync files efficiently (skip unchanged files) |
| `rsync -avz --delete <src> <dst>` | Sync and delete files removed from source |
| `hostname -I` | Show the machine's IP address |
| `ufw status` | Check firewall rules (Ubuntu) |
| `ufw allow <port>` | Allow traffic on a port through the firewall |
| `iptables -L -n` | List all firewall rules (low-level)

---

## 6. Disk & System Info Commands

| Command | Description |
|---|---|
| `df -h` | Show disk usage of all mounted filesystems |
| `df -h /` | Check remaining space on root partition |
| `du -sh <dir>` | Show total size of a directory |
| `du -sh * \| sort -rh \| head -10` | Top 10 largest items in current directory |
| `free -h` | Show RAM and swap usage |
| `lscpu` | Show CPU model, cores, threads |
| `lsblk` | Show block devices and disk partitions |
| `lsblk -f` | Show filesystems on each partition |
| `mount \| column -t` | Show mounted filesystems, formatted |
| `uname -r` | Show kernel version |
| `uname -a` | Show full OS/kernel/architecture info |
| `cat /etc/os-release` | Show distro name and version (universal) |
| `uptime` | Show system uptime and load averages |
| `vmstat 1 5` | System performance stats — 5 samples, 1s apart |
| `iostat -x 1` | Per-disk I/O stats (requires `sysstat`) |
| `iotop` | Live view of disk I/O per process |
| `dmesg -T \| tail -20` | Recent kernel messages with timestamps |
| `cat /proc/meminfo` | Detailed memory usage from kernel |
| `cat /proc/cpuinfo` | Detailed CPU info from kernel |

---

## 7. Package Management (Ubuntu/Debian)

| Command | Description |
|---|---|
| `sudo apt update` | Refresh the package list from repositories |
| `sudo apt upgrade` | Upgrade all installed packages |
| `sudo apt install <pkg>` | Install a package |
| `sudo apt install -y <pkg>` | Install without confirmation prompt (used in scripts) |
| `sudo apt remove <pkg>` | Remove a package (keeps config files) |
| `sudo apt purge <pkg>` | Remove a package and its config files |
| `sudo apt autoremove` | Remove unused dependency packages |
| `apt-cache search <keyword>` | Search available packages by keyword |
| `apt-cache show <pkg>` | Show package details (version, deps, description) |
| `dpkg -l \| grep <pkg>` | Check if a specific package is installed |
| `dpkg -i <file.deb>` | Install a local `.deb` package |
| `which <cmd>` | Show full path of an installed command |
| `type <cmd>` | Show whether a command is a binary, alias, or builtin |

---

## 8. Text Processing Commands

| Command | Description |
|---|---|
| `grep "text" <file>` | Search for a pattern in a file |
| `grep -r "text" <dir>` | Recursive search through a directory |
| `grep -i "text" <file>` | Case-insensitive search |
| `grep -n "text" <file>` | Show line numbers alongside matches |
| `grep -v "text" <file>` | Invert match — show lines that do NOT match |
| `grep -E "pat1\|pat2" <file>` | Match multiple patterns (extended regex) |
| `awk '{print $1}' <file>` | Extract the first column from text |
| `awk -F: '{print $1, $3}' <file>` | Use custom delimiter and extract multiple fields |
| `sed 's/old/new/g' <file>` | Replace all occurrences of a pattern in a file |
| `sed -i 's/old/new/g' <file>` | Replace in-place (edits the file directly) |
| `cut -d: -f1 <file>` | Cut a specific field using a delimiter |
| `sort <file>` | Sort lines alphabetically |
| `sort -rn <file>` | Sort numerically in reverse (e.g., largest first) |
| `uniq -c <file>` | Remove duplicates and count occurrences |
| `sort <file> \| uniq -c \| sort -rn` | Count + rank unique lines (log analysis pattern) |
| `tee <file>` | Read from stdin and write to both stdout and a file |
| `xargs <cmd>` | Build and execute commands from stdin input |
| `wc -l <file>` | Count number of lines in a file |

---

## 9. Archiving & Compression

| Command | Description |
|---|---|
| `tar -czvf file.tar.gz <dir>` | Create a compressed `.tar.gz` archive |
| `tar -xzvf file.tar.gz` | Extract a `.tar.gz` archive |
| `tar -xzvf file.tar.gz -C <dir>` | Extract into a specific directory |
| `tar -tzvf file.tar.gz` | List contents of a `.tar.gz` without extracting |
| `zip -r file.zip <dir>` | Create a zip file from a directory |
| `unzip file.zip` | Extract a zip file |
| `unzip -l file.zip` | List contents of a zip without extracting |
| `gzip <file>` | Compress a file in-place (replaces original) |
| `gunzip <file.gz>` | Decompress a `.gz` file |

---

## 10. User Management Commands

| Command | Description |
|---|---|
| `sudo adduser <name>` | Create a new user (interactive, sets home dir) |
| `sudo useradd -m -s /bin/bash <name>` | Create a user non-interactively (used in scripts) |
| `sudo deluser <name>` | Delete a user account |
| `sudo deluser --remove-home <name>` | Delete a user and their home directory |
| `sudo passwd <name>` | Set or change a user's password |
| `su - <user>` | Switch to another user with their environment |
| `sudo <cmd>` | Run a command as root |
| `sudo -u <user> <cmd>` | Run a command as a specific non-root user |
| `visudo` | Safely edit the sudoers file |
| `sudo usermod -aG <group> <user>` | Add a user to a group (e.g., `docker`, `sudo`) |
| `groups <user>` | Show which groups a user belongs to |
| `id <user>` | Show UID, GID, and all groups for a user |
| `last` | Show recent login history |
| `who` | Show currently logged-in users |
| `w` | Show logged-in users and what they are running |

---

