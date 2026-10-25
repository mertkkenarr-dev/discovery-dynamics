/**
 * K10 grafikleri: alt türlerin risk-ödül haritası ve hibrit tür çiftleri. Sayılar ozet.json → k10 (2021–2025 çıkışlı oyunlar).
 */
import { baseOptions, halo, Plot, type Colors } from './site/charts'
import { sayi, type Ozet, type TurKarne } from './veri'

type Kur = (o: { width: number; colors: Colors }) => SVGSVGElement | HTMLElement

/** Sol üst çeyrek: görünmez oranı ortalamanın altında, hit oranı üstünde. */
export const azRiskliOdullu = (oz: Ozet) => (k: TurKarne) => k.hit > oz.k10.ort_hit && k.gorunmez < oz.k10.ort_gorunmez

export const karneGrafik = (oz: Ozet): Kur => ({ width, colors: c }) => {
  const d = oz.k10.karne
  const iyi = azRiskliOdullu(oz)
  const sirali = [...d].sort((a, z) => z.hit - a.hit)
  const etiketli = new Set([...sirali.slice(0, 5), ...sirali.slice(-3)].map((k) => k.tur))
  return Plot.plot({
    ...baseOptions(width, c, 300),
    marginLeft: 40,
    marginRight: 70,
    x: { label: 'Görünmez kalan oyun payı (risk)', tickFormat: (v: number) => `%${v}`, labelArrow: 'none', labelAnchor: 'center', labelOffset: 36 },
    y: { label: null, tickFormat: (v: number) => `%${v}`, grid: true },
    r: { range: [2, 9] },
    marks: [
      Plot.ruleY([oz.k10.ort_hit], { stroke: c.muted, strokeDasharray: '3,3' }),
      Plot.ruleX([oz.k10.ort_gorunmez], { stroke: c.muted, strokeDasharray: '3,3' }),
      Plot.dot(d, { x: 'gorunmez', y: 'hit', r: 'n', fill: (k: TurKarne) => (iyi(k) ? c.accent : c.s2), fillOpacity: 0.85, stroke: c.ground, strokeWidth: 1,
        title: (k: TurKarne) => `${k.tur}: hit %${sayi(k.hit, 1)}, görünmez %${sayi(k.gorunmez, 0)}, ${sayi(k.n)} oyun` }),  // fmt: skip
      Plot.text(d.filter((k) => etiketli.has(k.tur)), { x: 'gorunmez', y: 'hit', text: 'tur', dx: 8, textAnchor: 'start', fill: c.ink, fontSize: 11, ...halo(c) }),
      Plot.text([{ x: oz.k10.ort_gorunmez, y: oz.k10.ort_hit }], { x: 'x', y: 'y', text: () => 'ortalama', dx: 4, dy: -8, textAnchor: 'start', fill: c.muted, fontSize: 10 }),
    ],
  })
}

export const hibritGrafik = (oz: Ozet): Kur => ({ width, colors: c }) => {
  const d = [...oz.k10.hibrit_uc].sort((a, z) => z.ob - a.ob)
  return Plot.plot({
    ...baseOptions(width, c, 40 + d.length * 24),
    marginLeft: Math.min(270, width * 0.55),
    marginRight: 40,
    marginBottom: 32,
    x: { label: null, type: 'log', domain: [0.1, 12], ticks: [0.25, 0.5, 1, 2, 4, 8], tickFormat: (v: number) => `×${sayi(v, v < 1 ? 2 : 0)}`, grid: true },
    y: { label: null, domain: d.map((v) => v.cift), tickSize: 0 },
    marks: [
      Plot.ruleX([1], { stroke: c.ink }),
      Plot.ruleY(d, { y: 'cift', x1: (v: { alt: number }) => Math.max(v.alt, 0.1), x2: (v: { ust: number }) => Math.min(v.ust, 12), stroke: (v: { q: number }) => (v.q < 0.05 ? c.accent : c.s2), strokeWidth: 2 }),
      Plot.dot(d.filter((v) => v.ob > 0), { y: 'cift', x: 'ob', r: 4, fill: (v: { q: number }) => (v.q < 0.05 ? c.accent : c.s2), stroke: c.ground, strokeWidth: 1.5 }),
    ],
  })
}
