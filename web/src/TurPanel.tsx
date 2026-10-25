/**
 * Etkileşimli tür paneli: alt tür seçilince oyunları haritada yanar (App → Sahne maskesi), karnesi burada açılır.
 * Değerler K10'dan (2021–2025 çıkışlı bağımsız oyunlar); karşılaştırma için 67 tür içindeki sıra da verilir.
 */
import { useMemo } from 'react'
import { sayi, yuzde, type Ozet } from './veri'

const FIYAT: Record<string, string> = { '<5': '5 dolar altı', '5-10': '5–10 dolar', '10-20': '10–20 dolar', '20-30': '20–30 dolar', '>=30': '30 dolar ve üstü' }

export function TurPanel({ oz, secili, onSec }: { oz: Ozet; secili: number; onSec: (i: number) => void }) {
  const k = oz.k10.karne
  const alfabetik = useMemo(() => k.map((x, i) => ({ ad: x.tur, i })).sort((a, z) => a.ad.localeCompare(z.ad, 'tr')), [k])
  const t = k[secili]
  if (!t) return null
  const sira = [...k].sort((a, z) => z.hit - a.hit).findIndex((x) => x.tur === t.tur) + 1
  const anlamli = t.egilim_alt > 0 || t.egilim_ust < 0
  const satirlar: [string, string][] = [
    ['Hit oranı', `${yuzde(t.hit, 1)} (%95 aralık ${sayi(t.hit_alt, 1)}–${sayi(t.hit_ust, 1)}); ${k.length} tür içinde ${sira}. sırada`],
    ['Görünmez kalan', `${yuzde(t.gorunmez, 0)} (ortalama ${yuzde(oz.k10.ort_gorunmez, 0)})`],
    ['Beklenene göre', `×${sayi(t.ob, 2)} hit; fiyat, yıl ve dil karışımı ayrıldığında${t.ob_alt > 1 ? ', beklenenden iyi' : t.ob_ust < 1 ? ', beklenenden kötü' : ', fark belirsiz'}`],
    ['Arz', `2022–2025'te ${sayi(t.arz_22_25)} oyun; büyüme Steam ortalamasının ${sayi(t.goreli_buyume, 1)} katı`],
    ['En iyi fiyat bandı', t.tatli_fiyat ? `${FIYAT[t.tatli_fiyat] ?? t.tatli_fiyat} (hit ${yuzde(t.tatli_fiyat_hit ?? 0, 1)})` : 'yeterli veri yok'],
    ['Eğilim', `${yuzde(t.hit_erken, 1)} → ${yuzde(t.hit_gec, 1)} (2021–22 → 2023–24)${anlamli ? '' : ', anlamlı değil'}`],
  ]
  return (
    <div className="tur-panel">
      <label className="arama">
        <span>Alt tür</span>
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
        <p className="tur-n">{sayi(t.n)} bağımsız oyun</p>
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
