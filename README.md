# DeathConfuser

**The Ultimate Framework for Dependency Confusion & CI/CD Exploitation**

```
 /$$$$$$$                        /$$     /$$        /$$$$$$                       /$$$$$$                                        
| $$__  $$                      | $$    | $$       /$$__  $$                     /$$__  $$                                       
| $$  \ $$  /$$$$$$   /$$$$$$  /$$$$$$  | $$$$$$$ | $$  \__/  /$$$$$$  /$$$$$$$ | $$  \__//$$   /$$  /$$$$$$$  /$$$$$$   /$$$$$$ 
| $$  | $$ /$$__  $$ |____  $$|_  $$_/  | $$__  $$| $$       /$$__  $$| $$__  $$| $$$$   | $$  | $$ /$$_____/ /$$__  $$ /$$__  $$
| $$  | $$| $$$$$$$$  /$$$$$$$  | $$    | $$  \ $$| $$      | $$  \ $$| $$  \ $$| $$_/   | $$  | $$|  $$$$$$ | $$$$$$$$| $$  \__/
| $$  | $$| $$_____/ /$$__  $$  | $$ /$$| $$  | $$| $$    $$| $$  | $$| $$  | $$| $$     | $$  | $$ \____  $$| $$_____/| $$      
| $$$$$$$/|  $$$$$$$|  $$$$$$$  |  $$$$/| $$  | $$|  $$$$$$/|  $$$$$$/| $$  | $$| $$     |  $$$$$$/ /$$$$$$$/|  $$$$$$$| $$      
|_______/  \_______/ \_______/   \___/  |__/  |__/ \______/  \______/ |__/  |__/|__/      \______/ |_______/  \_______/|__/      
```

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-red)
![Status](https://img.shields.io/badge/Status-Active-success)
![OPSEC](https://img.shields.io/badge/OPSEC-Military%20Grade-black)

---

## ⚔️ Introduction

**DeathConfuser** is not just another script — it’s a **full-scale, modular framework** for **supply chain exploitation, CI/CD attacks, and dependency confusion.**
It automates **recon → payload generation → exploitation → callback verification → reporting**, letting you own pipelines and dependencies with zero manual effort.

Originally designed for **Bug Bounty Hunters, Red Teams, and Offensive Security researchers**, it weaponizes modern software ecosystems against themselves — while keeping you cloaked with **OPSEC-grade stealth features.**

---

## 🚀 Feature Matrix

| Category                     | Highlights                                                                                                      |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 🔍 **Recon**                 | Subdomain discovery, package leaks, typosquat generation, endpoint scraping, JS parser, tech fingerprinting     |
| 📦 **Dependency Confusion**  | Automatic ecosystem hijacking (`npm`, `pip`, `cargo`, `maven`, etc.), scoped package targeting, namespace abuse |
| ⚡ **CI/CD Exploitation**     | GitHub Actions, GitLab CI, Jenkins, Travis, CircleCI, DroneCI, TeamCity — fully automated injection & execution |
| 🧬 **Payload System**        | Jinja2-based polymorphic templates (`setup.py`, `cargo.toml`, `package.json`), adaptive YAML builders           |
| 🔁 **Callback Verification** | Interactsh, Burp Collaborator, custom webhooks, DNS/HTTP/SMTP listeners for exploit confirmation                |
| 👻 **OPSEC Engine**          | Proxy rotator, DoH resolvers, sandbox detectors, burner profiles, traffic jitter & padding, log scrubbing       |
| 📊 **Reporting**             | Export results in **HTML, JSON, Markdown** with timelines, IOCs, exploited hosts, callback metadata             |
| 🕹 **Interfaces**            | CLI for speed, REST API for automation, and WebUI for dashboards & orchestration                                |
| 🎯 **Presets**               | `stealth.yaml`, `aggressive.yaml`, `dev.yaml` — swap styles with a single flag                                  |

---

## 📂 Project Structure

```
DeathConfuser/
 ├── deathconfuser.py        # Main entrypoint
 ├── core/                   # Config, recon, logger, concurrency, proxy
 ├── modules/                # Exploit modules per ecosystem
 │    ├── npm/
 │    ├── pypi/
 │    ├── cargo/
 │    ├── maven/
 │    ├── composer/
 │    ├── docker/
 │    ├── nuget/
 │    ├── rubygems/
 │    ├── terraform/
 │    └── golang/
 ├── payloads/               # Jinja2 templates + builder
 ├── opsec/                  # Proxy rotation, sandbox detector, DoH, burners
 ├── reports/                # HTML, JSON, Markdown exporters
 ├── integrations/           # GitHub/GitLab API, CI injectors, Slack, webhooks
 ├── interfaces/             # CLI, REST API, WebUI
 ├── presets/                # Stealth / aggressive / dev configs
 └── utils/                  # fs_utils, js_parser, urltools, wordlists
```

---

## ⚡ Quickstart Guide

### 1️⃣ Install

```bash
git clone https://github.com/HasilMusil/DeathConfuser.git
cd DeathConfuser
pip install -r requirements.txt
```

### 2️⃣ Recon a Target

```bash
python3 deathconfuser.py --mode recon --target example.com
```

### 3️⃣ Run Exploitation

```bash
python3 deathconfuser.py --mode exploit --preset aggressive.yaml
```

### 4️⃣ Verify Callbacks

```bash
python3 deathconfuser.py --mode verify --collaborator-url xyz.oast.fun
```

### 5️⃣ Generate Report

```bash
python3 deathconfuser.py --report html --output report.html
```

---

## 🕵️ Example Workflow

1. **Recon** finds `internal-npm.example.com` and `requirements.txt` with private deps.
2. **DeathConfuser** generates typosquat `internal-utils` with backdoored `setup.py`.
3. Publishes payload to PyPI, pipeline installs it automatically.
4. **RCE executed** in GitHub Actions → callback logged via Interactsh.
5. Auto-generates `report.html` with timeline, payload hash, callback data.

---

###🔎 How Config Works in DeathConfuser

* **Main config file:** `config.yaml`
* **Presets folder:** `presets/` (e.g. `dev.yaml`, `stealth.yaml`, `aggressive.yaml`)
* Config loader merges:

  1. **Global defaults** (`config.yaml`)
  2. **Preset file** (if specified)
  3. **CLI overrides** (`--set key=value`)

So your config is **layered** → global defaults → preset → CLI flags.

---

## 📂 Example `config.yaml`

```yaml
# 🌍 Global configuration for DeathConfuser

# Logging
log_level: INFO               # DEBUG / INFO / WARNING / ERROR
log_file: deathconfuser.log   # Log file path

# Default preset if none specified in CLI
default_preset: dev

# Recon settings
recon:
  wordlist: utils/wordlists/common.txt   # Wordlist for subdomain/pkg hunting
  threads: 10                            # Concurrency for recon
  timeout: 10                            # Request timeout
  user_agents:                           # Randomized UA pool
    - Mozilla/5.0 (Windows NT 10.0; Win64; x64)
    - curl/7.88.0
    - Wget/1.21.3

# Exploitation settings
exploit:
  package_managers:
    - npm
    - pip
    - cargo
    - maven
  auto_publish: true         # Push poisoned package automatically
  verify_callback: true      # Require callback verification
  callback_url: https://xyz.oast.fun

# Payload system
payloads:
  polymorphic: true          # Enable randomized polymorphic payloads
  builder: jinja2            # Template engine
  stealth_sleep: 5-15        # Random sleep for sandbox evasion

# OPSEC / Privacy
opsec:
  proxy_rotation: true
  proxy_list: proxies.txt    # File containing proxy list
  doh_resolver: https://dns.google/dns-query
  scrub_logs: true
  sandbox_detect: true

# Reporting
report:
  formats: [html, json, md]   # Export formats
  output_dir: reports/        # Where to save reports
```

---

## 📝 Explanation of Fields

### **Global**

* `log_level`: Controls verbosity → `DEBUG` for dev, `INFO` for normal ops.
* `log_file`: Central log file for all modules.
* `default_preset`: If you don’t pass `--preset`, it uses this.

### **Recon**

* `wordlist`: Wordlist path for subdomain/package brute-forcing.
* `threads`: Concurrency (10 = safe, 50+ = aggressive).
* `timeout`: HTTP timeout in seconds.
* `user_agents`: Pool of UAs for rotation → avoid fingerprinting.

### **Exploit**

* `package_managers`: Which ecosystems to target (e.g. npm, pip).
* `auto_publish`: If `true`, DeathConfuser pushes payload automatically.
* `verify_callback`: Only consider success if callback received.
* `callback_url`: Your Interactsh/Burp Collab server.

### **Payloads**

* `polymorphic`: Randomizes payloads each run → avoids sig detection.
* `builder`: Currently Jinja2-based template system.
* `stealth_sleep`: Random delays to bypass sandbox timing checks.

### **OPSEC**

* `proxy_rotation`: Enable multi-proxy rotation.
* `proxy_list`: File containing proxy IPs (HTTP/SOCKS).
* `doh_resolver`: DNS-over-HTTPS server for leak-free lookups.
* `scrub_logs`: Auto-wipe local logs after run.
* `sandbox_detect`: Stops execution in sandbox/VM.

### **Reports**

* `formats`: Can export in HTML (pretty), JSON (machine-parseable), Markdown (bug bounty ready).
* `output_dir`: Where reports are saved.

---

## ⚡ Preset Example (`presets/aggressive.yaml`)

```yaml
# Aggressive engagement style
recon:
  threads: 50
  timeout: 5
exploit:
  auto_publish: true
  verify_callback: false   # Skip verification, just fire & forget
opsec:
  proxy_rotation: false    # YOLO mode
```

---

## 🌐 Interfaces

* **CLI** → Fast usage, chaining with scripts.
* **REST API** → Automate in bigger ops frameworks.
* **WebUI** → Control panel with dashboards, preset selectors, exploit orchestration, and live callback monitoring.

---

## 🧩 Supported Ecosystems

* **npm** (JavaScript)
* **pip/PyPI** (Python)
* **cargo** (Rust)
* **maven** (Java)
* **nuget** (.NET)
* **rubygems** (Ruby)
* **composer** (PHP)
* **docker** (Images / Hub hijacks)
* **terraform** (Registry poisoning)
* **golang** (Modules)

---

## 👻 OPSEC Toolkit

* Proxy rotator with **SOCKS + HTTP support**
* DNS over HTTPS resolvers (avoid local leaks)
* Sandbox detection (VM markers, sleep-skipping)
* Burner profiles & fake package metadata
* Traffic jitter / padding to evade correlation
* Auto log scrubbing + OPSEC verification engine

---

## 📊 Reports

* **HTML** → Clean dashboards for executives.
* **JSON** → Integrate with automation pipelines.
* **Markdown** → Copy-paste ready for bug bounty reports.
* Auto includes **exploit chain, timelines, payload hashes, IOCs.**

---

## ⚠️ Disclaimer

**DeathConfuser is for authorized penetration testing and research purposes only.**
The author is not responsible for misuse.

---

## 📜 License

This project is licensed over the [MIT License](LICENSE).
