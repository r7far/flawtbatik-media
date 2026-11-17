import json, sys
IG = 'https://www.instagram.com/'
CC = 'https://pippit.capcut.com/templates/'
S = 'Suhad Shami'; M = 'Mohammed Alshahrani'; J = 'Jana Mohamed'; ALL = 'All media team'

def it(date, kind, title, owner, submit='', status='planned', trend=None, needs='', note=''):
    d = dict(date=date, kind=kind, title=title, owner=owner, submit=submit, status=status, needs=needs, note=note)
    if trend: d['trend'] = dict(name=trend[0], how=trend[1], links=trend[2])
    return d

items = [
 it('2026-11-15', 'Post', 'Launch post on Instagram (Coming soon · 24–25 Dec · Jeddah)', S, status='done'),
 it('2026-11-16', 'Filming', 'Visit to the venue: filming (venue name, sign and street stay hidden)', M, status='done'),
 it('2026-11-17', 'Reel', 'Reel from Monday\'s venue visit (was planned for Mon 16, moved: editing took longer)', M, submit='Tue 17 Nov, 6 PM', status='moved',
    trend=('Appointment timestamps', 'Short clips with the time on screen, following the visit from arrival to leaving.', [IG+'p/DbQcmnVNJMh/'])),
 it('2026-11-18', 'Stories', '“What’s coming?” story week starts: Wed quiz → Thu poll “Padel or Baloot?” → Fri emoji slider → Sat question box (save the answers)', S, submit='Tue 17 Nov'),
 it('2026-11-20', 'Reel', 'Teaser reel: “Something new is coming to Jeddah” (our first ad)', M, submit='Wed 18 Nov',
    trend=('Plane so low / Tap to reveal', 'An unexpected setup or a blurred image builds tension, then the reveal: our logo + 24–25 Dec.', [IG+'p/Db_VMwxvP6y/', IG+'reel/DZAfd4DO8im/', CC+'coming-soon-teaser-template'])),
 it('2026-11-22', 'Reel + story', 'Booth registration reel + story with the form link', M, submit='Fri 20 Nov', status='depends',
    needs='The booth form link (PR & Logistics / tickets site). If it is not ready, this moves.',
    trend=('This is your sign', 'Camera-roll clips of small businesses, text says “this is your sign”, ends with “Register now”.', [IG+'p/DdBwj9AIMFR/'])),
 it('2026-11-23', 'Post + story', 'Guess the venue: hint 1 (a close-up detail, nothing that gives the place away)', J, submit='Sat 21 Nov', status='depends',
    needs='Rashad approves the contest rules and the prize.'),
 it('2026-11-24', 'Carousel', 'Activities carousel: what you can do at Fla w Tbatik', J, submit='Sun 22 Nov', needs='The confirmed activities list (Organizers).',
    trend=('Stretched word', 'One word split across the slides so people swipe to read it.', [IG+'p/DZFg-uhCDgj/'])),
 it('2026-11-25', 'Filming + story', 'Filming day at the venue (promo video + reels for the next weeks) · hint 2 story', M),
 it('2026-11-26', 'Story', 'Guess the venue: hint 3', J, submit='Tue 24 Nov', status='depends', needs='Same as hint 1.'),
 it('2026-11-27', 'Reel', 'Location reveal reel + contest winners (only on the date Rashad sets; backup: behind-the-scenes reel)', M, submit='Thu 26 Nov', status='depends',
    needs='Rashad sets the reveal date. Until then the venue stays hidden.',
    trend=('Stomp to reveal', 'A stomp or jump changes the frame to show the new place.', [IG+'reel/DWuaKdtiR4a/', IG+'p/DTsQbv4D0su/'])),
 it('2026-11-29', 'Reel', 'Padel reel: “Do you wanna play padel on 24 Dec?” + tag your partner', M, submit='Fri 27 Nov', needs='Padel rules and how to register (Organizers).',
    trend=('Do you wanna?', 'Opens with “Do you wanna…”, cuts to the person fully dressed and playing.', [IG+'p/DZA61cPPuDz/'])),
 it('2026-12-01', 'Reel', 'Baloot reel: “My reaction”', M, submit='Sun 29 Nov',
    trend=('My reaction', 'An opinion told only with face expressions.', [IG+'p/DeFnyr-q4Jq/'])),
 it('2026-12-03', 'Reel', 'FIFA reel: “The trio” + tag your 2v2 partner', M, submit='Tue 1 Dec',
    trend=('The trio', 'Three friends and how they are together, quick and funny.', [IG+'reel/DTtg7NQksQ0/'])),
 it('2026-12-05', 'Main video', 'Promo video (our main ad)', M, submit='Thu 3 Dec',
    trend=('Beat-drop transitions', 'Every cut lands on the beat; ends with logo + dates.', [IG+'p/DXCn62aCYXz/', CC+'coming-soon-event-trailer'])),
 it('2026-12-06', 'Deadline', 'Exams: every December post and reel is designed and approved by today', ALL),
 it('TBD', 'Reel + post', '🎟️ Tickets on sale: reel + ticket post + link sticker (date when the tickets platform is ready: Rashad tells us)', M, status='tbd',
    needs='The tickets platform is live and the prices are confirmed.',
    trend=('On-off / Toggle on', 'One switch flips from “closed” to “open”: tickets are live.', [IG+'reel/Da5lieLo_N5/', IG+'reels/audio/29285135541104810/'])),
 it('2026-12-09', 'Reel + collabs', 'Vendors reel + collab posts + vendors story', M, submit='Mon 7 Dec', needs='Confirmed vendors and their approval.',
    trend=('The process', 'Tools and steps behind a product, then the finished result.', [IG+'reel/Dc1PVCTR6Za/'])),
 it('2026-12-11', 'Reel', 'Behind the scenes: the team getting ready', M, submit='Wed 9 Dec',
    trend=('5 stages of being…', 'Five clips: from confident to overwhelmed (“5 stages of organizing an event”).', [IG+'reel/DeweozVRBpC/'])),
 it('2026-12-12', 'Carousel', 'Sponsors carousel: thank you to our sponsors', J, submit='Thu 10 Dec', status='depends', needs='Confirmed sponsors and their logos (Finance).'),
 it('2026-12-14', 'Reel + story', 'Save the date reel + “10 days to go” story', M, submit='Sat 12 Dec',
    trend=('Interactive calendar', 'Calendar entries come to life on screen.', [IG+'reel/DZSFl2vAn5w/', CC+'save-the-date-reel-template'])),
 it('2026-12-16', 'Reel', 'Q&A reel (answers from the story question box)', M, submit='Mon 14 Dec',
    trend=('Eye-zoom transition', 'Zoom into the eye to move to the next question.', [CC+'zoom-in-eye-transition'])),
 it('2026-12-19', 'Reel + post', '“5 days to go” post + tournaments reel', M, submit='Thu 17 Dec',
    trend=('Group pose', 'Same pose, each person holds an item that shows who they are; fast cuts.', [IG+'p/DYuudgavFOE/'])),
 it('2026-12-20', 'Posts + stories', 'Final reminder + event schedule + reposts', J, submit='Fri 18 Dec'),
 it('2026-12-23', 'Reel + filming', 'Venue reel the day before (setup)', M,
    trend=('POV: you’re the influencer', 'One of us steps in front of the camera like an influencer visit.', [IG+'reel/DZX7v6Ao5rt/'])),
 it('2026-12-24', 'Live', 'Event day 1: live stories every hour + reels', ALL),
 it('2026-12-25', 'Live', 'Event day 2: finals, winners, closing', ALL),
 it('2026-12-26', 'Carousel', 'Thank you post', J, submit='Fri 25 Dec'),
 it('2026-12-29', 'Reel', 'Recap reel (+ a longer recap video)', M, submit='Sun 27 Dec',
    trend=('Rapid-fire recap', 'Flash cuts turn the two days into a visual diary.', [IG+'reel/DcjONHUu1QM/'])),
]
data = dict(updated='2026-11-17', time='Posts go out 8–10 PM. Reels around 8:30 PM.',
            note='Days with nothing are rest days. Dates marked “depends” move if what they need is not ready. Trends checked 13–17 Nov (later.com).',
            items=items)
json.dump(data, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(items))
