const SHEET_EXIUM = "Exium_Achievers_Sep_2026";
const SHEET_CORALCAL = "Coralcal_Achievers_Sep_2026";

const HEADERS = [
  "SL",
  "Brand",
  "Zone Name",
  "SAP Zone Code",
  "Zonal Head",
  "Region Name",
  "SAP Region Code",
  "Regional Head",
  "SAP Area Code",
  "Territory Name",
  "SAP MIO Code",
  "Sr. / MIO Name",
  "Designation",
  "Mobile Number",
  "Seen Rx (Sep 26)",
  "Territory Sales Positive?",
  "Required Growth (Box Qty)",
  "Actual Growth (Box Qty)",
  "Award Tier",
  "Calculated Award",
  "Active Payable Award",
  "Selected Gift Voucher",
  "Status",
  "RH/ZH Recommendation",
  "Cancelled By",
  "Cancellation Reason",
  "Timestamp (BDT)"
];

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
  const upper = str.toUpperCase();
  if ((upper.indexOf(" AM") !== -1 || upper.indexOf(" PM") !== -1) && str.indexOf("-") !== -1) {
    return str;
  }
  const parsed = new Date(str);
  if (!isNaN(parsed.getTime())) {
    return Utilities.formatDate(parsed, "Asia/Dhaka", "dd-MMM-yyyy hh:mm:ss a");
  }
  return str;
}

function getOrCreateBrandSheet(ss, isExium) {
  const primaryName = isExium ? SHEET_EXIUM : SHEET_CORALCAL;
  const fallbackName = isExium ? "Award_Exium_Sep_2026" : "Award_Coralcal_Sep_2026";
  let sheet = ss.getSheetByName(primaryName) || ss.getSheetByName(fallbackName);

  if (!sheet) {
    sheet = ss.insertSheet(primaryName);
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
    const headerRange = sheet.getRange(1, 1, 1, HEADERS.length);
    headerRange.setFontWeight("bold");
    headerRange.setBackground(isExium ? "#1E40AF" : "#6D28D9");
    headerRange.setFontColor("#FFFFFF");
    sheet.setFrozenRows(1);
  } else if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
    const headerRange = sheet.getRange(1, 1, 1, HEADERS.length);
    headerRange.setFontWeight("bold");
    headerRange.setBackground(isExium ? "#1E40AF" : "#6D28D9");
    headerRange.setFontColor("#FFFFFF");
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function getSheetColMap(sheet) {
  const lastCol = Math.max(sheet.getLastColumn(), HEADERS.length);
  const headerRow = sheet.getRange(1, 1, 1, lastCol).getValues()[0];

  const map = {
    colRegion: 6,
    colArea: 9,
    colMio: 11,
    colAward: 20,
    colActiveAward: 21,
    colVoucher: 22,
    colStatus: 23,
    colRec: 24,
    colCancBy: 25,
    colReason: 26,
    colTimestamp: 27
  };

  for (let i = 0; i < headerRow.length; i++) {
    const h = String(headerRow[i] || "").trim().toLowerCase();
    const c = i + 1;
    if (h === "region name" || h === "region") map.colRegion = c;
    else if (h.indexOf("area code") !== -1) map.colArea = c;
    else if (h.indexOf("mio code") !== -1 || h === "mio sap id") map.colMio = c;
    else if (h === "calculated award" || h === "award amount") map.colAward = c;
    else if (h === "active payable award") map.colActiveAward = c;
    else if (h.indexOf("voucher") !== -1) map.colVoucher = c;
    else if (h === "status" || h === "submission status") map.colStatus = c;
    else if (h.indexOf("recommendation") !== -1) map.colRec = c;
    else if (h === "cancelled by") map.colCancBy = c;
    else if (h.indexOf("cancel reason") !== -1 || h.indexOf("cancellation reason") !== -1) map.colReason = c;
    else if (h.indexOf("timestamp") !== -1) map.colTimestamp = c;
  }
  return map;
}

function doGet(e) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const props = PropertiesService.getScriptProperties();
    const isLocked = props.getProperty("SUBMISSIONS_LOCKED") === "true";

    const exiumMap = {};
    const coralMap = {};

    const readSheetIntoMap = function(isExium, targetObj) {
      const primaryName = isExium ? SHEET_EXIUM : SHEET_CORALCAL;
      const fallbackName = isExium ? "Award_Exium_Sep_2026" : "Award_Coralcal_Sep_2026";
      const sheet = ss.getSheetByName(primaryName) || ss.getSheetByName(fallbackName);
      if (!sheet || sheet.getLastRow() < 2) return;

      const data = sheet.getDataRange().getValues();
      const cols = getSheetColMap(sheet);

      for (let i = 1; i < data.length; i++) {
        const row = data[i];
        const areaCode = String(row[cols.colArea - 1] || "").trim();
        const mioCode = String(row[cols.colMio - 1] || "").trim();
        if (!areaCode) continue;

        const voucher = String(row[cols.colVoucher - 1] || "").trim();
        const status = String(row[cols.colStatus - 1] || "").trim();
        const rec = String(row[cols.colRec - 1] || "Recommended").trim();
        const cancBy = String(row[cols.colCancBy - 1] || "").trim();
        const reason = String(row[cols.colReason - 1] || "").trim();
        const timestamp = normalizeToBDTimestamp(row[cols.colTimestamp - 1]);

        const isCancelled = (
          status === "Cancelled" ||
          voucher === "CANCELLED" ||
          rec.toLowerCase().indexOf("not recommended") !== -1
        );

        if (voucher || isCancelled || timestamp || status === "Pending") {
          const key = areaCode + "_" + mioCode;
          targetObj[key] = {
            voucher: isCancelled ? "" : (voucher === "Not Selected" ? "" : voucher),
            timestamp: timestamp,
            status: isCancelled ? "Cancelled" : (voucher && voucher !== "Not Selected" ? "Complete" : "Pending"),
            cancelled: isCancelled,
            cancelled_by: cancBy || (isCancelled ? "Regional Head" : ""),
            cancel_reason: reason
          };
        }
      }
    };

    readSheetIntoMap(true, exiumMap);
    readSheetIntoMap(false, coralMap);

    const reviewsJson = props.getProperty("REVIEWS_DATA") || "{}";
    const overridesJson = props.getProperty("OVERRIDES_DATA") || "{}";
    let parsedReviews = {};
    let parsedOverrides = {};
    try { parsedReviews = JSON.parse(reviewsJson); } catch (e) {}
    try { parsedOverrides = JSON.parse(overridesJson); } catch (e) {}

    return ContentService.createTextOutput(
      JSON.stringify({
        status: "success",
        submissions_locked: isLocked,
        data: {
          Exium_2026: exiumMap,
          Coralcal_2026: coralMap,
          Exium_Sep_2026: exiumMap,
          Coralcal_Sep_2026: coralMap
        },
        reviews: parsedReviews,
        overrides: parsedOverrides
      })
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ status: "error", message: err.toString() })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.tryLock(10000);
  try {
    const payload = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const props = PropertiesService.getScriptProperties();

    if (payload.action === "set_submission_lock") {
      const lockState = payload.locked ? "true" : "false";
      props.setProperty("SUBMISSIONS_LOCKED", lockState);
      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", submissions_locked: Boolean(payload.locked) })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    if (payload.action === "delete_all_data") {
      [true, false].forEach(function(isExium) {
        const sheet = getOrCreateBrandSheet(ss, isExium);
        const lastRow = sheet.getLastRow();
        if (lastRow < 2) return;
        const cols = getSheetColMap(sheet);
        const numRows = lastRow - 1;
        sheet.getRange(2, cols.colVoucher, numRows, 1).clearContent();
        sheet.getRange(2, cols.colStatus, numRows, 1).setValue("Pending");
        sheet.getRange(2, cols.colRec, numRows, 1).setValue("Recommended");
        sheet.getRange(2, cols.colCancBy, numRows, 1).clearContent();
        sheet.getRange(2, cols.colReason, numRows, 1).clearContent();
        sheet.getRange(2, cols.colTimestamp, numRows, 1).clearContent();
      });
      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", message: "All national data reset" })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    if (payload.action === "delete_region_data" && payload.region) {
      const targetReg = String(payload.region).trim().toLowerCase();
      [true, false].forEach(function(isExium) {
        const sheet = getOrCreateBrandSheet(ss, isExium);
        const lastRow = sheet.getLastRow();
        if (lastRow < 2) return;
        const data = sheet.getDataRange().getValues();
        const cols = getSheetColMap(sheet);
        for (let i = 1; i < data.length; i++) {
          const rowReg = String(data[i][cols.colRegion - 1] || "").trim().toLowerCase();
          if (rowReg === targetReg) {
            const rIdx = i + 1;
            sheet.getRange(rIdx, cols.colVoucher).clearContent();
            sheet.getRange(rIdx, cols.colStatus).setValue("Pending");
            sheet.getRange(rIdx, cols.colRec).setValue("Recommended");
            sheet.getRange(rIdx, cols.colCancBy).clearContent();
            sheet.getRange(rIdx, cols.colReason).clearContent();
            sheet.getRange(rIdx, cols.colTimestamp).clearContent();
          }
        }
      });
      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", message: "Region data reset" })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    if (payload.action === "save_choices" && Array.isArray(payload.choices)) {
      let updatedCount = 0;

      payload.choices.forEach(function(item) {
        const brandKey = String(item.brand || item.month || "");
        const isExium = (
          brandKey.toLowerCase().indexOf("exium") !== -1 ||
          String(item.id || "").indexOf("EXIUM_") === 0
        );
        const sheet = getOrCreateBrandSheet(ss, isExium);
        const lastRow = sheet.getLastRow();
        const data = lastRow >= 1 ? sheet.getDataRange().getValues() : [];
        const cols = getSheetColMap(sheet);

        const targetArea = String(item.area_code || "").trim();
        const targetMio = String(item.mio_code || "").trim();
        const bdTime = normalizeToBDTimestamp(item.timestamp) || getBDTimestampServer();

        const isCancelled = Boolean(
          item.cancelled ||
          item.action === "cancel" ||
          item.status === "Cancelled"
        );
        const cleanVoucher = isCancelled
          ? "CANCELLED"
          : (item.action === "remove" || item.action === "restore" ? "" : String(item.voucher || "").trim());
        const statusVal = isCancelled ? "Cancelled" : (cleanVoucher ? "Complete" : "Pending");
        const recVal = isCancelled ? "Not Recommended" : "Recommended";
        const cancByVal = isCancelled ? String(item.cancelled_by || "Regional Head") : "";
        const reasonVal = isCancelled ? String(item.cancel_reason || "") : "";
        const awardAmt = Number(item.award || 0);
        const activeAwardAmt = isCancelled ? 0 : awardAmt;

        let foundRowIndex = -1;
        for (let i = 1; i < data.length; i++) {
          const rowArea = String(data[i][cols.colArea - 1] || "").trim();
          const rowMio = String(data[i][cols.colMio - 1] || "").trim();
          if (rowArea === targetArea && (!targetMio || rowMio === targetMio)) {
            foundRowIndex = i + 1;
            break;
          }
        }

        if (foundRowIndex > 0) {
          sheet.getRange(foundRowIndex, cols.colActiveAward).setValue(activeAwardAmt);
          sheet.getRange(foundRowIndex, cols.colVoucher).setValue(cleanVoucher);
          sheet.getRange(foundRowIndex, cols.colStatus).setValue(statusVal);
          sheet.getRange(foundRowIndex, cols.colRec).setValue(recVal);
          sheet.getRange(foundRowIndex, cols.colCancBy).setValue(cancByVal);
          sheet.getRange(foundRowIndex, cols.colReason).setValue(reasonVal);
          const tsCell = sheet.getRange(foundRowIndex, cols.colTimestamp);
          tsCell.setNumberFormat("@");
          tsCell.setValue(bdTime);
          updatedCount++;
        } else {
          const newSl = Math.max(1, sheet.getLastRow());
          const newRow = [
            newSl,
            isExium ? "Exium MUPS" : "Coralcal-D/DX/Vita",
            item.zone || "",
            item.sap_zone_code || "",
            item.zonal_head || "",
            item.region || "",
            item.sap_region_code || "",
            item.regional_head || "",
            targetArea,
            item.area_name || "",
            targetMio,
            item.mio_name || "",
            item.desig || "",
            item.mobile || "",
            item.rx || 0,
            item.terr_pos ? "Yes" : "No",
            item.brand_req_box || 30,
            item.brand_growth_box !== undefined ? item.brand_growth_box : "",
            item.tier || "",
            awardAmt,
            activeAwardAmt,
            cleanVoucher,
            statusVal,
            recVal,
            cancByVal,
            reasonVal,
            bdTime
          ];
          sheet.appendRow(newRow);
          const appendedRow = sheet.getLastRow();
          const tsCell = sheet.getRange(appendedRow, 27);
          tsCell.setNumberFormat("@");
          tsCell.setValue(bdTime);
          updatedCount++;
        }
      });

      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", updated: updatedCount })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    if (payload.action === "save_review" && payload.review) {
      const rev = payload.review;
      const reviewsJson = props.getProperty("REVIEWS_DATA") || "{}";
      let reviewsObj = {};
      try { reviewsObj = JSON.parse(reviewsJson); } catch (e) {}
      reviewsObj[rev.id] = rev;
      props.setProperty("REVIEWS_DATA", JSON.stringify(reviewsObj));

      try {
        const revHeaders = ["Timestamp (BDT)", "Status", "Brand", "Area Code", "Territory Name", "MIO SAP ID", "MIO Name", "Designation", "Mobile", "Region", "Zone", "Dispute Category", "Remarks", "Submitter Role", "Submitter Name", "Contact Mobile"];
        let revSheet = ss.getSheetByName("Data_Reviews");
        if (!revSheet) {
          revSheet = ss.insertSheet("Data_Reviews");
          revSheet.getRange(1, 1, 1, revHeaders.length).setValues([revHeaders]);
          const hRange = revSheet.getRange(1, 1, 1, revHeaders.length);
          hRange.setFontWeight("bold");
          hRange.setBackground("#D97706");
          hRange.setFontColor("#FFFFFF");
          revSheet.setFrozenRows(1);
        }
        revSheet.appendRow([
          normalizeToBDTimestamp(rev.timestamp) || getBDTimestampServer(),
          rev.status || "pending",
          rev.brand_label || rev.brand || "",
          rev.area_code || "",
          rev.area_name || "",
          rev.mio_code || "",
          rev.mio_name || "",
          rev.desig || "",
          rev.mobile || "",
          rev.region || "",
          rev.zone || "",
          rev.dispute_category || "",
          rev.remarks || "",
          rev.submitter_role || "",
          rev.submitter_name || "",
          rev.contact_mobile || ""
        ]);
      } catch (eRevSheet) {}

      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", message: "Review request recorded" })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    if (payload.action === "delete_review" && payload.review_id) {
      const reviewsJson = props.getProperty("REVIEWS_DATA") || "{}";
      let reviewsObj = {};
      try { reviewsObj = JSON.parse(reviewsJson); } catch (e) {}
      delete reviewsObj[payload.review_id];
      props.setProperty("REVIEWS_DATA", JSON.stringify(reviewsObj));
      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", message: "Review deleted" })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    if (payload.action === "save_manual_override" && payload.override) {
      const ov = payload.override;
      const overridesJson = props.getProperty("OVERRIDES_DATA") || "{}";
      let overridesObj = {};
      try { overridesObj = JSON.parse(overridesJson); } catch (e) {}
      if (Number(ov.award) > 0) {
        overridesObj[ov.id] = ov;
      } else {
        delete overridesObj[ov.id];
      }
      props.setProperty("OVERRIDES_DATA", JSON.stringify(overridesObj));

      try {
        const isExium = (ov.brand && ov.brand.toLowerCase().indexOf("exium") !== -1) || String(ov.id).indexOf("EXIUM_") === 0;
        const sheet = getOrCreateBrandSheet(ss, isExium);
        const lastRow = sheet.getLastRow();
        const data = lastRow >= 1 ? sheet.getDataRange().getValues() : [];
        const cols = getSheetColMap(sheet);
        const targetArea = String(ov.area_code || "").trim();
        const targetMio = String(ov.mio_code || "").trim();
        const awardVal = Number(ov.award || 0);

        let foundRow = -1;
        for (let i = 1; i < data.length; i++) {
          const rowArea = String(data[i][cols.colArea - 1] || "").trim();
          const rowMio = String(data[i][cols.colMio - 1] || "").trim();
          if (rowArea === targetArea && (!targetMio || rowMio === targetMio)) {
            foundRow = i + 1;
            break;
          }
        }
        if (foundRow > 0) {
          sheet.getRange(foundRow, cols.colAward).setValue(awardVal);
          sheet.getRange(foundRow, cols.colActiveAward).setValue(awardVal);
          sheet.getRange(foundRow, cols.colReason).setValue(ov.reason || "Admin Manual Grant");
        } else if (awardVal > 0) {
          const newSl = Math.max(1, sheet.getLastRow());
          sheet.appendRow([
            newSl,
            isExium ? "Exium MUPS" : "Coralcal-D/DX/Vita",
            ov.zone || "",
            "",
            "",
            ov.region || "",
            "",
            "",
            targetArea,
            ov.area_name || "",
            targetMio,
            ov.mio_name || "",
            ov.desig || "",
            ov.mobile || "",
            ov.rx || 0,
            "Yes (Manual)",
            30,
            "",
            ov.tier || "Manual Grant",
            awardVal,
            awardVal,
            "",
            "Pending",
            "Recommended",
            "",
            ov.reason || "Admin Manual Grant",
            getBDTimestampServer()
          ]);
        }
      } catch (eOvSheet) {}

      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", message: "Manual override recorded" })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    return ContentService.createTextOutput(
      JSON.stringify({ status: "error", message: "Invalid action" })
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ status: "error", message: err.toString() })
    ).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
