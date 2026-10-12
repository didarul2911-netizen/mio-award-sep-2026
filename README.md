# Exium MUPS & Coralcal-D/DX/Vita — September 2026 Award Calculation, Choice & Recommendation System

Standalone, production-grade **September 2026 Award Calculation Master Excel** & **Catalogue Choice + RH/ZH Recommendation Web Portal** for **Exium MUPS** and **Coralcal-D/DX/Vita**.

---

## 📂 Project Structure (`G:\Exium\2026\Award\September\`)

```
G:\Exium\2026\Award\September\
│
├── index.html                                         # Production Web Portal (Single-file, self-contained)
├── Award_Choice_Portal.html                           # Direct duplicate for backup/alternative hosting
│
├── Exium_Award_Choice_Master_Sep_2026.xlsx            # Master Award Calculation & Choice Workbook (6 Sheets)
├── Calculation\
│   ├── September_2026_Award_Calculation_Master.xlsx   # Master Award Calculation Workbook inside Calculation folder
│   ├── Award Criteria_Sep'26.png                      # Official September 2026 Award Criteria Circular
│   ├── Exium Award for September'26.xlsx              # Source: Exium Daily Seen Rx (1-Sep to 30-Sep)
│   ├── Coralcal Award for September'26.xlsx           # Source: Coralcal Daily Seen Rx (1-Sep to 30-Sep)
│   ├── Award Data, RPL.xlsx                           # Source: Aug'26 & Sep'26 Territory & Brand Sales
│   └── Value Growth Calculation - Team A.xlsx         # Source: Sep'26 Required Sales Value for Award (30-Box Growth)
│
├── FF list.xlsx                                       # Official Field Force Hierarchy (1,856 Territories)
├── september_award_data.json                          # Pre-computed JSON dataset of all 1,856 territories
├── generate_september_award_calculation_excel.py      # Precise Calculation Engine & Excel Generator
├── build_september_award_portal.py                    # Web Portal HTML Generator
├── sync_excel.py                                      # Local Excel Synchronization Script
├── Google_Apps_Script_Award_Backend.js                # Google Sheets 2-Way Cloud Sync Backend
└── README.md                                          # Documentation & Summary
```

---

## 🏆 September 2026 Award Criteria & National Calculation Summary

Evaluated across **1,856 Territories** (`35 Zones`, `252 Regions`) independently for **Exium MUPS** and **Coralcal-D/DX/Vita**:

### Criteria Rules
1. **1,000 Award (Rx Criteria):**
   - **No. of Seen Rx $\ge 200$** in the full month of September 2026 (`1-Sep` to `30-Sep`).
   - If `Seen Rx < 200`, the MIO receives **No Award (`0`)** for that brand.
2. **3,000 Award (Sales Value Growth Criteria — All 3 Must Be Met Serially):**
   - **(a)** `Seen Rx >= 200` in September 2026.
   - **(b)** `Total Territory Sales` in Sep'26 is **Positive** over Aug'26 (`Sep'26 Total Sales > Aug'26 Total Sales` in `Award Data, RPL.xlsx`).
   - **(c)** Brand Sales Value in Sep'26 $\ge$ `Sep'26 Sales Required for Award` (`Value Growth Calculation - Team A.xlsx`, representing 30-box value growth over Aug'26: `+19,790` for Exium and `+19,115` for Coralcal).
3. **Regional Head (RH) & Zonal Head (ZH) Recommendation / Cancellation:**
   - Regional Head and Zonal Head can **Cancel (Not Recommend)** any eligible award by writing a mandatory **Reason**.

### National Results Summary

| Metric | Exium MUPS | Coralcal-D/DX/Vita | Combined Total |
| :--- | :---: | :---: | :---: |
| **Total Territories Evaluated** | 1,856 | 1,856 | 1,856 |
| **Criterion 1 Met (`Seen Rx >= 200`)** | 1,753 | 1,649 | — |
| **Criterion 2(b) Met (`Total Territory Sales Positive`)** | 1,176 | 1,176 | — |
| **Criterion 2(c) Met (`Brand Value Growth Met`)** | 481 | 505 | — |
| **3,000 Award Achievers (All 3 Criteria Met)** | **455** (`1,365,000`) | **465** (`1,395,000`) | **920 Awards** (`2,760,000`) |
| **1,000 Award Achievers (`Rx >= 200` Only)** | **1,298** (`1,298,000`) | **1,184** (`1,184,000`) | **2,482 Awards** (`2,482,000`) |
| **Total Eligible Brand Achievers** | **1,753** (`2,663,000`) | **1,649** (`2,579,000`) | **3,402 Awards** (**`5,242,000`**) |
| **No Award (`Seen Rx < 200`)** | 103 | 207 | 88 MIOs in neither |
