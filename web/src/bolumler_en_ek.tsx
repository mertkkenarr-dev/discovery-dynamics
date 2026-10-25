/**
 * English chapters K5–K10 (hidden gems, copycats, opportunity zones, genres, genre mixing, the 50-review threshold, store text).
 * Same data-driven logic as the Turkish versions in bolumler_ek.tsx and bolumler_tur.tsx.
 */
import type { Bolum } from './bolumler'
import { bolgeAdi, oncuEtiketleri } from './bolumler_ek'
import { korelasyon } from './bolumler_tur'
import { bicim } from './dil'
import { bitMaske, cokTurMaske } from './galaksi/maske'
import { esikGrafik, firsatGrafik, gizliGrafik, klonGrafik, metinGrafik } from './grafikler_ek'
import { azRiskliOdullu, hibritGrafik, karneGrafik } from './grafikler_tur'
import type { Galaksi, Ozet } from './veri'

const { sayi, yuzde } = bicim('en')
const liste = (a: string[]) => (a.length <= 2 ? a.join(' and ') : `${a.slice(0, -1).join(', ')} and ${a[a.length - 1]}`)

export function enGizli(oz: Ozet): Bolum {
  const k = oz.k7
  const f = (ad: string) => k.farklar[ad]!
  const [sim, pt, demo] = [f('Tür: Simulation'), f('Playtest'), f('Çıkıştan önce demo')]
  return {
    id: 'gizli', kisa: 'Hidden gems', maske: 'gizli', uzaklik: 21,
    baslik: `${Math.round((k.n_gizli / k.cok_begenilen) * 10)} out of every 10 highly rated games also stay invisible.`,
    govde: <>
      <p>{sayi(k.n_gizli)} games are loved by almost all of their players yet received fewer than 100 reviews in their first year. Invisibility isn't only a problem for weak games.</p>
      <p>What separates these hidden gems from equally loved but visible games (500+ reviews), using only what is known before launch? Visible ones are more often Simulation ({yuzde(sim.gorunur * 100)} vs {yuzde(sim.gizli * 100)}) and twice as likely to have run a Playtest ({yuzde(pt.gorunur * 100)} vs {yuzde(pt.gizli * 100)}). The share with a pre-launch demo is the same in both groups: {yuzde(demo.gizli * 100)}.</p>
    </>,
    harita: 'Hidden gems: highly rated games with 10–99 first-year reviews.',
    yontem: 'Rating: Wilson 95% lower bound of the positive-review share ≥ 80%. Groups compared with standardized differences and a controlled logistic model. Exploratory.',
    grafikler: [{ kur: gizliGrafik(oz, 'en'), etiket: 'Feature shares among hidden and visible gems', baslik: 'Share of games with each feature: hidden vs visible gems', yukseklik: 220 }],
  }
}

export function enKlon(oz: Ozet, g: Galaksi): Bolum {
  const k = oz.k5
  const ayni = k.takipci.wilson[0] <= k.oncul.wilson[1] && k.oncul.wilson[0] <= k.takipci.wilson[1]
  const dl = Object.values(k.takipci_dilim)
  const vs = k.dalgalar[0]!
  return {
    id: 'klon', kisa: 'Copycats', maske: 'klon', uzaklik: 21, etiketler: oncuEtiketleri(oz, g),
    baslik: ayni ? 'Copying a hit adds no extra odds; the luck is in the region itself.' : 'Copycats of a hit fare differently from the games that came before it.',
    govde: <>
      <p>{yuzde(k.takipci.hit_oran, 1)} of later games that closely resemble a big hit become hits themselves, {sayi(k.takipci.hit_oran / oz.hit_yuzde, 0)}× the sample average. But {yuzde(k.oncul.hit_oran, 1)} of games released into the same content region <em>before</em> the hit also became hits: the hit is a sign of an already fertile region.</p>
      <p>Timing matters: {yuzde(dl[0]!.oran, 1)} of followers arriving in the first six months become hits, versus {yuzde(dl[dl.length - 1]!.oran, 1)} of those arriving one to two years later. Among indie games in the {vs.ad} wave ({sayi(vs.takipci.length)} games), only {yuzde((vs.hit / vs.orneklem) * 100, 1)} became hits.</p>
    </>,
    harita: `Games in the wave that started with ${vs.ad} and the deckbuilder wave that followed ${k.dalgalar[1]!.diger[0] ?? k.dalgalar[1]!.ad}.`,
    yontem: `Pioneers: ${sayi(k.dalga.oncu.n_merkez)} games with 5,000+ first-year reviews. Similarity: cosine of content-tag vectors ≥ 0.70. Compared against placebo and predecessor groups; Wilson intervals. Exploratory.`,
    grafikler: [{ kur: klonGrafik(oz, 'en'), etiket: 'Hit rate of games released into a hit’s region before and after it', baslik: 'Hit rate: before the hit, after it (months), and lookalikes of an ordinary game', yukseklik: 200 }],
  }
}

export function enFirsat(oz: Ozet): Bolum {
  const firsat = oz.k6.bolgeler.filter((x) => x.firsat)
  const cozy = firsat.find((x) => x.ad.startsWith('Cozy'))
  const sessiz = [...firsat].sort((a, z) => a.goreli_buyume - z.goreli_buyume)[0]
  const d21 = sessiz ? oz.duyarlilik.K6[sessiz.ad] : undefined
  return {
    id: 'firsat', kisa: 'Opportunity zones', maske: 'firsat', uzaklik: 17,
    etiketler: oz.k6.etiketler.map((e) => ({ konum: e.merkez, ad: bolgeAdi(e.ad), tur: 'bolge' as const })),
    baslik: `${firsat.length} content regions are both uncrowded and produce more hits than expected.`,
    govde: <>
      <p>We split games into {oz.k6.k} regions by content tags and compared each region's actual number of hits with what its mix of price, genre and year would predict. Fewer games are released in opportunity regions than in most, but those that are released become hits more often than expected.</p>
      {cozy && <p>Cozy and wholesome games produce {sayi(cozy.ob, 1)}× the expected hits, but the number of games released there is growing {sayi(cozy.goreli_buyume, 1)}× faster than Steam overall: the window is closing.</p>}
      {sessiz && sessiz !== cozy && (
        <p>
          The quietest candidate is {bolgeAdi(sessiz.ad, ' and ')}: {sayi(sessiz.ob, 1)}× the expected hits, and supply isn't outgrowing Steam.
          {(d21?.alt ?? 2) <= 1 && ` But looking only at games released since 2021 the difference becomes uncertain (${sayi(d21!.ob, 2)}×), so this result isn't robust.`}
        </p>
      )}
    </>,
    harita: 'Games in opportunity regions, with region names.',
    yontem: 'Spherical k-means on content-tag vectors. Expected hits: logistic model controlling for year, genre, price, Early Access and languages; Poisson interval for the ratio. Exploratory.',
    grafikler: [{ kur: firsatGrafik(oz, 'en'), etiket: 'Observed ÷ expected hits by region', baslik: 'Hits: actual ÷ expected (orange = opportunity region)', yukseklik: 250 }],
  }
}

export function enTurler(oz: Ozet, g: Galaksi, bitler: Uint8Array[]): Bolum {
  const k = oz.k10.karne
  const sirali = [...k].sort((a, z) => z.hit - a.hit)
  const [ust, alt] = [sirali.slice(0, 3), sirali.slice(-3)]
  const r = korelasyon(k.map((x) => x.gorunmez), k.map((x) => x.hit))
  const ob = [...k].sort((a, z) => z.ob - a.ob)
  const dusen = k.filter((x) => x.egilim_ust < 0).sort((a, z) => a.egilim - z.egilim)
  const iyi = azRiskliOdullu(oz)
  return {
    id: 'turler', kisa: 'Genres', maske: null, uzaklik: 21,
    maskeOzel: bitMaske(g, k.flatMap((x, i) => (iyi(x) ? [bitler[i]!] : []))),
    baslik: r < -0.5 ? 'In genres, risk and reward don’t trade off: the most rewarding genres are also the least risky.' : 'Risk and reward vary independently across genres.',
    govde: <>
      <p>{liste(ust.map((x) => x.tur))} have hit rates of {sayi(Math.min(...ust.map((x) => x.hit)), 0)}–{yuzde(Math.max(...ust.map((x) => x.hit)), 0)}. At the other end, {liste(alt.map((x) => x.tur))}: a hit rate of at most {yuzde(Math.max(...alt.map((x) => x.hit)), 1)}, with at least {yuzde(Math.min(...alt.map((x) => x.gorunmez)))} of games staying invisible.</p>
      <p>The ranking largely holds after accounting for price and scope: furthest above expectations are {liste(ob.slice(0, 3).map((x) => x.tur))}, furthest below {liste(ob.slice(-3).map((x) => x.tur))}.{dusen.length > 0 && ` Genres whose hit rate fell significantly from 2021–22 to 2023–24: ${liste(dusen.map((x) => x.tur))}${dusen.every((x) => x.goreli_buyume > 1) ? '; supply in all of them is growing faster than Steam overall' : ''}.`}</p>
    </>,
    harita: 'Games in low-risk, high-reward genres (invisibility below average, hit rate above).',
    yontem: `Indie games released 2021–2025; ${k.length} subgenres (each ≥ 500 games). Subgenre: a genre tag among a game’s top 10 tags. Wilson intervals; expected hits from a logistic model controlling for year, genre, price, Early Access and languages. Earlier games are excluded because tag coverage then was linked to success. Exploratory.`,
    grafikler: [{ kur: karneGrafik(oz, 'en'), etiket: 'Risk and reward map of subgenres', baslik: 'Risk (staying invisible) and reward (becoming a hit) by subgenre', yukseklik: 300 }],
  }
}

export function enHibrit(oz: Ozet, g: Galaksi, bitler: Uint8Array[]): Bolum {
  const h = oz.k10
  const yok = h.n_anlamli === 0
  return {
    id: 'hibrit', kisa: 'Genre mixing', maske: null, uzaklik: 22,
    maskeOzel: cokTurMaske(g, bitler, 3),
    baslik: yok ? 'Mixing genres isn’t an advantage in itself: hybrids do as well as the sum of their parts.' : `${h.n_anlamli} genre mixes perform differently from what their parts predict.`,
    govde: <>
      <p>We compared {sayi(h.n_cift)} genre pairs with what each genre predicts on its own. {yok ? `None differs from expectations after correcting for multiple tests; the ${h.n_p05} pairs that look significant on their own are about what chance alone would produce.` : `${h.n_anlamli} pairs remain different after multiple-test correction.`}</p>
      {yok && <p>In practice, a hybrid's success is set by the success of its component genres. The idea of "combine the right two genres and get synergy" has no support in the data.</p>}
    </>,
    harita: 'Games with three or more subgenre tags.',
    yontem: 'Expected hits: logistic model with year, genre, price, Early Access, languages and each subgenre’s separate effect (no interactions). Observed ÷ expected per pair, Poisson test, Benjamini–Hochberg correction. Synonymous pairs excluded; 2021–2025. Exploratory.',
    grafikler: [{ kur: hibritGrafik(oz, 'en'), etiket: 'Observed ÷ expected hits for genre pairs', baslik: 'Most extreme genre pairs: observed ÷ expected hits (grey = not significant)', yukseklik: 360 }],
  }
}

export function enEsik(oz: Ozet): Bolum {
  const t = oz.k8.tahmin.find((x) => x.esik === 50)!
  const yuz = (v: number) => (Math.exp(v) - 1) * 100
  const isaretli = (v: number) => `${v >= 0 ? '+' : '−'}${yuzde(Math.abs(v), 1)}`
  const yok = t.alt <= 0 && t.ust >= 0
  return {
    id: 'esik', kisa: '50 threshold', maske: null, uzaklik: 24,
    baslik: yok ? '“Pass 50 reviews and the algorithm will notice you” finds no support in the data.' : `Interest ${t.sicrama > 0 ? 'jumps' : 'drops'} for games that pass 50 reviews.`,
    govde: <>
      <p>A common belief among developers: once a game passes 50 reviews, Steam starts recommending it. Across {sayi(Math.round(oz.k8.oyun / 1000))} thousand games and {sayi(Math.round(oz.k8.gozlem / 1e6))} million monthly review slices, passing 50 changes the review rate by {isaretli(yuz(t.sicrama))} (95% interval {isaretli(yuz(t.alt))} … {isaretli(yuz(t.ust))}).</p>
      <p>That is no different from placebo thresholds that should have no effect (20, 30, 40…). Interest grows smoothly, not like a door opening at a threshold.</p>
    </>,
    harita: 'All games.',
    yontem: 'Regression discontinuity (two-sided local linear), placebo thresholds, game-clustered errors. The 10-review threshold isn’t interpreted because of selection bias. Exploratory.',
    grafikler: [{ kur: esikGrafik(oz, 'en'), etiket: 'Jump in review rate at review-count thresholds', baslik: 'Change in review rate after crossing the threshold', yukseklik: 210 }],
  }
}

export function enMetin(oz: Ozet): Bolum {
  const m = oz.k9.modeller
  const [k4, km, tf] = [m['K4 nitelikleri']!, m['K4 + metin']!, m['Yalnız metin (TF-IDF)']!]
  const uz = oz.k9.uslup_or['Metin uzunluğu (log)']!
  const ab = oz.k9.uslup_or['Abartı sıfatları (unique, epic…)']!
  return {
    id: 'metin', kisa: 'Store page', maske: 'hit', uzaklik: 22,
    baslik: km.fark_alt > 0 ? 'A game’s store-page text hints at its fate.' : 'The store-page text carries no extra information about success.',
    govde: <>
      <p>Adding the store description to our pre-launch prediction model raises accuracy (PR-AUC) from {sayi(k4.pr_auc, 2)} to {sayi(km.pr_auc, 2)}; random guessing scores {sayi(oz.hit_yuzde / 100, 2)}. The text alone scores {sayi(tf.pr_auc, 2)}.</p>
      <p>Words that go with hits: "co-op", "wishlist" and "from the creators of"; the other way: "VR", "arcade", "levels". In style, the strongest signal is effort: longer, more concrete texts succeed more often (×{sayi(uz.tahmin, 2)}). Big words like "unique" and "epic" {ab.alt <= 1 && ab.ust >= 1 ? 'show no link' : `have an effect of ×${sayi(ab.tahmin, 2)}`}.</p>
    </>,
    harita: 'Games that became hits in their first year.',
    yontem: `${sayi(oz.k9.n_test)} test games (2024–25), trained on ≤ 2023. TF-IDF and sentence embeddings (MiniLM) + logistic regression; leak-free stacking with LightGBM; paired bootstrap. Sentences mentioning awards, sales or press quotes were removed; since the text is today’s version, the gain is an upper bound. Exploratory.`,
    grafikler: [{ kur: metinGrafik(oz, 'en'), etiket: 'Prediction accuracy of the models (PR-AUC)', baslik: 'Prediction accuracy (PR-AUC, test 2024–2025)', yukseklik: 170 }],
  }
}
