/**
 * K5–K8 bölümleri (gizli hazineler, taklit, fırsat bölgeleri, 50 eşiği). bolumler.tsx ile aynı kural: başlıklar veriden üretilir,
 * yön tersine dönerse cümle de döner. Sayılar ozet.json'dan (analysis/sonuclar/K5–K8).
 */
import type { Bolum } from './bolumler'
import type { Etiket } from './galaksi/Etiketler'
import { esikGrafik, firsatGrafik, gizliGrafik, klonGrafik, metinGrafik } from './grafikler_ek'
import { ekI } from './lib/ek'
import { sayi, yuzde, type Galaksi, type Ozet } from './veri'

const konum = (g: Galaksi, i: number): [number, number, number] => [g.konum[i * 3]!, g.konum[i * 3 + 1]!, g.konum[i * 3 + 2]!]
const yz = (v: number, d = 1) => yuzde(v, d)
// K6 bölge adı analizde orta noktayla ayrılmış üç etiket olarak gelir; ekranda ilk ikisi virgülle gösterilir.
const AYRAC = ' \u00b7 '
const bolgeAdi = (ad: string, bag = ', ') => ad.split(AYRAC).slice(0, 2).join(bag)

function oncuEtiketleri(oz: Ozet, g: Galaksi): Etiket[] {
  // Öncüler çıkış sırasında; diger[k] adı oncu[k + 1]'e karşılık gelir (ikisi de aynı sıradan kesilir). Çok yakın düşen adlar atlanır.
  // Akım içinde daha çok inceleme alan (daha parlak) öncü önce yerleşir: üst üste binenlerden tanınanı kalsın.
  const aday = oz.k5.dalgalar.slice(0, 2).flatMap((d) =>
    [{ i: d.oncu[0]!, ad: d.ad }, ...d.diger.flatMap((ad, k) => (d.oncu[k + 1] === undefined ? [] : [{ i: d.oncu[k + 1]!, ad }]))]
      .sort((a, z) => g.parlaklik[z.i]! - g.parlaklik[a.i]!)
      .map((x) => ({ konum: konum(g, x.i), ad: x.ad })),
  )
  const secilen: Etiket[] = []
  for (const a of aday) {
    if (secilen.length >= 4) break
    if (secilen.some((e) => Math.hypot(e.konum[0] - a.konum[0], e.konum[1] - a.konum[1], e.konum[2] - a.konum[2]) < 0.12)) continue
    secilen.push({ ...a, tur: 'yildiz' })
  }
  return secilen
}

export function gizliBolum(oz: Ozet): Bolum {
  const k = oz.k7
  const onda = Math.round((k.n_gizli / k.cok_begenilen) * 10)
  const f = (ad: string) => k.farklar[ad]!
  const [sim, pt, demo] = [f('Tür: Simulation'), f('Playtest'), f('Çıkıştan önce demo')]
  return {
    id: 'gizli', kisa: 'Gizli hazineler', maske: 'gizli', uzaklik: 21,
    baslik: `Çok beğenilen her 10 oyundan ${onda} tanesi de görünmez kalıyor.`,
    govde: <>
      <p>Oyuncularının neredeyse tamamının beğendiği ama ilk yılında 100'den az inceleme alan {sayi(k.n_gizli)} oyun var. Görünmezlik yalnız kalitesiz oyunların sorunu değil.</p>
      <p>Bu gizli hazineleri, aynı beğeniye sahip görünür oyunlardan (500+ inceleme) ayıran çıkış öncesi özellikler: görünürler daha sık Simulation ({yz(sim.gizli * 100, 0)} yerine {yz(sim.gorunur * 100, 0)}) ve iki kat sık Playtest açmış ({yz(pt.gizli * 100, 0)} yerine {yz(pt.gorunur * 100, 0)}). Çıkış öncesi demo oranı ise iki grupta aynı: {yz(demo.gizli * 100, 0)}.</p>
    </>,
    harita: 'Gizli hazineler: ilk yılında 10–99 inceleme alan, çok beğenilen oyunlar.',
    yontem: 'Beğeni: olumlu inceleme oranının Wilson %95 alt sınırı ≥ %80. Gruplar standartlaştırılmış farkla ve kontrollü lojistik modelle karşılaştırıldı. Keşifsel.',
    grafikler: [{ kur: gizliGrafik(oz), etiket: 'Gizli ve görünür hazinelerde nitelik payları', baslik: 'Gizli ve görünür hazinelerde özelliklerin payı', yukseklik: 220 }],
  }
}

export function klonBolum(oz: Ozet, g: Galaksi): Bolum {
  const k = oz.k5
  const ayni = k.takipci.wilson[0] <= k.oncul.wilson[1] && k.oncul.wilson[0] <= k.takipci.wilson[1]
  const dl = Object.values(k.takipci_dilim)
  const vs = k.dalgalar[0]!
  return {
    id: 'klon', kisa: 'Taklit', maske: 'klon', uzaklik: 21, etiketler: oncuEtiketleri(oz, g),
    baslik: ayni ? 'Bir hit’i taklit etmek ek şans getirmiyor; şans, bölgenin kendisinde.' : 'Bir hit’i taklit edenler, ondan önce gelenlerden farklı sonuç alıyor.',
    govde: <>
      <p>Büyük bir hit'e çok benzeyen sonraki oyunların {ekI(yz(k.takipci.hit_oran))} hit oluyor; örneklem ortalamasının {sayi(k.takipci.hit_oran / oz.hit_yuzde, 0)} katı. Ancak aynı içerik bölgesine hit'ten <em>önce</em> çıkanların da {ekI(yz(k.oncul.hit_oran))} hit olmuş: hit, zaten verimli bir bölgenin işareti.</p>
      <p>Zamanlama önemli: ilk altı ayda gelen takipçilerin {yz(dl[0]!.oran)}, bir-iki yıl sonra gelenlerin {yz(dl[dl.length - 1]!.oran)} hit oluyor. {vs.ad} akımına katılan {sayi(vs.takipci.length)} oyunun bağımsızlarında oran yalnız {yz((vs.hit / vs.orneklem) * 100)}.</p>
    </>,
    harita: `${vs.ad} ile başlayan akıma ve ${k.dalgalar[1]!.diger[0] ?? k.dalgalar[1]!.ad} ile gelen deste kurma dalgasına katılan oyunlar.`,
    yontem: `Öncü: ilk yılında 5.000+ inceleme alan ${sayi(k.dalga.oncu.n_merkez)} oyun. Benzerlik: içerik etiketi vektörlerinin kosinüsü ≥ 0,70. Plasebo ve öncül karşılaştırmalı; Wilson aralıkları. Keşifsel.`,
    grafikler: [{ kur: klonGrafik(oz), etiket: 'Hit’ten önce ve sonra aynı bölgeye çıkan oyunların hit oranı', baslik: 'Hit olma oranı: hit’ten önce, sonra (ay) ve sıradan bir oyunun benzerleri', yukseklik: 200 }],
  }
}

export function firsatBolum(oz: Ozet): Bolum {
  const firsat = oz.k6.bolgeler.filter((x) => x.firsat)
  const cozy = firsat.find((x) => x.ad.startsWith('Cozy'))
  const sessiz = [...firsat].sort((a, z) => a.goreli_buyume - z.goreli_buyume)[0]
  return {
    id: 'firsat', kisa: 'Fırsat bölgeleri', maske: 'firsat', uzaklik: 17,
    etiketler: oz.k6.etiketler.map((e) => ({ konum: e.merkez, ad: bolgeAdi(e.ad), tur: 'bolge' as const })),
    baslik: `${firsat.length} içerik bölgesi hem az kalabalık hem beklenenden sık hit veriyor.`,
    govde: <>
      <p>Oyunları içerik etiketlerine göre {oz.k6.k} bölgeye ayırdık ve her bölgede gerçekleşen hit sayısını, aynı fiyat, tür ve yıl karışımından beklenenle karşılaştırdık. Fırsat bölgelerinde çoğu bölgeden az oyun çıkıyor, ama çıkanlar beklenenden sık hit oluyor.</p>
      {cozy && <p>Cozy ve Wholesome oyunlar beklenenin {sayi(cozy.ob, 1)} katı hit veriyor; ancak bu bölgeye çıkan oyun sayısı Steam ortalamasının {sayi(cozy.goreli_buyume, 1)} katı hızla artıyor. Fırsat penceresi daralıyor.</p>}
      {sessiz && sessiz !== cozy && (
        <p>
          En sakin aday {bolgeAdi(sessiz.ad, ' ve ')}: beklenenin {sayi(sessiz.ob, 1)} katı hit, arz ise Steam'den hızlı büyümüyor.
          {(oz.duyarlilik.K6[sessiz.ad]?.alt ?? 2) <= 1 && ` Ancak yalnız 2021 sonrası oyunlarla bakıldığında fark belirsizleşiyor (×${sayi(oz.duyarlilik.K6[sessiz.ad]!.ob, 2)}); bu bölge için sonuç sağlam değil.`}
        </p>
      )}
    </>,
    harita: 'Fırsat bölgelerindeki oyunlar ve bölge adları.',
    yontem: 'Küresel k-ortalamalar (içerik etiketi vektörleri). Beklenen hit: yıl, tür, fiyat, Early Access ve dil kontrollü lojistik model; oran için Poisson aralığı. Keşifsel.',
    grafikler: [{ kur: firsatGrafik(oz), etiket: 'Bölgelere göre gözlenen ÷ beklenen hit', baslik: 'Hit: gerçekleşen ÷ beklenen (turuncu = fırsat bölgesi)', yukseklik: 250 }],
  }
}

export function esikBolum(oz: Ozet): Bolum {
  const t = oz.k8.tahmin.find((x) => x.esik === 50)!
  const yuz = (v: number) => (Math.exp(v) - 1) * 100
  const isaretli = (v: number) => `${v >= 0 ? '+' : '−'}%${sayi(Math.abs(v), 1)}`
  const yok = t.alt <= 0 && t.ust >= 0
  return {
    id: 'esik', kisa: '50 eşiği', maske: null, uzaklik: 24,
    baslik: yok ? '“50 incelemeyi geç, algoritma seni görsün” veride karşılık bulmuyor.' : `50 incelemeyi geçen oyunların ilgisi ${t.sicrama > 0 ? 'sıçrıyor' : 'düşüyor'}.`,
    govde: <>
      <p>Geliştiriciler arasında yaygın bir kanı var: 50 incelemeyi geçen oyunu Steam önermeye başlar. {sayi(Math.round(oz.k8.oyun / 1000))} bin oyunun {sayi(Math.round(oz.k8.gozlem / 1e6))} milyon aylık inceleme diliminde, 50'yi geçen oyunların inceleme hızı {isaretli(yuz(t.sicrama))} değişiyor (%95 aralık {isaretli(yuz(t.alt))} … {isaretli(yuz(t.ust))}).</p>
      <p>Etkisi olmaması gereken plasebo eşiklerden (20, 30, 40…) farkı yok. İlgi bir eşikte açılan bir kapı gibi değil, pürüzsüz büyüyor.</p>
    </>,
    harita: 'Tüm oyunlar.',
    yontem: 'Süreksizlik regresyonu (iki taraflı yerel doğrusal), plasebo eşikler, oyun düzeyinde kümelenmiş hata. 10 eşiği seçilim yanlılığı nedeniyle yorumlanmadı. Keşifsel.',
    grafikler: [{ kur: esikGrafik(oz), etiket: 'İnceleme eşiklerinde inceleme hızındaki sıçrama', baslik: 'Eşiği geçince inceleme hızındaki değişim', yukseklik: 210 }],
  }
}

export function metinBolum(oz: Ozet): Bolum {
  const m = oz.k9.modeller
  const [k4, km, tf] = [m['K4 nitelikleri']!, m['K4 + metin']!, m['Yalnız metin (TF-IDF)']!]
  const us = oz.k9.uslup_or
  const uz = us['Metin uzunluğu (log)']!
  const ab = us['Abartı sıfatları (unique, epic…)']!
  const katiyor = km.fark_alt > 0
  return {
    id: 'metin', kisa: 'Mağaza sayfası', maske: 'hit', uzaklik: 22,
    baslik: katiyor ? 'Mağaza sayfasının metni, oyunun kaderi hakkında ipucu veriyor.' : 'Mağaza sayfasının metni, başarı hakkında ek bilgi taşımıyor.',
    govde: <>
      <p>Çıkış öncesi bilgilerle kurduğumuz tahmin modeline mağaza açıklaması eklendiğinde isabet (PR-AUC) {sayi(k4.pr_auc, 2)} iken {sayi(km.pr_auc, 2)} oluyor; rastgele tahminin değeri {sayi(oz.hit_yuzde / 100, 2)}. Metin tek başına da {sayi(tf.pr_auc, 2)} alıyor.</p>
      <p>Hit'le birlikte görülen ifadeler "co-op", "wishlist" ve "from the creators of"; ters yönde "VR", "arcade", "levels". Üslupta en güçlü işaret emek: uzun ve somut metinler daha sık tutuyor (×{sayi(uz.tahmin, 2)}). "Unique", "epic" gibi büyük sözcüklerin ise {ab.alt <= 1 && ab.ust >= 1 ? 'ilişkisi yok' : `etkisi ×${sayi(ab.tahmin, 2)}`}.</p>
    </>,
    harita: 'İlk yılında hit olan oyunlar.',
    yontem: `${sayi(oz.k9.n_test)} test oyunu (2024–25), eğitim ≤ 2023. TF-IDF ve cümle gömmesi (MiniLM) + lojistik regresyon; LightGBM ile sızıntısız yığınlama; paired bootstrap. Ödül, satış ve basın alıntısı içeren cümleler çıkarıldı; metin bugünkü hâli olduğundan artış bir üst sınır. Keşifsel.`,
    grafikler: [{ kur: metinGrafik(oz), etiket: 'Modellerin tahmin isabeti (PR-AUC)', baslik: 'Tahmin isabeti (PR-AUC, test 2024–2025)', yukseklik: 170 }],
  }
}
