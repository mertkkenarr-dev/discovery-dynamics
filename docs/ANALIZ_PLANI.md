# Discovery Dynamics: Bütünleşik Analiz Planı

*Sürüm 1.0 · 2026-10-22 · İlk veri incelemesinden sonra yazıldı.*

Bu belge kapsamı, hipotezleri ve veri mimarisini somut bir iş planına bağlıyor. Belgede şunlar var:
- İlk incelemenin ortaya çıkardığı sorunlar
- Hangi analizin hangi veriye ihtiyaç duyduğu
- "Saçma sonuç" risklerine karşı alınan önlemler
- Adım adım yol haritası

Hipotezler (HIPOTEZLER.md) değişmedi. Burada sadece ölçüm ayrıntıları netleştirildi.

---

## 1. İlk incelemeden çıkan bulgular (2026-10-22)

| # | Bulgu | Neden önemli | Karar |
|---|---|---|---|
| B1 | FronkonGames 124.146 kayıt içeriyor; 2018–2025 arasında 106.459 kayıt var | Evren büyüklüğü yeterli | Evren listesi olarak kullanılır |
| B2 | **Kayıtların bir kısmı oyun değil.** 2025'ten rastgele seçilen 100 kayıtta 12 *Playtest* ve 3 *yazılım* çıktı. 2025 sayısı (24.973) sektör takipçilerinin saydığı ~20.300'den bu yüzden yüksek | Playtest'ler incelemesiz ve ücretsiz; filtrelenmezse "görünmez oyun" oranı yapay olarak şişer. **En büyük saçma sonuç riski buydu** | Tür bilgisi `IStoreBrowseService/GetItems` ile her kayıt için doğrulanır; sadece `type = 0` (oyun) kalır. Playtest'ler `parent_appid` ile ana oyuna bağlanır ve **yeni bir nitelik** türetilir: `playtest_var` |
| B3 | **Parquet dosyasında etiketler boş geliyor** (sütun tipi `list<null>`). JSON sürümünde etiket oyları var | Etiketler içerik analizinin temeli | Etiket ağırlıkları doğrudan Steam'den (GetItems, `tags.weight`) çekilir. 970 MB'lık JSON'u indirmeye gerek kalmadı |
| B4 | Set Şubat 2026'dan sonra yeni oyun eklemiyor (2026'da sadece 1.617 kayıt var) | Kohortumuz 2025'te bittiği için sorun değil. Ama setteki inceleme sayıları "ne zamanki" belli değil | Sonuç metrikleri setten alınmaz, Steam'den tarih damgalı olarak yeniden çekilir |
| B5 | `user_score` ve `score_rank` boş; Metacritic sadece %3,4 dolu; geliştirici/yayıncı/tür %7 boş | Bu alanlar analizde kullanılamaz | Kullanılmaz. Boş kayıtların çoğunun kaldırılmış ya da yayınlanmamış oyun olduğu tahmin ediliyor; GetItems ile kontrol edilecek |
| B6 | Kohortta oyunların %60,1'i 10'dan az, %93,9'u 500'den az inceleme almış (setteki toplam sayılara göre) | `hit` sınıfı yaklaşık %6. Model kurmak için yeterli ama dengesiz bir dağılım | Modellerde sınıf ağırlığı kullanılır; değerlendirme metriği PR-AUC olur |
| B7 | İnceleme grafiği uç noktası **ay ay** (genç oyunlarda **hafta hafta**) veri veriyor. Toplamı, Steam'den satın alınanların incelemelerine çok yakın; bütün incelemelerin %84–97'sini kapsıyor | `reviews_365` için tutarlı bir tanım sağlıyor | Birincil sonuç metriği bu uç noktadan hesaplanır: "Steam skoruna sayılan incelemeler". Tanım raporda açıkça yazılır |
| B8 | `GetItems` uç noktası 100 oyunu tek istekte yaklaşık 1 saniyede döndürüyor. Cevapta şunlar var: tür, gerçek çıkış tarihi, **Early Access başlangıç tarihi**, etiket ağırlıkları, geliştirici/yayıncı ve (oyunların ~%40'ında) bunların **sabit kimlik numaraları**, seri, inceleme özeti, fiyat | 106 bin oyun yaklaşık 20–30 dakikada çekilir. SteamSpy ile 30 saat sürecekti | **Omurga bu uç nokta oldu.** SteamSpy sadece çapraz doğrulama için kullanılır |
| B9 | Kaggle oyuncu sayısı setleri (lunthu: 6.729 oyun, kohortla örtüşen sadece 1.484; michau96: 2021'e kadar) büyük oyunlara odaklı ve lisansları belirsiz | Organik örneklemle örtüşmüyor | Sadece pazarın genel tablosunda kullanılır |

---

## 2. Güncellenmiş kaynak mimarisi

```
EVREN       FronkonGames appID listesi (124 bin)  ─┐
                                                  ├─► GetItems (tür, tarih, etiket ağırlıkları, stüdyo kimliği, fiyat, inceleme özeti)
SONUÇ       appreviewhistogram (aylık/haftalık inceleme serisi) ──► reviews_30/90/365, tail_share, yörüngeler
İÇERİK      IGDB (tema, mod, bakış açısı, motor, oynama süresi, stüdyo ülkesi)
OLAY        appreviews tek tek kayıtlar (M7 metin + M8 günlük sıçramalar; örneklem)
ÜRETİCİ     YouTube Data API + Twitch Clips (M8 örneklemi)
BAĞLAM      Kaggle Twitch ilk 200 + SteamCharts setleri (sadece genel pazar tablosu)
REFERANS    Steam indirim ve Next Fest tarihleri, büyük yayıncı listesi (elle derlenir, kaynaklı)
```

---

## 3. Veri ihtiyaç matrisi

Durum işaretleri: ✅ test edildi ve çalışıyor · 🔶 kaynağı belli, çekilecek · ⚠️ eksik veya dolaylı gösterge gerekiyor

| Modül / Hipotez | Gereken değişken | Kaynak | Durum |
|---|---|---|---|
| **Tümü: sonuç** | `reviews_30/90/365`, `positive_ratio`, `tail_share` | appreviewhistogram | ✅ |
| **Tümü: kohort** | Gerçek çıkış tarihi, uygulama türü, Early Access başlangıcı | GetItems `release`, `type` | ✅ |
| Organik örneklem (§3.2) | Geliştirici/yayıncı sabit kimlikleri, yayıncının o tarihe kadarki oyun sayısı | GetItems `basic_info` (kimlik numarası) + evren listesinden hesaplama | ✅ |
| Büyük yayıncı bayrağı | Büyük yayıncılar listesi | Elle derlenir + veriden kontrol (yayıncı başına oyun ve inceleme hacmi) | 🔶 |
| M1, H7 doygunluk | Etiket kombinasyonu, çıkış tarihi | GetItems etiketleri | ✅ |
| M2, H6 | Desteklenen diller (Basitleştirilmiş Çince) | GetItems `supported_languages` | ✅ |
| M2 içerik A–H | Etiket ağırlıkları + IGDB tema, mod, bakış açısı, motor | GetItems + IGDB | ✅ / 🔶 |
| M2 motivasyon | Etiket → 12 motivasyon eşlemesi | Elle hazırlanır; iki ayrı kodlayıcı ile uyum ölçülür (Cohen κ) | 🔶 |
| M3, H1 yenilik | Çıkıştan önce çıkmış oyunların etiket vektörleri | GetItems | ✅ (bkz. R4) |
| M4, H4 yörüngeler | Seri; Early Access giriş ve çıkış tarihleri | histogram + GetItems | ✅ |
| M5, H2 demo | Demo var mı ve **demo çıkış tarihi** | GetItems `related_items.demo_appid` → demonun appID'si → GetItems tarihi | ✅ (bkz. R13) |
| M5, H3 Next Fest | Katılım | **Resmi liste yok.** Dolaylı gösterge: demo bir Next Fest penceresinde yayında mıydı | ⚠️ |
| M5 (yeni) | Playtest var mı | GetItems `parent_appid` | ✅ |
| M6, H5 | Stüdyonun kaçıncı oyunu, önceki oyunun sonucu | Geliştirici kimliği + evren | ✅ |
| M7 | İnceleme metinleri | appreviews (organik örneklem, oyun başına üst sınırlı) | 🔶 |
| M8, H8 | Günlük inceleme serisi, video ve klip zamanları, kanal büyüklüğü | appreviews + YouTube + Twitch | ✅ (anahtarlar test edildi) |
| Kontrol: fiyat | Çıkış fiyatı | GetItems mevcut fiyat; çıkış fiyatı için eski anlık görüntüler veya IsThereAnyDeal (değerlendirilecek) | ⚠️ |
| Kontrol: zamanlama | İndirim ve Next Fest tarihleri | Elle derlenen tablo (Valve duyuruları, basın) | 🔶 |
| Kontrol: stüdyo ülkesi | Ülke | IGDB `companies.country` (kısmi) | 🔶 |

---

## 4. "Saçma sonuç" risk kaydı

Her risk için önlem ve sonucu nasıl kontrol edeceğimiz yazılı. Bu tablo veri raporuna da girecek.

| # | Risk | Ne olur | Önlem | Kontrol |
|---|---|---|---|---|
| R1 | **Oyun olmayan kayıtlar** (playtest, yazılım, demo) | "Oyunların %60'ı görünmez" gibi şişirilmiş bir sonuç çıkar | Sadece `type=0`; playtest'ler ayrı tutulur | Yıllık oyun sayısı, sektör takipçilerinin saydığıyla (~20 bin, 2025) %5 içinde tutarlı olmalı |
| R2 | **Sağdan sansür** (yakın tarihli oyunların gözlem süresi kısa) | Yeni oyunlar haksız yere "başarısız" görünür | `reviews_365` sadece en az 13 tam ay gözlenmiş oyunlarda hesaplanır | Çıkış ayına göre ortanca eğrilerin son aylarında çökme olmamalı |
| R3 | **Yıl etkisi / Simpson paradoksu** | Çıkan oyun sayısı yıllar içinde 2,5 kat arttı; başarı oranı her alt grupta yıla göre değişir | Tüm modellere çıkış yılı sabit etkisi; oranlar yıla göre normalize edilir | Ana bulgular yıl yıl ayrı ayrı da gösterilir |
| R4 | **Etiketlerin sonradan oluşması (ters nedensellik)** | Başarılı oyunlar daha çok oy ve daha spesifik etiket alır; yenilik ve doygunluk skorları başarının *sonucu* olabilir | Etiketler oy sayısına göre değil sırasına göre kullanılır (ilk 10, normalize). Duyarlılık analizi için geliştiricinin çıkışta seçtiği tür/kategori ve IGDB bilgileri kullanılır. Tahmin modelinde kullanıcı etiketi **kullanılmaz** | Yenilik skoru, inceleme sayısı 10–50 olan "az oylanmış" alt grupta da aynı yönde çıkmalı |
| R5 | **Seçilim yanlılığı (M5, M6)** | Demo yapan stüdyolar zaten daha iyi olabilir; ikinci oyun sadece ilki başarılı olanlarda çıkıyor olabilir | Propensity score matching + doubly robust tahmin, Rosenbaum Γ; M6'da ilk oyunun başarı kademesine göre tabakalama | Eşleştirme sonrası standartlaştırılmış ortalama farkı < 0,1; plasebo testi: demo *sonra* eklendiyse etki çıkmamalı |
| R6 | **Sızıntı (modelleme)** | Çıkıştan sonra oluşan bilgi modele girerse "çok iyi" ama sahte bir doğruluk çıkar | Özellik listesi "çıkış öncesi bilinebilir mi" sorusuna göre denetlenir; zamansal bölme (≤2023 eğitim / 2024–25 test) | Etiketsiz model ile tam model arasındaki fark raporlanır |
| R7 | **Seri üreticiler ve yapay zekâyla seri üretilmiş içerik** | Organik örneklemde binlerce "sıfır" birikir, oranlar çarpılır | `seri_uretici` bayrağı; analiz bu hesaplar dahil ve hariç olarak iki kez | İki sonuç aynı yönde olmalı |
| R8 | **İnceleme ≠ satış** | Türler arasında inceleme yazma eğilimi farklı (ör. F2P, yetişkin içerik) | Tür sabit etkisi; F2P ayrı analiz edilir; sonuçlar sıralama üzerinden yorumlanır | Bir alt örneklemde SteamSpy sahip aralıklarıyla sıra korelasyonu raporlanır |
| R9 | **Çoklu karşılaştırma ve keşif** | Çok sayıda kesitte rastgele "anlamlı" sonuç çıkar | Ön kayıt, Holm düzeltmesi, keşifsel bulgular ayrı etiketlenir | — |
| R10 | **Yayından kaldırılmış oyunlar** (survivorship'in kendisi) | Kaldırılan başarısız oyunlar görünmez olur, başarı oranı yükselir | Evren listesinde olup GetItems'ta görünmeyenler `kaldirilmis` olarak sayılır ve raporlanır | Yıl yıl kaldırılma oranı raporlanır |
| R11 | **Etki büyüklüğü yerine p-değerine bakmak** | Büyük örneklemde anlamsız küçük farklar "anlamlı" görünür | Her sonuç etki büyüklüğü ve güven aralığıyla verilir; pratik anlamlılık eşikleri önceden belirlenir | — |
| R13 | **Kaldırılmış demolar** | Çıkıştan sonra mağaza sayfasından kaldırılan demolar `demo_appid` alanında görünmez; demosu olan oyunlar "demosuz" sayılır, H2'nin etkisi olduğundan küçük çıkar | Demo uygulamalarının tam listesi (Steam API anahtarıyla uygulama listesi) üzerinden `parent_appid` eşlemesi denenecek; olmazsa ölçüm hatası yönü raporda belirtilir | Bilinen demolu çıkışlardan oluşan küçük bir doğrulama listesiyle isabet oranı ölçülür |
| R12 | **Kaynaklar arası tutarsızlık** | Sessiz bir çekim hatası sonucu bozar | Otomatik kontroller: histogram toplamı ile GetItems inceleme özeti oranı 0,95–1,30 arasında olmalı (pilotla kalibre edildi, bkz. PILOT_RAPORU.md) | Kontrol başarısızsa hat durur |

---

## 5. Pilot: önce 1.000 oyun

Tam çekimden önce, **yıl × başarı kademesi** tabakalarından seçilen 1.000 oyunla tüm hat baştan sona çalıştırılır. Pilotta kontrol edilecekler:

1. Çekici betikler hata, hız limiti ve kaldığı yerden devam etme senaryolarında doğru çalışıyor mu?
2. R1, R2, R10 ve R12 kontrolleri geçiyor mu?
3. Oyun türü dağılımı nasıl: playtest, yazılım ve kaldırılmış oyun oranları ne?
4. Organik örneklem tanımı kaç oyun bırakıyor? Hedef: kohortun en az %70'i.
5. Etiket ve IGDB eşleşme oranları ne? IGDB için hedef: inceleme sayısı ≥ 10 olan oyunlarda %60'ın üzeri.

Pilot raporu `docs/PILOT_RAPORU.md` dosyasına yazılır. Ancak bundan sonra tam çekime geçilir.

---

## 6. Yol haritası (Prepare + Process)

| Adım | Betik | Girdi → Çıktı | Tahmini süre |
|---|---|---|---|
| 1 | `00_indir.py`, `00b_indir_kaggle.py` | Açık setler → raw | ✅ Tamamlandı |
| 2 | `01_evren.py` | FronkonGames appID'leri → `interim/evren.parquet` | dakikalar |
| 3 | `02_getitems.py` | Evren → tür, tarih, etiket, stüdyo, fiyat | ✅ 2026-10-23: 124.146/124.146 kayıt + 15.633 demo uygulaması |
| 4 | `03_histogram.py` | Kohorttaki ve ömür boyu ≥10 incelemesi olan oyunlar → inceleme serileri | ~55,5 bin istek (GetItems sonrası kesin sayı), 4 paralel istekle (~11 istek/sn, 429 hatası yok) **~1,5 saat**. <10 incelemeli oyunlarda kademe (T0) ve hit=0 kesin; sürekli değer = ömür boyu toplam |
| 6 | `05_igdb.py` | Steam kimliği → IGDB içerik bilgileri | ✅ 2026-10-23: kohortta ≥10 incelemelilerin %94,7'si eşleşti; kalite: PILOT_RAPORU.md |
| 7 | `06_referans.py` | İndirim ve Next Fest tarihleri, büyük yayıncı listesi | Elle derleme + kaynak kaydı |
| 8 | `10_temizle_steam.py`, `11_sonuc.py` … `13_yayinla.py` | Temizlik T01–T15, sonuç metrikleri, öznitelikler, kontroller, DuckDB/Excel/rapor | 🔄 10 ✅, 11 yazıldı (yöntem doğrulandı, bkz. PILOT_RAPORU "Process 2"); 12–13 sırada |
| 9 | `07_inceleme.py`, `08_youtube.py`, `09_twitch.py` | M7 ve M8 örneklemleri | Analiz aşamasında |

**Çalıştırma ortamı:** Uzun çekimler senin Mac'inde arka planda (`caffeinate`) çalışır. Bütün çekiciler kaldığı yerden devam edebilir.

---

## 7. Açık konular

1. **Next Fest katılımı:** Resmi liste yok. Dolaylı gösterge, demonun bir Next Fest penceresinde yayında olup olmadığı. Bu göstergenin isabetini, basında yayımlanan Next Fest listeleriyle (ör. howtomarketagame analizleri) küçük bir örnek üzerinden doğrulamaya çalışacağız.
2. **Çıkış fiyatı:** IsThereAnyDeal API'sinin fiyat geçmişi ve kullanım şartları incelenecek. Uygun değilse, fiyat "mevcut fiyat" olarak kullanılır ve bu sınır raporda belirtilir.
3. **Steam API anahtarı:** Bu plan için zorunlu değil. Uygulama türlerinin tam listesine ihtiyaç olursa eklenir.
