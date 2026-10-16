const SHEET_EXIUM = "Award_Exium_Sep_2026";
const SHEET_CORALCAL = "Award_Coralcal_Sep_2026";

const HEADERS = [
  "SL",
  "Zone Name",
  "SAP Zone Code",
  "Zonal Head",
  "Region Name",
  "SAP Region Code",
  "Regional Head",
  "SAP Area Code",
  "Area Name",
  "SAP MIO Code",
  "MIO Name",
  "Designation",
  "Seen Rx (Sep'26)",
  "Aug'26 Total Sales",
  "Sep'26 Total Sales",
  "Total Sales Positive?",
  "Aug'26 Brand Sales",
  "Sep'26 Brand Required",
  "Sep'26 Brand Actual",
  "Brand Growth Met?",
  "Award Tier",
  "Award Amount",
  "RH Recommendation",
  "RH Cancel Reason",
  "ZH Recommendation",
  "ZH Cancel Reason",
  "Selected Gift Voucher",
  "Status",
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

/**
 * ONE-CLICK RESTORE FUNCTION
 * Select "restoreAllRecommendationsInSheet" from the Apps Script toolbar dropdown and click "Run" (▶️).
 * This immediately fills "Recommended" in RH Recommendation (Col 23) and ZH Recommendation (Col 25)
 * for all rows in both Award_Exium_Sep_2026 and Award_Coralcal_Sep_2026 without deleting any data.
 */
function restoreAllRecommendationsInSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const summary = [];

  [true, false].forEach(function(isExium) {
    const sheet = getOrCreateBrandSheet(ss, isExium);
    const lastRow = sheet.getLastRow();
    if (lastRow < 2) return;
    const cols = getSheetColMap(sheet);
    const numRows = lastRow - 1;

    // Read current statuses to preserve any explicit cancellations
    const statusCol = cols.colStatus ? sheet.getRange(2, cols.colStatus, numRows, 1).getValues() : null;
    const rhRange = cols.colRhRec ? sheet.getRange(2, cols.colRhRec, numRows, 1) : null;
    const zhRange = cols.colZhRec ? sheet.getRange(2, cols.colZhRec, numRows, 1) : null;

    const rhVals = rhRange ? rhRange.getValues() : [];
    const zhVals = zhRange ? zhRange.getValues() : [];

    let updatedCount = 0;
    for (let i = 0; i < numRows; i++) {
      const st = statusCol ? String(statusCol[i][0] || "").trim() : "";
      if (st !== "Cancelled") {
        if (rhRange) {
          const curRh = String(rhVals[i][0] || "").trim();
          if (!curRh || curRh.toLowerCase().indexOf("not") === -1) {
            rhVals[i][0] = "Recommended";
          }
        }
        if (zhRange) {
          const curZh = String(zhVals[i][0] || "").trim();
          if (!curZh || curZh.toLowerCase().indexOf("not") === -1) {
            zhVals[i][0] = "Recommended";
          }
        }
        updatedCount++;
      }
    }

    if (rhRange) rhRange.setValues(rhVals);
    if (zhRange) zhRange.setValues(zhVals);

    summary.push(sheet.getName() + ": " + updatedCount + " rows restored");
  });

  SpreadsheetApp.getActiveSpreadsheet().toast(summary.join(", "), "Restore Complete", 6);
  Logger.log("DONE:\n" + summary.join("\n"));
  return summary.join("\n");
}

function getOrCreateBrandSheet(ss, isExium) {
  const primaryName = isExium ? "Award_Exium_Sep_2026" : "Award_Coralcal_Sep_2026";
  const fallbackName = isExium ? "Exium_Achievers_Sep_2026" : "Coralcal_Achievers_Sep_2026";
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
  const lastCol = Math.max(sheet.getLastColumn(), 30);
  const headerRow = sheet.getRange(1, 1, 1, lastCol).getValues()[0];

  const map = {
    colRegion: 0,
    colArea: 0,
    colMio: 0,
    colAward: 0,
    colActiveAward: 0,
    colVoucher: 0,
    colStatus: 0,
    colRhRec: 0,
    colRhReason: 0,
    colZhRec: 0,
    colZhReason: 0,
    colRec: 0,
    colCancBy: 0,
    colReason: 0,
    colTimestamp: 0
  };

  for (let i = 0; i < headerRow.length; i++) {
    const rawH = String(headerRow[i] || "").trim();
    if (!rawH) continue;
    const h = rawH.toLowerCase();
    const c = i + 1;

    // Specific RH and ZH columns first
    if (h.indexOf("rh rec") !== -1 || h.indexOf("regional head rec") !== -1 || h.indexOf("rm rec") !== -1) {
      map.colRhRec = c;
    } else if (h.indexOf("zh rec") !== -1 || h.indexOf("zonal head rec") !== -1 || h.indexOf("zm rec") !== -1) {
      map.colZhRec = c;
    } else if (h.indexOf("rh cancel") !== -1 || h.indexOf("regional head cancel") !== -1 || h.indexOf("rm cancel") !== -1) {
      map.colRhReason = c;
    } else if (h.indexOf("zh cancel") !== -1 || h.indexOf("zonal head cancel") !== -1 || h.indexOf("zm cancel") !== -1) {
      map.colZhReason = c;
    }
    // Generic / unified recommendation columns
    else if (h === "rh/zh recommendation" || h === "recommendation" || h === "award recommendation") {
      map.colRec = c;
    } else if (h === "cancelled by" || h.indexOf("cancelled by") !== -1) {
      map.colCancBy = c;
    } else if (h.indexOf("cancel reason") !== -1 || h.indexOf("cancellation reason") !== -1) {
      map.colReason = c;
    }
    // Standard data columns
    else if (h === "region name" || h === "region") {
      map.colRegion = c;
    } else if (h.indexOf("area code") !== -1) {
      map.colArea = c;
    } else if (h.indexOf("mio code") !== -1 || h === "mio sap id" || h === "mio id") {
      map.colMio = c;
    } else if (h === "calculated award" || h === "award amount" || h === "award") {
      map.colAward = c;
    } else if (h === "active payable award" || h === "active award") {
      map.colActiveAward = c;
    } else if (h.indexOf("voucher") !== -1) {
      map.colVoucher = c;
    } else if (h === "status" || h === "submission status") {
      map.colStatus = c;
    } else if (h.indexOf("timestamp") !== -1) {
      map.colTimestamp = c;
    }
  }

  // Fallbacks based on 29-column Award_Exium_Sep_2026 / Award_Coralcal_Sep_2026 sheet
  if (!map.colRegion) map.colRegion = 5;
  if (!map.colArea) map.colArea = 8;
  if (!map.colMio) map.colMio = 10;
  if (!map.colAward) map.colAward = 22;
  if (!map.colVoucher) map.colVoucher = 27;
  if (!map.colStatus) map.colStatus = 28;
  if (!map.colTimestamp) map.colTimestamp = 29;

  // Fallback for recommendation columns
  if (!map.colRhRec && !map.colRec) {
    if (headerRow.length >= 26) {
      map.colRhRec = 23;
      map.colRhReason = 24;
      map.colZhRec = 25;
      map.colZhReason = 26;
    } else {
      map.colRec = 24;
      map.colCancBy = 25;
      map.colReason = 26;
    }
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
      const primaryName = isExium ? "Award_Exium_Sep_2026" : "Award_Coralcal_Sep_2026";
      const fallbackName = isExium ? "Exium_Achievers_Sep_2026" : "Coralcal_Achievers_Sep_2026";
      const sheet = ss.getSheetByName(primaryName) || ss.getSheetByName(fallbackName);
      if (!sheet || sheet.getLastRow() < 2) return;

      const data = sheet.getDataRange().getValues();
      const cols = getSheetColMap(sheet);

      for (let i = 1; i < data.length; i++) {
        const row = data[i];
        const areaCode = String(row[cols.colArea - 1] || "").trim();
        const mioCode = String(row[cols.colMio - 1] || "").trim();
        if (!areaCode) continue;

        const voucher = cols.colVoucher ? String(row[cols.colVoucher - 1] || "").trim() : "";
        const status = cols.colStatus ? String(row[cols.colStatus - 1] || "").trim() : "";

        const rhRec = cols.colRhRec ? String(row[cols.colRhRec - 1] || "").trim() : "";
        const zhRec = cols.colZhRec ? String(row[cols.colZhRec - 1] || "").trim() : "";
        const rhReason = cols.colRhReason ? String(row[cols.colRhReason - 1] || "").trim() : "";
        const zhReason = cols.colZhReason ? String(row[cols.colZhReason - 1] || "").trim() : "";
        const genRec = cols.colRec ? String(row[cols.colRec - 1] || "").trim() : "";
        const genCancBy = cols.colCancBy ? String(row[cols.colCancBy - 1] || "").trim() : "";
        const genReason = cols.colReason ? String(row[cols.colReason - 1] || "").trim() : "";
        const timestamp = cols.colTimestamp ? normalizeToBDTimestamp(row[cols.colTimestamp - 1]) : "";

        const isRhCancelled = rhRec.toLowerCase().indexOf("not recommended") !== -1;
        const isZhCancelled = zhRec.toLowerCase().indexOf("not recommended") !== -1;
        const isGenCancelled = genRec.toLowerCase().indexOf("not recommended") !== -1;
        const isCancelled = (
          status === "Cancelled" ||
          voucher === "CANCELLED" ||
          isRhCancelled ||
          isZhCancelled ||
          isGenCancelled
        );

        let cancBy = "";
        let cancReason = "";
        if (isCancelled) {
          if (isZhCancelled) {
            cancBy = "Zonal Head";
            cancReason = zhReason || genReason;
          } else if (isRhCancelled) {
            cancBy = "Regional Head";
            cancReason = rhReason || genReason;
          } else if (genCancBy) {
            cancBy = genCancBy;
            cancReason = genReason;
          } else {
            cancBy = "Regional Head";
            cancReason = rhReason || zhReason || genReason;
          }
        }

        if (voucher || isCancelled || timestamp || status === "Pending") {
          const key = areaCode + "_" + mioCode;
          targetObj[key] = {
            voucher: isCancelled ? "" : (voucher === "Not Selected" ? "" : voucher),
            timestamp: timestamp,
            status: isCancelled ? "Cancelled" : (voucher && voucher !== "Not Selected" ? "Complete" : "Pending"),
            cancelled: isCancelled,
            cancelled_by: cancBy,
            cancel_reason: cancReason
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

    if (payload.action === "restore_recommendations") {
      const res = restoreAllRecommendationsInSheet();
      return ContentService.createTextOutput(
        JSON.stringify({ status: "success", message: res })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    if (payload.action === "delete_all_data") {
      [true, false].forEach(function(isExium) {
        const sheet = getOrCreateBrandSheet(ss, isExium);
        const lastRow = sheet.getLastRow();
        if (lastRow < 2) return;
        const cols = getSheetColMap(sheet);
        const numRows = lastRow - 1;

        if (cols.colVoucher) sheet.getRange(2, cols.colVoucher, numRows, 1).clearContent();
        if (cols.colStatus) sheet.getRange(2, cols.colStatus, numRows, 1).setValue("Pending");
        if (cols.colTimestamp) sheet.getRange(2, cols.colTimestamp, numRows, 1).clearContent();

        // Recommendations must ALWAYS be reset to "Recommended", never cleared or wiped out!
        if (cols.colRhRec) sheet.getRange(2, cols.colRhRec, numRows, 1).setValue("Recommended");
        if (cols.colRhReason) sheet.getRange(2, cols.colRhReason, numRows, 1).clearContent();
        if (cols.colZhRec) sheet.getRange(2, cols.colZhRec, numRows, 1).setValue("Recommended");
        if (cols.colZhReason) sheet.getRange(2, cols.colZhReason, numRows, 1).clearContent();

        if (cols.colRec && cols.colRec !== cols.colRhRec && cols.colRec !== cols.colZhRec) {
          sheet.getRange(2, cols.colRec, numRows, 1).setValue("Recommended");
        }
        if (cols.colCancBy && cols.colCancBy !== cols.colZhRec && cols.colCancBy !== cols.colRhRec) {
          sheet.getRange(2, cols.colCancBy, numRows, 1).clearContent();
        }
        if (cols.colReason && cols.colReason !== cols.colZhReason && cols.colReason !== cols.colRhReason) {
          sheet.getRange(2, cols.colReason, numRows, 1).clearContent();
        }
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
            if (cols.colVoucher) sheet.getRange(rIdx, cols.colVoucher).clearContent();
            if (cols.colStatus) sheet.getRange(rIdx, cols.colStatus).setValue("Pending");
            if (cols.colTimestamp) sheet.getRange(rIdx, cols.colTimestamp).clearContent();

            if (cols.colRhRec) sheet.getRange(rIdx, cols.colRhRec).setValue("Recommended");
            if (cols.colRhReason) sheet.getRange(rIdx, cols.colRhReason).clearContent();
            if (cols.colZhRec) sheet.getRange(rIdx, cols.colZhRec).setValue("Recommended");
            if (cols.colZhReason) sheet.getRange(rIdx, cols.colZhReason).clearContent();

            if (cols.colRec && cols.colRec !== cols.colRhRec && cols.colRec !== cols.colZhRec) {
              sheet.getRange(rIdx, cols.colRec).setValue("Recommended");
            }
            if (cols.colCancBy && cols.colCancBy !== cols.colZhRec && cols.colCancBy !== cols.colRhRec) {
              sheet.getRange(rIdx, cols.colCancBy).clearContent();
            }
            if (cols.colReason && cols.colReason !== cols.colZhReason && cols.colReason !== cols.colRhReason) {
              sheet.getRange(rIdx, cols.colReason).clearContent();
            }
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
        const cancByRaw = String(item.cancelled_by || "").toLowerCase();
        const isZH = (
          cancByRaw.indexOf("zonal") !== -1 ||
          cancByRaw.indexOf("zm") !== -1
        );
        const cleanVoucher = isCancelled
          ? "CANCELLED"
          : (item.action === "remove" || item.action === "restore" ? "" : String(item.voucher || "").trim());
        const statusVal = isCancelled ? "Cancelled" : (cleanVoucher ? "Complete" : "Pending");
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
          if (cols.colActiveAward) {
            sheet.getRange(foundRowIndex, cols.colActiveAward).setValue(activeAwardAmt);
          }
          if (cols.colVoucher) {
            sheet.getRange(foundRowIndex, cols.colVoucher).setValue(cleanVoucher);
          }
          if (cols.colStatus) {
            sheet.getRange(foundRowIndex, cols.colStatus).setValue(statusVal);
          }

          if (isCancelled) {
            if (isZH) {
              if (cols.colZhRec) sheet.getRange(foundRowIndex, cols.colZhRec).setValue("Not Recommended");
              if (cols.colZhReason) sheet.getRange(foundRowIndex, cols.colZhReason).setValue(reasonVal);
              if (cols.colRhRec) {
                const curRh = String(data[foundRowIndex - 1][cols.colRhRec - 1] || "").trim();
                if (!curRh) sheet.getRange(foundRowIndex, cols.colRhRec).setValue("Recommended");
              }
            } else {
              if (cols.colRhRec) sheet.getRange(foundRowIndex, cols.colRhRec).setValue("Not Recommended");
              if (cols.colRhReason) sheet.getRange(foundRowIndex, cols.colRhReason).setValue(reasonVal);
              if (cols.colZhRec) {
                const curZh = String(data[foundRowIndex - 1][cols.colZhRec - 1] || "").trim();
                if (!curZh) sheet.getRange(foundRowIndex, cols.colZhRec).setValue("Recommended");
              }
            }
            if (cols.colRec && cols.colRec !== cols.colZhRec && cols.colRec !== cols.colRhRec) {
              sheet.getRange(foundRowIndex, cols.colRec).setValue("Not Recommended");
            }
            if (cols.colCancBy && cols.colCancBy !== cols.colZhRec && cols.colCancBy !== cols.colRhRec) {
              sheet.getRange(foundRowIndex, cols.colCancBy).setValue(isZH ? "Zonal Head" : "Regional Head");
            }
            if (cols.colReason && cols.colReason !== cols.colZhReason && cols.colReason !== cols.colRhReason) {
              sheet.getRange(foundRowIndex, cols.colReason).setValue(reasonVal);
            }
          } else {
            // NOT cancelled - voucher selected, restored, or selection removed
            // Regional Head recommendation is Recommended:
            if (cols.colRhRec) sheet.getRange(foundRowIndex, cols.colRhRec).setValue("Recommended");
            if (cols.colRhReason) sheet.getRange(foundRowIndex, cols.colRhReason).clearContent();

            // Zonal Head recommendation: KEEP / SET AS "Recommended", NEVER CLEAR OR BLANK!
            if (cols.colZhRec) {
              const curZh = String(data[foundRowIndex - 1][cols.colZhRec - 1] || "").trim();
              if (!curZh || item.action === "restore") {
                sheet.getRange(foundRowIndex, cols.colZhRec).setValue("Recommended");
                if (cols.colZhReason) sheet.getRange(foundRowIndex, cols.colZhReason).clearContent();
              }
            }

            if (cols.colRec && cols.colRec !== cols.colZhRec && cols.colRec !== cols.colRhRec) {
              sheet.getRange(foundRowIndex, cols.colRec).setValue("Recommended");
            }
            if (cols.colCancBy && cols.colCancBy !== cols.colZhRec && cols.colCancBy !== cols.colRhRec) {
              sheet.getRange(foundRowIndex, cols.colCancBy).clearContent();
            }
            if (cols.colReason && cols.colReason !== cols.colZhReason && cols.colReason !== cols.colRhReason) {
              sheet.getRange(foundRowIndex, cols.colReason).clearContent();
            }
          }

          if (cols.colTimestamp) {
            const tsCell = sheet.getRange(foundRowIndex, cols.colTimestamp);
            tsCell.setNumberFormat("@");
            tsCell.setValue(bdTime);
          }
          updatedCount++;
        } else {
          // Dynamic append for new row
          const headerValues = lastRow >= 1 ? data[0] : HEADERS;
          const newRow = new Array(headerValues.length).fill("");
          const newSl = Math.max(1, lastRow);

          for (let cIdx = 0; cIdx < headerValues.length; cIdx++) {
            const h = String(headerValues[cIdx] || "").trim().toLowerCase();
            const colNum = cIdx + 1;

            if (colNum === 1 || h === "sl") {
              newRow[cIdx] = newSl;
            } else if (h === "brand") {
              newRow[cIdx] = isExium ? "Exium MUPS" : "Coralcal-D/DX/Vita";
            } else if (h === "zone name" || h === "zone") {
              newRow[cIdx] = item.zone || "";
            } else if (h.indexOf("zone code") !== -1) {
              newRow[cIdx] = item.sap_zone_code || "";
            } else if (h.indexOf("zonal head") !== -1) {
              newRow[cIdx] = item.zonal_head || "";
            } else if (h === "region name" || h === "region") {
              newRow[cIdx] = item.region || "";
            } else if (h.indexOf("region code") !== -1) {
              newRow[cIdx] = item.sap_region_code || "";
            } else if (h.indexOf("regional head") !== -1) {
              newRow[cIdx] = item.regional_head || "";
            } else if (h.indexOf("area code") !== -1) {
              newRow[cIdx] = targetArea;
            } else if (h === "area name" || h === "territory name") {
              newRow[cIdx] = item.area_name || "";
            } else if (h.indexOf("mio code") !== -1 || h === "mio sap id") {
              newRow[cIdx] = targetMio;
            } else if (h.indexOf("mio name") !== -1 || h.indexOf("sr. / mio") !== -1) {
              newRow[cIdx] = item.mio_name || "";
            } else if (h === "designation") {
              newRow[cIdx] = item.desig || "";
            } else if (h.indexOf("mobile") !== -1) {
              newRow[cIdx] = item.mobile || "";
            } else if (h.indexOf("rx") !== -1) {
              newRow[cIdx] = item.rx || 0;
            } else if (h.indexOf("total sales positive") !== -1 || h.indexOf("territory sales positive") !== -1) {
              newRow[cIdx] = item.terr_pos ? "Yes" : "No";
            } else if (h.indexOf("award tier") !== -1 || h === "tier") {
              newRow[cIdx] = item.tier || "";
            } else if (h === "calculated award" || h === "award amount" || h === "award") {
              newRow[cIdx] = awardAmt;
            } else if (h === "active payable award" || h === "active award") {
              newRow[cIdx] = activeAwardAmt;
            } else if (h.indexOf("voucher") !== -1) {
              newRow[cIdx] = cleanVoucher;
            } else if (h === "status" || h === "submission status") {
              newRow[cIdx] = statusVal;
            } else if (colNum === cols.colRhRec) {
              newRow[cIdx] = (isCancelled && !isZH) ? "Not Recommended" : "Recommended";
            } else if (colNum === cols.colRhReason) {
              newRow[cIdx] = (isCancelled && !isZH) ? reasonVal : "";
            } else if (colNum === cols.colZhRec) {
              newRow[cIdx] = (isCancelled && isZH) ? "Not Recommended" : "Recommended";
            } else if (colNum === cols.colZhReason) {
              newRow[cIdx] = (isCancelled && isZH) ? reasonVal : "";
            } else if (colNum === cols.colRec) {
              newRow[cIdx] = isCancelled ? "Not Recommended" : "Recommended";
            } else if (colNum === cols.colCancBy) {
              newRow[cIdx] = isCancelled ? (isZH ? "Zonal Head" : "Regional Head") : "";
            } else if (colNum === cols.colReason) {
              newRow[cIdx] = isCancelled ? reasonVal : "";
            } else if (colNum === cols.colTimestamp) {
              newRow[cIdx] = bdTime;
            }
          }

          sheet.appendRow(newRow);
          const appendedRow = sheet.getLastRow();
          if (cols.colTimestamp) {
            const tsCell = sheet.getRange(appendedRow, cols.colTimestamp);
            tsCell.setNumberFormat("@");
            tsCell.setValue(bdTime);
          }
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
          if (cols.colAward) sheet.getRange(foundRow, cols.colAward).setValue(awardVal);
          if (cols.colActiveAward) sheet.getRange(foundRow, cols.colActiveAward).setValue(awardVal);
          if (cols.colRhRec) sheet.getRange(foundRow, cols.colRhRec).setValue("Recommended");
          if (cols.colZhRec) sheet.getRange(foundRow, cols.colZhRec).setValue("Recommended");
          if (cols.colRec && cols.colRec !== cols.colZhRec) sheet.getRange(foundRow, cols.colRec).setValue("Recommended");
          if (cols.colReason) sheet.getRange(foundRow, cols.colReason).setValue(ov.reason || "Admin Manual Grant");
        } else if (awardVal > 0) {
          const newSl = Math.max(1, sheet.getLastRow());
          const headerValues = lastRow >= 1 ? data[0] : HEADERS;
          const newRow = new Array(headerValues.length).fill("");
          for (let cIdx = 0; cIdx < headerValues.length; cIdx++) {
            const h = String(headerValues[cIdx] || "").trim().toLowerCase();
            const colNum = cIdx + 1;
            if (colNum === 1 || h === "sl") newRow[cIdx] = newSl;
            else if (h === "brand") newRow[cIdx] = isExium ? "Exium MUPS" : "Coralcal-D/DX/Vita";
            else if (h === "zone name" || h === "zone") newRow[cIdx] = ov.zone || "";
            else if (h === "region name" || h === "region") newRow[cIdx] = ov.region || "";
            else if (h.indexOf("area code") !== -1) newRow[cIdx] = targetArea;
            else if (h === "area name" || h === "territory name") newRow[cIdx] = ov.area_name || "";
            else if (h.indexOf("mio code") !== -1 || h === "mio sap id") newRow[cIdx] = targetMio;
            else if (h.indexOf("mio name") !== -1 || h.indexOf("sr. / mio") !== -1) newRow[cIdx] = ov.mio_name || "";
            else if (h === "designation") newRow[cIdx] = ov.desig || "";
            else if (h.indexOf("mobile") !== -1) newRow[cIdx] = ov.mobile || "";
            else if (h.indexOf("rx") !== -1) newRow[cIdx] = ov.rx || 0;
            else if (h.indexOf("total sales positive") !== -1) newRow[cIdx] = "Yes (Manual)";
            else if (h.indexOf("award tier") !== -1 || h === "tier") newRow[cIdx] = ov.tier || "Manual Grant";
            else if (h === "calculated award" || h === "award amount" || h === "award") newRow[cIdx] = awardVal;
            else if (h === "active payable award" || h === "active award") newRow[cIdx] = awardVal;
            else if (h === "status" || h === "submission status") newRow[cIdx] = "Pending";
            else if (colNum === cols.colRhRec || colNum === cols.colZhRec || colNum === cols.colRec) newRow[cIdx] = "Recommended";
            else if (colNum === cols.colReason || colNum === cols.colRhReason) newRow[cIdx] = ov.reason || "Admin Manual Grant";
            else if (colNum === cols.colTimestamp) newRow[cIdx] = getBDTimestampServer();
          }
          sheet.appendRow(newRow);
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
