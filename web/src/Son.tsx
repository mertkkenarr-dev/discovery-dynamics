/**
 * Haritanın sınırları ve yöntem. Okur bir bulguyu paylaşmadan önce neyi göstermediğini de görmeli;
 * bu yüzden sınırlar dipnotta değil, ayrı bir bölümde ve sade dille.
 */
import { sayi, type Ozet } from './veri'

export function Son({ oz }: { oz: Ozet }) {
  return (
    <section id="son" className="son" data-bolum="son">
      <div className="son-ic">
        <h2>Bu harita neyi göstermiyor?</h2>
        <ul className="sinirlar">
          <li>
            <strong>Neden-sonuç değil.</strong> Buradaki her bulgu "birlikte görülüyor" demek. Çince eklemek, fiyatı artırmak ya da çok oyunculu yapmak bir oyunu tek başına
            büyütmez.
          </li>
          <li>
            <strong>Satış değil, inceleme.</strong> Steam satış rakamı yayınlamıyor. İnceleme sayısı satış sıralamasını iyi izliyor, ama oyuncu başına inceleme oranı türe göre
            değişiyor.
          </li>
          <li>
            <strong>Konum yaklaşık.</strong> Her oyunun ilk on içerik etiketi 391 boyutlu bir vektöre çevrildi ve üç boyuta indirildi (UMAP). Yakınlık anlamlı; eksenlerin ve
            uzak mesafelerin anlamı yok.
          </li>
          <li>
            <strong>Etiketler sonradan oylanıyor.</strong> Başarılı oyunlar daha çok ve daha belirgin etiket alabiliyor; etiket temelli bulgular bu yüzden keşifsel.
          </li>
          <li>
            <strong>Tahmin sınırlı.</strong> Yalnız çıkış öncesi bilinenlerle kurulan model, en umut verici bulduğu %10'luk dilimde %{sayi(oz.model.ust_dilim, 0)} isabet
            yakalıyor (ortalama %{sayi(oz.model.taban * 100, 1)}). İyi bir eleme aracı, kehanet değil.
          </li>
        </ul>

        <h2>Nasıl yapıldı?</h2>
        <p>
          2018–2025 arasında Steam'de çıkan {sayi(oz.yildiz)} oyun haritada. Bulgular, büyük yayıncı desteği olmayan {sayi(oz.orneklem)} bağımsız oyundan oluşan örneklemden
          geliyor. Başarı ölçüsü oyunun ilk 365 günde aldığı Steam incelemesi; hit, ilk yılda 500 ve üstü. Hipotezler veriye bakılmadan önce kaydedildi ve çoklu test için
          düzeltildi; ön kayıtta olmayan analizler "keşifsel" olarak işaretlendi.
        </p>
        <p>
          Veri: Steam mağaza API'si (IStoreBrowseService), Steam inceleme histogramları ve IGDB. Analiz kodu, temizlik kararlarının kaydı ve tam rapor Discovery Dynamics
          deposunda.
        </p>
      </div>
      <footer className="alt">Discovery Dynamics, Steam'de bağımsız oyunların görünürlüğü üzerine bir araştırma. Ekim 2026 taslağı.</footer>
    </section>
  )
}
