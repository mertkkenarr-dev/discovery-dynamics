/**
 * Anlatı bölümleri. Başlıklar bulguyu söyler ve veriden üretilir: bir sayı değişirse cümle de değişir,
 * yön tersine dönerse başlık "tutmadı" der (önceden yazılmış iddia yok). Kaynak: ozet.json ← analysis/sonuclar.
 */
import type { ReactNode } from 'react'
import type { MaskeAdi } from './galaksi/maske'
import { arzGrafik, fiyatGrafik, hitYilGrafik, ilkAyGrafik, yapayZekaGrafik } from './grafikler'
import type { Colors } from './site/charts'
import { ekDe, ekI } from './lib/ek'
import { sayi, yuzde, type Ozet } from './veri'

export interface Grafik {
  kur: (o: { width: number; colors: Colors }) => SVGSVGElement | HTMLElement
  etiket: string
  baslik: string
  yukseklik: number
}

export interface Bolum {
  id: string
  kisa: string
  baslik: string
  govde: ReactNode
  maske: MaskeAdi | null
  yilAnim?: boolean
  cizgiler?: boolean
  uzaklik: number
  grafikler?: Grafik[]
  modul: string
}

const kat = (v: number) => sayi(v, 1)

export function bolumler(oz: Ozet): Bolum[] {
  const yillar = Object.keys(oz.arz)
  const arzIlk = oz.arz[yillar[0]!]!
  const arzSon = oz.arz[yillar[yillar.length - 1]!]!
  const hitler = Object.values(oz.hit_yil)
  const hitMin = Math.min(...hitler)
  const hitMax = Math.max(...hitler)
  const fiyatlar = Object.entries(oz.fiyat_hit)
  const [fIlk, fSon] = [fiyatlar[0]!, fiyatlar[fiyatlar.length - 1]!]
  const yuz = Math.round(oz.gorunmez_yuzde)
  const azalan = oz.yenilik.egim_alt_t < 0 && oz.yenilik.egim_ust_t < 0
  const etiket = oz.etiket_en_olumlu.filter(([e]) => /co-op|multiplayer/i.test(e)).map(([, v]) => v)
  const uzun = oz.yorunge['Uzun soluklu']!
  const patla = oz.yorunge['Patlayıp sönen']!
  const carpanlar = Object.values(oz.ilk_ay.carpan).filter((v): v is number => v !== null)
  const yz = oz.yapay_zeka.gorunmez
  const yzVar = (yz['1']?.gorunmez ?? 0) * 100
  const yzYok = (yz['0']?.gorunmez ?? 0) * 100
  const io = oz.ikinci_oyun

  return [
    {
      id: 'gorunmez', kisa: 'Görünmezlik', modul: 'M1', maske: 'gorunmez', uzaklik: 23,
      baslik: `Her 100 bağımsız oyundan ${yuz} tanesi ilk yılında 10 inceleme bile alamıyor.`,
      govde: <>
        <p>Öne çıkan soğuk toz bu oyunlar. 10 inceleme kabaca birkaç yüz satış demek: oyun çıktı, ama neredeyse kimse fark etmedi.</p>
        <p>Geri kalan yıldızlar şimdilik karartıldı. Görünür olanlar, yani ilk yılında 500'den fazla inceleme toplayan oyunlar, örneklemin yalnız {ekI(yuzde(oz.hit_yuzde, 1))}.</p>
      </>,
    },
    {
      id: 'arz', kisa: 'Kalabalık', modul: 'M1', maske: null, yilAnim: true, uzaklik: 25,
      baslik: hitMax - hitMin < 2
        ? `Steam'e her yıl çıkan oyun ${kat(arzSon / arzIlk)} katına çıktı. Öne çıkma şansı yerinde sayıyor.`
        : `Steam'e her yıl çıkan oyun ${kat(arzSon / arzIlk)} katına çıktı ve öne çıkma şansı değişti.`,
      govde: <>
        <p>Yıldızlar çıkış yılına göre sırayla yanıyor: {ekDe(yillar[0]!)} {sayi(arzIlk)}, {ekDe(yillar[yillar.length - 1]!)} {sayi(arzSon)} oyun.</p>
        <p>"Steam artık çok kalabalık" algısı veride görünmüyor. Bağımsız oyunların hit oranı her yıl %{sayi(hitMin, 1)} ile %{sayi(hitMax, 1)} arasında kaldı. Kalabalık büyüdükçe öne çıkan oyun sayısı da büyüyor.</p>
      </>,
      grafikler: [
        { kur: arzGrafik(oz), etiket: 'Yıllara göre Steam’e çıkan oyun sayısı', baslik: 'Steam’e yılda çıkan oyun (tümü)', yukseklik: 180 },
        { kur: hitYilGrafik(oz), etiket: 'Yıllara göre bağımsız oyunların hit oranı', baslik: 'Hit olan bağımsız oyun payı', yukseklik: 150 },
      ],
    },
    {
      id: 'fiyat', kisa: 'Fiyat', modul: 'K1', maske: 'pahali', uzaklik: 20,
      baslik: fSon[1] > fIlk[1]
        ? `Ucuz oyun daha çok ilgi görmüyor: ${sayi(+fIlk[0], 2)} dolarda hit oranı %${sayi(fIlk[1], 1)}, ${sayi(+fSon[0], 2)} dolarda %${sayi(fSon[1], 0)}.`
        : `Fiyat yükseldikçe hit oranı düşüyor.`,
      govde: <>
        <p>Öne çıkanlar 20 doların üstündeki oyunlar. Haritanın her köşesine dağılmış durumdalar: pahalı oyun tek bir türe ait değil.</p>
        <p>Bunu "fiyatını artır" diye okumamak gerekiyor. 30 dolarlık bağımsız oyun genelde daha büyük bir proje; fiyat büyük ihtimalle kapsamı ve bütçeyi yansıtıyor.</p>
      </>,
      grafikler: [{ kur: fiyatGrafik(oz), etiket: 'Fiyata göre hit oranı', baslik: 'Fiyata göre hit oranı', yukseklik: 220 }],
    },
    {
      id: 'tanidik', kisa: 'Yenilik', modul: 'M3 (H1)', maske: 'tanidik', uzaklik: 18,
      baslik: azalan ? 'Tanıdık kazanıyor.' : 'Yenilik ile başarı arasında net bir yön yok.',
      govde: <>
        <p>Haritada yakın duran yıldızlar benzer etiket kombinasyonuna sahip. Öne çıkanlar, kombinasyonu en alışıldık dörtte birlik dilim: kalabalık merkezler.</p>
        <p>Çalışmaya başlamadan önce kaydettiğimiz hipotez "orta düzeyde yenilik en iyisi" idi. Tutmadı. {azalan ? 'Kombinasyon ne kadar alışılmadıksa beklenen inceleme o kadar az; tatlı bir orta nokta yok.' : ''}</p>
      </>,
    },
    {
      id: 'birlikte', kisa: 'Birlikte', modul: 'M2', maske: 'birlikte', uzaklik: 19,
      baslik: `Birlikte oynanan oyunlar öne çıkıyor.`,
      govde: <>
        <p>Öne çıkanlar Multiplayer, Co-op ya da Online Co-op etiketi taşıyan oyunlar. Tür ve fiyat sabitken hit olma olasılıkları (odds) ×{kat(Math.min(...etiket))}–{kat(Math.max(...etiket))}. Test edilen mekanik, görsel ve oyuncu yapısı etiketleri içinde en güçlü olumlu ilişki bunlarda.</p>
        <p>Dikkat: arkadaşlarla oynanan oyunlar oyuncu başına daha çok inceleme alıyor olabilir ve etiketleri oyuncular oyluyor. Bu bir ilişki, tarif değil.</p>
      </>,
    },
    {
      id: 'ea', kisa: 'Uzun soluk', modul: 'M4 (H4)', maske: 'ea', uzaklik: 20,
      baslik: `İlgisi zamana yayılan oyunların hit oranı, patlayıp sönenlerin ${kat(uzun.hit / patla.hit)} katı.`,
      govde: <>
        <p>Öne çıkanlar Erken Erişim (Early Access) ile başlayan oyunlar. Ön kayıtlı hipotez tuttu: bu oyunların ilgisi zamana daha çok yayılıyor (odds ×{sayi(oz.ea_kuyruk.or, 2)}).</p>
        <p>İlgisi ikinci yıla da taşan oyunlarda hit oranı %{sayi(uzun.hit, 0)}; ilk aylarda patlayıp sönenlerde %{sayi(patla.hit, 0)}.</p>
      </>,
    },
    {
      id: 'cince', kisa: 'Çince', modul: 'M2 (H6)', maske: 'cince', uzaklik: 20,
      baslik: `Basitleştirilmiş Çince destekleyen oyunlar daha başarılı, ama ilişkinin bir kısmı ters yönde.`,
      govde: <>
        <p>Öne çıkanlar Çince destekli oyunlar. Ön kayıtlı hipotez tuttu: diğer her şey eşitken inceleme sayısı +%{sayi(oz.cince.ana, 0)}, en temkinli hesapla +%{sayi(oz.cince.temkinli, 0)}.</p>
        <p>Ama sekiz ayda en başarılı oyunlar Çince'yi en alttakilerden {sayi(oz.cince.ekleme_T4 / oz.cince.ekleme_T0, 0)} kat daha sık ekledi. Yani bazen başarı dili getiriyor, dil başarıyı değil.</p>
      </>,
    },
    {
      id: 'ilkay', kisa: 'İlk ay', modul: 'K3', maske: 'hit', uzaklik: 22,
      baslik: `Lansman ayı yılı belirliyor: tipik oyun yılını ilk ayının ${kat(carpanlar[Math.floor(carpanlar.length / 2)]!)} katıyla kapatıyor.`,
      govde: <>
        <p>Öne çıkanlar hit olan oyunlar. Bu oyunların kaderi büyük ölçüde ilk 30 günde belli oluyor: ilk ay ile ilk yıl arasındaki sıra korelasyonu {sayi(oz.ilk_ay.rho, 2)}.</p>
        <p>İlk ayında 200–499 inceleme toplayan oyunların {ekI(yuzde(oz.ilk_ay.hit['200–499'] ?? 0))} yılı hit olarak bitiriyor.</p>
      </>,
      grafikler: [{ kur: ilkAyGrafik(oz), etiket: 'İlk ay inceleme bandına göre yılı hit bitirme oranı', baslik: 'Yılı hit bitirenlerin payı', yukseklik: 220 }],
    },
    {
      id: 'ikinci', kisa: 'İkinci oyun', modul: 'M6 (H5)', maske: 'hicbiri', cizgiler: true, uzaklik: 23,
      baslik: io.iyilesen < 0.5 ? 'İkinci oyun ilkinden iyi değil.' : 'İkinci oyun genelde ilkinden iyi.',
      govde: <>
        <p>Her çizgi bir stüdyonun ilk oyunundan ikincisine uzanıyor; yalnız iki oyunu arasında en az üç kat fark olanlar çizili. Turuncu çizgilerde ikinci oyun daha çok inceleme aldı, mavi çizgilerde daha az.</p>
        <p>{sayi(io.n)} stüdyonun yalnız {ekI(yuzde(io.iyilesen * 100))}nde ikinci oyun daha çok ilgi gördü. İlk oyunu görünmez kalanların {ekI(yuzde(io.T0_kalan))} ikincide de görünmez kaldı.</p>
      </>,
    },
    {
      id: 'yz', kisa: 'Yapay zekâ', modul: 'K2', maske: 'yapayZeka', uzaklik: 20,
      baslik: `Yapay zekâ kullandığını beyan eden oyunların ${ekI(yuzde(yzVar))} görünmez kalıyor. Beyan etmeyenlerde ${yuzde(yzYok)}.`,
      govde: <>
        <p>Steam Ocak 2024'ten beri yapay zekâ kullanımının beyan edilmesini istiyor. 2025'te çıkan oyunların {ekI(yuzde(oz.yapay_zeka.pay_yil['2025'] ?? 0, 1))} beyanlı.</p>
        <p>Bu bir neden-sonuç değil: beyan büyük ihtimalle düşük bütçeli, hızlı üretilmiş projelerle birlikte görülüyor. Oyuncuların beyana tepki vermesi de mümkün; bu veri ikisini ayıramıyor.</p>
      </>,
      grafikler: [{ kur: yapayZekaGrafik(oz), etiket: 'Yapay zekâ beyanına göre görünmez kalan oyun payı, 2024–2025', baslik: 'Görünmez kalan oyunların payı (2024–2025 çıkışlı bağımsız oyunlar)', yukseklik: 120 }],
    },
  ]
}
