#!/usr/bin/env python3
"""
eBay Purchase Report — public, config-driven version
- No personal data committed.
- Reads defaults from config.json or config.yaml if present.
- CLI flags override config.
- Login is manual in the opened Chrome window (recommended).

Author: {{AUTHOR_NAME}} (replace in README or config), 2025
License: MIT
"""
import re, time, random, argparse, sys, os, json
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Optional YAML support without hard dependency if file not present
def _load_yaml_if_available(text: str):
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except Exception:
        return None

# ------------------ Regex patterns ------------------
LBL_TOTAL = re.compile(r"(Order total|Celkem objednávky|Gesamtsumme|Total del pedido|Total de la commande|Totale ordine)", re.I)
LBL_NUM   = re.compile(r"(Order number|Číslo objednávky|Bestellnummer|Número de pedido|Numéro de commande|Numero ordine)", re.I)
LBL_SOLD  = re.compile(r"(Sold by|Prodává|Verkauft von|Vendido por|Vendu par)", re.I)
MONEY_RE  = re.compile(r"([£$€])\s*([\d\.,]+)")

def clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0"," ").split())

def sleep_with_jitter(base: float, jlo: float, jhi: float):
    time.sleep(base + random.uniform(jlo, jhi))

def auto_scroll(driver, steps=10, pause=0.7):
    last = 0
    for _ in range(steps):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        h = driver.execute_script("return document.body.scrollHeight;")
        if h == last: break
        last = h
    driver.execute_script("window.scrollTo(0, 0);")

def nearest_text_block(node):
    cur = node
    for _ in range(3):
        if getattr(cur, "parent", None):
            cur = cur.parent
    return clean(BeautifulSoup(str(cur), "lxml").get_text(" ")), cur

def extract_meta_from_text(txt: str):
    total = currency = order_no = seller = ""

    m = re.search(LBL_TOTAL.pattern + r"\s*:\s*([£$€]\s*[\d\.,]+)", txt, re.I)
    if m:
        total = m.group(2)
        m2 = MONEY_RE.search(total)
        if m2: currency = m2.group(1)

    m = re.search(LBL_NUM.pattern + r"\s*:\s*([0-9A-Za-z\-]+)", txt, re.I)
    if m:
        order_no = m.group(2)

    m = re.search(LBL_SOLD.pattern + r"\s*:\s*([^\|·\n\r]+?)\s*(?:\||·|$)", txt, re.I)
    if m:
        seller = clean(m.group(2))

    return total, currency, order_no, seller

def parse_page_list_only(html: str, target_year: int):
    soup = BeautifulSoup(html, "lxml")
    results = []

    item_links = [a for a in soup.find_all("a", href=True) if "/itm/" in a["href"]]
    seen_titles = set()

    for a in item_links:
        title = clean(a.get_text(" "))
        if not title or len(title) < 4:
            continue
        if title in seen_titles:
            continue
        seen_titles.add(title)

        block_txt, block_node = nearest_text_block(a)

        years = {int(y) for y in re.findall(r"\b(20\d{2})\b", block_txt)}
        if years and (target_year not in years) and any(y != target_year for y in years):
            continue

        total, currency, order_no, seller = extract_meta_from_text(block_txt)

        if not (total and order_no and seller):
            parent = block_node.parent if getattr(block_node, "parent", None) else None
            if parent:
                sibling_txt = clean(BeautifulSoup(str(parent), "lxml").get_text(" "))
                t2, c2, n2, s2 = extract_meta_from_text(sibling_txt)
                total = total or t2
                currency = currency or c2
                order_no = order_no or n2
                seller = seller or s2

        results.append({
            "seller": seller,
            "item_title": title,
            "order_total": total,
            "currency": currency,
            "order_number": order_no
        })

    return results

# ------------------ Config handling ------------------
DEFAULTS = {
    "year": None,
    "site": "co.uk",
    "headless": False,
    "max_pages": 800,
    "sleep": 2.0,
    "jitter": [0.5, 1.2],
    "lang": "en-GB,en-US,cs-CZ"
}

def _load_yaml_text(text: str):
    try:
        import yaml
        return yaml.safe_load(text)
    except Exception:
        return None

def load_config():
    cfg = DEFAULTS.copy()
    cwd = Path.cwd()
    json_path = cwd / "config.json"
    yaml_path = cwd / "config.yaml"
    yml_path  = cwd / "config.yml"

    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update({k: data[k] for k in data if k in cfg})
        except Exception:
            pass

    for ypath in (yaml_path, yml_path):
        if ypath.exists():
            try:
                data = _load_yaml_text(ypath.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    cfg.update({k: data[k] for k in data if k in cfg})
            except Exception:
                pass

    # Environment overrides
    cfg["site"] = os.getenv("EBAY_SITE", cfg["site"])
    if os.getenv("EBAY_YEAR"):
        try:
            cfg["year"] = int(os.getenv("EBAY_YEAR"))
        except Exception:
            pass
    if os.getenv("HEADLESS", "").lower() in ("1", "true", "yes"):
        cfg["headless"] = True

    return cfg

def make_arg_parser(defaults):
    ap = argparse.ArgumentParser(description="eBay Purchase History → list-only export (public, config-driven).")
    ap.add_argument("--year", type=int, default=defaults.get("year"), help="Year to export (e.g. 2024)")
    ap.add_argument("--site", default=defaults.get("site","co.uk"), choices=["co.uk","com"], help="eBay domain")
    ap.add_argument("--sleep", type=float, default=defaults.get("sleep",2.0), help="Base pause between pages (s)")
    ap.add_argument("--jitter", type=float, nargs=2, default=defaults.get("jitter",[0.5,1.2]), help="Random jitter (s) min max")
    ap.add_argument("--max-pages", type=int, default=defaults.get("max_pages",800), help="Upper page limit")
    ap.add_argument("--headless", action="store_true", default=defaults.get("headless",False), help="Run without opening browser window")
    ap.add_argument("--lang", default=defaults.get("lang","en-GB,en-US,cs-CZ"), help="Accept-Language for Chrome")
    return ap

def main():
    defaults = load_config()
    ap = make_arg_parser(defaults)
    args = ap.parse_args()

    if not args.year:
        print("ERROR: --year is required (or set it in config.json / config.yaml / EBAY_YEAR).", file=sys.stderr)
        sys.exit(2)

    YEAR_KEY = f"A{args.year}"
    BASE_URL = (
        f"https://www.ebay.{args.site}/mye/myebay/purchase"
        f"?filter=year_filter%3A{YEAR_KEY}&page={{page}}&mp=purchase&purchase-module-v2&type=v2"
    )
    out_csv  = f"ebay_purchases_{args.year}.csv"
    out_html = f"ebay_purchases_{args.year}.html"
    debug_html = f"debug_purchase_page_{args.year}_p1.html"

    chrome_opts = webdriver.ChromeOptions()
    if args.headless: chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--start-maximized")
    chrome_opts.add_argument(f"--lang={args.lang}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_opts)

    rows = []
    try:
        driver.get(BASE_URL.format(page=1))
        print(f">>> Log in to eBay, open Purchase history and set **See orders: {args.year}** (page=1).")
        input("When the page is ready, press Enter… ")

        page = 1
        while page <= args.max_pages:
            url = BASE_URL.format(page=page)
            driver.get(url)
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            auto_scroll(driver, steps=10, pause=0.7)
            sleep_with_jitter(args.sleep, *args.jitter)

            if f"year_filter%3A{YEAR_KEY}" not in driver.current_url:
                print(f"Stopping: year filter not present in URL ({YEAR_KEY}) → {driver.current_url}")
                break

            html = driver.page_source
            if page == 1:
                try:
                    with open(debug_html, "w", encoding="utf-8") as f:
                        f.write(html)
                    print(f"(debug saved: {debug_html})")
                except Exception as e:
                    print(f"(debug dump failed: {e})")

            page_rows = parse_page_list_only(html, args.year)
            if not page_rows:
                break

            rows.extend(page_rows)
            page += 1

        df = pd.DataFrame(rows)
        required = ["seller","item_title","order_total","currency","order_number"]
        for col in required:
            if col not in df.columns:
                df[col] = ""

        df = df[(df["item_title"].astype(str).str.len()>0) | (df["order_total"].astype(str).str.len()>0)]

        def sym_from_total(v):
            m = MONEY_RE.search(str(v))
            return m.group(1) if m else ""
        df["currency"] = df["currency"].mask(
            df["currency"].astype(str).isin(("", "nan", "NaN")),
            df["order_total"].map(sym_from_total)
        )

        out = df[required].drop_duplicates()

        out.to_csv(out_csv, index=False, encoding="utf-8-sig")
        with open(out_html, "w", encoding="utf-8") as f:
            f.write("<!doctype html><meta charset='utf-8'><title>eBay Purchases</title>" +
                    out.to_html(index=False, escape=False))

        print(f"Done: {out_csv} ({len(out)} rows)")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
