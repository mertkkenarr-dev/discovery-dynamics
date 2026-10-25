/**
 * Sayfa iskeleti. Veri durumu ayrık birleşimle tutulur (yükleniyor / hata / hazır); Canvas veri hazır olmadan kurulmaz.
 * Sahneye giden durum yalnız etkin bölüm ya da seçim değişince yeniden hesaplanır.
 */
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Anahtar, Anlati, Dizin, useEtkinBolum } from './Anlati'
import { bolumler } from './bolumler'
import { maskeUretici, tekYildiz } from './galaksi/maske'
import { Sahne, type SahneDurumu } from './galaksi/Sahne'
import { Ipucu, isaretAyarla, Kesif, useAdlar } from './Kesif'
import { QualityProvider } from './kit/quality'
import { Son } from './Son'
import { ekDe } from './lib/ek'
import { galaksiYukle, jsonYukle, sayi, type Cift, type Galaksi, type Ozet } from './veri'

type Durum = { durum: 'yukleniyor' } | { durum: 'hata'; mesaj: string } | { durum: 'hazir'; g: Galaksi; oz: Ozet; ciftler: Cift[] }

const hareketAzalt = window.matchMedia('(prefers-reduced-motion: reduce)').matches

export function App() {
  const [d, setD] = useState<Durum>({ durum: 'yukleniyor' })
  const [etkin, setEtkin] = useState('giris')
  const [secili, setSecili] = useState<number | null>(null)

  useEffect(() => {
    Promise.all([galaksiYukle(), jsonYukle<Ozet>('ozet.json'), jsonYukle<Cift[]>('ikinci.json')])
      .then(([g, oz, ciftler]) => setD({ durum: 'hazir', g, oz, ciftler }))
      .catch((e: unknown) => setD({ durum: 'hata', mesaj: e instanceof Error ? e.message : 'Veri yüklenemedi.' }))
  }, [])

  const hazir = d.durum === 'hazir' ? d : null
  const liste = useMemo(() => (hazir ? bolumler(hazir.oz, hazir.g) : []), [hazir])
  const maske = useMemo(() => (hazir ? maskeUretici(hazir.g, hazir.oz.k5.dalgalar.slice(0, 2).flatMap((d) => d.takipci)) : null), [hazir])
  const kesifte = etkin === 'kesif'
  const ad = useAdlar(kesifte || secili !== null)
  const secAd = secili !== null && ad.durum === 'hazir' ? ad.adlar[secili]?.[1] : undefined

  useEtkinBolum(useCallback((id: string) => setEtkin(id), []), hazir !== null)

  const sahne = useMemo<SahneDurumu | null>(() => {
    if (!hazir || !maske) return null
    const b = liste.find((x) => x.id === etkin)
    const sec = kesifte && secili !== null ? tekYildiz(hazir.g, secili) : null
    return {
      maske: sec ?? (b?.maske ? maske(b.maske) : null),
      yilAnim: b?.yilAnim ?? false,
      cizgiler: b?.cizgiler ?? false,
      uzaklik: b?.uzaklik ?? (etkin === 'son' ? 30 : 26),
      kesif: kesifte,
      ucus: sec?.merkez ?? null,
      etiketler: sec ? [{ konum: sec.merkez, ad: secAd ?? '', tur: 'secim' }] : kesifte ? [] : (b?.etiketler ?? []),
    }
  }, [hazir, maske, liste, etkin, kesifte, secili, secAd])

  const sec = useCallback((i: number | null) => setSecili(i), [])

  return (
    <QualityProvider>
      <div className="sahne-kap" data-kesif={kesifte}>
        {hazir && sahne && <Sahne g={hazir.g} ciftler={hazir.ciftler} durum={sahne} hareketAzalt={hareketAzalt} onIsaret={isaretAyarla} onSec={sec} />}
      </div>
      <header className="ust">
        <a href="#giris" className="marka">Steam Galaksisi</a>
        <a href="#kesif">Haritayı keşfet</a>
      </header>
      <main data-kesif={kesifte}>
        <section id="giris" className="giris" data-bolum="giris">
          {hazir && <Baslik oz={hazir.oz} />}
          {d.durum === 'yukleniyor' && <p className="durum">Plaka banyo ediliyor: 92 bin oyunun konumu yükleniyor…</p>}
          {d.durum === 'hata' && <p className="durum hata" role="alert">{d.mesaj} Sayfayı yenileyin; sorun sürerse veri dosyaları eksik olabilir (scripts/14_web_veri.py).</p>}
          {hazir && (
            <>
              <p className="giris-metin">
                Her nokta 2018–2025 arasında Steam'de çıkmış bir oyun: {sayi(hazir.g.n)} tane. Benzer etiketlere sahip oyunlar birbirine yakın duruyor. Bir yıldızın
                parlaklığı, oyunun ilk yılında aldığı inceleme sayısı.
              </p>
              <Anahtar />
              <a className="asagi" href={`#${liste[0]?.id ?? 'kesif'}`}>Neden çoğu sönük kalıyor?</a>
            </>
          )}
        </section>
        {hazir && <Anlati liste={liste} etkin={etkin} />}
        {hazir && (
          <section id="kesif" className="kesif" data-bolum="kesif">
            <div className="metin">
              <h2>Kendi yıldızını bul.</h2>
              <p>Haritayı sürükleyip döndürün, tekerlekle yakınlaşın. Bir yıldızın üzerine gelince adı görünür, tıklayınca künyesi açılır.</p>
              <Kesif g={hazir.g} ad={ad} secili={secili} onSec={sec} />
            </div>
          </section>
        )}
        {hazir && <Son oz={hazir.oz} />}
      </main>
      {hazir && <Dizin liste={[...liste, { id: 'kesif', kisa: 'Keşfet' }]} etkin={etkin} />}
      <Ipucu adlar={ad.durum === 'hazir' ? ad.adlar : null} />
    </QualityProvider>
  )
}

function Baslik({ oz }: { oz: Ozet }) {
  const yillar = Object.keys(oz.arz)
  const son = yillar[yillar.length - 1]!
  return (
    <h1>
      <span className="ince">
        {ekDe(son)} Steam'e {sayi(Math.round(oz.arz[son]! / 1000))} bin oyun düştü.
      </span>
      <span className="kalin">{oz.gorunmez_yuzde > 50 ? 'Çoğunu kimse görmedi.' : 'Neredeyse yarısını kimse görmedi.'}</span>
    </h1>
  )
}
