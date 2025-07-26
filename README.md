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
║   ░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓██████▓▒░         ║
║                                                                              ║
║                  🦡 Badg3rFuzz - Fuzzing & brute force with reCAPTCHAv3 🦡  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Badg3rFuzz** is a tool designed for fuzzing and brute-forcing forms protected with reCAPTCHA v3. It combines Selenium for automatic token retrieval and multithreading to maximize speed.

---

## 🔥 Key Features

* Supports reCAPTCHA v3 (`site-key` + `action`)
* Brute force for usernames and passwords
* Automatic user fuzzers generation with multiple types
* Configurable multithreading for parallel attacks
* Auto-stop on successful credential discovery (`--stop-on-success`)
* Detailed logging to `.log` file with timestamp
* Support for custom `Origin` HTTP header
* Clean handling of `Ctrl+C` to stop execution gracefully
* **Firefox and Chrome WebDriver support**
* **Real-time progress bar with ETA**
* **Verbose mode for detailed debugging**

---

## 💻 Requirements and Compatibility

* Python 3.7+
* **Firefox (default) or Google Chrome** installed on your system:
  * **Firefox (recommended)**: 
    - Windows: Download from [https://mozilla.org/firefox](https://mozilla.org/firefox)
    - Linux: `sudo apt install firefox`
    - **Important**: Place `geckodriver.exe` in the same directory as the script
  * **Chrome (alternative)**: Install Chrome from [https://google.com/chrome](https://google.com/chrome)

* Python packages:
  ```bash
  pip install selenium webdriver-manager requests
  ```

* **WebDriver Setup**:
  - For Firefox: Download `geckodriver` from [GitHub](https://github.com/mozilla/geckodriver/releases) and place `geckodriver.exe` in the script directory
  - For Chrome: Automatically managed by `webdriver-manager`

---

## 🚀 Basic Usage

```bash
python badg3rfuzz.py \
  --site-key 6LemxMwUAAAAABCD1234XYZ \
  --captcha-action login \
  --login-url https://targetsite.com/login \
  --post-url https://targetsite.com/api/login \
  --pass-file passwords.txt \
  --user-file users.txt \
  --threads 10 \
  --stop-on-success
```

---

## ⚙️ Advanced Usage Examples

### With User Fuzzer and Chrome WebDriver
```bash
python badg3rfuzz.py \
  --site-key 6LemxMwUAAAAABCD1234XYZ \
  --captcha-action submit_form \
  --login-url https://secure.example.com/auth \
  --post-url https://secure.example.com/api/auth \
  --pass-file rockyou.txt \
  --user-fuzz digits:6:8:500 \
  --threads 8 \
  --webdriver chrome \
  --origin-url https://secure.example.com \
  --stop-on-success \
  --verbose
```

### With Mixed Fuzzer and No Banner
```bash
python badg3rfuzz.py \
  --site-key 6LemxMwUAAAAABCD1234XYZ \
  --captcha-action login \
  --login-url https://example.com/login \
  --post-url https://example.com/auth \
  --user-fuzz mix:8:12:100 \
  --threads 15 \
  --no-banner \
  --verbose
```

---

## 📋 Complete Parameters Reference

| Parameter           | Description                                                                                 | Required       | Default   |
| ------------------- | ------------------------------------------------------------------------------------------- | -------------- | --------- |
| `--site-key`        | Public reCAPTCHA key used to obtain tokens                                                  | **Yes**        | -         |
| `--captcha-action`  | Action associated with the reCAPTCHA (e.g., `login`, `submit_form`)                         | **Yes**        | -         |
| `--login-url`       | URL where the form and reCAPTCHA widget are loaded                                          | **Yes**        | -         |
| `--post-url`        | URL that receives the POST request with credentials                                         | **Yes**        | -         |
| `--pass-file`       | File containing passwords (one per line)                                                    | No\*           | Auto-generated |
| `--user-file`       | File containing usernames (one per line)                                                    | No\*           | Auto-generated |
| `--user-fuzz`       | Fuzzer to generate usernames automatically, format: `type:min_len:max_len:count`            | No\*           | `digits:5:12:20` |
| `--threads`         | Number of parallel threads for sending requests                                             | No             | 5         |
| `--stop-on-success` | Stops the process once valid credentials are found                                          | No             | Continue  |
| `--origin-url`      | URL used in HTTP `Origin` and `Referer` headers (useful for sites that check these headers) | No             | Auto-detect |
| `--webdriver`       | WebDriver to use: `firefox` or `chrome`                                                     | No             | firefox   |
| `--no-banner`       | Disables the ASCII banner printing                                                          | No             | Show banner |
| `--verbose`         | Activates detailed output including HTTP responses                                           | No             | Quiet mode |

\* If neither `--user-file` nor `--user-fuzz` is specified, numeric usernames are generated by default. If no `--pass-file` is provided, a strong password fuzzer is used.

---

## 🎯 User Fuzzer Types

The `--user-fuzz` parameter accepts the format: `type:min_len:max_len:count`

| Type      | Characters Used                              | Example                    |
| --------- | -------------------------------------------- | -------------------------- |
| `digits`  | 0-9                                          | `digits:6:6:100`           |
| `digits+` | 1-9 (excluding 0)                            | `digits+:5:8:50`           |
| `letters` | a-z, A-Z                                     | `letters:4:10:200`         |
| `mix`     | a-z, A-Z, 0-9                                | `mix:8:12:300`             |
| `strong`  | a-z, A-Z, 0-9, punctuation                   | `strong:10:16:100`         |

**Examples:**
- `digits:6:6:100` - Generate 100 numeric usernames, exactly 6 digits long
- `mix:8:12:500` - Generate 500 alphanumeric usernames, between 8-12 characters
- `letters:4:8:50` - Generate 50 alphabetic usernames, between 4-8 characters

---

## 📊 Output and Logging

### Console Output
- **Progress bar** with real-time statistics (attempts, percentage, ETA)
- **Color-coded messages** for success/failure/errors
- **Verbose mode** shows detailed HTTP responses

### Log Files
- Auto-generated filename: `fuzzlog-DD-MM-YYYY_HH-MM-SS.log`
- Contains all attempts with SUCCESS/FAIL status
- Format: `SUCCESS: username:password` or `[-] FAIL: username:password`

### Example Output
```
🦡 Badg3rFuzz v1.0
Start: 26-07-2025 15:30:45

[>] Initializing Badg3rFuzz modules...
[>] Loading fuzzing payloads and brute force wordlists...
[>] 400 combo prepares.
[>] Ready to fuzz and bruteforce your targets! 🦡💥
[>] Starting 5 threads...

[==============================] 245/400 (61.25%) | ETA: 12.3s
[+] Attempt: admin:password123
[+] Valid Login Found! admin:password123

[✔] Finished Attacks. Total: 246
⌛ Finished: 26-07-2025 15:32:18 (duration 0:01:33)
```

---

## 🛠️ Installation and Setup

### Quick Installation
```bash
git clone https://github.com/yourusername/badg3rfuzz.git
cd badg3rfuzz
pip install -r requirements.txt
```

### WebDriver Setup

#### Firefox (Recommended)
1. Download geckodriver from: https://github.com/mozilla/geckodriver/releases
2. Extract `geckodriver.exe` to the same folder as `badg3rfuzz.py`
3. Ensure Firefox is installed in standard location:
   - Windows: `C:\Program Files\Mozilla Firefox\firefox.exe`
   - Linux: `/usr/bin/firefox`

#### Chrome (Alternative)
- No manual setup required, `webdriver-manager` handles everything automatically
- Just ensure Chrome is installed on your system

---

## 🔧 Troubleshooting

### Common Issues

**Firefox opens browser windows despite headless mode:**
- Update to latest Firefox and geckodriver versions
- Try using Chrome: `--webdriver chrome`
- Check verbose output: `--verbose`

**Ctrl+C doesn't stop the program:**
- Fixed in latest version with proper signal handling
- Force quit with Ctrl+Z (Linux/Mac) or Task Manager (Windows)

**"geckodriver.exe not found" error:**
- Download geckodriver and place in script directory
- Or use Chrome: `--webdriver chrome`

**reCAPTCHA token errors:**
- Verify the `--site-key` is correct (found in page source)
- Check that `--captcha-action` matches the form's action
- Ensure `--login-url` loads the reCAPTCHA widget

---

## 📈 Performance Tips

- **Optimal thread count**: Start with 5-10 threads, increase gradually
- **Use Chrome for stability**: `--webdriver chrome` (especially on Windows)
- **Large wordlists**: Use `--stop-on-success` to stop on first valid credentials
- **Network issues**: Reduce thread count if you see many connection errors
- **Memory usage**: For huge wordlists, consider splitting into smaller files

---

## ⚖️ Legal Disclaimer

This tool is intended for **authorized penetration testing and educational purposes only**. 

**You must:**
- Have explicit written permission to test the target system
- Comply with all applicable laws and regulations
- Use responsibly and ethically

**The author is not responsible for any misuse or damage caused by this tool.**

---

## 📈 To-Do / Future Improvements

* [ ] Proxy integration for anonymizing requests
* [ ] Support for reCAPTCHA v2 / visible challenges
* [ ] Robust pause and resume with checkpointing
* [ ] Support for multiple authentication types/forms
* [ ] Improved automatic success/error detection via dynamic response analysis
* [ ] More detailed reporting in JSON or CSV formats
* [ ] Enhanced interface with interactive menu or basic web GUI
* [ ] Rate limiting and delay options to avoid detection

---

## ☕ Buy Me a Coffee?

If you like Badg3rFuzz and want to support me to keep improving tools and learning, you can buy me a coffee.

Support my work here:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/X8X61IO019)

---

## 🔧 Requirements.txt

```
selenium>=4.0.0
webdriver-manager>=3.8.0
requests>=2.25.0
```

---

## 📞 Contact

If you have questions or suggestions, please open an issue on GitHub.

---

Thanks for using Badg3rFuzz! 🦡💥