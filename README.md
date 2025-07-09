# DeathConfuser (Beta)

🚨 **DeathConfuser** is an ultra-featured, multi-target automation tool for **Dependency Confusion** vulnerability detection.  
🎯 Built in pure Bash, this script scans live targets, detects tech stacks, extracts JS packages, checks unclaimed NPM names, and even generates live payloads for exploitation testing.  

> ⚠️ This is a **BETA version**. It's already highly functional and battle-tested, but more features are on the roadmap.

---

## 🚀 Features

- 🎯 Multi-target scanning (`targets.txt`)
- 🔍 Automatic tech stack detection (Node.js, PHP, Python, etc.)
- 🧠 Smart package name mutation (e.g., `pkg`, `pkg-dev`, `pkg-logger`)
- 📦 Live NPM registry checking for package claim status
- ⚙️ Auto payload generation based on stack
- 🌐 Listener callback system for exploit confirmation
- 🐚 Proxy support, CI mode, logging, JSON result output
- 📄 Config file support with `jq`

---

## 🔧 Usage

```bash
chmod +x deathconfuser_beta.sh
./deathconfuser_beta.sh targets.txt [options]
```

---

## 📚 Options

```
| Flag         | Description                                                                     |
| ------------ | ------------------------------------------------------------------------------- |
| `--listener` | Set custom listener URL (default: [http://your.oast.fun](http://your.oast.fun)) |
| `--tech`     | Manually override detected tech stack                                           |
| `--config`   | Load from a JSON config file                                                    |
| `--no-logs`  | Disable logging output                                                          |
| `--ci`       | Enable CI-compatible output (GitHub Actions, etc)                               |
```

---

## 📁 Output Structure

```
results/
├── example.com/
│   ├── jsdump/
│   ├── tech.txt
│   └── vulns.json
payloads/
└── example.com/
    └── [generated payloads here]
```

---

## 🧪 Example Config File

```
{
  "listener_url": "http://your.oast.fun",
  "concurrent": 10,
  "tech_override": "Node.js (Express)",
  "request_delay": 1,
  "proxy_cmd": "torsocks"
}
```

---

## ⚠️ Disclaimer
This tool is provided for educational and authorized testing purposes only.
The author is not responsible for any misuse. Always have permission before scanning or exploiting any system.

## 📜 License
This project is licensed under the terms of the [MIT License](LICENSE).
