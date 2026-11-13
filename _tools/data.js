// ================================================================
// Fla w Tbatik – Media site data
// Every week: add a new week at the TOP of `weeks`. Only the first
// week in the list is shown on the home page.
// Only public things here. Private team info is in local.js on the Raspberry Pi.
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
    placeAr: "مركز حي المحمدية، جدة",
    // The venue name is NOT public yet. Posts, captions and stories use this until Rashad says it can be announced.
    venuePublic: false,
    publicPlaceEn: "Jeddah · location announced soon",
    publicPlaceAr: "جدة · المكان نعلنه قريب"
  },

  // Team names and links are private: the team site adds them from local.js.
  head: "",
  team: [],
  links: { site: "/", folder: "", board: "" },

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
    "Do NOT write the venue name yet (only \"Jeddah\") until Rashad says it can be announced",
    "The official logo is used as it is: not redrawn, recolored, stretched or cut",
    "Empty space around the logo (at least 10% of its width)",
    "The logo is not on a busy background (or there is a blur / color layer behind it)",
    "Only the official colors: blue with white, cream with black",
    "Fonts: Impact (English) and Farah (Arabic)",
    "One short, clear message in the middle. Not crowded",
    "Text is big enough to read on a phone (also in the grid)",
    "Spelling checked (Arabic and English)",
    "No prices unless Rashad confirmed them",
    "Suhad or Rashad approved it on the team site (✅ Approve)",
    "Grid order is right (post 1 first)",
    "After every post or reel: an Instagram story saying “New Post”"
  ],
  dmReplies: [
    { q: "Where is it? / وين المكان؟", a: "📍 في جدة، والمكان بالتحديد نعلنه قريب، تابعونا 👀\nIn Jeddah. We will announce the exact place soon, stay tuned 👀" },
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
  // Official brand guideline from Roua (Brand Identity Guidelines v1.0, Nov 2026)
  colors: [
    { name: "Primary Blue", hex: "#1085BB" },
    { name: "Warm Cream", hex: "#E2D9BD" },
    { name: "Black", hex: "#000000" },
    { name: "White", hex: "#FFFFFF" }
  ],
  fonts: [
    { name: "Impact", use: "English: headlines and short emphasis", url: "https://learn.microsoft.com/typography/font-list/impact" },
    { name: "Farah", use: "Arabic: the approved Arabic typeface. Check it is installed and the Arabic shows right before you export", url: "" }
  ],
  logoRules: {
    do: ["Use the supplied logo only. Do not redraw, rearrange, separate or replace its lettering.", "Keep empty space around the logo: at least 10% of the logo width on every side.", "Scale it proportionally and keep all parts together.", "Use a high-resolution file, on a clean, high-contrast background.", "Keep the original logo colors. Do not recolor it to match the design."],
    avoid: ["Stretching or squashing it.", "Cropping the decorative strokes.", "Putting other things too close to it.", "Using it too small to read."]
  },
  brandWords: "Bringing people together through fun and creativity. Playful · Energetic · Welcoming · Creative · Connected · Memorable",
  colorPairs: [
    { bg: "#1085BB", fg: "#FFFFFF", text: "Blue background → white text" },
    { bg: "#E2D9BD", fg: "#000000", text: "Cream background → black text" }
  ],
  designRules: [
    "Clean and simple: one clear message, big, in the middle. Not a small text on the side.",
    "Short words with energy. No long paragraphs, in posts or in videos.",
    "Balance the sizes: the main words must be easy to read in one post and in the full grid.",
    "Do not put the logo straight on a busy picture. Put a soft blur or a color layer behind it first.",
    "The official logo is always the biggest and clearest logo. Other logos (sponsors) are smaller.",
    "Do not add new fonts. Only Impact and Farah (and the 2 extra fonts when Rashad confirms them).",
    "Only use the logo files we give you (folder 01 – Logo & Brand). Never send the logo to anyone, or change it, without asking Rashad.",
    "Every design is checked on the team site before it is posted."
  ],
  sizes: [
    { name: "Post (portrait)", px: "1080 × 1350", note: "Most posts" },
    { name: "Post (profile grid)", px: "1080 × 1440", note: "3:4, matches the profile grid" },
    { name: "Post (square)", px: "1080 × 1080", note: "" },
    { name: "Story / Reel", px: "1080 × 1920", note: "Keep text away from the top and bottom" }
  ],
  wrongDates: ["17–18 Dec", "18–19 Dec", "31 Dec – 1 Jan", "31 Dec – 2 Jan"]
};
