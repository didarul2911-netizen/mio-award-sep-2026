/**
 * ==============================================================================
 * Google Apps Script: Bulletproof "ONLY YOU" Range Protection (No Tab Lock Icon)
 * ==============================================================================
 * 
 * Features:
 * 1. NO LOCK ICON on tabs (Range Protection instead of Sheet Protection).
 * 2. STRICT "ONLY YOU" PERMISSION:
 *    - Columns A to H (MIO info), Row 1 Date Headers, and Columns AM:AN (Total)
 *      are strictly locked to ONLY YOU (the Owner/Admin).
 *    - Other accounts / editors CANNOT edit those cells (Google will show an error).
 * 3. Daily Rx Input Area (Columns I to AL, Rows 2 down) is UNLOCKED for collaborators.
 * 4. Includes Rate-Limit Protection (SpreadsheetApp.flush + sleep) so it does NOT
 *    crash with "Service Spreadsheets failed while accessing document".
 * 
 * Instructions:
 * 1. Open your Google Sheet.
 * 2. Go to "Extensions" > "Apps Script".
 * 3. Replace all existing code with this script.
 * 4. Click Save (Ctrl + S).
 * 5. Select "applyStrictProtectionNoLockIcon" and click "Run".
 * 6. Review and allow permissions if prompted.
 */

function applyStrictProtectionNoLockIcon() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ss.getSheets();
  const me = Session.getEffectiveUser();
  const owner = ss.getOwner();
  const ssEditors = ss.getEditors(); // All spreadsheet-level collaborators
  
  Logger.log("Starting protection for " + sheets.length + " sheets by user: " + me.getEmail());
  
  let successCount = 0;
  let failedSheets = [];
  
  for (let i = 0; i < sheets.length; i++) {
    const sheet = sheets[i];
    const sheetName = sheet.getName();
    
    try {
      // 1. Remove all old Sheet protections (removes lock icon on tab)
      const sheetProtections = sheet.getProtections(SpreadsheetApp.ProtectionType.SHEET);
      for (let j = 0; j < sheetProtections.length; j++) {
        sheetProtections[j].remove();
      }
      
      // 2. Remove all old Range protections (clean slate)
      const rangeProtections = sheet.getProtections(SpreadsheetApp.ProtectionType.RANGE);
      for (let j = 0; j < rangeProtections.length; j++) {
        rangeProtections[j].remove();
      }
      
      // Helper function to lock a range to "Only you"
      function lockRange(rangeA1, label) {
        const range = sheet.getRange(rangeA1);
        const p = range.protect().setDescription(sheetName + " - " + label);
        p.setWarningOnly(false);
        
        // Remove all editors from this protection rule -> flips to "Only you"
        p.removeEditors(p.getEditors());
        
        // Also remove any spreadsheet collaborators
        if (ssEditors && ssEditors.length > 0) {
          const others = ssEditors.filter(u => {
            const email = u.getEmail();
            return email !== me.getEmail() && (!owner || email !== owner.getEmail());
          });
          if (others.length > 0) {
            p.removeEditors(others);
          }
        }
        
        // Disable domain-wide editing
        if (p.canDomainEdit()) {
          p.setDomainEdit(false);
        }
      }
      
      // 3. Lock Columns A to H (MIO info)
      lockRange("A:H", "MIO Info");
      
      // 4. Lock Row 1 Date Headers (I1 to AL1)
      lockRange("I1:AL1", "Date Headers");
      
      // 5. Lock Columns AM & AN (Blank 31st Day & Total Formula)
      lockRange("AM:AN", "Blank & Total");
      
      successCount++;
      Logger.log("[" + (i + 1) + "/" + sheets.length + "] Protected: " + sheetName);
      
      // Flush and brief pause to prevent Google rate-limiting
      if ((i + 1) % 5 === 0) {
        SpreadsheetApp.flush();
        Utilities.sleep(300);
      } else {
        Utilities.sleep(150);
      }
      
    } catch (err) {
      Logger.log("Error on sheet " + sheetName + ": " + err.message);
      failedSheets.push(sheetName);
      // Wait 1 second before trying next sheet
      Utilities.sleep(1000);
    }
  }
  
  SpreadsheetApp.flush();
  
  let msg = "Success! " + successCount + " of " + sheets.length + " sheets configured.\n\n" +
            "✔ NO lock icon on any sheet tab.\n" +
            "✔ Restricted areas (A:H, I1:AL1, AM:AN) are strictly locked to 'ONLY YOU'.\n" +
            "✔ Collaborators can ONLY edit Columns I to AL (1-Sep to 30-Sep).\n";
            
  if (failedSheets.length > 0) {
    msg += "\n⚠️ " + failedSheets.length + " sheets had an error: " + failedSheets.join(", ") + "\n(You can run the script again to finish them).";
  }
  
  SpreadsheetApp.getUi().alert(msg);
}

/**
 * Optional: Run this if you want to wipe all protections on all sheets.
 */
function removeAllProtections() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ss.getSheets();
  
  for (let i = 0; i < sheets.length; i++) {
    const sheet = sheets[i];
    const sp = sheet.getProtections(SpreadsheetApp.ProtectionType.SHEET);
    sp.forEach(p => p.remove());
    const rp = sheet.getProtections(SpreadsheetApp.ProtectionType.RANGE);
    rp.forEach(p => p.remove());
  }
  SpreadsheetApp.flush();
  SpreadsheetApp.getUi().alert("All protections removed from all sheets.");
}
