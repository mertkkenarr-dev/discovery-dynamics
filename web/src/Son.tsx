/**
 * Kapanış: ön kayıtlı hipotezlerin sonuçları, yöntem ve veri hattı, araçlar, sınırlar (iki dil).
 * Okur bir bulguyu paylaşmadan önce kanıt düzeyini ve neyi göstermediğini de görmeli; bu yüzden ayrı bir bölüm, dipnot değil.
 */
import { hipotezMetni } from './arayuz'
import { bicim, useDil } from './dil'
import type { Ozet } from './veri'

const M = {
  tr: {
    hipotezler: 'Ön kayıtlı hipotezler',
    hipGiris: (n: number, k: number) => `Hipotezler veriye bakılmadan önce yazılıp tarihlendi; sonuçlar çoklu test için Holm yöntemiyle düzeltildi. ${n} hipotezden ${k} tanesi desteklendi. Ön kayıtta olmayan her analiz sitede "keşifsel" olarak işaretli.`,
    sutun: ['Hipotez', 'Konu', 'Sonuç'],
    yontem: 'Yöntem',
    y1: (n: string, o: string) => `Evren, 2018–2025 arasında Steam'de çıkan oyunlar; haritada içerik etiketi taşıyan ${n} oyun var. Bulgular, büyük yayıncı desteği olmayan ${o} bağımsız oyundan oluşan örneklemden geliyor. Başarı ölçüsü oyunun ilk 365 gününde aldığı Steam incelemesi; ilk yılda 500 ve üstü "hit" sayıldı ve her bulgu beğeni, tahmini gelir ve göreli sıra gibi ikincil ölçülerle de kontrol edildi.`,
    y2: 'Ham API cevapları değiştirilmeden saklandı; her temizlik kararı etkilediği kayıt sayısı ve gerekçesiyle kayda geçti, veri hattı otomatik tutarlılık kontrolleriyle doğrulanıyor. Nedensel sorularda eğilim skoru eşleştirmesi ve süreksizlik regresyonu, tahminde zamansal bölmeli LightGBM, metin analizinde TF-IDF ve cümle gömmeleri kullanıldı. Tahmin modellerinde yalnız çıkıştan önce bilinebilen bilgiler var; sonradan değişebilen alanlar ayrıca işaretlendi.',
    araclar: [['Veri ve analiz', 'Python, DuckDB, pandas, statsmodels, scikit-learn, LightGBM, UMAP, sentence-transformers'], ['Görselleştirme', 'matplotlib, Observable Plot, React, Three.js (React Three Fiber)'], ['Kaynaklar', 'Steam mağaza API’si (IStoreBrowseService), Steam inceleme grafikleri, IGDB']],
    sinirBaslik: 'Bu harita neyi göstermiyor?',
    sinirlar: [
      ['Neden-sonuç değil.', 'Ön kayıtlı testler dışındaki bulgular "birlikte görülüyor" demek. Çince eklemek, fiyatı artırmak ya da çok oyunculu yapmak bir oyunu tek başına büyütmez.'],
      ['Satış değil, inceleme.', 'Steam satış rakamı yayınlamıyor. İnceleme sayısı satışla güçlü biçimde ilişkili, ama oyuncu başına inceleme oranı türe göre değişiyor.'],
      ['Konum yaklaşık.', 'Her oyunun ilk on içerik etiketi bir vektöre çevrilip üç boyuta indirildi (UMAP). Yakınlık anlamlı; eksenlerin ve uzak mesafelerin anlamı yok.'],
      ['Etiketler sonradan oylanıyor.', 'Başarılı oyunlar daha çok ve daha belirgin etiket alabiliyor; etiket temelli bulgular bu yüzden keşifsel.'],
    ],
    tahmin: (u: string, t: string) => ['Tahmin sınırlı.', `Çıkış öncesi bilgilerle kurulan model en umut verici bulduğu %10'luk dilimde %${u} isabet yakalıyor (ortalama %${t}). İyi bir eleme aracı, kehanet değil.`] as const,
    alt: 'Discovery Dynamics, Mert Safa Kenar’ın veri analizi projesi.',
    yazar: 'Yazar',
  },
  en: {
    hipotezler: 'Pre-registered hypotheses',
    hipGiris: (n: number, k: number) => `The hypotheses were written down and dated before looking at the data; results are corrected for multiple testing with the Holm method. ${k} of ${n} hypotheses were supported. Every analysis that wasn't pre-registered is marked "exploratory" on this site.`,
    sutun: ['Hypothesis', 'Topic', 'Result'],
    yontem: 'Method',
    y1: (n: string, o: string) => `The universe is games released on Steam between 2018 and 2025; the map shows the ${n} that carry content tags. Findings come from a sample of ${o} indie games without major-publisher backing. Success is the number of Steam reviews in a game's first 365 days; 500 or more counts as a "hit", and every finding was also checked against secondary measures such as rating, estimated revenue and relative rank.`,
    y2: 'Raw API responses were stored unchanged; every cleaning decision was logged with the number of records it affected and its rationale, and the pipeline is validated by automated consistency checks. Causal questions use propensity-score matching and regression discontinuity, prediction uses LightGBM with a temporal split, and text analysis uses TF-IDF and sentence embeddings. Prediction models only use information known before launch; fields that can change after launch are flagged separately.',
    araclar: [['Data and analysis', 'Python, DuckDB, pandas, statsmodels, scikit-learn, LightGBM, UMAP, sentence-transformers'], ['Visualization', 'matplotlib, Observable Plot, React, Three.js (React Three Fiber)'], ['Sources', 'Steam store API (IStoreBrowseService), Steam review histograms, IGDB']],
    sinirBaslik: 'What this map doesn’t show',
    sinirlar: [
      ['Not cause and effect.', 'Outside the pre-registered tests, findings mean "seen together". Adding Chinese, raising the price or going multiplayer won’t grow a game on its own.'],
      ['Reviews, not sales.', 'Steam doesn’t publish sales figures. Review counts are strongly related to sales, but the share of players who leave a review varies by genre.'],
      ['Positions are approximate.', 'Each game’s first ten content tags were turned into a vector and reduced to three dimensions (UMAP). Closeness is meaningful; the axes and long distances are not.'],
      ['Tags are voted on after launch.', 'Successful games can collect more and sharper tags, so tag-based findings are exploratory.'],
    ],
    tahmin: (u: string, t: string) => ['Prediction is limited.', `A model built on pre-launch information finds ${u}% hits in the 10% of games it rates most promising (average ${t}%). A good screening tool, not a crystal ball.`] as const,
    alt: 'Discovery Dynamics, a data analysis project by Mert Safa Kenar.',
    yazar: 'Author',
  },
}

export function Son({ oz }: { oz: Ozet }) {
  const dil = useDil()
  const m = M[dil]
  const { sayi } = bicim(dil)
  const h = Object.entries(oz.hipotez)
  const tutan = h.filter(([, v]) => v.sonuc === 'desteklendi')
  const sinirlar = [...m.sinirlar, m.tahmin(sayi(oz.model.ust_dilim, 0), sayi(oz.model.taban * 100, 1))]
  return (
    <section id="son" className="son" data-bolum="son">
      <div className="son-ic">
        <h2>{m.hipotezler}</h2>
        <p>{m.hipGiris(h.length, tutan.length)}</p>
        <table className="hipotezler">
          <thead>
            <tr>
              {m.sutun.map((s) => (
                <th key={s} scope="col">
                  {s}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {h.map(([k, v]) => {
              const x = hipotezMetni(dil, k, v.konu, v.sonuc)
              return (
                <tr key={k} data-sonuc={v.sonuc === 'desteklendi' ? 'evet' : 'hayir'}>
                  <th scope="row">{k}</th>
                  <td>{x.konu}</td>
                  <td>{x.sonuc}</td>
                </tr>
              )
            })}
          </tbody>
        </table>

        <h2>{m.yontem}</h2>
        <p>{m.y1(sayi(oz.yildiz), sayi(oz.orneklem))}</p>
        <p>{m.y2}</p>
        <dl className="araclar">
          {m.araclar.map(([ad, deger]) => (
            <div key={ad}>
              <dt>{ad}</dt>
              <dd>{deger}</dd>
            </div>
          ))}
        </dl>

        <h2>{m.sinirBaslik}</h2>
        <ul className="sinirlar">
          {sinirlar.map(([b, metin]) => (
            <li key={b}>
              <strong>{b}</strong> {metin}
            </li>
          ))}
        </ul>
      </div>
      <footer className="alt">
        <p>{m.alt}</p>
        <nav className="alt-baglanti" aria-label={m.yazar}>
          <a href="https://github.com/mertkkenarr-dev" target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href="https://www.linkedin.com/in/mert-kenar-02b40529b" target="_blank" rel="noreferrer">
            LinkedIn
          </a>
        </nav>
      </footer>
    </section>
  )
}
