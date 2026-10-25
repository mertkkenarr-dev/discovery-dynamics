# Discovery Dynamics: Steam Galaksisi

[English](README.md) | **Türkçe**

**Canlı site:** https://mertkkenarr-dev.github.io/discovery-dynamics/?lang=tr

Steam'de bağımsız bir oyunu görünür kılan şeyin ne olduğunu araştıran bir veri analizi çalışması. Steam'e her yıl yaklaşık 20 bin oyun
çıkıyor ve çoğu neredeyse hiç görülmüyor. Proje, 2018–2025 arasında çıkan 92.492 oyunu izliyor, büyük yayıncı desteğini ayırıyor ve
çıkış öncesi hangi tercihlerin organik başarıyla birlikte görüldüğünü soruyor. Sonuçlar Türkçe ve İngilizce, etkileşimli bir 3B haritada
anlatılıyor: her yıldız bir oyun, yakın yıldızlar benzer oyunlar, parlaklık ilk yılın inceleme sayısı.

Çalışma Google Data Analytics çerçevesini izliyor (Ask → Prepare → Process → Analyze → Share → Act). Hipotezler veriye bakılmadan
önce yazılıp tarihlendi; ön kayıtta olmayan analizler "keşifsel" olarak işaretli.

## Bulgular

- **Oyunların çoğu hiç görülmüyor.** Bağımsız oyunların %54'ü ilk yılında 10'dan az inceleme alıyor; %4,8'i 500'ü geçiyor ("hit").
  Yıllık çıkış 2,8 katına çıktı (2018'de 7.398, 2025'te 20.363), ama hit oranı her yıl %4,0 ile %5,4 arasında kaldı.
- **Early Access kuyruğu uzatıyor** (ön kayıtlı, desteklendi): ilgi zamana yayılıyor (odds ×1,27); ilgisi ikinci yıla taşan oyunların
  hit oranı, patlayıp sönenlerin iki katı.
- **Basitleştirilmiş Çince desteği** (ön kayıtlı, desteklendi): +%57–75 inceleme; ama en başarılı oyunlar Çince'yi çıkıştan sonra 13 kat
  daha sık ekliyor, yani ilişkinin bir kısmı başarıdan dile doğru.
- **Tanıdık kazanıyor** (ön kayıtlı "ters U" desteklenmedi): etiket kombinasyonu ne kadar alışılmadıksa ilgi o kadar az. Stüdyoların
  ikinci oyunu ilkinden iyi değil; kalabalık alt türler dezavantaj değil.
- **Bir hit'i kopyalamak bir şey katmıyor.** Büyük hit'lere çok benzeyen sonraki oyunların %15,5'i hit oluyor, ama aynı bölgeye hit'ten
  önce çıkanların da %16,7'si: hit, verimli bir bölgenin işareti. Geç gelenler daha kötü yapıyor.
- **Gizli hazineler.** Çok beğenilen oyunların %44'ü görünmez kalıyor; görünür olanlar daha sık Simulation, daha pahalı, Early Access ile
  çıkmış ve Playtest açmış. Çıkış öncesi demo iki grubu ayırmıyor.
- **"50 inceleme eşiği" yok.** 1 milyon aylık inceleme diliminde süreksizlik regresyonu 50 incelemede sıçrama bulmuyor (−%1,0; %95 GA
  −%2,4 … +%0,4).
- **Mağaza metni bilgi taşıyor.** Mağaza açıklaması, çıkış öncesi LightGBM modelinin PR-AUC'sini 0,27'den 0,31'e çıkarıyor (üst sınır;
  ödül ve satış cümleleri çıkarıldı). Uzun ve somut açıklamalar başarıyla birlikte görülüyor; "unique", "epic" gibi kelimeler değil.
- **Türler.** Management, Dating Sim ve City Builder hem az riskli hem ödüllü (hit oranı %11–12). Tür karışımları parçalarının öngördüğü
  kadar başarılı: 176 tür çiftinin hiçbiri beklenenden farklı değil.

## Yöntem

- **Ön kayıt:** 5 yönlü hipotez Holm düzeltmesiyle sınandı; etki büyüklükleri %95 aralıklarla verildi.
- **Nedensel ve yarı nedensel araçlar:** kesin katmanlı eğilim skoru eşleştirmesi, plasebo eşikli süreksizlik regresyonu, birinci fark
  tasarımları, tekrarlanan dil anlık görüntüleriyle ters nedensellik kontrolü.
- **Makine öğrenmesi:** zamansal bölmeli LightGBM (eğitim ≤ 2023, test 2024–2025), SHAP katkıları, sızıntısız yığınlamayla TF-IDF ve cümle
  gömmesi metin modelleri, harita için UMAP, içerik bölgeleri için küresel k-ortalamalar.
- **Bulgu olarak veri kalitesi:** 2021 öncesi oyuncu etiketleri seçilimli (başarılı oyunlar iki kat fazla etiket taşıyor). Etiket temelli
  sonuçlar 2021+ oyunlarla yeniden hesaplandı; tutmayan tek sonuç "sağlam değil" olarak raporlandı.

Mimari diyagramı ve teknoloji gerekçesi için: [README.md](README.md#architecture).

## Kurulum

Siteyi çalıştırmak (veri dosyaları `web/public/veri/` içinde):

```bash
cd web && npm ci && npm run dev
```

Her şeyi ham kaynaklardan yeniden üretmek (saatler sürer; çekiciler kaldığı yerden devam eder; IGDB için `.env`'de Twitch API bilgileri gerekir):

```bash
cp .env.example .env && cd scripts && for s in 00_indir 01_evren 02_getitems 03_histogram 05_igdb; do uv run --no-project --python 3.12 --with pandas --with pyarrow --with pyyaml --with requests --with python-dotenv python $s.py; done && bash hat.sh && uv run --no-project --python 3.12 --with pandas --with pyarrow --with pyyaml --with requests --with numpy --with umap-learn python 14_web_veri.py
```

## Belgeler

- [docs/ANALIZ_RAPORU.md](docs/ANALIZ_RAPORU.md): bütün analizler, grafiklerle, sade dille
- [docs/HIPOTEZLER.md](docs/HIPOTEZLER.md): veriye bakılmadan önce yazılmış, tarihli hipotezler
- [docs/KESIFSEL_K5_K8.md](docs/KESIFSEL_K5_K8.md): keşifsel analizlerin önceden sabitlenen tanımları ve değişiklik günlüğü
- [docs/VERI_MIMARISI.md](docs/VERI_MIMARISI.md), [docs/VERI_RAPORU.md](docs/VERI_RAPORU.md): veri katmanları, temizlik protokolü, otomatik kontroller
- [docs/KAPSAM_VE_PLAN.md](docs/KAPSAM_VE_PLAN.md), [docs/ANALIZ_PLANI.md](docs/ANALIZ_PLANI.md), [docs/VERI_KATALOGU.md](docs/VERI_KATALOGU.md): kapsam, plan, kaynak ve lisans kaydı

## Sınırlar

Steam satış rakamı yayınlamadığı için başarı ilk yılın inceleme sayısıyla ölçülüyor; bu ölçü satış sıralamasını izliyor ama türe göre
değişiyor. Ön kayıtlı testler dışındaki bulgular ilişki, neden-sonuç değil. Oyuncu etiketleri çıkıştan sonra oylanıyor ve bu çekinceyle
kullanıldı; mağaza sayfaları bugünkü hâliyle, bu yüzden metin temelli artışlar üst sınır olarak verildi.

Veri: herkese açık Steam uç noktalarından mağaza ve inceleme verisi; IGDB (Twitch) oyun bilgileri; FronkonGames Steam Games Dataset (MIT).
Ham veri yeniden dağıtılmıyor. Bu bağımsız bir portföy projesidir, Valve ile bağlantılı değildir.

**Hazırlayan:** Mert Safa Kenar · [GitHub](https://github.com/mertkkenarr-dev) · [LinkedIn](https://www.linkedin.com/in/mert-kenar-02b40529b)
