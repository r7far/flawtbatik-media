/**
 * Fla w Tbatik – sheet bridge for the media site.
 * Lives in "Fla W Tbabtik Tasks Sheet" (Extensions › Apps Script).
 * Only touches the "Marketing and Media" tab.
 *
 * Setup (once):
 *  1. Run resetMediaTab()  → Google asks for permission → Allow.
 *  2. Project Settings › Script properties › add BRIDGE_TOKEN = (the token from the media site Admin › Settings).
 *  3. Deploy › New deployment › Web app › Execute as: Me, Who has access: Anyone › Deploy.
 *     Copy the Web app URL into the media site Admin › Settings.
 */
const TAB = 'Marketing and Media';
const HEAD = ['Department', 'Phase', 'Category', 'Task', 'Subtask / Detail', 'Owner', 'Support', 'Timing', 'Priority',
  'Dependency', 'Deliverable / Evidence', 'Quality Check / Acceptance', 'Status', 'Progress %', 'Notes'];
const STATUSES = ['Not Started', 'In Progress', 'Submitted', 'Changes requested', 'Done'];

function sheet_() {
  const sh = SpreadsheetApp.getActive().getSheetByName(TAB);
  if (!sh) throw new Error('Tab not found: ' + TAB);
  return sh;
}

function doPost(e) {
  let out;
  try {
    const b = JSON.parse(e.postData.contents);
    const token = PropertiesService.getScriptProperties().getProperty('BRIDGE_TOKEN');
    if (!token || b.token !== token) throw new Error('Bad token');
    if (b.action === 'read') out = { ok: true, rows: read_() };
    else if (b.action === 'update') out = update_(b.payload || {});
    else throw new Error('Unknown action');
  } catch (err) {
    out = { ok: false, error: String(err.message || err) };
  }
  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
}

function read_() {
  const sh = sheet_(), n = sh.getLastRow();
  if (n < 1) return [];
  return sh.getRange(1, 1, n, 15).getDisplayValues().map((v, i) => ({ row: i + 1, values: v }));
}

function update_(p) {
  const sh = sheet_(), row = Number(p.row);
  if (!row || row < 2 || row > sh.getLastRow()) throw new Error('Bad row');
  const task = sh.getRange(row, 4).getDisplayValue();
  if (String(task).trim() !== String(p.task || '').trim()) throw new Error('Row moved; sync again');
  if (p.status) {
    if (STATUSES.indexOf(p.status) < 0) throw new Error('Bad status');
    sh.getRange(row, 13).setValue(p.status);
    sh.getRange(row, 14).setValue(Number(p.progress) || 0);
  }
  if (typeof p.notes === 'string') sh.getRange(row, 15).setValue(p.notes);
  return { ok: true };
}

/** Clears the Marketing and Media tab and writes Week 1 in the shared layout. Run once. */
function resetMediaTab() {
  const sh = sheet_();
  sh.getRange(1, 1, sh.getMaxRows(), sh.getMaxColumns()).breakApart();
  sh.clear();
  sh.clearConditionalFormatRules();
  sh.getRange(1, 1, sh.getMaxRows(), sh.getMaxColumns()).clearDataValidations();
  const M = 'Marketing & Media';
  const rows = [
    HEAD,
    ['Week 1 – (Mon 9 – Sun 15 Nov)', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
    [M, 'Pre', 'Content', 'Send your Instagram post ideas', 'Your own ideas. Grid style: one design split across 3–6 posts.', 'Suhad Shami', 'Rashad', 'Wed 11 Nov', 'High', '', 'Ideas sent', 'At least one idea', 'Not Started', 0, ''],
    [M, 'Pre', 'Content', 'Send your Instagram post ideas', 'Your own ideas. Grid style: one design split across 3–6 posts.', 'Mohammed Alshahrani', 'Rashad', 'Wed 11 Nov', 'High', '', 'Ideas sent', 'At least one idea', 'Not Started', 0, ''],
    [M, 'Pre', 'Content', 'Send your Instagram post ideas', 'Your own ideas. Grid style: one design split across 3–6 posts.', 'Jana Mohamed', 'Rashad', 'Wed 11 Nov', 'High', '', 'Ideas sent', 'At least one idea', 'Not Started', 0, ''],
    [M, 'Pre', 'Meeting', 'Whole-team meeting', 'Review everyone\'s ideas together.', 'All media team', 'Rashad', 'Sat 14 Nov', 'High', '', 'Chosen ideas', 'Ideas chosen', 'Not Started', 0, '']
  ];
  sh.getRange(1, 1, rows.length, 15).setValues(rows);
  // look
  sh.getRange(1, 1, 1, 15).setBackground('#1F2A44').setFontColor('#FFFFFF').setFontWeight('bold').setWrap(true).setVerticalAlignment('middle');
  sh.setFrozenRows(1);
  sh.getRange(2, 1, 1, 15).merge().setBackground('#FFE8EA').setFontColor('#B3261E').setFontWeight('bold').setFontSize(13);
  sh.getRange(3, 1, sh.getMaxRows() - 2, 15).setWrap(true).setVerticalAlignment('top');
  [140, 60, 110, 230, 300, 160, 110, 100, 80, 100, 160, 160, 130, 80, 200].forEach((w, i) => sh.setColumnWidth(i + 1, w));
  // status dropdown + colors
  const st = sh.getRange(3, 13, sh.getMaxRows() - 2, 1);
  st.setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(STATUSES, true).setAllowInvalid(false).build());
  const colors = { 'Not Started': '#EDEFF2', 'In Progress': '#FFF4CC', 'Submitted': '#E4EEF4', 'Changes requested': '#FFD9DC', 'Done': '#D7F5E1' };
  sh.setConditionalFormatRules(Object.keys(colors).map(k =>
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo(k).setBackground(colors[k]).setRanges([st]).build()));
  SpreadsheetApp.flush();
}
