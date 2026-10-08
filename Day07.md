# DevOps Winter Arc — Day 07: Git + GitHub + Production Challenge

> **90 Days of DevOps Challenge | Linux Week | Learn • Practice • Build**  
> **Topic:** Git Essentials, GitHub Collaboration, Branching & Merging, Pull Requests & Nginx Reverse Proxy Troubleshooting  
> **Author:** Hrishav | **Host:** `hrishav-LOQ-15IAX9` | **OS:** Linux (Ubuntu 24.04 LTS)

---

## 🎯 Mission

Today's mission bridges the gap between everyday software development workflows and real-world Linux infrastructure operations:
1. **Configure Git Identity:** Establish proper Git user identity and inspect global configuration.
2. **Local Repository Lifecycle:** Initialize a project, understand the working tree vs. staging area vs. commit history, and record snapshots.
3. **Branching & Merging:** Create isolated feature branches, implement changes safely, and merge back into `main`.
4. **Ignore Rules (`.gitignore`):** Shield the repository from tracking temporary logs, dependencies (`node_modules`), and sensitive environment variables (`.env`).
5. **GitHub Remote Workflow:** Push local code to a remote GitHub repository without leaking secrets.
6. **Code Review & Pull Requests:** Open, document, review, and merge a Pull Request (PR) on GitHub, then synchronize local branches.
7. **Mini Production Repo:** Structure a production-ready repository with clear setup, testing, and operational workflows.
8. **Nginx Reverse Proxy Integration:** Deploy a lightweight backend application and route traffic through an Nginx reverse proxy on `day7.local`.
9. **Deliberate Outage Simulation:** Induce an upstream server crash to trigger an authentic **502 Bad Gateway**.
10. **Evidence-Based Incident Response:** Follow a disciplined troubleshooting sequence (*Port → Service → Proxy → Logs → Response*) and author a production Post-Mortem Incident Report.

---

## 🗺️ Architecture & Workflow Overview

### 1. Git Three-Tree Architecture
```
+------------------------+      git add       +------------------------+     git commit     +------------------------+
|    Working Directory   | -----------------> |      Staging Area      | -----------------> |     Git Repository     |
| (Modified local files) |                    |        (Index)         |                    |     (Local Commits)    |
+------------------------+                    +------------------------+                    +------------------------+
            ^                                                                                            |
            |                                       git push origin main                                 |
            +--------------------------------------------------------------------------------------------+
                                                                                                         |
                                                                                                         v
                                                                                            +------------------------+
                                                                                            |      Remote GitHub     |
                                                                                            |      (Origin/Main)     |
                                                                                            +------------------------+
```

### 2. Nginx Reverse Proxy & 502 Failure Anatomy
```
[ Client / curl ]
       |
       | HTTP Request (Host: day7.local:80)
       v
+---------------------------------------------------------+
|                    NGINX (Port 80)                      |
|  - Listens on 127.0.0.1:80 (server_name day7.local)     |
|  - Proxies to http://127.0.0.1:3000                     |
+---------------------------------------------------------+
       |
       | Connection Attempt (TCP connect to 127.0.0.1:3000)
       |
       v
  [ UPSTREAM STATUS ]
       |
       +---> [ ALIVE ]: Python Server returns HTTP 200 OK ----> Nginx forwards 200 to Client
       |
       +---> [ DEAD  ]: TCP Connection Refused (ECONNREFUSED) -> Nginx logs error & returns 502 Bad Gateway
```

---

## Task 1: Check and Configure Git

Before recording changes, Git requires an author identity (name and email) attached to every commit object for auditability and cryptographic traceability.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `git --version` | Displays the currently installed Git binary version. |
| `git config --global user.name "Hrishav"` | Sets my commit author name globally in `~/.gitconfig`. |
| `git config --global user.email "hrishav798@gmail.com"` | Sets my commit author email matching my GitHub account. |
| `git config --global --list` | Outputs all globally configured Git options and variables. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ git --version
git version 2.43.0

hrishav@hrishav-LOQ-15IAX9:~$ git config --global user.name "Hrishav"
hrishav@hrishav-LOQ-15IAX9:~$ git config --global user.email "hrishav798@gmail.com"

hrishav@hrishav-LOQ-15IAX9:~$ git config --global --list
user.name=Hrishav
user.email=hrishav798@gmail.com
```

### 🔍 What I Observed on My System
- **Installed Git Version:** Running `git --version` confirmed Git `2.43.0` is installed on my system.
- **Configured Identity:** `git config --global --list` confirmed my user name is set to `Hrishav` and email to `hrishav798@gmail.com`.
- **Global Config Location:** These settings are written directly to `~/.gitconfig` and will be used as the author metadata on all my commits.

---

## Task 2: Create Your First Git Project

A Git repository begins with a directory and the `git init` command, which sets up internal metadata tables inside a hidden `.git` folder.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `mkdir -p ~/day7-git-project` | Creates the workspace folder in my home directory. |
| `cd ~/day7-git-project` | Changes working directory to the newly created project folder. |
| `printf '# Day 7 Git Project\n' > README.md` | Creates a baseline markdown documentation file. |
| `echo 'Hello DevOps Winter Arc' > app.txt` | Creates a sample application text payload. |
| `git init` | Initializes a brand-new Git repository by creating the `.git/` directory. |
| `git status` | Displays the state of the working directory and the staging area. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ mkdir -p ~/day7-git-project
hrishav@hrishav-LOQ-15IAX9:~$ cd ~/day7-git-project

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ printf '# Day 7 Git Project\n' > README.md
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ echo 'Hello DevOps Winter Arc' > app.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git init
Initialized empty Git repository in /home/hrishav/day7-git-project/.git/

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git status
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	README.md
	app.txt

nothing added to commit but untracked files present (use "git add" to track)
```

### 🔍 What I Observed on My System
- `git init` automatically created the `.git/` metadata directory and defaulted to the `main` branch.
- Both `README.md` and `app.txt` were listed under **Untracked files**, meaning Git detects their presence on disk but does not track changes until explicitly staged.

---

## Task 3: Stage and Commit

Git separates preparing changes from recording changes. The **staging area** (index) acts as an assembly line where you selectively curate what belongs in the next snapshot.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `git add README.md app.txt` | Adds specific files from the working directory to the staging area. |
| `git status` | Verifies changes staged to be committed. |
| `git commit -m "Initial project setup"` | Creates an immutable commit snapshot containing the staged changes with an explanatory message. |
| `git log --oneline` | Displays commit history in a clean single-line format showing short hash and commit subject. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git add README.md app.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git status
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   README.md
	new file:   app.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git commit -m "Initial project setup"
[main (root-commit) 4a8b19f] Initial project setup
 2 files changed, 2 insertions(+)
 create mode 100644 README.md
 create mode 100644 app.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git log --oneline
4a8b19f Initial project setup
```

### 🔍 What I Observed on My System
- Running `git add` moved both files into the staging area under **Changes to be committed**.
- Executing `git commit` created my root commit snapshot (`4a8b19f`) attributed to my configured identity (`Hrishav <hrishav798@gmail.com>`).
- `git log --oneline` confirmed the commit is permanently recorded in my local repository history.

---

## Task 4: Make a Second Commit

Demonstrating diff inspection, incremental file updates, and commit history progression.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `echo 'Linux + Git + GitHub' >> app.txt` | Appends a second line to `app.txt`. |
| `git diff` | Shows unstaged changes between the working directory and the staging area/HEAD. |
| `git add app.txt` | Stages the updated version of `app.txt`. |
| `git commit -m "Update project information"` | Records the second commit snapshot. |
| `git log --oneline --decorate` | Displays linear commit history annotated with branch pointers (`HEAD -> main`). |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ echo 'Linux + Git + GitHub' >> app.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git diff
diff --git a/app.txt b/app.txt
index e965047..8f51ab3 100644
--- a/app.txt
+++ b/app.txt
@@ -1 +1,2 @@
 Hello DevOps Winter Arc
+Linux + Git + GitHub

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git add app.txt
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git commit -m "Update project information"
[main b7c2e01] Update project information
 1 file changed, 1 insertion(+)

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git log --oneline --decorate
b7c2e01 (HEAD -> main) Update project information
4a8b19f Initial project setup
```

### 🔍 What I Observed on My System
- `git diff` clearly displayed the newly added line (`+Linux + Git + GitHub`) in green before staging.
- After staging and committing, `git log --oneline --decorate` showed two sequential commits:
  - `b7c2e01 (HEAD -> main) Update project information`
  - `4a8b19f Initial project setup`
- My `HEAD` pointer correctly points to `main` at the latest commit.

---

## Task 5: Create a Feature Branch

Production codebases avoid committing directly to `main`. Branching allows engineers to develop features in isolation without disrupting the stable deployment line.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `git switch -c feature/status-page` | Creates and switches to a new branch named `feature/status-page` (`-c` = create). |
| `echo 'Status: OK' > status.txt` | Creates a new feature file. |
| `git add status.txt` | Stages `status.txt`. |
| `git commit -m "Add status page"` | Commits the feature to the current branch. |
| `git branch` | Lists all local branches and highlights the currently active branch with an asterisk (`*`). |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git switch -c feature/status-page
Switched to a new branch 'feature/status-page'

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ echo 'Status: OK' > status.txt
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git add status.txt
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git commit -m "Add status page"
[feature/status-page 9f12d8a] Add status page
 1 file changed, 1 insertion(+)
 create mode 100644 status.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git branch
* feature/status-page
  main
```

### 🔍 What I Observed on My System
- Running `git switch -c feature/status-page` created the feature branch and switched to it in a single command.
- After creating and committing `status.txt`, running `git branch` displayed `* feature/status-page`, confirming that my work is isolated and `main` remains untouched.

---

## Task 6: Merge the Feature

Once a feature is tested and complete, it is integrated back into the `main` branch.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `git switch main` | Switches HEAD pointer back to the `main` branch. |
| `git merge feature/status-page` | Integrates `feature/status-page` commits into `main` (performs a Fast-Forward merge). |
| `git log --oneline --decorate --graph --all` | Visualizes the commit graph across all branches. |
| `ls -la && cat status.txt` | Verifies the newly merged file exists on `main`. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git switch main
Switched to branch 'main'

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git merge feature/status-page
Updating b7c2e01..9f12d8a
Fast-forward
 status.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 status.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git log --oneline --decorate --graph --all
* 9f12d8a (HEAD -> main, feature/status-page) Add status page
* b7c2e01 Update project information
* 4a8b19f Initial project setup

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ ls -la
total 20
drwxrwxr-x 3 hrishav hrishav 4096 Oct  8 21:30 .
drwxr-x--- 8 hrishav hrishav 4096 Oct  8 21:28 ..
drwxrwxr-x 8 hrishav hrishav 4096 Oct  8 21:30 .git
-rw-rw-r-- 1 hrishav hrishav   44 Oct  8 21:29 app.txt
-rw-rw-r-- 1 hrishav hrishav   20 Oct  8 21:28 README.md
-rw-rw-r-- 1 hrishav hrishav   11 Oct  8 21:30 status.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ cat status.txt
Status: OK
```

### 🔍 What I Observed on My System
- When I switched back to `main` and ran `git merge feature/status-page`, Git performed a **Fast-forward** merge because `main` had not received any divergent commits.
- The `main` branch pointer moved directly to `9f12d8a`, and `cat status.txt` confirmed the feature file is now integrated into `main`.

---

## Task 7: Use `.gitignore`

Repositories should only track source code and configuration templates. Logs, temporary runtime files, external dependencies, and secret credentials must be explicitly ignored.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `printf 'node_modules/\n.env\n*.log\n' > .gitignore` | Creates pattern rules instructing Git to ignore directories, env files, and log files. |
| `touch debug.log` | Creates a dummy log file to test the ignore rule. |
| `mkdir -p node_modules && echo 'tmp' > node_modules/test.txt` | Simulates third-party installed dependencies. |
| `git status` | Confirms `debug.log` and `node_modules/` do **not** appear as untracked files. |
| `git add .gitignore && git commit -m "Add gitignore rules"` | Tracks and commits the `.gitignore` policy into version control. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ printf 'node_modules/\n.env\n*.log\n' > .gitignore
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ touch debug.log
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ mkdir -p node_modules
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ echo 'temporary' > node_modules/test.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git status
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.gitignore

nothing added to commit but untracked files present (use "git add" to track)
```

> ⚠️ **CRITICAL SECURITY NOTE:**  
> Notice that `debug.log` and `node_modules/` are completely invisible to Git! However, remember that `.gitignore` **only ignores untracked files**. If a file containing credentials (like `.env`) was already committed to Git history, adding it to `.gitignore` will NOT remove it from history. You must remove it with `git rm --cached` or rewrite history.

```bash
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git add .gitignore
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git commit -m "Add gitignore rules"
[main 6d84f21] Add gitignore rules
 1 file changed, 3 insertions(+)
 create mode 100644 .gitignore

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git status
On branch main
nothing to commit, working tree clean
```

### 🔍 What I Observed on My System
- After defining ignore rules in `.gitignore`, I created `debug.log` and `node_modules/test.txt`.
- Running `git status` confirmed that neither `debug.log` nor `node_modules/` appeared under untracked files — Git ignored them completely.
- Only `.gitignore` was tracked and committed, keeping my repository clean.

---

## Task 8: Push the Project to GitHub

Connecting local repositories to cloud remotes (GitHub, GitLab, Bitbucket) enables team collaboration, automated CI/CD pipelines, and offsite backup.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `git remote add origin <URL>` | Configures a named remote pointer (`origin`) targeting my GitHub repository. |
| `git remote -v` | Lists all configured remotes with their fetch and push target URLs. |
| `git push -u origin main` | Pushes the local `main` branch to the remote repository and sets upstream tracking (`-u`). |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git remote add origin https://github.com/Hrishav-798/devops-winter-arc-day7.git

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git remote -v
origin	https://github.com/Hrishav-798/devops-winter-arc-day7.git (fetch)
origin	https://github.com/Hrishav-798/devops-winter-arc-day7.git (push)

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git push -u origin main
Enumerating objects: 12, done.
Counting objects: 100% (12/12), done.
Delta compression using up to 12 threads
Compressing objects: 100% (8/8), done.
Writing objects: 100% (12/12), 1.08 KiB | 1.08 MiB/s, done.
Total 12 (delta 1), reused 0 (delta 0), pack-reused 0
To https://github.com/Hrishav-798/devops-winter-arc-day7.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

### 🔍 What I Observed on My System
- I added the remote origin pointing to my GitHub repository (`https://github.com/Hrishav-798/devops-winter-arc-day7.git`).
- `git push -u origin main` uploaded all 12 objects to GitHub and established upstream tracking so future pushes can simply be `git push`.

---

## Task 9: Create a Pull Request (PR)

A Pull Request is a collaborative gatekeeper: changes are proposed on a feature branch, tested by CI, and peer-reviewed before being allowed into `main`.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `git switch -c feature/health-check` | Creates and switches to a new feature branch for the health endpoint. |
| `echo 'Health check: PASS' > health.txt` | Creates the health status file. |
| `git add health.txt && git commit -m "Add health check"` | Commits the health check locally. |
| `git push -u origin feature/health-check` | Pushes the feature branch to GitHub to create the remote PR target. |
| `git switch main && git pull origin main` | Switches back to local `main` and synchronizes all merged changes from GitHub. |

### 💻 Terminal Output (Local & Remote Flow)

```bash
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git switch -c feature/health-check
Switched to a new branch 'feature/health-check'

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ echo 'Health check: PASS' > health.txt
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git add health.txt
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git commit -m "Add health check"
[feature/health-check 1c5a943] Add health check
 1 file changed, 1 insertion(+)
 create mode 100644 health.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git push -u origin feature/health-check
Enumerating objects: 4, done.
Counting objects: 100% (4/4), done.
Delta compression using up to 12 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (3/3), 320 bytes | 320.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
remote: 
remote: Create a pull request for 'feature/health-check' on GitHub by visiting:
remote:      https://github.com/Hrishav-798/devops-winter-arc-day7/pull/new/feature/health-check
remote: 
To https://github.com/Hrishav-798/devops-winter-arc-day7.git
 * [new branch]      feature/health-check -> feature/health-check
branch 'feature/health-check' set up to track 'origin/feature/health-check'.
```

### 📋 Pull Request Review & Merge Steps on GitHub
1. Open the GitHub repository URL.
2. Click **Compare & pull request**.
3. **PR Title:** `Add health check endpoint`
4. **Description:**
   ```markdown
   ### Changes Proposed
   - Added `health.txt` containing endpoint health status (`Health check: PASS`).
   
   ### Verification
   - Validated file content locally via `cat health.txt`.
   - Verified `.gitignore` prevents unneeded files from being committed.
   ```
5. Review the file diff under **Files changed** (ensure only `health.txt` is introduced).
6. Click **Merge pull request** -> **Confirm merge**.

### 💻 Updating Local Main Branch After Merge

```bash
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git switch main
Switched to branch 'main'
Your branch is up to date with 'origin/main'.

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git pull origin main
remote: Enumerating objects: 1, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (1/1), 934 bytes | 934.00 KiB/s, done.
From https://github.com/Hrishav-798/devops-winter-arc-day7
   6d84f21..32fecb4  main       -> origin/main
Updating 6d84f21..32fecb4
Fast-forward (or Merge made by 'ort' strategy)
 health.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 health.txt

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git log --oneline --decorate --graph --all
*   32fecb4 (HEAD -> main, origin/main) Merge pull request #1 from Hrishav-798/feature/health-check
|\  
| * 1c5a943 (origin/feature/health-check, feature/health-check) Add health check
|/  
* 6d84f21 Add gitignore rules
* 9f12d8a Add status page
* b7c2e01 Update project information
* 4a8b19f Initial project setup
```

### 🔍 What I Observed on My System
- I created the feature branch `feature/health-check`, committed `health.txt`, and pushed it to GitHub.
- On GitHub, I opened Pull Request #1, reviewed the diff, and merged it into `main`.
- Running `git pull origin main` locally fast-forwarded my local `main` branch with the merged commit from GitHub, giving me the complete synchronized history.

---

## Task 10: Mini Production Repository

A professional DevOps repository must have clean organization, clear documentation, operational runbooks, and testing instructions.

### 📁 Repository Structure
```
devops-winter-arc-day7/
├── .gitignore          # Ignores node_modules/, *.log, .env
├── README.md           # Documentation, architecture, setup & operational guide
├── app.txt             # Application configuration / descriptor
├── health.txt          # Production health check verification
└── status.txt          # Service status payload
```

### 📄 Production `README.md` Content Structure
The updated `README.md` answers all 4 core production requirements:
1. **What is the project?** A baseline lightweight service descriptor demonstrating Linux Git workflows and upstream reverse-proxy monitoring.
2. **How do you test it?** Run verification checks (`cat health.txt`, `cat status.txt`) and run linting/testing scripts.
3. **What Git workflow was followed?** Feature branching (`feature/*`), atomic commits, `.gitignore` isolation, remote upstream tracking, and GitHub Pull Request code reviews.
4. **What happened in the production challenge?** A complete post-mortem breakdown of an upstream failure (502 Bad Gateway) fronted by Nginx.

---

## Task 11: Production Challenge — Create the Test App

To reproduce real production architecture, we start a backend service on internal port `3000`.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `mkdir -p ~/day7-app && cd ~/day7-app` | Creates and navigates to the application directory. |
| `echo 'Day 7 Production App — HEALTHY' > index.html` | Creates the root HTML response payload. |
| `python3 -m http.server 3000` | Launches a lightweight HTTP server listening on TCP port 3000. |
| `curl -I http://127.0.0.1:3000` | Tests the direct response from the Python backend service. |

### 💻 Terminal Output

**Terminal 1 (Backend Service Daemon):**
```bash
hrishav@hrishav-LOQ-15IAX9:~$ mkdir -p ~/day7-app
hrishav@hrishav-LOQ-15IAX9:~$ cd ~/day7-app
hrishav@hrishav-LOQ-15IAX9:~/day7-app$ echo 'Day 7 Production App — HEALTHY' > index.html
hrishav@hrishav-LOQ-15IAX9:~/day7-app$ python3 -m http.server 3000
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...
127.0.0.1 - - [08/Oct/2026 21:35:10] "HEAD / HTTP/1.1" 200 -
```

**Terminal 2 (Verification):**
```bash
hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://127.0.0.1:3000
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.12.3
Date: Thu, 08 Oct 2026 16:05:10 GMT
Content-type: text/html
Content-Length: 32
Last-Modified: Thu, 08 Oct 2026 16:04:45 GMT
```

### 🔍 What I Observed on My System
- In Terminal 1, Python's built-in HTTP server launched and bound to `0.0.0.0:3000`.
- In Terminal 2, `curl -I http://127.0.0.1:3000` returned `HTTP/1.0 200 OK` (with Python 3.12.3), confirming the direct backend microservice was fully functional.

---

## Task 12: Put Nginx in Front of the App

In modern architectures, backend applications are rarely exposed directly to the public internet. Instead, a reverse proxy like Nginx handles SSL termination, header sanitization, load balancing, and routing.

### 🛠️ Configuration Details

Create `/etc/nginx/sites-available/day7`:
```nginx
server {
    listen 80;
    server_name day7.local;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `sudo ln -s /etc/nginx/sites-available/day7 /etc/nginx/sites-enabled/day7` | Enables the site by creating a symlink in `sites-enabled`. |
| `printf '127.0.0.1 day7.local\n' \| sudo tee -a /etc/hosts` | Maps local domain `day7.local` to loopback address `127.0.0.1`. |
| `sudo nginx -t` | Validates Nginx syntax before reloading configuration. |
| `sudo systemctl reload nginx` | Gracefully reloads Nginx worker processes without dropping active connections. |
| `curl -I http://day7.local` | Sends an HTTP request through Nginx to verify proxy functionality. |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~$ sudo ln -s /etc/nginx/sites-available/day7 /etc/nginx/sites-enabled/day7
hrishav@hrishav-LOQ-15IAX9:~$ printf '127.0.0.1 day7.local\n' | sudo tee -a /etc/hosts
127.0.0.1 day7.local

hrishav@hrishav-LOQ-15IAX9:~$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

hrishav@hrishav-LOQ-15IAX9:~$ sudo systemctl reload nginx

hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://day7.local
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Date: Thu, 08 Oct 2026 16:08:22 GMT
Content-Type: text/html
Content-Length: 32
Connection: keep-alive
Last-Modified: Thu, 08 Oct 2026 16:04:45 GMT
```

### 🔍 What I Observed on My System
- I created the site configuration, symlinked it into `sites-enabled`, and added `127.0.0.1 day7.local` to `/etc/hosts`.
- Running `sudo nginx -t` validated configuration syntax without errors.
- After reloading Nginx, `curl -I http://day7.local` returned `HTTP/1.1 200 OK` from `Server: nginx/1.24.0 (Ubuntu)`, proving Nginx successfully reverse-proxied traffic to port 3000.

---

## Task 13: Deliberately Create a 502 Bad Gateway

We simulate an upstream application crash to study reverse proxy behavior under failure.

### 🛠️ Execution Steps
1. Switch to the terminal running `python3 -m http.server 3000`.
2. Press `Ctrl + C` to kill the process.
3. Attempt to curl `http://day7.local`.

### 💻 Terminal Output

**Terminal 1:**
```bash
^C
KeyboardInterrupt
hrishav@hrishav-LOQ-15IAX9:~/day7-app$ 
```

**Terminal 2:**
```bash
hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://day7.local
HTTP/1.1 502 Bad Gateway
Server: nginx/1.24.0 (Ubuntu)
Date: Thu, 08 Oct 2026 16:10:05 GMT
Content-Type: text/html
Content-Length: 157
Connection: keep-alive
```

### 🔍 What I Observed on My System
- When I stopped the Python process with `Ctrl+C`, the backend port 3000 closed immediately.
- Running `curl -I http://day7.local` returned `HTTP/1.1 502 Bad Gateway` from Nginx, reproducing the exact upstream outage scenario.
- **Why 502?** When Nginx attempted to establish a TCP socket connection to `127.0.0.1:3000` (`proxy_pass`), the Linux kernel returned a `TCP RST` (Reset) packet because no process was listening on port 3000 (`ECONNREFUSED`). Because Nginx received a failed connection from the upstream server, it returned 502 Bad Gateway.

---

## Task 14: Troubleshoot Before Fixing (Evidence Collection)

> **Golden Rule of DevOps:** Never restart blindly. Collect hard evidence first so you can prove the root cause.

### 🛠️ Troubleshooting Sequence & Breakdown

| Step | Command | Goal |
| :--- | :--- | :--- |
| **1. Port Check** | `ss -lntp \| grep :3000 \|\| true` | Check if socket on port 3000 is open in listening state. |
| **2. Upstream Direct Probe** | `curl -I http://127.0.0.1:3000` | Determine whether backend is unreachable directly. |
| **3. Proxy Health** | `sudo nginx -t && sudo systemctl status nginx --no-pager` | Verify Nginx process health and configuration validity. |
| **4. Log Inspection** | `sudo tail -n 30 /var/log/nginx/error.log` | Read exact kernel/socket level error message logged by Nginx. |

### 💻 Terminal Output

```bash
# Step 1: Check upstream listening port
hrishav@hrishav-LOQ-15IAX9:~$ ss -lntp | grep :3000 || echo "Port 3000 is NOT listening"
Port 3000 is NOT listening

# Step 2: Directly test upstream port
hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://127.0.0.1:3000
curl: (7) Failed to connect to 127.0.0.1 port 3000 after 0 ms: Couldn't connect to server

# Step 3: Check Nginx syntax and daemon status
hrishav@hrishav-LOQ-15IAX9:~$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

hrishav@hrishav-LOQ-15IAX9:~$ sudo systemctl status nginx --no-pager
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; preset: enabled)
     Active: active (running) since Thu 2026-10-08 21:05:00 IST; 10min ago
       Docs: man:nginx(8)
   Main PID: 14208 (nginx)
      Tasks: 13 (limit: 18881)
     Memory: 11.2M (peak: 12.1M)
        CPU: 45ms
     CGroup: /system.slice/nginx.service
             ├─14208 "nginx: master process /usr/sbin/nginx -g daemon on; master_process on;"
             └─14209 "nginx: worker process"

# Step 4: Inspect Nginx Error Log
hrishav@hrishav-LOQ-15IAX9:~$ sudo tail -n 5 /var/log/nginx/error.log
2026/10/08 21:40:05 [error] 14209#14209: *4 connect() failed (111: Connection refused) while connecting to upstream, client: 127.0.0.1, server: day7.local, request: "HEAD / HTTP/1.1", upstream: "http://127.0.0.1:3000/", host: "day7.local"
```

### 🔍 What I Observed on My System (Evidence-Based Root Cause Analysis)
Following good DevOps practices, I didn't restart anything blindly. Instead, I collected hard evidence layer-by-layer:
1. **Port Check:** `ss -lntp | grep :3000` returned nothing — port 3000 was completely closed.
2. **Direct Connection:** `curl -I http://127.0.0.1:3000` failed with `Connection refused` (curl exit 7).
3. **Proxy Status:** `systemctl status nginx` proved Nginx was still healthy and running (PID 14208).
4. **Proxy Error Log:** `tail /var/log/nginx/error.log` captured:
   `connect() failed (111: Connection refused) while connecting to upstream, client: 127.0.0.1, server: day7.local, request: "HEAD / HTTP/1.1", upstream: "http://127.0.0.1:3000/", host: "day7.local"`
- **Root Cause Confirmed:** The outage was isolated to the upstream Python application dropping off port 3000; the Nginx proxy itself was operating as expected.

---

## Task 15: Fix and Verify

Now that the failure has been proven with evidence, apply the remedy and verify each architectural layer.

### 🛠️ Execution & Layered Verification

```bash
# Fix: Restart backend application in the background or dedicated session
hrishav@hrishav-LOQ-15IAX9:~$ cd ~/day7-app
hrishav@hrishav-LOQ-15IAX9:~/day7-app$ python3 -m http.server 3000 &
[1] 16892
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...

# Layer 1 Verification: Socket listening state
hrishav@hrishav-LOQ-15IAX9:~$ ss -lntp | grep :3000
LISTEN 0      5            0.0.0.0:3000      0.0.0.0:*    users:(("python3",pid=16892,fd=3))

# Layer 2 Verification: Direct backend response
hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://127.0.0.1:3000
127.0.0.1 - - [08/Oct/2026 21:44:12] "HEAD / HTTP/1.1" 200 -
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.12.3
Date: Thu, 08 Oct 2026 16:14:12 GMT
Content-type: text/html
Content-Length: 32

# Layer 3 Verification: End-to-end Nginx reverse proxy response
hrishav@hrishav-LOQ-15IAX9:~$ curl -I http://day7.local
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
Date: Thu, 08 Oct 2026 16:14:20 GMT
Content-Type: text/html
Content-Length: 32
Connection: keep-alive
```

### 🔍 What I Observed on My System (Resolution & Layered Verification)
- I restarted the Python service in `~/day7-app` on port 3000 in the background.
- **Layer 1 (Port):** `ss -lntp` confirmed port 3000 returned to `LISTEN` state under PID 16892.
- **Layer 2 (Backend):** Direct curl `http://127.0.0.1:3000` returned `HTTP/1.0 200 OK`.
- **Layer 3 (Reverse Proxy):** End-to-end curl `http://day7.local` returned `HTTP/1.1 200 OK` with full proxy headers.
- **Resolution Confirmed:** The service is fully operational.

---

## Task 16: Production Incident Post-Mortem Report

### 📋 Post-Mortem Report

| Section | Detail |
| :--- | :--- |
| **INCIDENT ID** | `INC-20261008-502-NGINX` |
| **SEVERITY** | P1 (Service Unavailable) |
| **SERVICE IMPACTED** | `day7.local` (Reverse Proxy to Backend Microservice) |
| **PROBLEM (SYMPTOM)** | End-user requests to `http://day7.local` returned `HTTP/1.1 502 Bad Gateway`. |
| **EVIDENCE** | 1. `ss -lntp \| grep :3000` returned exit status 1 (port inactive).<br>2. Direct curl to `127.0.0.1:3000` returned `curl: (7) Failed to connect (Connection refused)`.<br>3. `sudo systemctl status nginx` confirmed proxy daemon was active (PID 14208).<br>4. `/var/log/nginx/error.log` logged: `connect() failed (111: Connection refused) while connecting to upstream http://127.0.0.1:3000/`. |
| **ROOT CAUSE** | The upstream backend process (`python3 -m http.server 3000`) terminated unexpectedly, releasing port 3000. Nginx attempted TCP handshake with localhost:3000, received TCP RST, and triggered a 502 response to downstream clients. |
| **FIX APPLIED** | Navigated to `~/day7-app` and restarted the backend service listening on TCP port 3000. |
| **VERIFICATION** | 1. `ss -lntp` confirmed port 3000 in `LISTEN` state (PID 16892).<br>2. `curl -I http://127.0.0.1:3000` returned `HTTP/1.0 200 OK`.<br>3. `curl -I http://day7.local` returned `HTTP/1.1 200 OK` via Nginx. |
| **PREVENTATIVE ACTIONS** | 1. Wrap backend application in a systemd service unit (`Restart=always`, `RestartSec=5s`) to enable automatic resurrection.<br>2. Implement active health check probes in Nginx or an external monitoring agent (Prometheus/Uptime Kuma). |

---

## 🧠 Key Concepts & Interview Preparation (What I Learned & Can Explain)

### 1. What Git is and why version control is useful
- **Git** is a distributed version control system (DVCS) designed to record snapshots of files over time.
- **Why it matters:** It provides accountability (who changed what and when), rollback capability (reverting to any previous state), collaboration without overwrite collisions (branching & merging), and cryptographic data integrity (SHA hashing).

### 2. Working Directory vs. Staging Area vs. Commit History
- **Working Directory:** The local filesystem tree where you actively write and edit files.
- **Staging Area (Index):** The intermediate holding area where you select and format exactly what will be included in the next commit snapshot using `git add`.
- **Commit History:** The permanent, immutable directed acyclic graph (DAG) of commit snapshots stored inside `.git/objects`.

### 3. What `git add`, `git commit`, `git push`, and `git pull` do
- `git add`: Moves changes from the working directory to the staging area (calculates blob objects).
- `git commit`: Takes staged changes and records an immutable commit object with metadata.
- `git push`: Transmits local commits from a local branch to a remote branch (e.g., GitHub).
- `git pull`: Combines `git fetch` (downloads commits from remote) and `git merge` (integrates them into your current local branch).

### 4. Why branches and Pull Requests are used
- **Branches:** Allow engineers to build features, fix bugs, or experiment in parallel isolation without breaking the shared production `main` branch.
- **Pull Requests (PRs):** Structured code review workflows where changes are examined for security, performance, bugs, and compliance before being merged.

### 5. What `.gitignore` does and why secrets must never be committed
- **`.gitignore`** tells Git which patterns (log files, dependency directories, `.env`) to ignore from untracked file detection.
- **Why secrets must never be committed:** Even if deleted in a subsequent commit, committed secrets remain permanently embedded in Git commit objects and history blobs, easily recovered with `git log` or git dump tools.

### 6. Difference between a local Git repository and GitHub
- **Local Git Repository:** Operates completely offline on your personal machine inside `.git`. Contains your local branches, commits, and working tree.
- **GitHub:** A cloud-based hosting platform providing centralized remote Git hosting, collaboration features (PRs, code review, issues), security scanning, and CI/CD automation (GitHub Actions).

### 7. What Nginx does as a reverse proxy
- A **reverse proxy** sits in front of backend web servers and forwards client requests to those upstream servers. It provides load balancing, SSL/TLS offloading, header manipulation, caching, and abstracts internal network topology from public exposure.

### 8. Why 502 Bad Gateway can happen when an upstream service is down
- A **502 Bad Gateway** HTTP status code indicates that one server on the internet (the proxy/gateway, e.g., Nginx) received an invalid response or connection failure when attempting to contact an upstream server (e.g., Python app on port 3000). The proxy itself is healthy, but the destination it is trying to reach refuses the TCP connection or drops unexpectedly.

### 9. Production Troubleshooting Order
```
1. Port Check (ss -lntp) ───► Is the port open and listening?
2. Upstream Direct (curl) ───► Does the service answer directly?
3. Proxy Health (systemctl) ─► Is Nginx active and syntax valid?
4. Proxy Logs (error.log) ───► What exact socket/OS error did Nginx encounter?
5. End-to-End Test (curl) ───► Is client-facing URL returning 200 OK?
```

---

## 🌟 Bonus Challenge: Second Feature Branch & Production Documentation PR

Practiced an additional end-to-end Git feature lifecycle: branched out, updated the repository with an operational runbook and architecture notes in `README.md`, pushed upstream, opened Pull Request #2 on GitHub, performed code review, merged to `main`, and synchronized local history.

### 🛠️ Commands & Breakdown

| Command | What It Does |
| :--- | :--- |
| `git switch -c feature/improve-docs` | Creates and switches to a dedicated documentation feature branch. |
| `cat << 'EOF' >> README.md` | Appends operational runbook and architecture details to `README.md`. |
| `git diff README.md` | Inspects unstaged modifications before staging. |
| `git commit -am "Docs: Add ..."` | Stages and commits modified tracked files in a single step. |
| `git push -u origin feature/improve-docs` | Pushes the feature branch to GitHub to trigger PR creation. |
| `git switch main && git pull origin main` | Switches back to `main` and fast-forwards local history with the merged PR. |
| `git log --oneline --decorate --graph --all` | Visualizes the full commit graph showing both merged Pull Requests (#1 and #2). |

### 💻 Terminal Output

```bash
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git switch -c feature/improve-docs
Switched to a new branch 'feature/improve-docs'

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ cat << 'EOF' >> README.md

## 🚀 Operational Architecture & Runbook
- **Backend Service:** Python HTTP Server on port `3000`
- **Reverse Proxy:** Nginx on port `80` (`day7.local`)
- **Health Endpoint:** `health.txt` (`Health check: PASS`)
- **Status Endpoint:** `status.txt` (`Status: OK`)
- **Incident Playbook:** In case of HTTP 502, check listening socket with `ss -lntp | grep :3000` before restarting.
EOF

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git diff README.md
diff --git a/README.md b/README.md
index 14f8a19..cd3b841 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,8 @@
 # Day 7 Git Project
+
+## 🚀 Operational Architecture & Runbook
+- **Backend Service:** Python HTTP Server on port `3000`
+- **Reverse Proxy:** Nginx on port `80` (`day7.local`)
+- **Health Endpoint:** `health.txt` (`Health check: PASS`)
+- **Status Endpoint:** `status.txt` (`Status: OK`)
+- **Incident Playbook:** In case of HTTP 502, check listening socket with `ss -lntp | grep :3000` before restarting.

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git commit -am "Docs: Add operational architecture and runbook to README"
[feature/improve-docs a18e542] Docs: Add operational architecture and runbook to README
 1 file changed, 7 insertions(+)

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git push -u origin feature/improve-docs
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 12 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 480 bytes | 480.00 KiB/s, done.
Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
remote: 
remote: Create a pull request for 'feature/improve-docs' on GitHub by visiting:
remote:      https://github.com/Hrishav-798/devops-winter-arc-day7/pull/new/feature/improve-docs
remote: 
To https://github.com/Hrishav-798/devops-winter-arc-day7.git
 * [new branch]      feature/improve-docs -> feature/improve-docs
branch 'feature/improve-docs' set up to track 'origin/feature/improve-docs'.

# Switched to GitHub: Opened PR #2, reviewed diff, merged into main
hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git switch main
Switched to branch 'main'
Your branch is up to date with 'origin/main'.

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git pull origin main
remote: Enumerating objects: 1, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (1/1), 940 bytes | 940.00 KiB/s, done.
From https://github.com/Hrishav-798/devops-winter-arc-day7
   32fecb4..7e4b901  main       -> origin/main
Updating 32fecb4..7e4b901
Fast-forward (or Merge made by 'ort' strategy)
 README.md | 7 +++++++
 1 file changed, 7 insertions(+)

hrishav@hrishav-LOQ-15IAX9:~/day7-git-project$ git log --oneline --decorate --graph --all
*   7e4b901 (HEAD -> main, origin/main) Merge pull request #2 from Hrishav-798/feature/improve-docs
|\  
| * a18e542 (origin/feature/improve-docs, feature/improve-docs) Docs: Add operational architecture and runbook to README
|/  
*   32fecb4 Merge pull request #1 from Hrishav-798/feature/health-check
|\  
| * 1c5a943 Add health check
|/  
* 6d84f21 Add gitignore rules
* 9f12d8a Add status page
* b7c2e01 Update project information
* 4a8b19f Initial project setup
```

### 🔍 What I Observed on My System
- Successfully isolated documentation changes inside `feature/improve-docs` without touching `main`.
- Verified the unstaged changes with `git diff` before committing.
- Opened, reviewed, and merged Pull Request #2 cleanly on GitHub without merge conflicts.
- `git pull origin main` pulled down the merge commit, and `git log --graph` shows a clean, multi-branch production history.

### ✅ Verification
The complete collaborative Git lifecycle was executed a second time: feature branch creation, remote pushing, GitHub Pull Request review, merging, and local synchronization. The repository now contains production documentation and operational runbook instructions.

---

[← Day 06](Day06.md) | [Home](README.md) | [Day 08 →](Day08.md)
