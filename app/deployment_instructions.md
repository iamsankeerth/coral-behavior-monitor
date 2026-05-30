# Streamlit Dashboard Deployment Guide

You can deploy this dashboard for **free** in under 1 minute using **Streamlit Community Cloud** to meet the hackathon's "deployed link" requirement.

---

## 🚀 Step-by-Step Deployment

1. **Push Code to GitHub**:
   * Commit all code and processed CSV files in `data/coral/csv/` to your private or public GitHub repository.

2. **Sign In to Streamlit Cloud**:
   * Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.

3. **Deploy App**:
   * Click **New app**.
   * Select your GitHub repository (`Coral Project`).
   * Set Branch to `main`.
   * Set Main file path to `app/app.py`.
   * Click **Deploy!**

---

## 🔒 Private Sandbox / Anonymization

Since Health Connect and browsing history are highly sensitive:
* **Recommendation**: Push only the **anonymized / aggregated** daily metrics (`data/coral/csv/behavior_health_daily.csv`) to your public GitHub repo if the repo is public. 
* **Data Contract Ignored Raw**: The V8 original DB files (`stayfree_raw_dump.json`) and raw leveldb duplicates are in `.gitignore` and **will never be committed**! This ensures 100% compliance with privacy rules.
