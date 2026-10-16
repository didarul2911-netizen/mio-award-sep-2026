import json
import base64
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE_DIR = Path(r"G:\Exium\2026\Award\September")
MAY_JUN_DIR = Path(r"G:\Exium\2026\Award\May-Jun")
DATA_JSON = BASE_DIR / "september_award_data.json"
OUT_INDEX = BASE_DIR / "index.html"
OUT_PORTAL = BASE_DIR / "Award_Choice_Portal.html"

EXIUM_TP = 659.67
CORALCAL_TP = 637.18
REQ_GROWTH_BOX = 30


def round_half_up(val) -> int:
    if val is None:
        return 0
    return int(Decimal(str(val)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def encode_image_b64(img_path: Path) -> str:
    if not img_path.exists():
        for ext in [".png", ".jpg", ".jpeg", ".webp", ".avif"]:
            alt = img_path.with_suffix(ext)
            if alt.exists():
                img_path = alt
                break
    if not img_path.exists():
        return ""
    ext = img_path.suffix.lower().replace(".", "")
    mime = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
    b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def build_portal():
    print("Loading September 2026 calculated award data...")
    raw_records = json.loads(DATA_JSON.read_text(encoding="utf-8"))

    # Note: User explicitly requested NO Exium MUPS logo ("Exium MUPS er Logo hobe na")
    logo_dir = BASE_DIR / "Brand Logo"
    logos = {
        "infinity": encode_image_b64(logo_dir / "Infinity Logo.png"),
        "apex": encode_image_b64(logo_dir / "Apex Logo.png"),
        "bata": encode_image_b64(logo_dir / "Bata logo.jpg"),
        "aarong": encode_image_b64(logo_dir / "Aarong Logo.png"),
        "bestbuy": encode_image_b64(logo_dir / "Best Buy Logo.png"),
        "catseye": encode_image_b64(logo_dir / "Cats Eye Logo.jpeg"),
    }
    for k, v in logos.items():
        assert len(v) > 100, f"Logo {k} failed to load!"

    records = []
    achievers_exium = []
    achievers_coral = []
    zones_dict = {}
    regions_map = {}

    for r in raw_records:
        ex_aug = float(r.get("ex_aug") or 0.0)
        ex_req = float(r.get("ex_req") or 0.0)
        ex_sep = float(r.get("ex_sep") or 0.0)
        ex_req_growth = round(ex_req - ex_aug, 2) if r.get("ex_req") is not None else 0.0
        ex_actual_growth = round(ex_sep - ex_aug, 2)
        ex_req_box = REQ_GROWTH_BOX if r.get("ex_req") is not None else 0
        ex_aug_box = round_half_up(ex_aug / EXIUM_TP) if r.get("ex_aug") is not None else 0
        ex_growth_box = round_half_up((ex_sep - ex_aug) / EXIUM_TP) if r.get("ex_aug") is not None else 0
        ex_sep_box = (ex_aug_box + ex_growth_box) if r.get("ex_aug") is not None else round_half_up(ex_sep / EXIUM_TP)

        cc_aug = float(r.get("cc_aug") or 0.0)
        cc_req = float(r.get("cc_req") or 0.0)
        cc_sep = float(r.get("cc_sep") or 0.0)
        cc_req_growth = round(cc_req - cc_aug, 2) if r.get("cc_req") is not None else 0.0
        cc_actual_growth = round(cc_sep - cc_aug, 2)
        cc_req_box = REQ_GROWTH_BOX if r.get("cc_req") is not None else 0
        cc_aug_box = round_half_up(cc_aug / CORALCAL_TP) if r.get("cc_aug") is not None else 0
        cc_growth_box = round_half_up((cc_sep - cc_aug) / CORALCAL_TP) if r.get("cc_aug") is not None else 0
        cc_sep_box = (cc_aug_box + cc_growth_box) if r.get("cc_aug") is not None else round_half_up(cc_sep / CORALCAL_TP)

        norm = {
            "zone_name": str(r.get("zone_name") or ""),
            "sap_zone_code": str(r.get("sap_zone_code") or ""),
            "zonal_head": str(r.get("zm_name") or ""),
            "region_name": str(r.get("region_name") or ""),
            "sap_region_code": str(r.get("sap_region_code") or ""),
            "regional_head": str(r.get("rm_name") or ""),
            "area_code": str(r.get("tty") or ""),
            "area_name": str(r.get("area_name") or ""),
            "mio_id": str(r.get("mio_code") or ""),
            "mio_name": str(r.get("mio_name") or ""),
            "desig": str(r.get("designation") or ""),
            "mobile": str(r.get("mobile") or ""),
            "terr_aug_val": float(r.get("aug_total") or 0.0),
            "terr_sep_val": float(r.get("sep_total") or 0.0),
            "terr_growth_val": float(r.get("tot_growth_val") or 0.0),
            "terr_pos": bool(r.get("tot_sales_positive")),
            "exium_rx": int(r.get("ex_rx") or 0),
            "exium_rx_ok": bool(r.get("ex_c1_rx")),
            "exium_aug_val": ex_aug,
            "exium_req_growth": ex_req_growth,
            "exium_req_target": ex_req,
            "exium_sep_val": ex_sep,
            "exium_actual_growth": ex_actual_growth,
            "exium_aug_box": ex_aug_box,
            "exium_sep_box": ex_sep_box,
            "exium_req_box": ex_req_box,
            "exium_growth_box": ex_growth_box,
            "exium_growth_ok": bool(r.get("ex_growth_met")),
            "exium_award": int(r.get("ex_award") or 0),
            "exium_tier": r.get("ex_tier") or "",
            "exium_reason": r.get("ex_tier") or "",
            "coral_rx": int(r.get("cc_rx") or 0),
            "coral_rx_ok": bool(r.get("cc_c1_rx")),
            "coral_aug_val": cc_aug,
            "coral_req_growth": cc_req_growth,
            "coral_req_target": cc_req,
            "coral_sep_val": cc_sep,
            "coral_actual_growth": cc_actual_growth,
            "coral_aug_box": cc_aug_box,
            "coral_sep_box": cc_sep_box,
            "coral_req_box": cc_req_box,
            "coral_growth_box": cc_growth_box,
            "coral_growth_ok": bool(r.get("cc_growth_met")),
            "coral_award": int(r.get("cc_award") or 0),
            "coral_tier": r.get("cc_tier") or "",
            "coral_reason": r.get("cc_tier") or "",
        }
        records.append(norm)

        z_code = norm["sap_zone_code"]
        if z_code not in zones_dict:
            zones_dict[z_code] = {
                "zone_name": norm["zone_name"],
                "sap_zone_code": z_code,
                "zonal_head": norm["zonal_head"],
                "regions_dict": {}
            }

        reg_name = norm["region_name"]
        if reg_name not in regions_map:
            regions_map[reg_name] = {
                "region_name": reg_name,
                "sap_region_code": norm["sap_region_code"],
                "regional_head": norm["regional_head"],
                "zone_name": norm["zone_name"],
                "sap_zone_code": z_code,
                "zonal_head": norm["zonal_head"],
                "exium_count": 0,
                "exium_value": 0,
                "coral_count": 0,
                "coral_value": 0,
            }
        zones_dict[z_code]["regions_dict"][reg_name] = regions_map[reg_name]

        if norm["exium_award"] > 0:
            regions_map[reg_name]["exium_count"] += 1
            regions_map[reg_name]["exium_value"] += norm["exium_award"]
            achievers_exium.append({
                "id": f"EXIUM_{norm['area_code']}_{norm['mio_id']}",
                "brand": "Exium_2026",
                "brand_short": "Exium MUPS",
                "brand_label": "Exium MUPS",
                "brand_tp": EXIUM_TP,
                "zone": norm["zone_name"],
                "sap_zone_code": norm["sap_zone_code"],
                "zonal_head": norm["zonal_head"],
                "region": norm["region_name"],
                "sap_region_code": norm["sap_region_code"],
                "regional_head": norm["regional_head"],
                "area_code": norm["area_code"],
                "area_name": norm["area_name"],
                "mio_code": norm["mio_id"],
                "mio_name": norm["mio_name"],
                "desig": norm["desig"],
                "mobile": norm["mobile"],
                "rx": norm["exium_rx"],
                "rx_ok": norm["exium_rx_ok"],
                "terr_aug": norm["terr_aug_val"],
                "terr_sep": norm["terr_sep_val"],
                "terr_growth": norm["terr_growth_val"],
                "terr_pos": norm["terr_pos"],
                "brand_aug": norm["exium_aug_val"],
                "brand_req_growth": norm["exium_req_growth"],
                "brand_req_target": norm["exium_req_target"],
                "brand_sep": norm["exium_sep_val"],
                "brand_actual_growth": norm["exium_actual_growth"],
                "brand_aug_box": norm["exium_aug_box"],
                "brand_sep_box": norm["exium_sep_box"],
                "brand_req_box": norm["exium_req_box"],
                "brand_growth_box": norm["exium_growth_box"],
                "brand_growth_ok": norm["exium_growth_ok"],
                "award": norm["exium_award"],
                "tier": norm["exium_tier"],
                "reason": norm["exium_reason"],
            })

        if norm["coral_award"] > 0:
            regions_map[reg_name]["coral_count"] += 1
            regions_map[reg_name]["coral_value"] += norm["coral_award"]
            achievers_coral.append({
                "id": f"CORAL_{norm['area_code']}_{norm['mio_id']}",
                "brand": "Coralcal_2026",
                "brand_short": "Coralcal-D/DX/Vita",
                "brand_label": "Coralcal-D/DX/Vita",
                "brand_tp": CORALCAL_TP,
                "zone": norm["zone_name"],
                "sap_zone_code": norm["sap_zone_code"],
                "zonal_head": norm["zonal_head"],
                "region": norm["region_name"],
                "sap_region_code": norm["sap_region_code"],
                "regional_head": norm["regional_head"],
                "area_code": norm["area_code"],
                "area_name": norm["area_name"],
                "mio_code": norm["mio_id"],
                "mio_name": norm["mio_name"],
                "desig": norm["desig"],
                "mobile": norm["mobile"],
                "rx": norm["coral_rx"],
                "rx_ok": norm["coral_rx_ok"],
                "terr_aug": norm["terr_aug_val"],
                "terr_sep": norm["terr_sep_val"],
                "terr_growth": norm["terr_growth_val"],
                "terr_pos": norm["terr_pos"],
                "brand_aug": norm["coral_aug_val"],
                "brand_req_growth": norm["coral_req_growth"],
                "brand_req_target": norm["coral_req_target"],
                "brand_sep": norm["coral_sep_val"],
                "brand_actual_growth": norm["coral_actual_growth"],
                "brand_aug_box": norm["coral_aug_box"],
                "brand_sep_box": norm["coral_sep_box"],
                "brand_req_box": norm["coral_req_box"],
                "brand_growth_box": norm["coral_growth_box"],
                "brand_growth_ok": norm["coral_growth_ok"],
                "award": norm["coral_award"],
                "tier": norm["coral_tier"],
                "reason": norm["coral_reason"],
            })

    zones_list = []
    for z in sorted(zones_dict.values(), key=lambda x: x["zone_name"]):
        zones_list.append({
            "zone_name": z["zone_name"],
            "sap_zone_code": z["sap_zone_code"],
            "zonal_head": z["zonal_head"],
            "regions": sorted(z["regions_dict"].values(), key=lambda r: r["region_name"])
        })

    gs_path = BASE_DIR / "Google_Apps_Script_Award_Backend.js"
    gs_code_str = gs_path.read_text(encoding="utf-8") if gs_path.exists() else ""

    db_payload = {
        "zones": zones_list,
        "regions_map": regions_map,
        "achievers_exium": achievers_exium,
        "achievers_coral": achievers_coral,
        "all_territories": records,
        "logos": logos,
        "apps_script_code": gs_code_str,
    }

    json_db_str = json.dumps(db_payload, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Award for Sr. / MIO - Voucher Selection Portal (September 2026)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        html, body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #f1f5f9;
            color: #0f172a;
            overflow-x: hidden;
            max-width: 100vw;
        }}
        .brand-card {{
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .brand-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.08);
        }}
        .brand-card.selected {{
            border-color: #059669;
            background-color: #ecfdf5;
            box-shadow: 0 0 0 2px #059669;
        }}
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: #f1f5f9;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #cbd5e1;
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #94a3b8;
        }}
    </style>
</head>
<body class="min-h-screen flex flex-col bg-slate-100 overflow-x-hidden">

    <!-- Top Header Bar (Mobile-First: Single-Line Heading on Top, Options Row Below on Mobile) -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs w-full">
        <div class="max-w-7xl mx-auto px-2.5 sm:px-6 lg:px-8 py-2 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <!-- Row 1: Icon + Single-Line Heading + Brand Badges -->
            <div class="flex items-center gap-2 min-w-0 w-full sm:w-auto">
                <div class="w-8 h-8 sm:w-9 sm:h-9 bg-orange-50 text-orange-600 rounded-xl flex items-center justify-center shadow-inner border border-orange-200 flex-shrink-0">
                    <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
                    </svg>
                </div>
                <div class="min-w-0 flex-1">
                    <span class="text-[13px] sm:text-base font-extrabold text-slate-900 tracking-tight block leading-tight whitespace-nowrap truncate">
                        Award for Sr. / MIO — September 2026
                    </span>
                    <div class="flex items-center gap-1.5 mt-0.5 flex-wrap">
                        <span class="px-1.5 py-0.2 rounded text-[10px] font-extrabold bg-blue-600 text-white whitespace-nowrap">
                            Exium MUPS Award
                        </span>
                        <span class="px-1.5 py-0.2 rounded text-[10px] font-extrabold bg-purple-700 text-white whitespace-nowrap">
                            Coralcal-D/DX/Vita Award
                        </span>
                    </div>
                </div>
            </div>

            <!-- Row 2 on Mobile (Right Side on Desktop): Action Options -->
            <div class="grid grid-cols-4 sm:flex items-center gap-1.5 sm:gap-2 w-full sm:w-auto pt-1.5 sm:pt-0 border-t border-slate-100 sm:border-t-0">
                <!-- Live Cloud Sync Status Indicator -->
                <button id="header-sync-btn" onclick="onHeaderCloudSyncClick()" title="Click to Sync Now" class="flex items-center justify-center space-x-1 px-2 sm:px-2.5 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-[11px] font-bold text-slate-700 transition cursor-pointer whitespace-nowrap">
                    <span id="header-sync-dot" class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse flex-shrink-0"></span>
                    <span id="header-sync-status" class="truncate">Ready</span>
                    <svg id="sync-icon-desktop" class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-slate-500 flex-shrink-0 hidden sm:inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                </button>

                <!-- Award Criteria Button -->
                <button onclick="openAwardCriteriaModal('exium')" class="bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 px-2 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-bold transition flex items-center justify-center space-x-1 shadow-2xs whitespace-nowrap">
                    <span>📋</span>
                    <span class="sm:hidden">Criteria</span>
                    <span class="hidden sm:inline">Award Criteria</span>
                </button>

                <!-- Zonal Head Portal Button -->
                <button onclick="openZonalModal()" class="bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-700 px-2 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-bold transition flex items-center justify-center space-x-1 whitespace-nowrap">
                    <span>🌐</span>
                    <span>Zonal View</span>
                </button>

                <!-- Admin Button -->
                <button onclick="openAdminModal()" class="bg-orange-50 hover:bg-orange-100 border border-orange-200 text-orange-700 px-2 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-bold transition flex items-center justify-center space-x-1 whitespace-nowrap">
                    <span>🛡️</span>
                    <span>Admin</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-2.5 sm:px-6 lg:px-8 py-3 sm:py-5 overflow-x-hidden">

        <!-- ============================================== -->
        <!-- VIEW 1: LOGIN & ROLE SELECTION SCREEN          -->
        <!-- ============================================== -->
        <section id="login-view" class="max-w-lg w-full mx-auto my-2 sm:my-8">
            <div class="bg-white rounded-3xl shadow-xl border border-slate-200 overflow-hidden">
                
                <!-- Card Top Banner -->
                <div class="bg-gradient-to-r from-slate-50 via-white to-slate-50 p-4 sm:p-7 border-b border-slate-200 text-center">
                    <div class="w-11 h-11 sm:w-13 sm:h-13 bg-orange-50 text-orange-600 rounded-2xl mx-auto flex items-center justify-center mb-2 shadow-inner border border-orange-200">
                        <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
                        </svg>
                    </div>
                    <h1 class="text-base sm:text-2xl font-extrabold text-slate-900 tracking-tight whitespace-nowrap truncate">
                        Sr. / MIO Award Choice Portal
                    </h1>
                    <p class="text-[11px] sm:text-sm font-medium text-slate-500 mt-1">
                        Select Gift Vouchers for Eligible Medical Information Officers
                    </p>
                    <div class="flex items-center justify-center gap-1.5 sm:gap-2 mt-2.5 flex-wrap">
                        <span class="px-2 sm:px-2.5 py-0.5 rounded-md text-[11px] sm:text-xs font-extrabold bg-blue-600 text-white shadow-2xs whitespace-nowrap">
                            🟦 Exium MUPS Award
                        </span>
                        <span class="px-2 sm:px-2.5 py-0.5 rounded-md text-[11px] sm:text-xs font-extrabold bg-purple-700 text-white shadow-2xs whitespace-nowrap">
                            🟪 Coralcal-D/DX/Vita Award
                        </span>
                    </div>
                </div>

                <!-- Navigation Tabs: Regional Login | MIO Quick Search -->
                <div class="flex border-b border-slate-200 bg-slate-50 text-xs font-bold">
                    <button id="tab-reg" onclick="switchLoginTab('regional')" class="flex-1 py-3 text-center border-b-2 border-orange-500 text-orange-600 bg-white font-black">
                        Regional Head Login
                    </button>
                    <button id="tab-mio" onclick="switchLoginTab('mio')" class="flex-1 py-3 text-center border-b-2 border-transparent text-slate-500 hover:text-slate-800">
                        MIO Quick Check
                    </button>
                </div>

                <!-- Tab 1: Regional Head Form -->
                <form id="form-regional" autocomplete="off" onsubmit="handleRegionalLogin(event)" class="p-4 sm:p-7 space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                            1. Select Zone
                        </label>
                        <select id="reg-zone-select" onchange="onRegionalZoneChange()" class="w-full max-w-full truncate bg-slate-50 border border-slate-300 rounded-xl px-3 sm:px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none cursor-pointer">
                            <option value="">-- Choose Zone --</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                            2. Select Region
                        </label>
                        <select id="reg-region-select" onchange="onRegionalRegionChange()" disabled class="w-full max-w-full truncate bg-slate-100 border border-slate-300 rounded-xl px-3 sm:px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none cursor-pointer">
                            <option value="">-- Select Zone First --</option>
                        </select>
                    </div>

                    <!-- Auto-populated Region Details Box -->
                    <div id="reg-details-box" class="hidden bg-orange-50/70 border border-orange-200 rounded-2xl p-3 sm:p-3.5 text-xs space-y-2">
                        <div class="flex justify-between items-center gap-2 flex-wrap">
                            <span class="text-slate-500 font-semibold">Regional Head:</span>
                            <span id="disp-reg-head" class="font-bold text-slate-900">-</span>
                        </div>
                        <div class="flex justify-between items-center gap-2 flex-wrap border-t border-orange-200/60 pt-1.5">
                            <span class="text-blue-700 font-bold">🟦 Exium MUPS Achievers:</span>
                            <span id="disp-reg-exium" class="font-black text-blue-800 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">-</span>
                        </div>
                        <div class="flex justify-between items-center gap-2 flex-wrap">
                            <span class="text-purple-700 font-bold">🟪 Coralcal-D/DX/Vita Achievers:</span>
                            <span id="disp-reg-coral" class="font-black text-purple-800 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">-</span>
                        </div>
                    </div>

                    <div>
                        <div class="flex justify-between items-center mb-1.5">
                            <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                                3. Region Password
                            </label>
                            <span class="text-[11px] text-orange-600 font-extrabold bg-orange-50 px-2 py-0.5 rounded border border-orange-200">
                                SAP Region Code
                            </span>
                        </div>
                        <input type="password" id="reg-password-input" autocomplete="new-password" placeholder="Enter SAP Region Code" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none">
                    </div>

                    <button type="submit" class="w-full py-3 px-5 rounded-xl font-extrabold text-sm text-white bg-slate-900 hover:bg-slate-800 shadow-md hover:shadow-lg transition transform active:scale-[0.99] flex items-center justify-center space-x-2">
                        <span>Access Regional Portal</span>
                        <svg class="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                    </button>
                </form>

                <!-- Tab 2: MIO Quick Check Form -->
                <div id="form-mio-search" class="hidden p-4 sm:p-7 space-y-4">
                    <div class="bg-blue-50 border border-blue-200 rounded-2xl p-3.5 text-xs text-blue-900">
                        Enter your <strong>SAP MIO Code</strong>, <strong>Territory Code</strong>, or <strong>Name</strong> to check your <strong>Exium MUPS Award</strong> and <strong>Coralcal-D/DX/Vita Award</strong> status & selected gift vouchers.
                    </div>
                    <div class="flex gap-2">
                        <input type="text" id="mio-quick-query" onkeydown="if(event.key==='Enter') searchMioDirect(event)" placeholder="e.g. 52126 or DHK11 or Name..." class="flex-1 min-w-0 bg-slate-50 border border-slate-300 rounded-xl px-3 sm:px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-orange-500 outline-none">
                        <button type="button" onclick="searchMioDirect(event)" class="px-4 sm:px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs sm:text-sm transition flex-shrink-0">
                            Search
                        </button>
                    </div>
                    <div id="mio-search-results-box" class="space-y-3 max-h-96 overflow-y-auto pt-1"></div>
                </div>

            </div>
        </section>

        <!-- ============================================== -->
        <!-- VIEW 2: REGIONAL HEAD SELECTION PORTAL         -->
        <!-- ============================================== -->
        <section id="regional-view" class="hidden space-y-3.5 sm:space-y-4 pb-28 sm:pb-24">

            <!-- Region Info & Progress Card -->
            <div class="bg-white rounded-2xl p-3.5 sm:p-5 shadow-xs border border-slate-200">
                <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3 pb-3.5 border-b border-slate-100">
                    <div class="min-w-0">
                        <div class="flex flex-wrap items-center gap-1.5 mb-1">
                            <span id="regview-zone" class="px-2.5 py-0.5 rounded-full text-[11px] font-extrabold bg-orange-100 text-orange-800 border border-orange-200 uppercase tracking-wider">Zone</span>
                            <span id="regview-sap" class="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">SAP: -</span>
                        </div>
                        <h2 id="regview-name" class="text-base sm:text-xl font-black text-slate-900 tracking-tight truncate">Region Name</h2>
                        <div class="flex flex-wrap items-center gap-x-2.5 gap-y-0.5 text-xs text-slate-600 mt-0.5">
                            <span id="regview-rh">Regional Head: <strong class="text-slate-900 font-bold">-</strong></span>
                            <span class="text-slate-300 hidden sm:inline">•</span>
                            <span id="regview-zh">Zonal Head: <strong class="text-orange-700 font-bold">-</strong></span>
                        </div>
                    </div>

                    <!-- Separate Brand Progress + Overall Progress (Mobile Grid -> Desktop Flex) -->
                    <div class="grid grid-cols-2 sm:flex sm:flex-wrap items-stretch sm:items-center gap-2 w-full lg:w-auto">
                        <div class="bg-blue-600 text-white rounded-xl px-2.5 sm:px-3 py-2 border border-blue-500 sm:min-w-[140px] shadow-2xs">
                            <div class="text-[10px] font-extrabold uppercase tracking-wide text-blue-100 truncate">🟦 Exium MUPS Award</div>
                            <div id="regview-exium-stat" class="text-xs sm:text-sm font-black text-white mt-0.5">0 / 0 Done</div>
                        </div>
                        <div class="bg-purple-700 text-white rounded-xl px-2.5 sm:px-3 py-2 border border-purple-600 sm:min-w-[150px] shadow-2xs">
                            <div class="text-[10px] font-extrabold uppercase tracking-wide text-purple-100 truncate">🟪 Coralcal-D/DX/Vita</div>
                            <div id="regview-coral-stat" class="text-xs sm:text-sm font-black text-white mt-0.5">0 / 0 Done</div>
                        </div>
                        <div class="col-span-2 sm:col-span-1 bg-slate-50 rounded-xl px-3 py-2 border border-slate-200 sm:min-w-[190px]">
                            <div class="flex justify-between items-center text-[11px] mb-1">
                                <span class="font-bold text-slate-600">Overall Progress</span>
                                <span id="regview-progress-pct" class="font-black text-emerald-600">0%</span>
                            </div>
                            <div class="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                                <div id="regview-progress-bar" class="bg-emerald-500 h-1.5 rounded-full transition-all duration-300" style="width: 0%"></div>
                            </div>
                            <div class="flex justify-between items-center text-[10px] font-semibold text-slate-500 mt-1">
                                <span id="regview-progress-count" class="truncate">0 of 0 Completed</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Separate Brand Filter Tabs + Search + Separate Brand Excel Exports -->
                <div class="pt-3 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-2.5">
                    <!-- Brand Filter Buttons (Separate Exium MUPS / Coralcal View in Region) -->
                    <div class="flex flex-col sm:flex-row items-start sm:items-center gap-2 w-full md:w-auto">
                        <div class="flex items-center gap-1.5 flex-wrap">
                            <button type="button" id="reg-brand-tab-all" onclick="setRegionalBrandFilter('all')" class="px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-extrabold bg-slate-900 text-white shadow-2xs transition">
                                All Brands
                            </button>
                            <button type="button" id="reg-brand-tab-exium" onclick="setRegionalBrandFilter('exium')" class="px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-extrabold bg-blue-50 text-blue-800 hover:bg-blue-100 border border-blue-200 transition">
                                🟦 Exium MUPS Award
                            </button>
                            <button type="button" id="reg-brand-tab-coral" onclick="setRegionalBrandFilter('coral')" class="px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-extrabold bg-purple-50 text-purple-800 hover:bg-purple-100 border border-purple-200 transition">
                                🟪 Coralcal-D/DX/Vita Award
                            </button>
                        </div>
                    </div>

                    <!-- Search & Separate Brand Exports -->
                    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 flex-1 max-w-2xl justify-end w-full">
                        <div class="relative flex-1 min-w-0">
                            <svg class="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                            <input type="text" id="reg-mio-filter-input" oninput="renderAchievers()" placeholder="Filter by MIO Name, SAP ID, or Territory Code..." class="w-full pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:ring-2 focus:ring-orange-500 outline-none">
                        </div>
                        <div class="grid grid-cols-2 sm:flex items-center gap-1.5">
                            <button onclick="exportBrandExcel('region', 'exium')" class="px-2.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-[11px] font-bold transition shadow-2xs flex items-center justify-center gap-1 whitespace-nowrap" title="Download Only Exium MUPS Data for this Region">
                                <span>📥 Exium MUPS (.xlsx)</span>
                            </button>
                            <button onclick="exportBrandExcel('region', 'coral')" class="px-2.5 py-1.5 bg-purple-700 hover:bg-purple-800 text-white rounded-xl text-[11px] font-bold transition shadow-2xs flex items-center justify-center gap-1 whitespace-nowrap" title="Download Only Coralcal-D/DX/Vita Data for this Region">
                                <span>📥 Coralcal (.xlsx)</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Status Filter Pills Row (All MIOs / Achievers / Non-Achievers / In Review) -->
                <div class="pt-2.5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
                    <div class="flex items-center gap-1.5 flex-wrap" id="reg-status-pills">
                        <button type="button" id="reg-status-pill-all" onclick="setRegionalStatusFilter('all')" class="px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-black bg-slate-900 text-white shadow-2xs transition">
                            All MIOs (<span id="reg-count-all">0</span>)
                        </button>
                        <button type="button" id="reg-status-pill-achievers" onclick="setRegionalStatusFilter('achievers')" class="px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-bold bg-white text-emerald-800 hover:bg-emerald-50 border border-emerald-300 transition">
                            🏆 Achievers (<span id="reg-count-achievers">0</span>)
                        </button>
                        <button type="button" id="reg-status-pill-non_achievers" onclick="setRegionalStatusFilter('non_achievers')" class="px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-bold bg-white text-slate-700 hover:bg-slate-100 border border-slate-300 transition">
                            ⚪ Non-Achievers (<span id="reg-count-nonachievers">0</span>)
                        </button>
                        <button type="button" id="reg-status-pill-in_review" onclick="setRegionalStatusFilter('in_review')" class="px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-bold bg-white text-amber-800 hover:bg-amber-50 border border-amber-300 transition">
                            🔍 In Review (<span id="reg-count-inreview">0</span>)
                        </button>
                    </div>
                    <div class="text-[11px] text-slate-500 font-medium">
                        Showing all MIO territories in region. Non-achievers can submit review requests.
                    </div>
                </div>
            </div>

            <!-- Read-Only Locked Banner (Shown when Admin turns OFF Regional Head Input) -->
            <div id="regview-locked-banner" class="hidden bg-rose-50 border border-rose-300 rounded-2xl p-3.5 text-xs text-rose-950 flex items-center justify-between gap-3 shadow-2xs">
                <div class="flex items-center space-x-2.5">
                    <div class="w-8 h-8 rounded-xl bg-rose-600 text-white flex items-center justify-center text-sm flex-shrink-0 shadow-2xs">
                        🔒
                    </div>
                    <div>
                        <div class="font-black text-rose-900 text-xs sm:text-sm uppercase tracking-wide">Voucher Selection Currently Closed (Read-Only Mode)</div>
                        <div class="text-[11px] text-rose-800 mt-0.5">The Administrator has locked voucher submissions. You can view and export selections, but changes are disabled.</div>
                    </div>
                </div>
                <span class="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase bg-rose-200 text-rose-900 border border-rose-300 flex-shrink-0">Locked</span>
            </div>

            <!-- Achievers List Container -->
            <div id="regview-achievers-container" class="space-y-3.5"></div>

        </section>

        <!-- ============================================== -->
        <!-- VIEW 3: ZONAL HEAD DASHBOARD VIEW              -->
        <!-- ============================================== -->
        <section id="zonal-view" class="hidden space-y-5">

            <div class="bg-white rounded-2xl p-4 sm:p-5 shadow-sm border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-orange-500 text-white text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full">Zonal Dashboard</span>
                        <span id="zoneview-sap" class="bg-slate-100 text-slate-700 text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full border border-slate-200">SAP Zone: -</span>
                    </div>
                    <h2 id="zoneview-name" class="text-xl sm:text-2xl font-black text-slate-900">Zone Name</h2>
                    <p id="zoneview-zh" class="text-xs text-slate-500">Zonal Head: -</p>
                </div>
                <div class="flex flex-wrap items-center gap-2">
                    <button onclick="exportBrandExcel('zone', 'exium')" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center gap-1 shadow-sm transition">
                        <span>📥 Exium MUPS Zone (.xlsx)</span>
                    </button>
                    <button onclick="exportBrandExcel('zone', 'coral')" class="px-3 py-1.5 bg-purple-700 hover:bg-purple-800 text-white rounded-xl text-xs font-bold flex items-center gap-1 shadow-sm transition">
                        <span>📥 Coralcal Zone (.xlsx)</span>
                    </button>
                    <button onclick="exportBrandExcel('zone', 'both')" class="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold flex items-center gap-1 shadow-sm transition">
                        <span>📥 Both (.xlsx)</span>
                    </button>
                    <button onclick="exitToLogin()" class="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded-xl text-xs font-bold text-slate-700 transition">
                        Back to Login
                    </button>
                </div>
            </div>

            <!-- Separate Exium MUPS & Coralcal Zonal Summary Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                <!-- Exium MUPS Zonal Card -->
                <div class="bg-white border-2 border-blue-200 rounded-2xl p-4 shadow-sm space-y-2.5">
                    <div class="flex items-center justify-between border-b border-blue-100 pb-2">
                        <span class="px-2.5 py-1 rounded-lg text-xs font-black bg-blue-600 text-white">🟦 Exium MUPS Award</span>
                        <span id="zone-exium-val" class="text-xs font-black text-blue-900 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-200">Value: 0</span>
                    </div>
                    <div class="grid grid-cols-4 gap-2 text-center">
                        <div class="bg-slate-50 rounded-xl p-2 border border-slate-200">
                            <div class="text-[10px] font-bold text-slate-500 uppercase">Achievers</div>
                            <div id="zone-exium-total" class="text-lg font-black text-slate-900">0</div>
                        </div>
                        <div class="bg-emerald-50 rounded-xl p-2 border border-emerald-200">
                            <div class="text-[10px] font-bold text-emerald-700 uppercase">Done</div>
                            <div id="zone-exium-done" class="text-lg font-black text-emerald-800">0</div>
                        </div>
                        <div class="bg-amber-50 rounded-xl p-2 border border-amber-200">
                            <div class="text-[10px] font-bold text-amber-700 uppercase">Pending</div>
                            <div id="zone-exium-pend" class="text-lg font-black text-amber-800">0</div>
                        </div>
                        <div class="bg-rose-50 rounded-xl p-2 border border-rose-200">
                            <div class="text-[10px] font-bold text-rose-700 uppercase">Cancelled</div>
                            <div id="zone-exium-canc" class="text-lg font-black text-rose-800">0</div>
                        </div>
                    </div>
                </div>

                <!-- Coralcal Zonal Card -->
                <div class="bg-white border-2 border-purple-200 rounded-2xl p-4 shadow-sm space-y-2.5">
                    <div class="flex items-center justify-between border-b border-purple-100 pb-2">
                        <span class="px-2.5 py-1 rounded-lg text-xs font-black bg-purple-700 text-white">🟪 Coralcal-D/DX/Vita Award</span>
                        <span id="zone-coral-val" class="text-xs font-black text-purple-900 bg-purple-50 px-2.5 py-1 rounded-lg border border-purple-200">Value: 0</span>
                    </div>
                    <div class="grid grid-cols-4 gap-2 text-center">
                        <div class="bg-slate-50 rounded-xl p-2 border border-slate-200">
                            <div class="text-[10px] font-bold text-slate-500 uppercase">Achievers</div>
                            <div id="zone-coral-total" class="text-lg font-black text-slate-900">0</div>
                        </div>
                        <div class="bg-emerald-50 rounded-xl p-2 border border-emerald-200">
                            <div class="text-[10px] font-bold text-emerald-700 uppercase">Done</div>
                            <div id="zone-coral-done" class="text-lg font-black text-emerald-800">0</div>
                        </div>
                        <div class="bg-amber-50 rounded-xl p-2 border border-amber-200">
                            <div class="text-[10px] font-bold text-amber-700 uppercase">Pending</div>
                            <div id="zone-coral-pend" class="text-lg font-black text-amber-800">0</div>
                        </div>
                        <div class="bg-rose-50 rounded-xl p-2 border border-rose-200">
                            <div class="text-[10px] font-bold text-rose-700 uppercase">Cancelled</div>
                            <div id="zone-coral-canc" class="text-lg font-black text-rose-800">0</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Regions Breakdown Table -->
            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div class="p-3.5 bg-slate-50 border-b border-slate-200 flex justify-between items-center flex-wrap gap-1">
                    <h3 class="font-black text-xs uppercase tracking-wider text-slate-800">Regions in this Zone (Separate Exium MUPS & Coralcal Breakdown)</h3>
                    <span class="text-[11px] text-slate-500">Click "Manage / Recommend →" to select vouchers or cancel awards</span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                            <tr>
                                <th class="py-2.5 px-3">Region Name</th>
                                <th class="py-2.5 px-3">SAP Code</th>
                                <th class="py-2.5 px-3">Regional Head</th>
                                <th class="py-2.5 px-3 text-center text-blue-700">🟦 Exium MUPS (Done/Total)</th>
                                <th class="py-2.5 px-3 text-center text-purple-700">🟪 Coralcal-D/DX/Vita (Done/Total)</th>
                                <th class="py-2.5 px-3 text-center">Cancelled</th>
                                <th class="py-2.5 px-3 text-center">Overall Progress</th>
                                <th class="py-2.5 px-3 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody id="zone-regions-tbody" class="divide-y divide-slate-100 font-medium"></tbody>
                    </table>
                </div>
            </div>

            <!-- Zone Voucher Breakdown -->
            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 space-y-3">
                <h3 class="font-black text-xs uppercase tracking-wider text-slate-800">Voucher Choices in this Zone</h3>
                <div id="zone-voucher-cards-grid" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5"></div>
            </div>

        </section>

    </main>

    <!-- Bottom Sticky Action Bar (For Regional View - Mobile Responsive) -->
    <div id="sticky-bar" class="hidden fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur-md border-t border-slate-200 shadow-xl py-2 sm:py-3 z-30">
        <div class="max-w-7xl mx-auto px-2.5 sm:px-6 lg:px-8 flex flex-col sm:flex-row sm:items-center justify-between gap-2 sm:gap-4">
            <div class="flex items-center space-x-2 min-w-0">
                <div class="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-emerald-500 animate-pulse flex-shrink-0"></div>
                <div class="text-[11px] sm:text-xs truncate">
                    <span class="font-black text-slate-900" id="sticky-completed-text">0 Completed</span>
                    <span class="text-slate-400 mx-1">•</span>
                    <span class="text-slate-500 font-medium" id="sticky-region-text">Region</span>
                </div>
            </div>
            <div class="flex items-center gap-1.5 sm:gap-2 w-full sm:w-auto">
                <button onclick="exportBrandExcel('region', 'exium')" class="hidden sm:flex px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-800 border border-blue-300 rounded-xl text-xs font-bold transition items-center gap-1 shadow-xs">
                    <span>📥 Exium MUPS Excel</span>
                </button>
                <button onclick="exportBrandExcel('region', 'coral')" class="hidden sm:flex px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-300 rounded-xl text-xs font-bold transition items-center gap-1 shadow-xs">
                    <span>📥 Coralcal Excel</span>
                </button>
                <button onclick="exitToLogin()" class="flex-1 sm:flex-initial justify-center px-3 py-1.5 border border-slate-300 text-slate-700 hover:bg-slate-100 rounded-xl text-xs font-bold transition flex items-center">
                    Back to Login
                </button>
                <button onclick="manualSaveSync()" id="btn-save-sync" class="flex-1 sm:flex-initial justify-center px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold shadow transition flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg>
                    <span>Save</span>
                </button>
            </div>
        </div>
    </div>

    <!-- ============================================== -->
    <!-- MODAL: OFFICIAL AWARD CRITERIA (SEP 2026)      -->
    <!-- ============================================== -->
    <div id="criteria-modal" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-3 sm:p-5">
        <div class="bg-white rounded-3xl max-w-4xl w-full max-h-[92vh] flex flex-col shadow-2xl overflow-hidden border border-slate-200">
            
            <!-- Modal Header -->
            <div class="bg-white p-4 sm:p-5 border-b border-slate-200 flex justify-between items-center flex-shrink-0">
                <div class="flex items-center space-x-2.5">
                    <div class="w-9 h-9 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 font-bold text-base">
                        📋
                    </div>
                    <div>
                        <h3 class="text-sm sm:text-base font-black text-slate-900">Official Award Criteria — September 2026</h3>
                        <p class="text-[11px] text-slate-500">Separate Evaluation Criteria for Exium MUPS & Coralcal-D/DX/Vita</p>
                    </div>
                </div>
                <button onclick="closeAwardCriteriaModal()" class="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>

            <!-- Modal Tabs: Exium MUPS & Coralcal -->
            <div class="flex border-b border-slate-200 bg-slate-50 px-4 sm:px-6 pt-3 gap-2 flex-shrink-0">
                <button id="tab-crit-exium" onclick="switchCriteriaTab('exium')" class="px-4 py-2.5 rounded-t-xl text-xs sm:text-sm font-black transition border-b-2 border-blue-600 text-blue-700 bg-white shadow-xs">
                    🟦 Exium MUPS Criteria
                </button>
                <button id="tab-crit-coral" onclick="switchCriteriaTab('coral')" class="px-4 py-2.5 rounded-t-xl text-xs sm:text-sm font-bold transition border-b-2 border-transparent text-slate-500 hover:text-slate-800">
                    🟪 Coralcal-D/DX/Vita Criteria
                </button>
            </div>

            <!-- Modal Body -->
            <div class="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-100/70 space-y-4">
                <!-- Exium MUPS Criteria View -->
                <div id="crit-view-exium" class="space-y-4">
                    <div class="bg-blue-50 border border-blue-200 rounded-2xl p-4 text-xs text-blue-950 flex items-center justify-between flex-wrap gap-2">
                        <div>
                            <strong class="text-sm">🟦 Exium MUPS — September 2026 Campaign</strong>
                            <p class="text-[11px] text-blue-800 mt-0.5">National Qualified Achievers: <strong>1,753</strong> (456 × 3,000 + 1,297 × 1,000 = 2,665,000) • Exium MUPS TP: <strong>659.67</strong></p>
                        </div>
                        <span class="font-black bg-blue-600 text-white px-3 py-1 rounded-xl text-xs">Award: 1,000 / 3,000</span>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="px-2.5 py-1 rounded-lg text-xs font-black bg-blue-100 text-blue-800">Criteria 1 • Seen Rx Award</span>
                                <span class="text-sm font-black text-blue-700">Award: 1,000</span>
                            </div>
                            <p class="text-xs text-slate-600 leading-relaxed">
                                • Minimum <strong>200 Seen Rx</strong> of <strong>Exium MUPS</strong> in full month of September 2026.<br>
                                • If Seen Rx is <strong>less than 200</strong>, <strong>No Award (0)</strong> is given.
                            </p>
                        </div>
                        <div class="bg-white rounded-2xl p-4 border-2 border-blue-300 shadow-xs space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="px-2.5 py-1 rounded-lg text-xs font-black bg-blue-600 text-white">Criteria 2 • Sales & Growth Award</span>
                                <span class="text-sm font-black text-blue-700">Award: 3,000</span>
                            </div>
                            <p class="text-xs text-slate-600 leading-relaxed">
                                Must meet <strong>ALL 3 conditions</strong> serially:<br>
                                <strong>(a)</strong> <strong>Exium MUPS Seen Rx &ge; 200</strong> in Sep'26<br>
                                <strong>(b)</strong> <strong>Territory Sales Growth &gt; 0</strong> (Sep'26 Sales &gt; Aug'26 Sales)<br>
                                <strong>(c)</strong> <strong>Exium MUPS Growth &ge; +30 Boxes</strong> (Value Growth &divide; 659.67 TP, rounded to whole number)
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Coralcal Criteria View -->
                <div id="crit-view-coral" class="hidden space-y-4">
                    <div class="bg-purple-50 border border-purple-200 rounded-2xl p-4 text-xs text-purple-950 flex items-center justify-between flex-wrap gap-2">
                        <div>
                            <strong class="text-sm">🟪 Coralcal-D/DX/Vita — September 2026 Campaign</strong>
                            <p class="text-[11px] text-purple-800 mt-0.5">National Qualified Achievers: <strong>1,649</strong> (465 × 3,000 + 1,184 × 1,000 = 2,579,000) • Coralcal-D/DX/Vita TP: <strong>637.18</strong></p>
                        </div>
                        <span class="font-black bg-purple-700 text-white px-3 py-1 rounded-xl text-xs">Award: 1,000 / 3,000</span>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="px-2.5 py-1 rounded-lg text-xs font-black bg-purple-100 text-purple-800">Criteria 1 • Seen Rx Award</span>
                                <span class="text-sm font-black text-purple-700">Award: 1,000</span>
                            </div>
                            <p class="text-xs text-slate-600 leading-relaxed">
                                • Minimum <strong>200 Seen Rx</strong> of <strong>Coralcal-D/DX/Vita</strong> in full month of September 2026.<br>
                                • If Seen Rx is <strong>less than 200</strong>, <strong>No Award (0)</strong> is given.
                            </p>
                        </div>
                        <div class="bg-white rounded-2xl p-4 border-2 border-purple-300 shadow-xs space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="px-2.5 py-1 rounded-lg text-xs font-black bg-purple-700 text-white">Criteria 2 • Sales & Growth Award</span>
                                <span class="text-sm font-black text-purple-700">Award: 3,000</span>
                            </div>
                            <p class="text-xs text-slate-600 leading-relaxed">
                                Must meet <strong>ALL 3 conditions</strong> serially:<br>
                                <strong>(a)</strong> <strong>Coralcal-D/DX/Vita Seen Rx &ge; 200</strong> in Sep'26<br>
                                <strong>(b)</strong> <strong>Territory Sales Growth &gt; 0</strong> (Sep'26 Sales &gt; Aug'26 Sales)<br>
                                <strong>(c)</strong> <strong>Coralcal-D/DX/Vita Growth &ge; +30 Boxes</strong> (Value Growth &divide; 637.18 TP, rounded to whole number)
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Recommendation Rule -->
                <div class="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-xs text-amber-950 space-y-1">
                    <div class="font-black text-amber-900">⚠️ Regional Head & Zonal Head Recommendation Option</div>
                    <p class="text-amber-800">
                        Regional Head or Zonal Head can cancel/withhold any individual Exium MUPS or Coralcal-D/DX/Vita award by clicking <strong>"Cancel Award (Not Recommended)"</strong> on the MIO's brand award card and specifying the mandatory reason.
                    </p>
                </div>
            </div>

            <!-- Modal Footer -->
            <div class="bg-slate-50 p-3 sm:p-4 border-t border-slate-200 flex justify-between items-center flex-shrink-0 flex-wrap gap-2">
                <div class="flex items-center gap-2">
                    <button onclick="exportBrandExcel('admin', 'exium')" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition shadow-xs">
                        📥 Exium MUPS Calculation (.xlsx)
                    </button>
                    <button onclick="exportBrandExcel('admin', 'coral')" class="px-3 py-1.5 bg-purple-700 hover:bg-purple-800 text-white rounded-xl text-xs font-bold transition shadow-xs">
                        📥 Coralcal Calculation (.xlsx)
                    </button>
                </div>
                <button onclick="closeAwardCriteriaModal()" class="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition">
                    Close
                </button>
            </div>

        </div>
    </div>

    <!-- ============================================== -->
    <!-- MODAL: AWARD CANCELLATION (RH / ZH REASON)     -->
    <!-- ============================================== -->
    <div id="cancel-modal" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl max-w-md w-full flex flex-col shadow-2xl overflow-hidden border border-rose-200">
            <div class="bg-rose-50 p-4 sm:p-5 border-b border-rose-200 flex justify-between items-center">
                <div class="flex items-center space-x-2.5">
                    <div class="w-9 h-9 rounded-xl bg-rose-600 text-white flex items-center justify-center font-bold text-base shadow-xs">
                        🚫
                    </div>
                    <div>
                        <h3 class="text-sm sm:text-base font-black text-rose-950">Cancel Award (Not Recommended)</h3>
                        <p id="cancel-modal-subtitle" class="text-[11px] text-rose-700 font-semibold">Regional / Zonal Head Recommendation</p>
                    </div>
                </div>
                <button onclick="closeCancelModal()" class="text-rose-400 hover:text-rose-700 p-1">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>
            <form onsubmit="confirmCancelAward(event)" class="p-5 sm:p-6 space-y-4 text-xs">
                <input type="hidden" id="cancel-ach-id" value="">
                <div id="cancel-mio-summary" class="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-1 text-slate-700"></div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                        1. Cancelled By (Authority)
                    </label>
                    <select id="cancel-by-select" required class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs font-bold text-slate-800 focus:ring-2 focus:ring-rose-500 outline-none">
                        <option value="Regional Head">Regional Head</option>
                        <option value="Zonal Head">Zonal Head</option>
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                        2. Reason for Cancellation <span class="text-rose-600">*</span>
                    </label>
                    <textarea id="cancel-reason-input" required rows="3" placeholder="Write the specific reason for cancelling this award..." class="w-full bg-slate-50 border border-slate-300 rounded-xl p-3 text-xs font-semibold text-slate-800 focus:ring-2 focus:ring-rose-500 outline-none"></textarea>
                </div>

                <div class="flex items-center justify-end gap-2 pt-2">
                    <button type="button" onclick="closeCancelModal()" class="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-100 font-bold text-xs transition">
                        Keep Award
                    </button>
                    <button type="submit" class="px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-black text-xs shadow-md transition">
                        🚫 Confirm Cancellation
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- ============================================== -->
    <!-- MODAL: DATA REVIEW REQUEST (DISCREPANCY FORM)  -->
    <!-- ============================================== -->
    <div id="review-modal" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl max-w-lg w-full flex flex-col shadow-2xl overflow-hidden border border-amber-300 max-h-[90vh]">
            <div class="bg-gradient-to-r from-amber-500 to-orange-600 p-4 sm:p-5 text-white flex justify-between items-center flex-shrink-0">
                <div class="flex items-center space-x-2.5">
                    <div class="w-9 h-9 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center font-bold text-lg shadow-xs">
                        📝
                    </div>
                    <div>
                        <h3 class="text-sm sm:text-base font-black">Data Review Request (RH / ZH Only)</h3>
                        <p class="text-[11px] text-amber-100 font-semibold">Official dispute submission by Regional Head / Zonal Head for Admin verification</p>
                    </div>
                </div>
                <button onclick="closeReviewModal()" class="text-white/80 hover:text-white p-1">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>

            <form onsubmit="submitReviewRequest(event)" class="p-4 sm:p-6 space-y-3.5 text-xs overflow-y-auto">
                <input type="hidden" id="rev-ach-id" value="">
                
                <!-- Target MIO & Territory Card -->
                <div id="rev-mio-summary" class="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-1 text-slate-700"></div>

                <!-- Current System Metrics Breakdown -->
                <div id="rev-metrics-summary" class="bg-amber-50/60 border border-amber-200 rounded-xl p-3 space-y-1 text-slate-800"></div>

                <!-- Dispute Category Dropdown -->
                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        1. Reason for Review / Data Discrepancy <span class="text-rose-600">*</span>
                    </label>
                    <select id="rev-category-select" required class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-slate-800 focus:ring-2 focus:ring-amber-500 outline-none">
                        <option value="Prescription (Seen Rx) Mismatch (Claimed >= 200 Rx)">1. Prescription (Seen Rx) Mismatch (Claimed &ge; 200 Rx in Sep'26)</option>
                        <option value="Territory Sales Calculation Discrepancy (Sales was positive)">2. Territory Sales Calculation Discrepancy (Sales was Positive in Sep'26)</option>
                        <option value="Brand Sales Value / Box Growth Discrepancy">3. Brand Sales Value / Box Growth Discrepancy (Met &ge; +30 Boxes)</option>
                        <option value="Transfer / Joining / Territory Reassignment in Sep'26">4. Transfer / Joining / Territory Reassignment in Sep'26</option>
                        <option value="Tier / Award Amount Discrepancy (e.g. Claimed 3,000 instead of 1,000)">5. Tier / Award Amount Discrepancy (e.g. Claimed 3,000 instead of 1,000)</option>
                        <option value="Other Data Error / Verification Needed">6. Other Data Error / Verification Needed</option>
                    </select>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                            2. Submitter Role (RH / ZH Only) <span class="text-rose-600">*</span>
                        </label>
                        <select id="rev-role-select" required onchange="onRevRoleChange()" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-slate-800 focus:ring-2 focus:ring-amber-500 outline-none">
                            <option value="Regional Head">Regional Head</option>
                            <option value="Zonal Head">Zonal Head</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                            3. Contact Mobile Number <span class="text-rose-600">*</span>
                        </label>
                        <input type="text" id="rev-mobile-input" required placeholder="01XXXXXXXXX" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-slate-800 focus:ring-2 focus:ring-amber-500 outline-none font-mono">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        4. Submitter Name (Regional Head / Zonal Head) <span class="text-rose-600">*</span>
                    </label>
                    <input type="text" id="rev-name-input" required placeholder="Regional Head / Zonal Head Name" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold text-slate-800 focus:ring-2 focus:ring-amber-500 outline-none">
                </div>

                <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                    <button type="button" onclick="closeReviewModal()" class="px-4 py-2 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-100 font-bold text-xs transition">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white font-black text-xs shadow-md transition flex items-center gap-1.5">
                        <span>📤 Submit Review to Admin</span>
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- ============================================== -->
    <!-- MODAL: ADMIN MANUAL AWARD OVERRIDE             -->
    <!-- ============================================== -->
    <div id="manual-override-modal" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl max-w-lg w-full flex flex-col shadow-2xl overflow-hidden border border-blue-300 max-h-[90vh]">
            <div class="bg-gradient-to-r from-blue-700 to-indigo-800 p-4 sm:p-5 text-white flex justify-between items-center flex-shrink-0">
                <div class="flex items-center space-x-2.5">
                    <div class="w-9 h-9 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center font-bold text-lg shadow-xs">
                        🏆
                    </div>
                    <div>
                        <h3 class="text-sm sm:text-base font-black">Admin Manual Award Input & Override</h3>
                        <p class="text-[11px] text-blue-100 font-semibold">Manually grant or adjust award for any MIO / Territory</p>
                    </div>
                </div>
                <button onclick="closeManualOverrideModal()" class="text-white/80 hover:text-white p-1">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>

            <form onsubmit="confirmManualAwardOverride(event)" class="p-4 sm:p-6 space-y-4 text-xs overflow-y-auto">
                <input type="hidden" id="override-ach-id" value="">
                
                <div id="override-mio-summary" class="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-1 text-slate-700"></div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                        1. Select Award Amount to Grant <span class="text-rose-600">*</span>
                    </label>
                    <div class="space-y-2">
                        <label class="flex items-center gap-2.5 p-2.5 rounded-xl border border-emerald-300 bg-emerald-50/50 cursor-pointer hover:bg-emerald-50">
                            <input type="radio" name="override_award_radio" value="3000" id="ov-radio-3000" class="text-emerald-600 focus:ring-emerald-500">
                            <div class="min-w-0">
                                <span class="font-black text-xs text-emerald-900">🏆 3,000 Taka Award (Full 3-Criteria Achiever Tier)</span>
                                <div class="text-[10px] text-emerald-700">Rx &ge; 200 + Positive Territory Sales + Required Brand Growth Met</div>
                            </div>
                        </label>
                        <label class="flex items-center gap-2.5 p-2.5 rounded-xl border border-blue-300 bg-blue-50/50 cursor-pointer hover:bg-blue-50">
                            <input type="radio" name="override_award_radio" value="1000" id="ov-radio-1000" class="text-blue-600 focus:ring-blue-500">
                            <div class="min-w-0">
                                <span class="font-black text-xs text-blue-900">🎖️ 1,000 Taka Award (Prescription / Seen Rx Tier)</span>
                                <div class="text-[10px] text-blue-700">Rx &ge; 200 achieved, sales criteria partial / pending</div>
                            </div>
                        </label>
                        <label class="flex items-center gap-2.5 p-2.5 rounded-xl border border-slate-300 bg-slate-50 cursor-pointer hover:bg-slate-100">
                            <input type="radio" name="override_award_radio" value="0" id="ov-radio-0" class="text-slate-600 focus:ring-slate-500">
                            <div class="min-w-0">
                                <span class="font-black text-xs text-slate-700">⚪ 0 Taka (Revoke Override / Reset to Normal Calculation)</span>
                                <div class="text-[10px] text-slate-500">Reverts to automated system calculation</div>
                            </div>
                        </label>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        2. Admin Approval Reason / Justification <span class="text-rose-600">*</span>
                    </label>
                    <textarea id="override-reason-input" required rows="2.5" placeholder="Specify approval basis (e.g. Rx discrepancy verified with PMD, transfer adjustment approved by Admin, etc.)..." class="w-full bg-slate-50 border border-slate-300 rounded-xl p-2.5 text-xs font-semibold text-slate-800 focus:ring-2 focus:ring-blue-500 outline-none"></textarea>
                </div>

                <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                    <button type="button" onclick="closeManualOverrideModal()" class="px-4 py-2 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-100 font-bold text-xs transition">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-black text-xs shadow-md transition flex items-center gap-1.5">
                        <span>✅ Confirm & Grant Award</span>
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- ============================================== -->
    <!-- MODAL: ZONAL HEAD AUTHENTICATION              -->
    <!-- ============================================== -->
    <div id="zonal-modal" class="hidden fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl max-w-md w-full flex flex-col shadow-2xl overflow-hidden border border-slate-200">
            
            <div class="bg-white p-4 sm:p-5 border-b border-slate-200 flex justify-between items-center">
                <div class="flex items-center space-x-2.5">
                    <div class="w-8 h-8 rounded-lg bg-orange-50 border border-orange-200 flex items-center justify-center text-orange-600 font-bold text-base">
                        🌐
                    </div>
                    <div>
                        <h3 class="text-sm sm:text-base font-black text-slate-900">Zonal Head Login</h3>
                        <p class="text-[11px] text-slate-500">Zonal Award Dashboard (Exium MUPS & Coralcal-D/DX/Vita)</p>
                    </div>
                </div>
                <button onclick="closeZonalModal()" class="text-slate-400 hover:text-slate-600 p-1">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>

            <form id="form-zonal" autocomplete="off" onsubmit="handleZonalLogin(event)" class="p-5 sm:p-6 space-y-4">
                <div class="bg-orange-50 border border-orange-200 rounded-xl p-3 text-xs text-orange-900 font-medium">
                    Zonal Heads can login with their <strong>SAP Zone Code</strong> to inspect zone-wide award selections, completion rates, and submit Zonal Head recommendations.
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                        1. Select Your Zone
                    </label>
                    <select id="zone-login-select" onchange="onZonalZoneChange()" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-orange-500 outline-none cursor-pointer">
                        <option value="">-- Choose Zone --</option>
                    </select>
                </div>

                <div id="zone-details-box" class="hidden bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-xs space-y-1.5">
                    <div class="flex justify-between items-center"><span class="text-slate-500 font-bold">Zonal Head:</span><span id="disp-zh-name" class="font-black text-slate-900">-</span></div>
                    <div class="flex justify-between items-center"><span class="text-slate-500 font-bold">Total Regions:</span><span id="disp-zh-regcount" class="font-black text-slate-900">-</span></div>
                </div>

                <div>
                    <div class="flex justify-between items-center mb-1.5">
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                            2. Zonal Password
                        </label>
                        <span class="text-[10px] text-orange-600 font-black bg-orange-50 px-1.5 py-0.5 rounded border border-orange-200">SAP Zone Code</span>
                    </div>
                    <input type="password" id="zonal-password-input" autocomplete="new-password" placeholder="Enter SAP Zone Code" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-orange-500 outline-none">
                </div>

                <button type="submit" class="w-full py-3 px-4 rounded-xl font-black text-sm text-white bg-slate-900 hover:bg-slate-800 shadow-md transition transform active:scale-[0.99] flex items-center justify-center gap-2">
                    <span>Open Zonal Dashboard</span>
                    <svg class="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                </button>
            </form>
        </div>
    </div>

    <!-- ============================================== -->
    <!-- MODAL: ADMIN PANEL LOGIN & DASHBOARD           -->
    <!-- ============================================== -->
    <div id="admin-modal" class="hidden fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-3 sm:p-4">
        <div class="bg-white rounded-3xl max-w-6xl w-full max-h-[92vh] flex flex-col shadow-2xl overflow-hidden border border-slate-200">
            
            <div class="bg-white p-4 sm:p-5 border-b border-slate-200 flex justify-between items-center">
                <div class="flex items-center space-x-2.5">
                    <div class="w-8 h-8 rounded-lg bg-orange-50 border border-orange-200 flex items-center justify-center text-orange-600 font-bold text-base">
                        🛡️
                    </div>
                    <div>
                        <h3 class="text-sm sm:text-base font-black text-slate-900">Admin Panel - National Award Summary</h3>
                        <p class="text-[11px] text-slate-500">Separate Brand Management & Data Export for Exium MUPS and Coralcal-D/DX/Vita</p>
                    </div>
                </div>
                <button onclick="closeAdminModal()" class="text-slate-400 hover:text-slate-600 p-1">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>

            <div class="p-4 sm:p-6 overflow-y-auto space-y-5 flex-1 text-xs sm:text-sm">
                
                <!-- Password Prompt (If locked) -->
                <div id="admin-auth-box" class="space-y-3 max-w-sm mx-auto py-8 text-center">
                    <div class="w-10 h-10 bg-orange-50 text-orange-600 rounded-xl mx-auto flex items-center justify-center text-xl mb-1 border border-orange-100">
                        🔒
                    </div>
                    <h4 class="font-black text-sm text-slate-900">Admin Authentication</h4>
                    <p class="text-xs text-slate-500">Enter master password to access national summary</p>
                    <div class="flex gap-2">
                        <input type="password" id="admin-password-input" autocomplete="new-password" onkeydown="if(event.key==='Enter') verifyAdminPassword()" placeholder="Enter Admin Password..." class="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-xs font-semibold text-slate-800 outline-none focus:ring-2 focus:ring-orange-500">
                        <button onclick="verifyAdminPassword()" class="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition">
                            Unlock
                        </button>
                    </div>
                </div>

                <!-- Admin Dashboard (When unlocked) -->
                <div id="admin-dashboard-box" class="hidden space-y-5">

                    <!-- ==================================================== -->
                    <!-- SEPARATE BRAND OVERVIEW & DEDICATED EXPORT CARDS     -->
                    <!-- ==================================================== -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- 1. EXIUM MUPS STANDALONE ADMIN CARD -->
                        <div class="bg-blue-50/50 border-2 border-blue-200 rounded-2xl p-4 space-y-3 shadow-xs">
                            <div class="flex items-center justify-between gap-2 flex-wrap border-b border-blue-200/70 pb-2.5">
                                <div>
                                    <span class="px-2.5 py-1 rounded-lg text-xs font-black bg-blue-600 text-white">🟦 Exium MUPS Award</span>
                                    <div class="text-[11px] text-slate-600 font-semibold mt-1">
                                        3,000 Tier: <strong>456</strong> • 1,000 Tier: <strong>1,297</strong> • Total: <strong>1,753</strong>
                                    </div>
                                </div>
                                <button onclick="exportBrandExcel('admin', 'exium')" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-black transition flex items-center gap-1.5 shadow-sm">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                                    <span>Download Exium MUPS Data (.xlsx)</span>
                                </button>
                            </div>
                            <div class="grid grid-cols-4 gap-2 text-center">
                                <div class="bg-white rounded-xl p-2.5 border border-blue-200">
                                    <div class="text-[10px] font-bold text-slate-500 uppercase">Achievers</div>
                                    <div id="admin-exium-total" class="text-lg font-black text-slate-900">1,753</div>
                                    <div id="admin-exium-val" class="text-[9px] text-blue-700 font-bold">Val: 2,665,000</div>
                                </div>
                                <div class="bg-white rounded-xl p-2.5 border border-emerald-200">
                                    <div class="text-[10px] font-bold text-emerald-700 uppercase">Completed</div>
                                    <div id="admin-exium-done" class="text-lg font-black text-emerald-800">0</div>
                                    <div id="admin-exium-pct" class="text-[9px] text-emerald-600 font-bold">0.0%</div>
                                </div>
                                <div class="bg-white rounded-xl p-2.5 border border-amber-200">
                                    <div class="text-[10px] font-bold text-amber-700 uppercase">Pending</div>
                                    <div id="admin-exium-pend" class="text-lg font-black text-amber-800">1,753</div>
                                    <div class="text-[9px] text-amber-600">Awaiting</div>
                                </div>
                                <div class="bg-white rounded-xl p-2.5 border border-rose-200">
                                    <div class="text-[10px] font-bold text-rose-700 uppercase">Cancelled</div>
                                    <div id="admin-exium-canc" class="text-lg font-black text-rose-800">0</div>
                                    <div class="text-[9px] text-rose-600">RH/ZH Cancel</div>
                                </div>
                            </div>
                        </div>

                        <!-- 2. CORALCAL STANDALONE ADMIN CARD -->
                        <div class="bg-purple-50/50 border-2 border-purple-200 rounded-2xl p-4 space-y-3 shadow-xs">
                            <div class="flex items-center justify-between gap-2 flex-wrap border-b border-purple-200/70 pb-2.5">
                                <div>
                                    <span class="px-2.5 py-1 rounded-lg text-xs font-black bg-purple-700 text-white">🟪 Coralcal-D/DX/Vita Award</span>
                                    <div class="text-[11px] text-slate-600 font-semibold mt-1">
                                        3,000 Tier: <strong>465</strong> • 1,000 Tier: <strong>1,184</strong> • Total: <strong>1,649</strong>
                                    </div>
                                </div>
                                <button onclick="exportBrandExcel('admin', 'coral')" class="px-3 py-1.5 bg-purple-700 hover:bg-purple-800 text-white rounded-xl text-xs font-black transition flex items-center gap-1.5 shadow-sm">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                                    <span>Download Coralcal Data (.xlsx)</span>
                                </button>
                            </div>
                            <div class="grid grid-cols-4 gap-2 text-center">
                                <div class="bg-white rounded-xl p-2.5 border border-purple-200">
                                    <div class="text-[10px] font-bold text-slate-500 uppercase">Achievers</div>
                                    <div id="admin-coral-total" class="text-lg font-black text-slate-900">1,649</div>
                                    <div id="admin-coral-val" class="text-[9px] text-purple-700 font-bold">Val: 2,579,000</div>
                                </div>
                                <div class="bg-white rounded-xl p-2.5 border border-emerald-200">
                                    <div class="text-[10px] font-bold text-emerald-700 uppercase">Completed</div>
                                    <div id="admin-coral-done" class="text-lg font-black text-emerald-800">0</div>
                                    <div id="admin-coral-pct" class="text-[9px] text-emerald-600 font-bold">0.0%</div>
                                </div>
                                <div class="bg-white rounded-xl p-2.5 border border-amber-200">
                                    <div class="text-[10px] font-bold text-amber-700 uppercase">Pending</div>
                                    <div id="admin-coral-pend" class="text-lg font-black text-amber-800">1,649</div>
                                    <div class="text-[9px] text-amber-600">Awaiting</div>
                                </div>
                                <div class="bg-white rounded-xl p-2.5 border border-rose-200">
                                    <div class="text-[10px] font-bold text-rose-700 uppercase">Cancelled</div>
                                    <div id="admin-coral-canc" class="text-lg font-black text-rose-800">0</div>
                                    <div class="text-[9px] text-rose-600">RH/ZH Cancel</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- ==================================================== -->
                    <!-- ADMIN BRAND VIEW SWITCHER TABS                       -->
                    <!-- ==================================================== -->
                    <div class="bg-slate-100 p-1.5 rounded-2xl border border-slate-200 flex flex-wrap items-center justify-between gap-2">
                        <div class="flex items-center gap-1.5 flex-wrap">
                            <button type="button" id="admin-brand-tab-exium" onclick="setAdminBrandMode('exium')" class="px-4 py-2 rounded-xl text-xs font-black transition bg-blue-600 text-white shadow-sm">
                                🟦 View Exium MUPS Award Details (1,753)
                            </button>
                            <button type="button" id="admin-brand-tab-coral" onclick="setAdminBrandMode('coral')" class="px-4 py-2 rounded-xl text-xs font-bold transition bg-white text-purple-800 hover:bg-purple-50 border border-purple-200">
                                🟪 View Coralcal Award Details (1,649)
                            </button>
                            <button type="button" id="admin-brand-tab-both" onclick="setAdminBrandMode('both')" class="px-4 py-2 rounded-xl text-xs font-bold transition bg-white text-slate-700 hover:bg-slate-50 border border-slate-200">
                                📊 View Combined Overview (3,402)
                            </button>
                        </div>
                        <span id="admin-active-brand-indicator" class="px-3 py-1 rounded-xl text-[11px] font-black bg-blue-100 text-blue-900">
                            Showing: Exium MUPS Award
                        </span>
                    </div>

                    <!-- Region-Wise Submission & Completion Status Table (Filtered by Selected Brand) -->
                    <div class="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
                        
                        <!-- Header & Controls -->
                        <div class="p-3.5 sm:p-4 bg-slate-50 border-b border-slate-200 space-y-3">
                            <div class="flex flex-wrap items-center justify-between gap-2.5">
                                <div>
                                    <div class="flex items-center gap-2">
                                        <span class="text-base">📊</span>
                                        <h4 id="admin-reg-table-title" class="font-black text-xs sm:text-sm text-slate-900 uppercase tracking-wider">
                                            Region-wise Input & Submission Tracking (Exium MUPS)
                                        </h4>
                                        <span id="admin-reg-total-badge" class="px-2 py-0.5 rounded-full text-[10px] font-black bg-slate-200 text-slate-700">Regions</span>
                                    </div>
                                    <p class="text-[11px] text-slate-500 mt-0.5">
                                        Monitor which Regional Heads have completed inputs, who is in progress, and who has not started yet.
                                    </p>
                                </div>
                                <div class="flex flex-wrap items-center gap-1.5">
                                    <button type="button" onclick="copyPendingRegionsSummary()" title="Copy list of all pending regions to clipboard" class="px-2.5 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-300 rounded-lg text-xs font-bold transition flex items-center gap-1 shadow-2xs">
                                        <span>📋</span>
                                        <span>Copy Pending List</span>
                                    </button>
                                    <button type="button" onclick="exportRegionSummaryToExcel()" title="Export region completion status table to Excel" class="px-2.5 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg text-xs font-bold transition flex items-center gap-1 shadow-2xs">
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                                        <span>Export Regions (.xlsx)</span>
                                    </button>
                                </div>
                            </div>

                            <!-- Region Status Overview Mini-Cards -->
                            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
                                <div class="bg-white border border-emerald-200 rounded-xl p-2.5 text-center shadow-2xs">
                                    <div class="text-[10px] font-bold text-emerald-700 uppercase">100% Completed</div>
                                    <div id="admin-reg-stat-completed" class="text-lg font-black text-emerald-800">0</div>
                                    <div class="text-[9px] text-emerald-600 font-medium">All inputs given</div>
                                </div>
                                <div class="bg-white border border-amber-200 rounded-xl p-2.5 text-center shadow-2xs">
                                    <div class="text-[10px] font-bold text-amber-700 uppercase">In Progress</div>
                                    <div id="admin-reg-stat-inprogress" class="text-lg font-black text-amber-800">0</div>
                                    <div class="text-[9px] text-amber-600 font-medium">Partially submitted</div>
                                </div>
                                <div class="bg-white border border-rose-200 rounded-xl p-2.5 text-center shadow-2xs">
                                    <div class="text-[10px] font-bold text-rose-700 uppercase">Not Started</div>
                                    <div id="admin-reg-stat-notstarted" class="text-lg font-black text-rose-800">0</div>
                                    <div class="text-[9px] text-rose-600 font-medium">0% input given</div>
                                </div>
                                <div class="bg-white border border-slate-200 rounded-xl p-2.5 text-center shadow-2xs">
                                    <div class="text-[10px] font-bold text-slate-500 uppercase">Pending Inputs</div>
                                    <div id="admin-reg-stat-pendingawards" class="text-lg font-black text-slate-800">0</div>
                                    <div class="text-[9px] text-slate-500 font-medium">Achievers awaiting choice</div>
                                </div>
                            </div>

                            <!-- Search, Filter & Sort Controls -->
                            <div class="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-200/80">
                                <div class="flex flex-wrap items-center gap-2 flex-1 min-w-[240px]">
                                    <div class="relative flex-1 min-w-[180px]">
                                        <input type="text" id="admin-reg-search" oninput="renderAdminRegionTable()" placeholder="Search region, regional head, zone..." class="w-full bg-white border border-slate-300 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-800 outline-none focus:ring-2 focus:ring-orange-500">
                                        <svg class="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                                    </div>
                                    <select id="admin-reg-sort" onchange="renderAdminRegionTable()" class="bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-slate-700 outline-none focus:ring-2 focus:ring-orange-500 cursor-pointer">
                                        <option value="pending_first">Sort: Pending First (Default)</option>
                                        <option value="completed_first">Sort: Completed First</option>
                                        <option value="achievers_desc">Sort: Most Achievers</option>
                                        <option value="pct_asc">Sort: Progress % (Low to High)</option>
                                        <option value="pct_desc">Sort: Progress % (High to Low)</option>
                                        <option value="name_asc">Sort: Region Name (A-Z)</option>
                                        <option value="zone_asc">Sort: Zone Name (A-Z)</option>
                                    </select>
                                </div>
                                <div class="flex items-center gap-1 overflow-x-auto pb-0.5" id="admin-reg-filter-pills">
                                    <button type="button" onclick="setAdminRegionFilter('all')" id="rf-pill-all" class="px-2.5 py-1 rounded-md text-[11px] font-bold bg-slate-900 text-white transition">All</button>
                                    <button type="button" onclick="setAdminRegionFilter('pending')" id="rf-pill-pending" class="px-2.5 py-1 rounded-md text-[11px] font-bold bg-white text-slate-600 hover:bg-slate-100 border border-slate-200 transition">⚠️ Any Pending</button>
                                    <button type="button" onclick="setAdminRegionFilter('not_started')" id="rf-pill-not_started" class="px-2.5 py-1 rounded-md text-[11px] font-bold bg-white text-slate-600 hover:bg-slate-100 border border-slate-200 transition">🔴 Not Started</button>
                                    <button type="button" onclick="setAdminRegionFilter('in_progress')" id="rf-pill-in_progress" class="px-2.5 py-1 rounded-md text-[11px] font-bold bg-white text-slate-600 hover:bg-slate-100 border border-slate-200 transition">🟡 In Progress</button>
                                    <button type="button" onclick="setAdminRegionFilter('completed')" id="rf-pill-completed" class="px-2.5 py-1 rounded-md text-[11px] font-bold bg-white text-slate-600 hover:bg-slate-100 border border-slate-200 transition">🟢 Completed</button>
                                </div>
                            </div>

                        </div>

                        <!-- Scrollable Table Body -->
                        <div class="max-h-80 overflow-y-auto overflow-x-auto">
                            <table class="w-full text-left text-xs border-collapse">
                                <thead class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200 sticky top-0 z-10 shadow-2xs">
                                    <tr>
                                        <th class="py-2.5 px-3 w-10 text-center">#</th>
                                        <th class="py-2.5 px-3 min-w-[200px]">Region & Regional Head</th>
                                        <th class="py-2.5 px-3 min-w-[120px]">Zone</th>
                                        <th class="py-2.5 px-3 text-center min-w-[110px]">Total Awards</th>
                                        <th class="py-2.5 px-3 text-center min-w-[80px]">Done</th>
                                        <th class="py-2.5 px-3 text-center min-w-[80px]">Pending</th>
                                        <th class="py-2.5 px-3 min-w-[130px]">Completion Progress</th>
                                        <th class="py-2.5 px-3 text-center min-w-[110px]">Status</th>
                                        <th class="py-2.5 px-3 text-center min-w-[80px]">Action</th>
                                    </tr>
                                </thead>
                                <tbody id="admin-region-tbody" class="divide-y divide-slate-100 font-medium bg-white"></tbody>
                            </table>
                        </div>

                        <!-- Footer Summary of Filtered Rows -->
                        <div class="px-4 py-2 bg-slate-50 border-t border-slate-200 flex flex-wrap justify-between items-center text-[11px] text-slate-500 gap-2">
                            <span id="admin-reg-showing-count">Showing regions</span>
                            <span class="italic">Click "View ↗" to instantly open any region's award cards</span>
                        </div>

                    </div>

                    <!-- Voucher Brand Breakdown Table (Filtered by Selected Brand) -->
                    <div class="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                        <div class="p-3 bg-slate-50 border-b border-slate-200 font-black text-xs uppercase tracking-wider text-slate-800 flex justify-between items-center">
                            <span id="admin-voucher-table-title">National Voucher Brand Requirements (PO Planning)</span>
                            <span class="text-[11px] text-slate-500 font-normal">Real-time (Excludes Cancelled)</span>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs">
                                <thead class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                                    <tr>
                                        <th class="py-2 px-3">Brand Logo & Name</th>
                                        <th class="py-2 px-3 text-center">1,000 Vouchers</th>
                                        <th class="py-2 px-3 text-center">3,000 Vouchers</th>
                                        <th class="py-2 px-3 text-center">Total Count</th>
                                        <th class="py-2 px-3 text-center">Total Value</th>
                                        <th class="py-2 px-3 text-right">Share (%)</th>
                                    </tr>
                                </thead>
                                <tbody id="admin-voucher-tbody" class="divide-y divide-slate-100 font-medium"></tbody>
                            </table>
                        </div>
                    </div>
                    <!-- ==================================================== -->
                    <!-- DATA REVIEW REQUESTS & MANUAL AWARD OVERRIDE CENTER  -->
                    <!-- ==================================================== -->
                    <div class="bg-white border-2 border-amber-300 rounded-2xl overflow-hidden shadow-sm space-y-0">
                        <div class="p-3.5 sm:p-4 bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 text-white flex flex-wrap items-center justify-between gap-2">
                            <div class="flex items-center space-x-2">
                                <span class="text-xl">🔍</span>
                                <div>
                                    <h4 class="font-black text-xs sm:text-sm uppercase tracking-wider">
                                        Data Review Requests & Manual Award Override Center
                                    </h4>
                                    <p class="text-[11px] text-amber-100 font-medium">
                                        Review territory discrepancies reported by MIOs / RHs and manually grant or adjust awards.
                                    </p>
                                </div>
                            </div>
                            <div class="flex items-center gap-2">
                                <span id="admin-pending-review-badge" class="px-2.5 py-1 rounded-full text-xs font-black bg-white text-orange-800 shadow-2xs">
                                    0 Pending Reviews
                                </span>
                                <span id="admin-total-overrides-badge" class="px-2.5 py-1 rounded-full text-xs font-black bg-amber-900/40 text-white border border-amber-300/40">
                                    0 Manual Grants
                                </span>
                            </div>
                        </div>

                        <!-- Direct Manual Award Grant Quick Form -->
                        <div class="p-3.5 bg-amber-50/50 border-b border-amber-200 space-y-2">
                            <div class="font-black text-xs text-amber-950 flex items-center gap-1.5">
                                <span>⚡ Direct Manual Award Grant Tool (Any MIO / Territory):</span>
                            </div>
                            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2 items-end">
                                <div class="lg:col-span-2">
                                    <label class="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Search & Select MIO / Territory</label>
                                    <input type="text" id="admin-direct-mio-input" list="admin-all-mios-datalist" placeholder="Type MIO Name, SAP ID, or Area..." class="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 outline-none focus:ring-2 focus:ring-amber-500 font-medium">
                                    <datalist id="admin-all-mios-datalist"></datalist>
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Brand</label>
                                    <select id="admin-direct-brand-select" class="w-full bg-white border border-slate-300 rounded-lg px-2 py-1.5 text-xs font-bold text-slate-800 outline-none focus:ring-2 focus:ring-amber-500">
                                        <option value="exium">🟦 Exium MUPS</option>
                                        <option value="coral">🟪 Coralcal-D/DX/Vita</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-[10px] font-bold text-slate-600 uppercase mb-0.5">Award to Grant</label>
                                    <select id="admin-direct-award-select" class="w-full bg-white border border-slate-300 rounded-lg px-2 py-1.5 text-xs font-black text-slate-800 outline-none focus:ring-2 focus:ring-amber-500">
                                        <option value="3000">🏆 3,000 Taka</option>
                                        <option value="1000">🎖️ 1,000 Taka</option>
                                        <option value="0">⚪ 0 (Revoke)</option>
                                    </select>
                                </div>
                                <div>
                                    <button type="button" onclick="adminExecuteDirectGrant()" class="w-full py-1.5 px-3 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-black transition shadow-xs flex items-center justify-center gap-1">
                                        <span>⚡ Grant Award</span>
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Submitted Review Requests Table -->
                        <div class="max-h-72 overflow-y-auto overflow-x-auto">
                            <table class="w-full text-left text-xs border-collapse">
                                <thead class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200 sticky top-0 z-10 shadow-2xs">
                                    <tr>
                                        <th class="py-2 px-3 w-28">Submitted</th>
                                        <th class="py-2 px-3 min-w-[120px]">Brand</th>
                                        <th class="py-2 px-3 min-w-[180px]">MIO & Territory</th>
                                        <th class="py-2 px-3 min-w-[120px]">Region & Zone</th>
                                        <th class="py-2 px-3 min-w-[160px]">Dispute Category</th>
                                        <th class="py-2 px-3 min-w-[200px]">Remarks & Contact</th>
                                        <th class="py-2 px-3 text-center min-w-[90px]">Status</th>
                                        <th class="py-2 px-3 text-center min-w-[150px]">Admin Action</th>
                                    </tr>
                                </thead>
                                <tbody id="admin-reviews-tbody" class="divide-y divide-slate-100 font-medium bg-white"></tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Cancelled Awards Log (RH / ZH Recommendations) -->
                    <div class="bg-white border border-rose-200 rounded-xl overflow-hidden shadow-sm">
                        <div class="p-3 bg-rose-50 border-b border-rose-200 font-black text-xs uppercase tracking-wider text-rose-900 flex justify-between items-center">
                            <span id="admin-cancel-table-title">🚫 Cancelled Awards Log (RH / ZH Recommendations)</span>
                            <span id="admin-cancelled-badge" class="px-2 py-0.5 rounded-full text-[10px] font-black bg-rose-200 text-rose-900">0 Cancelled</span>
                        </div>
                        <div class="max-h-60 overflow-y-auto overflow-x-auto">
                            <table class="w-full text-left text-xs">
                                <thead class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                                    <tr>
                                        <th class="py-2 px-3">Brand</th>
                                        <th class="py-2 px-3">Zone & Region</th>
                                        <th class="py-2 px-3">Territory & MIO</th>
                                        <th class="py-2 px-3 text-center">Award</th>
                                        <th class="py-2 px-3">Cancelled By</th>
                                        <th class="py-2 px-3">Reason</th>
                                        <th class="py-2 px-3 text-right">Action</th>
                                    </tr>
                                </thead>
                                <tbody id="admin-cancelled-tbody" class="divide-y divide-slate-100 font-medium"></tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Admin Controls: Regional Head Input Control (On/Off) & Data Reset -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                        
                        <!-- 1. Regional Head Input On/Off Toggle -->
                        <div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 space-y-2.5 flex flex-col justify-between">
                            <div>
                                <div class="flex items-center justify-between gap-2 mb-1.5">
                                    <div class="flex items-center gap-1.5">
                                        <span class="text-base">🔒</span>
                                        <h4 class="font-black text-xs sm:text-sm text-slate-900">Regional Head Input Control</h4>
                                    </div>
                                    <span id="admin-lock-badge" class="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800 border border-emerald-300">🟢 Input ON (Active)</span>
                                </div>
                                <p class="text-[11px] text-slate-500 leading-snug">
                                    Enable or freeze voucher choices for Regional Heads. When <strong>OFF (Locked)</strong>, the portal switches to Read-Only mode.
                                </p>
                            </div>
                            <div class="pt-1">
                                <button id="admin-toggle-lock-btn" onclick="toggleSubmissionLock()" class="w-full py-2 px-3 rounded-xl text-xs font-black transition flex items-center justify-center gap-2 shadow-xs bg-rose-600 hover:bg-rose-700 text-white">
                                    <span>🔒 Turn OFF Input (Lock Submissions)</span>
                                </button>
                            </div>
                        </div>

                        <!-- 2. Data Deletion & Reset Center -->
                        <div class="bg-rose-50/60 border border-rose-200 rounded-2xl p-4 space-y-2.5 flex flex-col justify-between">
                            <div>
                                <div class="flex items-center justify-between gap-2 mb-1.5">
                                    <div class="flex items-center gap-1.5">
                                        <span class="text-base">🗑️</span>
                                        <h4 class="font-black text-xs sm:text-sm text-rose-950">Data Deletion & Reset</h4>
                                    </div>
                                    <span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">Admin Only</span>
                                </div>
                                <p class="text-[11px] text-rose-900/80 leading-snug">
                                    Clear submitted choices and reset MIO records back to <strong>Pending</strong> (with double-confirmation protection).
                                </p>
                            </div>
                            <div class="grid grid-cols-2 gap-2 pt-1">
                                <button onclick="adminDeleteCurrentRegionData()" title="Clear choices only for active region" class="py-2 px-2.5 bg-white hover:bg-rose-50 text-rose-700 font-bold rounded-xl border border-rose-300 text-xs transition flex items-center justify-center gap-1 shadow-2xs">
                                    <span>🗑️</span>
                                    <span>Reset Region</span>
                                </button>
                                <button onclick="adminDeleteAllNationalData()" title="Clear choices for all MIOs nationwide" class="py-2 px-2.5 bg-rose-600 hover:bg-rose-700 text-white font-black rounded-xl text-xs transition flex items-center justify-center gap-1 shadow-xs">
                                    <span>⚠️</span>
                                    <span>Delete All Data</span>
                                </button>
                            </div>
                        </div>

                    </div>

                    <!-- Google Apps Script URL Endpoint & Masked Link Banner -->
                    <div class="bg-slate-50 border border-slate-200 rounded-xl p-3.5 space-y-2.5">
                        <div class="flex flex-wrap items-center justify-between gap-2">
                            <label class="block text-xs font-bold text-slate-700">Google Apps Script Web App Endpoint URL (Google Sheet Live Sync)</label>
                            <div class="flex items-center gap-2">
                                <button type="button" onclick="copyGoogleAppsScriptCode()" class="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-[11px] font-bold transition shadow-2xs">
                                    📋 Copy Apps Script Code (.gs)
                                </button>
                                <span id="admin-endpoint-status" class="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300 hidden">✓ Connected</span>
                            </div>
                        </div>
                        <div class="flex flex-wrap gap-2">
                            <input type="text" id="admin-endpoint-input" placeholder="Paste deployed Google Apps Script URL (https://script.google.com/macros/s/.../exec)" class="flex-1 min-w-[260px] bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs font-mono text-slate-800 outline-none focus:ring-2 focus:ring-orange-500">
                            <button onclick="saveAdminEndpoint()" class="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition">Save URL</button>
                            <button onclick="syncFromCloud(false)" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition flex items-center gap-1 shadow-xs">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                                <span>Sync Now</span>
                            </button>
                        </div>

                        <!-- Universal Multi-Device Cloud Sync Link Banner -->
                        <div class="p-3 bg-emerald-50/90 border border-emerald-200 rounded-xl flex flex-wrap items-center justify-between gap-2">
                            <div class="space-y-0.5">
                                <span class="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
                                    <span>🌐</span>
                                    <span>Shareable Masked Portal Link</span>
                                </span>
                                <p class="text-[11px] text-emerald-800">
                                    Share this clean link with all Regional & Zonal Heads: <strong id="masked-link-text" class="font-mono text-emerald-950">https://tinyurl.com/mio-award-sep-2026</strong>
                                </p>
                            </div>
                            <button onclick="copyShareableLink()" class="px-2.5 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg text-xs font-bold transition flex items-center gap-1 shrink-0 shadow-xs">
                                <span>📋 Copy Masked Link</span>
                            </button>
                        </div>
                    </div>

                </div>

            </div>

            <!-- Admin Footer with Separate Exium MUPS & Coralcal Excel Export Buttons -->
            <div class="bg-slate-50 p-3.5 border-t border-slate-200 flex flex-wrap justify-between items-center gap-2">
                <div class="flex flex-wrap items-center gap-2">
                    <button onclick="exportBrandExcel('admin', 'exium')" class="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition shadow-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                        <span>Export Exium MUPS Data (.xlsx)</span>
                    </button>
                    <button onclick="exportBrandExcel('admin', 'coral')" class="px-3.5 py-2 bg-purple-700 hover:bg-purple-800 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition shadow-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                        <span>Export Coralcal Data (.xlsx)</span>
                    </button>
                    <button onclick="exportBrandExcel('admin', 'both')" class="px-3.5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition shadow-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                        <span>Export Combined (.xlsx)</span>
                    </button>
                </div>
                <button onclick="closeAdminModal()" class="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition">
                    Close
                </button>
            </div>

        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast-box" class="fixed top-16 right-4 bg-slate-900 text-white px-4 py-2.5 rounded-2xl shadow-xl flex items-center space-x-2 text-xs font-bold transform translate-x-32 opacity-0 pointer-events-none transition-all duration-300 z-50">
        <span id="toast-icon">✅</span>
        <span id="toast-text">Notification</span>
    </div>

    <!-- CLIENT LOGIC & EMBEDDED DATABASE -->
    <script>
        const DB = {json_db_str};

        const MASKED_PORTAL_URL = 'https://tinyurl.com/mio-award-sep-2026';

        const BRANDS = [
            {{
                name: 'Infinity Gift Voucher',
                subtitle: 'Mega Mall & Lifestyle',
                key: 'infinity',
                logo: DB.logos.infinity
            }},
            {{
                name: 'Apex Gift Voucher',
                subtitle: 'Premium Footwear & Leather',
                key: 'apex',
                logo: DB.logos.apex
            }},
            {{
                name: 'Bata Gift Voucher',
                subtitle: 'Footwear & Accessories',
                key: 'bata',
                logo: DB.logos.bata
            }},
            {{
                name: 'Aarong Gift Voucher',
                subtitle: 'Heritage & Lifestyle Fashion',
                key: 'aarong',
                logo: DB.logos.aarong
            }},
            {{
                name: 'Best Buy Gift Voucher',
                subtitle: 'RFL Home & Electronics',
                key: 'bestbuy',
                logo: DB.logos.bestbuy
            }},
            {{
                name: 'Cats Eye Gift Voucher',
                subtitle: 'Fashion & Lifestyle',
                key: 'catseye',
                logo: DB.logos.catseye
            }}
        ];

        // 12 Distinct Light Color Themes for MIO Profile & Territory Headers (Exact Previous System Palette)
        const MIO_COLOR_PALETTES = [
            {{ bg: 'bg-sky-100', border: 'border-sky-300', avatar: 'bg-sky-600', desigBg: 'bg-white text-sky-950 border-sky-300' }},
            {{ bg: 'bg-emerald-100', border: 'border-emerald-300', avatar: 'bg-emerald-600', desigBg: 'bg-white text-emerald-950 border-emerald-300' }},
            {{ bg: 'bg-amber-100', border: 'border-amber-300', avatar: 'bg-amber-600', desigBg: 'bg-white text-amber-950 border-amber-300' }},
            {{ bg: 'bg-purple-100', border: 'border-purple-300', avatar: 'bg-purple-600', desigBg: 'bg-white text-purple-950 border-purple-300' }},
            {{ bg: 'bg-rose-100', border: 'border-rose-300', avatar: 'bg-rose-600', desigBg: 'bg-white text-rose-950 border-rose-300' }},
            {{ bg: 'bg-teal-100', border: 'border-teal-300', avatar: 'bg-teal-600', desigBg: 'bg-white text-teal-950 border-teal-300' }},
            {{ bg: 'bg-indigo-100', border: 'border-indigo-300', avatar: 'bg-indigo-600', desigBg: 'bg-white text-indigo-950 border-indigo-300' }},
            {{ bg: 'bg-cyan-100', border: 'border-cyan-300', avatar: 'bg-cyan-600', desigBg: 'bg-white text-cyan-950 border-cyan-300' }},
            {{ bg: 'bg-orange-100', border: 'border-orange-300', avatar: 'bg-orange-600', desigBg: 'bg-white text-orange-950 border-orange-300' }},
            {{ bg: 'bg-violet-100', border: 'border-violet-300', avatar: 'bg-violet-600', desigBg: 'bg-white text-violet-950 border-violet-300' }},
            {{ bg: 'bg-lime-100', border: 'border-lime-300', avatar: 'bg-lime-600', desigBg: 'bg-white text-lime-950 border-lime-300' }},
            {{ bg: 'bg-fuchsia-100', border: 'border-fuchsia-300', avatar: 'bg-fuchsia-600', desigBg: 'bg-white text-fuchsia-950 border-fuchsia-300' }}
        ];

        const STORAGE_KEY_CHOICES = 'SEP26_AWARD_CHOICES';
        const STORAGE_KEY_QUEUE = 'SEP26_PENDING_QUEUE';
        const STORAGE_KEY_SESSION = 'SEP26_AWARD_SESSION';
        const STORAGE_KEY_ENDPOINT = 'SEP26_AWARD_ENDPOINT';
        const STORAGE_KEY_LOCKED = 'SEP26_SUBMISSIONS_LOCKED';
        const STORAGE_KEY_REVIEWS = 'SEP26_AWARD_REVIEWS';
        const STORAGE_KEY_OVERRIDES = 'SEP26_MANUAL_OVERRIDES';

        let currentRegionName = '';
        let currentActiveZoneCode = '';
        let currentRegionalBrandFilter = 'all'; // 'all' | 'exium' | 'coral'
        let currentRegionalStatusFilter = 'all'; // 'all' | 'achievers' | 'non_achievers' | 'in_review'
        let currentAdminBrandMode = 'exium';    // 'exium' | 'coral' | 'both'
        let currentAdminRegionFilter = 'all';

        let savedChoices = JSON.parse(localStorage.getItem(STORAGE_KEY_CHOICES) || '{{}}');
        let savedReviews = JSON.parse(localStorage.getItem(STORAGE_KEY_REVIEWS) || '{{}}');
        let savedOverrides = JSON.parse(localStorage.getItem(STORAGE_KEY_OVERRIDES) || '{{}}');

        const DEFAULT_CLOUD_ENDPOINT = 'https://script.google.com/macros/s/AKfycbwZnaiyLSlMSGEjgQa4hVWQ_GsR1hYKM1O95s_dYltG7yVeO1j7h4zFY8x11E7V9eu_/exec';

        let queryEndpoint = '';
        try {{
            const urlParams = new URLSearchParams(window.location.search);
            queryEndpoint = (urlParams.get('api') || urlParams.get('endpoint') || '').trim();
            if (queryEndpoint) {{
                localStorage.setItem(STORAGE_KEY_ENDPOINT, queryEndpoint);
            }}
        }} catch (e) {{}}

        let cloudEndpoint = queryEndpoint || localStorage.getItem(STORAGE_KEY_ENDPOINT) || DEFAULT_CLOUD_ENDPOINT;
        let isAdminUnlocked = false;
        let isSubmissionsLocked = (localStorage.getItem(STORAGE_KEY_LOCKED) === 'true');

        function getBDTimestamp() {{
            try {{
                const d = new Date();
                const parts = new Intl.DateTimeFormat('en-GB', {{
                    timeZone: 'Asia/Dhaka',
                    day: '2-digit',
                    month: 'short',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: true
                }}).formatToParts(d);

                let day = '', month = '', year = '', hour = '', min = '', sec = '', dayPeriod = '';
                for (const p of parts) {{
                    if (p.type === 'day') day = p.value;
                    else if (p.type === 'month') month = p.value;
                    else if (p.type === 'year') year = p.value;
                    else if (p.type === 'hour') hour = p.value;
                    else if (p.type === 'minute') min = p.value;
                    else if (p.type === 'second') sec = p.value;
                    else if (p.type === 'dayPeriod') dayPeriod = p.value.replace(/\\./g, '').toUpperCase();
                }}
                if (day && month && year && hour && min && sec && dayPeriod) {{
                    return `${{day}}-${{month}}-${{year}} ${{hour}}:${{min}}:${{sec}} ${{dayPeriod}}`;
                }}
            }} catch (e) {{}}

            const d = new Date();
            const bdDate = new Date(d.getTime() + (6 * 60 * 60 * 1000));
            const pad = n => String(n).padStart(2, '0');
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            let h = bdDate.getUTCHours();
            const ampm = h >= 12 ? 'PM' : 'AM';
            h = h % 12 || 12;
            return `${{pad(bdDate.getUTCDate())}}-${{months[bdDate.getUTCMonth()]}}-${{bdDate.getUTCFullYear()}} ${{pad(h)}}:${{pad(bdDate.getUTCMinutes())}}:${{pad(bdDate.getUTCSeconds())}} ${{ampm}}`;
        }}

        function formatToBDTime(isoOrStr) {{
            if (!isoOrStr) return '';
            const trimmed = String(isoOrStr).trim();
            if (/^\\d{{2}}-[A-Za-z]{{3}}-\\d{{4}}\\s+\\d{{1,2}}:\\d{{2}}:\\d{{2}}\\s+(AM|PM)/i.test(trimmed)) {{
                return trimmed;
            }}
            try {{
                const d = new Date(trimmed);
                if (isNaN(d.getTime())) return trimmed;
                const bdDate = new Date(d.getTime() + (6 * 60 * 60 * 1000));
                const pad = n => String(n).padStart(2, '0');
                const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                let h = bdDate.getUTCHours();
                const ampm = h >= 12 ? 'PM' : 'AM';
                h = h % 12 || 12;
                return `${{pad(bdDate.getUTCDate())}}-${{months[bdDate.getUTCMonth()]}}-${{bdDate.getUTCFullYear()}} ${{pad(h)}}:${{pad(bdDate.getUTCMinutes())}}:${{pad(bdDate.getUTCSeconds())}} ${{ampm}}`;
            }} catch (e) {{
                return trimmed;
            }}
        }}

        function isAwardResolved(achId) {{
            const ch = savedChoices[achId];
            if (!ch) return false;
            return Boolean(ch.voucher || ch.cancelled);
        }}

        function isAwardCancelled(achId) {{
            const ch = savedChoices[achId];
            return Boolean(ch && ch.cancelled);
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            initLoginDropdowns();

            const clearAuthPasswords = () => {{
                ['reg-password-input', 'zonal-password-input', 'admin-password-input'].forEach(id => {{
                    const el = document.getElementById(id);
                    if (el) el.value = '';
                }});
            }};
            clearAuthPasswords();
            setTimeout(clearAuthPasswords, 100);
            setTimeout(clearAuthPasswords, 300);

            if (cloudEndpoint) {{
                const input = document.getElementById('admin-endpoint-input');
                if (input) input.value = cloudEndpoint;
                const statusBadge = document.getElementById('admin-endpoint-status');
                if (statusBadge) statusBadge.classList.remove('hidden');
                flushPendingQueue();
                syncFromCloud(true);
            }} else {{
                updateSyncStatusBadge('ready');
            }}

            setInterval(() => {{
                if (cloudEndpoint && !isSyncing) {{
                    syncFromCloud(true);
                }}
            }}, 10000);

            updateSubmissionLockUI();

            const session = JSON.parse(localStorage.getItem(STORAGE_KEY_SESSION) || 'null');
            if (session && session.region && DB.regions_map[session.region]) {{
                openRegionalView(session.region);
            }}
        }});

        function initLoginDropdowns() {{
            const sortedZones = [...DB.zones].sort((a, b) => a.zone_name.localeCompare(b.zone_name));

            const regZoneSel = document.getElementById('reg-zone-select');
            regZoneSel.innerHTML = '<option value="">-- Choose Zone --</option>';
            sortedZones.forEach(z => {{
                const opt = document.createElement('option');
                opt.value = z.sap_zone_code;
                opt.textContent = `${{z.zone_name}} (${{z.sap_zone_code}})`;
                regZoneSel.appendChild(opt);
            }});

            const zoneLoginSel = document.getElementById('zone-login-select');
            zoneLoginSel.innerHTML = '<option value="">-- Choose Zone --</option>';
            sortedZones.forEach(z => {{
                const opt = document.createElement('option');
                opt.value = z.sap_zone_code;
                opt.textContent = `${{z.zone_name}} - ${{z.zonal_head}} (${{z.sap_zone_code}})`;
                zoneLoginSel.appendChild(opt);
            }});
        }}

        function switchLoginTab(mode) {{
            const tabReg = document.getElementById('tab-reg');
            const tabMio = document.getElementById('tab-mio');
            const formReg = document.getElementById('form-regional');
            const formMio = document.getElementById('form-mio-search');

            if (mode === 'regional') {{
                tabReg.className = 'flex-1 py-3 text-center border-b-2 border-orange-500 text-orange-600 bg-white font-black';
                tabMio.className = 'flex-1 py-3 text-center border-b-2 border-transparent text-slate-500 hover:text-slate-800';
                formReg.classList.remove('hidden');
                formMio.classList.add('hidden');
            }} else {{
                tabMio.className = 'flex-1 py-3 text-center border-b-2 border-orange-500 text-orange-600 bg-white font-black';
                tabReg.className = 'flex-1 py-3 text-center border-b-2 border-transparent text-slate-500 hover:text-slate-800';
                formMio.classList.remove('hidden');
                formReg.classList.add('hidden');
            }}
        }}

        function onRegionalZoneChange() {{
            const passInput = document.getElementById('reg-password-input');
            if (passInput) passInput.value = '';
            const zoneCode = document.getElementById('reg-zone-select').value;
            const regSel = document.getElementById('reg-region-select');
            regSel.innerHTML = '<option value="">-- Select Region --</option>';
            document.getElementById('reg-details-box').classList.add('hidden');

            if (!zoneCode) {{
                regSel.disabled = true;
                regSel.classList.add('bg-slate-100');
                return;
            }}

            const zoneObj = DB.zones.find(z => z.sap_zone_code === zoneCode);
            if (!zoneObj) return;

            regSel.disabled = false;
            regSel.classList.remove('bg-slate-100');

            zoneObj.regions.forEach(r => {{
                const opt = document.createElement('option');
                opt.value = r.region_name;
                opt.textContent = `${{r.region_name}} (${{r.sap_region_code}}) - Exium MUPS: ${{r.exium_count}} | Coralcal: ${{r.coral_count}}`;
                regSel.appendChild(opt);
            }});
        }}

        function onRegionalRegionChange() {{
            const passInput = document.getElementById('reg-password-input');
            if (passInput) passInput.value = '';
            const regName = document.getElementById('reg-region-select').value;
            const box = document.getElementById('reg-details-box');
            if (!regName || !DB.regions_map[regName]) {{
                box.classList.add('hidden');
                return;
            }}

            const r = DB.regions_map[regName];
            document.getElementById('disp-reg-head').textContent = r.regional_head || 'Not Assigned';
            document.getElementById('disp-reg-exium').textContent = `${{r.exium_count}} Achievers (Val: ${{(r.exium_value || 0).toLocaleString()}})`;
            document.getElementById('disp-reg-coral').textContent = `${{r.coral_count}} Achievers (Val: ${{(r.coral_value || 0).toLocaleString()}})`;
            box.classList.remove('hidden');
        }}

        function handleRegionalLogin(e) {{
            e.preventDefault();
            const regName = document.getElementById('reg-region-select').value;
            const pass = document.getElementById('reg-password-input').value.trim();

            if (!regName) {{
                alert('Please select a Region!');
                return;
            }}

            const r = DB.regions_map[regName];
            const expectedSap = String(r.sap_region_code).trim();

            if (pass !== expectedSap) {{
                alert('Invalid Region Password! Regional Head login strictly requires the SAP Region Code (' + expectedSap + ').');
                return;
            }}

            openRegionalView(regName);
        }}

        function setRegionalBrandFilter(mode) {{
            currentRegionalBrandFilter = mode;
            const btnAll = document.getElementById('reg-brand-tab-all');
            const btnEx = document.getElementById('reg-brand-tab-exium');
            const btnCo = document.getElementById('reg-brand-tab-coral');

            btnAll.className = mode === 'all'
                ? 'px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-extrabold bg-slate-900 text-white shadow-2xs transition'
                : 'px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-bold bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition';
            btnEx.className = mode === 'exium'
                ? 'px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-extrabold bg-blue-600 text-white shadow-sm ring-2 ring-blue-200 transition'
                : 'px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-extrabold bg-blue-50 text-blue-800 hover:bg-blue-100 border border-blue-200 transition';
            btnCo.className = mode === 'coral'
                ? 'px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-extrabold bg-purple-700 text-white shadow-sm ring-2 ring-purple-200 transition'
                : 'px-2.5 sm:px-3 py-1.5 rounded-xl text-[11px] sm:text-xs font-extrabold bg-purple-50 text-purple-800 hover:bg-purple-100 border border-purple-200 transition';

            renderAchievers();
        }}

        function setRegionalStatusFilter(status) {{
            currentRegionalStatusFilter = status;
            const pAll = document.getElementById('reg-status-pill-all');
            const pAch = document.getElementById('reg-status-pill-achievers');
            const pNon = document.getElementById('reg-status-pill-non_achievers');
            const pRev = document.getElementById('reg-status-pill-in_review');

            if (pAll) pAll.className = status === 'all'
                ? 'px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-black bg-slate-900 text-white shadow-2xs transition'
                : 'px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-bold bg-white text-slate-700 hover:bg-slate-100 border border-slate-300 transition';

            if (pAch) pAch.className = status === 'achievers'
                ? 'px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-black bg-emerald-600 text-white shadow-sm ring-2 ring-emerald-200 transition'
                : 'px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-bold bg-white text-emerald-800 hover:bg-emerald-50 border border-emerald-300 transition';

            if (pNon) pNon.className = status === 'non_achievers'
                ? 'px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-black bg-slate-600 text-white shadow-sm ring-2 ring-slate-200 transition'
                : 'px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-bold bg-white text-slate-700 hover:bg-slate-100 border border-slate-300 transition';

            if (pRev) pRev.className = status === 'in_review'
                ? 'px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-black bg-amber-600 text-white shadow-sm ring-2 ring-amber-200 transition'
                : 'px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-bold bg-white text-amber-800 hover:bg-amber-50 border border-amber-300 transition';

            renderAchievers();
        }}

        function openRegionalView(regName) {{
            currentRegionName = regName;
            const r = DB.regions_map[regName];

            localStorage.setItem(STORAGE_KEY_SESSION, JSON.stringify({{ region: regName }}));

            document.getElementById('login-view').classList.add('hidden');
            document.getElementById('zonal-view').classList.add('hidden');
            document.getElementById('regional-view').classList.remove('hidden');
            document.getElementById('sticky-bar').classList.remove('hidden');

            document.getElementById('regview-zone').textContent = r.zone_name;
            document.getElementById('regview-sap').textContent = `SAP: ${{r.sap_region_code}}`;
            document.getElementById('regview-name').textContent = r.region_name;
            document.getElementById('regview-rh').innerHTML = `Regional Head: <strong class="text-slate-900 font-bold">${{r.regional_head}}</strong>`;
            document.getElementById('regview-zh').innerHTML = `Zonal Head: <strong class="text-orange-700 font-bold">${{r.zonal_head}}</strong>`;
            document.getElementById('sticky-region-text').textContent = r.region_name;

            const filterInput = document.getElementById('reg-mio-filter-input');
            if (filterInput) filterInput.value = '';

            renderAchievers();
            updateRegionProgress();
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        function exitToLogin() {{
            localStorage.removeItem(STORAGE_KEY_SESSION);
            document.getElementById('regional-view').classList.add('hidden');
            document.getElementById('zonal-view').classList.add('hidden');
            document.getElementById('sticky-bar').classList.add('hidden');
            document.getElementById('login-view').classList.remove('hidden');
            currentRegionName = '';
            currentActiveZoneCode = '';
        }}

        // ALL TERRITORIES & MIOS IN REGION (ACHIEVERS + NON-ACHIEVERS)
        function getRegionMios(regName) {{
            const rawTerritories = DB.all_territories.filter(t => t.region_name === regName);

            const miosList = rawTerritories.map(t => {{
                const key = t.area_code + '_' + t.mio_id;
                const exId = `EXIUM_${{t.area_code}}_${{t.mio_id}}`;
                const coId = `CORAL_${{t.area_code}}_${{t.mio_id}}`;

                // Check manual overrides
                const exOverride = savedOverrides[exId];
                const coOverride = savedOverrides[coId];

                // Check review requests
                const exReview = savedReviews[`REV_${{exId}}`] || null;
                const coReview = savedReviews[`REV_${{coId}}`] || null;

                const exAwardVal = exOverride ? Number(exOverride.award) : Number(t.exium_award || 0);
                const exTierVal = exOverride ? exOverride.tier : (t.exium_tier || 'No Award');
                const exReasonVal = exOverride ? exOverride.reason : (t.exium_reason || '');

                const coAwardVal = coOverride ? Number(coOverride.award) : Number(t.coral_award || 0);
                const coTierVal = coOverride ? coOverride.tier : (t.coral_tier || 'No Award');
                const coReasonVal = coOverride ? coOverride.reason : (t.coral_reason || '');

                const exium_award = {{
                    id: exId,
                    brand: 'Exium_2026',
                    brand_short: 'Exium MUPS',
                    brand_label: 'Exium MUPS',
                    brand_tp: 659.67,
                    zone: t.zone_name,
                    sap_zone_code: t.sap_zone_code,
                    zonal_head: t.zonal_head,
                    region: t.region_name,
                    sap_region_code: t.sap_region_code,
                    regional_head: t.regional_head,
                    area_code: t.area_code,
                    area_name: t.area_name,
                    mio_code: t.mio_id,
                    mio_name: t.mio_name,
                    desig: t.desig,
                    mobile: t.mobile,
                    rx: t.exium_rx,
                    rx_ok: t.exium_rx_ok,
                    terr_aug: t.terr_aug_val,
                    terr_sep: t.terr_sep_val,
                    terr_growth: t.terr_growth_val,
                    terr_pos: t.terr_pos,
                    brand_aug: t.exium_aug_val,
                    brand_req_growth: t.exium_req_growth,
                    brand_req_target: t.exium_req_target,
                    brand_sep: t.exium_sep_val,
                    brand_actual_growth: t.exium_actual_growth,
                    brand_aug_box: t.exium_aug_box,
                    brand_sep_box: t.exium_sep_box,
                    brand_req_box: t.exium_req_box,
                    brand_growth_box: t.exium_growth_box,
                    brand_growth_ok: t.exium_growth_ok,
                    award: exAwardVal,
                    tier: exTierVal,
                    reason: exReasonVal,
                    is_manual_override: Boolean(exOverride),
                    override_info: exOverride,
                    review_info: exReview
                }};

                const coral_award = {{
                    id: coId,
                    brand: 'Coralcal_2026',
                    brand_short: 'Coralcal-D/DX/Vita',
                    brand_label: 'Coralcal-D/DX/Vita',
                    brand_tp: 637.18,
                    zone: t.zone_name,
                    sap_zone_code: t.sap_zone_code,
                    zonal_head: t.zonal_head,
                    region: t.region_name,
                    sap_region_code: t.sap_region_code,
                    regional_head: t.regional_head,
                    area_code: t.area_code,
                    area_name: t.area_name,
                    mio_code: t.mio_id,
                    mio_name: t.mio_name,
                    desig: t.desig,
                    mobile: t.mobile,
                    rx: t.coral_rx,
                    rx_ok: t.coral_rx_ok,
                    terr_aug: t.terr_aug_val,
                    terr_sep: t.terr_sep_val,
                    terr_growth: t.terr_growth_val,
                    terr_pos: t.terr_pos,
                    brand_aug: t.coral_aug_val,
                    brand_req_growth: t.coral_req_growth,
                    brand_req_target: t.coral_req_target,
                    brand_sep: t.coral_sep_val,
                    brand_actual_growth: t.coral_actual_growth,
                    brand_aug_box: t.coral_aug_box,
                    brand_sep_box: t.coral_sep_box,
                    brand_req_box: t.coral_req_box,
                    brand_growth_box: t.coral_growth_box,
                    brand_growth_ok: t.coral_growth_ok,
                    award: coAwardVal,
                    tier: coTierVal,
                    reason: coReasonVal,
                    is_manual_override: Boolean(coOverride),
                    override_info: coOverride,
                    review_info: coReview
                }};

                return {{
                    key: key,
                    mio_name: t.mio_name,
                    mio_code: t.mio_id,
                    area_code: t.area_code,
                    area_name: t.area_name,
                    desig: t.desig,
                    mobile: t.mobile,
                    region: t.region_name,
                    zone: t.zone_name,
                    exium_award: exium_award,
                    coral_award: coral_award
                }};
            }});

            return miosList.sort((a, b) => String(a.area_code || '').localeCompare(String(b.area_code || '')));
        }}

        function getMioStatus(mio) {{
            let eligibleBrands = 0;
            let completedBrands = 0;
            let isAchiever = false;
            let hasPendingReview = false;

            if (mio.exium_award && (currentRegionalBrandFilter === 'all' || currentRegionalBrandFilter === 'exium')) {{
                if (mio.exium_award.award > 0) {{
                    eligibleBrands++;
                    isAchiever = true;
                    if (isAwardResolved(mio.exium_award.id)) completedBrands++;
                }}
                if (mio.exium_award.review_info && mio.exium_award.review_info.status === 'pending') {{
                    hasPendingReview = true;
                }}
            }}
            if (mio.coral_award && (currentRegionalBrandFilter === 'all' || currentRegionalBrandFilter === 'coral')) {{
                if (mio.coral_award.award > 0) {{
                    eligibleBrands++;
                    isAchiever = true;
                    if (isAwardResolved(mio.coral_award.id)) completedBrands++;
                }}
                if (mio.coral_award.review_info && mio.coral_award.review_info.status === 'pending') {{
                    hasPendingReview = true;
                }}
            }}

            const isComplete = (eligibleBrands > 0 && completedBrands === eligibleBrands);
            return {{
                eligibleBrands,
                completedBrands,
                isAchiever,
                isNonAchiever: !isAchiever,
                hasPendingReview,
                isComplete
            }};
        }}

        // RENDER INDIVIDUAL BRAND AWARD BOX (HIGHLIGHTED BLUE FOR EXIUM MUPS, HIGHLIGHTED PURPLE FOR CORALCAL, RATIONAL PROPORTIONS)
        function renderBrandAwardBox(ach, brandKey) {{
            const isExium = (brandKey === 'Exium_2026');
            const choiceObj = savedChoices[ach.id] || {{}};
            const chosenVoucher = choiceObj.voucher || '';
            const isCancelled = Boolean(choiceObj.cancelled);
            const isCompleted = Boolean(chosenVoucher);
            const tsFormatted = choiceObj.timestamp ? formatToBDTime(choiceObj.timestamp) : '';

            const themeBorder = isCancelled
                ? 'border-rose-300 bg-rose-50/40'
                : (isExium ? 'border-blue-300 bg-gradient-to-br from-blue-50/60 via-white to-blue-50/25' : 'border-purple-300 bg-gradient-to-br from-purple-50/60 via-white to-purple-50/25');
            const badgeBrand = isExium
                ? 'bg-gradient-to-r from-blue-700 to-blue-600 text-white ring-1 ring-blue-300 shadow-2xs'
                : 'bg-gradient-to-r from-purple-800 to-purple-700 text-white ring-1 ring-purple-300 shadow-2xs';
            const badgeValue = isExium
                ? 'bg-blue-50 text-blue-900 border border-blue-300'
                : 'bg-purple-50 text-purple-900 border border-purple-300';
            const brandIcon = isExium ? '🟦' : '🟪';
            const brandTitle = isExium ? 'Exium MUPS Award' : 'Coralcal-D/DX/Vita Award';

            let selectionStatusHtml = '';
            if (isCancelled) {{
                selectionStatusHtml = `
                    <div class="flex items-center gap-1.5 flex-wrap w-full sm:w-auto">
                        <span class="text-[11px] sm:text-xs font-extrabold text-rose-800 bg-rose-100 border border-rose-300 px-2.5 py-1 rounded-lg flex items-center gap-1 shadow-2xs">
                            <span>🚫</span>
                            <span>Cancelled by ${{choiceObj.cancelled_by || 'RH/ZH'}}</span>
                        </span>
                        ${{!isSubmissionsLocked ? `
                            <button onclick="restoreCancelledAward('${{ach.id}}')" class="text-[11px] font-bold text-emerald-700 hover:text-white bg-emerald-50 hover:bg-emerald-600 border border-emerald-300 px-2.5 py-1 rounded-lg transition shadow-2xs">
                                ↩️ Restore Award
                            </button>
                        ` : ''}}
                    </div>
                `;
            }} else if (isCompleted) {{
                selectionStatusHtml = `
                    <div class="flex items-center gap-1.5 flex-wrap w-full sm:w-auto">
                        <span class="text-[11px] sm:text-xs font-extrabold text-emerald-800 bg-emerald-100/90 border border-emerald-300 px-2.5 py-1 rounded-lg flex items-center gap-1 shadow-2xs max-w-full">
                            <span>✓</span>
                            <span class="truncate">Selected: <strong>${{chosenVoucher}}</strong></span>
                            ${{tsFormatted ? `<span class="text-[10px] font-medium text-emerald-700 font-mono ml-0.5 hidden sm:inline">(${{tsFormatted}})</span>` : ''}}
                        </span>
                        ${{!isSubmissionsLocked ? `
                            <button onclick="removeVoucher('${{ach.id}}')" title="Remove / Clear this voucher choice" class="text-[11px] font-bold text-rose-700 hover:text-white bg-rose-50 hover:bg-rose-600 border border-rose-200 hover:border-rose-600 px-2 py-1 rounded-lg transition flex items-center gap-1 shadow-2xs">
                                <span>✕ Remove</span>
                            </button>
                            <button onclick="openCancelModal('${{ach.id}}')" title="Regional / Zonal Head: Cancel this Award with Reason" class="text-[11px] font-bold text-slate-600 hover:text-rose-700 bg-white hover:bg-rose-50 border border-slate-300 hover:border-rose-300 px-2 py-1 rounded-lg transition">
                                🚫 Cancel Award
                            </button>
                        ` : ''}}
                    </div>
                `;
            }} else {{
                selectionStatusHtml = `
                    <div class="flex items-center gap-1.5 flex-wrap w-full sm:w-auto">
                        <span class="text-[11px] sm:text-xs font-bold text-amber-800 bg-amber-50 border border-amber-200 px-2.5 py-1 rounded-lg flex items-center gap-1">
                            <span>⏳</span>
                            <span>Selection Pending</span>
                        </span>
                        ${{!isSubmissionsLocked ? `
                            <button onclick="openCancelModal('${{ach.id}}')" title="Regional / Zonal Head: Cancel this Award with Reason" class="text-[11px] font-bold text-rose-700 hover:text-white bg-rose-50 hover:bg-rose-600 border border-rose-200 hover:border-rose-600 px-2.5 py-1 rounded-lg transition flex items-center gap-1 shadow-2xs">
                                <span>🚫 Cancel Award (Not Recommended)</span>
                            </button>
                        ` : ''}}
                    </div>
                `;
            }}

            // Clear & Visible Calculation Metrics Bar with Aug'26 and Sep'26 Sales Value & Box Qty
            const tpVal = Number(ach.brand_tp || (isExium ? 659.67 : 637.18));
            const terrAugVal = Math.round(Number(ach.terr_aug || 0));
            const terrSepVal = Math.round(Number(ach.terr_sep || 0));
            const terrGrowthVal = Math.round(Number(ach.terr_growth || 0));
            const terrSign = terrGrowthVal > 0 ? '+' : '';

            const brandAugVal = Math.round(Number(ach.brand_aug || 0));
            const brandSepVal = Math.round(Number(ach.brand_sep || 0));
            const brandValGrowth = Math.round(Number(ach.brand_actual_growth || 0));
            const valSign = brandValGrowth >= 0 ? '+' : '';

            const boxGrowth = Number(ach.brand_growth_box ?? Math.round((ach.brand_actual_growth || 0) / tpVal));
            const brandAugBox = Number(ach.brand_aug_box ?? Math.round((ach.brand_aug || 0) / tpVal));
            const brandSepBox = Number(ach.brand_sep_box ?? (brandAugBox + boxGrowth));
            const reqBox = Number(ach.brand_req_box || 30);
            const boxSign = boxGrowth >= 0 ? '+' : '';
            const rxVal = Number(ach.rx || 0);
            const rxOk = rxVal >= 200;
            const brandDisplayTitle = isExium ? 'Exium MUPS' : 'Coralcal-D/DX/Vita';

            const metricsHtml = `
                <div class="grid grid-cols-1 md:grid-cols-3 gap-2 sm:gap-2.5 bg-white p-2 sm:p-3 rounded-xl border-2 ${{isExium ? 'border-blue-200' : 'border-purple-200'}} shadow-2xs">
                    <!-- 1. Seen Rx -->
                    <div class="min-w-0 overflow-hidden rounded-lg border ${{rxOk ? 'border-emerald-200 bg-emerald-50/50' : 'border-rose-200 bg-rose-50/50'}} p-2 sm:p-2.5 flex flex-col justify-between">
                        <div class="flex items-center justify-between gap-1">
                            <span class="text-slate-900 font-black uppercase text-[11px] sm:text-xs tracking-tight whitespace-nowrap">1. Seen Rx (Sep'26)</span>
                            <span class="px-1.5 py-0.5 rounded text-[10px] font-extrabold whitespace-nowrap ${{rxOk ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-rose-100 text-rose-800 border border-rose-300'}}">
                                ${{rxOk ? '✓ &ge;200 Rx' : '✗ &lt;200 Rx (No Award)'}}
                            </span>
                        </div>
                        <div class="mt-1 sm:mt-1.5 flex items-baseline gap-1.5 flex-wrap">
                            <span class="text-sm sm:text-base font-black ${{rxOk ? 'text-emerald-700' : 'text-rose-600'}}">
                                ${{rxOk ? '✓' : '✗'}} ${{rxVal.toLocaleString()}} Seen Rx
                            </span>
                            <span class="text-[11px] font-bold ${{rxOk ? 'text-slate-600' : 'text-rose-700'}}">(Req: &ge;200 Rx)</span>
                        </div>
                        <div class="mt-1 text-[11px] font-bold text-slate-700 bg-white/90 px-2 py-0.5 rounded border ${{rxOk ? 'border-emerald-200/80' : 'border-rose-200/80'}} flex items-center justify-between gap-1 flex-wrap">
                            <span>Sep'26 Full Month Rx: <strong class="${{rxOk ? 'text-slate-900' : 'text-rose-700 font-mono'}}">${{rxVal.toLocaleString()}}</strong></span>
                            ${{!rxOk ? '<span class="text-[10px] font-extrabold text-rose-600 uppercase">✗ Criteria Failed</span>' : ''}}
                        </div>
                    </div>

                    <!-- 2. Territory Sales Growth -->
                    <div class="min-w-0 overflow-hidden rounded-lg border ${{ach.terr_pos ? 'border-emerald-200 bg-emerald-50/40' : 'border-rose-200 bg-rose-50/40'}} p-2 sm:p-2.5 flex flex-col justify-between">
                        <div class="flex items-center justify-between gap-1">
                            <span class="text-slate-900 font-black uppercase text-[11px] sm:text-xs tracking-tight whitespace-nowrap truncate">2. Territory Sales Growth</span>
                            <span class="px-1.5 py-0.5 rounded text-[10px] font-extrabold whitespace-nowrap ${{ach.terr_pos ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-rose-100 text-rose-800 border border-rose-300'}}">
                                ${{ach.terr_pos ? '✓ Positive' : '✗ Negative'}}
                            </span>
                        </div>
                        <div class="mt-1 sm:mt-1.5">
                            <span class="text-sm sm:text-base font-black ${{ach.terr_pos ? 'text-emerald-700' : 'text-rose-600'}}">
                                ${{ach.terr_pos ? '✓' : '✗'}} Growth: ${{terrSign}}${{terrGrowthVal.toLocaleString()}} <span class="text-[11px] font-bold text-slate-600">(Val)</span>
                            </span>
                        </div>
                        <div class="mt-1 text-[11px] font-bold text-slate-700 bg-white/90 px-2 py-0.5 rounded border border-slate-200 flex items-center justify-between gap-1 flex-wrap">
                            <span>Aug'26: <strong class="text-slate-900 font-mono">${{terrAugVal.toLocaleString()}}</strong></span>
                            <span class="text-slate-400">➔</span>
                            <span>Sep'26: <strong class="text-slate-900 font-mono">${{terrSepVal.toLocaleString()}}</strong></span>
                        </div>
                    </div>

                    <!-- 3. Brand Growth (Exium MUPS / Coralcal-D/DX/Vita) -->
                    <div class="min-w-0 overflow-hidden rounded-lg border ${{isExium ? 'border-blue-200 bg-blue-50/50' : 'border-purple-200 bg-purple-50/50'}} p-2 sm:p-2.5 flex flex-col justify-between">
                        <div class="flex items-center justify-between gap-1">
                            <span class="${{isExium ? 'text-blue-950' : 'text-purple-950'}} font-black uppercase text-[11px] sm:text-xs tracking-tight whitespace-nowrap truncate">3. ${{brandDisplayTitle}} Growth</span>
                            <span class="px-1.5 py-0.5 rounded text-[10px] font-extrabold whitespace-nowrap ${{ach.brand_growth_ok ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-amber-100 text-amber-800 border border-amber-300'}}">
                                Req: +${{reqBox}} Boxes
                            </span>
                        </div>
                        <div class="mt-1 sm:mt-1.5 flex items-baseline justify-between gap-1 flex-wrap">
                            <span class="text-sm sm:text-base font-black ${{ach.brand_growth_ok ? 'text-emerald-700' : 'text-amber-700'}}">
                                ${{ach.brand_growth_ok ? '✓' : '✗'}} ${{boxSign}}${{boxGrowth.toLocaleString()}} Boxes
                            </span>
                            <span class="text-[11px] font-extrabold text-slate-700 font-mono">
                                (Val: ${{valSign}}${{brandValGrowth.toLocaleString()}})
                            </span>
                        </div>
                        <div class="mt-1 space-y-0.5 text-[11px] font-bold text-slate-700 bg-white/95 px-2 py-1 rounded border ${{isExium ? 'border-blue-200/80' : 'border-purple-200/80'}}">
                            <div class="flex items-center justify-between gap-1 flex-wrap">
                                <span>Qty: Aug <strong class="text-slate-900 font-mono">${{brandAugBox.toLocaleString()}}</strong> Box</span>
                                <span class="text-slate-400">➔</span>
                                <span>Sep <strong class="text-slate-900 font-mono">${{brandSepBox.toLocaleString()}}</strong> Box</span>
                            </div>
                            <div class="flex items-center justify-between gap-1 flex-wrap text-[10px] text-slate-600 border-t border-slate-100 pt-0.5">
                                <span>Val: Aug <strong class="text-slate-800 font-mono">${{brandAugVal.toLocaleString()}}</strong></span>
                                <span class="text-slate-400">➔</span>
                                <span>Sep <strong class="text-slate-800 font-mono">${{brandSepVal.toLocaleString()}}</strong></span>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            const rev = ach.review_info || savedReviews[`REV_${{ach.id}}`];
            const isPending = rev && rev.status === 'pending';
            const isRejected = rev && rev.status === 'rejected';
            const isApproved = rev && rev.status === 'approved';

            let revActionHtml = '';
            if (isPending) {{
                revActionHtml = `
                    <div class="flex items-center gap-1.5 flex-wrap">
                        <span class="px-2 sm:px-2.5 py-1 rounded-lg text-[10px] sm:text-[11px] font-black bg-amber-100 text-amber-900 border border-amber-300 shadow-2xs flex items-center gap-1 whitespace-nowrap">
                            <span>🔍</span>
                            <span>Review Requested (${{formatToBDTime(rev.timestamp || '')}})</span>
                        </span>
                        <button onclick="openReviewModal('${{ach.id}}')" class="text-[10px] sm:text-[11px] font-bold text-amber-800 hover:text-white bg-white hover:bg-amber-600 border border-amber-300 px-2 sm:px-2.5 py-1 rounded-lg transition shadow-2xs whitespace-nowrap">
                            View / Update Dispute
                        </button>
                    </div>
                `;
            }} else if (isRejected) {{
                revActionHtml = `
                    <div class="flex items-center gap-1.5 flex-wrap">
                        <span class="px-2 sm:px-2.5 py-1 rounded-lg text-[10px] sm:text-[11px] font-black bg-rose-100 text-rose-900 border border-rose-300 shadow-2xs flex items-center gap-1 whitespace-nowrap">
                            <span>❌</span>
                            <span>Review Rejected</span>
                        </span>
                        <button onclick="openReviewModal('${{ach.id}}')" class="text-[10px] sm:text-[11px] font-bold text-slate-700 hover:text-white bg-white hover:bg-slate-700 border border-slate-300 px-2 sm:px-2.5 py-1 rounded-lg transition shadow-2xs whitespace-nowrap">
                            Re-Submit Review (RH/ZH)
                        </button>
                    </div>
                `;
            }} else if (isApproved) {{
                revActionHtml = `
                    <span class="px-2 sm:px-2.5 py-1 rounded-lg text-[10px] sm:text-[11px] font-black bg-emerald-100 text-emerald-900 border border-emerald-300 shadow-2xs flex items-center gap-1 whitespace-nowrap">
                        <span>✅</span>
                        <span>Review Approved (${{rev.granted_award || 3000}})</span>
                    </span>
                `;
            }} else {{
                revActionHtml = `
                    <button onclick="openReviewModal('${{ach.id}}')" title="If there is a data discrepancy in Seen Rx, sales, or award tier, submit a review request for Admin verification" class="px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-xl text-[11px] sm:text-xs font-black bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 shadow-2xs transition flex items-center gap-1 whitespace-nowrap">
                        <span>📝</span>
                        <span>Request Data Review</span>
                    </button>
                `;
            }}

            if (Number(ach.award) === 0) {{
                return `
                    <div class="rounded-xl border-2 border-slate-200 bg-slate-50/60 p-2.5 sm:p-3.5 space-y-2.5 overflow-hidden">
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200/80 pb-2">
                            <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap min-w-0">
                                <span class="px-2.5 sm:px-3 py-1 rounded-lg text-xs sm:text-[13px] font-extrabold ${{badgeBrand}} opacity-85 whitespace-nowrap">
                                    ${{brandIcon}} ${{brandTitle}}
                                </span>
                                <span class="px-2 sm:px-2.5 py-1 rounded-lg text-xs sm:text-[13px] font-black bg-slate-200 text-slate-700 border border-slate-300 whitespace-nowrap">
                                    ⚪ No Award (0 Taka)
                                </span>
                                <span class="text-[11px] text-slate-500 font-semibold truncate">
                                    (${{ach.tier || 'Criteria Not Met'}})
                                </span>
                            </div>
                            <div class="w-full sm:w-auto flex items-center justify-end">
                                ${{revActionHtml}}
                            </div>
                        </div>

                        ${{metricsHtml}}

                        <!-- Discrepancy / Review Guidance Banner -->
                        <div class="bg-white border border-slate-200 rounded-xl p-2.5 text-xs text-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                            <div class="space-y-0.5 min-w-0">
                                <div class="font-black text-slate-900 flex items-center gap-1">
                                    <span>⚠️</span>
                                    <span>Award Calculation Criteria Status:</span>
                                    <span class="text-rose-700 font-bold">${{ach.reason || 'Criteria not fulfilled'}}</span>
                                </div>
                                <div class="text-[11px] text-slate-500">
                                    If this MIO's prescriptions or territory sales were recorded incorrectly (e.g. offline prescriptions, transfer, joining), Regional Head or Zonal Head can click <strong>Request Data Review</strong> to submit for Admin verification.
                                </div>
                            </div>
                            ${{isPending ? `
                                <div class="bg-amber-50 text-amber-900 border border-amber-200 px-2.5 py-1 rounded-lg text-[11px] font-bold self-start sm:self-center whitespace-nowrap">
                                    Dispute logged by ${{rev.submitter_role || 'RH'}}: "${{rev.dispute_category}}"
                                </div>
                            ` : ''}}
                        </div>
                    </div>
                `;
            }}

            if (isCancelled) {{
                return `
                    <div class="rounded-xl border-2 ${{themeBorder}} p-2.5 sm:p-3.5 space-y-2.5 overflow-hidden">
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-rose-200/80 pb-2">
                            <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap min-w-0">
                                <span class="px-2.5 sm:px-3 py-1 rounded-lg text-xs sm:text-[13px] font-extrabold ${{badgeBrand}} opacity-75 whitespace-nowrap">
                                    ${{brandIcon}} ${{brandTitle}}
                                </span>
                                <span class="px-2 sm:px-2.5 py-1 rounded-lg text-xs sm:text-[13px] font-black border bg-rose-100 text-rose-900 border-rose-300 line-through whitespace-nowrap">
                                    🏆 Award: ${{Number(ach.award).toLocaleString()}}
                                </span>
                                <span class="text-[10px] sm:text-[11px] font-black text-rose-700 uppercase bg-rose-100 px-2 py-0.5 rounded border border-rose-200 whitespace-nowrap">AWARD CANCELLED</span>
                            </div>
                            <div class="flex items-center gap-2 flex-wrap self-start sm:self-center">
                                ${{revActionHtml}}
                                ${{selectionStatusHtml}}
                            </div>
                        </div>
                        ${{metricsHtml}}
                        <div class="bg-rose-100/80 border border-rose-300 rounded-xl p-2.5 text-xs text-rose-950 flex items-start gap-2">
                            <span class="text-sm">📝</span>
                            <div class="min-w-0">
                                <div class="font-black">Cancellation Reason (${{choiceObj.cancelled_by || 'Regional/Zonal Head'}}):</div>
                                <div class="text-rose-900 font-semibold mt-0.5 break-words">"${{choiceObj.cancel_reason || 'Not Recommended'}}"</div>
                                ${{tsFormatted ? `<div class="text-[10px] text-rose-700 font-mono mt-0.5">Recorded: ${{tsFormatted}}</div>` : ''}}
                            </div>
                        </div>
                    </div>
                `;
            }}

            const brandsGrid = BRANDS.map(b => {{
                const isSelected = (chosenVoucher === b.name);
                const clickTooltip = isSubmissionsLocked ? '🔒 Submissions are currently locked by Administrator' : (isSelected ? 'Click to Deselect / Remove Choice' : 'Click to Select ' + b.name);
                return `
                    <div onclick="selectVoucher('${{ach.id}}', '${{b.name}}')" 
                         title="${{clickTooltip}}"
                         class="brand-card min-w-0 overflow-hidden ${{isSubmissionsLocked ? 'cursor-not-allowed opacity-90' : 'cursor-pointer'}} rounded-xl border-2 p-2 sm:p-2.5 flex flex-col justify-between relative transition-all ${{
                             isSelected ? 'selected ring-2 ring-emerald-500 ring-offset-1 bg-white shadow-xs' : 'border-slate-200 hover:border-slate-300 bg-white'
                         }}">
                        <div class="flex items-center justify-between mb-1.5 gap-1">
                            <div class="h-7 sm:h-8 w-20 sm:w-24 flex items-center min-w-0">
                                <img src="${{b.logo}}" alt="${{b.name}}" class="max-h-7 sm:max-h-8 max-w-full object-contain">
                            </div>
                            <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${{
                                isSelected ? 'border-emerald-600 bg-emerald-600 text-white shadow-2xs' : 'border-slate-300 bg-slate-50'
                            }}">
                                ${{isSelected ? '<svg class="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>' : ''}}
                            </div>
                        </div>
                        <div class="min-w-0">
                            <div class="text-xs font-extrabold text-slate-900 tracking-tight leading-tight truncate">${{b.name.replace(' Gift Voucher', '')}}</div>
                            <div class="text-[10px] text-slate-500 font-medium truncate mt-0.5">${{b.subtitle}}</div>
                        </div>
                        ${{isSelected ? `
                            <div class="mt-1.5 pt-1 border-t border-emerald-100 flex items-center justify-between text-[10px] text-emerald-800 font-black">
                                <span>✓ Selected</span>
                                ${{isSubmissionsLocked ? '<span class="text-slate-400">🔒 Locked</span>' : '<span class="text-rose-600 hover:underline">✕ Deselect</span>'}}
                            </div>
                        ` : ''}}
                    </div>
                `;
            }}).join('');

            return `
                <div class="rounded-xl border-2 ${{themeBorder}} p-2.5 sm:p-3.5 space-y-2.5 overflow-hidden">
                    <!-- Brand Heading on 1st Line, Selection/Cancel Options Below on Mobile -->
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b ${{isExium ? 'border-blue-200/80' : 'border-purple-200/80'}} pb-2">
                        <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap min-w-0">
                            <span class="px-2.5 sm:px-3 py-1 rounded-lg text-xs sm:text-[13px] font-extrabold ${{badgeBrand}} whitespace-nowrap">
                                ${{brandIcon}} ${{brandTitle}}
                            </span>
                            <span class="px-2 sm:px-2.5 py-1 rounded-lg text-xs sm:text-[13px] font-black ${{badgeValue}} whitespace-nowrap">
                                🏆 Award: ${{Number(ach.award).toLocaleString()}}
                            </span>
                            ${{ach.is_manual_override ? `
                                <span class="px-2 py-0.5 rounded text-[10px] sm:text-[11px] font-black bg-amber-100 text-amber-900 border border-amber-300 whitespace-nowrap shadow-2xs">
                                    ✨ Admin Manual Grant (${{ach.override_info && ach.override_info.reason ? ach.override_info.reason : 'Verified'}})
                                </span>
                            ` : ''}}
                            <span class="text-[11px] text-slate-600 font-semibold truncate">
                                (${{ach.tier}})
                            </span>
                        </div>
                        <div class="flex items-center gap-2 flex-wrap self-start sm:self-center">
                            ${{revActionHtml}}
                            ${{selectionStatusHtml}}
                        </div>
                    </div>

                    ${{metricsHtml}}

                    <!-- 6 Brand Options Grid -->
                    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                        ${{brandsGrid}}
                    </div>
                </div>
            `;
        }}

        // RENDER ACHIEVERS WITH SEPARATE EXIUM MUPS & CORALCAL BADGES AND BOXES (RATIONAL PROPORTIONS)
        function renderAchievers() {{
            const container = document.getElementById('regview-achievers-container');
            container.innerHTML = '';

            let mios = getRegionMios(currentRegionName);

            // Update status counts on the filter pills
            const totalCount = mios.length;
            let achCount = 0;
            let inRevCount = 0;
            mios.forEach(m => {{
                const st = getMioStatus(m);
                if (st.isAchiever) achCount++;
                if (st.hasPendingReview) inRevCount++;
            }});
            const nonAchCount = totalCount - achCount;

            const elAll = document.getElementById('reg-count-all');
            const elAch = document.getElementById('reg-count-achievers');
            const elNon = document.getElementById('reg-count-nonachievers');
            const elRev = document.getElementById('reg-count-inreview');
            if (elAll) elAll.textContent = totalCount;
            if (elAch) elAch.textContent = achCount;
            if (elNon) elNon.textContent = nonAchCount;
            if (elRev) elRev.textContent = inRevCount;

            // Apply Status Filter ('all' | 'achievers' | 'non_achievers' | 'in_review')
            if (currentRegionalStatusFilter === 'achievers') {{
                mios = mios.filter(m => getMioStatus(m).isAchiever);
            }} else if (currentRegionalStatusFilter === 'non_achievers') {{
                mios = mios.filter(m => getMioStatus(m).isNonAchiever);
            }} else if (currentRegionalStatusFilter === 'in_review') {{
                mios = mios.filter(m => getMioStatus(m).hasPendingReview);
            }}

            // Apply Brand Filter ('all' | 'exium' | 'coral')
            if (currentRegionalBrandFilter === 'exium') {{
                mios = mios.filter(m => Boolean(m.exium_award));
            }} else if (currentRegionalBrandFilter === 'coral') {{
                mios = mios.filter(m => Boolean(m.coral_award));
            }}

            // Apply Search Query Filter
            const filterInput = document.getElementById('reg-mio-filter-input');
            const q = (filterInput ? filterInput.value : '').trim().toLowerCase();
            if (q) {{
                mios = mios.filter(m => 
                    String(m.mio_name || '').toLowerCase().includes(q) ||
                    String(m.mio_code || '').toLowerCase().includes(q) ||
                    String(m.area_name || '').toLowerCase().includes(q) ||
                    String(m.area_code || '').toLowerCase().includes(q)
                );
            }}

            if (mios.length === 0) {{
                container.innerHTML = `
                    <div class="bg-white rounded-2xl p-10 text-center border border-slate-200 text-slate-400">
                        <span class="text-3xl">📭</span>
                        <h4 class="font-bold text-sm text-slate-700 mt-2">No matching Territory or MIO found</h4>
                        <p class="text-xs text-slate-500 mt-1">Try switching the Brand / Status Filter tab or clearing the search box.</p>
                    </div>
                `;
                return;
            }}

            mios.forEach((mio, mioIdx) => {{
                const status = getMioStatus(mio);
                const theme = MIO_COLOR_PALETTES[mioIdx % MIO_COLOR_PALETTES.length];

                const showExium = mio.exium_award && (currentRegionalBrandFilter === 'all' || currentRegionalBrandFilter === 'exium');
                const showCoral = mio.coral_award && (currentRegionalBrandFilter === 'all' || currentRegionalBrandFilter === 'coral');

                const card = document.createElement('div');
                card.id = `mio-card-${{mio.key}}`;
                card.className = `bg-white rounded-2xl shadow-xs border transition-all p-2.5 sm:p-4 space-y-3 overflow-hidden ${{
                    status.isComplete 
                        ? 'border-emerald-400 ring-1 ring-emerald-400/20 bg-emerald-50/5' 
                        : (status.completedBrands > 0 
                            ? 'border-amber-300 ring-1 ring-amber-300/20' 
                            : (status.hasPendingReview ? 'border-amber-400 ring-1 ring-amber-400/30 bg-amber-50/10' : (status.isAchiever ? 'border-blue-200' : 'border-slate-200')))
                }}`;

                let statusBadgeHtml = '';
                if (status.isComplete) {{
                    statusBadgeHtml = `
                        <span class="px-2.5 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1 shadow-2xs whitespace-nowrap">
                            <span>✓</span>
                            <span>Complete (${{status.completedBrands}}/${{status.eligibleBrands}})</span>
                        </span>
                    `;
                }} else if (status.completedBrands > 0) {{
                    statusBadgeHtml = `
                        <span class="px-2.5 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-extrabold bg-amber-100 text-amber-800 border border-amber-300 flex items-center gap-1 shadow-2xs whitespace-nowrap">
                            <span>⏳</span>
                            <span>${{status.completedBrands}}/${{status.eligibleBrands}} Complete</span>
                        </span>
                    `;
                }} else if (status.isAchiever) {{
                    statusBadgeHtml = `
                        <span class="px-2.5 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-bold bg-white/95 text-slate-700 border border-slate-300 flex items-center gap-1 shadow-2xs whitespace-nowrap">
                            <span>⚪</span>
                            <span>Pending (0/${{status.eligibleBrands}})</span>
                        </span>
                    `;
                }} else if (status.hasPendingReview) {{
                    statusBadgeHtml = `
                        <span class="px-2.5 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-black bg-amber-100 text-amber-900 border border-amber-300 flex items-center gap-1 shadow-2xs whitespace-nowrap">
                            <span>🔍</span>
                            <span>Review Requested</span>
                        </span>
                    `;
                }} else {{
                    statusBadgeHtml = `
                        <span class="px-2.5 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200 flex items-center gap-1 whitespace-nowrap">
                            <span>⚪</span>
                            <span>Non-Achiever</span>
                        </span>
                    `;
                }}

                // Separate Brand Value Badges in Card Header
                let brandBadgesHtml = '';
                if (showExium) {{
                    const exCancelled = isAwardCancelled(mio.exium_award.id);
                    const exAward = Number(mio.exium_award.award || 0);
                    const exInReview = mio.exium_award.review_info && mio.exium_award.review_info.status === 'pending';

                    if (exAward > 0) {{
                        brandBadgesHtml += `
                            <div class="px-2 sm:px-2.5 py-1 rounded-lg bg-blue-600 text-white border border-blue-500 shadow-2xs flex items-center gap-1 whitespace-nowrap">
                                <span class="text-[10px] sm:text-[11px] font-extrabold uppercase">🟦 Exium MUPS:</span>
                                <span class="text-[11px] sm:text-xs font-black ${{exCancelled ? 'line-through text-rose-200' : 'text-yellow-200'}} font-mono">${{exAward.toLocaleString()}}</span>
                            </div>
                        `;
                    }} else {{
                        brandBadgesHtml += `
                            <div class="px-2 sm:px-2.5 py-1 rounded-lg ${{exInReview ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-slate-100 text-slate-700 border border-slate-300'}} shadow-2xs flex items-center gap-1 whitespace-nowrap">
                                <span class="text-[10px] sm:text-[11px] font-extrabold uppercase">🟦 Exium MUPS:</span>
                                <span class="text-[11px] sm:text-xs font-bold font-mono">${{exInReview ? '🔍 In Review' : '0 (No Award)'}}</span>
                            </div>
                        `;
                    }}
                }}
                if (showCoral) {{
                    const coCancelled = isAwardCancelled(mio.coral_award.id);
                    const coAward = Number(mio.coral_award.award || 0);
                    const coInReview = mio.coral_award.review_info && mio.coral_award.review_info.status === 'pending';

                    if (coAward > 0) {{
                        brandBadgesHtml += `
                            <div class="px-2 sm:px-2.5 py-1 rounded-lg bg-purple-700 text-white border border-purple-600 shadow-2xs flex items-center gap-1 whitespace-nowrap">
                                <span class="text-[10px] sm:text-[11px] font-extrabold uppercase">🟪 Coralcal:</span>
                                <span class="text-[11px] sm:text-xs font-black ${{coCancelled ? 'line-through text-rose-200' : 'text-yellow-200'}} font-mono">${{coAward.toLocaleString()}}</span>
                            </div>
                        `;
                    }} else {{
                        brandBadgesHtml += `
                            <div class="px-2 sm:px-2.5 py-1 rounded-lg ${{coInReview ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-slate-100 text-slate-700 border border-slate-300'}} shadow-2xs flex items-center gap-1 whitespace-nowrap">
                                <span class="text-[10px] sm:text-[11px] font-extrabold uppercase">🟪 Coralcal:</span>
                                <span class="text-[11px] sm:text-xs font-bold font-mono">${{coInReview ? '🔍 In Review' : '0 (No Award)'}}</span>
                            </div>
                        `;
                    }}
                }}

                let headerHtml = `
                    <div class="rounded-xl border p-2.5 sm:p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 ${{theme.bg}} ${{theme.border}}">
                        <div class="space-y-1 min-w-0">
                            <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                                <span class="bg-orange-500 text-white text-[11px] sm:text-xs font-extrabold px-2 sm:px-2.5 py-0.5 rounded-lg flex items-center gap-1 shadow-2xs whitespace-nowrap">
                                    <span>📍</span>
                                    <span>${{mio.area_name}} (${{mio.area_code}})</span>
                                </span>
                                <h3 class="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight truncate max-w-full">
                                    ${{mio.mio_name}}
                                </h3>
                                <span class="bg-white text-blue-700 font-mono text-[11px] font-extrabold px-2 py-0.5 rounded border border-blue-200 shadow-2xs whitespace-nowrap">
                                    MIO: ${{mio.mio_code}}
                                </span>
                            </div>
                            <div class="flex items-center gap-2 text-[11px] text-slate-700 font-medium flex-wrap">
                                <span class="font-bold ${{theme.desigBg}} px-2 py-0.5 rounded text-[11px] border shadow-2xs">${{mio.desig || 'MIO'}}</span>
                                ${{mio.mobile ? `<span class="text-slate-400">•</span><span class="text-slate-600 font-mono text-[11px]">📞 ${{mio.mobile}}</span>` : ''}}
                            </div>
                        </div>

                        <div class="flex items-center gap-1.5 flex-shrink-0 self-start sm:self-center flex-wrap w-full sm:w-auto pt-1 sm:pt-0 border-t border-slate-200/50 sm:border-t-0">
                            ${{brandBadgesHtml}}
                            ${{statusBadgeHtml}}
                        </div>
                    </div>
                `;

                let awardBoxesHtml = '<div class="space-y-3">';
                if (showExium) {{
                    awardBoxesHtml += renderBrandAwardBox(mio.exium_award, 'Exium_2026');
                }}
                if (showCoral) {{
                    awardBoxesHtml += renderBrandAwardBox(mio.coral_award, 'Coralcal_2026');
                }}
                awardBoxesHtml += '</div>';

                card.innerHTML = headerHtml + awardBoxesHtml;
                container.appendChild(card);
            }});
        }}

        // ==============================================
        // VOUCHER SELECTION & RH/ZH CANCELLATION LOGIC
        // ==============================================
        function findAchieverById(achId) {{
            let found = DB.achievers_exium.find(x => x.id === achId) || DB.achievers_coral.find(x => x.id === achId);
            if (found) {{
                const ov = savedOverrides[achId];
                if (ov) {{
                    return Object.assign({{}}, found, {{
                        award: Number(ov.award),
                        tier: ov.tier || found.tier,
                        reason: ov.reason || found.reason,
                        is_manual_override: true,
                        override_info: ov
                    }});
                }}
                return found;
            }}

            // Fallback: search in DB.all_territories
            const isExium = String(achId).startsWith('EXIUM_');
            const parts = String(achId).split('_');
            const areaCode = parts[1];
            const mioId = parts.slice(2).join('_');
            const terr = DB.all_territories.find(t => String(t.area_code) === String(areaCode) && String(t.mio_id) === String(mioId));
            if (!terr) return null;

            const ov = savedOverrides[achId];
            if (isExium) {{
                return {{
                    id: achId,
                    brand: 'Exium_2026',
                    brand_short: 'Exium MUPS',
                    brand_label: 'Exium MUPS',
                    brand_tp: 659.67,
                    zone: terr.zone_name,
                    sap_zone_code: terr.sap_zone_code,
                    zonal_head: terr.zonal_head,
                    region: terr.region_name,
                    sap_region_code: terr.sap_region_code,
                    regional_head: terr.regional_head,
                    area_code: terr.area_code,
                    area_name: terr.area_name,
                    mio_code: terr.mio_id,
                    mio_name: terr.mio_name,
                    desig: terr.desig,
                    mobile: terr.mobile,
                    rx: terr.exium_rx,
                    rx_ok: terr.exium_rx_ok,
                    terr_aug: terr.terr_aug_val,
                    terr_sep: terr.terr_sep_val,
                    terr_growth: terr.terr_growth_val,
                    terr_pos: terr.terr_pos,
                    brand_aug: terr.exium_aug_val,
                    brand_req_growth: terr.exium_req_growth,
                    brand_req_target: terr.exium_req_target,
                    brand_sep: terr.exium_sep_val,
                    brand_actual_growth: terr.exium_actual_growth,
                    brand_aug_box: terr.exium_aug_box,
                    brand_sep_box: terr.exium_sep_box,
                    brand_req_box: terr.exium_req_box,
                    brand_growth_box: terr.exium_growth_box,
                    brand_growth_ok: terr.exium_growth_ok,
                    award: ov ? Number(ov.award) : Number(terr.exium_award || 0),
                    tier: ov ? ov.tier : terr.exium_tier,
                    reason: ov ? ov.reason : terr.exium_reason,
                    is_manual_override: Boolean(ov),
                    override_info: ov
                }};
            }} else {{
                return {{
                    id: achId,
                    brand: 'Coralcal_2026',
                    brand_short: 'Coralcal-D/DX/Vita',
                    brand_label: 'Coralcal-D/DX/Vita',
                    brand_tp: 637.18,
                    zone: terr.zone_name,
                    sap_zone_code: terr.sap_zone_code,
                    zonal_head: terr.zonal_head,
                    region: terr.region_name,
                    sap_region_code: terr.sap_region_code,
                    regional_head: terr.regional_head,
                    area_code: terr.area_code,
                    area_name: terr.area_name,
                    mio_code: terr.mio_id,
                    mio_name: terr.mio_name,
                    desig: terr.desig,
                    mobile: terr.mobile,
                    rx: terr.coral_rx,
                    rx_ok: terr.coral_rx_ok,
                    terr_aug: terr.terr_aug_val,
                    terr_sep: terr.terr_sep_val,
                    terr_growth: terr.terr_growth_val,
                    terr_pos: terr.terr_pos,
                    brand_aug: terr.coral_aug_val,
                    brand_req_growth: terr.coral_req_growth,
                    brand_req_target: terr.coral_req_target,
                    brand_sep: terr.coral_sep_val,
                    brand_actual_growth: terr.coral_actual_growth,
                    brand_aug_box: terr.coral_aug_box,
                    brand_sep_box: terr.coral_sep_box,
                    brand_req_box: terr.coral_req_box,
                    brand_growth_box: terr.coral_growth_box,
                    brand_growth_ok: terr.coral_growth_ok,
                    award: ov ? Number(ov.award) : Number(terr.coral_award || 0),
                    tier: ov ? ov.tier : terr.coral_tier,
                    reason: ov ? ov.reason : terr.coral_reason,
                    is_manual_override: Boolean(ov),
                    override_info: ov
                }};
            }}
        }}

        function selectVoucher(achId, voucherName) {{
            if (isSubmissionsLocked) {{
                alert('🔒 Voucher choice submissions are currently CLOSED by Administrator. Portal is in Read-Only mode.');
                return;
            }}

            if (savedChoices[achId] && savedChoices[achId].voucher === voucherName && !savedChoices[achId].cancelled) {{
                removeVoucher(achId);
                return;
            }}

            const a = findAchieverById(achId);
            if (!a) return;

            const bdTime = getBDTimestamp();
            savedChoices[achId] = {{
                voucher: voucherName,
                timestamp: bdTime,
                status: 'Complete',
                cancelled: false,
                cancelled_by: '',
                cancel_reason: ''
            }};

            localStorage.setItem(STORAGE_KEY_CHOICES, JSON.stringify(savedChoices));
            queueForUpload(achId, a.brand, a.area_code, a.mio_code, voucherName, bdTime, 'save', false, '', '');

            renderAchievers();
            updateRegionProgress();
            triggerDebouncedFlush();
            showToast(`Selected ${{voucherName}} (${{a.brand_short}})`, '✅');
        }}

        function removeVoucher(achId) {{
            if (isSubmissionsLocked) {{
                alert('🔒 Voucher choice submissions are currently CLOSED by Administrator.');
                return;
            }}
            if (!savedChoices[achId]) return;

            const a = findAchieverById(achId);
            if (!a) return;

            const oldVoucher = savedChoices[achId].voucher;
            const existingTimestamp = savedChoices[achId].timestamp || '';

            savedChoices[achId] = {{
                voucher: '',
                timestamp: existingTimestamp,
                status: 'Pending',
                cancelled: false,
                cancelled_by: '',
                cancel_reason: ''
            }};

            localStorage.setItem(STORAGE_KEY_CHOICES, JSON.stringify(savedChoices));
            queueForUpload(achId, a.brand, a.area_code, a.mio_code, '', existingTimestamp, 'remove', false, '', '');

            renderAchievers();
            updateRegionProgress();
            triggerDebouncedFlush();
            showToast(`Removed ${{oldVoucher || 'choice'}}`, '🗑️');
        }}

        function openCancelModal(achId) {{
            if (isSubmissionsLocked) {{
                alert('🔒 Submissions are currently locked by Administrator.');
                return;
            }}
            const a = findAchieverById(achId);
            if (!a) return;

            document.getElementById('cancel-ach-id').value = achId;
            document.getElementById('cancel-reason-input').value = (savedChoices[achId] && savedChoices[achId].cancel_reason) ? savedChoices[achId].cancel_reason : '';
            document.getElementById('cancel-mio-summary').innerHTML = `
                <div class="font-black text-slate-900">${{a.mio_name}} (MIO: ${{a.mio_code}})</div>
                <div>Territory: <strong>${{a.area_name}} (${{a.area_code}})</strong> • Region: <strong>${{a.region}}</strong></div>
                <div>Brand Award: <strong class="text-rose-700">${{a.brand_label}} — Award: ${{Number(a.award).toLocaleString()}}</strong></div>
            `;
            document.getElementById('cancel-modal').classList.remove('hidden');
        }}

        function closeCancelModal() {{
            document.getElementById('cancel-modal').classList.add('hidden');
        }}

        function confirmCancelAward(e) {{
            e.preventDefault();
            const achId = document.getElementById('cancel-ach-id').value;
            const cancelledBy = document.getElementById('cancel-by-select').value;
            const reason = document.getElementById('cancel-reason-input').value.trim();

            if (!reason) {{
                alert('Please write a reason for cancelling the award.');
                return;
            }}

            const a = findAchieverById(achId);
            if (!a) return;

            const bdTime = getBDTimestamp();
            savedChoices[achId] = {{
                voucher: '',
                timestamp: bdTime,
                status: 'Cancelled',
                cancelled: true,
                cancelled_by: cancelledBy,
                cancel_reason: reason
            }};

            localStorage.setItem(STORAGE_KEY_CHOICES, JSON.stringify(savedChoices));
            queueForUpload(achId, a.brand, a.area_code, a.mio_code, 'CANCELLED: ' + reason, bdTime, 'cancel', true, cancelledBy, reason);

            closeCancelModal();
            if (currentRegionName) {{
                renderAchievers();
                updateRegionProgress();
            }}
            if (isAdminUnlocked) {{
                refreshAdminStats();
            }}
            triggerDebouncedFlush();
            showToast(`Award Cancelled (${{a.brand_short}})`, '🚫');
        }}

        function restoreCancelledAward(achId) {{
            if (isSubmissionsLocked) {{
                alert('🔒 Submissions are currently locked by Administrator.');
                return;
            }}
            const a = findAchieverById(achId);
            if (!a) return;

            const bdTime = getBDTimestamp();
            savedChoices[achId] = {{
                voucher: '',
                timestamp: bdTime,
                status: 'Pending',
                cancelled: false,
                cancelled_by: '',
                cancel_reason: ''
            }};

            localStorage.setItem(STORAGE_KEY_CHOICES, JSON.stringify(savedChoices));
            queueForUpload(achId, a.brand, a.area_code, a.mio_code, '', bdTime, 'restore', false, '', '');

            if (currentRegionName) {{
                renderAchievers();
                updateRegionProgress();
            }}
            if (isAdminUnlocked) {{
                refreshAdminStats();
            }}
            triggerDebouncedFlush();
            showToast(`Award Restored to Pending (${{a.brand_short}})`, '↩️');
        }}

        function updateRegionProgress() {{
            const mios = getRegionMios(currentRegionName);
            let exTotal = 0, exDone = 0;
            let coTotal = 0, coDone = 0;
            let achCount = 0;
            let inRevCount = 0;

            mios.forEach(m => {{
                const st = getMioStatus(m);
                if (st.isAchiever) achCount++;
                if (st.hasPendingReview) inRevCount++;

                if (m.exium_award && m.exium_award.award > 0) {{
                    exTotal++;
                    if (isAwardResolved(m.exium_award.id)) exDone++;
                }}
                if (m.coral_award && m.coral_award.award > 0) {{
                    coTotal++;
                    if (isAwardResolved(m.coral_award.id)) coDone++;
                }}
            }});

            const elEx = document.getElementById('regview-exium-stat');
            const elCo = document.getElementById('regview-coral-stat');
            if (elEx) elEx.textContent = `${{exDone}} / ${{exTotal}} Done`;
            if (elCo) elCo.textContent = `${{coDone}} / ${{coTotal}} Done`;

            const totalAwards = exTotal + coTotal;
            const completedAwards = exDone + coDone;
            const pct = totalAwards > 0 ? Math.round((completedAwards / totalAwards) * 100) : 0;

            document.getElementById('regview-progress-pct').textContent = `${{pct}}%`;
            document.getElementById('regview-progress-bar').style.width = `${{pct}}%`;
            document.getElementById('regview-progress-count').textContent = `Exium MUPS: ${{exDone}}/${{exTotal}} • Coralcal: ${{coDone}}/${{coTotal}}`;
            document.getElementById('sticky-completed-text').textContent = `Exium MUPS: ${{exDone}}/${{exTotal}} | Coralcal: ${{coDone}}/${{coTotal}} (${{pct}}%)`;

            // Update pill counters
            const elAll = document.getElementById('reg-count-all');
            const elAch = document.getElementById('reg-count-achievers');
            const elNon = document.getElementById('reg-count-nonachievers');
            const elRev = document.getElementById('reg-count-inreview');
            if (elAll) elAll.textContent = mios.length;
            if (elAch) elAch.textContent = achCount;
            if (elNon) elNon.textContent = mios.length - achCount;
            if (elRev) elRev.textContent = inRevCount;
        }}

        // ==============================================
        // DATA REVIEW & MANUAL AWARD OVERRIDE LOGIC
        // ==============================================
        async function sendCloudReview(review) {{
            if (!cloudEndpoint) return;
            try {{
                await fetch(cloudEndpoint, {{
                    method: 'POST',
                    mode: 'no-cors',
                    headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
                    body: JSON.stringify({{ action: 'save_review', review: review }})
                }});
            }} catch (e) {{
                console.warn('Failed to send review to cloud', e);
            }}
        }}

        async function sendCloudOverride(override) {{
            if (!cloudEndpoint) return;
            try {{
                await fetch(cloudEndpoint, {{
                    method: 'POST',
                    mode: 'no-cors',
                    headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
                    body: JSON.stringify({{ action: 'save_manual_override', override: override }})
                }});
            }} catch (e) {{
                console.warn('Failed to send override to cloud', e);
            }}
        }}

        function openReviewModal(achId) {{
            const ach = findAchieverById(achId);
            if (!ach) {{
                alert('Territory details not found!');
                return;
            }}
            document.getElementById('rev-ach-id').value = achId;
            const revKey = 'REV_' + achId;
            const existingRev = savedReviews[revKey] || {{}};

            const isExium = ach.brand_short === 'Exium MUPS';
            const brandDisplay = isExium ? '🟦 Exium MUPS' : '🟪 Coralcal-D/DX/Vita';

            const summaryEl = document.getElementById('rev-mio-summary');
            summaryEl.innerHTML = `
                <div class="flex items-center justify-between gap-1 flex-wrap">
                    <span class="px-2 py-0.5 rounded text-[11px] font-black ${{isExium ? 'bg-blue-600 text-white' : 'bg-purple-700 text-white'}}">${{brandDisplay}}</span>
                    <span class="font-mono text-[11px] text-slate-500">${{ach.region}} • ${{ach.zone}}</span>
                </div>
                <div class="mt-1">
                    <span class="font-black text-slate-900 text-xs sm:text-sm">${{ach.mio_name}}</span>
                    <span class="text-slate-500 ml-1">(SAP: <strong>${{ach.mio_code}}</strong> • Area: <strong>${{ach.area_name}} [${{ach.area_code}}]</strong>)</span>
                </div>
                <div class="text-[11px] text-slate-600">
                    Designation: <strong>${{ach.desig || 'MIO'}}</strong> ${{ach.mobile ? `• Mobile: <strong class="font-mono">${{ach.mobile}}</strong>` : ''}}
                </div>
            `;

            const rxOk = Number(ach.rx || 0) >= 200;
            const metricsEl = document.getElementById('rev-metrics-summary');
            metricsEl.innerHTML = `
                <div class="font-bold text-[11px] text-amber-950 mb-1">Current Automated System Calculation:</div>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-1.5 text-[11px]">
                    <div class="${{rxOk ? 'bg-white/90 border-amber-200' : 'bg-rose-50 border-rose-300'}} p-1.5 rounded border">
                        <span class="text-slate-500 block text-[10px]">1. Seen Rx:</span>
                        <strong class="${{rxOk ? 'text-emerald-700' : 'text-rose-600'}}">${{rxOk ? '✓ ' + ach.rx : '✗ ' + ach.rx}} Rx</strong> (${{rxOk ? 'Req: &ge;200' : 'No Award (<200)'}})
                    </div>
                    <div class="${{ach.terr_pos ? 'bg-white/90 border-amber-200' : 'bg-rose-50 border-rose-300'}} p-1.5 rounded border">
                        <span class="text-slate-500 block text-[10px]">2. Territory Sales:</span>
                        <strong class="${{ach.terr_pos ? 'text-emerald-700' : 'text-rose-600'}}">${{ach.terr_pos ? 'Positive' : 'Negative'}}</strong> (${{Math.round(ach.terr_growth || 0).toLocaleString()}})
                    </div>
                    <div class="${{ach.brand_growth_ok ? 'bg-white/90 border-amber-200' : 'bg-amber-50 border-amber-300'}} p-1.5 rounded border">
                        <span class="text-slate-500 block text-[10px]">3. Brand Box Growth:</span>
                        <strong class="${{ach.brand_growth_ok ? 'text-emerald-700' : 'text-amber-700'}}">${{ach.brand_growth_box || 0}} Boxes</strong> (Req: +${{ach.brand_req_box || 30}})
                    </div>
                </div>
                <div class="mt-1 text-[11px] text-amber-950 font-semibold">
                    Current Award: <strong class="${{Number(ach.award || 0) > 0 ? 'text-emerald-700' : 'text-rose-700'}}">${{Number(ach.award || 0).toLocaleString()}} Taka (${{ach.reason || (Number(ach.award || 0) > 0 ? 'Eligible' : 'Criteria Not Met')}})</strong>
                </div>
            `;

            if (existingRev.dispute_category) {{
                document.getElementById('rev-category-select').value = existingRev.dispute_category;
            }}
            const defaultRole = currentActiveZoneCode ? 'Zonal Head' : 'Regional Head';
            document.getElementById('rev-role-select').value = existingRev.submitter_role || defaultRole;
            document.getElementById('rev-mobile-input').value = existingRev.contact_mobile || ach.mobile || '';
            const defaultName = (defaultRole === 'Zonal Head') ? (ach.zonal_head || '') : (ach.regional_head || '');
            document.getElementById('rev-name-input').value = existingRev.submitter_name || defaultName;

            document.getElementById('review-modal').classList.remove('hidden');
        }}

        function onRevRoleChange() {{
            const achId = document.getElementById('rev-ach-id').value;
            const ach = findAchieverById(achId);
            if (!ach) return;
            const role = document.getElementById('rev-role-select').value;
            if (role === 'Zonal Head') {{
                document.getElementById('rev-name-input').value = ach.zonal_head || '';
            }} else {{
                document.getElementById('rev-name-input').value = ach.regional_head || '';
            }}
        }}

        function closeReviewModal() {{
            document.getElementById('review-modal').classList.add('hidden');
        }}

        function submitReviewRequest(e) {{
            e.preventDefault();
            const achId = document.getElementById('rev-ach-id').value;
            const ach = findAchieverById(achId);
            if (!ach) return;

            const category = document.getElementById('rev-category-select').value;
            const role = document.getElementById('rev-role-select').value;
            const mobile = document.getElementById('rev-mobile-input').value.trim();
            const name = document.getElementById('rev-name-input').value.trim();

            if (role !== 'Regional Head' && role !== 'Zonal Head') {{
                alert('Data review request can only be submitted by Regional Head or Zonal Head.');
                return;
            }}

            const revKey = 'REV_' + achId;
            const reviewObj = {{
                id: revKey,
                ach_id: achId,
                area_code: ach.area_code,
                area_name: ach.area_name,
                mio_code: ach.mio_code,
                mio_name: ach.mio_name,
                desig: ach.desig,
                mobile: ach.mobile || mobile,
                region: ach.region,
                zone: ach.zone,
                brand: ach.brand,
                brand_label: ach.brand_label,
                dispute_category: category,
                remarks: category,
                submitter_role: role,
                submitter_name: name || role,
                contact_mobile: mobile,
                timestamp: new Date().toISOString(),
                status: 'pending'
            }};

            savedReviews[revKey] = reviewObj;
            localStorage.setItem(STORAGE_KEY_REVIEWS, JSON.stringify(savedReviews));

            sendCloudReview(reviewObj);

            closeReviewModal();
            renderAchievers();
            if (isAdminUnlocked) refreshAdminStats();
            showToast('Review request submitted by ' + role + '! Logged for Admin verification. 📤', '✅');
        }}

        function openManualOverrideModal(achId, prefillAward = 3000, prefillReason = '') {{
            const ach = findAchieverById(achId);
            if (!ach) {{
                alert('Territory not found!');
                return;
            }}
            document.getElementById('override-ach-id').value = achId;
            const existingOv = savedOverrides[achId] || {{}};

            const isExium = ach.brand_short === 'Exium MUPS';
            const brandDisplay = isExium ? '🟦 Exium MUPS' : '🟪 Coralcal-D/DX/Vita';

            const summaryEl = document.getElementById('override-mio-summary');
            summaryEl.innerHTML = `
                <div class="flex items-center justify-between gap-1 flex-wrap">
                    <span class="px-2 py-0.5 rounded text-[11px] font-black ${{isExium ? 'bg-blue-600 text-white' : 'bg-purple-700 text-white'}}">${{brandDisplay}}</span>
                    <span class="font-mono text-[11px] text-slate-500">${{ach.region}} • ${{ach.zone}}</span>
                </div>
                <div class="mt-1">
                    <span class="font-black text-slate-900 text-xs sm:text-sm">${{ach.mio_name}}</span>
                    <span class="text-slate-500 ml-1">(SAP: <strong>${{ach.mio_code}}</strong> • Area: <strong>${{ach.area_name}} [${{ach.area_code}}]</strong>)</span>
                </div>
                <div class="mt-1 text-[11px] text-slate-700 bg-white p-2 rounded border border-slate-200">
                    Rx: <strong>${{ach.rx}}</strong> • Terr Sales: <strong>${{ach.terr_pos ? 'Positive' : 'Negative'}}</strong> • Brand Box Growth: <strong>${{ach.brand_growth_box || 0}} Boxes</strong>
                </div>
            `;

            const currentVal = existingOv.award !== undefined ? existingOv.award : prefillAward;
            if (currentVal === 3000) {{
                document.getElementById('ov-radio-3000').checked = true;
            }} else if (currentVal === 1000) {{
                document.getElementById('ov-radio-1000').checked = true;
            }} else {{
                document.getElementById('ov-radio-0').checked = true;
            }}

            document.getElementById('override-reason-input').value = existingOv.reason || prefillReason || 'Approved by Admin';
            document.getElementById('manual-override-modal').classList.remove('hidden');
        }}

        function closeManualOverrideModal() {{
            document.getElementById('manual-override-modal').classList.add('hidden');
        }}

        function confirmManualAwardOverride(e) {{
            e.preventDefault();
            const achId = document.getElementById('override-ach-id').value;
            const ach = findAchieverById(achId);
            if (!ach) return;

            const selectedRadio = document.querySelector('input[name="override_award_radio"]:checked');
            const awardVal = selectedRadio ? Number(selectedRadio.value) : 0;
            const reason = document.getElementById('override-reason-input').value.trim();

            if (awardVal > 0) {{
                const overrideObj = {{
                    id: achId,
                    area_code: ach.area_code,
                    area_name: ach.area_name,
                    mio_code: ach.mio_code,
                    mio_name: ach.mio_name,
                    desig: ach.desig,
                    mobile: ach.mobile,
                    region: ach.region,
                    zone: ach.zone,
                    brand: ach.brand,
                    brand_label: ach.brand_label,
                    rx: ach.rx,
                    award: awardVal,
                    tier: awardVal === 3000 ? '3,000 Award Tier (Manual Admin Grant)' : '1,000 Award Tier (Manual Admin Grant)',
                    reason: reason || 'Manually Granted by Admin',
                    admin_by: 'Admin',
                    timestamp: new Date().toISOString()
                }};
                savedOverrides[achId] = overrideObj;

                // If there was a pending review, mark it approved
                const revKey = 'REV_' + achId;
                if (savedReviews[revKey]) {{
                    savedReviews[revKey].status = 'approved';
                    savedReviews[revKey].admin_note = reason;
                    savedReviews[revKey].granted_award = awardVal;
                    savedReviews[revKey].resolved_at = new Date().toISOString();
                    sendCloudReview(savedReviews[revKey]);
                }}
                sendCloudOverride(overrideObj);
            }} else {{
                delete savedOverrides[achId];
                sendCloudOverride({{ id: achId, area_code: ach.area_code, mio_code: ach.mio_code, brand: ach.brand, award: 0 }});
            }}

            localStorage.setItem(STORAGE_KEY_OVERRIDES, JSON.stringify(savedOverrides));
            localStorage.setItem(STORAGE_KEY_REVIEWS, JSON.stringify(savedReviews));

            closeManualOverrideModal();
            renderAchievers();
            updateRegionProgress();
            if (isAdminUnlocked) refreshAdminStats();
            showToast(awardVal > 0 ? `Manual award of ${{awardVal.toLocaleString()}} Taka granted! 🏆` : 'Override revoked! Reverted to automated calculation.', '✅');
        }}

        function adminExecuteDirectGrant() {{
            const inputVal = (document.getElementById('admin-direct-mio-input')?.value || '').trim();
            if (!inputVal) {{
                alert('Please type or select an MIO / Territory first!');
                return;
            }}

            const matched = DB.all_territories.find(t => 
                inputVal.includes(t.mio_id) ||
                inputVal.includes(t.area_code) ||
                inputVal.toLowerCase().includes(t.mio_name.toLowerCase()) ||
                inputVal.toLowerCase().includes(t.area_name.toLowerCase())
            );

            if (!matched) {{
                alert('No matching territory found for: ' + inputVal);
                return;
            }}

            const brandType = document.getElementById('admin-direct-brand-select').value;
            const awardVal = Number(document.getElementById('admin-direct-award-select').value);
            const achId = brandType === 'exium' ? `EXIUM_${{matched.area_code}}_${{matched.mio_id}}` : `CORAL_${{matched.area_code}}_${{matched.mio_id}}`;

            openManualOverrideModal(achId, awardVal, 'Direct Admin Grant');
        }}

        function renderAdminReviewsTable() {{
            const tbody = document.getElementById('admin-reviews-tbody');
            if (!tbody) return;
            tbody.innerHTML = '';

            const revList = Object.values(savedReviews);
            const pendingCount = revList.filter(r => r.status === 'pending').length;
            const overridesCount = Object.keys(savedOverrides).length;

            const bPending = document.getElementById('admin-pending-review-badge');
            const bOverrides = document.getElementById('admin-total-overrides-badge');
            if (bPending) bPending.textContent = `${{pendingCount}} Pending Reviews`;
            if (bOverrides) bOverrides.textContent = `${{overridesCount}} Manual Grants`;

            // Populate datalist for quick manual grant tool
            const datalist = document.getElementById('admin-all-mios-datalist');
            if (datalist && datalist.children.length === 0) {{
                DB.all_territories.forEach(t => {{
                    const opt = document.createElement('option');
                    opt.value = `[${{t.mio_id}}] ${{t.mio_name}} (${{t.area_code}} - ${{t.area_name}}) - ${{t.region_name}}`;
                    datalist.appendChild(opt);
                }});
            }}

            if (revList.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="8" class="py-6 text-center text-slate-400 font-medium">No review requests submitted yet.</td></tr>`;
                return;
            }}

            revList.sort((a, b) => {{
                if (a.status === 'pending' && b.status !== 'pending') return -1;
                if (a.status !== 'pending' && b.status === 'pending') return 1;
                return String(b.timestamp || '').localeCompare(String(a.timestamp || ''));
            }});

            revList.forEach(r => {{
                const isExium = (r.brand || '').toLowerCase().includes('exium') || r.ach_id.startsWith('EXIUM_');
                const isPending = r.status === 'pending';
                const isApproved = r.status === 'approved';

                const tr = document.createElement('tr');
                tr.className = isPending ? 'bg-amber-50/30 hover:bg-amber-50/50' : 'hover:bg-slate-50';
                tr.innerHTML = `
                    <td class="py-2.5 px-3 font-mono text-[10px] text-slate-500 whitespace-nowrap">
                        ${{formatToBDTime(r.timestamp || '')}}
                    </td>
                    <td class="py-2.5 px-3 whitespace-nowrap">
                        <span class="px-2 py-0.5 rounded text-[10px] font-black ${{isExium ? 'bg-blue-600 text-white' : 'bg-purple-700 text-white'}}">
                            ${{isExium ? '🟦 Exium MUPS' : '🟪 Coralcal'}}
                        </span>
                    </td>
                    <td class="py-2.5 px-3">
                        <div class="font-black text-slate-900">${{r.mio_name}}</div>
                        <div class="text-[10px] text-slate-500 font-mono">SAP: ${{r.mio_code}} • ${{r.area_name}} (${{r.area_code}})</div>
                    </td>
                    <td class="py-2.5 px-3 whitespace-nowrap">
                        <div class="font-bold text-slate-800">${{r.region}}</div>
                        <div class="text-[10px] text-slate-500">${{r.zone}}</div>
                    </td>
                    <td class="py-2.5 px-3">
                        <span class="font-extrabold text-amber-950 bg-amber-100/80 px-2 py-0.5 rounded border border-amber-200 text-[10px] block">
                            ${{r.dispute_category}}
                        </span>
                    </td>
                    <td class="py-2.5 px-3 text-[11px]">
                        <div class="text-slate-800 font-medium">"${{r.remarks}}"</div>
                        <div class="text-[10px] text-slate-500 mt-0.5">By: <strong>${{r.submitter_name || r.submitter_role}}</strong> (${{r.contact_mobile}})</div>
                    </td>
                    <td class="py-2.5 px-3 text-center whitespace-nowrap">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-black ${{
                            isPending ? 'bg-amber-100 text-amber-900 border border-amber-300' :
                            (isApproved ? 'bg-emerald-100 text-emerald-900 border border-emerald-300' : 'bg-rose-100 text-rose-900 border border-rose-300')
                        }}">
                            ${{isPending ? '⏳ Pending' : (isApproved ? '✅ Approved (' + (r.granted_award || 3000) + ')' : '❌ Rejected')}}
                        </span>
                    </td>
                    <td class="py-2.5 px-3 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                            <button onclick="openManualOverrideModal('${{r.ach_id}}', 3000, 'Approved review: ${{r.dispute_category}}')" class="px-2 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-[10px] font-black transition shadow-2xs">
                                🏆 Grant 3,000
                            </button>
                            <button onclick="openManualOverrideModal('${{r.ach_id}}', 1000, 'Approved review: ${{r.dispute_category}}')" class="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-[10px] font-black transition shadow-2xs">
                                🎖️ Grant 1,000
                            </button>
                            ${{isPending ? `
                                <button onclick="adminRejectReview('${{r.id}}')" title="Reject / Dismiss this dispute" class="px-1.5 py-1 bg-rose-50 hover:bg-rose-600 text-rose-700 hover:text-white border border-rose-300 rounded text-[10px] font-bold transition">
                                    ✕
                                </button>
                            ` : ''}}
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function adminRejectReview(reviewId) {{
            if (!confirm('Are you sure you want to dismiss / reject this review request?')) return;
            if (savedReviews[reviewId]) {{
                savedReviews[reviewId].status = 'rejected';
                savedReviews[reviewId].resolved_at = new Date().toISOString();
                localStorage.setItem(STORAGE_KEY_REVIEWS, JSON.stringify(savedReviews));
                sendCloudReview(savedReviews[reviewId]);
                renderAdminReviewsTable();
                renderAchievers();
                showToast('Review request marked as rejected.', 'ℹ️');
            }}
        }}

        // ==============================================
        // ZONAL VIEW FUNCTIONS (SEPARATE EXIUM MUPS & CORALCAL)
        // ==============================================
        function openZonalModal() {{
            const passInput = document.getElementById('zonal-password-input');
            if (passInput) passInput.value = '';
            document.getElementById('zonal-modal').classList.remove('hidden');
        }}

        function closeZonalModal() {{
            document.getElementById('zonal-modal').classList.add('hidden');
        }}

        function onZonalZoneChange() {{
            const passInput = document.getElementById('zonal-password-input');
            if (passInput) passInput.value = '';
            const zoneCode = document.getElementById('zone-login-select').value;
            const box = document.getElementById('zone-details-box');
            if (!zoneCode) {{
                box.classList.add('hidden');
                return;
            }}
            const z = DB.zones.find(x => x.sap_zone_code === zoneCode);
            if (z) {{
                document.getElementById('disp-zh-name').textContent = z.zonal_head;
                document.getElementById('disp-zh-regcount').textContent = `${{z.regions.length}} Regions`;
                box.classList.remove('hidden');
            }}
        }}

        function handleZonalLogin(e) {{
            e.preventDefault();
            const zoneCode = document.getElementById('zone-login-select').value;
            const pass = document.getElementById('zonal-password-input').value.trim();

            if (!zoneCode) {{
                alert('Please select your Zone!');
                return;
            }}

            if (pass !== zoneCode) {{
                alert('Invalid Zonal Password! Zonal login strictly requires your SAP Zone Code (' + zoneCode + ').');
                return;
            }}

            closeZonalModal();
            openZonalDashboard(zoneCode);
        }}

        function openZonalDashboard(zoneCode) {{
            currentActiveZoneCode = zoneCode;
            const zoneObj = DB.zones.find(z => z.sap_zone_code === zoneCode);
            if (!zoneObj) return;

            document.getElementById('login-view').classList.add('hidden');
            document.getElementById('regional-view').classList.add('hidden');
            document.getElementById('sticky-bar').classList.add('hidden');
            document.getElementById('zonal-view').classList.remove('hidden');

            document.getElementById('zoneview-name').textContent = zoneObj.zone_name;
            document.getElementById('zoneview-sap').textContent = `SAP Zone: ${{zoneObj.sap_zone_code}}`;
            document.getElementById('zoneview-zh').textContent = `Zonal Head: ${{zoneObj.zonal_head}}`;

            const exList = DB.achievers_exium.filter(a => a.sap_zone_code === zoneCode);
            const coList = DB.achievers_coral.filter(a => a.sap_zone_code === zoneCode);

            const calcBrandStat = (list) => {{
                let done = 0, canc = 0, val = 0;
                list.forEach(a => {{
                    const ch = savedChoices[a.id];
                    if (ch && ch.cancelled) canc++;
                    else {{
                        val += Number(a.award || 0);
                        if (ch && ch.voucher) done++;
                    }}
                }});
                const pend = list.length - done - canc;
                return {{ total: list.length, done, canc, pend, val }};
            }};

            const exSt = calcBrandStat(exList);
            const coSt = calcBrandStat(coList);

            document.getElementById('zone-exium-total').textContent = exSt.total;
            document.getElementById('zone-exium-done').textContent = exSt.done;
            document.getElementById('zone-exium-pend').textContent = exSt.pend;
            document.getElementById('zone-exium-canc').textContent = exSt.canc;
            document.getElementById('zone-exium-val').textContent = `Active Value: ${{exSt.val.toLocaleString()}}`;

            document.getElementById('zone-coral-total').textContent = coSt.total;
            document.getElementById('zone-coral-done').textContent = coSt.done;
            document.getElementById('zone-coral-pend').textContent = coSt.pend;
            document.getElementById('zone-coral-canc').textContent = coSt.canc;
            document.getElementById('zone-coral-val').textContent = `Active Value: ${{coSt.val.toLocaleString()}}`;

            const brandCounts = {{}};
            BRANDS.forEach(b => brandCounts[b.name] = 0);
            exList.concat(coList).forEach(a => {{
                const ch = savedChoices[a.id];
                if (ch && ch.voucher && !ch.cancelled && brandCounts[ch.voucher] !== undefined) {{
                    brandCounts[ch.voucher]++;
                }}
            }});

            const tbody = document.getElementById('zone-regions-tbody');
            tbody.innerHTML = '';

            zoneObj.regions.forEach(r => {{
                const regEx = DB.achievers_exium.filter(a => a.region === r.region_name);
                const regCo = DB.achievers_coral.filter(a => a.region === r.region_name);
                let exDone = 0, coDone = 0, regCanc = 0;
                regEx.forEach(a => {{
                    if (isAwardResolved(a.id)) exDone++;
                    if (isAwardCancelled(a.id)) regCanc++;
                }});
                regCo.forEach(a => {{
                    if (isAwardResolved(a.id)) coDone++;
                    if (isAwardCancelled(a.id)) regCanc++;
                }});
                const regTotal = regEx.length + regCo.length;
                const regDone = exDone + coDone;
                const regPct = regTotal > 0 ? Math.round((regDone / regTotal) * 100) : 0;

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="py-2.5 px-3 font-black text-slate-900">${{r.region_name}}</td>
                    <td class="py-2.5 px-3 font-mono text-slate-600">${{r.sap_region_code}}</td>
                    <td class="py-2.5 px-3 text-slate-700">${{r.regional_head}}</td>
                    <td class="py-2.5 px-3 text-center font-bold text-blue-700">${{exDone}} / ${{regEx.length}}</td>
                    <td class="py-2.5 px-3 text-center font-bold text-purple-700">${{coDone}} / ${{regCo.length}}</td>
                    <td class="py-2.5 px-3 text-center font-bold ${{regCanc > 0 ? 'text-rose-600' : 'text-slate-400'}}">${{regCanc}}</td>
                    <td class="py-2.5 px-3 text-center">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${{
                            regDone === regTotal && regTotal > 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'
                        }}">${{regDone}}/${{regTotal}} (${{regPct}}%)</span>
                    </td>
                    <td class="py-2.5 px-3 text-right">
                        <button onclick="openRegionalView('${{r.region_name}}')" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold rounded-lg border border-slate-300 text-[11px] transition">
                            Manage / Recommend →
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            }});

            const vGrid = document.getElementById('zone-voucher-cards-grid');
            vGrid.innerHTML = '';
            BRANDS.forEach(b => {{
                const count = brandCounts[b.name] || 0;
                const vCard = document.createElement('div');
                vCard.className = 'bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-center space-y-1';
                vCard.innerHTML = `
                    <div class="h-6 flex items-center justify-center">
                        <img src="${{b.logo}}" alt="${{b.name}}" class="max-h-6 max-w-full object-contain">
                    </div>
                    <div class="text-[10px] font-bold text-slate-700 truncate">${{b.name.replace(' Gift Voucher', '')}}</div>
                    <div class="text-base font-black text-slate-900">${{count}}</div>
                `;
                vGrid.appendChild(vCard);
            }});

            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        // ==============================================
        // MIO QUICK CHECK (SHOWS SEPARATE EXIUM MUPS & CORALCAL WITH AUG & SEP SALES VALUE / QTY)
        // ==============================================
        function searchMioDirect(e) {{
            if (e && e.preventDefault) e.preventDefault();
            const q = document.getElementById('mio-quick-query').value.trim().toLowerCase();
            const resBox = document.getElementById('mio-search-results-box');
            resBox.innerHTML = '';
            if (!q) return;

            const matched = DB.all_territories.filter(r =>
                String(r.mio_id || '').toLowerCase().includes(q) ||
                String(r.area_code || '').toLowerCase().includes(q) ||
                String(r.mio_name || '').toLowerCase().includes(q) ||
                String(r.area_name || '').toLowerCase().includes(q)
            );

            if (matched.length === 0) {{
                resBox.innerHTML = `<div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-slate-500 text-xs text-center">No matching territory or MIO found for "${{q}}".</div>`;
                return;
            }}

            matched.slice(0, 10).forEach((r, idx) => {{
                const theme = MIO_COLOR_PALETTES[idx % MIO_COLOR_PALETTES.length];
                const exId = `EXIUM_${{r.area_code}}_${{r.mio_id}}`;
                const coId = `CORAL_${{r.area_code}}_${{r.mio_id}}`;
                const exCh = savedChoices[exId] || {{}};
                const coCh = savedChoices[coId] || {{}};

                const exOv = savedOverrides[exId];
                const coOv = savedOverrides[coId];

                const exAward = exOv !== undefined ? Number(exOv.award) : Number(r.exium_award || 0);
                const exReason = exOv ? (exOv.reason || 'Admin Manual Override') : r.exium_reason;

                const coAward = coOv !== undefined ? Number(coOv.award) : Number(r.coral_award || 0);
                const coReason = coOv ? (coOv.reason || 'Admin Manual Override') : r.coral_reason;

                const exRev = savedReviews['REV_' + exId];
                const coRev = savedReviews['REV_' + coId];

                const renderBrandStatus = (label, brandShort, badgeClass, award, reason, rx, terrAug, terrSep, terrGrowth, terrPos, brandAugVal, brandSepVal, brandValGrowth, brandAugBox, brandSepBox, growthBox, reqBox, ch, achId, isOverridden, revObj) => {{
                    const boxText = `${{growthBox >= 0 ? '+' : ''}}${{growthBox}} Boxes (Req: +${{reqBox || 30}} Boxes)`;
                    const terrText = `${{terrGrowth > 0 ? '+' : ''}}${{Math.round(terrGrowth).toLocaleString()}}`;
                    const metricsLine = `
                        <div class="grid grid-cols-1 gap-1 pt-1 text-[11px] bg-slate-50/90 p-2 rounded-lg border border-slate-200">
                            <div class="flex items-center justify-between">
                                <span class="font-black text-slate-900">1. Seen Rx (Sep'26):</span>
                                <span class="font-extrabold ${{rx >= 200 ? 'text-emerald-700' : 'text-rose-600'}}">${{rx >= 200 ? '✓ ' + rx + ' Rx (Req: &ge;200)' : '✗ ' + rx + ' Rx (No Award: <200)'}}</span>
                            </div>
                            <div class="flex items-center justify-between border-t border-slate-200/70 pt-1 flex-wrap gap-1">
                                <span class="font-black text-slate-900">2. Territory Sales Growth:</span>
                                <span class="font-bold text-slate-700">Aug: <strong>${{Math.round(terrAug).toLocaleString()}}</strong> ➔ Sep: <strong>${{Math.round(terrSep).toLocaleString()}}</strong> (<strong class="${{terrPos ? 'text-emerald-700' : 'text-rose-600'}}">${{terrText}}</strong>)</span>
                            </div>
                            <div class="border-t border-slate-200/70 pt-1 space-y-0.5">
                                <div class="flex items-center justify-between flex-wrap gap-1">
                                    <span class="font-black text-slate-900">3. ${{brandShort}} Growth:</span>
                                    <span class="font-extrabold ${{growthBox >= (reqBox || 30) ? 'text-emerald-700' : 'text-amber-700'}}">${{boxText}}</span>
                                </div>
                                <div class="text-[10px] font-bold text-slate-600 flex items-center justify-between flex-wrap gap-1">
                                    <span>Qty: Aug <strong>${{brandAugBox}}</strong> Box ➔ Sep <strong>${{brandSepBox}}</strong> Box</span>
                                    <span>Val: Aug <strong>${{Math.round(brandAugVal).toLocaleString()}}</strong> ➔ Sep <strong>${{Math.round(brandSepVal).toLocaleString()}}</strong> (${{brandValGrowth >= 0 ? '+' : ''}}${{Math.round(brandValGrowth).toLocaleString()}})</span>
                                </div>
                            </div>
                        </div>
                    `;

                    let revActionHtml = '';
                    if (revObj && revObj.status === 'pending') {{
                        revActionHtml = `
                            <div class="mt-2 pt-2 border-t border-amber-200 flex items-center justify-between gap-1 flex-wrap">
                                <span class="px-2 py-0.5 rounded font-black text-[10px] bg-amber-100 text-amber-900 border border-amber-300">🔍 Review Requested by ${{revObj.submitter_role || 'RH'}}</span>
                                <button onclick="openReviewModal('${{achId}}')" class="text-[10px] font-bold text-amber-800 hover:underline">View Details</button>
                            </div>
                        `;
                    }} else if (revObj && revObj.status === 'rejected') {{
                        revActionHtml = `
                            <div class="mt-2 pt-2 border-t border-rose-200 flex items-center justify-between gap-1 flex-wrap">
                                <span class="px-2 py-0.5 rounded font-black text-[10px] bg-rose-100 text-rose-800 border border-rose-300">❌ Review Rejected</span>
                                <button onclick="openReviewModal('${{achId}}')" class="text-[10px] font-bold text-slate-700 hover:underline">Re-submit Review (RH/ZH)</button>
                            </div>
                        `;
                    }} else if (revObj && revObj.status === 'approved') {{
                        revActionHtml = `
                            <div class="mt-2 pt-2 border-t border-emerald-200 flex items-center justify-between gap-1 flex-wrap">
                                <span class="px-2 py-0.5 rounded font-black text-[10px] bg-emerald-100 text-emerald-900 border border-emerald-300">✅ Review Approved (${{revObj.granted_award || 3000}})</span>
                            </div>
                        `;
                    }} else {{
                        revActionHtml = `
                            <div class="mt-2 pt-2 border-t border-slate-200 flex items-center justify-between gap-2 flex-wrap">
                                <span class="text-[10px] text-slate-500 font-medium">Data dispute? Regional/Zonal Head can request review:</span>
                                <button onclick="openReviewModal('${{achId}}')" class="px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-[10px] font-black transition shadow-2xs flex items-center gap-1">
                                    <span>📝</span>
                                    <span>Request Data Review (RH/ZH)</span>
                                </button>
                            </div>
                        `;
                    }}

                    if (award === 0) {{
                        return `
                            <div class="bg-slate-50 border border-slate-200 rounded-xl p-2.5 space-y-1.5">
                                <div class="flex justify-between items-center">
                                    <span class="px-2 py-0.5 rounded text-[11px] font-black ${{badgeClass}}">${{label}}</span>
                                    <span class="text-[11px] font-bold text-slate-400">No Award (0)</span>
                                </div>
                                ${{metricsLine}}
                                <div class="text-[10px] text-slate-500">${{reason}}</div>
                                ${{revActionHtml}}
                            </div>
                        `;
                    }}

                    if (ch.cancelled) {{
                        return `
                            <div class="bg-rose-50 border border-rose-200 rounded-xl p-2.5 space-y-1.5">
                                <div class="flex justify-between items-center">
                                    <span class="px-2 py-0.5 rounded text-[11px] font-black ${{badgeClass}}">${{label}}</span>
                                    <span class="text-[11px] font-black text-rose-700">🚫 Cancelled (${{ch.cancelled_by || 'RH/ZH'}})</span>
                                </div>
                                ${{metricsLine}}
                                <div class="text-[10px] text-rose-800 font-semibold">Reason: "${{ch.cancel_reason || '-'}}"</div>
                                ${{revActionHtml}}
                            </div>
                        `;
                    }}

                    let badgeRight = '';
                    if (isOverridden) {{
                        badgeRight = `<span class="px-2 py-0.5 rounded font-black text-[10px] bg-purple-100 text-purple-900 border border-purple-300 shadow-2xs">✨ Admin Manual Grant: ${{award.toLocaleString()}}</span>`;
                    }} else {{
                        badgeRight = `<span class="px-2 py-0.5 rounded font-black text-[11px] bg-emerald-50 text-emerald-800 border border-emerald-200">Award: ${{award.toLocaleString()}}</span>`;
                    }}

                    return `
                        <div class="bg-white border border-slate-200 rounded-xl p-2.5 space-y-1.5">
                            <div class="flex justify-between items-center">
                                <span class="px-2 py-0.5 rounded text-[11px] font-black ${{badgeClass}}">${{label}}</span>
                                ${{badgeRight}}
                            </div>
                            ${{metricsLine}}
                            <div class="text-[10px] text-slate-500">${{reason}}</div>
                            <div class="pt-0.5 text-[11px] font-bold ${{ch.voucher ? 'text-emerald-700' : 'text-amber-700'}}">
                                ${{ch.voucher ? `✓ Voucher: ${{ch.voucher}}` : '⏳ Pending Selection by Regional Head'}}
                            </div>
                            ${{revActionHtml}}
                        </div>
                    `;
                }};

                const card = document.createElement('div');
                card.className = 'p-4 bg-white border border-slate-200 rounded-2xl shadow-sm text-xs space-y-3';
                card.innerHTML = `
                    <div class="p-3 rounded-xl border flex items-start justify-between gap-2 ${{theme.bg}} ${{theme.border}}">
                        <div>
                            <div class="flex items-center gap-1.5 flex-wrap mb-1">
                                <span class="bg-orange-500 text-white text-[11px] font-black px-2 py-0.5 rounded-md">📍 ${{r.area_name}} (${{r.area_code}})</span>
                                <span class="px-2 py-0.5 rounded-md font-black text-[10px] bg-slate-900 text-white">MIO: ${{r.mio_id}}</span>
                            </div>
                            <h4 class="text-sm font-black text-slate-900">${{r.mio_name}}</h4>
                            <div class="text-[11px] text-slate-600">${{r.region_name}} • ${{r.zone_name}}</div>
                        </div>
                    </div>
                    <div class="space-y-2">
                        ${{renderBrandStatus('🟦 Exium MUPS', 'Exium MUPS', 'bg-blue-600 text-white', exAward, exReason, r.exium_rx, r.terr_aug_val, r.terr_sep_val, r.terr_growth_val, r.terr_pos, r.exium_aug_val, r.exium_sep_val, r.exium_actual_growth, r.exium_aug_box, r.exium_sep_box, r.exium_growth_box, r.exium_req_box, exCh, exId, Boolean(exOv), exRev)}}
                        ${{renderBrandStatus('🟪 Coralcal-D/DX/Vita', 'Coralcal-D/DX/Vita', 'bg-purple-700 text-white', coAward, coReason, r.coral_rx, r.terr_aug_val, r.terr_sep_val, r.terr_growth_val, r.terr_pos, r.coral_aug_val, r.coral_sep_val, r.coral_actual_growth, r.coral_aug_box, r.coral_sep_box, r.coral_growth_box, r.coral_req_box, coCh, coId, Boolean(coOv), coRev)}}
                    </div>
                `;
                resBox.appendChild(card);
            }});
        }}

        // ==============================================
        // CRITERIA MODAL
        // ==============================================
        function openAwardCriteriaModal(initialTab = 'exium') {{
            switchCriteriaTab(initialTab);
            document.getElementById('criteria-modal').classList.remove('hidden');
        }}

        function closeAwardCriteriaModal() {{
            document.getElementById('criteria-modal').classList.add('hidden');
        }}

        function switchCriteriaTab(tab) {{
            const tabEx = document.getElementById('tab-crit-exium');
            const tabCo = document.getElementById('tab-crit-coral');
            const viewEx = document.getElementById('crit-view-exium');
            const viewCo = document.getElementById('crit-view-coral');

            if (tab === 'exium') {{
                tabEx.className = 'px-4 py-2.5 rounded-t-xl text-xs sm:text-sm font-black transition border-b-2 border-blue-600 text-blue-700 bg-white shadow-xs';
                tabCo.className = 'px-4 py-2.5 rounded-t-xl text-xs sm:text-sm font-bold transition border-b-2 border-transparent text-slate-500 hover:text-slate-800';
                viewEx.classList.remove('hidden');
                viewCo.classList.add('hidden');
            }} else {{
                tabCo.className = 'px-4 py-2.5 rounded-t-xl text-xs sm:text-sm font-black transition border-b-2 border-purple-700 text-purple-700 bg-white shadow-xs';
                tabEx.className = 'px-4 py-2.5 rounded-t-xl text-xs sm:text-sm font-bold transition border-b-2 border-transparent text-slate-500 hover:text-slate-800';
                viewCo.classList.remove('hidden');
                viewEx.classList.add('hidden');
            }}
        }}

        // ==============================================
        // ADMIN PANEL (SEPARATE EXIUM MUPS & CORALCAL VIEWS & DATA)
        // ==============================================
        function openAdminModal() {{
            const passInput = document.getElementById('admin-password-input');
            if (passInput) passInput.value = '';
            document.getElementById('admin-modal').classList.remove('hidden');
            if (isAdminUnlocked) {{
                showAdminDashboard();
            }} else {{
                document.getElementById('admin-auth-box').classList.remove('hidden');
                document.getElementById('admin-dashboard-box').classList.add('hidden');
            }}
        }}

        function closeAdminModal() {{
            document.getElementById('admin-modal').classList.add('hidden');
        }}

        function verifyAdminPassword() {{
            const pass = document.getElementById('admin-password-input').value.trim();
            if (pass === 'Exium MUPS' || pass === 'Sep 2026') {{
                isAdminUnlocked = true;
                showAdminDashboard();
            }} else {{
                alert('Invalid Admin Password! Please enter the correct password.');
            }}
        }}

        function showAdminDashboard() {{
            document.getElementById('admin-auth-box').classList.add('hidden');
            document.getElementById('admin-dashboard-box').classList.remove('hidden');
            updateSubmissionLockUI();
            refreshAdminStats();
        }}

        function setAdminBrandMode(mode) {{
            currentAdminBrandMode = mode;
            const btnEx = document.getElementById('admin-brand-tab-exium');
            const btnCo = document.getElementById('admin-brand-tab-coral');
            const btnBo = document.getElementById('admin-brand-tab-both');
            const ind = document.getElementById('admin-active-brand-indicator');

            btnEx.className = mode === 'exium'
                ? 'px-4 py-2 rounded-xl text-xs font-black transition bg-blue-600 text-white shadow-sm'
                : 'px-4 py-2 rounded-xl text-xs font-bold transition bg-white text-blue-800 hover:bg-blue-50 border border-blue-200';
            btnCo.className = mode === 'coral'
                ? 'px-4 py-2 rounded-xl text-xs font-black transition bg-purple-700 text-white shadow-sm'
                : 'px-4 py-2 rounded-xl text-xs font-bold transition bg-white text-purple-800 hover:bg-purple-50 border border-purple-200';
            btnBo.className = mode === 'both'
                ? 'px-4 py-2 rounded-xl text-xs font-black transition bg-slate-900 text-white shadow-sm'
                : 'px-4 py-2 rounded-xl text-xs font-bold transition bg-white text-slate-700 hover:bg-slate-50 border border-slate-200';

            if (mode === 'exium') {{
                ind.className = 'px-3 py-1 rounded-xl text-[11px] font-black bg-blue-100 text-blue-900';
                ind.textContent = 'Showing: 🟦 Exium MUPS Award Only';
                document.getElementById('admin-reg-table-title').textContent = 'Region-wise Input & Submission Tracking (Exium MUPS)';
                document.getElementById('admin-voucher-table-title').textContent = 'Exium MUPS — National Voucher Brand Requirements (PO Planning)';
                document.getElementById('admin-cancel-table-title').textContent = '🚫 Exium MUPS — Cancelled Awards Log (RH / ZH Recommendations)';
            }} else if (mode === 'coral') {{
                ind.className = 'px-3 py-1 rounded-xl text-[11px] font-black bg-purple-100 text-purple-900';
                ind.textContent = 'Showing: 🟪 Coralcal-D/DX/Vita Award Only';
                document.getElementById('admin-reg-table-title').textContent = 'Region-wise Input & Submission Tracking (Coralcal-D/DX/Vita)';
                document.getElementById('admin-voucher-table-title').textContent = 'Coralcal-D/DX/Vita — National Voucher Brand Requirements (PO Planning)';
                document.getElementById('admin-cancel-table-title').textContent = '🚫 Coralcal-D/DX/Vita — Cancelled Awards Log (RH / ZH Recommendations)';
            }} else {{
                ind.className = 'px-3 py-1 rounded-xl text-[11px] font-black bg-slate-200 text-slate-900';
                ind.textContent = 'Showing: 📊 Combined Overview (Exium MUPS + Coralcal)';
                document.getElementById('admin-reg-table-title').textContent = 'Region-wise Input & Submission Tracking (Combined Exium MUPS & Coralcal)';
                document.getElementById('admin-voucher-table-title').textContent = 'Combined — National Voucher Brand Requirements (PO Planning)';
                document.getElementById('admin-cancel-table-title').textContent = '🚫 Combined — Cancelled Awards Log (RH / ZH Recommendations)';
            }}

            refreshAdminStats();
        }}

        function getActiveAdminAchieversList() {{
            const getBrandAchievers = (isExium) => {{
                const baseList = isExium ? DB.achievers_exium : DB.achievers_coral;
                const map = {{}};
                baseList.forEach(a => {{
                    const ov = savedOverrides[a.id];
                    if (ov) {{
                        if (Number(ov.award) > 0) {{
                            map[a.id] = Object.assign({{}}, a, {{ award: Number(ov.award), tier: ov.tier || a.tier, is_manual_override: true, reason: ov.reason || a.reason }});
                        }}
                    }} else {{
                        map[a.id] = a;
                    }}
                }});
                Object.values(savedOverrides).forEach(ov => {{
                    const ovBrand = ov.brand || '';
                    const matchBrand = isExium ? 
                        (ovBrand.toLowerCase().includes('exium') || ov.id.startsWith('EXIUM_')) : 
                        (ovBrand.toLowerCase().includes('coral') || ov.id.startsWith('CORAL_'));
                    if (matchBrand && Number(ov.award) > 0 && !map[ov.id]) {{
                        const found = findAchieverById(ov.id);
                        if (found) map[ov.id] = found;
                    }}
                }});
                return Object.values(map);
            }};

            if (currentAdminBrandMode === 'exium') return getBrandAchievers(true);
            if (currentAdminBrandMode === 'coral') return getBrandAchievers(false);
            return getBrandAchievers(true).concat(getBrandAchievers(false));
        }}

        function refreshAdminStats() {{
            // 1. Always update top standalone Exium MUPS & Coralcal summary cards
            const computeBrandSummary = (isExium) => {{
                const baseList = isExium ? DB.achievers_exium : DB.achievers_coral;
                const map = {{}};
                baseList.forEach(a => {{
                    const ov = savedOverrides[a.id];
                    if (ov) {{
                        if (Number(ov.award) > 0) {{
                            map[a.id] = {{ id: a.id, award: Number(ov.award) }};
                        }}
                    }} else {{
                        map[a.id] = {{ id: a.id, award: Number(a.award || 0) }};
                    }}
                }});
                Object.values(savedOverrides).forEach(ov => {{
                    const ovBrand = ov.brand || '';
                    const matchBrand = isExium ? 
                        (ovBrand.toLowerCase().includes('exium') || ov.id.startsWith('EXIUM_')) : 
                        (ovBrand.toLowerCase().includes('coral') || ov.id.startsWith('CORAL_'));
                    if (matchBrand) {{
                        const ovAward = Number(ov.award || 0);
                        if (ovAward > 0) {{
                            map[ov.id] = {{ id: ov.id, award: ovAward }};
                        }} else {{
                            delete map[ov.id];
                        }}
                    }}
                }});

                const activeAchievers = Object.values(map);
                let done = 0, canc = 0, activeVal = 0;
                activeAchievers.forEach(a => {{
                    const ch = savedChoices[a.id];
                    if (ch && ch.cancelled) canc++;
                    else {{
                        activeVal += Number(a.award || 0);
                        if (ch && ch.voucher) done++;
                    }}
                }});
                const pend = activeAchievers.length - done - canc;
                const resolved = done + canc;
                const pct = activeAchievers.length > 0 ? ((resolved / activeAchievers.length) * 100).toFixed(1) : '0.0';
                return {{ total: activeAchievers.length, done, canc, pend, activeVal, pct }};
            }};

            const exSum = computeBrandSummary(true);
            const coSum = computeBrandSummary(false);

            document.getElementById('admin-exium-total').textContent = exSum.total.toLocaleString();
            document.getElementById('admin-exium-done').textContent = exSum.done.toLocaleString();
            document.getElementById('admin-exium-pct').textContent = `${{exSum.pct}}%`;
            document.getElementById('admin-exium-pend').textContent = exSum.pend.toLocaleString();
            document.getElementById('admin-exium-canc').textContent = exSum.canc.toLocaleString();
            document.getElementById('admin-exium-val').textContent = `Val: ${{exSum.activeVal.toLocaleString()}}`;

            document.getElementById('admin-coral-total').textContent = coSum.total.toLocaleString();
            document.getElementById('admin-coral-done').textContent = coSum.done.toLocaleString();
            document.getElementById('admin-coral-pct').textContent = `${{coSum.pct}}%`;
            document.getElementById('admin-coral-pend').textContent = coSum.pend.toLocaleString();
            document.getElementById('admin-coral-canc').textContent = coSum.canc.toLocaleString();
            document.getElementById('admin-coral-val').textContent = `Val: ${{coSum.activeVal.toLocaleString()}}`;

            // 2. Compute Voucher PO Table & Cancelled Log for active brand tab
            const activeList = getActiveAdminAchieversList();
            let activeCompletedVouchers = 0;
            const brandCounts = {{}};
            BRANDS.forEach(b => {{
                brandCounts[b.name] = {{ c1000: 0, c3000: 0, total: 0, val: 0 }};
            }});

            const cancelledList = [];

            activeList.forEach(a => {{
                const ch = savedChoices[a.id];
                if (ch && ch.cancelled) {{
                    cancelledList.push({{ a, ch }});
                }} else if (ch && ch.voucher) {{
                    activeCompletedVouchers++;
                    if (brandCounts[ch.voucher]) {{
                        if (Number(a.award) === 3000) brandCounts[ch.voucher].c3000++;
                        else brandCounts[ch.voucher].c1000++;
                        brandCounts[ch.voucher].total++;
                        brandCounts[ch.voucher].val += Number(a.award || 0);
                    }}
                }}
            }});

            const tbody = document.getElementById('admin-voucher-tbody');
            if (tbody) {{
                tbody.innerHTML = '';
                BRANDS.forEach(b => {{
                    const data = brandCounts[b.name];
                    const share = activeCompletedVouchers > 0 ? ((data.total / activeCompletedVouchers) * 100).toFixed(1) : '0.0';
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="py-2 px-3 font-bold text-slate-900 flex items-center gap-2.5">
                            <img src="${{b.logo}}" alt="${{b.name}}" class="h-6 w-14 object-contain">
                            <span>${{b.name}}</span>
                        </td>
                        <td class="py-2 px-3 text-center">${{data.c1000}}</td>
                        <td class="py-2 px-3 text-center">${{data.c3000}}</td>
                        <td class="py-2 px-3 text-center font-black text-slate-900">${{data.total}}</td>
                        <td class="py-2 px-3 text-center font-bold text-emerald-700">${{data.val.toLocaleString()}}</td>
                        <td class="py-2 px-3 text-right font-bold text-orange-600">${{share}}%</td>
                    `;
                    tbody.appendChild(row);
                }});
            }}

            // 3. Render Cancelled Log Table
            const cancTbody = document.getElementById('admin-cancelled-tbody');
            const cancBadge = document.getElementById('admin-cancelled-badge');
            if (cancBadge) cancBadge.textContent = `${{cancelledList.length}} Cancelled`;
            if (cancTbody) {{
                cancTbody.innerHTML = '';
                if (cancelledList.length === 0) {{
                    cancTbody.innerHTML = `<tr><td colspan="7" class="py-4 text-center text-slate-400">No awards cancelled in this view.</td></tr>`;
                }} else {{
                    cancelledList.forEach(({{ a, ch }}) => {{
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td class="py-2 px-3 font-bold ${{a.brand === 'Exium_2026' ? 'text-blue-700' : 'text-purple-700'}}">${{a.brand_label}}</td>
                            <td class="py-2 px-3">${{a.region}} <span class="text-[10px] text-slate-400">(${{a.zone}})</span></td>
                            <td class="py-2 px-3"><strong>${{a.mio_name}}</strong> (${{a.mio_code}}) • ${{a.area_code}}</td>
                            <td class="py-2 px-3 text-center font-bold text-rose-700 line-through">${{a.award.toLocaleString()}}</td>
                            <td class="py-2 px-3 font-bold">${{ch.cancelled_by || 'RH/ZH'}}</td>
                            <td class="py-2 px-3 text-rose-900">${{ch.cancel_reason || '-'}}</td>
                            <td class="py-2 px-3 text-right">
                                <button onclick="restoreCancelledAward('${{a.id}}')" class="px-2 py-0.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-300 rounded text-[10px] font-bold">Restore</button>
                            </td>
                        `;
                        cancTbody.appendChild(tr);
                    }});
                }}
            }}

            renderAdminReviewsTable();
            renderAdminRegionTable();
        }}

        function setAdminRegionFilter(filter) {{
            currentAdminRegionFilter = filter;
            const pills = ['all', 'pending', 'not_started', 'in_progress', 'completed'];
            pills.forEach(p => {{
                const btn = document.getElementById('rf-pill-' + p);
                if (!btn) return;
                if (p === filter) {{
                    btn.className = 'px-2.5 py-1 rounded-md text-[11px] font-bold bg-slate-900 text-white transition';
                }} else {{
                    btn.className = 'px-2.5 py-1 rounded-md text-[11px] font-bold bg-white text-slate-600 hover:bg-slate-100 border border-slate-200 transition';
                }}
            }});
            renderAdminRegionTable();
        }}

        function getRegionCompletionStats() {{
            const statsMap = {{}};

            Object.values(DB.regions_map).forEach(r => {{
                statsMap[r.region_name] = {{
                    region_name: r.region_name,
                    sap_region_code: r.sap_region_code,
                    regional_head: r.regional_head || 'Not Assigned',
                    zone_name: r.zone_name || '-',
                    sap_zone_code: r.sap_zone_code || '',
                    zonal_head: r.zonal_head || '-',
                    total_exium: 0,
                    total_coral: 0,
                    total_awards: 0,
                    completed_awards: 0,
                    pending_awards: 0,
                    pct: 0,
                    status: 'not_started'
                }};
            }});

            const activeList = getActiveAdminAchieversList();
            activeList.forEach(a => {{
                const reg = a.region;
                if (!statsMap[reg]) {{
                    statsMap[reg] = {{
                        region_name: reg,
                        sap_region_code: a.sap_region_code || '',
                        regional_head: a.regional_head || 'Not Assigned',
                        zone_name: a.zone || '-',
                        sap_zone_code: a.sap_zone_code || '',
                        zonal_head: a.zonal_head || '-',
                        total_exium: 0,
                        total_coral: 0,
                        total_awards: 0,
                        completed_awards: 0,
                        pending_awards: 0,
                        pct: 0,
                        status: 'not_started'
                    }};
                }}
                const isExium = (a.brand || '').toLowerCase().includes('exium') || a.id.startsWith('EXIUM_');
                if (isExium) statsMap[reg].total_exium++;
                else statsMap[reg].total_coral++;
                statsMap[reg].total_awards++;

                if (isAwardResolved(a.id)) {{
                    statsMap[reg].completed_awards++;
                }}
            }});

            return Object.values(statsMap).filter(item => item.total_awards > 0).map(item => {{
                item.pending_awards = item.total_awards - item.completed_awards;
                item.pct = item.total_awards > 0 ? (item.completed_awards / item.total_awards) * 100 : 0;
                if (item.completed_awards === 0) item.status = 'not_started';
                else if (item.completed_awards === item.total_awards) item.status = 'completed';
                else item.status = 'in_progress';
                return item;
            }});
        }}

        function renderAdminRegionTable() {{
            const allStats = getRegionCompletionStats();
            let completedCount = 0, inProgressCount = 0, notStartedCount = 0, totalPendingAwards = 0;

            allStats.forEach(r => {{
                if (r.status === 'completed') completedCount++;
                else if (r.status === 'in_progress') inProgressCount++;
                else notStartedCount++;
                totalPendingAwards += r.pending_awards;
            }});

            document.getElementById('admin-reg-stat-completed').textContent = completedCount;
            document.getElementById('admin-reg-stat-inprogress').textContent = inProgressCount;
            document.getElementById('admin-reg-stat-notstarted').textContent = notStartedCount;
            document.getElementById('admin-reg-stat-pendingawards').textContent = totalPendingAwards.toLocaleString();
            document.getElementById('admin-reg-total-badge').textContent = `${{allStats.length}} Regions`;

            document.getElementById('rf-pill-all').textContent = `All (${{allStats.length}})`;
            document.getElementById('rf-pill-pending').textContent = `⚠️ Any Pending (${{inProgressCount + notStartedCount}})`;
            document.getElementById('rf-pill-not_started').textContent = `🔴 Not Started (${{notStartedCount}})`;
            document.getElementById('rf-pill-in_progress').textContent = `🟡 In Progress (${{inProgressCount}})`;
            document.getElementById('rf-pill-completed').textContent = `🟢 Completed (${{completedCount}})`;

            const query = (document.getElementById('admin-reg-search')?.value || '').trim().toLowerCase();

            let filtered = allStats.filter(r => {{
                if (currentAdminRegionFilter === 'completed' && r.status !== 'completed') return false;
                if (currentAdminRegionFilter === 'in_progress' && r.status !== 'in_progress') return false;
                if (currentAdminRegionFilter === 'not_started' && r.status !== 'not_started') return false;
                if (currentAdminRegionFilter === 'pending' && r.pending_awards === 0) return false;

                if (query) {{
                    const matchName = r.region_name.toLowerCase().includes(query);
                    const matchSap = String(r.sap_region_code).toLowerCase().includes(query);
                    const matchRh = r.regional_head.toLowerCase().includes(query);
                    const matchZone = r.zone_name.toLowerCase().includes(query);
                    if (!matchName && !matchSap && !matchRh && !matchZone) return false;
                }}
                return true;
            }});

            const sortVal = document.getElementById('admin-reg-sort')?.value || 'pending_first';
            filtered.sort((a, b) => {{
                if (sortVal === 'pending_first') return (b.pending_awards - a.pending_awards) || (a.pct - b.pct);
                if (sortVal === 'completed_first') return (b.pct - a.pct) || (a.pending_awards - b.pending_awards);
                if (sortVal === 'achievers_desc') return b.total_awards - a.total_awards;
                if (sortVal === 'pct_asc') return a.pct - b.pct;
                if (sortVal === 'pct_desc') return b.pct - a.pct;
                if (sortVal === 'name_asc') return a.region_name.localeCompare(b.region_name);
                if (sortVal === 'zone_asc') return a.zone_name.localeCompare(b.zone_name);
                return 0;
            }});

            const tbody = document.getElementById('admin-region-tbody');
            tbody.innerHTML = '';

            if (filtered.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="9" class="py-8 text-center text-slate-400 font-medium">No regions found matching the current filter.</td></tr>`;
            }} else {{
                filtered.forEach((r, idx) => {{
                    const tr = document.createElement('tr');
                    tr.className = 'hover:bg-slate-50/80 transition';

                    let statusBadge = '';
                    if (r.status === 'completed') {{
                        statusBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800 border border-emerald-300">🟢 100% Completed</span>';
                    }} else if (r.status === 'in_progress') {{
                        statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">🟡 In Progress (${{r.completed_awards}}/${{r.total_awards}})</span>`;
                    }} else {{
                        statusBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">🔴 Not Started</span>';
                    }}

                    const pctFormatted = r.pct.toFixed(1);
                    const barColor = r.status === 'completed' ? 'bg-emerald-500' : (r.status === 'in_progress' ? 'bg-amber-500' : 'bg-slate-200');
                    const subBreakdown = currentAdminBrandMode === 'exium'
                        ? `<div class="text-[10px] text-blue-600 font-normal">Exium MUPS: ${{r.total_exium}}</div>`
                        : (currentAdminBrandMode === 'coral'
                            ? `<div class="text-[10px] text-purple-600 font-normal">Coralcal: ${{r.total_coral}}</div>`
                            : `<div class="text-[10px] text-slate-400 font-normal">Exium MUPS:${{r.total_exium}} | Cor:${{r.total_coral}}</div>`);

                    tr.innerHTML = `
                        <td class="py-2.5 px-3 text-center text-slate-400 font-mono text-[11px]">${{idx + 1}}</td>
                        <td class="py-2.5 px-3">
                            <div class="flex items-center gap-1.5 flex-wrap">
                                <span class="font-bold text-slate-900">${{r.region_name}}</span>
                                <span class="px-1.5 py-0.2 text-[10px] font-mono font-bold text-slate-600 bg-slate-100 rounded border border-slate-200">SAP: ${{r.sap_region_code}}</span>
                            </div>
                            <div class="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
                                <span>👤</span>
                                <span class="font-semibold text-slate-700">${{r.regional_head}}</span>
                            </div>
                        </td>
                        <td class="py-2.5 px-3 text-slate-600">
                            <div class="font-medium text-slate-800">${{r.zone_name}}</div>
                            <div class="text-[10px] text-slate-400 font-mono">${{r.sap_zone_code || ''}}</div>
                        </td>
                        <td class="py-2.5 px-3 text-center font-bold text-slate-900">
                            <span>${{r.total_awards}}</span>
                            ${{subBreakdown}}
                        </td>
                        <td class="py-2.5 px-3 text-center">
                            <span class="font-bold ${{r.completed_awards > 0 ? 'text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200' : 'text-slate-400'}}">${{r.completed_awards}}</span>
                        </td>
                        <td class="py-2.5 px-3 text-center">
                            <span class="font-bold ${{r.pending_awards > 0 ? 'text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200' : 'text-slate-400'}}">${{r.pending_awards}}</span>
                        </td>
                        <td class="py-2.5 px-3">
                            <div class="flex items-center gap-2">
                                <div class="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200 min-w-[50px]">
                                    <div class="${{barColor}} h-full transition-all duration-300" style="width: ${{pctFormatted}}%"></div>
                                </div>
                                <span class="font-mono text-[10px] font-bold ${{r.pct === 100 ? 'text-emerald-700' : (r.pct > 0 ? 'text-amber-700' : 'text-slate-400')}} min-w-[36px] text-right">${{pctFormatted}}%</span>
                            </div>
                        </td>
                        <td class="py-2.5 px-3 text-center">${{statusBadge}}</td>
                        <td class="py-2.5 px-3 text-center">
                            <button type="button" onclick="adminViewRegion('${{r.region_name.replace(/'/g, "\\\\'")}}')" class="px-2 py-1 bg-slate-100 hover:bg-orange-50 hover:text-orange-700 hover:border-orange-300 text-slate-700 rounded-lg text-[11px] font-bold border border-slate-200 transition shadow-2xs">
                                View ↗
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                }});
            }}

            document.getElementById('admin-reg-showing-count').textContent = `Showing ${{filtered.length}} of ${{allStats.length}} regions`;
        }}

        function adminViewRegion(regName) {{
            closeAdminModal();
            if (currentAdminBrandMode === 'exium') setRegionalBrandFilter('exium');
            else if (currentAdminBrandMode === 'coral') setRegionalBrandFilter('coral');
            else setRegionalBrandFilter('all');
            openRegionalView(regName);
        }}

        function copyPendingRegionsSummary() {{
            const list = getRegionCompletionStats().filter(r => r.pending_awards > 0);
            if (list.length === 0) {{
                showToast('All regions have completed their submissions! 🎉', '✅');
                return;
            }}
            const brandLabel = currentAdminBrandMode === 'exium' ? 'Exium MUPS' : (currentAdminBrandMode === 'coral' ? 'Coralcal-D/DX/Vita' : 'Combined');
            const bdTime = formatToBDTime(new Date());
            let text = `📢 September 2026 Award Campaign (${{brandLabel}}) - Pending Regions (${{list.length}} Regions Pending)\\n`;
            text += 'Recorded at: ' + bdTime + '\\n\\n';
            list.forEach((r, i) => {{
                text += (i + 1) + '. ' + r.region_name + ' (SAP: ' + r.sap_region_code + ') | RH: ' + r.regional_head + ' | Zone: ' + r.zone_name + ' | Pending: ' + r.pending_awards + '/' + r.total_awards + '\\n';
            }});
            text += '\\nPortal Link: ' + MASKED_PORTAL_URL;

            navigator.clipboard.writeText(text).then(() => {{
                showToast('Copied ' + list.length + ' pending regions to clipboard! 📋', '✅');
            }}).catch(() => {{
                prompt('Copy pending regions:', text);
            }});
        }}

        function exportRegionSummaryToExcel() {{
            const list = getRegionCompletionStats();
            const brandTag = currentAdminBrandMode === 'exium' ? 'Exium_MUPS' : (currentAdminBrandMode === 'coral' ? 'Coralcal' : 'Combined');
            const rows = list.map((r, i) => ({{
                'SL': i + 1,
                'Brand Filter': brandTag.replace('_', ' '),
                'Zone Name': r.zone_name,
                'SAP Zone Code': r.sap_zone_code,
                'Zonal Head': r.zonal_head,
                'Region Name': r.region_name,
                'SAP Region Code': r.sap_region_code,
                'Regional Head': r.regional_head,
                'Total Award Achievers': r.total_awards,
                'Inputs Given (Completed)': r.completed_awards,
                'Pending Inputs': r.pending_awards,
                'Completion %': r.pct.toFixed(1) + '%',
                'Status': r.status === 'completed' ? '100% Completed' : (r.status === 'in_progress' ? 'In Progress' : 'Not Started')
            }}));

            if (typeof XLSX !== 'undefined') {{
                const ws = XLSX.utils.json_to_sheet(rows);
                const wb = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(wb, ws, `${{brandTag}}_Region_Status`);
                XLSX.writeFile(wb, `${{brandTag}}_Region_Submission_Status_Sep_2026.xlsx`);
                showToast(`${{brandTag.replace('_', ' ')}} Region status exported! 📊`, '✅');
            }}
        }}

        // ==============================================
        // SEPARATE BRAND EXCEL EXPORTS (EXIUM MUPS / CORALCAL / BOTH)
        // ==============================================
        function exportBrandExcel(scope = 'admin', brandMode = 'exium') {{
            let exList = DB.achievers_exium;
            let coList = DB.achievers_coral;
            let calcList = DB.all_territories;
            let scopeTag = 'National';

            if (scope === 'region') {{
                if (!currentRegionName) {{
                    showToast('Please open a region first!', '⚠️');
                    return;
                }}
                exList = exList.filter(x => x.region === currentRegionName);
                coList = coList.filter(x => x.region === currentRegionName);
                calcList = calcList.filter(x => x.region_name === currentRegionName);
                scopeTag = `Region_${{currentRegionName.replace(/[^A-Za-z0-9]+/g, '_')}}`;
            }} else if (scope === 'zone') {{
                const zoneObj = DB.zones.find(z => z.sap_zone_code === currentActiveZoneCode);
                if (!zoneObj) {{
                    showToast('Please select a zone first!', '⚠️');
                    return;
                }}
                exList = exList.filter(x => x.sap_zone_code === currentActiveZoneCode);
                coList = coList.filter(x => x.sap_zone_code === currentActiveZoneCode);
                calcList = calcList.filter(x => x.sap_zone_code === currentActiveZoneCode);
                scopeTag = `Zone_${{zoneObj.zone_name.replace(/[^A-Za-z0-9]+/g, '_')}}`;
            }}

            const formatBrandAchieverRow = (a) => {{
                const ch = savedChoices[a.id] || {{}};
                const isCanc = Boolean(ch.cancelled);
                const voucher = isCanc ? 'CANCELLED' : (ch.voucher || 'Not Selected');
                const status = isCanc ? 'Cancelled' : (ch.voucher ? 'Complete' : 'Pending');
                const activeAward = isCanc ? 0 : (a.award || 0);

                return {{
                    'Brand': a.brand_label,
                    'Zone': a.zone,
                    'SAP Zone Code': a.sap_zone_code,
                    'Zonal Head': a.zonal_head,
                    'Region': a.region,
                    'SAP Region Code': a.sap_region_code,
                    'Regional Head': a.regional_head,
                    'Area Code': a.area_code,
                    'Territory Name': a.area_name,
                    'MIO SAP ID': a.mio_code,
                    'Sr. / MIO Name': a.mio_name,
                    'Designation': a.desig,
                    'Mobile': a.mobile || '',
                    'Seen Rx (Sep 26)': a.rx,
                    'Territory Aug 26 Sales': Math.round(a.terr_aug),
                    'Territory Sep 26 Sales': Math.round(a.terr_sep),
                    'Territory Sales Growth': Math.round(a.terr_growth),
                    'Territory Positive?': a.terr_pos ? 'Yes' : 'No',
                    'Brand Aug 26 Sales': Math.round(a.brand_aug),
                    'Brand Required Growth (Value)': Math.round(a.brand_req_growth),
                    'Brand Required Target': Math.round(a.brand_req_target),
                    'Brand Sep 26 Sales': Math.round(a.brand_sep),
                    'Brand Actual Growth (Value)': Math.round(a.brand_actual_growth),
                    'Brand Aug 26 Qty (Boxes)': a.brand_aug_box,
                    'Brand Sep 26 Qty (Boxes)': a.brand_sep_box,
                    'Brand Required Growth (Box Qty)': a.brand_req_box || 30,
                    'Brand Actual Growth (Box Qty)': a.brand_growth_box,
                    'Brand Growth Met?': a.brand_growth_ok ? 'Yes' : 'No',
                    'Calculated Award': a.award,
                    'Active Payable Award': activeAward,
                    'Award Tier': a.tier,
                    'Selected Gift Voucher': voucher,
                    'Status': status,
                    'RH/ZH Recommendation': isCanc ? `Not Recommended (${{ch.cancelled_by}})` : 'Recommended',
                    'Cancellation Reason': ch.cancel_reason || '',
                    'Timestamp (BDT)': formatToBDTime(ch.timestamp || '')
                }};
            }};

            const dateTag = new Date().toISOString().slice(0, 10);
            const wb = XLSX.utils.book_new();

            if (brandMode === 'exium' || brandMode === 'both') {{
                const exRows = exList.map(formatBrandAchieverRow);
                const wsEx = XLSX.utils.json_to_sheet(exRows);
                XLSX.utils.book_append_sheet(wb, wsEx, 'Exium_MUPS_Achievers_Choices');

                const exCalcRows = calcList.map((r, i) => ({{
                    'SL': i + 1,
                    'Zone': r.zone_name,
                    'SAP Zone': r.sap_zone_code,
                    'Zonal Head': r.zonal_head,
                    'Region': r.region_name,
                    'SAP Region': r.sap_region_code,
                    'Regional Head': r.regional_head,
                    'Area Code': r.area_code,
                    'Territory Name': r.area_name,
                    'MIO ID': r.mio_id,
                    'MIO Name': r.mio_name,
                    'Designation': r.desig,
                    'Exium MUPS Seen Rx': r.exium_rx,
                    'Rx >= 200?': r.exium_rx_ok ? 'Yes' : 'No',
                    'Territory Aug Sales': Math.round(r.terr_aug_val),
                    'Territory Sep Sales': Math.round(r.terr_sep_val),
                    'Territory Growth': Math.round(r.terr_growth_val),
                    'Territory Positive?': r.terr_pos ? 'Yes' : 'No',
                    'Exium MUPS Aug Sales': Math.round(r.exium_aug_val),
                    'Exium MUPS Req Growth (Value)': Math.round(r.exium_req_growth),
                    'Exium MUPS Req Target': Math.round(r.exium_req_target),
                    'Exium MUPS Sep Sales': Math.round(r.exium_sep_val),
                    'Exium MUPS Actual Growth (Value)': Math.round(r.exium_actual_growth),
                    'Exium MUPS TP Price': 659.67,
                    'Exium MUPS Aug Qty (Boxes)': r.exium_aug_box,
                    'Exium MUPS Sep Qty (Boxes)': r.exium_sep_box,
                    'Exium MUPS Req Growth (Box Qty)': r.exium_req_box || 30,
                    'Exium MUPS Actual Growth (Box Qty)': r.exium_growth_box,
                    'Exium MUPS Growth Met?': r.exium_growth_ok ? 'Yes' : 'No',
                    'Exium MUPS Award': r.exium_award,
                    'Exium MUPS Award Tier': r.exium_tier,
                    'Qualification Remarks': r.exium_reason
                }}));
                const wsExCalc = XLSX.utils.json_to_sheet(exCalcRows);
                XLSX.utils.book_append_sheet(wb, wsExCalc, 'Exium_MUPS_Full_Calc');
            }}

            if (brandMode === 'coral' || brandMode === 'both') {{
                const coRows = coList.map(formatBrandAchieverRow);
                const wsCo = XLSX.utils.json_to_sheet(coRows);
                XLSX.utils.book_append_sheet(wb, wsCo, 'Coralcal_Achievers_Choices');

                const coCalcRows = calcList.map((r, i) => ({{
                    'SL': i + 1,
                    'Zone': r.zone_name,
                    'SAP Zone': r.sap_zone_code,
                    'Zonal Head': r.zonal_head,
                    'Region': r.region_name,
                    'SAP Region': r.sap_region_code,
                    'Regional Head': r.regional_head,
                    'Area Code': r.area_code,
                    'Territory Name': r.area_name,
                    'MIO ID': r.mio_id,
                    'MIO Name': r.mio_name,
                    'Designation': r.desig,
                    'Coralcal Seen Rx': r.coral_rx,
                    'Rx >= 200?': r.coral_rx_ok ? 'Yes' : 'No',
                    'Territory Aug Sales': Math.round(r.terr_aug_val),
                    'Territory Sep Sales': Math.round(r.terr_sep_val),
                    'Territory Growth': Math.round(r.terr_growth_val),
                    'Territory Positive?': r.terr_pos ? 'Yes' : 'No',
                    'Coralcal Aug Sales': Math.round(r.coral_aug_val),
                    'Coralcal Req Growth (Value)': Math.round(r.coral_req_growth),
                    'Coralcal Req Target': Math.round(r.coral_req_target),
                    'Coralcal Sep Sales': Math.round(r.coral_sep_val),
                    'Coralcal Actual Growth (Value)': Math.round(r.coral_actual_growth),
                    'Coralcal TP Price': 637.18,
                    'Coralcal Aug Qty (Boxes)': r.coral_aug_box,
                    'Coralcal Sep Qty (Boxes)': r.coral_sep_box,
                    'Coralcal Req Growth (Box Qty)': r.coral_req_box || 30,
                    'Coralcal Actual Growth (Box Qty)': r.coral_growth_box,
                    'Coralcal Growth Met?': r.coral_growth_ok ? 'Yes' : 'No',
                    'Coralcal Award': r.coral_award,
                    'Coralcal Award Tier': r.coral_tier,
                    'Qualification Remarks': r.coral_reason
                }}));
                const wsCoCalc = XLSX.utils.json_to_sheet(coCalcRows);
                XLSX.utils.book_append_sheet(wb, wsCoCalc, 'Coralcal_Full_Calculation');
            }}

            const prefix = brandMode === 'exium' ? 'Exium_MUPS_Award_Data' : (brandMode === 'coral' ? 'Coralcal_Award_Data' : 'Combined_Award_Data');
            XLSX.writeFile(wb, `${{prefix}}_${{scopeTag}}_Sep_2026_${{dateTag}}.xlsx`);
            showToast(`Exported ${{prefix.replace(/_/g, ' ')}} (.xlsx)!`, '📊');
        }}

        // ==============================================
        // LOCK, RESET & CLOUD SYNC FUNCTIONS
        // ==============================================
        function updateSubmissionLockUI() {{
            const banner = document.getElementById('regview-locked-banner');
            const badge = document.getElementById('admin-lock-badge');
            const toggleBtn = document.getElementById('admin-toggle-lock-btn');

            if (banner) {{
                if (isSubmissionsLocked) banner.classList.remove('hidden');
                else banner.classList.add('hidden');
            }}
            if (badge) {{
                if (isSubmissionsLocked) {{
                    badge.className = 'px-2.5 py-0.5 rounded-full text-[10px] font-black bg-rose-100 text-rose-800 border border-rose-300';
                    badge.textContent = '🔒 Input OFF (Locked / Read-Only)';
                }} else {{
                    badge.className = 'px-2.5 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800 border border-emerald-300';
                    badge.textContent = '🟢 Input ON (Active)';
                }}
            }}
            if (toggleBtn) {{
                if (isSubmissionsLocked) {{
                    toggleBtn.className = 'w-full py-2 px-3 rounded-xl text-xs font-black transition flex items-center justify-center gap-2 shadow-xs bg-emerald-600 hover:bg-emerald-700 text-white';
                    toggleBtn.innerHTML = '<span>🔓 Turn ON Input (Allow Submissions)</span>';
                }} else {{
                    toggleBtn.className = 'w-full py-2 px-3 rounded-xl text-xs font-black transition flex items-center justify-center gap-2 shadow-xs bg-rose-600 hover:bg-rose-700 text-white';
                    toggleBtn.innerHTML = '<span>🔒 Turn OFF Input (Lock Submissions)</span>';
                }}
            }}
            if (currentRegionName) renderAchievers();
        }}

        async function toggleSubmissionLock() {{
            const targetState = !isSubmissionsLocked;
            if (!confirm(targetState ? 'Lock all Regional Head submissions into Read-Only mode?' : 'Unlock portal to allow Regional Head submissions?')) return;
            isSubmissionsLocked = targetState;
            localStorage.setItem(STORAGE_KEY_LOCKED, isSubmissionsLocked ? 'true' : 'false');
            updateSubmissionLockUI();
            if (cloudEndpoint) {{
                try {{
                    await fetch(cloudEndpoint, {{
                        method: 'POST',
                        mode: 'no-cors',
                        headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
                        body: JSON.stringify({{ action: 'set_submission_lock', locked: isSubmissionsLocked }})
                    }});
                }} catch (e) {{}}
            }}
            showToast(isSubmissionsLocked ? 'Input Locked (Read-Only)' : 'Input Unlocked (Active)', isSubmissionsLocked ? '🔒' : '🔓');
        }}

        async function adminDeleteCurrentRegionData() {{
            let targetRegion = currentRegionName || prompt('Enter exact Region Name to reset:');
            if (!targetRegion || !DB.regions_map[targetRegion]) return;
            if (!confirm(`Reset all choices for Region "${{targetRegion}}" back to Pending?`)) return;

            const allReg = DB.achievers_exium.filter(a => a.region === targetRegion).concat(DB.achievers_coral.filter(a => a.region === targetRegion));
            allReg.forEach(a => delete savedChoices[a.id]);
            localStorage.setItem(STORAGE_KEY_CHOICES, JSON.stringify(savedChoices));
            if (cloudEndpoint) {{
                try {{
                    await fetch(cloudEndpoint, {{
                        method: 'POST',
                        mode: 'no-cors',
                        headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
                        body: JSON.stringify({{ action: 'delete_region_data', region: targetRegion }})
                    }});
                }} catch (e) {{}}
            }}
            if (currentRegionName === targetRegion) {{
                renderAchievers();
                updateRegionProgress();
            }}
            refreshAdminStats();
            showToast(`Region "${{targetRegion}}" reset!`, '🗑️');
        }}

        async function adminDeleteAllNationalData() {{
            const typed = prompt('To confirm permanent deletion of all choices, type "DELETE":');
            if (typed !== 'DELETE') return;
            savedChoices = {{}};
            localStorage.setItem(STORAGE_KEY_CHOICES, JSON.stringify(savedChoices));
            localStorage.setItem(STORAGE_KEY_QUEUE, '{{}}');
            if (cloudEndpoint) {{
                try {{
                    await fetch(cloudEndpoint, {{
                        method: 'POST',
                        mode: 'no-cors',
                        headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
                        body: JSON.stringify({{ action: 'delete_all_data' }})
                    }});
                }} catch (e) {{}}
            }}
            if (currentRegionName) {{
                renderAchievers();
                updateRegionProgress();
            }}
            refreshAdminStats();
            showToast('All National Choices Reset!', '🗑️');
        }}

        function getPendingQueue() {{
            try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY_QUEUE) || '{{}}'); }} catch (e) {{ return {{}}; }}
        }}

        function savePendingQueue(q) {{
            try {{ localStorage.setItem(STORAGE_KEY_QUEUE, JSON.stringify(q)); }} catch (e) {{}}
        }}

        function queueForUpload(achId, brand, area_code, mio_code, voucher, timestamp, action = 'save', cancelled = false, cancelled_by = '', cancel_reason = '') {{
            const q = getPendingQueue();
            const a = findAchieverById(achId) || {{}};
            q[achId] = {{
                id: achId,
                month: brand,
                brand,
                zone: a.zone || '',
                sap_zone_code: a.sap_zone_code || '',
                zonal_head: a.zonal_head || '',
                region: a.region || '',
                sap_region_code: a.sap_region_code || '',
                regional_head: a.regional_head || '',
                area_code,
                area_name: a.area_name || '',
                mio_code,
                mio_name: a.mio_name || '',
                desig: a.desig || '',
                mobile: a.mobile || '',
                rx: a.rx || 0,
                terr_pos: Boolean(a.terr_pos),
                brand_req_box: a.brand_req_box || 30,
                brand_growth_box: a.brand_growth_box !== undefined ? a.brand_growth_box : '',
                tier: a.tier || '',
                award: a.award || 0,
                voucher,
                timestamp,
                action,
                cancelled,
                cancelled_by: cancelled ? `Not Recommended (${{cancelled_by || 'Regional Head'}})` : 'Recommended',
                cancel_reason,
                clientTime: Date.now()
            }};
            savePendingQueue(q);
        }}

        let isFlushingQueue = false;
        async function flushPendingQueue() {{
            if (!cloudEndpoint || isFlushingQueue) return;
            const q = getPendingQueue();
            const batch = Object.values(q);
            if (batch.length === 0) return;

            isFlushingQueue = true;
            updateSyncStatusBadge('syncing');
            try {{
                const bodyStr = JSON.stringify({{ action: 'save_choices', choices: batch }});
                await fetch(cloudEndpoint, {{ method: 'POST', mode: 'no-cors', headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }}, body: bodyStr }});
                savePendingQueue({{}});
                updateSyncStatusBadge('synced');
            }} catch (e) {{
                updateSyncStatusBadge('pending');
            }} finally {{
                isFlushingQueue = false;
            }}
        }}

        let debounceFlushTimer = null;
        function triggerDebouncedFlush() {{
            clearTimeout(debounceFlushTimer);
            debounceFlushTimer = setTimeout(() => flushPendingQueue(), 350);
        }}

        let isSyncing = false;
        async function syncFromCloud(silent = false) {{
            if (!cloudEndpoint || isSyncing) return;
            isSyncing = true;
            updateSyncStatusBadge('syncing');
            try {{
                await flushPendingQueue();
                const url = cloudEndpoint + (cloudEndpoint.includes('?') ? '&' : '?') + 'action=fetch_data&t=' + Date.now();
                const res = await fetch(url);
                if (res.ok) {{
                    const json = await res.json();
                    if (json && json.status === 'success') {{
                        if (typeof json.submissions_locked === 'boolean') {{
                            isSubmissionsLocked = json.submissions_locked;
                            localStorage.setItem(STORAGE_KEY_LOCKED, isSubmissionsLocked ? 'true' : 'false');
                            updateSubmissionLockUI();
                        }}
                        if (json.reviews && typeof json.reviews === 'object') {{
                            Object.assign(savedReviews, json.reviews);
                            localStorage.setItem(STORAGE_KEY_REVIEWS, JSON.stringify(savedReviews));
                        }}
                        if (json.overrides && typeof json.overrides === 'object') {{
                            Object.assign(savedOverrides, json.overrides);
                            localStorage.setItem(STORAGE_KEY_OVERRIDES, JSON.stringify(savedOverrides));
                        }}
                        if (json.data) {{
                            const mergeBrand = (list, dict) => {{
                                list.forEach(a => {{
                                    const k = a.area_code + '_' + a.mio_code;
                                    const c = dict[k];
                                    if (c) {{
                                        if (c.voucher || c.cancelled) {{
                                            let cleanCancBy = String(c.cancelled_by || '');
                                            if (cleanCancBy.startsWith('Not Recommended (')) {{
                                                cleanCancBy = cleanCancBy.replace('Not Recommended (', '').replace(/\\)$/, '');
                                            }} else if (cleanCancBy === 'Recommended' || cleanCancBy === 'Not Recommended') {{
                                                cleanCancBy = c.cancelled ? 'Regional Head' : '';
                                            }}
                                            savedChoices[a.id] = {{
                                                voucher: c.voucher || '',
                                                timestamp: c.timestamp || '',
                                                status: c.cancelled ? 'Cancelled' : 'Complete',
                                                cancelled: Boolean(c.cancelled),
                                                cancelled_by: cleanCancBy,
                                                cancel_reason: c.cancel_reason || ''
                                            }};
                                        }} else if (c.status === 'Pending') {{
                                            delete savedChoices[a.id];
                                        }}
                                    }}
                                }});
                            }};
                            mergeBrand(DB.achievers_exium, json.data.Exium_2026 || json.data.Exium_Sep_2026 || {{}});
                            mergeBrand(DB.achievers_coral, json.data.Coralcal_2026 || json.data.Coralcal_Sep_2026 || {{}});
                            localStorage.setItem(STORAGE_KEY_CHOICES, JSON.stringify(savedChoices));
                            if (currentRegionName) {{ renderAchievers(); updateRegionProgress(); }}
                            if (isAdminUnlocked) refreshAdminStats();
                        }}
                    }}
                }}
                updateSyncStatusBadge('synced');
                if (!silent) showToast('Synced with Google Sheet!', '☁️');
            }} catch (e) {{
                updateSyncStatusBadge('ready');
            }} finally {{
                isSyncing = false;
            }}
        }}

        function updateSyncStatusBadge(state) {{
            const elDesk = document.getElementById('header-sync-status');
            const dotDesk = document.getElementById('header-sync-dot');
            if (!elDesk || !dotDesk) return;
            if (state === 'syncing') {{
                elDesk.textContent = 'Syncing...';
                dotDesk.className = 'w-2 h-2 rounded-full bg-blue-500 animate-ping';
            }} else if (state === 'synced') {{
                elDesk.textContent = 'Synced';
                dotDesk.className = 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse';
            }} else {{
                elDesk.textContent = 'Ready';
                dotDesk.className = 'w-2 h-2 rounded-full bg-emerald-500';
            }}
        }}

        function onHeaderCloudSyncClick() {{
            if (cloudEndpoint) syncFromCloud(false);
            else showToast('All selections saved in browser storage!', '💾');
        }}

        function saveAdminEndpoint() {{
            const val = document.getElementById('admin-endpoint-input').value.trim();
            cloudEndpoint = val;
            localStorage.setItem(STORAGE_KEY_ENDPOINT, val);
            const statusBadge = document.getElementById('admin-endpoint-status');
            if (statusBadge) {{
                if (val) statusBadge.classList.remove('hidden');
                else statusBadge.classList.add('hidden');
            }}
            if (val) syncFromCloud(false);
            showToast(val ? 'Google Sheet Endpoint Saved & Connected!' : 'Endpoint Cleared', '⚙️');
        }}

        function copyGoogleAppsScriptCode() {{
            const code = DB.apps_script_code || '';
            if (!code) return;
            navigator.clipboard.writeText(code).then(() => {{
                showToast('Google Apps Script code copied to clipboard! Paste into Extensions > Apps Script.', '📋');
            }}).catch(() => {{
                alert('Please open Google_Apps_Script_Award_Backend.js from the folder.');
            }});
        }}

        async function manualSaveSync() {{
            localStorage.setItem(STORAGE_KEY_CHOICES, JSON.stringify(savedChoices));
            if (cloudEndpoint) await flushPendingQueue();
            showToast('All selections saved!', '💾');
        }}

        function copyShareableLink() {{
            const urlToShare = cloudEndpoint
                ? ( window.location.origin + window.location.pathname + '?api=' + encodeURIComponent(cloudEndpoint) )
                : MASKED_PORTAL_URL;
            navigator.clipboard.writeText(urlToShare).then(() => {{
                showToast('Shareable Link copied!', '📋');
            }}).catch(() => {{
                prompt('Copy link:', urlToShare);
            }});
        }}

        function showToast(msg, icon = '✅') {{
            const t = document.getElementById('toast-box');
            document.getElementById('toast-text').textContent = msg;
            document.getElementById('toast-icon').textContent = icon;
            t.classList.remove('translate-x-32', 'opacity-0', 'pointer-events-none');
            setTimeout(() => {{
                t.classList.add('translate-x-32', 'opacity-0', 'pointer-events-none');
            }}, 3000);
        }}
    </script>
</body>
</html>
"""

    OUT_INDEX.write_text(html_content, encoding="utf-8")
    OUT_PORTAL.write_text(html_content, encoding="utf-8")
    print(f"Built {OUT_INDEX} ({OUT_INDEX.stat().st_size:,} bytes)")
    print(f"Built {OUT_PORTAL} ({OUT_PORTAL.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build_portal()
