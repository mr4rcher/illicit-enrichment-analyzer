# Illicit Enrichment Analyzer

Source and Application of Funds analysis tool for forensic accounting investigations.

## What It Does
Implements the [UNODC Source and Application methodology](https://www.unodc.org) to detect unexplained wealth by comparing documented income against expenditures and asset accumulation.

## Demo Output
![Analysis Dashboard](screenshot.png)

## Tech Stack
- Python 3.14
- Flet (Flutter UI)
- Pandas/Decimal for financial precision

## Quick Start
```bash
python -m venv venv
source venv/bin/activate  # .fish for fish shell
pip install flet
python gui_flet.py