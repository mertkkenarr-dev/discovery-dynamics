/**
 * Sayfa iskeleti. Veri durumu ayrık birleşimle tutulur (yükleniyor / hata / hazır); Canvas veri hazır olmadan kurulmaz.
 * Sahneye giden durum yalnız etkin bölüm ya da seçim değişince yeniden hesaplanır.
 */
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Anlati, Dizin, useEtkinBolum } from './Anlati'
import { arayuz } from './arayuz'
import { bolumler } from './bolumler'
import { bolumlerEn } from './bolumler_en'
import { DilBaglam, dilKaydet, ilkDil, type Dil } from './dil'
import { Giris } from './Giris'
import { bitMaske, maskeUretici, tekYildiz } from './galaksi/maske'
import { Sahne, type SahneDurumu } from './galaksi/Sahne'
import { Ipucu, isaretAyarla, Kesif, useAdlar } from './Kesif'
import { QualityProvider } from './kit/quality'
import { Son } from './Son'
import { TurPanel } from './TurPanel'
import { galaksiYukle, jsonYukle, turlerYukle, type Cift, type Galaksi, type Ozet } from './veri'

type Durum = { durum: 'yukleniyor' } | { durum: 'hata'; mesaj: string } | { durum: 'hazir'; g: Galaksi; oz: Ozet; ciftler: Cift[]; bitler: Uint8Array[] }

const hareketAzalt = window.matchMedia('(prefers-reduced-motion: reduce)').matches

export function App() {
  const [d, setD] = useState<Durum>({ durum: 'yukleniyor' })
  const [etkin, setEtkin] = useState('giris')
  const [secili, setSecili] = useState<number | null>(null)
  const [tur, setTur] = useState(0)
  const [dil, setDil] = useState<Dil>(ilkDil)
  const m = arayuz(dil)
  useEffect(() => {
    dilKaydet(dil)
    document.title = m.marka
  }, [dil, m.marka])

  useEffect(() => {
    galaksiYukle()
      .then((g) => Promise.all([g, jsonYukle<Ozet>('ozet.json'), jsonYukle<Cift[]>('ikinci.json'), turlerYukle(g.n)]))
      .then(([g, oz, ciftler, bitler]) => setD({ durum: 'hazir', g, oz, ciftler, bitler }))
      .catch((e: unknown) => setD({ durum: 'hata', mesaj: e instanceof Error ? e.message : 'Veri yüklenemedi.' }))
  }, [])

  const hazir = d.durum === 'hazir' ? d : null
  const liste = useMemo(() => (hazir ? (dil === 'tr' ? bolumler : bolumlerEn)(hazir.oz, hazir.g, hazir.bitler) : []), [hazir, dil])
  const maske = useMemo(() => (hazir ? maskeUretici(hazir.g, hazir.oz.k5.dalgalar.slice(0, 2).flatMap((d) => d.takipci)) : null), [hazir])
  const kesifte = etkin === 'kesif'
  const ad = useAdlar(kesifte || secili !== null)
  const secAd = secili !== null && ad.durum === 'hazir' ? ad.adlar[secili]?.[1] : undefined

  useEtkinBolum(useCallback((id: string) => setEtkin(id), []), hazir !== null)

  const sahne = useMemo<SahneDurumu | null>(() => {
    if (!hazir || !maske) return null
    const b = liste.find((x) => x.id === etkin)
    const sec = kesifte && secili !== null ? tekYildiz(hazir.g, secili) : null
    const turMaske = etkin === 'turpanel' ? bitMaske(hazir.g, [hazir.bitler[tur]!]) : null
    return {
      maske: sec ?? turMaske ?? b?.maskeOzel ?? (b?.maske ? maske(b.maske) : null),
      yilAnim: b?.yilAnim ?? false,
      cizgiler: b?.cizgiler ?? false,
      uzaklik: b?.uzaklik ?? (etkin === 'son' ? 30 : etkin === 'turpanel' ? 19 : etkin === 'giris' ? 30 : 26),
      kesif: kesifte,
      ucus: sec?.merkez ?? null,
      etiketler: sec ? [{ konum: sec.merkez, ad: secAd ?? '', tur: 'secim' }] : kesifte ? [] : (b?.etiketler ?? []),
    }
  }, [hazir, maske, liste, etkin, kesifte, secili, secAd, tur])

  const sec = useCallback((i: number | null) => setSecili(i), [])

  return (
    <DilBaglam.Provider value={dil}>
    <QualityProvider>
      <div className="sahne-kap" data-kesif={kesifte}>
        {hazir && sahne && <Sahne g={hazir.g} ciftler={hazir.ciftler} durum={sahne} hareketAzalt={hareketAzalt} onIsaret={isaretAyarla} onSec={sec} />}
      </div>
      <header className="ust">
        <a href="#giris" className="marka">{m.marka}</a>
        <nav className="ust-baglanti" aria-label={m.sayfa}>
          <a href={`#${liste[0]?.id ?? 'kesif'}`}>{m.bulgular}</a>
          <a href="#son">{m.yontem}</a>
          <a href="#kesif">{m.kesfet}</a>
          <button type="button" className="dil-dugme" onClick={() => setDil(dil === 'tr' ? 'en' : 'tr')} aria-label={m.dilEtiket} lang={dil === 'tr' ? 'en' : 'tr'}>
            {m.dilDugme}
          </button>
        </nav>
      </header>
      <main data-kesif={kesifte}>
        <Giris d={d} ilkBolum={liste[0]?.id ?? 'kesif'} />
        {hazir && <Anlati liste={liste} etkin={etkin} hipotezler={hazir.oz.hipotez} />}
        {hazir && (
          <section id="turpanel" className="adim tur-bolum" data-bolum="turpanel" data-etkin={etkin === 'turpanel'}>
            <div className="metin">
              <p className="katalog">{m.etkilesimli}</p>
              <h2>{m.turBaslik}</h2>
              <p>{m.turAciklama}</p>
              <TurPanel oz={hazir.oz} secili={tur} onSec={setTur} />
            </div>
          </section>
        )}
        {hazir && (
          <section id="kesif" className="kesif" data-bolum="kesif">
            <div className="metin">
              <h2>{m.kesifBaslik}</h2>
              <p>{m.kesifAciklama}</p>
              <Kesif g={hazir.g} ad={ad} secili={secili} onSec={sec} />
            </div>
          </section>
        )}
        {hazir && <Son oz={hazir.oz} />}
      </main>
      {hazir && <Dizin liste={[...liste, { id: 'turpanel', kisa: m.turPaneli }, { id: 'kesif', kisa: m.kesfetKisa }]} etkin={etkin} />}
      <Ipucu adlar={ad.durum === 'hazir' ? ad.adlar : null} />
    </QualityProvider>
    </DilBaglam.Provider>
  )
}

