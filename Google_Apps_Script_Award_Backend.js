/**
 * ============================================================================
 * EXIUM MUPS & CORALCAL-D/DX/VITA - SEPTEMBER 2026 AWARD PORTAL BACKEND
 * ============================================================================
 * Supports:
 * 1. Dual-Brand Tabs: 'Award_Exium_Sep_2026' & 'Award_Coralcal_Sep_2026'
 * 2. Gift Voucher Selection & Deselection (with preserved BDT Timestamps)
 * 3. Regional Head (RH) & Zonal Head (ZH) Recommendation & Award Cancellation
 *    with Mandatory Reason logging
 * 4. Admin Submission Lock/Unlock & Region/National Reset
 * ============================================================================
 */

const SHEET_EXIUM = "Award_Exium_Sep_2026";
const SHEET_CORALCAL = "Award_Coralcal_Sep_2026";

function getBDTimestampServer() {
  return Utilities.formatDate(new Date(), "Asia/Dhaka", "dd-MMM-yyyy hh:mm:ss a");
}

function normalizeToBDTimestamp(val) {
  if (!val) return "";
  if (Object.prototype.toString.call(val) === "[object Date]") {
    if (isNaN(val.getTime())) return "";
    return Utilities.formatDate(val, "Asia/Dhaka", "dd-MMM-yyyy hh:mm:ss a");
  }
  const str = String(val).trim();
  if (!str) return "";
  if (/^\d{2}-[A-Za-z]{3}-\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+(AM|PM)/i.test(str)) {
    return str;
  }
  const parsed = new Date(str);
  if (!isNaN(parsed.getTime())) {
    return Utilities.formatDate(parsed, "Asia/Dhaka", "dd-MMM-yyyy hh:mm:ss a");
  }
  return str;
}

/**
 * Locate column indices dynamically (or fall back to default 29-column layout:
 * Col 5 = Region Name, Col 8 = SAP Area Code, Col 10 = SAP MIO Code,
 * Col 23 = RH Recommendation, Col 24 = RH Cancel Reason,
 * Col 25 = ZH Recommendation, Col 26 = ZH Cancel Reason,
 * Col 27 = Selected Gift Voucher, Col 28 = Status, Col 29 = Timestamp (BDT))
 */
function getSheetColMap(sheet) {
  const lastCol = Math.max(sheet.getLastColumn(), 29);
  const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];

  let colRegion = 5;
  let colArea = 8;
  let colMio = 10;
  let colRhRec = 23;
  let colRhReason = 24;
  let colZhRec = 25;
  let colZhReason = 26;
  let colVoucher = 27;
  let colStatus = 28;
  let colTimestamp = 29;

  for (let i = 0; i < headers.length; i++) {
    const h = String(headers[i] || "").trim().toLowerCase();
    const colNum = i + 1;
    if (h === "region name" || h === "current region") colRegion = colNum;
    else if (h === "sap area code" || h === "sap area code (tty)" || h.includes("area code")) colArea = colNum;
    else if (h === "sap mio code" || h.includes("mio code")) colMio = colNum;
    else if (h.includes("rh recommendation") || h.includes("regional head recommendation")) colRhRec = colNum;
    else if (h.includes("rh cancel reason") || h.includes("regional head cancel reason")) colRhReason = colNum;
    else if (h.includes("zh recommendation") || h.includes("zonal head recommendation")) colZhRec = colNum;
    else if (h.includes("zh cancel reason") || h.includes("zonal head cancel reason")) colZhReason = colNum;
    else if (h.includes("voucher") || h.includes("choice")) colVoucher = colNum;
    else if (h === "status" || h === "submission status") colStatus = colNum;
    else if (h.includes("timestamp")) colTimestamp = colNum;
  }

  return {
    colRegion,
    colArea,
    colMio,
    colRhRec,
    colRhReason,
    colZhRec,
    colZhReason,
    colVoucher,
    colStatus,
    colTimestamp
  };
}

function doGet(e) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const props = PropertiesService.getScriptProperties();
    const isLocked = props.getProperty("SUBMISSIONS_LOCKED") === "true";

    const result = {
      Exium_Sep_2026: {},
      Coralcal_Sep_2026: {}
    };

    const readBrandSheet = (sheetName, targetObj) => {
      const sheet = ss.getSheetByName(sheetName);
      if (!sheet) return;
      const data = sheet.getDataRange().getValues();
      if (data.length < 2) return;
      const cols = getSheetColMap(sheet);

      for (let i = 1; i < data.length; i++) {
        const row = data[i];
        const areaCode = String(row[cols.colArea - 1] || "").trim();
        const mioCode = String(row[cols.colMio - 1] || "").trim();
        const rhRec = String(row[cols.colRhRec - 1] || "Recommended").trim();
        const rhReason = String(row[cols.colRhReason - 1] || "").trim();
        const zhRec = String(row[cols.colZhRec - 1] || "Recommended").trim();
        const zhReason = String(row[cols.colZhReason - 1] || "").trim();
        const voucher = String(row[cols.colVoucher - 1] || "").trim();
        const status = String(row[cols.colStatus - 1] || "").trim();
        const rawTs = row[cols.colTimestamp - 1];
        const timestamp = normalizeToBDTimestamp(rawTs);

        const isCancelled = (status === "Cancelled" || rhRec === "Not Recommended" || zhRec === "Not Recommended");
        if (voucher || isCancelled || timestamp || status === "Pending") {
          const key = areaCode + "_" + mioCode;
          let cancelledBy = "";
          if (zhRec === "Not Recommended" && rhRec === "Not Recommended") cancelledBy = "Regional Head & Zonal Head";
          else if (zhRec === "Not Recommended") cancelledBy = "Zonal Head";
          else if (rhRec === "Not Recommended") cancelledBy = "Regional Head";

          targetObj[key] = {
            voucher: isCancelled ? "" : voucher,
            timestamp: timestamp,
            status: isCancelled ? "Cancelled" : (voucher ? "Complete" : "Pending"),
            rh_rec: rhRec || "Recommended",
            rh_reason: rhReason,
            zh_rec: zhRec || "Recommended",
            zh_reason: zhReason,
            cancelled_by: cancelledBy,
            cancel_reason: zhReason || rhReason || ""
          };
        }
      }
    };

    readBrandSheet(SHEET_EXIUM, result.Exium_Sep_2026);
    readBrandSheet(SHEET_CORALCAL, result.Coralcal_Sep_2026);

    return ContentService.createTextOutput(
      JSON.stringify({
        status: "success",
        submissions_locked: isLocked,
        data: result
      })
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ status: "error", message: err.toString() })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const props = PropertiesService.getScriptProperties();

    if (payload.action === "set_submission_lock") {
      const lockState = payload.locked ? "true" : "false";
      props.setProperty("SUBMISSIONS_LOCKED", lockState);
      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", submissions_locked: payload.locked })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    if (payload.action === "delete_all_data") {
      [SHEET_EXIUM, SHEET_CORALCAL].forEach(sName => {
        const sheet = ss.getSheetByName(sName);
        if (!sheet) return;
        const lastRow = sheet.getLastRow();
        if (lastRow < 2) return;
        const cols = getSheetColMap(sheet);
        const numRows = lastRow - 1;
        sheet.getRange(2, cols.colRhRec, numRows, 1).setValue("Recommended");
        sheet.getRange(2, cols.colRhReason, numRows, 1).clearContent();
        sheet.getRange(2, cols.colZhRec, numRows, 1).setValue("Recommended");
        sheet.getRange(2, cols.colZhReason, numRows, 1).clearContent();
        sheet.getRange(2, cols.colVoucher, numRows, 1).clearContent();
        sheet.getRange(2, cols.colStatus, numRows, 1).setValue("Pending");
        sheet.getRange(2, cols.colTimestamp, numRows, 1).clearContent();
      });
      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", message: "All national data reset" })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    if (payload.action === "save_choices" && Array.isArray(payload.choices)) {
      let updatedCount = 0;

      payload.choices.forEach(item => {
        const brandKey = item.brand || item.month || "";
        const isExium = (brandKey === "Exium_Sep_2026" || String(item.id || "").startsWith("EX_"));
        const sheetName = isExium ? SHEET_EXIUM : SHEET_CORALCAL;
        const sheet = ss.getSheetByName(sheetName);
        if (!sheet) return;

        const data = sheet.getDataRange().getValues();
        const cols = getSheetColMap(sheet);
        const targetArea = String(item.area_code || "").trim();
        const targetMio = String(item.mio_code || "").trim();

        for (let i = 1; i < data.length; i++) {
          const rowArea = String(data[i][cols.colArea - 1] || "").trim();
          const rowMio = String(data[i][cols.colMio - 1] || "").trim();

          if (rowArea === targetArea && (!targetMio || rowMio === targetMio)) {
            const rowIndex = i + 1;
            const bdTime = normalizeToBDTimestamp(item.timestamp) || getBDTimestampServer();

            const rhRec = item.rh_rec || "Recommended";
            const rhReason = item.rh_reason || "";
            const zhRec = item.zh_rec || "Recommended";
            const zhReason = item.zh_reason || "";
            const isCancelled = (item.status === "Cancelled" || item.action === "cancel" || rhRec === "Not Recommended" || zhRec === "Not Recommended");
            const voucherVal = isCancelled ? "CANCELLED" : String(item.voucher || "").trim();
            const statusVal = isCancelled ? "Cancelled" : (voucherVal ? "Complete" : "Pending");

            sheet.getRange(rowIndex, cols.colRhRec).setValue(rhRec);
            sheet.getRange(rowIndex, cols.colRhReason).setValue(rhReason);
            sheet.getRange(rowIndex, cols.colZhRec).setValue(zhRec);
            sheet.getRange(rowIndex, cols.colZhReason).setValue(zhReason);
            sheet.getRange(rowIndex, cols.colVoucher).setValue(isCancelled ? "" : voucherVal);
            sheet.getRange(rowIndex, cols.colStatus).setValue(statusVal);

            const tsCell = sheet.getRange(rowIndex, cols.colTimestamp);
            tsCell.setNumberFormat("@");
            tsCell.setValue(bdTime);

            updatedCount++;
            break;
          }
        }
      });

      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", updated: updatedCount })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    return ContentService.createTextOutput(
      JSON.stringify({ status: "error", message: "Invalid action" })
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ status: "error", message: err.toString() })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}
