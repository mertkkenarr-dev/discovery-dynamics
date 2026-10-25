/* avoid-ai-design-ignore-file: SD4d (" · " yalnız K6 bölge adlarını ayrıştırmak için split edilir; ekranda orta nokta gösterilmez) */
/**
 * K5–K8 bölümleri (gizli hazineler, taklit, fırsat bölgeleri, 50 eşiği). bolumler.tsx ile aynı kural: başlıklar veriden üretilir,
 * yön tersine dönerse cümle de döner. Sayılar ozet.json'dan (analysis/sonuclar/K5–K8).
 */
import type { Bolum } from './bolumler'
import type { Etiket } from './galaksi/Etiketler'
import { esikGrafik, firsatGrafik, gizliGrafik, klonGrafik } from './grafikler_ek'
import { ekI } from './lib/ek'
import { sayi, yuzde, type Galaksi, type Ozet } from './veri'

const konum = (g: Galaksi, i: number): [number, number, number] => [g.konum[i * 3]!, g.konum[i * 3 + 1]!, g.konum[i * 3 + 2]!]
const yz = (v: number, d = 1) => yuzde(v, d)

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
  const sim = f('Tür: Simulation')
  const pt = f('Playtest')
  const demo = f('Çıkıştan önce demo')
  return {
    id: 'gizli', kisa: 'Gizli hazineler', modul: 'K7', maske: 'gizli', uzaklik: 21,
    baslik: `Çok beğenilen her 10 oyundan ${onda} tanesi de görünmez kalıyor.`,
    govde: <>
      <p>Öne çıkanlar gizli hazineler: oyuncuların neredeyse hepsinin beğendiği ama ilk yılında 100'den az inceleme alan {sayi(k.n_gizli)} oyun. Kötü oyun olmak görünmez kalmanın tek nedeni değil.</p>
      <p>Görünür olan hazinelerden (500+ inceleme) neyle ayrılıyorlar? Görünürler daha sık Simulation ({yz(sim.gizli * 100, 0)} yerine {yz(sim.gorunur * 100, 0)}) ve iki kat sık Playtest açmış ({yz(pt.gizli * 100, 0)} yerine {yz(pt.gorunur * 100, 0)}). Çıkış öncesi demo ise iki grupta da aynı: {yz(demo.gizli * 100, 0)}.</p>
    </>,
    grafikler: [{ kur: gizliGrafik(oz), etiket: 'Gizli ve görünür hazinelerde nitelik payları', baslik: 'Gizli ve görünür hazineler: oyunların payı', yukseklik: 220 }],
  }
}

export function klonBolum(oz: Ozet, g: Galaksi): Bolum {
  const k = oz.k5
  const ayni = k.takipci.wilson[0] <= k.oncul.wilson[1] && k.oncul.wilson[0] <= k.takipci.wilson[1]
  const dl = Object.values(k.takipci_dilim)
  const vs = k.dalgalar[0]!
  return {
    id: 'klon', kisa: 'Taklit', modul: 'K5', maske: 'klon', uzaklik: 21, etiketler: oncuEtiketleri(oz, g),
    baslik: ayni ? 'Bir hit’i taklit etmek ek şans getirmiyor. Şans, bölgenin kendisinde.' : 'Bir hit’i taklit edenler, ondan önce gelenlerden farklı sonuç alıyor.',
    govde: <>
      <p>Öne çıkanlar {vs.ad} ile başlayan akıma ve {k.dalgalar[1]!.diger[0]} ile gelen deste kurma dalgasına katılan oyunlar. Büyük bir hit'e çok benzeyen sonraki oyunların {ekI(yz(k.takipci.hit_oran))} hit oluyor; bu, ortalamanın {sayi(k.takipci.hit_oran / oz.hit_yuzde, 0)} katı.</p>
      <p>Ama aynı bölgeye hit'ten <em>önce</em> çıkanların da {ekI(yz(k.oncul.hit_oran))} hit olmuş: hit, verimli bir bölgenin işareti. Geç kalan kaybediyor: ilk altı ayda gelenlerin {yz(dl[0]!.oran)}, bir-iki yıl sonra gelenlerin {yz(dl[dl.length - 1]!.oran)} tutuyor. {vs.ad} akımına katılan {sayi(vs.takipci.length)} oyunun bağımsızlarından yalnız {ekI(yz((vs.hit / vs.orneklem) * 100))} hit oldu.</p>
    </>,
    grafikler: [{ kur: klonGrafik(oz), etiket: 'Hit’ten önce ve sonra aynı bölgeye çıkan oyunların hit oranı', baslik: 'Hit olma oranı: hit’ten önce, sonra (ay) ve sıradan bir oyunun benzerleri', yukseklik: 200 }],
  }
}

export function firsatBolum(oz: Ozet): Bolum {
  const b = oz.k6.bolgeler
  const firsat = b.filter((x) => x.firsat)
  const cozy = firsat.find((x) => x.ad.startsWith('Cozy'))
  const sessiz = [...firsat].sort((a, z) => a.goreli_buyume - z.goreli_buyume)[0]
  return {
    id: 'firsat', kisa: 'Fırsat bölgeleri', modul: 'K6', maske: 'firsat', uzaklik: 17,
    etiketler: oz.k6.etiketler.map((e) => ({ konum: e.merkez, ad: e.ad.split(' · ').slice(0, 2).join(', '), tur: 'bolge' as const })),
    baslik: `${firsat.length} içerik bölgesi hem az kalabalık hem beklenenden sık hit veriyor.`,
    govde: <>
      <p>Haritayı içerik etiketlerine göre {oz.k6.k} bölgeye ayırdık ve her bölgede gerçek hit sayısını, aynı fiyat, tür ve yıl karışımından beklenenle karşılaştırdık. Öne çıkanlar fırsat bölgeleri: çoğu bölgeden az oyun çıkıyor, ama çıkanlar beklenenden sık hit oluyor.</p>
      {cozy && <p>Cozy ve Wholesome oyunlar beklenenin {sayi(cozy.ob, 1)} katı hit veriyor, ama bu bölgeye çıkan oyun sayısı Steam'in {sayi(cozy.goreli_buyume, 1)} katı hızla artıyor: kapı kapanıyor.</p>}
      {sessiz && sessiz !== cozy && <p>En sessiz fırsat {sessiz.ad.split(' · ').slice(0, 2).join(' ve ')}: beklenenin {sayi(sessiz.ob, 1)} katı hit, arz ise Steam'den hızlı büyümüyor.</p>}
    </>,
    grafikler: [{ kur: firsatGrafik(oz), etiket: 'Bölgelere göre gözlenen ÷ beklenen hit', baslik: 'Hit: gerçekleşen ÷ beklenen (turuncu = fırsat)', yukseklik: 250 }],
  }
}

export function esikBolum(oz: Ozet): Bolum {
  const t = oz.k8.tahmin.find((x) => x.esik === 50)!
  const yuz = (v: number) => (Math.exp(v) - 1) * 100
  const isaretli = (v: number) => `${v >= 0 ? '+' : '−'}%${sayi(Math.abs(v), 1)}`
  const yok = t.alt <= 0 && t.ust >= 0
  return {
    id: 'esik', kisa: '50 eşiği', modul: 'K8', maske: null, uzaklik: 24,
    baslik: yok ? '“50 incelemeyi geç, algoritma seni görsün” veride yok.' : `50 incelemeyi geçen oyunların ilgisi ${t.sicrama > 0 ? 'sıçrıyor' : 'düşüyor'}.`,
    govde: <>
      <p>Geliştiriciler arasında yaygın bir kanı var: 50 incelemeyi geçen oyunu Steam önermeye başlar. {sayi(Math.round(oz.k8.oyun / 1000))} bin oyunun {sayi(Math.round(oz.k8.gozlem / 1e6))} milyon aylık inceleme dilimine baktık: 50'yi geçince inceleme hızı {isaretli(yuz(t.sicrama))} değişiyor (%95 aralık {isaretli(yuz(t.alt))} … {isaretli(yuz(t.ust))}).</p>
      <p>Etkisi olmaması gereken 20, 30, 40 gibi eşiklerden farkı yok. İlgi bir kapıdan geçer gibi değil, pürüzsüz büyüyor. (Puanın görünür olduğu 10 eşiği bu veriyle ölçülemiyor: seriler yalnız eninde sonunda 10'u geçen oyunlar için var.)</p>
    </>,
    grafikler: [{ kur: esikGrafik(oz), etiket: 'İnceleme eşiklerinde inceleme hızındaki sıçrama', baslik: 'Eşiği geçince inceleme hızındaki değişim', yukseklik: 210 }],
  }
}
