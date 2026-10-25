/**
 * Etkileşimli tür paneli: alt tür seçilince oyunları haritada yanar (App → Sahne maskesi), karnesi burada açılır.
 * Değerler K10'dan (2021–2025 çıkışlı bağımsız oyunlar); karşılaştırma için 67 tür içindeki sıra da verilir.
 */
import { useMemo } from 'react'
import { bicim, useDil } from './dil'
import type { Ozet } from './veri'

const FIYAT: Record<'tr' | 'en', Record<string, string>> = {
  tr: { '<5': '5 dolar altı', '5-10': '5–10 dolar', '10-20': '10–20 dolar', '20-30': '20–30 dolar', '>=30': '30 dolar ve üstü' },
  en: { '<5': 'Under $5', '5-10': '$5–10', '10-20': '$10–20', '20-30': '$20–30', '>=30': '$30 and up' },
}

export function TurPanel({ oz, secili, onSec }: { oz: Ozet; secili: number; onSec: (i: number) => void }) {
  const dil = useDil()
  const { sayi, yuzde } = bicim(dil)
  const k = oz.k10.karne
  const alfabetik = useMemo(() => k.map((x, i) => ({ ad: x.tur, i })).sort((a, z) => a.ad.localeCompare(z.ad, dil)), [k, dil])
  const t = k[secili]
  if (!t) return null
  const sira = [...k].sort((a, z) => z.hit - a.hit).findIndex((x) => x.tur === t.tur) + 1
  const anlamli = t.egilim_alt > 0 || t.egilim_ust < 0
  const fiyat = t.tatli_fiyat ? `${FIYAT[dil][t.tatli_fiyat] ?? t.tatli_fiyat} (hit ${yuzde(t.tatli_fiyat_hit ?? 0, 1)})` : null
  const durum = t.ob_alt > 1 ? ['beklenenden iyi', 'better than expected'] : t.ob_ust < 1 ? ['beklenenden kötü', 'worse than expected'] : ['fark belirsiz', 'difference uncertain']
  const satirlar: [string, string][] = dil === 'tr'
    ? [
        ['Hit oranı', `${yuzde(t.hit, 1)} (%95 aralık ${sayi(t.hit_alt, 1)}–${sayi(t.hit_ust, 1)}); ${k.length} tür içinde ${sira}. sırada`],
        ['Görünmez kalan', `${yuzde(t.gorunmez, 0)} (ortalama ${yuzde(oz.k10.ort_gorunmez, 0)})`],
        ['Beklenene göre', `×${sayi(t.ob, 2)} hit; fiyat, yıl ve dil karışımı ayrıldığında, ${durum[0]}`],
        ['Arz', `2022–2025'te ${sayi(t.arz_22_25)} oyun; büyüme Steam ortalamasının ${sayi(t.goreli_buyume, 1)} katı`],
        ['En iyi fiyat bandı', fiyat ?? 'yeterli veri yok'],
        ['Eğilim', `${yuzde(t.hit_erken, 1)} → ${yuzde(t.hit_gec, 1)} (2021–22 → 2023–24)${anlamli ? '' : ', anlamlı değil'}`],
      ]
    : [
        ['Hit rate', `${yuzde(t.hit, 1)} (95% interval ${sayi(t.hit_alt, 1)}–${sayi(t.hit_ust, 1)}); ranked ${sira} of ${k.length} genres`],
        ['Stay invisible', `${yuzde(t.gorunmez, 0)} (average ${yuzde(oz.k10.ort_gorunmez, 0)})`],
        ['Vs expected', `×${sayi(t.ob, 2)} hits after accounting for price, year and languages; ${durum[1]}`],
        ['Supply', `${sayi(t.arz_22_25)} games in 2022–2025; growing ${sayi(t.goreli_buyume, 1)}× as fast as Steam overall`],
        ['Best price band', fiyat ?? 'not enough data'],
        ['Trend', `${yuzde(t.hit_erken, 1)} → ${yuzde(t.hit_gec, 1)} (2021–22 → 2023–24)${anlamli ? '' : ', not significant'}`],
      ]  // fmt: skip
  return (
    <div className="tur-panel">
      <label className="arama">
        <span>{dil === 'tr' ? 'Alt tür' : 'Subgenre'}</span>
        <select value={secili} onChange={(e) => onSec(Number(e.target.value))}>
          {alfabetik.map(({ ad, i }) => (
            <option key={ad} value={i}>
              {ad}
            </option>
          ))}
        </select>
      </label>
      <article className="tur-karne" aria-live="polite">
        <h3>{t.tur}</h3>
        <p className="tur-n">
          {sayi(t.n)} {dil === 'tr' ? 'bağımsız oyun' : 'indie games'}
        </p>
        <dl>
          {satirlar.map(([ad, deger]) => (
            <div key={ad}>
              <dt>{ad}</dt>
              <dd>{deger}</dd>
            </div>
          ))}
        </dl>
      </article>
    </div>
  )
}
