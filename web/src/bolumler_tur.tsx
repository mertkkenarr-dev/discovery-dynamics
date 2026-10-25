/**
 * K10 bölümleri: alt türlerin risk-ödül karnesi ve hibrit türler. Başlıklar veriden: risk ile ödül ters gitmiyorsa ya da anlamlı
 * hibrit çıkarsa cümleler de değişir. Haritadaki vurgu tür bit dizilerinden (turler.bin).
 */
import type { Bolum } from './bolumler'
import { bitMaske, cokTurMaske } from './galaksi/maske'
import { azRiskliOdullu, hibritGrafik, karneGrafik } from './grafikler_tur'
import { sayi, yuzde, type Galaksi, type Ozet } from './veri'

const liste = (a: string[]) => (a.length <= 1 ? a.join('') : `${a.slice(0, -1).join(', ')} ve ${a[a.length - 1]}`)

function korelasyon(x: number[], y: number[]): number {
  const mx = x.reduce((s, v) => s + v, 0) / x.length
  const my = y.reduce((s, v) => s + v, 0) / y.length
  const sxy = x.reduce((s, v, i) => s + (v - mx) * (y[i]! - my), 0)
  return sxy / Math.sqrt(x.reduce((s, v) => s + (v - mx) ** 2, 0) * y.reduce((s, v) => s + (v - my) ** 2, 0))
}

export function turlerBolum(oz: Ozet, g: Galaksi, bitler: Uint8Array[]): Bolum {
  const k = oz.k10.karne
  const sirali = [...k].sort((a, z) => z.hit - a.hit)
  const [ust, alt] = [sirali.slice(0, 3), sirali.slice(-3)]
  const r = korelasyon(k.map((x) => x.gorunmez), k.map((x) => x.hit))
  const ob = [...k].sort((a, z) => z.ob - a.ob)
  const dusen = k.filter((x) => x.egilim_ust < 0).sort((a, z) => a.egilim - z.egilim)
  const iyi = azRiskliOdullu(oz)
  return {
    id: 'turler', kisa: 'Türler', maske: null, uzaklik: 21,
    maskeOzel: bitMaske(g, k.flatMap((x, i) => (iyi(x) ? [bitler[i]!] : []))),
    baslik: r < -0.5 ? 'Türlerde risk ile ödül ters gitmiyor: en ödüllü türler aynı zamanda en az riskli.' : 'Türlerde risk ve ödül birbirinden bağımsız değişiyor.',
    govde: <>
      <p>{liste(ust.map((x) => x.tur))} oyunlarında hit oranı %{sayi(Math.min(...ust.map((x) => x.hit)), 0)}–{sayi(Math.max(...ust.map((x) => x.hit)), 0)}. Öbür uçta {liste(alt.map((x) => x.tur))}: hit oranı en fazla {yuzde(Math.max(...alt.map((x) => x.hit)), 1)}, görünmez kalan oyun payı en az {yuzde(Math.min(...alt.map((x) => x.gorunmez)))}.</p>
      <p>Fiyat ve kapsam farkı ayrıldığında da sıralama büyük ölçüde korunuyor: beklenenin en üstünde {liste(ob.slice(0, 3).map((x) => x.tur))}, en altında {liste(ob.slice(-3).map((x) => x.tur))}.{dusen.length > 0 && ` 2021–22'den 2023–24'e hit oranı anlamlı biçimde düşen türler: ${liste(dusen.map((x) => x.tur))}${dusen.every((x) => x.goreli_buyume > 1) ? '; hepsinin arzı Steam ortalamasından hızlı büyüyor' : ''}.`}</p>
    </>,
    harita: 'Hem az riskli hem ödüllü alt türlerin oyunları (görünmez oranı ortalamanın altında, hit oranı üstünde).',
    yontem: `2021–2025 çıkışlı bağımsız oyunlar; ${k.length} alt tür (her biri ≥ 500 oyun). Alt tür: oyunun ilk 10 etiketindeki tür etiketi. Wilson aralıkları; beklenen hit yıl, tür, fiyat, Early Access ve dil kontrollü lojistik modelden. 2021 öncesi etiket kapsamı başarıyla ilişkili olduğu için dışarıda. Keşifsel.`,
    grafikler: [{ kur: karneGrafik(oz), etiket: 'Alt türlerin risk ve ödül haritası', baslik: 'Alt türlere göre risk (görünmez kalma) ve ödül (hit olma)', yukseklik: 300 }],
  }
}

export function hibritBolum(oz: Ozet, g: Galaksi, bitler: Uint8Array[]): Bolum {
  const h = oz.k10
  const yok = h.n_anlamli === 0
  return {
    id: 'hibrit', kisa: 'Tür karışımı', maske: null, uzaklik: 22,
    maskeOzel: cokTurMaske(g, bitler, 3),
    baslik: yok ? 'Tür karıştırmak tek başına bir avantaj değil: karışımlar, parçalarının toplamı kadar başarılı.' : `${h.n_anlamli} tür karışımı, parçalarının öngördüğünden farklı sonuç veriyor.`,
    govde: <>
      <p>{sayi(h.n_cift)} tür çiftini, her türün tek başına öngördüğü başarıyla karşılaştırdık. {yok ? `Hiçbiri çoklu test düzeltmesinden sonra beklenenden farklı değil; tek başına anlamlı görünen ${h.n_p05} çift, şansla beklenenle aynı düzeyde.` : `${h.n_anlamli} çift çoklu test düzeltmesinden sonra da beklenenden farklı.`}</p>
      {yok && <p>Pratik anlamı: bir karışımın başarısını bileşen türlerin kendi başarısı belirliyor. "Doğru iki türü birleştir, sinerji yakala" fikrinin veride karşılığı yok.</p>}
    </>,
    harita: 'Üç ya da daha fazla alt tür etiketi taşıyan oyunlar.',
    yontem: 'Beklenen hit: yıl, tür, fiyat, Early Access, dil ve tüm alt türlerin ayrı etkilerini içeren lojistik model (etkileşimsiz). Çift başına gözlenen ÷ beklenen, Poisson testi, Benjamini–Hochberg düzeltmesi. Eş anlamlı çiftler hariç; 2021–2025. Keşifsel.',
    grafikler: [{ kur: hibritGrafik(oz), etiket: 'Tür çiftlerinde gözlenen ÷ beklenen hit', baslik: 'En uç tür çiftleri: gözlenen ÷ beklenen hit (gri = anlamsız)', yukseklik: 360 }],
  }
}
