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

## Configuration System

Configuration values are layered:
1. **Default** – `config.yaml` (if present).
2. **Preset** – YAML file from `presets/` selected via `--preset`.
3. **Overrides** – `--set key=value` pairs on the CLI.

`core/config.py` exposes:
+ `Config.load(path, preset, overrides)` – merge all layers.
+ `ArgumentParser.parse()` – convenience parser returning a `Config` instance.
+ Deep dot‑notation overrides (`--set recon.mode=aggressive`).

### Example `config.yaml`
``` yaml
# logging
log_level: INFO
log_file: logs/deathconfuser.log

# default targets file
targets: targets.txt

# recon behaviour
recon_v2: true
recon_mode: stealth

# enabled modules
modules:
  - npm
  - pypi
  - maven

# async execution limits
concurrency:
  limit: 10
  retries: 1
  timeout: 30

# callback destinations
callback:
  http_url: http://127.0.0.1:8000/
  dns_domain: cb.example

# preferred payload builder
payload_builder: template
```

Any of these can be overridden by presets or `--set`.

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
