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
* Automatic user fuzzers generation
* Configurable multithreading for parallel attacks
* Auto-stop on successful credential discovery (`--stop-on-success`)
* Detailed logging to `.log` file
* Support for custom `Origin` HTTP header
* Clean handling of `Ctrl+C` to stop execution gracefully

---

## 💻 Requirements and Compatibility

* Python 3.7+
* Google Chrome installed on your system:

  * Windows: Install Chrome from [https://google.com/chrome](https://google.com/chrome)
  * Linux (Debian/Ubuntu): `sudo apt install google-chrome-stable` or official Chrome/Chromium
* Python packages:

  ```bash
  pip install -r requirements.txt
  ```

- Unix and Windows environments behave similarly, but on Windows it is recommended to run from CMD/Powershell with proper permissions and avoid paths with spaces.
- The script uses Selenium with `webdriver-manager` to automatically manage the matching `chromedriver` version.

---

## 🚀 Basic Usage

```bash
python badg3rscan.py \
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

## ⚙️ Usage with User Fuzzer and Origin Header

```bash
python badg3rscan.py \
  --site-key 6LemxMwUAAAAABCD1234XYZ \
  --captcha-action submit_form \
  --login-url https://secure.example.com/auth \
  --post-url https://secure.example.com/api/auth \
  --pass-file rockyou.txt \
  --user-fuzz digits:6:8:500 \
  --threads 8 \
  --origin-url https://secure.example.com \
  --stop-on-success
```

* `--user-fuzz digits:6:8:500` generates 500 numeric usernames between 6 and 8 characters long.
* `--origin-url` sets the HTTP `Origin` and `Referer` headers (useful to avoid CORS blocks or strict validation).

---

## 📋 Parameters

| Parameter           | Description                                                                                 | Required       |
| ------------------- | ------------------------------------------------------------------------------------------- | -------------- |
| `--site-key`        | Public reCAPTCHA key used to obtain tokens                                                  | Yes            |
| `--captcha-action`  | Action associated with the reCAPTCHA (e.g., `login`, `submit_form`)                         | Yes            |
| `--login-url`       | URL where the form and reCAPTCHA widget are loaded                                          | Yes            |
| `--post-url`        | URL that receives the POST request with credentials                                         | Yes            |
| `--pass-file`       | File containing passwords (one per line)                                                    | No\*           |
| `--user-file`       | File containing usernames (one per line)                                                    | No\*           |
| `--user-fuzz`       | Fuzzer to generate usernames automatically, format: `type:min_len:max_len:count`            | No\*           |
| `--threads`         | Number of parallel threads for sending requests                                             | No (default 5) |
| `--stop-on-success` | Stops the process once valid credentials are found                                          | No             |
| `--origin-url`      | URL used in HTTP `Origin` and `Referer` headers (useful for sites that check these headers) | No             |
| `--no-banner`       | Disables the ASCII banner printing                                                          | No             |

\* If neither `--user-file` nor `--user-fuzz` is specified, numeric usernames are generated by default. If no `--pass-file` is provided, a strong password fuzzer is used.

---

## 📈 To-Do / Future Improvements

* [ ] Proxy integration for anonymizing requests
* [ ] Support for reCAPTCHA v2 / visible challenges
* [ ] Robust pause and resume with checkpointing
* [ ] Support for multiple authentication types/forms
* [ ] Improved automatic success/error detection via dynamic response analysis
* [ ] More detailed reporting in JSON or CSV formats
* [ ] Enhanced interface with interactive menu or basic web GUI

---

## ☕ Buy Me a Coffee?

If you like Badg3rFuzz and want to support me to keep improving tools and learning, you can buy me a coffee.

Support my work here:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/X8X61IO019)

---

## 🔧 Quick Installation

```bash
git clone https://github.com/yourusername/badg3rfuzz.git
cd badg3rfuzz
pip install -r requirements.txt
```

---

## 📞 Contact

If you have questions or suggestions, please open an issue on GitHub.

---

Thanks for using Badg3rFuzz! 🦡💥

---
