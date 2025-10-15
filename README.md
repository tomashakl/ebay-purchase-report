# 🧾 eBay Purchase Report (public, config-driven)

## 🔍 About this project

This repository contains a **universal, public Python tool** for exporting your **eBay Purchase History** (filtered by year) into **CSV** and **HTML** reports.  
It is designed to be **privacy-safe**, easy to configure, and fully reusable — no personal credentials or API keys are stored.  
Ideal for collectors, analysts, or resellers who want to keep a local record of their purchases.

---

## 🚀 Quick Start

1. Install **Python 3.10+** and **Google Chrome**.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Create `config.yaml` or `config.json` (use `config.example.yaml` as a template).
4. Run:
   ```bash
   python ebay_purchases_list_only.py --year 2024 --site co.uk
   ```
   When the browser opens, **log in to eBay**, open **Purchase history**, select the desired year, and press **Enter** in the terminal.

> 🛡️ The tool does not use or store any credentials. You log in manually inside the opened Chrome window.

---

## ⚙️ Config

The script reads **`config.yaml`** or **`config.json`** if present in the same folder.  
Command-line arguments override values from the config file.

**Supported keys:**
- `year` *(int)* — target year (required unless passed via CLI/ENV)
- `site` *(`co.uk` or `com`)* — eBay domain (default: `co.uk`)
- `headless` *(bool)* — run Chrome invisibly
- `max_pages` *(int, default: 800)*
- `sleep` *(float, default: 2.0)* — pause between pages
- `jitter` *(list of two floats, default: `[0.5, 1.2]`)*
- `lang` *(string, default: `en-GB,en-US,cs-CZ`)*

You can also use environment variables:
```
EBAY_YEAR=2024
HEADLESS=true
```

---

## 🧩 How to Use the Config Generator

You can create your configuration file visually — no coding required.

1. Open **`config_generator.html`** in your web browser (double-click it).  
   It runs locally — nothing is uploaded or sent online.
2. Fill in your desired values:
   - Author name (optional)
   - Year (e.g. `2024`)
   - eBay domain (`co.uk` or `com`)
   - Whether to run in *headless* mode
   - Max pages to fetch (default: 800)
3. Click **“Download config.yaml”** or **“Download config.json”**.
4. Save the file in the same directory as the script.
5. Run:
   ```bash
   python ebay_purchases_list_only.py
   ```
   The script will automatically detect and use your config file.

> 💡 Tip: You can keep both `config.yaml` and `config.json` for different setups — the script automatically picks the first one it finds.

---

## 📊 Outputs

- `ebay_purchases_<YEAR>.csv` — clean CSV file for Excel or Sheets  
- `ebay_purchases_<YEAR>.html` — formatted HTML table  
- `debug_purchase_page_<YEAR>_p1.html` — first-page dump for offline parser testing  

**Columns:** `seller`, `item_title`, `order_total`, `currency`, `order_number`

---

## 🔒 Security & Privacy

- No passwords or sensitive data are used or stored.
- Manual login is performed inside your Chrome session.
- Safe for public or collaborative use.
- The `.gitignore` file already excludes output files and config data, so they won’t be pushed to GitHub.

---

## 🧠 Technology Stack

- **Python 3.10+**
- **Selenium**
- **WebDriver Manager**
- **BeautifulSoup4 + lxml**
- **pandas**
- *(optional)* **PyYAML** – for reading YAML configs

---

## 🪪 License

**MIT License** — you can freely use, modify, and redistribute this project, provided the copyright notice remains.  
See the file [LICENSE](LICENSE) for full text.

---

## 🙌 Credits

Created as an open, safe template for collectors and developers who want to analyze their eBay purchase history without exposing any personal data.  
Replace `{{AUTHOR_NAME}}` with your name or organization if you fork this repository.

---
