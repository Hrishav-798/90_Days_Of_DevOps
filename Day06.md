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
# TODO: Paste output
#               total        used        free      shared  buff/cache   available
# Mem:           15Gi       X.XGi       X.XGi       XXXMi       X.XGi       XXGi
# Swap:         X.XGi       XXXMi       X.XGi

hrishav@hrishav-LOQ-15IAX9:~$ uptime
# TODO: Paste output
# e.g., 20:30:00 up 2 days, 5:14,  1 user,  load average: 0.52, 0.48, 0.44

hrishav@hrishav-LOQ-15IAX9:~$ systemctl --failed
# TODO: Paste output
# Ideally: "0 loaded units listed."
# If services are failed, investigate with: systemctl status <unit-name>
```

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
hrishav@hrishav-LOQ-15IAX9:~$ sudo fallocate -l 100M /var/lib/day6/day6-disk.img

hrishav@hrishav-LOQ-15IAX9:~$ sudo mkfs.ext4 /var/lib/day6/day6-disk.img
# TODO: Paste output
# Expected: Warning about not being a block device (safe to proceed)
# mke2fs will create filesystem with inodes, blocks, and journal

hrishav@hrishav-LOQ-15IAX9:~$ sudo mkdir -p /mnt/day6disk
hrishav@hrishav-LOQ-15IAX9:~$ sudo mount -o loop /var/lib/day6/day6-disk.img /mnt/day6disk

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
# TODO: Paste output
# Expected: Filesystem shows ~93M total (ext4 reserves ~5% for root), mounted on /mnt/day6disk

hrishav@hrishav-LOQ-15IAX9:~$ lsblk -f
# TODO: Paste output — look for the loop device with ext4 and /mnt/day6disk mount
```

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
# Step 1: Find the UUID
hrishav@hrishav-LOQ-15IAX9:~$ sudo blkid /var/lib/day6/day6-disk.img
# TODO: Paste output
# Expected: /var/lib/day6/day6-disk.img: UUID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" TYPE="ext4"

# Step 2: Add fstab entry
hrishav@hrishav-LOQ-15IAX9:~$ sudo nano /etc/fstab
# Added line:
# UUID=YOUR-UUID /mnt/day6disk ext4 loop,nofail 0 2

# Step 3: Validate BEFORE rebooting
hrishav@hrishav-LOQ-15IAX9:~$ sudo umount /mnt/day6disk

hrishav@hrishav-LOQ-15IAX9:~$ sudo mount -a
# No errors = success

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
# TODO: Paste output — should show the filesystem mounted at /mnt/day6disk

hrishav@hrishav-LOQ-15IAX9:~$ findmnt /mnt/day6disk
# TODO: Paste output
# Expected: TARGET=/mnt/day6disk  SOURCE=/dev/loopN  FSTYPE=ext4  OPTIONS=rw,loop,nofail

hrishav@hrishav-LOQ-15IAX9:~$ sudo findmnt --verify
# TODO: Paste output — should show 0 errors (or only cosmetic warnings)
```

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
# TODO: Paste output
# Expected: 40+0 records in, 40+0 records out, 41943040 bytes (42 MB) copied

hrishav@hrishav-LOQ-15IAX9:~$ sync

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
# TODO: Paste output — Used should now be ~40M higher

hrishav@hrishav-LOQ-15IAX9:~$ du -sh /mnt/day6disk
# TODO: Paste output — Should show ~40M (just the user files)
```

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
# TODO: Paste output

hrishav@hrishav-LOQ-15IAX9:~$ sudo dd if=/dev/zero of=/mnt/day6disk/fill2 bs=1M count=15 status=progress
# TODO: Paste output
# May end with: dd: error writing '/mnt/day6disk/fill2': No space left on device

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
# TODO: Paste output
# Expected: Use% at 95-100%
```

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
hrishav@hrishav-LOQ-15IAX9:~$ df -h
# TODO: Paste output
# Identify the filesystem with very high (95-100%) usage
# Expected: /dev/loopN  ... 100% /mnt/day6disk
```

#### Step 2 — Check Inode Usage

```bash
hrishav@hrishav-LOQ-15IAX9:~$ df -i
# TODO: Paste output
# If IUse% is also high, the problem may be inode exhaustion (too many small files)
# If IUse% is low but disk is full, the problem is large files consuming data blocks
```

#### Step 3 — Find the Largest Consumers

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo du -h --max-depth=1 /mnt/day6disk | sort -h
# TODO: Paste output
# Shows each subdirectory's size, sorted smallest to largest

hrishav@hrishav-LOQ-15IAX9:~$ sudo du -ah /mnt/day6disk | sort -h | tail -20
# TODO: Paste output
# Shows the 20 largest individual files — these are your culprits
```

#### Step 4 — Check for Deleted Files Still Held Open

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo lsof +L1 2>/dev/null | head -30
# TODO: Paste output
# +L1 = show files with link count < 1 (deleted but still open)
# If a process holds a deleted file open, its disk space is NOT freed until the process exits
```

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
| **ROOT CAUSE** | Three large test files (`testfile` 40 MB, `fill1` 40 MB, `fill2` ~13 MB) consumed all available data blocks on the 100 MB ext4 filesystem. |
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
hrishav@hrishav-LOQ-15IAX9:~$ sync

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
# TODO: Paste output
# Expected: Use% drops back to ~1-5% (only lost+found remains)

hrishav@hrishav-LOQ-15IAX9:~$ du -sh /mnt/day6disk
# TODO: Paste output
# Expected: 16K or similar (just the lost+found directory)
```

### ✅ Verification Checkpoint
- Filesystem usage returned to a healthy level.
- New files can be created successfully on `/mnt/day6disk`.
- The troubleshooting framework was applied end-to-end.

---

## Task 11: Reboot Verification (Optional)

If working on a VM/server, prove that the `/etc/fstab` entry survives a reboot.

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo reboot

# After reconnecting:
hrishav@hrishav-LOQ-15IAX9:~$ findmnt /mnt/day6disk
# TODO: Paste output
# Expected: TARGET=/mnt/day6disk  SOURCE=/dev/loopN  FSTYPE=ext4

hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
# TODO: Paste output
# Expected: Filesystem is mounted and accessible

hrishav@hrishav-LOQ-15IAX9:~$ lsblk -f
# TODO: Paste output — confirm loop device with ext4 and mount point
```

### ✅ Expected Result
The test filesystem is automatically mounted at `/mnt/day6disk` after reboot, proving the `/etc/fstab` entry is correct and persistent.

---

## 🌟 Bonus Challenge: Block Exhaustion vs Inode Exhaustion

Demonstrate that a filesystem can have free storage blocks but still refuse new files if it runs out of inodes.

### 💻 Terminal Output

```bash
# Create 5000 small (empty) files
hrishav@hrishav-LOQ-15IAX9:~$ for i in $(seq 1 5000); do sudo touch /mnt/day6disk/file_$i; done

# Compare block usage vs inode usage
hrishav@hrishav-LOQ-15IAX9:~$ df -h /mnt/day6disk
# TODO: Paste output — blocks still mostly free (empty files use almost no space)

hrishav@hrishav-LOQ-15IAX9:~$ df -i /mnt/day6disk
# TODO: Paste output — inodes consumed! IUse% may be significantly higher

# Clean up
hrishav@hrishav-LOQ-15IAX9:~$ sudo rm -f /mnt/day6disk/file_*

hrishav@hrishav-LOQ-15IAX9:~$ df -i /mnt/day6disk
# TODO: Paste output — inodes freed again
```

### 📝 Explanation

| Dimension | Block (Storage) Space | Inodes |
| :--- | :--- | :--- |
| **What it tracks** | Actual data bytes on disk | Metadata entries (one per file/directory) |
| **Checked with** | `df -h` | `df -i` |
| **Exhausted by** | Large files (logs, databases, media) | Many small/empty files (caches, mail queues, session tokens) |
| **Symptom when full** | `No space left on device` | `No space left on device` (same error, different cause!) |
| **Key insight** | Free inodes ≠ free space; free space ≠ free inodes. **Both** must be available to create a new file. |

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

## 📋 Submission Checklist

- [ ] Storage layout: `lsblk -f` + `df -h`
- [ ] Disk usage investigation using `du`
- [ ] Basic health check: `free -h`, `uptime`, `systemctl --failed`
- [ ] Test filesystem created and mounted
- [ ] `/etc/fstab` entry + `mount -a` validation
- [ ] Controlled disk-full condition
- [ ] Troubleshooting evidence: `df`, `df -i`, `du`, and logs/process evidence
- [ ] Incident report: Problem → Evidence → Root Cause → Fix → Verification
- [ ] Final healthy filesystem verification
- [ ] Optional reboot verification
- [ ] Bonus: Block vs inode exhaustion comparison
- [ ] LinkedIn post + Day 6 submission form

---

> **⚠️ Final Note:** The goal is not to collect screenshots. The goal is to learn a repeatable Linux troubleshooting method:  
> **Confirm the symptom → Collect evidence → Find the resource → Identify the root cause → Apply a safe fix → Verify the result.**

---

[← Day 05](Day05.md) | [Home](README.md) | [Day 07 →](Day07.md)
