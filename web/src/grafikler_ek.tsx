/**
 * K5–K8 grafikleri. grafikler.tsx ile aynı kurallar: tek eksen, doğrudan etiket, sayılar ozet.json'dan.
 */
import { baseOptions, halo, Plot, type Colors } from './site/charts'
import { sayi, type Ozet } from './veri'

type Kur = (o: { width: number; colors: Colors }) => SVGSVGElement | HTMLElement

const yz = (v: number, d = 1) => `%${sayi(v, d)}`

export const klonGrafik = (oz: Ozet): Kur => ({ width, colors: c }) => {
  const k = oz.k5
  const dl = Object.entries(k.takipci_dilim)
  const d = [
    { ad: 'Önce', v: k.oncul.hit_oran, alt: k.oncul.wilson[0], ust: k.oncul.wilson[1], tur: 'oncul' },
    ...dl.map(([ad, v]) => ({ ad, v: v.oran, alt: v.alt, ust: v.ust, tur: 'takipci' })),
    { ad: 'Sıradan', v: k.plasebo.hit_oran, alt: k.plasebo.wilson[0], ust: k.plasebo.wilson[1], tur: 'plasebo' },
  ]
  const renk = (t: string) => (t === 'takipci' ? c.accent : t === 'oncul' ? c.ink : c.s2)
  return Plot.plot({
    ...baseOptions(width, c, 200),
    marginLeft: 8,
    marginBottom: 40,
    x: { label: null, domain: d.map((v) => v.ad), padding: 0.25 },
    y: { axis: null, domain: [0, Math.max(...d.map((v) => v.ust)) * 1.25] },
    marks: [
      Plot.barY(d, { x: 'ad', y: 'v', fill: (v: { tur: string }) => renk(v.tur), fillOpacity: 0.9, rx: 2 }),
      Plot.ruleX(d, { x: 'ad', y1: 'alt', y2: 'ust', stroke: c.muted, strokeWidth: 1.5 }),
      Plot.text(d, { x: 'ad', y: 'ust', text: (v: { v: number }) => yz(v.v), dy: -10, fill: c.ink, fontWeight: 600, ...halo(c) }),
      Plot.ruleY([0], { stroke: c.rule }),
    ],
  })
}

export const firsatGrafik = (oz: Ozet): Kur => ({ width, colors: c }) => {
  const d = oz.k6.bolgeler.slice(0, 7).map((b) => ({ ...b, kisa: b.ad.split(' \u00b7 ').slice(0, 2).join(', ') }))
  return Plot.plot({
    ...baseOptions(width, c, 40 + d.length * 30),
    marginLeft: Math.min(190, width * 0.45),
    marginRight: 46,
    marginBottom: 32,
    x: { label: null, domain: [0, Math.max(...d.map((v) => v.ust)) * 1.05], ticks: [0, 1, 2, 3], tickFormat: (v: number) => `×${v}`, grid: true },
    y: { label: null, domain: d.map((v) => v.kisa), tickSize: 0 },
    marks: [
      Plot.ruleX([1], { stroke: c.muted, strokeDasharray: '3,3' }),
      Plot.ruleY(d, { y: 'kisa', x1: 'alt', x2: 'ust', stroke: (v: { firsat: boolean }) => (v.firsat ? c.accent : c.s2), strokeWidth: 2 }),
      Plot.dot(d, { y: 'kisa', x: 'ob', r: 4.5, fill: (v: { firsat: boolean }) => (v.firsat ? c.accent : c.s2), stroke: c.ground, strokeWidth: 1.5 }),
      Plot.text(d, { y: 'kisa', x: 'ust', text: (v: { ob: number }) => `×${sayi(v.ob, 1)}`, dx: 6, textAnchor: 'start', fill: c.ink, fontSize: 11 }),
    ],
  })
}

export const gizliGrafik = (oz: Ozet): Kur => ({ width, colors: c }) => {
  const ad: Record<string, string> = { 'Tür: Simulation': 'Simulation türü', 'Early Access ile çıkış': 'Early Access', 'Playtest': 'Playtest',
    'Stüdyonun önceki oyunu var': 'Önceki oyunu var', 'Çıkıştan önce demo': 'Çıkış öncesi demo', 'Kendi yayını': 'Kendi yayını' }  // fmt: skip
  const d = Object.entries(oz.k7.farklar).map(([k, v]) => ({ ad: ad[k] ?? k, gizli: v.gizli * 100, gorunur: v.gorunur * 100 }))
  return Plot.plot({
    ...baseOptions(width, c, 40 + d.length * 30),
    marginLeft: Math.min(140, width * 0.36),
    marginRight: 20,
    marginBottom: 32,
    x: { label: null, domain: [0, 100], ticks: [0, 25, 50, 75, 100], tickFormat: (v: number) => `%${v}`, grid: true },
    y: { label: null, domain: d.map((v) => v.ad), tickSize: 0 },
    marks: [
      Plot.ruleY(d, { y: 'ad', x1: 'gizli', x2: 'gorunur', stroke: c.rule, strokeWidth: 2 }),
      Plot.dot(d, { y: 'ad', x: 'gizli', r: 4.5, fill: c.s2, stroke: c.ground, strokeWidth: 1.5 }),
      Plot.dot(d, { y: 'ad', x: 'gorunur', r: 4.5, fill: c.accent, stroke: c.ground, strokeWidth: 1.5 }),
      Plot.text(d.slice(0, 1), { y: 'ad', x: 'gizli', text: () => 'gizli', dy: -12, fill: c.muted, fontSize: 11 }),
      Plot.text(d.slice(0, 1), { y: 'ad', x: 'gorunur', text: () => 'görünür', dy: -12, fill: c.muted, fontSize: 11 }),
    ],
  })
}

export const esikGrafik = (oz: Ozet): Kur => ({ width, colors: c }) => {
  // 10 eşiği gösterilmez: seri yalnız ömür boyu 10+ incelemeli oyunlarda var, eşik altı seçilimli (metinde açıklanıyor).
  const yuz = (v: number) => (Math.exp(v) - 1) * 100
  const d = oz.k8.tahmin.filter((t) => t.esik !== 10).map((t) => ({ esik: String(t.esik), v: yuz(t.sicrama), alt: yuz(t.alt), ust: yuz(t.ust), gercek: t.esik === 50 }))
  return Plot.plot({
    ...baseOptions(width, c, 210),
    marginLeft: 44,
    x: { label: 'Toplam inceleme eşiği', domain: d.map((v) => v.esik), padding: 0.4, labelArrow: 'none', labelAnchor: 'center', labelOffset: 36 },
    y: { label: null, domain: [-5, 5], ticks: [-4, -2, 0, 2, 4], tickFormat: (v: number) => `${v > 0 ? '+' : v < 0 ? '−' : ''}%${Math.abs(v)}`, grid: true },
    marks: [
      Plot.ruleY([0], { stroke: c.muted }),
      Plot.ruleX(d, { x: 'esik', y1: 'alt', y2: 'ust', stroke: (v: { gercek: boolean }) => (v.gercek ? c.accent : c.s2), strokeWidth: 2.5 }),
      Plot.dot(d, { x: 'esik', y: 'v', r: 4.5, fill: (v: { gercek: boolean }) => (v.gercek ? c.accent : c.s2), stroke: c.ground, strokeWidth: 1.5 }),
      Plot.text(d.filter((v) => v.gercek), { x: 'esik', y: 'ust', text: () => '“50 eşiği”', dy: -10, fill: c.ink, fontWeight: 600, ...halo(c) }),
    ],
  })
}
