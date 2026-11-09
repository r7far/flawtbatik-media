// ================================================================
// Fla w Tbatik – Media site data
// Every week: add a new week at the TOP of `weeks`. Only the first
// week in the list is shown on the home page.
// Only put things here that can be public (this site is public).
// ================================================================
window.FTB = {
  event: {
    nameEn: "Fla w Tbatik",
    nameAr: "فله وتباتيك",
    start: "2026-12-24",
    datesEn: "Thursday 24 – Friday 25 December 2026",
    datesAr: "الخميس 24 والجمعة 25 ديسمبر 2026",
    shortEn: "24–25 Dec 2026",
    shortAr: "24–25 ديسمبر 2026",
    placeEn: "Al-Mohammadiya District Center, Jeddah",
    placeAr: "مركز حي المحمدية، جدة"
  },

  head: "Suhad Shami (Head of Media) checks that everyone finishes their tasks.",

  team: [
    { name: "Suhad Shami", role: "Head of Media", job: "Checks every task is done on time. Makes the media plan. Approves posts." },
    { name: "Mohammed Alshahrani", role: "Deputy Head", job: "Media team member." },
    { name: "Jana Mohamed", role: "Deputy Head", job: "Media team member." }
  ],

  links: {
    sheet: "https://docs.google.com/spreadsheets/d/1BNeiNM-ZyXTPEIJnDDJlA3dNZR-PrOfGQokb1Qia6FY/edit",
    folder: "https://drive.google.com/drive/folders/1goJaC8B4k2qjFOvUWZGO7qzfKalFgDZf",
    board: "https://docs.google.com/spreadsheets/d/12aNntFQ5hwVH1juBkOwy9ge9vWfIwfXp/edit"
  },

  weeks: [
    {
      n: 1,
      range: "Mon 9 – Sun 15 Nov",
      tasks: [
        { due: "2026-11-11", en: "Send your Instagram post ideas", ar: "أرسل أفكارك لبوستات الإنستقرام", who: "Everyone" },
        { due: "2026-11-14", en: "Whole-team meeting", ar: "اجتماع التيم كامل", who: "Everyone" }
      ]
    }
  ],

  // ---------- Captions ----------
  hashtags: ["#فله_وتباتيك", "#FlaWTbatik", "#جدة", "#فعاليات_جدة", "#Jeddah"],
  captionTemplates: [
    { name: "Save the date", text: "📅 {datesAr}\n📍 {placeAr}\n\n📅 {datesEn}\n📍 {placeEn}" },
    { name: "Countdown", text: "⏳ باقي {days} يوم\n{days} days to go\n\n📅 {shortAr} | {shortEn}\n📍 {placeAr}" },
    { name: "Empty + event info", text: "\n\n—\n📅 {shortAr} | {shortEn}\n📍 {placeAr}" }
  ],
  checklist: [
    "Date is 24–25 Dec 2026 (no old dates)",
    "Place is Al-Mohammadiya District Center",
    "Logo is on the design",
    "Spelling checked (Arabic and English)",
    "No prices unless Rashad confirmed them",
    "Suhad approved it (Media Board > Approvals)",
    "Grid order is right (post 1 first)"
  ],
  dmReplies: [
    { q: "Where is it? / وين المكان؟", a: "📍 مركز حي المحمدية، جدة\nAl-Mohammadiya District Center, Jeddah" },
    { q: "When is it? / متى؟", a: "📅 الخميس 24 والجمعة 25 ديسمبر 2026\nThursday 24 – Friday 25 December 2026" },
    { q: "Tickets? / التذاكر؟", a: "التذاكر قريب، تابعونا عشان تعرفون أول ما تنزل 🎟️\nTickets are coming soon. Follow us to know first 🎟️" },
    { q: "Booths? / أبي بوث", a: "تسجيل البوثات قريب، تابعونا وبنعلن الرابط 🛍️\nBooth registration opens soon. Follow us for the link 🛍️" }
  ],

  // ---------- Event ----------
  // Fees and prizes stay "TBA" until Rashad confirms them.
  tournaments: [
    { icon: "🎾", en: "Padel", ar: "بادل", format: "Teams of 2, knockout", spots: "16 teams" },
    { icon: "🃏", en: "Baloot", ar: "بلوت", format: "Tables of 4", spots: "5 tables (20 players)" },
    { icon: "🎮", en: "FIFA 1v1", ar: "فيفا فردي", format: "Knockout", spots: "16 players" },
    { icon: "🎮", en: "FIFA 2v2", ar: "فيفا زوجي", format: "Teams of 2", spots: "16 teams" }
  ],
  shotList: [
    "Entrance and the logo sign",
    "Wide shot of the whole place (day and night)",
    "Bazaar booths, one by one",
    "Food court and food close-ups",
    "Padel matches and the final",
    "Baloot tables",
    "FIFA screens and players' reactions",
    "Kids zone (no faces without parents' OK)",
    "Crowd at the busiest time",
    "Team behind the scenes",
    "Winners with their prizes",
    "Closing shot at the end of each day"
  ],

  // ---------- Brand ----------
  colors: [
    { name: "Slate", hex: "#7F99A8" },
    { name: "Deep", hex: "#4F6877" },
    { name: "Cream", hex: "#E6DCC0" },
    { name: "Paper", hex: "#F6F2E6" },
    { name: "Black", hex: "#0B0B0B" }
  ],
  fonts: [
    { name: "Lalezar", use: "Big Arabic titles", url: "https://fonts.google.com/specimen/Lalezar" },
    { name: "IBM Plex Sans Arabic", use: "Body text, Arabic and English", url: "https://fonts.google.com/specimen/IBM+Plex+Sans+Arabic" }
  ],
  sizes: [
    { name: "Post (portrait)", px: "1080 × 1350", note: "Most posts" },
    { name: "Post (profile grid)", px: "1080 × 1440", note: "3:4, matches the profile grid" },
    { name: "Post (square)", px: "1080 × 1080", note: "" },
    { name: "Story / Reel", px: "1080 × 1920", note: "Keep text away from the top and bottom" }
  ],
  wrongDates: ["17–18 Dec", "18–19 Dec", "31 Dec – 1 Jan", "31 Dec – 2 Jan"]
};
