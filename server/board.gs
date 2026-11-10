
/** Builds the Media Board from the Marketing and Media tasks in the leadership sheet. Safe to run again (rebuilds). */
function buildBoard() {
  const ss = SpreadsheetApp.openById(PropertiesService.getScriptProperties().getProperty('BOARD_ID'));
  const ST = ['Not Started', 'In Progress', 'Waiting', 'Done'];
  const DRAFT = 'Draft – needs OK';
  const tabs = [
    ['How to use', '📘 Media Board – how to use | طريقة الاستخدام',
      'One tab for each thing the media team has to track. Tasks themselves are on the team site. | كل تبويب لشي لازم الفريق يتابعه. المهام نفسها في موقع التيم.',
      ['Tab', 'What it is for', 'Who fills it', 'From task (leadership sheet)'], [190, 420, 170, 300], [
        ['Content Calendar', 'Every post, reel and story with its date and owner', 'Suhad', 'Create master content calendar'],
        ['Profiles', 'Checklist to update Instagram and TikTok profiles', 'Mohammed', 'Optimize social profiles'],
        ['Ticket Assets', 'Everything the ticket page needs before sales open', 'Suhad + Finance', 'Prepare ticket sales assets'],
        ['Promo Video', 'Script / storyboard for the promo video, scene by scene', 'Media team', 'Create promo video concept / shoot / edit'],
        ['Vendors', 'Spotlight posts for bazaar and food vendors', 'Jana', 'Create vendor spotlight process'],
        ['Sponsors', 'Sponsor files, where their logo goes, and proof on event day', 'Suhad + Finance', 'Collect sponsor assets / Map sponsor placements / Capture sponsor evidence'],
        ['Ads', 'Paid ads plan and daily results', 'Suhad + Finance', 'Plan paid advertising'],
        ['Outreach', 'Pages, creators and media we contact', 'Media team', 'Create media/press outreach list'],
        ['Shot List', 'Shots we must have on event day', 'Media team', 'Create event-day shot list'],
        ['Coverage', 'Who covers which zone and when, on 24 and 25 Dec', 'Suhad', 'Create event-day content schedule'],
        ['Ideas', 'Free ideas from anyone. We choose in the meeting', 'Everyone', 'Weekly ideas'],
        ['Report', 'Results after the event', 'Suhad', 'Create marketing performance report']
      ], null],
    ['Content Calendar', '🗓️ Content Calendar | تقويم المحتوى',
      'Draft plan from the leadership sheet. Suhad sets the final dates and an owner for every row. Nothing is posted before ✅ on the team site. | مسودة، سهاد تثبت التواريخ وصاحب كل سطر.',
      ['Date', 'Day', 'Type', 'Post', 'Platform', 'Owner', 'Status', 'Link', 'Notes'], [95, 60, 110, 330, 110, 140, 130, 180, 220], [
        ['2026-11-21', 'Sat', 'Launch', 'Event announcement: name, date, place, what is in it, follow for tickets', 'IG + TikTok', '', DRAFT, '', 'Founders approve the facts first'],
        ['2026-11-23', 'Mon', 'Reel', 'Teaser reel: what is Fla w Tbatik', 'IG + TikTok', '', DRAFT, '', ''],
        ['2026-11-26', 'Thu', 'Post', 'Booth registration is open', 'IG', '', DRAFT, '', 'When the booth link is ready'],
        ['2026-11-28', 'Sat', 'Reveal', 'Activity reveal: Padel tournament', 'IG + TikTok', '', DRAFT, '', 'Fees and prizes only after Rashad confirms'],
        ['2026-11-30', 'Mon', 'Engagement', 'Poll: which activity are you coming for?', 'IG story', '', DRAFT, '', ''],
        ['2026-12-01', 'Tue', 'Reveal', 'Activity reveal: Baloot tournament', 'IG + TikTok', '', DRAFT, '', ''],
        ['2026-12-03', 'Thu', 'Reveal', 'Activity reveal: FIFA 1v1 and 2v2', 'IG + TikTok', '', DRAFT, '', ''],
        ['2026-12-05', 'Sat', 'Video', 'Promo video release', 'IG + TikTok', '', DRAFT, '', 'Depends on the Promo Video tab'],
        ['2026-12-06', 'Sun', 'Tickets', 'Tickets on sale', 'IG + TikTok', '', DRAFT, '', 'Date and price from Finance'],
        ['2026-12-07', 'Mon', 'Vendor', 'Vendor spotlights start (see Vendors tab)', 'IG', '', DRAFT, '', ''],
        ['2026-12-09', 'Wed', 'Sponsor', 'Sponsor posts (see Sponsors tab)', 'IG', '', DRAFT, '', 'Only confirmed sponsors'],
        ['2026-12-10', 'Thu', 'Engagement', 'Q&A story: ask us anything', 'IG story', '', DRAFT, '', ''],
        ['2026-12-14', 'Mon', 'FAQ', 'FAQ post: place, times, tickets, parking, kids', 'IG', '', DRAFT, '', ''],
        ['2026-12-14', 'Mon', 'Countdown', '10 days to go', 'IG story', '', DRAFT, '', ''],
        ['2026-12-17', 'Thu', 'Countdown', '7 days to go', 'IG + TikTok', '', DRAFT, '', ''],
        ['2026-12-21', 'Mon', 'Countdown', '3 days to go', 'IG story', '', DRAFT, '', ''],
        ['2026-12-23', 'Wed', 'Reminder', 'Final reminder: tomorrow! place, times, tickets', 'IG + TikTok', '', DRAFT, '', ''],
        ['2026-12-24', 'Thu', 'Live', 'Event day 1: live stories and reels (see Coverage)', 'IG + TikTok', '', DRAFT, '', ''],
        ['2026-12-25', 'Fri', 'Live', 'Event day 2: live stories and reels (see Coverage)', 'IG + TikTok', '', DRAFT, '', ''],
        ['2026-12-26', 'Sat', 'Thanks', 'Thank-you post', 'IG', '', DRAFT, '', ''],
        ['2026-12-29', 'Tue', 'Recap', 'Recap reel with the best footage', 'IG + TikTok', '', DRAFT, '', 'Facts approved']
      ], [7, [DRAFT, 'Not Started', 'In Progress', 'Ready', 'Posted']]],
    ['Profiles', '👤 Profiles | تحديث الحسابات',
      'Check each item on each account. Test every link. | جرّب كل رابط.',
      ['Platform', 'Item', 'What to put', 'Done by', 'Status', 'Notes'], [100, 160, 340, 130, 120, 220],
      [].concat(...['Instagram', 'TikTok'].map(p => [
        [p, 'Name and handle', 'Fla w Tbatik | فله وتباتيك', '', 'Not Started', p === 'TikTok' ? 'Mohammad is making the account' : ''],
        [p, 'Profile photo', 'Official logo (brand kit)', '', 'Not Started', ''],
        [p, 'Bio', 'What it is + 24–25 Dec 2026 + Al-Mohammadiya District Center, Jeddah', '', 'Not Started', ''],
        [p, 'Link', 'Ticket / registration link', '', 'Not Started', 'When ready'],
        [p, 'Contact method', 'How people reach us (DM)', '', 'Not Started', ''],
        [p, 'Highlights', 'About, Tickets, Activities, Booths, FAQ', '', 'Not Started', p === 'TikTok' ? 'Not on TikTok' : '']
      ])), [5, ST]],
    ['Ticket Assets', '🎟️ Ticket Assets | أشياء صفحة التذاكر',
      'Everything ready before ticket sales open. Prices come from Finance only. | الأسعار من المالية بس.',
      ['Item', 'Details', 'Owner', 'Status', 'Checked with', 'Link'], [200, 360, 130, 120, 150, 200], [
        ['Ticket page graphics', 'Cover image and post sizes', '', 'Not Started', '', ''],
        ['FAQ', 'Place, dates, times, kids, parking, entry', '', 'Not Started', '', ''],
        ['Prices', 'From Finance. Do not write a price before it is confirmed', '', 'Waiting', 'Finance', ''],
        ['Terms', 'Ticket terms', '', 'Not Started', 'Legal', ''],
        ['Payment confirmation', 'Message people get after paying (Moyasar)', '', 'Not Started', 'Finance', ''],
        ['Refund / cancellation', 'Wording', '', 'Not Started', 'Legal + Finance', ''],
        ['Gate rule', 'Phone number required, name optional', '', 'Not Started', 'Operations', '']
      ], [4, ST]],
    ['Promo Video', '🎬 Promo Video | فيديو الإعلان',
      'Write the scenes first, get OK, then shoot and edit. | اكتبوا المشاهد، ناخذ موافقة، بعدين تصوير ومونتاج.',
      ['Scene', 'What we see', 'Text / voice', 'Place / people needed', 'Length (s)', 'Shot?', 'Notes'], [60, 300, 260, 220, 80, 80, 200],
      [1, 2, 3, 4, 5, 6].map(n => [n, '', '', '', '', '', n === 6 ? 'Last scene: date, place, follow / tickets' : '']), [6, ['', 'Yes', 'No']]],
    ['Vendors', '🛍️ Vendors | البائعين',
      'One row per vendor. Post only after the vendor approves. No claims they did not approve. | ما ننشر إلا بعد موافقتهم.',
      ['Vendor', 'Type', 'Logo', 'Description', 'Product photos', 'Offer', 'Vendor approved', 'Post date', 'Posted', 'Notes'], [160, 100, 70, 260, 110, 160, 110, 100, 80, 180], [], [9, ['', 'Yes', 'No']]],
    ['Sponsors', '🤝 Sponsors | الرعاة',
      'Files, placements and proof. Placements must match the contract. | الأماكن لازم تطابق العقد.',
      ['Sponsor', 'Logo + brand rules', 'Copy / text', 'Required placements', 'Where (banner, screen, booth, post)', 'Matches contract', 'Evidence on event day', 'Notes'], [150, 130, 200, 200, 220, 110, 160, 180], [], [6, ['', 'Yes', 'No', 'Check']]],
    ['Ads', '📣 Paid Ads | الإعلانات',
      'Budget only after Finance approves. Check results every day while ads run. | الميزانية بعد موافقة المالية.',
      ['Campaign', 'Platform', 'Audience', 'Budget (from Finance)', 'Start', 'End', 'Creative', 'Tracking link', 'Status', 'Results'], [160, 100, 220, 130, 90, 90, 160, 170, 110, 220], [], [9, ST]],
    ['Outreach', '📨 Outreach | التواصل',
      'Local pages, creators, community accounts and media. Use the account handle, not phone numbers. | حطوا اسم الحساب، لا أرقام جوال.',
      ['Name / account', 'Type', 'Platform', 'Followers', 'Why them', 'Contacted by', 'Status', 'Notes'], [180, 120, 100, 90, 240, 130, 120, 220], [], [7, ['Not contacted', 'Contacted', 'Replied', 'Agreed', 'No']]],
    ['Shot List', '📸 Shot List | قائمة اللقطات',
      'Shots we must have on event day. Tick when done. | علّموا لما تخلص اللقطة.',
      ['Shot', 'Zone', 'Day', 'Who', 'Done'], [340, 150, 90, 140, 80], [
        ['Entrance and the logo sign', 'Entrance', 'Both', '', ''],
        ['Wide shot of the whole place (day and night)', 'All', 'Both', '', ''],
        ['Bazaar booths, one by one', 'Bazaar', 'Both', '', ''],
        ['Food court and food close-ups', 'Food court', 'Both', '', ''],
        ['Padel matches and the final', 'Padel', 'Both', '', ''],
        ['Baloot tables', 'Baloot', 'Both', '', ''],
        ['FIFA screens and players’ reactions', 'FIFA', 'Both', '', ''],
        ['Kids zone (no faces without parents’ OK)', 'Kids', 'Both', '', ''],
        ['Crowd at the busiest time', 'All', 'Both', '', ''],
        ['Sponsor banners, screens and booths', 'Sponsors', 'Both', '', 'Proof for sponsors'],
        ['Leadership and team behind the scenes', 'All', 'Both', '', ''],
        ['Safety and organizers at work', 'All', 'Both', '', ''],
        ['Guest short interviews / testimonials', 'All', 'Both', '', ''],
        ['Winners with their prizes', 'Stage', 'Fri 25', '', ''],
        ['Closing shot at the end of each day', 'All', 'Both', '', '']
      ].map(r => r.slice(0, 4).concat([''])), [5, ['', 'Yes']]],
    ['Coverage', '🎥 Coverage | التغطية يوم الإيفنت',
      'Who covers which zone and when. Every zone needs someone. Send files to the Media Files folder the same night. | كل منطقة لازم لها أحد.',
      ['Day', 'Time block', 'Zone', 'Photos / video', 'Stories', 'Files sent?', 'Notes'], [90, 120, 140, 160, 160, 90, 220],
      [].concat(...['Thu 24 Dec', 'Fri 25 Dec'].map(d => [].concat(...['Opening', 'Afternoon', 'Evening (busiest)', 'Closing'].map(t =>
        ['Entrance', 'Bazaar + food', 'Tournaments', 'Kids + crowd'].map(z => [d, t, z, '', '', '', ''])))))
      , [6, ['', 'Yes', 'No']]],
    ['Ideas', '💡 Ideas Box | صندوق الأفكار',
      'Write your own ideas here. We choose together in the meeting. | اكتب أفكارك هنا، ونختار في الاجتماع.',
      ['Date', 'Your name', 'Idea', 'Type', 'Notes', 'Chosen?'], [95, 150, 380, 120, 220, 90], [], [6, ['', 'Yes', 'No', 'Later']]],
    ['Report', '📊 Report | التقرير بعد الإيفنت',
      'Fill within 7 days after the event. Write where each number came from. | اكتبوا مصدر كل رقم.',
      ['Metric', 'Instagram', 'TikTok', 'Total', 'Source'], [220, 120, 120, 120, 260], [
        ['Reach', '', '', '', ''], ['Engagement', '', '', '', ''], ['Profile visits', '', '', '', ''], ['Link clicks', '', '', '', ''],
        ['New followers', '', '', '', ''], ['Tickets sold (if tracked)', '', '', '', ''], ['Ad spend', '', '', '', 'Finance'],
        ['Best post', '', '', '', ''], ['Best reel', '', '', '', '']
      ], null]
  ];
  const tmp = ss.insertSheet('tmp_' + Date.now());
  ss.getSheets().forEach(s => { if (s.getSheetId() !== tmp.getSheetId()) ss.deleteSheet(s); });
  const ids = [];
  tabs.forEach(t => {
    const [name, title, note, head, widths, rows, status] = t;
    const sh = ss.insertSheet(name);
    const n = head.length;
    sh.getRange(1, 1, 1, n).merge().setValue(title).setFontSize(15).setFontWeight('bold').setBackground('#F6F2E6').setFontColor('#0B0B0B');
    sh.getRange(2, 1, 1, n).merge().setValue(note).setFontColor('#4F6877').setWrap(true).setBackground('#F6F2E6');
    sh.setRowHeight(1, 34); sh.setRowHeight(2, 38);
    sh.getRange(3, 1, 1, n).setValues([head]).setBackground('#1F2A44').setFontColor('#FFFFFF').setFontWeight('bold').setWrap(true);
    sh.setFrozenRows(3);
    widths.forEach((w, c) => sh.setColumnWidth(c + 1, w));
    if (rows.length) sh.getRange(4, 1, rows.length, n).setValues(rows.map(r => r.map(v => v === undefined ? '' : v)));
    const last = Math.max(rows.length + 3, 60);
    if (sh.getMaxRows() < last) sh.insertRowsAfter(sh.getMaxRows(), last - sh.getMaxRows());
    sh.getRange(4, 1, last - 3, n).setWrap(true).setVerticalAlignment('top');
    if (status) {
      const r = sh.getRange(4, status[0], last - 3, 1);
      r.setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(status[1].filter(Boolean), true).setAllowInvalid(true).build());
    }
    if (sh.getMaxColumns() > n) sh.deleteColumns(n + 1, sh.getMaxColumns() - n);
    ids.push(name + '=' + sh.getSheetId());
  });
  ss.deleteSheet(tmp);
  console.log('BOARD ' + ss.getId() + ' ' + ids.join(','));
}
