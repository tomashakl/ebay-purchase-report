# 🧾 eBay Purchase Report (public, config-driven)

This repository contains a **public, universal** tool to export your eBay Purchase History for a given year into **CSV** and **HTML**.  
It stores **no personal data** and is safe to publish as a template. Users provide their own session by logging in manually in the opened browser window.

---

## Quick Start

1. Install Python 3.10+ and Google Chrome.
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

> No credentials are stored in this repo. If desired, you can set env vars like `EBAY_YEAR=2024` or `HEADLESS=true`.

---

## Config

- The script reads `config.yaml` or `config.json` if present.
- CLI flags override config values.
- Supported keys:
  - `year` (int) — target year (required unless passed via CLI/ENV)
  - `site` (`co.uk` or `com`) — eBay domain (default: `co.uk`)
  - `headless` (bool)
  - `max_pages` (int, default: 800)
  - `sleep` (float, default: 2.0)
  - `jitter` (list of two floats, default: `[0.5, 1.2]`)
  - `lang` (string, default: `en-GB,en-US,cs-CZ`)

Use the local **Config Generator** page to produce a config file offline: `config_generator.html` (nothing is uploaded anywhere).

---

## Outputs

- `ebay_purchases_<YEAR>.csv` — clean CSV
- `ebay_purchases_<YEAR>.html` — simple HTML table
- `debug_purchase_page_<YEAR>_p1.html` — first page dump for parser testing

Columns: `seller`, `item_title`, `order_total`, `currency`, `order_number`

---

## Security & Privacy

- No passwords or personal data in code or repo.
- Prefer manual login in the opened browser window (recommended).
- If you use credentials, store them in an OS keychain or environment variables — **never commit them**.
- Add exports to `.gitignore` (included by default) to avoid committing private data.

---

## License

MIT — see `LICENSE`.

---

## Credits

Based on public parsing and Selenium automation patterns. Replace `{{AUTHOR_NAME}}` with your name or organization in this README if you wish.
