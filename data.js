// ================================================================
// Fla w Tbatik – Media site data
// Every week: add a new week at the TOP of WEEKS. Only the first
// week in the list is shown on the home page.
// ================================================================
window.FTB = {
  event: {
    nameEn: "Fla w Tbatik",
    nameAr: "فله وتباتيك",
    start: "2026-12-24T16:00:00+03:00",
    datesEn: "Thursday 24 – Friday 25 December 2026",
    datesAr: "الخميس 24 والجمعة 25 ديسمبر 2026",
    placeEn: "Al-Mohammadiya District Center, Jeddah",
    placeAr: "مركز حي المحمدية، جدة"
  },

  head: "Suhad Shami (Head of Media) checks that everyone finishes their tasks.",

  team: [
    { name: "Suhad Shami", role: "Head of Media" },
    { name: "Mohammed Alshahrani", role: "Deputy Head" },
    { name: "Jana Mohamed", role: "Deputy Head" }
  ],

  sheet: "https://docs.google.com/spreadsheets/d/1BNeiNM-ZyXTPEIJnDDJlA3dNZR-PrOfGQokb1Qia6FY/edit",

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

  // Sections that open in later weeks (shown as "coming soon")
  soon: [
    { en: "Tournaments info for your posts", ar: "معلومات البطولات للإعلان" },
    { en: "Design approvals", ar: "موافقات التصاميم" }
  ],

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

  wrongDates: ["17–18 Dec", "18–19 Dec", "31 Dec – 1 Jan", "31 Dec – 2 Jan"]
};

