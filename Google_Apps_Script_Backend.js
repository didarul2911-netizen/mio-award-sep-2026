/**
 * ============================================================================
 * SEPTEMBER 2026 AWARD CHOICE PORTAL — GOOGLE APPS SCRIPT BACKEND
 * ============================================================================
 * Separate Brand Tabs:
 *   1. Award_Exium_Sep_2026     (brand key: Exium_2026)
 *   2. Award_Coralcal_Sep_2026  (brand key: Coralcal_2026)
 *
 * Instructions:
 *   1. Import Exium_Award_Calculation_Sep_2026.xlsx or September_2026_Award_Master_Calculation.xlsx
 *      into Google Sheets so it has tabs:
 *      - Award_Exium_Sep_2026
 *      - Award_Coralcal_Sep_2026
 *   2. Open Extensions -> Apps Script, paste this code, and Deploy -> New deployment -> Web app
 *      (Execute as: Me, Who has access: Anyone).
 *   3. Paste the Web App URL into the Admin Panel of the September 2026 Portal.
 * ============================================================================
 */

const SHEET_MAP = {
  'Exium_2026': 'Award_Exium_Sep_2026',
  'Coralcal_2026': 'Award_Coralcal_Sep_2026'
};

function doGet(e) {
  const action = (e && e.parameter && e.parameter.action) ? e.parameter.action : 'fetch_data';
  if (action === 'fetch_data') {
    return fetchAllData();
  }
  return jsonResponse({ status: 'ok', message: 'September 2026 Award Backend Active' });
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(25000);
  try {
    const payload = JSON.parse(e.postData.contents || '{}');
    const action = payload.action || '';

    if (action === 'save_choices' && Array.isArray(payload.choices)) {
      const updated = saveBatchChoices(payload.choices);
      return jsonResponse({ status: 'success', updated: updated });
    }
    return jsonResponse({ status: 'error', message: 'Unknown action: ' + action });
  } catch (err) {
    return jsonResponse({ status: 'error', message: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function fetchAllData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const data = {
    Exium_2026: readBrandSheet(ss.getSheetByName(SHEET_MAP.Exium_2026)),
    Coralcal_2026: readBrandSheet(ss.getSheetByName(SHEET_MAP.Coralcal_2026))
  };
  return jsonResponse({ status: 'success', data: data });
}

function readBrandSheet(sheet) {
  const result = {};
  if (!sheet) return result;
  const rows = sheet.getDataRange().getValues();
  if (rows.length < 2) return result;

  const headers = rows[0].map(h => String(h).trim().toLowerCase());
  const idxArea = headers.findIndex(h => h.includes('area code') || h.includes('tty'));
  const idxMio = headers.findIndex(h => h.includes('mio code') || h.includes('mio id'));
  const idxVoucher = headers.findIndex(h => h.includes('selected gift voucher'));
  const idxStatus = headers.findIndex(h => h === 'status');
  const idxTime = headers.findIndex(h => h.includes('timestamp'));
  const idxRhRec = headers.findIndex(h => h.includes('rh recommendation'));
  const idxRhReason = headers.findIndex(h => h.includes('rh cancel reason'));
  const idxZhRec = headers.findIndex(h => h.includes('zh recommendation'));
  const idxZhReason = headers.findIndex(h => h.includes('zh cancel reason'));

  for (let i = 1; i < rows.length; i++) {
    const r = rows[i];
    const area = idxArea >= 0 ? String(r[idxArea]).trim() : '';
    const mio = idxMio >= 0 ? String(r[idxMio]).trim() : '';
    if (!area) continue;
    const key = area + '_' + mio;
    const voucher = idxVoucher >= 0 ? String(r[idxVoucher]).trim() : '';
    const status = idxStatus >= 0 ? String(r[idxStatus]).trim() : 'Pending';
    const timestamp = idxTime >= 0 ? String(r[idxTime]).trim() : '';
    const rhRec = idxRhRec >= 0 ? String(r[idxRhRec]).trim() : '';
    const zhRec = idxZhRec >= 0 ? String(r[idxZhRec]).trim() : '';
    const rhReason = idxRhReason >= 0 ? String(r[idxRhReason]).trim() : '';
    const zhReason = idxZhReason >= 0 ? String(r[idxZhReason]).trim() : '';

    const cancelled = (status.toLowerCase() === 'cancelled' || rhRec.toLowerCase().includes('not') || zhRec.toLowerCase().includes('not'));
    const cancelledBy = zhRec.toLowerCase().includes('not') ? 'Zonal Head' : (rhRec.toLowerCase().includes('not') ? 'Regional Head' : '');
    const cancelReason = zhReason || rhReason || '';

    if (voucher || cancelled || status === 'Complete') {
      result[key] = {
        voucher: cancelled ? '' : voucher,
        status: cancelled ? 'Cancelled' : status,
        timestamp: timestamp,
        cancelled: cancelled,
        cancelled_by: cancelledBy,
        cancel_reason: cancelReason
      };
    }
  }
  return result;
}

function saveBatchChoices(choices) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let updatedCount = 0;

  choices.forEach(item => {
    const brandKey = item.brand || item.month || 'Exium_2026';
    const sheetName = SHEET_MAP[brandKey];
    if (!sheetName) return;
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) return;

    const rows = sheet.getDataRange().getValues();
    if (rows.length < 2) return;

    const headers = rows[0].map(h => String(h).trim().toLowerCase());
    const idxArea = headers.findIndex(h => h.includes('area code') || h.includes('tty'));
    const idxVoucher = headers.findIndex(h => h.includes('selected gift voucher'));
    const idxStatus = headers.findIndex(h => h === 'status');
    const idxTime = headers.findIndex(h => h.includes('timestamp'));
    const idxRhRec = headers.findIndex(h => h.includes('rh recommendation'));
    const idxRhReason = headers.findIndex(h => h.includes('rh cancel reason'));
    const idxZhRec = headers.findIndex(h => h.includes('zh recommendation'));
    const idxZhReason = headers.findIndex(h => h.includes('zh cancel reason'));

    const targetArea = String(item.area_code || '').trim();
    for (let i = 1; i < rows.length; i++) {
      const rowArea = idxArea >= 0 ? String(rows[i][idxArea]).trim() : '';
      if (rowArea === targetArea) {
        const rowNum = i + 1;
        if (item.cancelled) {
          if (idxVoucher >= 0) sheet.getRange(rowNum, idxVoucher + 1).setValue('');
          if (idxStatus >= 0) sheet.getRange(rowNum, idxStatus + 1).setValue('Cancelled');
          if (item.cancelled_by === 'Zonal Head') {
            if (idxZhRec >= 0) sheet.getRange(rowNum, idxZhRec + 1).setValue('Not Recommended');
            if (idxZhReason >= 0) sheet.getRange(rowNum, idxZhReason + 1).setValue(item.cancel_reason || '');
          } else {
            if (idxRhRec >= 0) sheet.getRange(rowNum, idxRhRec + 1).setValue('Not Recommended');
            if (idxRhReason >= 0) sheet.getRange(rowNum, idxRhReason + 1).setValue(item.cancel_reason || '');
          }
        } else {
          if (idxVoucher >= 0) sheet.getRange(rowNum, idxVoucher + 1).setValue(item.voucher || '');
          if (idxStatus >= 0) sheet.getRange(rowNum, idxStatus + 1).setValue(item.voucher ? 'Complete' : 'Pending');
          if (idxRhRec >= 0) sheet.getRange(rowNum, idxRhRec + 1).setValue('Recommended');
          if (idxRhReason >= 0) sheet.getRange(rowNum, idxRhReason + 1).setValue('');
          if (idxZhRec >= 0) sheet.getRange(rowNum, idxZhRec + 1).setValue('Recommended');
          if (idxZhReason >= 0) sheet.getRange(rowNum, idxZhReason + 1).setValue('');
        }
        if (idxTime >= 0) sheet.getRange(rowNum, idxTime + 1).setValue("'" + (item.timestamp || ''));
        updatedCount++;
        break;
      }
    }
  });

  return updatedCount;
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
