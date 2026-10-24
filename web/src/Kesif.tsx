/**
 * Keşif: ada göre arama, yıldıza uçuş, seçili oyunun künyesi. Ad listesi (≈2,9 MB) yalnız bu bölüme gelince indirilir.
 * Üzerine gelme bilgisi küçük bir dış depoda tutulur: her fare hareketi tüm sayfayı (ve Canvas'ı) yeniden çizdirmesin.
 */
import { useDeferredValue, useEffect, useMemo, useState, useSyncExternalStore } from 'react'
import type { Isaret } from './galaksi/Yildizlar'
import { BAYRAK, jsonYukle, type Galaksi } from './veri'

type Adlar = [number, string][]
type AdDurumu = { durum: 'bekliyor' } | { durum: 'yukleniyor' } | { durum: 'hata'; mesaj: string } | { durum: 'hazir'; adlar: Adlar }

const KADEME = ['10’dan az inceleme', '10–99 inceleme', '100–499 inceleme', 'Hit: 500–4.999 inceleme', 'Büyük hit: 5.000+ inceleme']
const FIYAT = ['Ücretsiz', '5 dolar altı', '5–10 dolar', '10–20 dolar', '20–30 dolar', '30 dolar ve üstü']

let isaret: Isaret | null = null
const dinleyiciler = new Set<() => void>()
export const isaretAyarla = (i: Isaret | null) => {
  if (i?.i === isaret?.i && i?.x === isaret?.x) return
  isaret = i
  dinleyiciler.forEach((f) => f())
}
const abone = (f: () => void) => (dinleyiciler.add(f), () => void dinleyiciler.delete(f))

const sade = (s: string) => s.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase()

export function useAdlar(etkin: boolean): AdDurumu {
  const [d, setD] = useState<AdDurumu>({ durum: 'bekliyor' })
  useEffect(() => {
    if (!etkin || d.durum !== 'bekliyor') return
    setD({ durum: 'yukleniyor' })
    jsonYukle<Adlar>('adlar.json')
      .then((adlar) => setD({ durum: 'hazir', adlar }))
      .catch((e: unknown) => setD({ durum: 'hata', mesaj: e instanceof Error ? e.message : 'Ad listesi yüklenemedi.' }))
  }, [etkin, d.durum])
  return d
}

export function Ipucu({ adlar }: { adlar: Adlar | null }) {
  const i = useSyncExternalStore(abone, () => isaret)
  if (!i || !adlar) return null
  return (
    <div className="ipucu" style={{ transform: `translate(${i.x + 14}px, ${i.y + 14}px)` }} role="status">
      {adlar[i.i]?.[1]}
    </div>
  )
}

interface Props {
  g: Galaksi
  ad: AdDurumu
  secili: number | null
  onSec: (i: number | null) => void
}

export function Kesif({ g, ad, secili, onSec }: Props) {
  const [sorgu, setSorgu] = useState('')
  const ertelenen = useDeferredValue(sorgu)
  const adlar = ad.durum === 'hazir' ? ad.adlar : null
  const dizin = useMemo(() => adlar?.map(([, n]) => sade(n)) ?? null, [adlar])

  const sonuclar = useMemo(() => {
    const q = sade(ertelenen.trim())
    if (!dizin || q.length < 2) return []
    const bas: number[] = []
    const ic: number[] = []
    for (let i = 0; i < dizin.length && bas.length < 8; i++) {
      const p = dizin[i]!.indexOf(q)
      if (p === 0) bas.push(i)
      else if (p > 0 && ic.length < 8) ic.push(i)
    }
    return [...bas, ...ic].slice(0, 8)
  }, [dizin, ertelenen])

  return (
    <div className="kesif-panel">
      <label className="arama">
        <span>Bir oyun ara</span>
        <input
          type="search"
          value={sorgu}
          onChange={(e) => setSorgu(e.target.value)}
          placeholder={ad.durum === 'hazir' ? 'ör. Vampire Survivors' : 'Ad listesi yükleniyor…'}
          disabled={ad.durum !== 'hazir'}
          autoComplete="off"
          spellCheck={false}
        />
      </label>
      {ad.durum === 'hata' && <p className="hata">{ad.mesaj} Sayfayı yenileyip tekrar deneyin.</p>}
      {sorgu.trim().length >= 2 && adlar && (
        <ul className="sonuclar" aria-label="Arama sonuçları">
          {sonuclar.length === 0 && <li className="bos">Bu adla bir oyun yok. Haritada yalnız 2018–2025 arasında çıkmış ve en az üç içerik etiketi olan oyunlar var.</li>}
          {sonuclar.map((i) => (
            <li key={i}>
              <button type="button" aria-pressed={secili === i} onClick={() => onSec(i)}>
                {adlar[i]![1]} <span className="yil">{2018 + g.yil[i]!}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
      {secili !== null && adlar && <Kunye g={g} i={secili} adlar={adlar} onKapat={() => onSec(null)} />}
    </div>
  )
}

function Kunye({ g, i, adlar, onKapat }: { g: Galaksi; i: number; adlar: Adlar; onKapat: () => void }) {
  const [appid, ad] = adlar[i]!
  const b = g.bayrak[i]!
  const etiketler = [
    b & BAYRAK.ea && 'Erken Erişim ile başladı',
    b & BAYRAK.cokOyunculu && 'Birlikte oynanır',
    b & BAYRAK.cince && 'Çince destekli',
    b & BAYRAK.yapayZeka && 'Yapay zekâ beyanı var',
    !(b & BAYRAK.organik) && 'Yerleşik bir yayıncıyla çıktı',
  ].filter((v): v is string => typeof v === 'string')
  const k = g.kademe[i]!
  return (
    <article className="kunye" aria-live="polite">
      <h3>{ad}</h3>
      <dl>
        <dt>Çıkış</dt>
        <dd>{2018 + g.yil[i]!}</dd>
        <dt>İlk yıl</dt>
        <dd>{k <= 4 ? KADEME[k] : 'Henüz bir yılı dolmadı'}</dd>
        <dt>Fiyat</dt>
        <dd>{FIYAT[g.fiyat[i]!] ?? 'Bilinmiyor'}</dd>
      </dl>
      {etiketler.length > 0 && <p className="bayraklar">{etiketler.join(', ')}</p>}
      <div className="kunye-alt">
        <a href={`https://store.steampowered.com/app/${appid}`} target="_blank" rel="noreferrer">Steam sayfasını aç</a>
        <button type="button" onClick={onKapat}>Seçimi kaldır</button>
      </div>
    </article>
  )
}
