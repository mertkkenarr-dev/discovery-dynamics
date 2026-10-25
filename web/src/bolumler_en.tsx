/**
 * English chapters: same ids, masks, charts and data-driven sentence logic as bolumler.tsx (Turkish), written as natural English
 * rather than translated word for word. The remaining chapters (K5–K10) live in bolumler_en_ek.tsx.
 */
import type { Bolum } from './bolumler'
import { enEsik, enFirsat, enGizli, enHibrit, enKlon, enMetin, enTurler } from './bolumler_en_ek'
import { bicim } from './dil'
import { arzGrafik, fiyatGrafik, hitYilGrafik, ilkAyGrafik, yapayZekaGrafik } from './grafikler'
import type { Galaksi, Ozet } from './veri'

const { sayi, yuzde } = bicim('en')
const kat = (v: number) => sayi(v, 1)

export function bolumlerEn(oz: Ozet, g: Galaksi, bitler: Uint8Array[]): Bolum[] {
  const b = temel(oz)
  const sira = (id: string) => b.find((x) => x.id === id)!
  return [sira('gorunmez'), enGizli(oz), sira('arz'), sira('fiyat'), sira('tanidik'), enKlon(oz, g), enFirsat(oz), enTurler(oz, g, bitler), enHibrit(oz, g, bitler),
    sira('birlikte'), sira('ea'), sira('cince'), sira('ilkay'), enEsik(oz), enMetin(oz), sira('ikinci'), sira('yz')]  // fmt: skip
}

function temel(oz: Ozet): Bolum[] {
  const yillar = Object.keys(oz.arz)
  const [y0, y1] = [yillar[0]!, yillar[yillar.length - 1]!]
  const [arzIlk, arzSon] = [oz.arz[y0]!, oz.arz[y1]!]
  const hitler = Object.values(oz.hit_yil)
  const [hitMin, hitMax] = [Math.min(...hitler), Math.max(...hitler)]
  const fiyatlar = Object.entries(oz.fiyat_hit)
  const [fIlk, fSon] = [fiyatlar[0]!, fiyatlar[fiyatlar.length - 1]!]
  const azalan = oz.yenilik.egim_alt_t < 0 && oz.yenilik.egim_ust_t < 0
  const etiket = oz.etiket_en_olumlu.filter(([e]) => /co-op|multiplayer/i.test(e)).map(([, v]) => v)
  const uzun = oz.yorunge['Uzun soluklu']!
  const patla = oz.yorunge['Patlayıp sönen']!
  const carpanlar = Object.values(oz.ilk_ay.carpan).filter((v): v is number => v !== null)
  const yz = oz.yapay_zeka.gorunmez
  const [yzVar, yzYok] = [(yz['1']?.gorunmez ?? 0) * 100, (yz['0']?.gorunmez ?? 0) * 100]
  const io = oz.ikinci_oyun

  return [
    {
      id: 'gorunmez', kisa: 'Invisibility', maske: 'gorunmez', uzaklik: 23,
      baslik: `${Math.round(oz.gorunmez_yuzde)} out of every 100 indie games get fewer than 10 reviews in their first year.`,
      govde: <>
        <p>Steam doesn't publish sales figures, so we measure success by the number of user reviews a game receives in its first 365 days; review counts are strongly related to sales rank. Ten reviews means roughly a few hundred sales.</p>
        <p>At the other end of the scale, games that pass 500 reviews in their first year, counted as a "hit" in this study, make up only {yuzde(oz.hit_yuzde, 1)}.</p>
      </>,
      harita: 'Games with fewer than 10 reviews in their first year; the rest are dimmed.',
      yontem: `${sayi(oz.orneklem)} games released 2018–2025 without major-publisher backing. Success: first-365-day review count from Steam’s review histograms.`,
    },
    {
      id: 'arz', kisa: 'Crowding', maske: null, yilAnim: true, uzaklik: 25,
      baslik: hitMax - hitMin < 2
        ? `Yearly releases on Steam grew ${kat(arzSon / arzIlk)}×. The odds of standing out didn't move.`
        : `Yearly releases on Steam grew ${kat(arzSon / arzIlk)}×, and the odds of standing out changed.`,
      govde: <>
        <p>Annual releases went from {sayi(arzIlk)} in {y0} to {sayi(arzSon)} in {y1}. Yet the hit rate of indie games stayed between {yuzde(hitMin, 1)} and {yuzde(hitMax, 1)} every year.</p>
        <p>The "Steam is too crowded now" story isn't in the data: competition grows, but the share of games that become visible holds steady, so more games stand out each year in absolute terms.</p>
      </>,
      harita: 'Games appear in order of release year.',
      yontem: 'Supply: all games released on Steam. Hit rate: indie sample, by release year.',
      grafikler: [
        { kur: arzGrafik(oz, 'en'), etiket: 'Games released on Steam per year', baslik: 'Games released on Steam per year (all)', yukseklik: 180 },
        { kur: hitYilGrafik(oz, 'en'), etiket: 'Hit rate of indie games by year', baslik: 'Share of indie games that became hits', yukseklik: 150 },
      ],
    },
    {
      id: 'fiyat', kisa: 'Price', maske: 'pahali', uzaklik: 20,
      baslik: fSon[1] > fIlk[1]
        ? `Cheap games don't get more attention: the hit rate is ${yuzde(fIlk[1], 1)} at $${sayi(+fIlk[0], 2)} and ${yuzde(fSon[1], 0)} at $${sayi(+fSon[0], 2)}.`
        : 'The hit rate falls as price rises.',
      govde: <>
        <p>The hit rate rises steadily with price. This isn't pricing advice: a $30 indie game usually means a bigger team, budget and scope, and price is most likely a proxy for those.</p>
      </>,
      harita: 'Games listed above $20; they are spread across every region of the map.',
      yontem: 'Raw hit rates by list price. Price is also the strongest variable in genre- and year-controlled models.',
      grafikler: [{ kur: fiyatGrafik(oz, 'en'), etiket: 'Hit rate by price', baslik: 'Hit rate by price', yukseklik: 220 }],
    },
    {
      id: 'tanidik', kisa: 'Novelty', hipotez: 'H1', maske: 'tanidik', uzaklik: 18,
      baslik: azalan ? 'Familiar wins: unusual games get less attention.' : 'There is no clear link between novelty and success.',
      govde: <>
        <p>At the start of the study we pre-registered the hypothesis that "moderate novelty is best" (an inverted U). The data didn't support it.{azalan && ' The further a game’s tag combination is from established examples of its genre, the less attention it gets; there is no sweet spot in the middle.'}</p>
      </>,
      harita: 'The most familiar quarter of tag combinations. Nearby stars carry similar content.',
      yontem: 'Novelty: cosine distance between a game’s content tags and the 10 nearest earlier releases. Controlled regression and Lind–Mehlum U test.',
    },
    {
      id: 'birlikte', kisa: 'Together', maske: 'birlikte', uzaklik: 19,
      baslik: 'Games played together stand out.',
      govde: <>
        <p>Looking at mechanic, visual and player-structure tags one by one, the strongest positive association is with games played together: for Multiplayer, Online Co-op and Co-op the odds of becoming a hit are {kat(Math.min(...etiket))}–{kat(Math.max(...etiket))}×.</p>
        <p>Multiplayer games may collect more reviews per player, so the finding is an association, not a recipe.</p>
      </>,
      harita: 'Games tagged Multiplayer, Co-op or Online Co-op.',
      yontem: 'Logistic regression per tag, controlling for year, genre, price, Early Access and languages; Benjamini–Hochberg correction. Exploratory.',
    },
    {
      id: 'ea', kisa: 'Long tail', hipotez: 'H4', maske: 'ea', uzaklik: 20,
      baslik: `Games whose interest spreads over time have ${kat(uzun.hit / patla.hit)}× the hit rate of games that burn out fast.`,
      govde: <>
        <p>Games that launch in Early Access see interest spread out more over time (odds ×{sayi(oz.ea_kuyruk.or, 2)}).</p>
        <p>That matters: among games whose interest carries into a second year the hit rate is {yuzde(uzun.hit, 0)}; among those that spike and fade in the first months it is {yuzde(patla.hit, 0)}.</p>
      </>,
      harita: 'Games that launched in Early Access.',
      yontem: 'Second-year share of reviews. Controlled logistic regression and propensity-score matching (PSM); Holm correction.',
    },
    {
      id: 'cince', kisa: 'Chinese', hipotez: 'H6', maske: 'cince', uzaklik: 20,
      baslik: 'Games that support Simplified Chinese do better, but part of the link runs the other way.',
      govde: <>
        <p>All else equal, games with Chinese support get {sayi(oz.cince.ana, 0)}% more reviews; the most cautious estimate is {sayi(oz.cince.temkinli, 0)}%.</p>
        <p>But over eight months of tracking, the most successful games added Chinese {sayi(oz.cince.ekleme_T4 / oz.cince.ekleme_T0, 0)}× more often than the least successful ones. Sometimes success brings the language, not just the other way round.</p>
      </>,
      harita: 'Games that support Simplified Chinese.',
      yontem: 'Log-linear regression and PSM. Reverse causality measured by comparing language lists from February and October 2026.',
    },
    {
      id: 'ilkay', kisa: 'First month', maske: 'hit', uzaklik: 22,
      baslik: `Launch month decides the year: a typical game ends its first year at ${kat(carpanlar[Math.floor(carpanlar.length / 2)]!)}× its first-month reviews.`,
      govde: <>
        <p>The rank correlation between first-30-day and first-year reviews is {sayi(oz.ilk_ay.rho, 2)}. {yuzde(oz.ilk_ay.hit['200–499'] ?? 0)} of games with 200–499 reviews in their first month end the year as hits.</p>
        <p>Implication: visibility is mostly won before launch; recovering afterwards is the exception.</p>
      </>,
      harita: 'Games that became hits in their first year.',
      yontem: 'Review counts for the first 30 and 365 days; Spearman rank correlation. Exploratory.',
      grafikler: [{ kur: ilkAyGrafik(oz, 'en'), etiket: 'Share ending the year as hits by first-month review band', baslik: 'Games ending the year as hits, by first-month reviews', yukseklik: 220 }],
    },
    {
      id: 'ikinci', kisa: 'Second game', hipotez: 'H5', maske: 'hicbiri', cizgiler: true, uzaklik: 23,
      baslik: io.iyilesen < 0.5 ? 'A studio’s second game is no better than its first.' : 'A studio’s second game is usually better than its first.',
      govde: <>
        <p>Only {yuzde(io.iyilesen * 100)} of {sayi(io.n)} studios got more reviews for their second game. {yuzde(io.T0_kalan)} of studios whose first game stayed invisible stayed invisible with the second: experience alone doesn't bring visibility.</p>
      </>,
      harita: 'Each line runs from a studio’s first game to its second (only pairs that differ at least threefold). Orange: the second game did better; blue: worse.',
      yontem: 'A studio’s first two games; paired difference and Wilcoxon signed-rank test, Holm correction.',
    },
    {
      id: 'yz', kisa: 'AI', maske: 'yapayZeka', uzaklik: 20,
      baslik: `${yuzde(yzVar)} of games that disclose AI use stay invisible; among games without a disclosure it is ${yuzde(yzYok)}.`,
      govde: <>
        <p>Since January 2024 Steam has required developers to disclose AI use; {yuzde(oz.yapay_zeka.pay_yil['2025'] ?? 0, 1)} of games released in 2025 carry a disclosure.</p>
        <p>This isn't cause and effect. A disclosure most likely goes with low-budget, quickly made projects; players reacting to it is also possible. The data can't tell the two apart.</p>
      </>,
      harita: 'Games that disclose AI use.',
      yontem: `Indie games released 2024–2025; disclosures from IGDB keywords. Controlled logistic regression: odds ×${sayi(oz.yapay_zeka.or, 1)}. Exploratory.`,
      grafikler: [{ kur: yapayZekaGrafik(oz, 'en'), etiket: 'Share of games staying invisible by AI disclosure, 2024–2025', baslik: 'Share of games staying invisible (2024–2025)', yukseklik: 120 }],
    },
  ]
}
