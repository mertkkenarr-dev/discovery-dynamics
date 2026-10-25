/**
 * Anlatı bölümleri. Her bölüm: bulguyu söyleyen başlık + açıklama + haritada ne vurgulandığı + yöntem notu.
 * Başlıklar ve sayılar veriden üretilir (ozet.json ← analysis/sonuclar); yön tersine dönerse cümle de döner.
 * Ön kayıtlı hipotezlerin sonucu (desteklendi / desteklenmedi) hipotez_ozeti.json'dan gelir, burada yazılmaz.
 */
import type { ReactNode } from 'react'
import { esikBolum, firsatBolum, gizliBolum, klonBolum, metinBolum } from './bolumler_ek'
import type { Etiket } from './galaksi/Etiketler'
import type { MaskeAdi } from './galaksi/maske'
import { arzGrafik, fiyatGrafik, hitYilGrafik, ilkAyGrafik, yapayZekaGrafik } from './grafikler'
import type { Colors } from './site/charts'
import { ekDe, ekI } from './lib/ek'
import { sayi, yuzde, type Galaksi, type Ozet } from './veri'

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
  harita: string
  yontem: string
  hipotez?: string
  maske: MaskeAdi | null
  yilAnim?: boolean
  cizgiler?: boolean
  uzaklik: number
  grafikler?: Grafik[]
  etiketler?: Etiket[]
}

const kat = (v: number) => sayi(v, 1)

export function bolumler(oz: Ozet, g: Galaksi): Bolum[] {
  const b = temel(oz)
  const sira = (id: string) => b.find((x) => x.id === id)!
  return [sira('gorunmez'), gizliBolum(oz), sira('arz'), sira('fiyat'), sira('tanidik'), klonBolum(oz, g), firsatBolum(oz), sira('birlikte'), sira('ea'),
    sira('cince'), sira('ilkay'), esikBolum(oz), metinBolum(oz), sira('ikinci'), sira('yz')]  // fmt: skip
}

function temel(oz: Ozet): Bolum[] {
  const yillar = Object.keys(oz.arz)
  const [y0, y1] = [yillar[0]!, yillar[yillar.length - 1]!]
  const [arzIlk, arzSon] = [oz.arz[y0]!, oz.arz[y1]!]
  const hitler = Object.values(oz.hit_yil)
  const [hitMin, hitMax] = [Math.min(...hitler), Math.max(...hitler)]
  const fiyatlar = Object.entries(oz.fiyat_hit)
  const [fIlk, fSon] = [fiyatlar[0]!, fiyatlar[fiyatlar.length - 1]!]
  const azalan = oz.yenilik.egim_alt_t < 0 && oz.yenilik.egim_ust_t < 0
  const etiket = oz.etiket_en_olumlu.filter(([e]) => /co-op|multiplayer/i.test(e)).map(([, v]) => v)
  const uzun = oz.yorunge['Uzun soluklu']!
  const patla = oz.yorunge['Patlayıp sönen']!
  const carpanlar = Object.values(oz.ilk_ay.carpan).filter((v): v is number => v !== null)
  const yz = oz.yapay_zeka.gorunmez
  const [yzVar, yzYok] = [(yz['1']?.gorunmez ?? 0) * 100, (yz['0']?.gorunmez ?? 0) * 100]
  const io = oz.ikinci_oyun

  return [
    {
      id: 'gorunmez', kisa: 'Görünmezlik', maske: 'gorunmez', uzaklik: 23,
      baslik: `Her 100 bağımsız oyundan ${Math.round(oz.gorunmez_yuzde)} tanesi ilk yılında 10 inceleme bile alamıyor.`,
      govde: <>
        <p>Steam satış rakamı yayınlamıyor. Bu yüzden başarıyı, oyunun ilk 365 gününde aldığı kullanıcı incelemesiyle ölçtük; inceleme sayısı satış sıralamasıyla güçlü biçimde ilişkili. 10 inceleme kabaca birkaç yüz satış demek.</p>
        <p>Ölçeğin öbür ucunda, ilk yılında 500'ü aşan ve bu çalışmada "hit" sayılan oyunların payı yalnız {yuzde(oz.hit_yuzde, 1)}.</p>
      </>,
      harita: 'İlk yılında 10’dan az inceleme alan oyunlar; diğerleri karartıldı.',
      yontem: `2018–2025 arasında çıkan, büyük yayıncı desteği olmayan ${sayi(oz.orneklem)} oyun. Başarı ölçüsü: Steam inceleme grafiğinden ilk 365 günün inceleme sayısı.`,
    },
    {
      id: 'arz', kisa: 'Kalabalık', maske: null, yilAnim: true, uzaklik: 25,
      baslik: hitMax - hitMin < 2
        ? `Steam'e her yıl çıkan oyun ${kat(arzSon / arzIlk)} katına çıktı. Öne çıkma şansı ise yerinde sayıyor.`
        : `Steam'e her yıl çıkan oyun ${kat(arzSon / arzIlk)} katına çıktı ve öne çıkma şansı değişti.`,
      govde: <>
        <p>Yıllık çıkış {ekDe(y0)} {sayi(arzIlk)}, {ekDe(y1)} {sayi(arzSon)} oldu. Buna karşın bağımsız oyunların hit oranı her yıl %{sayi(hitMin, 1)} ile %{sayi(hitMax, 1)} arasında kaldı.</p>
        <p>"Steam artık fazla kalabalık" algısı veride karşılık bulmuyor: rekabet büyüyor, ama görünür olanların payı sabit; mutlak sayıda her yıl daha çok oyun öne çıkıyor.</p>
      </>,
      harita: 'Oyunlar çıkış yılına göre sırayla beliriyor.',
      yontem: 'Arz: Steam’e çıkan tüm oyunlar. Hit oranı: bağımsız örneklem, çıkış yılına göre.',
      grafikler: [
        { kur: arzGrafik(oz), etiket: 'Yıllara göre Steam’e çıkan oyun sayısı', baslik: 'Steam’e yılda çıkan oyun (tümü)', yukseklik: 180 },
        { kur: hitYilGrafik(oz), etiket: 'Yıllara göre bağımsız oyunların hit oranı', baslik: 'Hit olan bağımsız oyun payı', yukseklik: 150 },
      ],
    },
    {
      id: 'fiyat', kisa: 'Fiyat', maske: 'pahali', uzaklik: 20,
      baslik: fSon[1] > fIlk[1]
        ? `Ucuz oyun daha çok ilgi görmüyor: ${sayi(+fIlk[0], 2)} dolarda hit oranı %${sayi(fIlk[1], 1)}, ${sayi(+fSon[0], 2)} dolarda %${sayi(fSon[1], 0)}.`
        : 'Fiyat yükseldikçe hit oranı düşüyor.',
      govde: <>
        <p>Hit oranı fiyatla birlikte düzenli biçimde artıyor. Bu bir fiyatlama tavsiyesi değil: 30 dolarlık bağımsız oyun çoğunlukla daha büyük bir ekip, bütçe ve kapsam demek. Fiyat, büyük olasılıkla bunların göstergesi.</p>
      </>,
      harita: 'Liste fiyatı 20 doların üstündeki oyunlar; haritanın her bölgesine dağılmış durumdalar.',
      yontem: 'Liste fiyatına göre ham hit oranları. Tür ve yıl kontrollü modellerde de fiyat en güçlü değişken.',
      grafikler: [{ kur: fiyatGrafik(oz), etiket: 'Fiyata göre hit oranı', baslik: 'Fiyata göre hit oranı', yukseklik: 220 }],
    },
    {
      id: 'tanidik', kisa: 'Yenilik', hipotez: 'H1', maske: 'tanidik', uzaklik: 18,
      baslik: azalan ? 'Tanıdık kazanıyor: alışılmadık oyunlar daha az ilgi görüyor.' : 'Yenilik ile başarı arasında net bir yön yok.',
      govde: <>
        <p>Çalışmanın başında "orta düzeyde yenilik en iyisi" (ters U) hipotezini kaydettik. Veri bunu desteklemedi.{azalan && ' Etiket kombinasyonu, türünün yerleşik örneklerinden ne kadar uzaksa beklenen ilgi o kadar az; tatlı bir orta nokta görünmüyor.'}</p>
      </>,
      harita: 'Etiket kombinasyonu en alışıldık dörtte birlik dilim. Haritada yakın yıldızlar benzer içerik taşıyor.',
      yontem: 'Yenilik: içerik etiketlerinin, oyundan önce çıkan en yakın 10 oyuna kosinüs uzaklığı. Kontrollü regresyon ve Lind–Mehlum U testi.',
    },
    {
      id: 'birlikte', kisa: 'Birlikte', maske: 'birlikte', uzaklik: 19,
      baslik: 'Birlikte oynanan oyunlar öne çıkıyor.',
      govde: <>
        <p>Mekanik, görsel ve oyuncu yapısı etiketleri tek tek incelendiğinde en güçlü olumlu ilişki birlikte oynanan oyunlarda: Multiplayer, Online Co-op ve Co-op etiketlerinde hit olma olasılığı (odds) ×{kat(Math.min(...etiket))}–{kat(Math.max(...etiket))}.</p>
        <p>Çok oyunculu oyunlar oyuncu başına daha fazla inceleme topluyor olabilir; bulgu bir ilişki, tarif değil.</p>
      </>,
      harita: 'Multiplayer, Co-op ya da Online Co-op etiketli oyunlar.',
      yontem: 'Her etiket için yıl, tür, fiyat, Early Access ve dil kontrollü lojistik regresyon; Benjamini–Hochberg düzeltmesi. Keşifsel.',
    },
    {
      id: 'ea', kisa: 'Uzun soluk', hipotez: 'H4', maske: 'ea', uzaklik: 20,
      baslik: `İlgisi zamana yayılan oyunların hit oranı, patlayıp sönenlerin ${kat(uzun.hit / patla.hit)} katı.`,
      govde: <>
        <p>Early Access ile başlayan oyunların ilgisi zamana daha çok yayılıyor (odds ×{sayi(oz.ea_kuyruk.or, 2)}).</p>
        <p>Bu önemli, çünkü ilgisi ikinci yıla da taşan oyunlarda hit oranı %{sayi(uzun.hit, 0)}; ilk aylarda patlayıp sönenlerde %{sayi(patla.hit, 0)}.</p>
      </>,
      harita: 'Early Access ile çıkan oyunlar.',
      yontem: 'İkinci yıl inceleme payı. Kontrollü lojistik regresyon ve eğilim skoru eşleştirmesi (PSM); Holm düzeltmesi.',
    },
    {
      id: 'cince', kisa: 'Çince', hipotez: 'H6', maske: 'cince', uzaklik: 20,
      baslik: 'Basitleştirilmiş Çince destekleyen oyunlar daha başarılı; ama ilişkinin bir kısmı ters yönde.',
      govde: <>
        <p>Diğer her şey eşitken Çince destekli oyunlar +%{sayi(oz.cince.ana, 0)} daha fazla inceleme alıyor; en temkinli tahmin +%{sayi(oz.cince.temkinli, 0)}.</p>
        <p>Ancak sekiz aylık izlemede en başarılı oyunlar Çince desteğini en alttakilerden {sayi(oz.cince.ekleme_T4 / oz.cince.ekleme_T0, 0)} kat daha sık ekledi. Başarı bazen dili getiriyor, yalnız tersi değil.</p>
      </>,
      harita: 'Basitleştirilmiş Çince destekli oyunlar.',
      yontem: 'Log-doğrusal regresyon ve PSM. Ters nedensellik, Şubat ve Ekim 2026 dil listeleri karşılaştırılarak ölçüldü.',
    },
    {
      id: 'ilkay', kisa: 'İlk ay', maske: 'hit', uzaklik: 22,
      baslik: `Lansman ayı yılı belirliyor: tipik oyun yılını ilk ayının ${kat(carpanlar[Math.floor(carpanlar.length / 2)]!)} katıyla kapatıyor.`,
      govde: <>
        <p>İlk 30 günün inceleme sayısı ile ilk yılınki arasındaki sıra korelasyonu {sayi(oz.ilk_ay.rho, 2)}. İlk ayında 200–499 inceleme toplayan oyunların {ekI(yuzde(oz.ilk_ay.hit['200–499'] ?? 0))} yılı hit olarak kapatıyor.</p>
        <p>Çıkarım: görünürlük çoğunlukla lansmandan önce kazanılıyor; lansman sonrası toparlanma istisna.</p>
      </>,
      harita: 'İlk yılında hit olan oyunlar.',
      yontem: 'İlk 30 ve ilk 365 günün inceleme sayıları; Spearman sıra korelasyonu. Keşifsel.',
      grafikler: [{ kur: ilkAyGrafik(oz), etiket: 'İlk ay inceleme bandına göre yılı hit bitirme oranı', baslik: 'İlk ayın inceleme sayısına göre yılı hit bitirenler', yukseklik: 220 }],
    },
    {
      id: 'ikinci', kisa: 'İkinci oyun', hipotez: 'H5', maske: 'hicbiri', cizgiler: true, uzaklik: 23,
      baslik: io.iyilesen < 0.5 ? 'İkinci oyun ilkinden iyi değil.' : 'İkinci oyun genelde ilkinden iyi.',
      govde: <>
        <p>{sayi(io.n)} stüdyonun yalnız {ekI(yuzde(io.iyilesen * 100))}nde ikinci oyun daha çok inceleme aldı. İlk oyunu görünmez kalanların {ekI(yuzde(io.T0_kalan))} ikincide de görünmez kaldı: deneyim tek başına görünürlük getirmiyor.</p>
      </>,
      harita: 'Her çizgi bir stüdyonun ilk oyunundan ikincisine uzanıyor (aralarında en az üç kat fark olanlar). Turuncu: ikinci oyun daha başarılı; mavi: daha az.',
      yontem: 'Aynı stüdyonun ilk iki oyunu; eşleştirilmiş fark ve Wilcoxon işaretli sıra testi, Holm düzeltmesi.',
    },
    {
      id: 'yz', kisa: 'Yapay zekâ', maske: 'yapayZeka', uzaklik: 20,
      baslik: `Yapay zekâ kullandığını beyan eden oyunların ${ekI(yuzde(yzVar))} görünmez kalıyor; beyan etmeyenlerde bu oran ${yuzde(yzYok)}.`,
      govde: <>
        <p>Steam, Ocak 2024'ten beri geliştiricilerden yapay zekâ kullanımını beyan etmelerini istiyor; 2025'te çıkan oyunların {ekI(yuzde(oz.yapay_zeka.pay_yil['2025'] ?? 0, 1))} beyanlı.</p>
        <p>Bu bir neden-sonuç değil. Beyan büyük olasılıkla düşük bütçeli, hızlı üretilmiş projelerle birlikte görülüyor; oyuncuların beyana tepki vermesi de mümkün. Mevcut veri iki açıklamayı ayıramıyor.</p>
      </>,
      harita: 'Yapay zekâ kullanımını beyan eden oyunlar.',
      yontem: `2024–2025 çıkışlı bağımsız oyunlar; beyanlar IGDB anahtar kelimelerinden. Kontrollü lojistik regresyonda odds ×${sayi(oz.yapay_zeka.or, 1)}. Keşifsel.`,
      grafikler: [{ kur: yapayZekaGrafik(oz), etiket: 'Yapay zekâ beyanına göre görünmez kalan oyun payı, 2024–2025', baslik: 'Görünmez kalan oyunların payı (2024–2025)', yukseklik: 120 }],
    },
  ]
}
