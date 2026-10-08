# DevOps Winter Arc — Day 03: Linux Practical Assignment

> **90 Days of DevOps Challenge | Linux Week | Learn • Practice • Build**  
> **Topic: Terminal Navigation, Directory Scaffolding, File Manipulation & Verification**

---

## 🎯 Mission

Day 3 of my DevOps Winter Arc challenge!

Today’s mission was a strict hands-on practical test: **manage the Linux filesystem entirely through the command line**. No GUI, no file manager, and no mouse shortcuts—just raw terminal commands.

### The Objectives:
1. **Directory Navigation:** Inspect current working location, explore hidden and visible entries, and return to home safely.
2. **Directory Scaffolding:** Create a nested multi-tier directory structure (`DevOps/Linux/Commands`, `Scripts`, `Docker`) using clean CLI commands.
3. **File Operations:** Generate files, write text through shell redirection, inspect contents, copy across subdirectories, and rename without data loss.
4. **Verification:** Inspect the complete directory tree and confirm file placement and contents.
5. **Bonus Challenge:** Complete the assignment in the fewest possible commands using shell chaining and brace expansion.

---

## Task 1: Directory Navigation

The goal of this task is to establish situational awareness inside the Linux filesystem before performing any operations.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `pwd` | **Print Working Directory:** Outputs the absolute path of where the current shell session is located. |
| `ls -la` | **List All (Long Format):** Lists all files and directories (including hidden ones starting with `.`) with permissions, owner, group, file size, and timestamps. |
| `cd ~` | **Change Directory to Home:** Moves the current shell session back to the user's home directory (`/home/hrishav`). |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/projects$ pwd
/home/hrishav/projects

hrishav@hrishav-LOQ-15IAX9:~/projects$ ls -la
total 16
drwxrwxr-x  4 hrishav hrishav 4096 Oct  8 22:30 .
drwxr-x--- 32 hrishav hrishav 4096 Oct  8 22:28 ..
-rw-rw-r--  1 hrishav hrishav  220 Oct  8 22:25 .bashrc_custom
drwxrwxr-x  8 hrishav hrishav 4096 Oct  8 22:20 90_Days_of_DevOps
drwxrwxr-x  2 hrishav hrishav 4096 Oct  8 22:15 test-lab

hrishav@hrishav-LOQ-15IAX9:~/projects$ cd ~

hrishav@hrishav-LOQ-15IAX9:~$ pwd
/home/hrishav
```

### 🔍 What I Observed on My System
- `pwd` returned `/home/hrishav/projects` initially, confirming my current working directory before navigating.
- `ls -la` revealed hidden configuration files like `.bashrc_custom` as well as the special directory references `.` (current directory) and `..` (parent directory).
- Running `cd ~` (or simply `cd`) instantly relocated my session to `/home/hrishav`, indicated by the `~` symbol in my shell prompt.

---

## Task 2: Create the Directory Structure

The assignment requires creating this exact directory structure:

```
DevOps/
└── Linux/
    ├── Commands/
    ├── Docker/
    └── Scripts/
```

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `mkdir -p DevOps/Linux/Commands` | Creates the nested `DevOps/Linux/Commands` folder structure. The `-p` flag creates parent directories if they don't already exist. |
| `mkdir -p DevOps/Linux/Scripts` | Creates the `Scripts` directory inside `DevOps/Linux/`. |
| `mkdir -p DevOps/Linux/Docker` | Creates the `Docker` directory inside `DevOps/Linux/`. |
| `mkdir -p DevOps/Linux/{Commands,Scripts,Docker}` | **Power Command:** Uses Bash **brace expansion** to create all three subdirectories and their parents in a single operation. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ mkdir -p DevOps/Linux/Commands DevOps/Linux/Scripts DevOps/Linux/Docker

hrishav@hrishav-LOQ-15IAX9:~$ ls -l DevOps/Linux
total 12
drwxrwxr-x 2 hrishav hrishav 4096 Oct  8 22:32 Commands
drwxrwxr-x 2 hrishav hrishav 4096 Oct  8 22:32 Docker
drwxrwxr-x 2 hrishav hrishav 4096 Oct  8 22:32 Scripts
```

### 🔍 What I Observed on My System
- Using the `-p` (parents) flag is critical: without `-p`, running `mkdir DevOps/Linux/Commands` when `DevOps` does not yet exist triggers `mkdir: cannot create directory ‘DevOps/Linux/Commands’: No such file or directory`.
- By passing multiple directory targets or using brace expansion `{Commands,Scripts,Docker}`, I eliminated repetitive commands and scaffolded the entire hierarchy cleanly.

---

## Task 3: File Operations

With the directory hierarchy in place, this task tests file creation, text redirection, content inspection, copying, and renaming.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `echo "I am learning Linux." > DevOps/Linux/Commands/day03.txt` | Writes the text directly into `day03.txt` inside `Commands/`. The `>` operator creates the file if it doesn't exist or overwrites it. |
| `cat DevOps/Linux/Commands/day03.txt` | Displays the contents of `day03.txt` to the terminal standard output (`stdout`). |
| `cp DevOps/Linux/Commands/day03.txt DevOps/Linux/Scripts/` | Copies `day03.txt` from the `Commands/` directory into the `Scripts/` directory while keeping the original intact. |
| `mv DevOps/Linux/Scripts/day03.txt DevOps/Linux/Scripts/linux-notes.txt` | Renames the copied file in `Scripts/` to `linux-notes.txt`. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ echo "I am learning Linux." > DevOps/Linux/Commands/day03.txt

hrishav@hrishav-LOQ-15IAX9:~$ cat DevOps/Linux/Commands/day03.txt
I am learning Linux.

hrishav@hrishav-LOQ-15IAX9:~$ cp DevOps/Linux/Commands/day03.txt DevOps/Linux/Scripts/

hrishav@hrishav-LOQ-15IAX9:~$ ls -l DevOps/Linux/Scripts/
total 4
-rw-rw-r-- 1 hrishav hrishav 21 Oct  8 22:33 day03.txt

hrishav@hrishav-LOQ-15IAX9:~$ mv DevOps/Linux/Scripts/day03.txt DevOps/Linux/Scripts/linux-notes.txt

hrishav@hrishav-LOQ-15IAX9:~$ ls -l DevOps/Linux/Scripts/
total 4
-rw-rw-r-- 1 hrishav hrishav 21 Oct  8 22:33 linux-notes.txt
```

### 🔍 What I Observed on My System
- The output redirection operator `>` allowed me to create and populate `day03.txt` in a single command, without needing an interactive editor like `nano` or `vim`.
- `cp` left the original `day03.txt` inside `Commands/` untouched while duplicating it into `Scripts/`.
- In Linux, `mv` handles both moving files between directories and renaming files within the same directory because both are essentially inode link modifications.

---

## Task 4: Verification

To prove the structure and file operations were executed with 100% precision, I ran comprehensive tree and content verifications.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `tree DevOps` | Displays a visual hierarchical diagram of all directories and nested files inside `DevOps/`. |
| `ls -lR DevOps` | Fallback recursive listing showing permissions, sizes, and subdirectories (works on systems without `tree`). |
| `cat DevOps/Linux/Commands/day03.txt` | Verifies the content of the primary file. |
| `cat DevOps/Linux/Scripts/linux-notes.txt` | Verifies the content of the copied and renamed file. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ tree DevOps
DevOps
└── Linux
    ├── Commands
    │   └── day03.txt
    ├── Docker
    └── Scripts
        └── linux-notes.txt

4 directories, 2 files

hrishav@hrishav-LOQ-15IAX9:~$ ls -lR DevOps
DevOps:
total 4
drwxrwxr-x 5 hrishav hrishav 4096 Oct  8 22:32 Linux

DevOps/Linux:
total 12
drwxrwxr-x 2 hrishav hrishav 4096 Oct  8 22:33 Commands
drwxrwxr-x 2 hrishav hrishav 4096 Oct  8 22:32 Docker
drwxrwxr-x 2 hrishav hrishav 4096 Oct  8 22:33 Scripts

DevOps/Linux/Commands:
total 4
-rw-rw-r-- 1 hrishav hrishav 21 Oct  8 22:33 day03.txt

DevOps/Linux/Docker:
total 0

DevOps/Linux/Scripts:
total 4
-rw-rw-r-- 1 hrishav hrishav 21 Oct  8 22:33 linux-notes.txt

hrishav@hrishav-LOQ-15IAX9:~$ cat DevOps/Linux/Commands/day03.txt
I am learning Linux.

hrishav@hrishav-LOQ-15IAX9:~$ cat DevOps/Linux/Scripts/linux-notes.txt
I am learning Linux.
```

### ✅ Verification Checklist
- [x] Current working directory verified with `pwd`.
- [x] Hidden files listed with `ls -la`.
- [x] `DevOps/Linux` directory created.
- [x] `Commands/`, `Scripts/`, and `Docker/` created inside `DevOps/Linux/`.
- [x] `day03.txt` created inside `Commands/` with text `"I am learning Linux."`.
- [x] `day03.txt` copied to `Scripts/` and renamed to `linux-notes.txt`.
- [x] Complete directory tree confirmed with `tree DevOps` (4 directories, 2 files).
- [x] Contents of both files independently confirmed with `cat`.

---

## ⚡ Bonus Challenge: Minimal Command Execution

The assignment asks: *Can you complete the entire assignment using the fewest possible commands?*

Yes! By utilizing Bash **brace expansion** and the **`&&` logical AND operator** (which ensures a command only executes if the preceding command succeeded with exit code `0`), the entire assignment can be executed in just **2 commands**:

### The 2-Command One-Liner

```bash
# 1. Create the complete folder structure in a single command using brace expansion:
mkdir -p DevOps/Linux/{Commands,Scripts,Docker}

# 2. Populate, copy, rename, and verify in a chained pipeline:
echo "I am learning Linux." > DevOps/Linux/Commands/day03.txt && \
cp DevOps/Linux/Commands/day03.txt DevOps/Linux/Scripts/linux-notes.txt && \
tree DevOps
```

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ mkdir -p DevOps/Linux/{Commands,Scripts,Docker}

hrishav@hrishav-LOQ-15IAX9:~$ echo "I am learning Linux." > DevOps/Linux/Commands/day03.txt && cp DevOps/Linux/Commands/day03.txt DevOps/Linux/Scripts/linux-notes.txt && tree DevOps
DevOps
└── Linux
    ├── Commands
    │   └── day03.txt
    ├── Docker
    └── Scripts
        └── linux-notes.txt

4 directories, 2 files
```

### 🧠 How This Works Under the Hood:
1. **`mkdir -p DevOps/Linux/{Commands,Scripts,Docker}`:**
   - The shell expands the braces before executing `mkdir`, turning it into: `mkdir -p DevOps/Linux/Commands DevOps/Linux/Scripts DevOps/Linux/Docker`.
   - The `-p` flag handles parent directory creation on the fly.
2. **`echo "..." > .../day03.txt`:** Creates and populates the file directly.
3. **`cp .../day03.txt .../Scripts/linux-notes.txt`:** Copies and renames in a single step by specifying the new filename in the destination path instead of copying and running `mv` separately!
4. **`&&` chaining:** Ensures each command only triggers if the previous step exited with status `0` (success).

---

## 📝 Key Takeaways & Reflection

1. **GUI vs. CLI Speed:** What would take 15–20 clicks in a graphical file manager (creating folders, opening text editors, renaming files) took under 2 seconds in the terminal.
2. **Brace Expansion is a Superpower:** `{dir1,dir2,dir3}` saves immense typing and reduces script complexity.
3. **Combining Copy & Rename:** When using `cp <src> <dest_path/new_name>`, you don't need a separate `mv` step if you declare the target filename directly.
4. **Verification is DevOps Culture:** An engineer never assumes a command worked; always verify with `tree`, `ls -l`, and exit code checks.

---

[← Day 02](Day02.md) | [Home](README.md) | [Day 04 →](Day04.md)
