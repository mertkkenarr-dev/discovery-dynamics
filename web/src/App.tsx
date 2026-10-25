/**
 * Sayfa iskeleti. Veri durumu ayrık birleşimle tutulur (yükleniyor / hata / hazır); Canvas veri hazır olmadan kurulmaz.
 * Sahneye giden durum yalnız etkin bölüm ya da seçim değişince yeniden hesaplanır.
 */
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Anahtar, Anlati, Dizin, useEtkinBolum } from './Anlati'
import { bolumler } from './bolumler'
import { bitMaske, maskeUretici, tekYildiz } from './galaksi/maske'
import { Sahne, type SahneDurumu } from './galaksi/Sahne'
import { Ipucu, isaretAyarla, Kesif, useAdlar } from './Kesif'
import { QualityProvider } from './kit/quality'
import { Son } from './Son'
import { TurPanel } from './TurPanel'
import { galaksiYukle, jsonYukle, turlerYukle, sayi, type Cift, type Galaksi, type Ozet } from './veri'

type Durum = { durum: 'yukleniyor' } | { durum: 'hata'; mesaj: string } | { durum: 'hazir'; g: Galaksi; oz: Ozet; ciftler: Cift[]; bitler: Uint8Array[] }

const hareketAzalt = window.matchMedia('(prefers-reduced-motion: reduce)').matches

export function App() {
  const [d, setD] = useState<Durum>({ durum: 'yukleniyor' })
  const [etkin, setEtkin] = useState('giris')
  const [secili, setSecili] = useState<number | null>(null)
  const [tur, setTur] = useState(0)

  useEffect(() => {
    galaksiYukle()
      .then((g) => Promise.all([g, jsonYukle<Ozet>('ozet.json'), jsonYukle<Cift[]>('ikinci.json'), turlerYukle(g.n)]))
      .then(([g, oz, ciftler, bitler]) => setD({ durum: 'hazir', g, oz, ciftler, bitler }))
      .catch((e: unknown) => setD({ durum: 'hata', mesaj: e instanceof Error ? e.message : 'Veri yüklenemedi.' }))
  }, [])

  const hazir = d.durum === 'hazir' ? d : null
  const liste = useMemo(() => (hazir ? bolumler(hazir.oz, hazir.g, hazir.bitler) : []), [hazir])
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
    <QualityProvider>
      <div className="sahne-kap" data-kesif={kesifte}>
        {hazir && sahne && <Sahne g={hazir.g} ciftler={hazir.ciftler} durum={sahne} hareketAzalt={hareketAzalt} onIsaret={isaretAyarla} onSec={sec} />}
      </div>
      <header className="ust">
        <a href="#giris" className="marka">Steam Galaksisi</a>
        <nav className="ust-baglanti" aria-label="Sayfa">
          <a href={`#${liste[0]?.id ?? 'kesif'}`}>Bulgular</a>
          <a href="#son">Yöntem</a>
          <a href="#kesif">Haritayı keşfet</a>
        </nav>
      </header>
      <main data-kesif={kesifte}>
        <section id="giris" className="giris" data-bolum="giris">
          {hazir && <Baslik oz={hazir.oz} />}
          {d.durum === 'yukleniyor' && <p className="durum">Plaka banyo ediliyor: 92 bin oyunun konumu yükleniyor…</p>}
          {d.durum === 'hata' && <p className="durum hata" role="alert">{d.mesaj} Sayfayı yenileyin; sorun sürerse veri dosyaları eksik olabilir (scripts/14_web_veri.py).</p>}
          {hazir && (
            <>
              <p className="giris-metin">
                Discovery Dynamics, Steam'de bağımsız bir oyunu görünür kılan şeyin ne olduğunu araştıran bir veri analizi projesi. 2018–2025 arasında çıkan{' '}
                {sayi(hazir.g.n)} oyun, içerik benzerliğine göre bu haritaya yerleştirildi: yakın yıldızlar benzer oyunlar, parlaklık ilk yılın inceleme sayısı.
              </p>
              <dl className="kunye-proje">
                <div>
                  <dt>Veri</dt>
                  <dd>{sayi(hazir.oz.yildiz)} oyun; {sayi(Math.floor(hazir.oz.k8.gozlem / 1e6))} milyonu aşkın aylık inceleme kaydı</dd>
                </div>
                <div>
                  <dt>Yaklaşım</dt>
                  <dd>{Object.keys(hazir.oz.hipotez).length} ön kayıtlı hipotez testi, nedensel çıkarım, makine öğrenmesi ve metin analizi</dd>
                </div>
              </dl>
              <Anahtar />
              <a className="asagi" href={`#${liste[0]?.id ?? 'kesif'}`}>Bulgulara geç</a>
            </>
          )}
        </section>
        {hazir && <Anlati liste={liste} etkin={etkin} hipotezler={hazir.oz.hipotez} />}
        {hazir && (
          <section id="turpanel" className="adim tur-bolum" data-bolum="turpanel" data-etkin={etkin === 'turpanel'}>
            <div className="metin">
              <p className="katalog">Etkileşimli</p>
              <h2>Bir türü incele.</h2>
              <p>Bir alt tür seçin: oyunları haritada yanar, karnesi açılır. Değerler 2021–2025 arasında çıkan bağımsız oyunlardan.</p>
              <TurPanel oz={hazir.oz} secili={tur} onSec={setTur} />
            </div>
          </section>
        )}
        {hazir && (
          <section id="kesif" className="kesif" data-bolum="kesif">
            <div className="metin">
              <h2>Bir oyunu haritada bul.</h2>
              <p>Haritayı sürükleyerek döndürün, tekerlekle yakınlaşın. Bir yıldızın üzerine gelince oyunun adı görünür; tıklayınca künyesi açılır.</p>
              <Kesif g={hazir.g} ad={ad} secili={secili} onSec={sec} />
            </div>
          </section>
        )}
        {hazir && <Son oz={hazir.oz} />}
      </main>
      {hazir && <Dizin liste={[...liste, { id: 'turpanel', kisa: 'Tür paneli' }, { id: 'kesif', kisa: 'Keşfet' }]} etkin={etkin} />}
      <Ipucu adlar={ad.durum === 'hazir' ? ad.adlar : null} />
    </QualityProvider>
  )
}

function Baslik({ oz }: { oz: Ozet }) {
  return (
    <h1>
      <span className="ince">Bu gökyüzündeki her yıldız bir Steam oyunu.</span>
      <span className="kalin">{oz.gorunmez_yuzde > 50 ? 'Çoğu hiç parlamadı.' : 'Neredeyse yarısı hiç parlamadı.'}</span>
    </h1>
  )
}
