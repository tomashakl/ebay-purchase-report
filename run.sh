#!/usr/bin/env bash
# eBay Purchase Report — public runner
# Reads config.json/config.yaml if present. CLI args override config.
set -euo pipefail
python3 ebay_purchases_list_only.py "$@"
