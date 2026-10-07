# DevOps Winter Arc — Day 06: Storage + Monitoring + Debugging

> **90 Days of DevOps Challenge | Linux Week | Learn • Practice • Build**  
> **Topic:** Linux Storage Inspection, Disk Usage Analysis, System Health Monitoring & Disk-Full Troubleshooting

---

## 🎯 Mission
Today's mission focuses on Linux storage fundamentals and real-world debugging techniques:
1. Inspect disks, partitions, filesystems, and mount points using `lsblk` and `df`.
2. Hunt down disk space consumers using `du`.
3. Monitor basic system health: memory, uptime/load, and failed services.
4. Create a safe test disk image, format it with ext4, and mount it.
5. Make the mount persistent using `/etc/fstab` with proper validation.
6. Simulate a controlled disk-full production incident.
7. Troubleshoot and resolve the disk-full problem using a repeatable evidence-based framework.

---

## Task 1: Inspect Your Linux Storage

Understanding what disks, partitions, filesystems, and mount points exist on your machine is the first step to managing storage.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `lsblk` | Lists all block devices (disks, partitions, loop devices) in a tree view showing name, size, type, and mount point. |
| `lsblk -f` | Adds filesystem type (`FSTYPE`), label, UUID, and filesystem available space (`FSAVAIL`) columns. |
| `df -h` | Reports filesystem disk space usage in human-readable format (GB/MB). Shows total, used, available, and use%. |
| `df -Th` | Same as `df -h` but also includes the filesystem **type** column (ext4, tmpfs, etc.). |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ lsblk
NAME        MAJ:MIN RM    SIZE RO TYPE MOUNTPOINTS
loop0         7:0    0      4K  1 loop /snap/bare/5
loop1         7:1    0    216M  1 loop /snap/brave/686
loop2         7:2    0  216.1M  1 loop /snap/brave/690
loop4         7:4    0  519.9M  1 loop /snap/code/264
loop5         7:5    0   55.5M  1 loop /snap/core18/2999
loop6         7:6    0   63.8M  1 loop /snap/core20/2866
loop7         7:7    0   55.5M  1 loop /snap/core18/3084
loop8         7:8    0   63.8M  1 loop /snap/core20/2922
loop9         7:9    0     74M  1 loop /snap/core22/2437
loop10        7:10   0     74M  1 loop /snap/core22/2955
loop11        7:11   0   66.8M  1 loop /snap/core24/1643
loop12        7:12   0   66.8M  1 loop /snap/core24/2124
loop13        7:13   0   47.9M  1 loop /snap/cups/1238
loop14        7:14   0  261.1M  1 loop /snap/firefox/8803
loop15        7:15   0  260.8M  1 loop /snap/firefox/8863
loop16        7:16   0   16.4M  1 loop /snap/firmware-updater/216
loop17        7:17   0   16.5M  1 loop /snap/firmware-updater/226
loop18        7:18   0  242.6M  1 loop /snap/gaming-graphics-core24/13
loop19        7:19   0  120.4M  1 loop /snap/gemini-desktop/48
loop20        7:20   0  531.4M  1 loop /snap/gnome-42-2204/247
loop21        7:21   0  531.5M  1 loop /snap/gnome-42-2204/263
loop22        7:22   0  606.1M  1 loop /snap/gnome-46-2404/153
loop23        7:23   0  614.5M  1 loop /snap/gnome-46-2404/164
loop24        7:24   0    395M  1 loop /snap/mesa-2404/1165
loop25        7:25   0   91.7M  1 loop /snap/gtk-common-themes/1535
loop26        7:26   0    402M  1 loop /snap/mesa-2404/1839
loop27        7:27   0 1009.1M  1 loop /snap/onlyoffice-desktopeditors/1220
loop28        7:28   0  174.4M  1 loop /snap/postman/360
loop29        7:29   0   11.8M  1 loop /snap/snap-store/1390
loop30        7:30   0   11.8M  1 loop /snap/snap-store/1427
loop31        7:31   0   50.3M  1 loop /snap/snapd/27738
loop32        7:32   0   44.7M  1 loop /snap/snapd/28254
loop33        7:33   0    828K  1 loop /snap/snapd-desktop-integration/387
loop34        7:34   0    828K  1 loop /snap/snapd-desktop-integration/391
loop35        7:35   0  291.2M  1 loop /snap/steam/271
loop36        7:36   0   60.1M  1 loop /snap/core26/462
loop37        7:37   0   50.7M  1 loop /snap/cups/1262
loop38        7:38   0  529.8M  1 loop /snap/code/268
nvme0n1     259:0    0  476.9G  0 disk 
├─nvme0n1p1 259:1    0    260M  0 part /boot/efi
└─nvme0n1p6 259:2    0  476.7G  0 part /

hrishav@hrishav-LOQ-15IAX9:~$ lsblk -f
NAME        FSTYPE   FSVER LABEL      UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
loop0       squashfs 4.0                                                         0   100% /snap/bare/5
loop1       squashfs 4.0                                                         0   100% /snap/brave/686
loop2       squashfs 4.0                                                         0   100% /snap/brave/690
loop4       squashfs 4.0                                                         0   100% /snap/code/264
loop5       squashfs 4.0                                                         0   100% /snap/core18/2999
loop6       squashfs 4.0                                                         0   100% /snap/core20/2866
loop7       squashfs 4.0                                                         0   100% /snap/core18/3084
loop8       squashfs 4.0                                                         0   100% /snap/core20/2922
loop9       squashfs 4.0                                                         0   100% /snap/core22/2437
loop10      squashfs 4.0                                                         0   100% /snap/core22/2955
loop11      squashfs 4.0                                                         0   100% /snap/core24/1643
loop12      squashfs 4.0                                                         0   100% /snap/core24/2124
loop13      squashfs 4.0                                                         0   100% /snap/cups/1238
loop14      squashfs 4.0                                                         0   100% /snap/firefox/8803
loop15      squashfs 4.0                                                         0   100% /snap/firefox/8863
loop16      squashfs 4.0                                                         0   100% /snap/firmware-updater/216
loop17      squashfs 4.0                                                         0   100% /snap/firmware-updater/226
loop18      squashfs 4.0                                                         0   100% /snap/gaming-graphics-core24/13
loop19      squashfs 4.0                                                         0   100% /snap/gemini-desktop/48
loop20      squashfs 4.0                                                         0   100% /snap/gnome-42-2204/247
loop21      squashfs 4.0                                                         0   100% /snap/gnome-42-2204/263
loop22      squashfs 4.0                                                         0   100% /snap/gnome-46-2404/153
loop23      squashfs 4.0                                                         0   100% /snap/gnome-46-2404/164
loop24      squashfs 4.0                                                         0   100% /snap/mesa-2404/1165
loop25      squashfs 4.0                                                         0   100% /snap/gtk-common-themes/1535
loop26      squashfs 4.0                                                         0   100% /snap/mesa-2404/1839
loop27      squashfs 4.0                                                         0   100% /snap/onlyoffice-desktopeditors/1220
loop28      squashfs 4.0                                                         0   100% /snap/postman/360
loop29      squashfs 4.0                                                         0   100% /snap/snap-store/1390
loop30      squashfs 4.0                                                         0   100% /snap/snap-store/1427
loop31      squashfs 4.0                                                         0   100% /snap/snapd/27738
loop32      squashfs 4.0                                                         0   100% /snap/snapd/28254
loop33      squashfs 4.0                                                         0   100% /snap/snapd-desktop-integration/387
loop34      squashfs 4.0                                                         0   100% /snap/snapd-desktop-integration/391
loop35      squashfs 4.0                                                         0   100% /snap/steam/271
loop36      squashfs 4.0                                                         0   100% /snap/core26/462
loop37      squashfs 4.0                                                         0   100% /snap/cups/1262
loop38      squashfs 4.0                                                         0   100% /snap/code/268
nvme0n1                                                                                   
├─nvme0n1p1 vfat     FAT32 SYSTEM_DRV EE32-550B                             238.8M     7% /boot/efi
└─nvme0n1p6 ext4     1.0              b87d3f68-23d8-4751-94cf-66ce3e1e1c6e    321G    26% /

hrishav@hrishav-LOQ-15IAX9:~$ df -h
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           1.2G  3.1M  1.2G   1% /run
/dev/nvme0n1p6  469G  124G  322G  28% /
tmpfs           5.7G   20M  5.7G   1% /dev/shm
tmpfs           5.0M   12K  5.0M   1% /run/lock
efivarfs        268K  188K   76K  72% /sys/firmware/efi/efivars
tmpfs           5.7G     0  5.7G   0% /run/qemu
/dev/nvme0n1p1  256M   18M  239M   7% /boot/efi
tmpfs           1.2G  136K  1.2G   1% /run/user/1000

hrishav@hrishav-LOQ-15IAX9:~$ df -Th
Filesystem     Type      Size  Used Avail Use% Mounted on
tmpfs          tmpfs     1.2G  3.1M  1.2G   1% /run
/dev/nvme0n1p6 ext4      469G  124G  322G  28% /
tmpfs          tmpfs     5.7G   20M  5.7G   1% /dev/shm
tmpfs          tmpfs     5.0M   12K  5.0M   1% /run/lock
efivarfs       efivarfs  268K  188K   76K  72% /sys/firmware/efi/efivars
tmpfs          tmpfs     5.7G     0  5.7G   0% /run/qemu
/dev/nvme0n1p1 vfat      256M   18M  239M   7% /boot/efi
tmpfs          tmpfs     1.2G  136K  1.2G   1% /run/user/1000
```

### 🔍 What I Observed on My System

Looking at the output, here's what I found on my machine:

- **`nvme0n1`** — This is my physical NVMe SSD (Non-Volatile Memory Express). The `nvme` prefix tells me it's connected via the NVMe interface, which is much faster than traditional SATA SSDs (`sda`). The total disk size is **476.9 GB**.
- **`nvme0n1p1`** — The first partition (260 MB), formatted with **vfat (FAT32)**, mounted at `/boot/efi`. This is the EFI System Partition that stores the bootloader (GRUB/systemd-boot) used by UEFI firmware to boot my Linux system.
- **`nvme0n1p6`** — The main partition (476.7 GB), formatted with **ext4**, mounted at `/` (root). This is where my entire Linux system lives — OS files, home directory, installed packages, everything. According to `df -h`, I've used **124 GB out of 469 GB (28%)** with **322 GB still available**.
- **`loop0` through `loop38`** — These are loop devices used by **snap packages**. Each snap (like Firefox, VS Code, Brave, Steam) is packaged as a compressed **squashfs** image and mounted as a read-only loop device. That's why they all show `FSUSE% 100%` — they're compressed read-only images, not filling up.
- **`tmpfs`** entries — These are temporary filesystems stored entirely in **RAM** (not on disk). They're used for `/run`, `/dev/shm`, and session data. They disappear on reboot.
- **UUID `b87d3f68-23d8-4751-94cf-66ce3e1e1c6e`** — This is the unique identifier for my root ext4 filesystem. I'll need this kind of UUID later when working with `/etc/fstab`.

### 📝 Notes & Key Takeaways

- **Block Device:** A raw storage device (physical disk or virtual disk) represented as a file under `/dev/` (e.g., `/dev/sda`, `/dev/nvme0n1`). It provides block-level access to data.
- **Partition:** A logical subdivision of a block device. Example: `/dev/nvme0n1p1` is the first partition of disk `/dev/nvme0n1`.
- **Filesystem:** A structured layer (ext4, xfs, btrfs, etc.) written onto a partition or device that organizes raw blocks into files, directories, permissions, and metadata (inodes).
- **Mount Point:** A directory in the Linux filesystem tree where a filesystem is attached and made accessible. Example: the root filesystem is mounted at `/`, the EFI partition mounts at `/boot/efi`.
- **UUID (Universally Unique Identifier):** A 128-bit identifier assigned when a filesystem is created. Using UUIDs in `/etc/fstab` is preferred over device names (`/dev/nvme0n1p6`) because device names can change across reboots.
- **Loop Devices:** Virtual block devices (`loop0`, `loop1`, ...) that present a file as if it were a physical disk. Snap packages and disk image files use loop devices.

### 🧠 What Is the Difference Between a Disk/Device, a Filesystem, and a Mount Point?

These three concepts confused me initially, but after running `lsblk` and `df`, the difference clicked:

1. **Disk / Block Device** — This is the **physical hardware** (or virtual representation of it). On my machine, `nvme0n1` is the actual NVMe SSD. It's just raw storage — a sequence of blocks with no structure. Think of it as a blank notebook with empty pages. You can't read or write files to it directly; it's just unformatted space. Partitions like `nvme0n1p1` and `nvme0n1p6` divide this raw disk into separate sections.

2. **Filesystem** — This is the **organizational layer** written on top of a partition. When I ran `mkfs.ext4` (or when Ubuntu installed), it created the ext4 filesystem structure: a superblock (metadata about the filesystem), inode tables (metadata about each file — permissions, timestamps, block pointers), a journal (for crash recovery), and data blocks (where actual file contents live). Without a filesystem, the partition is just raw bytes with no concept of "files" or "directories." The filesystem is what turns raw blocks into something usable.

3. **Mount Point** — This is where the filesystem becomes **accessible to users and programs**. My ext4 filesystem on `nvme0n1p6` is mounted at `/`, which means when I do `ls /`, `cd /home`, or write any file, I'm actually reading from and writing to the ext4 filesystem on that NVMe partition. Mounting is the act of attaching a filesystem to a directory in the existing directory tree. Without mounting, the filesystem exists but is invisible and inaccessible.

**In short:** The disk holds the raw storage → the filesystem organizes it into files → the mount point makes it accessible.

```
Physical Layer          Logical Layer           Access Layer
┌──────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Block Device │ ──► │   Filesystem     │ ──► │ Mount Point  │
│  /dev/nvme0n1 │     │   ext4 format    │     │ /            │
│  p6 (476.7G) │     │   (files/dirs/   │     │ (accessible  │
│  (raw blocks) │     │    inodes)       │     │  to users)   │
└──────────────┘     └──────────────────┘     └─────────────┘
```

---

## Task 2: Find Where Disk Space Is Going

`df` tells you **which** filesystem is full. `du` tells you **what** is consuming the space.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `du -sh ~` | Reports the **total** size of your home directory in human-readable format. |
| `du -h --max-depth=1 ~ \| sort -h` | Shows the size of each immediate subdirectory in `~`, sorted smallest to largest. |
| `du -h --max-depth=1 /var 2>/dev/null \| sort -h` | Same for `/var` (logs, cache, packages). `2>/dev/null` suppresses permission errors. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ du -sh ~
69G	/home/hrishav

hrishav@hrishav-LOQ-15IAX9:~$ du -h --max-depth=1 ~ | sort -h
4.0K	/home/hrishav/antigravity-update
4.0K	/home/hrishav/movies
4.0K	/home/hrishav/Music
4.0K	/home/hrishav/Public
4.0K	/home/hrishav/Templates
8.0K	/home/hrishav/.redhat
8.0K	/home/hrishav/day5-app
12K	/home/hrishav/.bridge
12K	/home/hrishav/Desktop
16K	/home/hrishav/.gnome
20K	/home/hrishav/.gitlab
20K	/home/hrishav/.ssh
20K	/home/hrishav/java_dsa
28M	/home/hrishav/.serena
32K	/home/hrishav/.vscode-shared
32K	/home/hrishav/DevOps
40K	/home/hrishav/.cagent
40K	/home/hrishav/.gnupg
40K	/home/hrishav/.minikube
40K	/home/hrishav/.mongodb
44K	/home/hrishav/.password-store
48K	/home/hrishav/.password-store
52M	/home/hrishav/Zidd2
57M	/home/hrishav/kubernetes
60K	/home/hrishav/bct
76K	/home/hrishav/.pki
80M	/home/hrishav/.net
82M	/home/hrishav/Agentic_ai_hrms
85M	/home/hrishav/3_tier_app
122M	/home/hrishav/task-tracker
136M	/home/hrishav/.m2
153M	/home/hrishav/.joplin
233M	/home/hrishav/.nvm
247M	/home/hrishav/Pictures
266M	/home/hrishav/.gradle
269M	/home/hrishav/aws
276K	/home/hrishav/hotstar_churn_analysis
296K	/home/hrishav/.dotnet
328K	/home/hrishav/90_Days_of_DevOps
413M	/home/hrishav/.codex
418M	/home/hrishav/hrms
508K	/home/hrishav/JoplinBackup
699M	/home/hrishav/PrivAI
740K	/home/hrishav/demo_project
775M	/home/hrishav/antigravity-new
984K	/home/hrishav/.claude
1.3G	/home/hrishav/.antigravity
1.4M	/home/hrishav/.copilot
1.5G	/home/hrishav/.antigravity-ide
1.6G	/home/hrishav/chat-application
2.4G	/home/hrishav/.npm
2.9G	/home/hrishav/.gemini
3.1G	/home/hrishav/snap
4.4G	/home/hrishav/.vscode
5.7G	/home/hrishav/.config
6.1M	/home/hrishav/node
6.7G	/home/hrishav/.cache
8.0G	/home/hrishav/.docker
8.6M	/home/hrishav/Finlyt
9.6M	/home/hrishav/LenovoLegionLinux
9.8M	/home/hrishav/Videos
14G	/home/hrishav/.local
14G	/home/hrishav/Downloads
21M	/home/hrishav/Python
69G	/home/hrishav

hrishav@hrishav-LOQ-15IAX9:~$ du -h --max-depth=1 /var 2>/dev/null | sort -h
4.0K	/var/crash
4.0K	/var/local
4.0K	/var/mail
4.0K	/var/metrics
4.0K	/var/opt
12K	/var/www
36K	/var/spool
224K	/var/tmp
5.1M	/var/backups
16M	/var/snap
532M	/var/log
613M	/var/cache
11G	/var/lib
12G	/var
```

### 🔍 What I Observed on My System

My home directory is using **69 GB** total. Breaking it down, the biggest consumers are:

| Directory | Size | What It Is |
| :--- | :--- | :--- |
| `~/Downloads` | 14G | Downloaded files I probably need to clean up |
| `~/.local` | 14G | Local application data (share files, pipx, local bins) |
| `~/.docker` | 8.0G | Docker images, containers, and build cache |
| `~/.cache` | 6.7G | Application caches (browsers, build tools) |
| `~/.config` | 5.7G | Application configuration and data |
| `~/.vscode` | 4.4G | VS Code extensions and workspace data |
| `~/snap` | 3.1G | Snap user data |
| `~/.gemini` | 2.9G | Gemini/Antigravity IDE data |
| `~/.npm` | 2.4G | npm package cache |
| `~/chat-application` | 1.6G | A project directory |

For `/var`, the breakdown shows **`/var/lib`** at **11 GB** (this is where Docker stores its data, apt package info, and snap data), `/var/cache` at **613 MB** (downloaded `.deb` packages), and `/var/log` at **532 MB** (system logs).

**Takeaway:** If I ever needed to free up space quickly, my top targets would be `~/Downloads`, `~/.docker` (running `docker system prune`), `~/.cache`, and `~/.npm` (running `npm cache clean --force`). For `/var`, I could clean old logs with `sudo journalctl --vacuum-time=7d` and clear the apt cache with `sudo apt clean`.

### 📝 Notes & Key Takeaways

- **`df` vs `du` — Why both?**
  - `df` reports from the **filesystem metadata** — it knows total capacity, reserved blocks, and what the kernel considers "used". It answers: *"Is this filesystem running out of space?"*
  - `du` walks the **directory tree** and sums file sizes. It answers: *"Which directories/files are consuming the space?"*
  - They can disagree! If a large file is deleted but still held open by a process, `df` still counts it as used, while `du` won't see it. This is a real production gotcha (covered in Task 8).
- **Typical large directories in `/var`:**
  - `/var/log` — System and application logs (can grow unbounded without log rotation).
  - `/var/cache/apt` — Downloaded `.deb` packages (clean with `sudo apt clean`).
  - `/var/lib/docker` — Docker images, containers, and volumes.
  - `/var/lib/snapd` — Snap package data.

---

## Task 3: Check Basic System Health

A quick health check covers three dimensions: **memory**, **load**, and **service status**.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `free -h` | Displays total, used, free, shared, buff/cache, and available memory (RAM + swap). |
| `uptime` | Shows current time, how long the system has been running, number of logged-in users, and 1/5/15-minute load averages. |
| `systemctl --failed` | Lists all systemd units (services, timers, mounts) in a **failed** state. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ free -h
               total        used        free      shared  buff/cache   available
Mem:            11Gi       6.7Gi       1.1Gi       685Mi       4.7Gi       4.7Gi
Swap:          4.0Gi       1.0Gi       3.0Gi

hrishav@hrishav-LOQ-15IAX9:~$ uptime
 21:21:24 up 46 min,  1 user,  load average: 0.23, 0.36, 0.51

hrishav@hrishav-LOQ-15IAX9:~$ systemctl --failed
  UNIT LOAD ACTIVE SUB DESCRIPTION

0 loaded units listed.
```

### 🔍 What I Observed on My System

- **Memory:** My system has **11 GB total RAM**. Out of that, **6.7 GB is in use** and only **1.1 GB is truly "free"** — but **4.7 GB is "available"**. This is a perfect example of how Linux works: it uses spare RAM for disk caching (`buff/cache` = 4.7 GB), but that cache is reclaimable. So even though `free` looks low, `available` tells me I have plenty of room for new processes. No memory pressure here.
- **Swap:** I have **4.0 GB of swap** and **1.0 GB is used**. Some swap usage is normal — Linux may swap out idle pages to make room for active caches. If swap usage was very high and growing, that would indicate the system is running out of RAM and actively thrashing (bad for performance).
- **Uptime & Load:** My system has been up for **46 minutes** with **1 user** logged in. The load averages are **0.23, 0.36, 0.51** (1-min, 5-min, 15-min). Since my machine has multiple CPU cores, these numbers are very low — the system is essentially idle. The decreasing trend (0.51 → 0.36 → 0.23) tells me the system was slightly busier right after boot and has settled down.
- **Failed Services:** **0 loaded units listed** — no failed services. This is the healthy state I want to see. If anything was failed, I'd investigate with `systemctl status <unit>` and `journalctl -u <unit>`.

### 📝 Notes & Key Takeaways

- **`free -h` — "available" vs "free":**
  - `free` = completely unused RAM.
  - `available` = RAM that can be made available to new processes (includes reclaimable buff/cache). This is the number that matters.
  - Linux aggressively uses "free" RAM for disk caching (`buff/cache`). Low `free` with high `available` is **normal and healthy**.
- **Load Average (from `uptime`):**
  - Three numbers represent average system load over 1, 5, and 15 minutes.
  - A load average equal to the number of CPU cores means the system is fully utilized. Above that indicates overload/queueing.
  - Example: On a 4-core machine, load average `4.0` = 100% utilization, `8.0` = processes are waiting in queue.
- **`systemctl --failed`:**
  - Any failed service should be investigated: `systemctl status <service>` and `journalctl -u <service> --no-pager -n 50`.

---

## Task 4: Create a Safe Test Disk

Instead of modifying a real disk, create a small 100 MB file-based filesystem for safe experimentation.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `sudo mkdir -p /var/lib/day6` | Creates the directory to hold the disk image file. |
| `sudo fallocate -l 100M /var/lib/day6/day6-disk.img` | Allocates a 100 MB file instantly (no actual data written, just space reserved). |
| `sudo mkfs.ext4 /var/lib/day6/day6-disk.img` | Formats the file with the ext4 filesystem. Creates superblock, inode tables, and journal. |
| `sudo mkdir -p /mnt/day6disk` | Creates the mount point directory. |
| `sudo mount -o loop /var/lib/day6/day6-disk.img /mnt/day6disk` | Mounts the image file as a loop device at `/mnt/day6disk`. |
| `df -h /mnt/day6disk` | Verifies the mounted filesystem shows correct size and mount point. |
| `lsblk -f` | Confirms the loop device appears in the block device listing. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo mkdir -p /var/lib/day6
[sudo] password for hrishav: 
hrishav@hrishav-LOQ-15IAX9:~$ sudo fallocate -l 100M /var/lib/day6/day6-disk.img

hrishav@hrishav-LOQ-15IAX9:~$ sudo mkfs.ext4 /var/lib/day6/day6-disk.img
mke2fs 1.47.0 (5-Feb-2023)
Discarding device blocks: done                            
Creating filesystem with 25600 4k blocks and 25600 inodes

Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (1024 blocks): done
Writing superblocks and filesystem accounting information: done

hrishav@hrishav-LOQ-15IAX9:~$ sudo mkdir -p /mnt/day6disk
hrishav@hrishav-LOQ-15IAX9:~$ sudo mount -o loop /var/lib/day6/day6-disk.img /mnt/day6disk

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop3       90M   24K   83M   1% /mnt/day6disk

hrishav@hrishav-LOQ-15IAX9:~$ lsblk -f
NAME        FSTYPE   FSVER LABEL      UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
loop0       squashfs 4.0                                                         0   100% /snap/bare/5
loop1       squashfs 4.0                                                         0   100% /snap/brave/686
loop2       squashfs 4.0                                                         0   100% /snap/brave/690
loop3       ext4     1.0              528756c6-ef96-42a8-9eee-ba9d4ed43f24   82.7M     0% /mnt/day6disk
loop4       squashfs 4.0                                                         0   100% /snap/code/264
loop5       squashfs 4.0                                                         0   100% /snap/core18/2999
loop6       squashfs 4.0                                                         0   100% /snap/core20/2866
loop7       squashfs 4.0                                                         0   100% /snap/core18/3084
loop8       squashfs 4.0                                                         0   100% /snap/core20/2922
loop9       squashfs 4.0                                                         0   100% /snap/core22/2437
loop10      squashfs 4.0                                                         0   100% /snap/core22/2955
loop11      squashfs 4.0                                                         0   100% /snap/core24/1643
loop12      squashfs 4.0                                                         0   100% /snap/core24/2124
loop13      squashfs 4.0                                                         0   100% /snap/cups/1238
loop14      squashfs 4.0                                                         0   100% /snap/firefox/8803
loop15      squashfs 4.0                                                         0   100% /snap/firefox/8863
loop16      squashfs 4.0                                                         0   100% /snap/firmware-updater/216
loop17      squashfs 4.0                                                         0   100% /snap/firmware-updater/226
loop18      squashfs 4.0                                                         0   100% /snap/gaming-graphics-core24/13
loop19      squashfs 4.0                                                         0   100% /snap/gemini-desktop/48
loop20      squashfs 4.0                                                         0   100% /snap/gnome-42-2204/247
loop21      squashfs 4.0                                                         0   100% /snap/gnome-42-2204/263
loop22      squashfs 4.0                                                         0   100% /snap/gnome-46-2404/153
loop23      squashfs 4.0                                                         0   100% /snap/gnome-46-2404/164
loop24      squashfs 4.0                                                         0   100% /snap/mesa-2404/1165
loop25      squashfs 4.0                                                         0   100% /snap/gtk-common-themes/1535
loop26      squashfs 4.0                                                         0   100% /snap/mesa-2404/1839
loop27      squashfs 4.0                                                         0   100% /snap/onlyoffice-desktopeditors/1220
loop28      squashfs 4.0                                                         0   100% /snap/postman/360
loop29      squashfs 4.0                                                         0   100% /snap/snap-store/1390
loop30      squashfs 4.0                                                         0   100% /snap/snap-store/1427
loop31      squashfs 4.0                                                         0   100% /snap/snapd/27738
loop32      squashfs 4.0                                                         0   100% /snap/snapd/28254
loop33      squashfs 4.0                                                         0   100% /snap/snapd-desktop-integration/387
loop34      squashfs 4.0                                                         0   100% /snap/snapd-desktop-integration/391
loop35      squashfs 4.0                                                         0   100% /snap/steam/271
loop36      squashfs 4.0                                                         0   100% /snap/core26/462
loop37      squashfs 4.0                                                         0   100% /snap/cups/1262
loop38      squashfs 4.0                                                         0   100% /snap/code/268
nvme0n1                                                                                   
├─nvme0n1p1 vfat     FAT32 SYSTEM_DRV EE32-550B                             238.8M     7% /boot/efi
└─nvme0n1p6 ext4     1.0              b87d3f68-23d8-4751-94cf-66ce3e1e1c6e    321G    26% /
```

### 🔍 What I Observed on My System

- **`mkfs.ext4` output breakdown:** It created a filesystem with **25,600 blocks** (each 4K = 100 MB total) and **25,600 inodes** (maximum number of files I can create). It also allocated a **journal** (1024 blocks = 4 MB) for crash recovery. No "not a block device" warning appeared this time — newer versions of `mke2fs` silently proceed for regular files.
- **Where did my 100 MB go?** I allocated 100 MB, but `df -h` shows only **90M total** and **83M available**. The ~10 MB difference is consumed by ext4 filesystem overhead: the superblock, inode tables, journal (4 MB), and group descriptors. The remaining gap between 90M and 83M is the 5% reserved space for root (so the filesystem doesn't completely fill up and become unrecoverable).
- **Loop device `loop3`:** My disk image got assigned to `/dev/loop3` — the first available loop device number. In `lsblk -f`, I can see it's the only loop device with `ext4` filesystem (all the snap loop devices use `squashfs`). Its UUID is `528756c6-ef96-42a8-9eee-ba9d4ed43f24` — I'll need this for the `/etc/fstab` entry in Task 5.
- **Mount verified:** `df -h /mnt/day6disk` confirms the filesystem is mounted and accessible at `/mnt/day6disk` with 1% usage (just the `lost+found` directory that ext4 creates automatically).

### 📝 Notes & Key Takeaways

- **`fallocate` vs `dd`:** `fallocate` is instant — it reserves space in the filesystem metadata without writing actual bytes. `dd if=/dev/zero` physically writes zeros, which is slower but guarantees zeroed-out data.
- **Loop Device:** The `-o loop` option tells `mount` to associate the file with a loop device (`/dev/loopN`), which presents the file as a block device to the kernel. This is the same mechanism used by snap packages and ISO images.
- **ext4 Reserved Space:** By default, ext4 reserves 5% of blocks for the root user. On a 100 MB filesystem, this means only ~93 MB is shown as available to regular users.
- **"Not a block device" Warning:** When running `mkfs.ext4` on a file (not `/dev/sdX`), you get a warning. This is expected and safe — you're intentionally formatting a file-based image.

### 🧠 What Just Happened (Visual)

```
fallocate                  mkfs.ext4                 mount -o loop
┌────────────┐          ┌──────────────────┐       ┌──────────────────┐
│ 100 MB file │   ──►   │ ext4 filesystem  │  ──►  │ Accessible at    │
│ (raw bytes) │         │ (superblock +    │       │ /mnt/day6disk    │
│             │         │  inodes + journal│       │                  │
└────────────┘          │  + data blocks)  │       │ $ ls /mnt/day6disk│
                        └──────────────────┘       │ $ touch file.txt │
                                                   └──────────────────┘
```

---

## Task 5: Make the Mount Persistent with /etc/fstab

Without an `/etc/fstab` entry, the filesystem will not automatically mount after a reboot.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `sudo blkid /var/lib/day6/day6-disk.img` | Displays the UUID, filesystem type, and other attributes of the disk image. |
| `sudo nano /etc/fstab` | Opens the filesystem table for editing. Each line defines an automatic mount. |
| `sudo umount /mnt/day6disk` | Unmounts the filesystem to test the fstab entry from scratch. |
| `sudo mount -a` | Mounts all filesystems listed in `/etc/fstab` that are not currently mounted. |
| `df -h /mnt/day6disk` | Verifies the filesystem re-mounted correctly via fstab. |
| `findmnt /mnt/day6disk` | Shows mount details including source, fstype, and options for the mount point. |
| `sudo findmnt --verify` | Validates all `/etc/fstab` entries for correctness (catches typos and invalid UUIDs). |

### 💻 Terminal Output

```bash
# Step 1: Find the UUID of the disk image
hrishav@hrishav-LOQ-15IAX9:~$ sudo blkid /var/lib/day6/day6-disk.img
/var/lib/day6/day6-disk.img: UUID="528756c6-ef96-42a8-9eee-ba9d4ed43f24" BLOCK_SIZE="4096" TYPE="ext4"

# Step 2: Edit /etc/fstab and add persistent mount entry
hrishav@hrishav-LOQ-15IAX9:~$ sudo nano /etc/fstab
# Added line:
# UUID=528756c6-ef96-42a8-9eee-ba9d4ed43f24 /mnt/day6disk ext4 loop,nofail 0 2

# Step 3: Validate BEFORE rebooting
hrishav@hrishav-LOQ-15IAX9:~$ sudo umount /mnt/day6disk
umount: /mnt/day6disk: not mounted.

hrishav@hrishav-LOQ-15IAX9:~$ sudo mount -a
mount: (hint) your fstab has been modified, but systemd still uses
       the old version; use 'systemctl daemon-reload' to reload.

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop3       90M   24K   83M   1% /mnt/day6disk

hrishav@hrishav-LOQ-15IAX9:~$ findmnt /mnt/day6disk
TARGET        SOURCE     FSTYPE OPTIONS
/mnt/day6disk /dev/loop3 ext4   rw,relatime

hrishav@hrishav-LOQ-15IAX9:~$ sudo findmnt --verify
none
   [W] non-bind mount source /swap.img is a directory or regular file
   [W] your fstab has been modified, but systemd still uses the old version;
       use 'systemctl daemon-reload' to reload

0 parse errors, 0 errors, 2 warnings
```

### 🔍 What I Observed on My System

- **Finding the UUID:** `blkid` gave `UUID="528756c6-ef96-42a8-9eee-ba9d4ed43f24"` and `TYPE="ext4"`. Using this exact UUID ensures Linux uniquely identifies this specific filesystem even if the assigned loop device index changes across reboots.
- **The systemd hint (`systemctl daemon-reload`):** When modifying `/etc/fstab` on modern systemd Linux, systemd notices that `/etc/fstab` has changed since the system booted. Systemd internally generates `.mount` units from fstab on the fly using `systemd-fstab-generator`. Running `sudo systemctl daemon-reload` updates systemd's in-memory mount unit cache.
- **`mount -a` verification:** Running `sudo mount -a` after unmounting immediately picked up the fstab entry and remounted `/dev/loop3` onto `/mnt/day6disk` without syntax errors. `df -h /mnt/day6disk` showed the 90M disk healthy at 1% usage.
- **`findmnt --verify` passed with 0 errors:** The initial dry run caught an error when the placeholder was still present (`[E] unreachable on boot required source: UUID=YOUR-UUID`). After fixing it with the real UUID, `sudo findmnt --verify` reported **`0 parse errors, 0 errors, 2 warnings`**. The two warnings are standard cosmetic notices (one about `/swap.img` and one regarding `systemctl daemon-reload`), confirming the fstab entry is 100% syntactically correct and boot-safe!

### 📝 Notes & Key Takeaways

- **`/etc/fstab` Format:**
  ```
  <device/UUID>    <mount-point>    <fstype>    <options>    <dump>    <pass>
  UUID=xxxx...     /mnt/day6disk    ext4        loop,nofail  0         2
  ```
  - `loop` — Required because we're mounting a file image, not a physical device.
  - `nofail` — **Critical safety option**: If the image file is missing or corrupt at boot, the system will still boot instead of dropping to emergency mode.
  - `0` (dump) — Don't include in backup dumps.
  - `2` (pass) — Run `fsck` after root filesystem check (pass 1).

- **⚠️ Golden Rule:** **Never reboot with an untested fstab entry.** A bad entry can prevent the system from booting entirely. Always:
  1. `sudo umount <mount-point>`
  2. `sudo mount -a` (test)
  3. `sudo findmnt --verify` (validate)
  4. Only then reboot (if needed).

- **Why UUID instead of `/dev/loopN`?** Loop device numbers are assigned dynamically at boot and can change. UUIDs are permanent identifiers tied to the filesystem itself.

- **Is a Filesystem UUID Sensitive to Post on GitHub?** **No, it is 100% safe to post.** A UUID is merely a randomly generated 128-bit label created during `mkfs` to differentiate disk partitions. It contains no authentication secrets, credentials, passwords, or network locations. Nobody can access or exploit your machine using a filesystem UUID.

---

## Task 6: Create Test Data

Write controlled data and observe how filesystem usage changes.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `sudo dd if=/dev/zero of=/mnt/day6disk/testfile bs=1M count=40 status=progress` | Writes 40 MB of zeros to a file. `bs=1M` sets block size; `status=progress` shows live throughput. |
| `sync` | Flushes all buffered writes to disk, ensuring `df` reflects accurate usage. |
| `df -h /mnt/day6disk` | Shows filesystem-level usage (includes metadata overhead). |
| `du -sh /mnt/day6disk` | Shows total size of files in the directory (user data only). |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo dd if=/dev/zero of=/mnt/day6disk/testfile bs=1M count=40 status=progress
[sudo] password for hrishav: 
40+0 records in
40+0 records out
41943040 bytes (42 MB, 40 MiB) copied, 0.013946 s, 3.0 GB/s

hrishav@hrishav-LOQ-15IAX9:~$ sync

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop3       90M   41M   43M  49% /mnt/day6disk

hrishav@hrishav-LOQ-15IAX9:~$ du -sh /mnt/day6disk
du: cannot read directory '/mnt/day6disk/lost+found': Permission denied
41M	/mnt/day6disk
```

### 🔍 What I Observed on My System

- **Blazing write speed (3.0 GB/s):** The 40 MiB file wrote in just `0.013946 s` (~3.0 GB/s). This speed happens because Linux writes to page cache (RAM dirty buffers) first rather than direct synchronous disk I/O.
- **The importance of `sync`:** Because modern OS kernels buffer writes in RAM, running `sync` forces all uncommitted dirty buffers to be flushed to `/var/lib/day6/day6-disk.img` before running space checks.
- **Filesystem jump (1% ➔ 49%):** Prior to writing `testfile`, used space was 24 KB. After writing 40 MiB, `df -h` shows **41M used** and **43M available**, putting the filesystem at **49% capacity**.
- **`du` vs `df` alignment:** `du -sh` showed `41M`, matching the `41M` reported by `df -h`.
- **`lost+found` Permission Notice:** Running `du` without `sudo` produced `du: cannot read directory '/mnt/day6disk/lost+found': Permission denied`. This is normal on ext4 because `lost+found` is created with `root:root` `700` (`rwx------`) permissions for recovering corrupted inodes. Even without reading `lost+found`, `du` accurately tallied our 40 MB `testfile`.

### 📝 Notes & Key Takeaways

- **`dd` — Disk Duplicator:** A low-level copy tool. `if` = input file (source), `of` = output file (destination), `bs` = block size, `count` = number of blocks.
- **`/dev/zero`:** A special device that produces an infinite stream of zero bytes. Useful for creating test files of exact sizes.
- **`sync`:** The kernel buffers disk writes for performance. `sync` forces all pending writes to be committed to the underlying storage. Always run before checking `df` for accurate results.
- **Why `df` and `du` might differ:** `df` includes filesystem metadata (journal, inode tables, superblock), while `du` only counts file data. `df` also counts reserved blocks.

---

## Task 7: Create a Controlled 'Disk Full' Incident

Simulate a common production problem: an application fails with `No space left on device`.

### ⚠️ Safety Warning
> **Only write to `/mnt/day6disk`.** Never run this test against `/` or any other important filesystem.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `sudo dd if=/dev/zero of=/mnt/day6disk/fill1 bs=1M count=40 status=progress` | Writes another 40 MB to further fill the 100 MB filesystem. |
| `sudo dd if=/dev/zero of=/mnt/day6disk/fill2 bs=1M count=15 status=progress` | Attempts to write 15 MB more. The filesystem may run out of space mid-write. |
| `df -h /mnt/day6disk` | Confirms the filesystem is at or near 100% usage. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo dd if=/dev/zero of=/mnt/day6disk/fill1 bs=1M count=40 status=progress
40+0 records in
40+0 records out
41943040 bytes (42 MB, 40 MiB) copied, 0.0703638 s, 596 MB/s

hrishav@hrishav-LOQ-15IAX9:~$ sudo dd if=/dev/zero of=/mnt/day6disk/fill2 bs=1M count=15 status=progress
dd: error writing '/mnt/day6disk/fill2': No space left on device
8+0 records in
7+0 records out
7340032 bytes (7.3 MB, 7.0 MiB) copied, 0.0301307 s, 244 MB/s

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop3       90M   88M     0 100% /mnt/day6disk
```

### 🔍 What I Observed on My System

- **`fill1` succeeds:** Writing another 40 MiB completed smoothly, bringing used space to ~81 MB.
- **The classic `ENOSPC` error on `fill2`:** When trying to allocate 15 MiB more, `dd` crashed mid-write:
  `dd: error writing '/mnt/day6disk/fill2': No space left on device`
- **Partial write analysis:** `dd` logged `8+0 records in, 7+0 records out` (`7,340,032 bytes` copied). It successfully wrote 7 full 1 MB blocks before the filesystem completely exhausted its assignable data blocks.
- **Complete saturation (100% / 0 Avail):** `df -h /mnt/day6disk` now shows **Size: 90M, Used: 88M, Avail: 0, Use%: 100%**. The filesystem is in a full disk pressure state—any application trying to write logs, upload files, or create temp files here will crash with HTTP 500 or IO exceptions.

### 📝 Notes & Key Takeaways

- **`No space left on device` (ENOSPC):** The classic Unix error. When a filesystem has no free data blocks, any write operation fails with this error.
- **In production, this manifests as:**
  - Web applications returning HTTP 500 errors.
  - Databases refusing writes or corrupting data.
  - Log files failing to rotate, causing cascading failures.
  - Container orchestrators evicting pods (Kubernetes `DiskPressure`).
- **Why we test in isolation:** Using a dedicated 100 MB test filesystem ensures we never impact the real root (`/`) or any critical data.

---

## Task 8: Troubleshoot the Disk-Full Problem

**Scenario:** A web application reports `No space left on device`. Your job: prove the cause and find the culprit.

### 🩺 Step-by-Step Diagnostic Framework

#### Step 1 — Confirm the Symptom

```bash
hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop3       90M   88M     0 100% /mnt/day6disk
```

#### Step 2 — Check Inode Usage

```bash
hrishav@hrishav-LOQ-15IAX9:~$ df -i /mnt/day6disk
Filesystem     Inodes IUsed IFree IUse% Mounted on
/dev/loop3      25600    14 25586    1% /mnt/day6disk
```

#### Step 3 — Find the Largest Consumers

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo du -h --max-depth=1 /mnt/day6disk | sort -h
16K	/mnt/day6disk/lost+found
88M	/mnt/day6disk

hrishav@hrishav-LOQ-15IAX9:~$ sudo du -ah /mnt/day6disk | sort -h | tail -20
16K	/mnt/day6disk/lost+found
7.0M	/mnt/day6disk/fill2
40M	/mnt/day6disk/fill1
40M	/mnt/day6disk/testfile
88M	/mnt/day6disk
```

#### Step 4 — Check for Deleted Files Still Held Open

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo lsof +L1 2>/dev/null | head -30
COMMAND     PID    USER   FD   TYPE DEVICE SIZE/OFF NLINK    NODE NAME
mysqld     3755 dnsmasq    5u   REG   0,88        0     0 9460913 /tmp/#9460913 (deleted)
mysqld     3755 dnsmasq    6u   REG   0,88        0     0 9460914 /tmp/#9460914 (deleted)
mysqld     3755 dnsmasq    7u   REG   0,88        0     0 9460915 /tmp/#9460915 (deleted)
mysqld     3755 dnsmasq   12u   REG   0,88        0     0 9460917 /tmp/#9460917 (deleted)
pipewire   6273 hrishav   36u   REG    0,1     2312     0    6161 /memfd:pipewire-memfd:flags=0x0000000f,type=2,size=2312 (deleted)
pipewire   6273 hrishav   39u   REG    0,1     2312     0    6162 /memfd:pipewire-memfd:flags=0x0000000f,type=2,size=2312 (deleted)
pipewire   6273 hrishav   47u   REG    0,1     2312     0    7187 /memfd:pipewire-memfd:flags=0x0000000f,type=2,size=2312 (deleted)
pipewire   6273 hrishav   49u   REG    0,1     2312     0   10258 /memfd:pipewire-memfd:flags=0x0000000f,type=2,size=2312 (deleted)
pipewire   6273 hrishav   51u   REG    0,1     2312     0    6163 /memfd:pipewire-memfd:flags=0x0000000f,type=2,size=2312 (deleted)
Xorg       6389 hrishav   30u   REG    0,1  2379776     0    6164 /memfd:/.nvidia_drv.XXXXXX (deleted)
Xorg       6389 hrishav   58u   REG    0,1        4     0    1053 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   77u   REG    0,1        4     0   11484 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   78u   REG    0,1        4     0   14929 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   83u   REG    0,1        4     0      34 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   85u   REG    0,1        4     0      35 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   86u   REG    0,1        4     0   14679 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   87u   REG    0,1        4     0   14677 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   88u   REG    0,1        4     0   19487 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   90u   REG    0,1        4     0    5528 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   92u   REG    0,1        4     0   18987 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   97u   REG    0,1        4     0    1307 /memfd:xshmfence (deleted)
Xorg       6389 hrishav   99u   REG    0,1        4     0    1308 /memfd:xshmfence (deleted)
Xorg       6389 hrishav  100u   REG    0,1        4     0   17273 /memfd:xshmfence (deleted)
Xorg       6389 hrishav  101u   REG    0,1        4     0   15758 /memfd:xshmfence (deleted)
Xorg       6389 hrishav  106u   REG    0,1        4     0    6262 /memfd:xshmfence (deleted)
Xorg       6389 hrishav  107u   REG    0,1        4     0   18979 /memfd:xshmfence (deleted)
Xorg       6389 hrishav  108u   REG    0,1        4     0    6263 /memfd:xshmfence (deleted)
Xorg       6389 hrishav  111u   REG    0,1        4     0   11248 /memfd:xshmfence (deleted)
Xorg       6389 hrishav  113u   REG    0,1        4     0     562 /memfd:xshmfence (deleted)
```

### 🔍 What I Observed on My System

- **Step 1 (Symptom Verified):** `df -h /mnt/day6disk` confirmed the disk was 100% full (88M Used, 0 Avail).
- **Step 2 (Inodes Ruling):** `df -i /mnt/day6disk` showed only **14 out of 25,600 inodes used (1%)**. This proved definitively that the out-of-space issue was not caused by millions of tiny files consuming metadata, but rather by block storage exhaustion.
- **Step 3 (Culprit Identification):** `du -ah /mnt/day6disk | sort -h` immediately isolated the top three space consumers: `testfile` (40M), `fill1` (40M), and `fill2` (7.0M), totaling ~87M.
- **Step 4 (Ghost/Deleted Files Rule-out):** `lsof +L1` returned no open unlinked files on `/mnt/day6disk` (only temporary pipes and memfds from `mysqld`, `pipewire`, and `Xorg` on root/tmpfs). This confirmed the space was locked by visible files on the filesystem, not hidden held-open file descriptors.

### 📝 Diagnostic Decision Tree

```
Filesystem full? (df -h shows 100%)
│
├── YES → Check inode usage (df -i)
│          │
│          ├── Inodes OK → Large files consuming blocks
│          │                └── Find them: du -ah | sort -h | tail -20
│          │
│          └── Inodes full → Too many small files
│                            └── Find them: find /path -type f | wc -l
│
└── NO → Problem is elsewhere (permissions, read-only mount, quota)
```

### 🧠 Key Concept: Two Ways a Filesystem Can Be "Full"

| Exhaustion Type | What Ran Out | `df -h` Shows | `df -i` Shows | Common Cause |
| :--- | :--- | :--- | :--- | :--- |
| **Block exhaustion** | Data blocks (storage space) | 100% | Low % | Large log files, database files, core dumps |
| **Inode exhaustion** | Inodes (file metadata entries) | May show free space! | 100% | Millions of tiny files (mail queues, session files, temp cache) |

---

## Task 9: Incident Report

### 📋 Post-Mortem Report

| Stage | Detail |
| :--- | :--- |
| **PROBLEM** | Application error: `No space left on device`. Write operations to `/mnt/day6disk` failed. |
| **EVIDENCE** | `df -h /mnt/day6disk` showed the filesystem at **100% usage** (Use% = 100%). `df -i` confirmed inodes were **not exhausted**, ruling out inode exhaustion. |
| **ROOT CAUSE** | Three large test files (`testfile` 40 MB, `fill1` 40 MB, `fill2` 7.0 MB) consumed all available data blocks on the 100 MB ext4 filesystem. |
| **FIX** | Removed the offending test files: `sudo rm -f /mnt/day6disk/testfile /mnt/day6disk/fill1 /mnt/day6disk/fill2` followed by `sync`. |
| **VERIFICATION** | `df -h /mnt/day6disk` confirmed usage dropped back to a healthy level. New write operations succeeded. |

> **Key Learning:** The troubleshooting method is what matters — not the fix itself. In production, the root cause might be an unrotated log, a runaway backup, or a memory-mapped temp file held open by a crashed process. The **framework** (symptom → evidence → root cause → fix → verify) remains the same.

---

## Task 10: Fix and Verify

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `sudo rm -f /mnt/day6disk/testfile /mnt/day6disk/fill1 /mnt/day6disk/fill2` | Removes the test files. `-f` suppresses errors if files don't exist. |
| `sync` | Flushes filesystem metadata to ensure the kernel updates free block counters. |
| `df -h /mnt/day6disk` | Confirms available space has been recovered. |
| `du -sh /mnt/day6disk` | Confirms directory-level usage matches expectations. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo rm -f /mnt/day6disk/testfile /mnt/day6disk/fill1 /mnt/day6disk/fill2
[sudo] password for hrishav: 
hrishav@hrishav-LOQ-15IAX9:~$ sync

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
Filesystem      Size  Used Avail Use% Mounted on
/dev/loop3       90M   24K   83M   1% /mnt/day6disk

hrishav@hrishav-LOQ-15IAX9:~$ du -sh /mnt/day6disk
du: cannot read directory '/mnt/day6disk/lost+found': Permission denied
20K	/mnt/day6disk
```

### 🔍 What I Observed on My System

- **Clean block reclamation:** Removing the three offending files (`testfile`, `fill1`, and `fill2`) immediately reclaimed all ~87 MB of consumed space.
- **Back to baseline (100% ➔ 1%):** `df -h /mnt/day6disk` confirmed the disk dropped right back to its pristine post-format state: **24K used**, **83M available**, and **1% utilization**.
- **Minimal overhead confirmed:** `du -sh` shows only `20K` remaining, representing just the internal ext4 directory tables and the empty `lost+found` folder.
- **Incident Resolved:** The filesystem is fully responsive and capable of receiving new writes without errors.

### ✅ Verification Checkpoint
- Filesystem usage returned to a healthy level.
- New files can be created successfully on `/mnt/day6disk`.
- The troubleshooting framework was applied end-to-end.

---

## 🧠 What You Should Be Able to Explain (Interview & Concept Recap)

1. **What a block device, filesystem, UUID, and mount point are:**
   - A block device is raw storage (`/dev/sda`). A filesystem (ext4) organizes blocks into files. A UUID uniquely identifies a filesystem. A mount point is the directory where the filesystem becomes accessible.

2. **What `lsblk`, `df`, `du`, and `df -i` show:**
   - `lsblk` — block devices and their tree structure. `df` — filesystem-level space usage. `du` — directory/file-level space usage. `df -i` — inode allocation and usage.

3. **Why `/etc/fstab` is used:**
   - To define persistent mount configurations that survive reboots. Without it, mounted filesystems disappear after restart.

4. **Why `mount -a` should be tested before rebooting:**
   - A broken fstab entry (typo, missing UUID, wrong options) can cause boot failure, dropping the system to emergency mode. `mount -a` and `findmnt --verify` catch errors safely.

5. **How to identify which directory/file is consuming disk space:**
   - Start with `df -h` to find the full filesystem, then drill down with `du -h --max-depth=1 <path> | sort -h` to isolate the largest consumers.

6. **What inode exhaustion means:**
   - The filesystem has free data blocks but no available inode entries. Every file requires one inode. Creating a new file fails even though `df -h` shows free space.

7. **Why a deleted file can still consume space when a process keeps it open:**
   - In Linux, `rm` removes the directory entry (filename → inode link). But the kernel won't free the data blocks until the file's reference count reaches zero. If a process still has the file open (e.g., a log writer), the space remains allocated. `lsof +L1` finds these phantom files.

8. **How to troubleshoot a disk-full incident using evidence instead of guessing:**
   - **Framework:** Confirm symptom (`df -h`) → Classify exhaustion type (`df -i`) → Find the consumer (`du -ah | sort -h | tail`) → Check for hidden usage (`lsof +L1`) → Apply targeted fix (`rm`, restart process, add storage) → Verify resolution (`df -h`, test write).

---

> **⚠️ Final Note:** The goal is not to collect screenshots. The goal is to learn a repeatable Linux troubleshooting method:  
> **Confirm the symptom → Collect evidence → Find the resource → Identify the root cause → Apply a safe fix → Verify the result.**

---

[← Day 05](Day05.md) | [Home](README.md) | [Day 07 →](Day07.md)
