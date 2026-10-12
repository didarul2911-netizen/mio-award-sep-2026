import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from decimal import Decimal, ROUND_HALF_UP
import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

SEP_DIR = r"G:\Exium\2026\Award\September"
CALC_DIR = os.path.join(SEP_DIR, "Calculation")

EXIUM_TP = 659.67
CORALCAL_TP = 637.18
REQ_GROWTH_BOX = 30

def round_half_up(val):
    if val is None:
        return None
    return int(Decimal(str(val)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def load_all_september_data():
    # 1. Load FF list (G:\Exium\2026\Award\September\FF list.xlsx)
    ff_path = os.path.join(SEP_DIR, "FF list.xlsx")
    wb_ff = openpyxl.load_workbook(ff_path, read_only=True, data_only=True)
    ws_ff = wb_ff[wb_ff.sheetnames[0]]
    ff_list = []
    ff_by_tty = {}
    for r_idx, row in enumerate(ws_ff.iter_rows(values_only=True), 1):
        if r_idx == 1 or row[9] is None:
            continue
        tty = int(row[9])
        rec = {
            'tty': tty,
            'area_code_str': str(row[8]).strip() if row[8] else '',
            'area_name': str(row[7]).strip(),
            'mio_code': int(row[1]) if row[1] is not None else 0,
            'mio_name': str(row[2]).strip() if row[2] else '',
            'designation': str(row[3]).strip() if row[3] else 'Medical Information Officer',
            'rm_code': int(row[11]) if row[11] is not None else 0,
            'rm_name': str(row[12]).strip() if row[12] else '',
            'region_name': str(row[16]).strip() if row[16] else '',
            'sap_region_code': int(row[18]) if row[18] is not None else 0,
            'zm_code': int(row[20]) if row[20] is not None else 0,
            'zm_name': str(row[21]).strip() if row[21] else '',
            'zone_name': str(row[25]).strip() if row[25] else '',
            'sap_zone_code': int(row[27]) if row[27] is not None else 0,
        }
        ff_list.append(rec)
        ff_by_tty[tty] = rec
    wb_ff.close()

    # 2. Load Exium & Coralcal Rx files
    def load_rx_file(fname):
        fpath = os.path.join(CALC_DIR, fname)
        wb = openpyxl.load_workbook(fpath, read_only=True, data_only=True)
        rx_map = {}
        for sname in wb.sheetnames:
            ws = wb[sname]
            for r_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
                if r_idx == 1 or len(row) < 8 or row[4] is None:
                    continue
                tty = int(float(row[4]))
                # Sum numeric values across all 30 days of September (Col I=index 8 to Col AL=index 37)
                daily_vals = []
                for x in row[8:38]:
                    if isinstance(x, (int, float)):
                        daily_vals.append(float(x))
                    else:
                        daily_vals.append(0.0)
                full_month_rx = int(round(sum(daily_vals)))
                cached_total = int(round(float(row[39]))) if len(row) > 39 and isinstance(row[39], (int, float)) else 0
                rx_map[tty] = {
                    'sheet': sname,
                    'row': r_idx,
                    'full_month_rx': full_month_rx,
                    'cached_total': cached_total,
                    'days_active': sum(1 for v in daily_vals if v > 0),
                }
        wb.close()
        return rx_map

    ex_rx_map = load_rx_file("Exium Award for September'26.xlsx")
    cc_rx_map = load_rx_file("Coralcal Award for September'26.xlsx")

    # 3. Load Value Growth Calculation - Team A.xlsx
    vg_path = os.path.join(CALC_DIR, "Value Growth Calculation - Team A.xlsx")
    wb_vg = openpyxl.load_workbook(vg_path, read_only=True, data_only=True)
    vg_ex_map = {}
    for r_idx, row in enumerate(wb_vg['Exium'].iter_rows(values_only=True), 1):
        if r_idx == 1 or row[3] is None:
            continue
        tty = int(row[3])
        vg_ex_map[tty] = {
            'aug_sales_vg': float(row[6]) if isinstance(row[6], (int, float)) else None,
            'req_sales_vg': float(row[7]) if isinstance(row[7], (int, float)) else None,
        }
    vg_cc_map = {}
    for r_idx, row in enumerate(wb_vg['Coralcal'].iter_rows(values_only=True), 1):
        if r_idx == 1 or row[3] is None:
            continue
        tty = int(row[3])
        vg_cc_map[tty] = {
            'aug_sales_vg': float(row[6]) if isinstance(row[6], (int, float)) else None,
            'req_sales_vg': float(row[7]) if isinstance(row[7], (int, float)) else None,
        }
    wb_vg.close()

    # 4. Load Award Data, RPL.xlsx (Gen A)
    rpl_path = os.path.join(CALC_DIR, "Award Data, RPL.xlsx")
    wb_rpl = openpyxl.load_workbook(rpl_path, read_only=True, data_only=True)
    rpl_by_area = {}
    for r_idx, row in enumerate(wb_rpl['Gen A'].iter_rows(values_only=True), 1):
        if r_idx <= 2 or len(row) < 15 or row[6] is None:
            continue
        aname = str(row[6]).strip()
        if aname == 'Total':
            continue
        rpl_by_area[aname] = {
            'aug_exium': float(row[9]) if isinstance(row[9], (int, float)) else None,
            'aug_coralcal': float(row[10]) if isinstance(row[10], (int, float)) else None,
            'aug_total': float(row[11]) if isinstance(row[11], (int, float)) else 0.0,
            'sep_exium': float(row[12]) if isinstance(row[12], (int, float)) else 0.0,
            'sep_coralcal': float(row[13]) if isinstance(row[13], (int, float)) else 0.0,
            'sep_total': float(row[14]) if isinstance(row[14], (int, float)) else 0.0,
            'rpl_mio_code': int(float(row[7])) if isinstance(row[7], (int, float)) else 0,
            'rpl_mio_name': str(row[8]).strip() if row[8] else '',
        }
    wb_rpl.close()

    # Combine all 1,856 territories
    combined = []
    for f in ff_list:
        tty = f['tty']
        aname = f['area_name']
        ex_r = ex_rx_map.get(tty, {'full_month_rx': 0, 'cached_total': 0, 'days_active': 0})
        cc_r = cc_rx_map.get(tty, {'full_month_rx': 0, 'cached_total': 0, 'days_active': 0})
        vg_e = vg_ex_map.get(tty, {'aug_sales_vg': None, 'req_sales_vg': None})
        vg_c = vg_cc_map.get(tty, {'aug_sales_vg': None, 'req_sales_vg': None})
        rpl_d = rpl_by_area.get(aname, {
            'aug_exium': None, 'aug_coralcal': None, 'aug_total': 0.0,
            'sep_exium': 0.0, 'sep_coralcal': 0.0, 'sep_total': 0.0,
            'rpl_mio_code': 0, 'rpl_mio_name': ''
        })

        # Criterion 1: Seen Rx >= 200 in Sep'26 full month
        ex_rx_val = ex_r['full_month_rx']
        cc_rx_val = cc_r['full_month_rx']
        ex_c1_rx = (ex_rx_val >= 200)
        cc_c1_rx = (cc_rx_val >= 200)

        # Criterion 2(b): Total Territory Sales Positive in Sep'26 over Aug'26
        # Note: Must have positive base in Aug'26 and Sep'26 > Aug'26
        aug_tot = rpl_d['aug_total'] or 0.0
        sep_tot = rpl_d['sep_total'] or 0.0
        tot_growth_val = sep_tot - aug_tot
        tot_sales_positive = (aug_tot > 0) and (sep_tot > aug_tot)

        # Criterion 2(c): Brand Growth in Equivalent Box Quantity (Dividing Value Growth by TP, rounded half-up >= 30 Boxes)
        ex_aug_val = rpl_d['aug_exium']
        ex_sep_val = rpl_d['sep_exium'] or 0.0
        ex_req_val = vg_e['req_sales_vg']
        ex_growth_val_raw = (ex_sep_val - ex_aug_val) if ex_aug_val is not None else None
        ex_growth_box = round_half_up(ex_growth_val_raw / EXIUM_TP) if ex_growth_val_raw is not None else None
        ex_req_box = REQ_GROWTH_BOX if ex_req_val is not None else None
        ex_growth_met = (ex_req_val is not None) and (ex_growth_box is not None) and (ex_growth_box >= REQ_GROWTH_BOX)

        cc_aug_val = rpl_d['aug_coralcal']
        cc_sep_val = rpl_d['sep_coralcal'] or 0.0
        cc_req_val = vg_c['req_sales_vg']
        cc_growth_val_raw = (cc_sep_val - cc_aug_val) if cc_aug_val is not None else None
        cc_growth_box = round_half_up(cc_growth_val_raw / CORALCAL_TP) if cc_growth_val_raw is not None else None
        cc_req_box = REQ_GROWTH_BOX if cc_req_val is not None else None
        cc_growth_met = (cc_req_val is not None) and (cc_growth_box is not None) and (cc_growth_box >= REQ_GROWTH_BOX)

        # Final Award Determination per Brand:
        # - If all 3 met (Rx >= 200 AND Total Sales Positive AND Brand Growth >= 30 Boxes) -> 3000
        # - Else if Rx >= 200 -> 1000
        # - Else -> 0 (No Award)
        ex_all3 = (ex_c1_rx and tot_sales_positive and ex_growth_met)
        ex_award = 3000 if ex_all3 else (1000 if ex_c1_rx else 0)
        ex_tier = "3,000 (Rx + Sales Growth)" if ex_all3 else ("1,000 (Rx >= 200 Only)" if ex_c1_rx else "No Award (Rx < 200)")

        cc_all3 = (cc_c1_rx and tot_sales_positive and cc_growth_met)
        cc_award = 3000 if cc_all3 else (1000 if cc_c1_rx else 0)
        cc_tier = "3,000 (Rx + Sales Growth)" if cc_all3 else ("1,000 (Rx >= 200 Only)" if cc_c1_rx else "No Award (Rx < 200)")

        rec = {
            **f,
            'ex_rx': ex_rx_val,
            'ex_c1_rx': ex_c1_rx,
            'cc_rx': cc_rx_val,
            'cc_c1_rx': cc_c1_rx,
            'aug_total': round(aug_tot, 2),
            'sep_total': round(sep_tot, 2),
            'tot_growth_val': round(tot_growth_val, 2),
            'tot_growth_pct': round((tot_growth_val / aug_tot) * 100, 2) if aug_tot > 0 else None,
            'tot_sales_positive': tot_sales_positive,
            'ex_aug': round(ex_aug_val, 2) if ex_aug_val is not None else None,
            'ex_aug_vg': int(round(vg_e['aug_sales_vg'])) if vg_e['aug_sales_vg'] is not None else None,
            'ex_req': int(round(ex_req_val)) if ex_req_val is not None else None,
            'ex_sep': round(ex_sep_val, 2),
            'ex_growth_val': round(ex_sep_val - ex_aug_val, 2) if ex_aug_val is not None else None,
            'ex_req_box': ex_req_box,
            'ex_growth_box': ex_growth_box,
            'ex_growth_met': ex_growth_met,
            'ex_all3': ex_all3,
            'ex_award': ex_award,
            'ex_tier': ex_tier,
            'cc_aug': round(cc_aug_val, 2) if cc_aug_val is not None else None,
            'cc_aug_vg': int(round(vg_c['aug_sales_vg'])) if vg_c['aug_sales_vg'] is not None else None,
            'cc_req': int(round(cc_req_val)) if cc_req_val is not None else None,
            'cc_sep': round(cc_sep_val, 2),
            'cc_growth_val': round(cc_sep_val - cc_aug_val, 2) if cc_aug_val is not None else None,
            'cc_req_box': cc_req_box,
            'cc_growth_box': cc_growth_box,
            'cc_growth_met': cc_growth_met,
            'cc_all3': cc_all3,
            'cc_award': cc_award,
            'cc_tier': cc_tier,
            'total_award': ex_award + cc_award,
        }
        combined.append(rec)

    return combined

def build_excel_workbooks(records):
    wb = openpyxl.Workbook()
    default_ws = wb.active

    # Styling definitions
    font_title = Font(name='Calibri', size=14, bold=True, color='FFFFFFFF')
    font_sec = Font(name='Calibri', size=11, bold=True, color='FF0F172A')
    font_hdr = Font(name='Calibri', size=11, bold=True, color='FF0F172A')
    font_hdr_w = Font(name='Calibri', size=11, bold=True, color='FFFFFFFF')
    font_data = Font(name='Calibri', size=11, bold=False)
    font_bold = Font(name='Calibri', size=11, bold=True)
    font_green = Font(name='Calibri', size=11, bold=True, color='FF065F46')
    font_blue = Font(name='Calibri', size=11, bold=True, color='FF1E40AF')
    font_red = Font(name='Calibri', size=11, bold=True, color='FF991B1B')

    fill_navy = PatternFill(start_color='FF1E293B', end_color='FF1E293B', fill_type='solid')
    fill_blue_hdr = PatternFill(start_color='FFCAEDFB', end_color='FFCAEDFB', fill_type='solid')
    fill_exium_hdr = PatternFill(start_color='FFDBEAFE', end_color='FFDBEAFE', fill_type='solid')
    fill_coral_hdr = PatternFill(start_color='FFEDE9FE', end_color='FFEDE9FE', fill_type='solid')
    fill_green = PatternFill(start_color='FFD1FAE5', end_color='FFD1FAE5', fill_type='solid')
    fill_blue_soft = PatternFill(start_color='FFE0F2FE', end_color='FFE0F2FE', fill_type='solid')
    fill_red_soft = PatternFill(start_color='FFFEE2E2', end_color='FFFEE2E2', fill_type='solid')
    fill_yellow = PatternFill(start_color='FFFEF9C3', end_color='FFFEF9C3', fill_type='solid')
    fill_total = PatternFill(start_color='FFF1F5F9', end_color='FFF1F5F9', fill_type='solid')

    thin = Side(style='thin', color='FFCBD5E1')
    border_all = Border(left=thin, right=thin, top=thin, bottom=thin)

    align_c = Alignment(horizontal='center', vertical='center')
    align_cw = Alignment(horizontal='center', vertical='center', wrap_text=True)
    align_l = Alignment(horizontal='left', vertical='center')
    align_r = Alignment(horizontal='right', vertical='center')

    # =========================================================================
    # SHEET 1: Summary_Dashboard
    # =========================================================================
    ws_sum = wb.create_sheet(title='Summary_Dashboard')
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum.merge_cells('A1:N1')
    ws_sum['A1'] = "EXIUM MUPS & CORALCAL-D/DX/VITA — SEPTEMBER 2026 RX & SALES AWARD CALCULATION SUMMARY"
    ws_sum['A1'].font = font_title
    ws_sum['A1'].fill = fill_navy
    ws_sum['A1'].alignment = align_c
    ws_sum.row_dimensions[1].height = 34

    # National KPI Comparison Table
    ws_sum.merge_cells('A3:F3')
    ws_sum['A3'] = "1. NATIONAL AWARD CALCULATION BREAKDOWN (SEPTEMBER 2026)"
    ws_sum['A3'].font = font_sec
    ws_sum['A3'].fill = fill_blue_hdr
    ws_sum.row_dimensions[3].height = 24

    sum_headers = ['SL', 'Criteria / Award Metric', 'Exium MUPS (Territories)', 'Exium Award Value', 'Coralcal-D/DX/Vita (Territories)', 'Coralcal Award Value']
    ws_sum.row_dimensions[4].height = 28
    for c_i, h in enumerate(sum_headers, 1):
        cell = ws_sum.cell(4, c_i, h)
        cell.font = font_hdr
        cell.fill = fill_blue_hdr
        cell.border = border_all
        cell.alignment = align_cw

    ex_3000 = sum(1 for r in records if r['ex_award'] == 3000)
    ex_1000 = sum(1 for r in records if r['ex_award'] == 1000)
    ex_0 = sum(1 for r in records if r['ex_award'] == 0)
    ex_rx_ok = sum(1 for r in records if r['ex_c1_rx'])
    ex_gr_ok = sum(1 for r in records if r['ex_growth_met'])

    cc_3000 = sum(1 for r in records if r['cc_award'] == 3000)
    cc_1000 = sum(1 for r in records if r['cc_award'] == 1000)
    cc_0 = sum(1 for r in records if r['cc_award'] == 0)
    cc_rx_ok = sum(1 for r in records if r['cc_c1_rx'])
    cc_gr_ok = sum(1 for r in records if r['cc_growth_met'])
    tot_pos_cnt = sum(1 for r in records if r['tot_sales_positive'])

    summary_rows = [
        (1, "Total Evaluated Territories (Gen-A)", len(records), "-", len(records), "-"),
        (2, "Criterion 1 Met: Seen Rx >= 200 in Sep'26 (Full Month)", ex_rx_ok, "-", cc_rx_ok, "-"),
        (3, "Criterion 2(b) Met: Total Territory Sales Positive (Sep'26 > Aug'26)", tot_pos_cnt, "-", tot_pos_cnt, "-"),
        (4, "Criterion 2(c) Met: Brand Sales >= Required Value (30 Box Growth)", ex_gr_ok, "-", cc_gr_ok, "-"),
        (5, "Tier 1 Achievers: 3,000 Award (All 3 Criteria Met: Rx + Territory + Brand Growth)", ex_3000, ex_3000 * 3000, cc_3000, cc_3000 * 3000),
        (6, "Tier 2 Achievers: 1,000 Award (Only Criterion 1 Met: Seen Rx >= 200)", ex_1000, ex_1000 * 1000, cc_1000, cc_1000 * 1000),
        (7, "Total Eligible Award Achievers (1,000 + 3,000)", ex_3000 + ex_1000, (ex_3000 * 3000) + (ex_1000 * 1000), cc_3000 + cc_1000, (cc_3000 * 3000) + (cc_1000 * 1000)),
        (8, "Not Eligible / No Award (Seen Rx < 200)", ex_0, 0, cc_0, 0),
    ]

    for idx, srow in enumerate(summary_rows, start=5):
        ws_sum.row_dimensions[idx].height = 22
        for c_i, val in enumerate(srow, 1):
            c = ws_sum.cell(idx, c_i, val)
            c.border = border_all
            c.font = font_bold if idx in (9, 10, 11) else font_data
            if idx == 9:
                c.fill = fill_green
            elif idx == 10:
                c.fill = fill_blue_soft
            elif idx == 11:
                c.fill = fill_yellow
            elif idx == 12:
                c.fill = fill_red_soft
            if c_i == 1:
                c.alignment = align_c
            elif c_i == 2:
                c.alignment = align_l
            else:
                c.alignment = align_c
                if isinstance(val, int):
                    c.number_format = '#,##0'

    # Zone-wise Breakdown Table starting at Row 15
    ws_sum.merge_cells('A15:N15')
    ws_sum['A15'] = "2. ZONE-WISE AWARD CALCULATION SUMMARY (35 ZONES)"
    ws_sum['A15'].font = font_sec
    ws_sum['A15'].fill = fill_blue_hdr
    ws_sum.row_dimensions[15].height = 24

    z_headers = [
        'SL', 'Zone Name', 'SAP Zone Code', 'Zonal Head', 'Total Territories',
        'Exium 3,000 Count', 'Exium 1,000 Count', 'Exium Total Achievers', 'Exium Award Amount',
        'Coralcal 3,000 Count', 'Coralcal 1,000 Count', 'Coralcal Total Achievers', 'Coralcal Award Amount',
        'Combined Total Award'
    ]
    ws_sum.row_dimensions[16].height = 30
    for c_i, h in enumerate(z_headers, 1):
        c = ws_sum.cell(16, c_i, h)
        c.font = font_hdr
        c.fill = fill_blue_hdr
        c.border = border_all
        c.alignment = align_cw

    zones_sorted = sorted(list({r['zone_name'] for r in records}))
    r_curr = 17
    for z_idx, zname in enumerate(zones_sorted, 1):
        z_recs = [r for r in records if r['zone_name'] == zname]
        z_code = z_recs[0]['sap_zone_code']
        z_head = z_recs[0]['zm_name']
        t_cnt = len(z_recs)
        ze_3 = sum(1 for r in z_recs if r['ex_award'] == 3000)
        ze_1 = sum(1 for r in z_recs if r['ex_award'] == 1000)
        ze_tot = ze_3 + ze_1
        ze_amt = ze_3 * 3000 + ze_1 * 1000
        zc_3 = sum(1 for r in z_recs if r['cc_award'] == 3000)
        zc_1 = sum(1 for r in z_recs if r['cc_award'] == 1000)
        zc_tot = zc_3 + zc_1
        zc_amt = zc_3 * 3000 + zc_1 * 1000
        z_comb = ze_amt + zc_amt

        row_vals = [z_idx, zname, z_code, z_head, t_cnt, ze_3, ze_1, ze_tot, ze_amt, zc_3, zc_1, zc_tot, zc_amt, z_comb]
        ws_sum.row_dimensions[r_curr].height = 21
        for c_i, v in enumerate(row_vals, 1):
            c = ws_sum.cell(r_curr, c_i, v)
            c.font = font_bold if c_i in (8, 9, 12, 13, 14) else font_data
            c.border = border_all
            c.alignment = align_l if c_i in (2, 4) else align_c
            if c_i >= 5 and isinstance(v, int):
                c.number_format = '#,##0'
        r_curr += 1

    # Total row for Zone table
    ws_sum.row_dimensions[r_curr].height = 24
    tot_zone_vals = [
        '', 'NATIONAL GRAND TOTAL', '', '', len(records),
        ex_3000, ex_1000, ex_3000 + ex_1000, ex_3000 * 3000 + ex_1000 * 1000,
        cc_3000, cc_1000, cc_3000 + cc_1000, cc_3000 * 3000 + cc_1000 * 1000,
        (ex_3000 * 3000 + ex_1000 * 1000) + (cc_3000 * 3000 + cc_1000 * 1000)
    ]
    for c_i, v in enumerate(tot_zone_vals, 1):
        c = ws_sum.cell(r_curr, c_i, v)
        c.font = font_bold
        c.fill = fill_yellow
        c.border = border_all
        c.alignment = align_l if c_i == 2 else align_c
        if c_i >= 5 and isinstance(v, int):
            c.number_format = '#,##0'

    sum_col_widths = [6, 36, 18, 26, 18, 18, 18, 20, 20, 18, 18, 20, 20, 22]
    for c_i, w in enumerate(sum_col_widths, 1):
        ws_sum.column_dimensions[get_column_letter(c_i)].width = w

    # =========================================================================
    # Helper to populate Brand Calculation Sheet (All 1,856 rows)
    # =========================================================================
    def create_brand_calc_sheet(sheet_title, brand_label, prefix, hdr_fill):
        ws = wb.create_sheet(title=sheet_title)
        ws.views.sheetView[0].showGridLines = True
        ws.freeze_panes = 'A2'

        headers = [
            'SL', 'Zone Name', 'SAP Zone Code', 'Zonal Head',
            'Region Name', 'SAP Region Code', 'Regional Head',
            'SAP Area Code (TTY)', 'Territory (Area Name)', 'SAP MIO Code', 'MIO / Sr. MIO Name', 'Designation',
            f"Sep'26 Seen Rx ({brand_label})", 'Criteria 1: Seen Rx >= 200?',
            "Aug'26 Total Territory Sales", "Sep'26 Total Territory Sales", "Total Territory Sales Diff",
            "Criteria 2(b): Total Territory Sales Positive?",
            f"Aug'26 {brand_label} Sales", f"Sep'26 {brand_label} Required Sales (30 Box Growth)",
            f"Sep'26 {brand_label} Actual Sales", f"{brand_label} Sales Diff (Actual - Req)",
            f"Criteria 2(c): {brand_label} Growth Met?",
            "All 3 Criteria Met (for 3,000)?",
            f"Eligible {brand_label} Award Tier", f"Award Amount ({brand_label})",
            "Regional Head Recommendation", "Regional Head Cancel Reason",
            "Zonal Head Recommendation", "Zonal Head Cancel Reason",
            "Final Award Status", "Selected Gift Voucher", "Submission Status", "Timestamp (BDT)"
        ]
        ws.row_dimensions[1].height = 36
        for c_i, h in enumerate(headers, 1):
            c = ws.cell(1, c_i, h)
            c.font = font_hdr
            c.fill = hdr_fill if c_i >= 13 else fill_blue_hdr
            c.border = border_all
            c.alignment = align_cw

        for idx, r in enumerate(records, start=2):
            ws.row_dimensions[idx].height = 22
            rx_val = r[f'{prefix}_rx']
            c1_ok = r[f'{prefix}_c1_rx']
            aug_tot = r['aug_total']
            sep_tot = r['sep_total']
            tot_diff = r['tot_growth_val']
            c2b_ok = r['tot_sales_positive']
            b_aug = r[f'{prefix}_aug']
            b_req = r[f'{prefix}_req']
            b_sep = r[f'{prefix}_sep']
            b_diff = round(b_sep - b_req, 2) if b_req is not None else None
            c2c_ok = r[f'{prefix}_growth_met']
            all3_ok = r[f'{prefix}_all3']
            tier_str = r[f'{prefix}_tier']
            aw_amt = r[f'{prefix}_award']

            row_vals = [
                idx - 1, r['zone_name'], r['sap_zone_code'], r['zm_name'],
                r['region_name'], r['sap_region_code'], r['rm_name'],
                r['tty'], r['area_name'], r['mio_code'], r['mio_name'], r['designation'],
                rx_val, 'Yes' if c1_ok else 'No',
                aug_tot, sep_tot, tot_diff,
                'Yes' if c2b_ok else ('No (New TTY)' if aug_tot == 0 else 'No'),
                b_aug if b_aug is not None else 'N/A (New TTY)',
                b_req if b_req is not None else 'N/A (New TTY)',
                b_sep,
                b_diff if b_diff is not None else 'N/A',
                'Yes' if c2c_ok else ('N/A (New TTY)' if b_req is None else 'No'),
                'Yes' if all3_ok else 'No',
                tier_str, aw_amt,
                'Recommended' if aw_amt > 0 else 'N/A', '',
                'Recommended' if aw_amt > 0 else 'N/A', '',
                'Eligible' if aw_amt > 0 else 'No Award',
                '', 'Pending' if aw_amt > 0 else 'N/A', ''
            ]

            for c_i, v in enumerate(row_vals, 1):
                c = ws.cell(idx, c_i, v)
                c.border = border_all
                c.font = font_data
                if c_i in (2, 4, 5, 7, 9, 11, 12, 25, 28, 30):
                    c.alignment = align_l
                elif c_i in (15, 16, 17, 19, 20, 21, 22):
                    c.alignment = align_r if isinstance(v, (int, float)) else align_c
                    if isinstance(v, (int, float)):
                        c.number_format = '#,##0'
                else:
                    c.alignment = align_c
                    if c_i in (13, 26) and isinstance(v, (int, float)):
                        c.number_format = '#,##0'

                # Highlight Award Amount & Tier
                if c_i in (25, 26):
                    if aw_amt == 3000:
                        c.fill = fill_green
                        c.font = font_green
                    elif aw_amt == 1000:
                        c.fill = fill_blue_soft
                        c.font = font_blue
                    else:
                        c.fill = fill_red_soft
                        c.font = font_red
                elif c_i in (14, 18, 23, 24):
                    if v == 'Yes':
                        c.font = font_green
                    elif str(v).startswith('No'):
                        c.font = font_red

        widths = [
            6, 18, 13, 24, 20, 14, 24, 14, 22, 13, 25, 24,
            15, 15, 18, 18, 18, 18, 18, 22, 18, 18, 18, 16,
            24, 16, 18, 22, 18, 22, 16, 22, 16, 22
        ]
        for c_i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(c_i)].width = w

    create_brand_calc_sheet('Exium_Calculation_All', 'Exium MUPS', 'ex', fill_exium_hdr)
    create_brand_calc_sheet('Coralcal_Calculation_All', 'Coralcal', 'cc', fill_coral_hdr)

    # =========================================================================
    # SHEET 4 & 5: Award_Exium_Sep_2026 & Award_Coralcal_Sep_2026 (Achievers Only, for Cloud Sync)
    # =========================================================================
    def create_achiever_cloud_sheet(sheet_title, brand_label, prefix, hdr_fill):
        ws = wb.create_sheet(title=sheet_title)
        ws.views.sheetView[0].showGridLines = True
        ws.freeze_panes = 'A2'

        headers = [
            'SL', 'Zone Name', 'SAP Zone Code', 'Zonal Head',
            'Region Name', 'SAP Region Code', 'Regional Head',
            'SAP Area Code', 'Area Name', 'SAP MIO Code', 'MIO Name', 'Designation',
            'Seen Rx (Sep\'26)', 'Aug\'26 Total Sales', 'Sep\'26 Total Sales', 'Total Sales Positive?',
            f'Aug\'26 {brand_label} Sales', f'Sep\'26 {brand_label} Required', f'Sep\'26 {brand_label} Actual',
            f'{brand_label} Growth Met?', 'Award Tier', 'Award Amount',
            'RH Recommendation', 'RH Cancel Reason',
            'ZH Recommendation', 'ZH Cancel Reason',
            'Selected Gift Voucher', 'Status', 'Timestamp (BDT)'
        ]
        ws.row_dimensions[1].height = 34
        for c_i, h in enumerate(headers, 1):
            c = ws.cell(1, c_i, h)
            c.font = font_hdr
            c.fill = hdr_fill
            c.border = border_all
            c.alignment = align_cw

        elig_recs = [r for r in records if r[f'{prefix}_award'] > 0]
        for idx, r in enumerate(elig_recs, start=2):
            ws.row_dimensions[idx].height = 22
            aw_amt = r[f'{prefix}_award']
            row_vals = [
                idx - 1, r['zone_name'], r['sap_zone_code'], r['zm_name'],
                r['region_name'], r['sap_region_code'], r['rm_name'],
                r['tty'], r['area_name'], r['mio_code'], r['mio_name'], r['designation'],
                r[f'{prefix}_rx'], r['aug_total'], r['sep_total'],
                'Yes' if r['tot_sales_positive'] else 'No',
                r[f'{prefix}_aug'] if r[f'{prefix}_aug'] is not None else 0,
                r[f'{prefix}_req'] if r[f'{prefix}_req'] is not None else 'N/A',
                r[f'{prefix}_sep'],
                'Yes' if r[f'{prefix}_growth_met'] else 'No',
                r[f'{prefix}_tier'], aw_amt,
                'Recommended', '',
                'Recommended', '',
                '', 'Pending', ''
            ]
            for c_i, v in enumerate(row_vals, 1):
                c = ws.cell(idx, c_i, v)
                c.border = border_all
                c.font = font_data
                if c_i in (2, 4, 5, 7, 9, 11, 12, 21, 24, 26, 27):
                    c.alignment = align_l
                elif c_i in (14, 15, 17, 18, 19):
                    c.alignment = align_r if isinstance(v, (int, float)) else align_c
                    if isinstance(v, (int, float)):
                        c.number_format = '#,##0'
                else:
                    c.alignment = align_c
                    if c_i in (13, 22) and isinstance(v, (int, float)):
                        c.number_format = '#,##0'
                if c_i in (21, 22):
                    c.fill = fill_green if aw_amt == 3000 else fill_blue_soft
                    c.font = font_green if aw_amt == 3000 else font_blue
                if c_i == 29:
                    c.number_format = '@'

        widths = [
            6, 18, 13, 24, 20, 14, 24, 14, 22, 13, 25, 24,
            15, 18, 18, 16, 18, 18, 18, 16, 24, 15,
            18, 22, 18, 22, 24, 14, 22
        ]
        for c_i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(c_i)].width = w

    create_achiever_cloud_sheet('Award_Exium_Sep_2026', 'Exium', 'ex', fill_exium_hdr)
    create_achiever_cloud_sheet('Award_Coralcal_Sep_2026', 'Coralcal', 'cc', fill_coral_hdr)

    # =========================================================================
    # SHEET 6: Combined_MIO_Summary (All 1,856 Territories Combined View)
    # =========================================================================
    ws_comb = wb.create_sheet(title='Combined_MIO_Summary')
    ws_comb.views.sheetView[0].showGridLines = True
    ws_comb.freeze_panes = 'A2'

    comb_headers = [
        'SL', 'Zone Name', 'SAP Zone Code', 'Zonal Head',
        'Region Name', 'SAP Region Code', 'Regional Head',
        'SAP Area Code (TTY)', 'Territory (Area Name)', 'SAP MIO Code', 'MIO / Sr. MIO Name',
        'Total Territory Sales Positive?',
        'Exium Seen Rx', 'Exium Growth Met?', 'Exium Award Tier', 'Exium Award',
        'Coralcal Seen Rx', 'Coralcal Growth Met?', 'Coralcal Award Tier', 'Coralcal Award',
        'Combined Total Award'
    ]
    ws_comb.row_dimensions[1].height = 34
    for c_i, h in enumerate(comb_headers, 1):
        c = ws_comb.cell(1, c_i, h)
        c.font = font_hdr
        c.fill = fill_blue_hdr
        c.border = border_all
        c.alignment = align_cw

    for idx, r in enumerate(records, start=2):
        ws_comb.row_dimensions[idx].height = 22
        row_vals = [
            idx - 1, r['zone_name'], r['sap_zone_code'], r['zm_name'],
            r['region_name'], r['sap_region_code'], r['rm_name'],
            r['tty'], r['area_name'], r['mio_code'], r['mio_name'],
            'Yes' if r['tot_sales_positive'] else 'No',
            r['ex_rx'], 'Yes' if r['ex_growth_met'] else 'No', r['ex_tier'], r['ex_award'],
            r['cc_rx'], 'Yes' if r['cc_growth_met'] else 'No', r['cc_tier'], r['cc_award'],
            r['total_award']
        ]
        for c_i, v in enumerate(row_vals, 1):
            c = ws_comb.cell(idx, c_i, v)
            c.border = border_all
            c.font = font_bold if c_i in (16, 20, 21) else font_data
            c.alignment = align_l if c_i in (2, 4, 5, 7, 9, 11, 15, 19) else align_c
            if c_i in (13, 16, 17, 20, 21) and isinstance(v, (int, float)):
                c.number_format = '#,##0'
            if c_i == 16 and r['ex_award'] > 0:
                c.fill = fill_green if r['ex_award'] == 3000 else fill_blue_soft
            if c_i == 20 and r['cc_award'] > 0:
                c.fill = fill_green if r['cc_award'] == 3000 else fill_blue_soft
            if c_i == 21 and r['total_award'] > 0:
                c.fill = fill_yellow

    comb_widths = [6, 18, 13, 24, 20, 14, 24, 14, 22, 13, 25, 18, 14, 16, 24, 15, 14, 16, 24, 15, 18]
    for c_i, w in enumerate(comb_widths, 1):
        ws_comb.column_dimensions[get_column_letter(c_i)].width = w

    wb.remove(default_ws)

    out_calc = os.path.join(CALC_DIR, "September_2026_Award_Calculation_Master.xlsx")
    out_master = os.path.join(SEP_DIR, "Exium_Award_Choice_Master_Sep_2026.xlsx")
    wb.save(out_calc)
    wb.save(out_master)
    print(f"Saved calculation master to:\n  1. {out_calc}\n  2. {out_master}")

if __name__ == '__main__':
    recs = load_all_september_data()
    build_excel_workbooks(recs)
    # Also save JSON cache for fast portal building
    json_path = os.path.join(SEP_DIR, "september_award_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(recs)} territory records to {json_path}")
