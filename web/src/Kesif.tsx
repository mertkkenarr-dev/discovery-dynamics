/**
 * Keşif: ada göre arama, yıldıza uçuş, seçili oyunun künyesi. Ad listesi (≈2,9 MB) yalnız bu bölüme gelince indirilir.
 * Üzerine gelme bilgisi küçük bir dış depoda tutulur: her fare hareketi tüm sayfayı (ve Canvas'ı) yeniden çizdirmesin.
 */
import { useDeferredValue, useEffect, useMemo, useState, useSyncExternalStore } from 'react'
import type { Isaret } from './galaksi/Yildizlar'
import { useDil } from './dil'
import { BAYRAK, jsonYukle, type Galaksi } from './veri'

type Adlar = [number, string][]
type AdDurumu = { durum: 'bekliyor' } | { durum: 'yukleniyor' } | { durum: 'hata'; mesaj: string } | { durum: 'hazir'; adlar: Adlar }

const M = {
  tr: {
    kademe: ['10’dan az inceleme', '10–99 inceleme', '100–499 inceleme', 'Hit: 500–4.999 inceleme', 'Büyük hit: 5.000+ inceleme'],
    fiyat: ['Ücretsiz', '5 dolar altı', '5–10 dolar', '10–20 dolar', '20–30 dolar', '30 dolar ve üstü'],
    ara: 'Bir oyun ara', ornek: 'ör. Vampire Survivors', yukleniyor: 'Ad listesi yükleniyor…', tekrar: 'Sayfayı yenileyip tekrar deneyin.',
    sonuclar: 'Arama sonuçları', bos: 'Bu adla bir oyun yok. Haritada yalnız 2018–2025 arasında çıkmış ve en az üç içerik etiketi olan oyunlar var.',
    ea: 'Erken Erişim ile başladı', birlikte: 'Birlikte oynanır', cince: 'Çince destekli', yz: 'Yapay zekâ beyanı var', yayinci: 'Yerleşik bir yayıncıyla çıktı',
    cikis: 'Çıkış', ilkYil: 'İlk yıl', dolmadi: 'Henüz bir yılı dolmadı', fiyatEt: 'Fiyat', bilinmiyor: 'Bilinmiyor', steam: 'Steam sayfasını aç', kaldir: 'Seçimi kaldır',
  },
  en: {
    kademe: ['Fewer than 10 reviews', '10–99 reviews', '100–499 reviews', 'Hit: 500–4,999 reviews', 'Big hit: 5,000+ reviews'],
    fiyat: ['Free', 'Under $5', '$5–10', '$10–20', '$20–30', '$30 and up'],
    ara: 'Search for a game', ornek: 'e.g. Vampire Survivors', yukleniyor: 'Loading game names…', tekrar: 'Reload the page and try again.',
    sonuclar: 'Search results', bos: 'No game with that name. The map only includes games released 2018–2025 with at least three content tags.',
    ea: 'Launched in Early Access', birlikte: 'Played together', cince: 'Supports Chinese', yz: 'Discloses AI use', yayinci: 'Released with an established publisher',
    cikis: 'Released', ilkYil: 'First year', dolmadi: 'Not a full year yet', fiyatEt: 'Price', bilinmiyor: 'Unknown', steam: 'Open Steam page', kaldir: 'Clear selection',
  },
} as const

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
  const m = M[useDil()]
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
        <span>{m.ara}</span>
        <input
          type="search"
          value={sorgu}
          onChange={(e) => setSorgu(e.target.value)}
          placeholder={ad.durum === 'hazir' ? m.ornek : m.yukleniyor}
          disabled={ad.durum !== 'hazir'}
          autoComplete="off"
          spellCheck={false}
        />
      </label>
      {ad.durum === 'hata' && <p className="hata">{ad.mesaj} {m.tekrar}</p>}
      {sorgu.trim().length >= 2 && adlar && (
        <ul className="sonuclar" aria-label={m.sonuclar}>
          {sonuclar.length === 0 && <li className="bos">{m.bos}</li>}
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
  const m = M[useDil()]
  const [appid, ad] = adlar[i]!
  const b = g.bayrak[i]!
  const etiketler = [
    b & BAYRAK.ea && m.ea,
    b & BAYRAK.cokOyunculu && m.birlikte,
    b & BAYRAK.cince && m.cince,
    b & BAYRAK.yapayZeka && m.yz,
    !(b & BAYRAK.organik) && m.yayinci,
  ].filter((v) => typeof v === 'string') as string[]
  const k = g.kademe[i]!
  return (
    <article className="kunye" aria-live="polite">
      <h3>{ad}</h3>
      <dl>
        <dt>{m.cikis}</dt>
        <dd>{2018 + g.yil[i]!}</dd>
        <dt>{m.ilkYil}</dt>
        <dd>{k <= 4 ? m.kademe[k] : m.dolmadi}</dd>
        <dt>{m.fiyatEt}</dt>
        <dd>{m.fiyat[g.fiyat[i]!] ?? m.bilinmiyor}</dd>
      </dl>
      {etiketler.length > 0 && <p className="bayraklar">{etiketler.join(', ')}</p>}
      <div className="kunye-alt">
        <a href={`https://store.steampowered.com/app/${appid}`} target="_blank" rel="noreferrer">{m.steam}</a>
        <button type="button" onClick={onKapat}>{m.kaldir}</button>
      </div>
    </article>
  )
}
