/**
 * Bölüm grafikleri. Her grafik tek eksen, tek ölçü; sonuç doğrudan etiketle grafiğin üstünde yazar.
 * Sayılar ozet.json'dan gelir (analiz JSON'larından türetilmiş); burada elle sayı yazılmaz.
 */
import { axis, baseOptions, halo, Plot, type Colors } from './site/charts'
import { bicim, t, type Dil } from './dil'
import type { Ozet } from './veri'

type Kur = (o: { width: number; colors: Colors }) => SVGSVGElement | HTMLElement

const H = 220

export const arzGrafik = (oz: Ozet, dil: Dil = 'tr'): Kur => ({ width, colors: c }) => {
  const b = bicim(dil)
  const d = Object.entries(oz.arz).map(([yil, n]) => ({ yil: +yil, n }))
  const uc = [d[0]!, d[d.length - 1]!]
  return Plot.plot({
    ...baseOptions(width, c, 180),
    marginLeft: 8,
    marginBottom: 28,
    x: { label: null, tickFormat: (v: number) => `’${String(v).slice(2)}`, padding: 0.18 },
    y: { axis: null, domain: [0, Math.max(...d.map((v) => v.n)) * 1.18] },
    marks: [
      Plot.barY(d, { x: 'yil', y: 'n', fill: c.s2, rx: 2, title: (v: { yil: number; n: number }) => `${v.yil}: ${b.sayi(v.n)} ${t(dil, 'oyun', 'games')}` }),
      Plot.text(uc, { x: 'yil', y: 'n', text: (v: { n: number }) => b.sayi(v.n), dy: -10, fill: c.ink, fontWeight: 600, ...halo(c) }),
      Plot.ruleY([0], { stroke: c.rule }),
    ],
  })
}

export const hitYilGrafik = (oz: Ozet, dil: Dil = 'tr'): Kur => ({ width, colors: c }) => {
  const b = bicim(dil)
  const d = Object.entries(oz.hit_yil).map(([yil, v]) => ({ yil: +yil, v }))
  return Plot.plot({
    ...baseOptions(width, c, 150),
    marginBottom: 28,
    marginLeft: 36,
    x: { label: null, tickFormat: (v: number) => `’${String(v).slice(2)}`, ticks: d.map((v) => v.yil) },
    y: { label: null, domain: [0, 10], ticks: [0, 5, 10], tickFormat: (v: number) => b.yuzde(v), grid: true },
    marks: [
      Plot.lineY(d, { x: 'yil', y: 'v', stroke: c.accent, strokeWidth: 2 }),
      Plot.dot(d, { x: 'yil', y: 'v', fill: c.accent, r: 4, stroke: c.ground, strokeWidth: 2, title: (v: { yil: number; v: number }) => `${v.yil}: ${b.yuzde(v.v, 1)} hit` }),
    ],
  })
}

export const fiyatGrafik = (oz: Ozet, dil: Dil = 'tr'): Kur => ({ width, colors: c }) => {
  const b = bicim(dil)
  const d = Object.entries(oz.fiyat_hit).map(([f, v]) => ({ f: +f, v }))
  const uc = [d[0]!, d[d.length - 1]!]
  return Plot.plot({
    ...baseOptions(width, c, H),
    marginLeft: 40,
    marginRight: 30,
    x: { label: t(dil, 'Fiyat (USD)', 'Price (USD)'), type: 'log', ticks: [1, 2, 5, 10, 20, 30], tickFormat: (v: number) => `$${v}`, ...axis },
    y: { label: null, domain: [0, 32], ticks: [0, 10, 20, 30], tickFormat: (v: number) => b.yuzde(v), grid: true },
    marks: [
      Plot.lineY(d, { x: 'f', y: 'v', stroke: c.accent, strokeWidth: 2, curve: 'monotone-x' }),
      Plot.dot(d, { x: 'f', y: 'v', fill: c.accent, r: 4, stroke: c.ground, strokeWidth: 2, title: (v: { f: number; v: number }) => `$${v.f}: ${b.yuzde(v.v, 1)} hit` }),
      Plot.text(uc, { x: 'f', y: 'v', text: (v: { v: number }) => `${b.yuzde(v.v, 1)}`, dy: -14, fill: c.ink, fontWeight: 600, ...halo(c) }),
    ],
  })
}

export const ilkAyGrafik = (oz: Ozet, dil: Dil = 'tr'): Kur => ({ width, colors: c }) => {
  const b = bicim(dil)
  const d = Object.entries(oz.ilk_ay.hit).map(([bant, v]) => ({ bant, v }))
  return Plot.plot({
    ...baseOptions(width, c, H),
    marginLeft: 8,
    x: { label: t(dil, 'İlk 30 günde inceleme', 'Reviews in the first 30 days'), domain: d.map((v) => v.bant), padding: 0.2, ...axis },
    y: { axis: null, domain: [0, 112] },
    marks: [
      Plot.barY(d, { x: 'bant', y: 'v', fill: (v: { v: number }) => (v.v >= 50 ? c.accent : c.s2), rx: 2, title: (v: { bant: string; v: number }) => `${v.bant}: ${b.yuzde(v.v, 1)} hit` }),
      Plot.text(d.filter((v) => v.v >= 1), { x: 'bant', y: 'v', text: (v: { v: number }) => `${b.yuzde(v.v, 0)}`, dy: -10, fill: c.ink, fontWeight: 600, ...halo(c) }),
      Plot.ruleY([0], { stroke: c.rule }),
    ],
  })
}

export const yapayZekaGrafik = (oz: Ozet, dil: Dil = 'tr'): Kur => ({ width, colors: c }) => {
  const b = bicim(dil)
  const g = oz.yapay_zeka.gorunmez
  const [yok, var_] = [t(dil, 'Beyan yok', 'No disclosure'), t(dil, 'Beyan var', 'AI disclosed')]
  const d = [
    { ad: yok, v: (g['0']?.gorunmez ?? 0) * 100 },
    { ad: var_, v: (g['1']?.gorunmez ?? 0) * 100 },
  ]
  return Plot.plot({
    ...baseOptions(width, c, 120),
    marginLeft: 96,
    marginRight: 48,
    marginBottom: 12,
    marginTop: 8,
    x: { axis: null, domain: [0, 100] },
    y: { label: null, domain: d.map((v) => v.ad), tickSize: 0, padding: 0.3 },
    marks: [
      Plot.barX(d, { y: 'ad', x: 100, fill: c.rule, fillOpacity: 0.3, rx: 2 }),
      Plot.barX(d, { y: 'ad', x: 'v', fill: (v: { ad: string }) => (v.ad === yok ? c.s2 : c.accent), rx: 2 }),
      Plot.text(d, { y: 'ad', x: 'v', text: (v: { v: number }) => `${b.yuzde(v.v, 0)}`, dx: 8, textAnchor: 'start', fill: c.ink, fontWeight: 600 }),
    ],
  })
}
