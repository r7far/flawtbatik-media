"""Media tasks for weeks 2–8, from the leadership sheet (only leadership tasks sheet › Marketing and Media)
plus the few extra tasks worth keeping. The posts themselves live in the 🗓️ Schedule, not here."""
import json, sys, datetime as dt
S = 'Suhad Shami'; M = 'Mohammed Alshahrani'; J = 'Jana Mohamed'; R = 'Rashad'; ALL = 'All media team'
D = lambda m, d: dt.date(2026, m, d)
starts = {w: D(11, 16) + dt.timedelta(7 * (w - 2)) for w in range(2, 9)}
def label(w):
    s = starts[w]; e = s + dt.timedelta(6)
    return 'Week %d – (%s – %s)' % (w, s.strftime('%a %d %b'), e.strftime('%a %d %b'))
def wk(d):
    return max((w for w in starts if starts[w] <= d), default=2)
BRAND = ('\n\nRULES\n• Colours, fonts and logo: [[brand|🎨 Brand]] (Blue #7C98A3, Cream #E2D9BD, black, white; Impact / Farah).\n'
         '• Dates big. Nothing off-theme (no palms, suns, flowers, balls, stars).\n• Venue name stays hidden until Rashad says the reveal is out.')

def T(key, due, cat, task, owner, what, steps, deliver, done, src=None, support='', prio='High', brand=False, status='Not Started', note=''):
    det = 'WHAT\n' + what
    if src: det += '\n\nFROM THE LEADERSHIP SHEET\n“' + src + '”'
    det += '\n\nSTEPS\n' + '\n'.join('%d. %s' % (i, x) for i, x in enumerate(steps, 1))
    det += '\n\nDELIVER\n' + deliver + '\n\nDONE WHEN\n' + done
    if note: det += '\n\nNOTE\n' + note
    if brand: det += BRAND
    w = wk(due)
    return dict(key='p-' + key, row=0, week=w, week_label=label(w), category=cat, task=task, detail=det, owner=owner, support=support,
                timing=due.strftime('%a %d %b'), due=due.isoformat(), priority=prio, deliverable=deliver if len(deliver) < 60 else 'See details',
                status=status, progress=100 if status == 'Done' else 0, notes='', synced=0)

tasks = [
 # ---------- Week 2 ----------
 T('L06', D(11, 15), 'Campaign', 'Launch event announcement', S, 'The first post that tells people the event is coming.',
   ['Post the launch post (done Sun 15 Nov).', 'Ticket link and venue come later, when Rashad says.'], 'The live post link', 'Posted.',
   src='Launch event announcement: publish event identity, date, venue/area, value proposition and registration/ticket CTA.', status='Done', prio='Critical'),
 T('L03', D(11, 18), 'Content Calendar', 'Master content calendar', S,
   'One calendar from now to after the event: every post, reel, story, countdown, FAQ and reminder, each with a date and an owner.',
   ['Start from the [[sched|🗓️ Schedule]]: it has every post and reel.', 'Add the stories for each day (countdowns, polls, “New post” stories, FAQs, reminders).',
    'Give every line a date and one owner.', 'Send it to Rashad. When he approves, the Schedule is updated from it.'],
   'Calendar (sheet or Canva link) uploaded here', 'Every date has an owner and Rashad approved it.',
   src='Create master content calendar: announcement, launch, vendor reveals, sponsor posts, activities, countdowns, FAQs and final reminders.', support=R, prio='Critical'),
 T('L04', D(11, 18), 'Social', 'Optimize the social profiles', M,
   'Instagram and TikTok look finished: bio, link, highlights, contact method and event info.',
   ['Wait for Rashad to confirm the handle and the bio text before changing anything.', 'Instagram: bio, link in bio, contact button, highlight covers (from Jana\'s templates).',
    'TikTok: Business account with the same photo, name and bio.', 'Send Rashad screenshots of both profiles.'],
   'Screenshots of both profiles', 'Rashad approved both profiles.',
   src='Optimize social profiles: update bio, links, highlights, contact method, registration link and event information.', support=J,
   note='Passwords stay with Rashad. Never put them on this site.'),
 T('L02', D(11, 18), 'Brand', 'Brand templates, hashtags and tone', J,
   'Templates the whole team uses, plus the event hashtags and how we write.',
   ['Read [[brand|🎨 Brand]] first.', 'Make in Canva: feed post 1080×1440, story 1080×1920, reel cover, highlight covers.',
    'Suggest one English and one Arabic hashtag (Rashad and the founders choose).', 'Write 3 lines on our tone (how captions sound).',
    'Share the Canva folder with Suhad and Mohammed and add the link in [[board|📁 Board]].'],
   'Canva link + hashtags + tone lines', 'Suhad and Rashad approved them.',
   src='Finalize event identity: lock logo, colors, typography, templates, tone, hashtags and sponsor branding rules.', support=S, brand=True),
 T('L01', D(11, 19), 'Strategy', 'Marketing strategy', S,
   'One page that says who we talk to, what we say, in which phases, on which channels, and how we measure it.',
   ['Start from the media plan (open [[plan|📅 Plan]]).', 'Write: audience, key message, campaign phases (teaser → reveal → tickets → countdown → event → recap), content pillars, channels.',
    'Add the numbers we aim for (followers, reach, ticket clicks) and the call to action of each phase.', 'Send it to Rashad. He sends it to the founders.'],
   'The strategy page (doc or PDF)', 'Rashad approved it.',
   src='Build marketing strategy: define audience, positioning, key message, campaign phases, content pillars, channels, KPIs and CTA.', support=R, prio='Critical'),
 T('L07', D(11, 21), 'Video', 'Promo video concept', M,
   'The plan for our main ad (posts Sat 5 Dec): script, storyboard, shot list, who approves.',
   ['Read the promo card in [[plan|📅 Plan]] and the trend in the [[sched|🗓️ Schedule]].', 'Write the script (what is said or written on screen, second by second).',
    'Draw a simple storyboard (one box per shot).', 'Write the shot list for the filming day (Wed 25 Nov): place, people, props.', 'Send it to Rashad and Suhad.'],
   'Script + storyboard + shot list', 'Rashad approved it before the filming day.',
   src='Create promo video concept: write script/storyboard, shot list, talent/location/product requirements and approval flow.', support=S),
 T('X01', D(11, 22), 'Reporting', 'Weekly summary for the founders', S,
   'What went out this week and what is late.',
   ['List what was posted this week (from the [[sched|🗓️ Schedule]]).', 'List what is late and its new date.', 'Add the main numbers from Instagram insights.', 'Send it to Rashad. Rashad sends it to the founders.'],
   'Summary text', 'Rashad has it by Sunday night.', note='Founders\' meeting rule (9 Nov): a weekly summary every week.'),
 # ---------- Week 3 ----------
 T('L13', D(11, 23), 'Community', 'Engagement campaign plan', S,
   'The plan for polls, Q&A, countdowns, activity reveals, the guess-the-venue hints and people\'s own posts (UGC), up to the event.',
   ['List the engagement items already in the [[sched|🗓️ Schedule]].', 'Add the countdown stickers and the question boxes with their dates.',
    'Write the rules of the guess-the-venue contest for Rashad to approve (prize, how to answer, how winners are picked).', 'Send it to Rashad.'],
   'Engagement plan', 'Rashad approved it.',
   src='Build engagement campaign: polls, Q&A, countdowns, activity reveals, UGC prompts and reminders.', support=J, prio='Medium'),
 T('L08', D(11, 25), 'Video', 'Shoot the promo video', M,
   'Film the promo video at the venue on the filming day, from the approved shot list.',
   ['Take the approved shot list.', 'Film every shot twice, vertical 9:16, plus a few horizontal.', 'Film backup shots.',
    'Anyone who appears agreed to be filmed. Nothing that shows the venue name before the reveal.', 'Upload all raw clips to [[board|📁 Board]] the same night.'],
   'Link to the raw clips folder', 'Every shot on the list is filmed and uploaded.',
   src='Shoot promo video: capture planned footage with backup shots and releases/permissions where needed.', support=ALL),
 T('L12', D(11, 27), 'Paid Ads', 'Paid advertising plan', S,
   'Which posts we boost, to whom, with what budget and on which dates.',
   ['Pick the posts to boost from the [[sched|🗓️ Schedule]] (teaser, promo, tickets).', 'Audience: Jeddah, ages, interests.',
    'Budget per post: ask Rashad (Finance decides).', 'How we check results every day.'],
   'Ads plan (one page)', 'Rashad and Finance approved it.',
   src='Plan paid advertising: audience, budget, creative variations, campaign dates, tracking and daily performance checks.', support=R),
 T('L05', D(11, 28), 'Ticketing', 'Ticket sales assets', J,
   'Everything we need the day tickets open: graphics, FAQ, prices, terms wording, payment confirmation text.',
   ['Design the ticket post and story (prices left blank until Rashad confirms them).', 'Suhad writes the FAQ and the short terms/refund wording from the tickets site.',
    'Get it ready, do not post: the date comes when the tickets platform is live.'],
   'Designs + FAQ text', 'Rashad approved them.',
   src='Prepare ticket sales assets: ticket page graphics, FAQs, pricing, terms, payment confirmation and refund/cancellation wording.', support=S, prio='Critical', brand=True),
 T('L10', D(11, 29), 'Vendor Content', 'Vendor spotlight process', S,
   'How we collect each vendor\'s logo, description, photos and offer, get their approval, and post them.',
   ['Make a short form or sheet: logo, one-line description, 3 photos, offer, Instagram handle.', 'Jana prepares the Participant post template.',
    'Agree with PR & Logistics who sends it to the vendors.', 'Spotlights go in the [[sched|🗓️ Schedule]] once vendors are confirmed.'],
   'Form/sheet + Participant template', 'Rashad approved the process.',
   src='Create vendor spotlight process: collect vendor logo, description, product photos, offers and approval; schedule spotlight content.', support=J),
 T('L11', D(11, 29), 'Sponsor Content', 'Collect sponsor assets', S,
   'Logos, brand rules, copy and required placements from every confirmed sponsor.',
   ['Ask Rashad / Finance for the confirmed sponsors list.', 'Collect logo files, their brand rules, the text they want and where they must appear.', 'Save everything in [[board|📁 Board]].'],
   'Sponsor folder', 'Every confirmed sponsor has its files.',
   src='Collect sponsor assets: logos, brand guidelines, copy, activation details and required placements.', support=R, prio='Critical', note='Starts when Finance confirms sponsors.'),
 T('L14', D(11, 29), 'PR', 'Media and creators outreach list', R,
   'Local pages, creators and community accounts that could share the event, plus the message and a media kit.',
   ['List Jeddah pages and creators that fit (name, handle, followers).', 'Write the outreach message.', 'Make a one-page media kit (what, when, activities, logo).'],
   'List + message + media kit', 'Rashad approved; nothing is sent before that.',
   src='Create media/press outreach list: local pages, creators, community accounts and relevant media; outreach message and media kit.', support=S, prio='Medium'),
 T('X01b', D(11, 29), 'Reporting', 'Weekly summary for the founders', S, 'Same as last week.', ['Posted / late / numbers.', 'Send to Rashad.'], 'Summary text', 'Rashad has it by Sunday night.'),
 # ---------- Week 4 ----------
 T('L09', D(12, 3), 'Video', 'Edit the promo video', M,
   'Final promo video for Instagram and TikTok, with captions, subtitles and the call to action.',
   ['Edit from the approved script; trend and example in the [[sched|🗓️ Schedule]].', 'Versions: 9:16 reel and a short cut.', 'Subtitles (Arabic + English), logo end card with the dates.', 'Submit here for Rashad to approve.'],
   'Final video files', 'Approved in [[review|Review]] before Thu 3 Dec.',
   src='Edit promo video: produce platform versions, captions, subtitles and final CTA.', support=S, brand=True),
 T('X02', D(12, 6), 'Deadline', 'All December content ready before exams', ALL,
   'Every December post and reel in the Schedule is designed and approved, because the groups stop during exams.',
   ['Check every December item in the [[sched|🗓️ Schedule]].', 'Submit each one here or in its task.', 'Suhad checks nothing is missing.'],
   'Everything submitted', 'Rashad approved all December items.', prio='Critical'),
 T('X01c', D(12, 6), 'Reporting', 'Weekly summary for the founders', S, 'Same as last week.', ['Posted / late / numbers.', 'Send to Rashad.'], 'Summary text', 'Rashad has it by Sunday night.'),
 # ---------- Week 5 ----------
 T('L15', D(12, 10), 'Production', 'Event-day shot list', M,
   'Every shot we need on event day: venue, crowd, zones, vendors, sponsors, activities, leadership, safety, closing, short interviews.',
   ['Walk through the floor plan zone by zone.', 'List the shots for each zone and each time of day.', 'Mark the sponsor shots (they are needed for the sponsor report).'],
   'Shot list', 'Rashad approved it.', src='Create event-day shot list.', support=S),
 T('L17', D(12, 12), 'Sponsor Fulfillment', 'Sponsor placement map', S,
   'Where every sponsor appears: banners, screens, mentions, booths and posts.',
   ['Take the sponsor list and what each one bought (Finance).', 'Mark each placement on the floor plan and in the [[sched|🗓️ Schedule]].', 'Check with Logistics and Organization.'],
   'Placement map', 'Finance and Rashad approved it.', src='Map sponsor placements.', support='Finance + Logistics + Organization', prio='Critical'),
 T('X03', D(12, 12), 'Design', 'Signage designs for Logistics', J,
   'The event signs (zones, directions, booths, rules) designed for printing.',
   ['Get the list of signs and sizes from Logistics.', 'Design them on the brand templates.', 'Submit for Rashad, then Logistics prints.'],
   'Print-ready files', 'Rashad approved; Logistics has the files.', src='(PR & Logistics sheet) Produce operational signage, support: Marketing.', support='Logistics', brand=True),
 T('X01d', D(12, 13), 'Reporting', 'Weekly summary for the founders', S, 'Same as last week.', ['Posted / late / numbers.', 'Send to Rashad.'], 'Summary text', 'Rashad has it by Sunday night.'),
 # ---------- Week 6 ----------
 T('L16', D(12, 17), 'Production', 'Event-day content schedule', M,
   'Who films which zone and when on both days, and how files are sent.',
   ['Split both days into time blocks.', 'Give each block a person and zones.', 'Decide how files go to the editor (folder, every 2 hours).'],
   'Event-day schedule', 'Rashad and Organization approved it.', src='Create event-day content schedule.', support='Organization', prio='Critical'),
 T('X01e', D(12, 20), 'Reporting', 'Weekly summary for the founders', S, 'Same as last week.', ['Posted / late / numbers.', 'Send to Rashad.'], 'Summary text', 'Rashad has it by Sunday night.'),
 # ---------- Week 7 ----------
 T('L18', D(12, 24), 'Content', 'Capture live event content (both days)', M,
   'Film opening, crowd, activities, vendors, sponsors, guests and behind the scenes on both days.',
   ['Follow the event-day shot list and schedule.', 'Upload clips every 2 hours.'], 'Clips folder', 'Every shot on the list is filmed.', src='Capture live event content.', support=ALL),
 T('L19', D(12, 24), 'Social', 'Live stories and reels (both days)', S,
   'Approved live updates without disturbing the work or showing anything restricted.',
   ['Stories every hour.', 'One reel per day.', 'Nothing posted that the founders or safety team said to keep private.'], 'Live posts', 'Posted on both days.', src='Post live stories/reels.', support='Operations'),
 T('L20', D(12, 24), 'Sponsor', 'Sponsor proof photos and videos', J,
   'Photos and videos of every sponsor placement for the sponsor report.',
   ['Use the sponsor placement map.', 'Photo + short video of each placement on day 1.', 'Save in the sponsor folder.'], 'Sponsor proof folder', 'Every placement has proof.',
   src='Capture sponsor fulfillment evidence.', support='Finance', prio='Critical'),
 T('X01f', D(12, 27), 'Reporting', 'Weekly summary for the founders', S, 'Event week summary.', ['Posted / numbers.', 'Send to Rashad.'], 'Summary text', 'Rashad has it by Sunday night.'),
 # ---------- Week 8 ----------
 T('L21', D(12, 29), 'Content', 'Recap reel and post', M, 'The recap of the two days (trend in the Schedule).',
   ['Pick the strongest clips.', 'Edit the recap reel and a longer version.', 'Submit for approval.'], 'Recap video', 'Approved and posted.', src='Publish recap.', support=S),
 T('L22', D(12, 31), 'Reporting', 'Marketing performance report', S,
   'Reach, engagement, clicks, ticket sales from our links, ad spend and best posts.',
   ['Take the numbers from Instagram, TikTok and the ads.', 'Show the top 5 posts.', 'What worked and what to change next time.'], 'Report', 'Sent to Rashad.',
   src='Create marketing performance report.', support='Finance'),
]
for w in range(2, 8):
    e = starts[w] + dt.timedelta(6)
    tasks.append(T('W%d' % w, e, 'Posting', "This week's posts from the Schedule", ALL,
      "Make and hand in every post, reel and story the 🗓️ Schedule gives you this week (each one by its 'Submit by' date).",
      ['Open [[sched|🗓️ Schedule]] and find this week\'s items with your name.', 'Follow the trend and the example link on each item.',
       'Press 📤 Submit here for each one (file or link + caption). One submission per item.', 'Suhad checks and Rashad approves in [[review|Review]] before anything is posted.'],
      'One submission per Schedule item', 'Every item of the week is approved and posted on its day.', brand=True))
json.dump(tasks, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(tasks), Counter(t['week'] for t in tasks))
