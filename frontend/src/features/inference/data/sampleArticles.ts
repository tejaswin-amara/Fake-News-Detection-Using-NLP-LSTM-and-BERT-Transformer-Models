import type { ArticlePreset } from "@/types/inference";

export const SAMPLE_ARTICLES: ArticlePreset[] = [
  {
    id: "preset-reuters-geopolitical",
    name: "Reuters Geopolitical Report",
    category: "credible",
    expectedVerdict: "REAL",
    title: "Central Banks Coordinate Liquidity Facility Amid Global Trade Realignment",
    description:
      "Objective financial news reporting verified international policy coordination with cited treasury officials.",
    text: `WASHINGTON/GENEVA — The Federal Reserve and four peer central banks announced a synchronized expansion of bilateral US dollar swap lines on Tuesday, aiming to stabilize short-term cross-border liquidity following shifting tariff structures in the North Atlantic corridor.

According to joint statements released simultaneously by the Bank of England, the European Central Bank, the Swiss National Bank, and the Bank of Japan, the standing 7-day maturity operations will transition from weekly auctions to daily offerings beginning Monday.

"This coordinated measure serves as an important liquidity backstop to ease strains in global funding markets, thereby helping to mitigate the effects of such strains on the supply of credit to households and businesses," the central banking coalition stated.

Economists surveyed by independent financial monitoring bodies noted that commercial paper spreads tightened by 14 basis points immediately following the announcement, reflecting restored confidence in interbank clearing mechanisms.`,
  },
  {
    id: "preset-onion-satire",
    name: "The Onion Satire",
    category: "satire",
    expectedVerdict: "FAKE",
    title:
      "Scientists Confirm Moon Actually Just Giant Glow-In-The-Dark Ceiling Sticker Placed in 1969",
    description:
      "High-irony satirical article containing absurd physical claims, deadpan scientific commentary, and comedic hyperbole.",
    text: `HOUSTON — In a revelation that has sent shockwaves through the astrophysical community, NASA administrators conceded Monday that the celestial body long believed to be Earth's natural satellite is, in fact, an enormous phosphorescent vinyl adhesive stuck to the upper atmosphere during the Apollo 11 mission.

"We honestly didn't think the adhesive backing would hold up for fifty-seven consecutive years," admitted Chief Orbital Engineer Dr. Dale Vanderhoof, observing that several edges along the Mare Tranquillitatis appear to be slightly curling downward. "Neil and Buzz pressed it firmly against the mesosphere using industrial double-sided foam tape, but sunlight degradation was always our chief worry."

According to documents declassified under the Freedom of Information Act, the original budget for the Apollo program had allocated $25 billion for a legitimate lunar landing, but engineers discovered that buying an extra-large novelty glow sticker from an Orlando gift shop freed up billions for an executive lounge.

Astronomers globally have been advised to avoid using high-magnification optical telescopes, which risk exposing the faint plastic barcode visible along the crater Tycho.`,
  },
  {
    id: "preset-clickbait-health",
    name: "Clickbait Health Miracle",
    category: "clickbait",
    expectedVerdict: "FAKE",
    title:
      "SHOCKING SECRET: Ancient Himalayan Moss Cures All Joint Inflammation Overnight Doctors Beg You Not To See",
    description:
      "Sensationalized medical clickbait using urgency tokens, conspiracy against medical establishments, and miraculous guarantees.",
    text: `Big Pharma is furiously trying to remove this web page! If you or a loved one suffer from back pain, arthritis, or stiffness, you must read this urgent medical alert before it gets banned forever.

A lone botanist trekking through secret, forbidden valleys in the high Himalayas stumbled upon an ancient luminous moss that monks have guarded for five thousand years. Clinical tests that mainstream laboratories refused to publish prove that just three drops of this raw distilled extract completely rebuilds destroyed cartilage in under eight hours.

"Traditional doctors will tell you that cartilage cannot regenerate," claims Dr. Marcus Thorne, whose medical license was mysteriously revoked after he tried to bring this revolutionary formula to the public. "They want you trapped on expensive monthly prescriptions and toxic pain injections that slowly destroy your liver."

Over 420,000 Americans have already thrown away their walking canes in just the last twelve days. Supplies are down to the final 14 bottles due to a pending federal gag order. Click the button below immediately to claim your risk-free miracle trial package before mainstream corrupt elites shut our website down.`,
  },
  {
    id: "preset-conspiracy-tech",
    name: "Subterranean Network Conspiracy",
    category: "conspiracy",
    expectedVerdict: "FAKE",
    title:
      "Whistleblower Leaks Documents Exposing Underground Neural Substation Under Denver Airport",
    description:
      "Unverified anonymous claims citing secret plots, shadow operations, and suppressed biometric surveillance programs.",
    text: `An anonymous military contractor has smuggled four encrypted flash drives out of a subterranean bunker complex buried five stories beneath the Denver International Airport baggage concourse.

The unredacted manifests describe a black-budget classified project known internally as 'Aegis Resonance', which reportedly utilizes high-frequency subsurface antenna arrays to map neural oscillatory patterns of passengers waiting at terminal gates. According to the whistleblower, the automated biometric scanners installed throughout 2024 were secretly modified with microscopic quantum sensors that transmit direct cognitive telemetry to an unacknowledged deep-state server farm in the Nevada desert.

Mainstream media outlets have completely blacklisted the story after receiving classified national security directives from unnamed intelligence officials. Independent researchers who attempted to measure electromagnetic frequencies near Baggage Carousel 4 reported sudden device malfunctions and unmarked surveillance vehicles shadowing them across Colorado highway corridors.`,
  },
];
