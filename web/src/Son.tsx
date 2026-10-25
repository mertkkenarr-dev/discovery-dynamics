/**
 * Kapanış: ön kayıtlı hipotezlerin sonuçları, yöntem ve veri hattı, araçlar, sınırlar.
 * Okur bir bulguyu paylaşmadan önce kanıt düzeyini ve neyi göstermediğini de görmeli; bu yüzden ayrı bir bölüm, dipnot değil.
 */
import { sayi, type Ozet } from './veri'

const ARACLAR = [
  ['Veri ve analiz', 'Python, DuckDB, pandas, statsmodels, scikit-learn, LightGBM, UMAP, sentence-transformers'],
  ['Görselleştirme', 'matplotlib, Observable Plot, React, Three.js (React Three Fiber)'],
  ['Kaynaklar', 'Steam mağaza API’si (IStoreBrowseService), Steam inceleme grafikleri, IGDB'],
] as const

export function Son({ oz }: { oz: Ozet }) {
  const h = Object.entries(oz.hipotez)
  const sinanan = h.filter(([, v]) => v.sonuc.startsWith('destek'))
  const tutan = sinanan.filter(([, v]) => v.sonuc === 'desteklendi')
  return (
    <section id="son" className="son" data-bolum="son">
      <div className="son-ic">
        <h2>Ön kayıtlı hipotezler</h2>
        <p>
          Çalışmanın {h.length} hipotezi veriye bakılmadan önce yazılıp tarihlendi; sonuçlar çoklu test için Holm yöntemiyle düzeltildi. Şimdiye kadar
          sınanan {sinanan.length} hipotezden {tutan.length} tanesi desteklendi. Ön kayıtta olmayan her analiz sitede "keşifsel" olarak işaretli.
        </p>
        <table className="hipotezler">
          <thead>
            <tr>
              <th scope="col">Hipotez</th>
              <th scope="col">Konu</th>
              <th scope="col">Sonuç</th>
            </tr>
          </thead>
          <tbody>
            {h.map(([k, v]) => (
              <tr key={k} data-sonuc={v.sonuc === 'desteklendi' ? 'evet' : v.sonuc.startsWith('destek') ? 'hayir' : 'bekliyor'}>
                <th scope="row">{k}</th>
                <td>{v.konu.replace(/\s*\(M\d\)$/, '')}</td>
                <td>{v.sonuc}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <h2>Yöntem</h2>
        <p>
          Evren, 2018–2025 arasında Steam'de çıkan oyunlar; haritada içerik etiketi taşıyan {sayi(oz.yildiz)} oyun var. Bulgular, büyük yayıncı desteği olmayan{' '}
          {sayi(oz.orneklem)} bağımsız oyundan oluşan örneklemden geliyor. Başarı ölçüsü oyunun ilk 365 gününde aldığı Steam incelemesi; ilk yılda 500 ve
          üstü "hit" sayıldı ve her bulgu beğeni, tahmini gelir ve göreli sıra gibi ikincil ölçülerle de kontrol edildi.
        </p>
        <p>
          Ham API cevapları değiştirilmeden saklandı; her temizlik kararı etkilediği kayıt sayısı ve gerekçesiyle kayda geçti, veri hattı otomatik tutarlılık
          kontrolleriyle doğrulanıyor. Nedensel sorularda eğilim skoru eşleştirmesi ve süreksizlik regresyonu, tahminde zamansal bölmeli LightGBM, metin
          analizinde TF-IDF ve cümle gömmeleri kullanıldı. Tahmin modellerinde yalnız çıkıştan önce bilinebilen bilgiler var; sonradan değişebilen alanlar
          ayrıca işaretlendi.
        </p>
        <dl className="araclar">
          {ARACLAR.map(([ad, deger]) => (
            <div key={ad}>
              <dt>{ad}</dt>
              <dd>{deger}</dd>
            </div>
          ))}
        </dl>

        <h2>Bu harita neyi göstermiyor?</h2>
        <ul className="sinirlar">
          <li>
            <strong>Neden-sonuç değil.</strong> Ön kayıtlı testler dışındaki bulgular "birlikte görülüyor" demek. Çince eklemek, fiyatı artırmak ya da çok
            oyunculu yapmak bir oyunu tek başına büyütmez.
          </li>
          <li>
            <strong>Satış değil, inceleme.</strong> Steam satış rakamı yayınlamıyor. İnceleme sayısı satışla güçlü biçimde ilişkili, ama oyuncu başına
            inceleme oranı türe göre değişiyor.
          </li>
          <li>
            <strong>Konum yaklaşık.</strong> Her oyunun ilk on içerik etiketi bir vektöre çevrilip üç boyuta indirildi (UMAP). Yakınlık anlamlı; eksenlerin ve
            uzak mesafelerin anlamı yok.
          </li>
          <li>
            <strong>Etiketler sonradan oylanıyor.</strong> Başarılı oyunlar daha çok ve daha belirgin etiket alabiliyor; etiket temelli bulgular bu yüzden
            keşifsel.
          </li>
          <li>
            <strong>Tahmin sınırlı.</strong> Çıkış öncesi bilgilerle kurulan model en umut verici bulduğu %10'luk dilimde %{sayi(oz.model.ust_dilim, 0)} isabet
            yakalıyor (ortalama %{sayi(oz.model.taban * 100, 1)}). İyi bir eleme aracı, kehanet değil.
          </li>
        </ul>
      </div>
      <footer className="alt">
        <p>Discovery Dynamics, Mert Safa Kenar'ın veri analizi projesi.</p>
        <nav className="alt-baglanti" aria-label="Yazar">
          <a href="https://github.com/mertkkenarr-dev" target="_blank" rel="noreferrer">GitHub</a>
          <a href="https://www.linkedin.com/in/mert-kenar-02b40529b" target="_blank" rel="noreferrer">LinkedIn</a>
        </nav>
      </footer>
    </section>
  )
}
