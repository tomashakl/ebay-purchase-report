@echo off
REM eBay Purchase Report — public runner
REM Reads config.json/config.yaml if present. CLI args override config.

python ebay_purchases_list_only.py %*
