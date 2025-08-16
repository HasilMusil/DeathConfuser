# DeathConfuser

**The Ultimate Framework for Dependency Confusion & CI/CD Exploitation**

```
________                 __  .__    _________                _____                         
\______ \   ____ _____ _/  |_|  |__ \_   ___ \  ____   _____/ ______ __ ______ ___________ 
 |    |  \_/ __ \\__  \\   __|  |  \/    \  \/ /  _ \ /    \   __|  |  /  ____/ __ \_  __ \
 |    `   \  ___/ / __ \|  | |   Y  \     \___(  <_> |   |  |  | |  |  \___ \\  ___/|  | \/
/_______  /\___  (____  |__| |___|  /\______  /\____/|___|  |__| |____/____  >\___  |__|   
        \/     \/     \/          \/        \/            \/               \/     \/       
```

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-red)
![Status](https://img.shields.io/badge/Status-Active-success)
![OPSEC](https://img.shields.io/badge/OPSEC-Military%20Grade-black)

---

## Introduction & Purpose

DeathConfuser is a research framework focused on dependency confusion and CI/CD exploitation.
It automates discovery of package references, probes public registries for unclaimed names, generates
opsec-aware payloads and verifies execution via multiple callback channels.

The project is intended for red‑team exercises and supply‑chain security research.
It includes interfaces for command‑line usage, a REST API and a small WebUI.


---

## Feature Matrix

| Category                  | Highlights                                                                                                                                                                                                            |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Recon**                 | Passive subdomain enumeration, JavaScript scraping, GitHub/GitLab search, local file scanning, technology fingerprinting, target feed aggregation                                                                     |
| **Dependency Confusion**  | Scanner modules for `npm`, `pypi`, `maven`, `nuget`, `composer`, `rubygems`, `golang`, `rust`, `docker`, `terraform`, `cpan`, `hackage`, `hexpm`, `swiftpm`, `cocoapods`, `conda`, `meteor` with typosquat generation |
| **CI/CD Injection**       | Injects GitHub Actions workflows, GitLab CI jobs and Jenkins steps (`integrations/ci_injector.py`)                                                                                                                    |
| **Payload System**        | Jinja2 templates, dynamic builders extracting environment secrets, optional obfuscation (base64/xor/timing)                                                                                                           |
| **Callback Verification** | HTTP listener, DNS over HTTPS lookups, optional Interactsh/Burp endpoints, callback classification and correlation                                                                                                    |
| **OPSEC Toolkit**         | Proxy rotation with Tor support, DNS-over-HTTPS resolver, sandbox detection heuristics, disposable infrastructure & burner identities                                                                                 |
| **Machine Learning**      | Package variant prediction, payload selection, callback severity classification, OPSEC behaviour adjustment, target priority scoring                                                                                  |
| **Reporting**             | Export findings in **HTML**, **JSON** and **Markdown** using Jinja2 templates                                                                                                                                         |
| **Interfaces**            | CLI (`--mode cli`), REST API (`--mode api`) and WebUI (`--mode web`)                                                                                                                                                  |
| **Extensibility**         | Plugin system, simulation environment, configurable presets                                                                                                                                                           |

---

## Architecture Overview

```
DeathConfuser/
├── deathconfuser.py        – entry point
├── core/                   – recon, ML, callback, concurrency, proxy, config
├── integrations/           – GitHub/GitLab APIs, CI injectors, notifications
├── modules/                – ecosystem scanners, payloads and publishers
├── payloads/               – Jinja2 templates and dynamic builders
├── opsec/                  – proxy rotator, DoH resolver, sandbox detector
├── reports/                – export utilities & templates
├── interface/              – CLI, REST API, WebUI
├── presets/                – configurable profiles
├── plugins/                – plugin API and examples
├── ml_models/              – JSON ML models
└── ml_training/            – training scripts & datasets
```

---

## Installation

```bash
git clone https://github.com/HasilMusil/DeathConfuser.git
cd DeathConfuser
pip install -r requirements.txt
```

### Retrain ML Models (optional)

```bash
python ml_training/train_models.py
```

Generates updated `.json` model files in `ml_models/` using the synthetic datasets in `ml_training/data/`.

## Quickstart Examples

### Recon

```
python deathconfuser.py --mode cli --targets targets.txt --preset recon-only
```
+ Uses the configured recon engine (Recon by default, ReconEngineV2 when recon_v2: true).


### Exploitation Scan

```
python deathconfuser.py --mode cli --preset stealth --targets targets.txt --builder template --output reports
```
+ Scrapes targets, detects unclaimed packages across enabled modules and writes reports.


### Callback Verification

```
python deathconfuser.py --mode cli --preset dev --targets targets.txt --builder dynamic
```
+ Callbacks are recorded in reports/json/callbacks.json
+ Dynamic payloads exfiltrate environment variables to the configured callback endpoints.


### Reporting Only

```
python deathconfuser.py --mode cli --targets targets.txt --output reports
```
+ Reports generated in reports/{html,json,markdown}/scan.*

---

###  How Config Works in DeathConfuser

* **Main config file:** `config.yaml` (project root)
* **Presets folder:** `presets/` (e.g. `dev.yaml`, `stealth.yaml`, `aggressive.yaml`)
* **CLI override:** `--set key=value` for deep nested keys

**Merge order is always deterministic**:

1. **Global defaults** → loaded from `config.yaml`
2. **Preset file** → `--preset name` or `default_preset` in `config.yaml`
3. **External config** → `-c / --config` (overrides both defaults & preset)
4. **CLI overrides** → `--set key=value` (deep merge, dot-notation & list indexing)

*Preset and external config merges are **shallow** at top-level keys; CLI `--set` merges are **deep**, creating nested dicts if missing.*

---

## Example `config.yaml`

```yaml
# Global configuration for DeathConfuser

# Logging
log_level: INFO                # DEBUG / INFO / WARNING / ERROR
log_file: logs/deathconfuser.log  # Relative or absolute path to log file

# Default preset if none specified in CLI
default_preset: dev

# Recon settings
recon:
  wordlist: utils/wordlists/common.txt  # Wordlist for subdomain/pkg hunting
  threads: 10                           # Concurrency for recon (safe = 10, high = 50+)
  timeout: 10                           # HTTP request timeout in seconds
  user_agents:                          # UA rotation pool (avoids fingerprinting)
    - Mozilla/5.0 (Windows NT 10.0; Win64; x64)
    - curl/7.88.0
    - Wget/1.21.3
  mode: stealth                         # Default scan mode: passive / stealth / aggressive
  v2_engine: true                       # Use ReconEngineV2 if true

# Exploitation settings
exploit:
  package_managers:                     # Which ecosystems to scan/publish to
    - npm
    - pypi
    - cargo
    - maven
  auto_publish: true                     # Automatically publish found package names
  verify_callback: true                  # Only confirm exploitation if callback received
  callback:
    http_url: https://xyz.oast.fun       # Primary HTTP callback endpoint
    dns_domain: cb.example               # Optional DNS callback domain
  retries: 1                             # Retry failed exploitation attempts
  timeout: 30                            # Exploitation request timeout

# Payload system
payloads:
  polymorphic: true                      # Enable randomized, mutation-based payloads
  builder: template                      # template | dynamic
  stealth_sleep: 5-15                    # Random delay (seconds) for sandbox/timing evasion
  obfuscation:                           # Optional payload obfuscation
    base64: true
    xor: false
    timing: false

# OPSEC / Privacy
opsec:
  proxy_rotation: true
  proxy_list: proxies.txt                # Path to proxy list file (HTTP/SOCKS)
  use_tor: false                         # Route traffic via Tor (requires running Tor daemon)
  doh_resolver: https://dns.google/dns-query  # DNS-over-HTTPS server
  sandbox_detect: true                   # Abort in CI/VM/sandbox environments
  scrub_logs: false                      # Planned feature: remove sensitive data from logs
  burner_profiles: opsec/burner_profiles.yaml # Pre-built fake identities

# Reporting
report:
  formats: [html, json, markdown]        # html | json | markdown
  output_dir: reports/                   # Directory to store reports
  template_dir: reports/templates/       # Directory containing export templates
  callback_log: reports/json/callbacks.json  # File to record callbacks

# Concurrency
concurrency:
  limit: 10                              # Max concurrent async tasks
  retries: 1                             # Retry count for failed requests
  timeout: 30                            # Task timeout in seconds
```

---

## Explanation of Fields

### **Global**

* `log_level`: Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
* `log_file`: Path to log output. Relative paths are resolved from project root.
* `default_preset`: Name of preset to auto-load if `--preset` not passed.

---

### **Recon**

* `wordlist`: Wordlist path for subdomain/package enumeration.
* `threads`: Thread count for synchronous operations. For async scans, see `concurrency.limit`.
* `timeout`: Max wait time for each request.
* `user_agents`: Pool for random UA rotation per request.
* `mode`: Recon mode – `passive` (no requests), `stealth` (low volume), `aggressive` (fast & noisy).
* `v2_engine`: Switch to ReconEngineV2 for better detection & speed.

---

### **Exploit**

* `package_managers`: List of ecosystems to scan and publish payload packages into.
* `auto_publish`: If true, automatically upload payload package once a free namespace is found.
* `verify_callback`: Require a successful callback event before marking a target exploited.
* `callback.http_url`: HTTP endpoint for receiving callbacks (Interactsh, Burp Collaborator, custom).
* `callback.dns_domain`: Optional domain for DNS-based callbacks.
* `retries`: Retry failed publication attempts.
* `timeout`: Timeout for publishing and verification requests.

---

### **Payloads**

* `polymorphic`: Enable payload mutation per run (avoids signature-based detection).
* `builder`:

  * `template`: Jinja2 templates from `payloads/`
  * `dynamic`: Auto-build payload from target’s stack fingerprint
* `stealth_sleep`: Range in seconds for random delays before execution.
* `obfuscation.base64`: Encode payload in base64.
* `obfuscation.xor`: XOR-encode payload.
* `obfuscation.timing`: Insert timing-based delays for anti-analysis.

---

### **OPSEC**

* `proxy_rotation`: Rotate outbound requests through a proxy list.
* `proxy_list`: File containing proxy IPs.
* `use_tor`: Enable routing through Tor network.
* `doh_resolver`: DNS-over-HTTPS endpoint to avoid local DNS leaks.
* `sandbox_detect`: Detect CI, virtual machines, and sandbox environments.
* `scrub_logs`: Planned feature to remove sensitive lines from local logs.
* `burner_profiles`: YAML file with pre-generated fake identities for OPSEC.

---

### **Reports**

* `formats`: Output formats (`html` for human-readable, `json` for automation, `markdown` for bug bounty reports).
* `output_dir`: Directory for storing generated reports.
* `template_dir`: Jinja2 templates for HTML/Markdown export.
* `callback_log`: File to record received callback events in JSON format.

---

### **Concurrency**

* `limit`: Max simultaneous async tasks.
* `retries`: Retry attempts for failed requests.
* `timeout`: Async task timeout in seconds.

---

## Presets

| File              | Purpose                                                                      |
| ----------------- | ---------------------------------------------------------------------------- |
| `stealth.yaml`    | Low thread count, proxy chain with Tor, delayed callbacks, no auto‑publish   |
| `aggressive.yaml` | High thread count, all callbacks enabled, automatic publishing and reporting |
| `dev.yaml`        | Verbose logging, dry‑run, local HTTP listener, outputs to `./debug_reports`  |
| `recon-only.yaml` | Passive reconnaissance only, no payloads or callbacks                        |
| `ci-burner.yaml`  | CI focused attacks, enables `ci_injector` and delayed payload execution      |

---

## Interfaces

### CLI

``` css
python deathconfuser.py --preset <name> --targets <file> [--output DIR] [--builder template|dynamic] [--mode cli|api|web] [-c config.yaml]
```
+ `--mode cli` (default) runs a scan and optionally writes reports.
+ `--mode api` starts the REST API.
+ `--mode web` launches the WebUI.

### REST API (`--mode api`)

Endpoints:
+ `POST /start` – JSON body `{ "targets": "...", "preset": "dev" }`
+ `POST /stop` – cancel running scan.
+ `GET /status` – check running state.
+ `GET /results` – retrieve accumulated results.

### WebUI (`--mode web`)

Minimal FastAPI dashboard:
+ Shows running status and tail of log file.
+ Form to start/stop scans and select preset or builder.
+ Displays recorded callbacks with severity filtering.

---

## OPSEC Toolkit

Located under `opsec/` and `core/opsec.py`.
+ **ProxyRotator** – rotates through HTTP/SOCKS proxies, supports chaining and Tor (`use_tor`).
+ **DNS-over-HTTPS** – `dns_over_https.py` performs asynchronous resolution to hide DNS queries.
+ **Sandbox Detector** – heuristics detecting CI/sandbox/VM environments.
+ **InfraManager** – provisions disposable domains/IPs and generates burner identities.
+ **Jitter & Identity** – random delays and header injection (`core/opsec.py`).
+ **Profiles** – `burner_profiles.yaml` contains pre‑built personas.
+ Log scrubbing is planned but not yet implemented.

---

## Machine Learning Features

+ `predict_package_variants` – suggests typosquat names from a base package (`ml_models/package_model.json`).
+ `select_payload_for_stack` – chooses an appropriate payload template based on detected stack.
+ `classify_callback_severity` – rates callback events (`ml_models/severity.json`).
+ `adjust_opsec_behavior` – alters identities (UA, delay) based on risk level.
+ `score_target_priority` – ranks targets when generating feeds.
Models are simple JSON look‑ups or optional sklearn pipelines.
Training data and scripts reside in `ml_training/`.


---

## Supported Ecosystems

Modules implement a uniform interface:
+ **JavaScript/Node:** npm, yarn (npm module), meteor
+ **Python:** pypi, conda
+ **Java:** maven
+ **.NET:** nuget
+ **PHP:** composer
+ **Ruby:** rubygems
+ **Go:** golang
+ **Rust:** rust (cargo)
+ **Perl/Haskell/Swift/Objective‑C:** cpan, hackage, swiftpm, cocoapods
+ **Infrastructure:** docker, terraform
+ **Others:** hexpm (Elixir), cocoapods, conda, meteor
Each module contains a `Scanner`, `payload` generator and `publisher`.

---

## Reporting

`reports/exporter.py` normalises scan data and writes reports to:
+ `reports/json/scan.json`
+ `reports/html/scan.html`
+ `reports/markdown/scan.md`
Templates are located under `reports/templates/`.

---

## Development Notes & Contributing

+ Designed for Python 3.10+.
+ Asynchronous code uses `aiohttp` and `asyncio`.
+ Tests cover core features (`test/`).
+ Plugins can extend functionality by subclassing `plugins.plugin_api.Plugin`.

Contributions are welcome via pull request.
Please ensure additions are tested.

---

## Announcements

**There is no announcements.**

---

## Disclaimer

**DeathConfuser is for authorized penetration testing and research purposes only.**
**The author is not responsible for misuse.**

---

## License

This project is licensed over the [MIT License](LICENSE).
