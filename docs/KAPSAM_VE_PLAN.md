# Discovery Dynamics: Kapsam ve Plan

*Sürüm 1.0 · 2026-10-18*

## 1. Ana soru

> Büyük yayıncıların ve pazarlama bütçelerinin etkisi örneklemden ayrıldığında, bağımsız stüdyolar Steam'de organik görünürlüğe nasıl ulaşıyor? Hangi içerik, ticari ve zamanlama kararları bu olasılığı ölçülebilir biçimde değiştiriyor?

### Araştırma soruları

| # | Soru | Modül |
|---|---|---|
| S1 | Bir oyunun "görünür" olma olasılığı tür, fiyat, yıl ve stüdyo tipine göre nasıl değişiyor? | M1 |
| S2 | Hangi içerik bileşenleri (tür, mekanik, görsel, tema, oyuncu yapısı, motivasyon) başarıyla ilişkili? | M2 |
| S3 | "Tanıdık ama farklı" oyunlar, yani orta düzeyde yenilikçi olanlar, en iyi sonucu mu alıyor? | M3 |
| S4 | Oyunların inceleme eğrileri hangi tipik yörüngelere ayrılıyor ve bu yörüngeleri ne belirliyor? | M4 |
| S5 | Demo, Next Fest ve Early Access başarıyı nedensel olarak artırıyor mu? | M5 |
| S6 | Stüdyolar ikinci oyunlarında daha mı başarılı? | M6 |
| S7 | Oyuncular türlere göre neyi övüyor, neden şikâyet ediyor? | M7 |
| S8 | İçerik üreticisi etkisi: tek büyük kanal mı, çok sayıda küçük kanal mı daha kalıcı bir sıçrama yaratıyor? | M8 |

## 2. Kapsam

**Dahil:**
- Steam (PC) oyunları
- Analiz kohortu: 2018-01-01 ile 2025-12-31 arasında çıkan oyunlar
- 365 günlük sonuç metrikleri, en az 365 gün gözlem süresi olan oyunlar için hesaplanır

**Hariç:**
- Mobil (ileride ayrı proje)
- Konsol
- Canlı Twitch ve oyuncu sayısı takibi (kapsamdan çıkarıldı; yerine M8'deki YouTube ve Twitch klip olay analizi geldi)
- Oyun dışı uygulamalar: yazılım, film, soundtrack
- DLC
- Kaldırılmış oyunlar, betimsel istatistikte ayrıca raporlanır

**Kaynak politikası:** Ücretsiz olan ve kullanım şartları izin veren her kaynak kullanılır. Kullanım şartları veri çekmeyi açıkça yasaklayan siteler (ör. SteamDB) kullanılmaz; bu boşluk Kaggle ve Hugging Face'teki açık veri setleriyle doldurulur. Ham veri repoda paylaşılacağı için her kaynağın lisansı veri kataloğunda kayıt altına alınır.

## 3. Temel tanımlar

### 3.1 Başarı metrikleri

- **Birincil sonuç:** `reviews_365` — çıkıştan sonraki ilk 365 günde alınan inceleme sayısı. İnceleme zaman damgalarından hesaplanır.
- **Birincil ikili sonuç:** `hit` = `reviews_365 ≥ 500`.
- **Duyarlılık eşikleri:** 100 ve 1.000.

**İkincil sonuçlar:**
- `positive_ratio`: olumlu inceleme oranı
- `reviews_30`, `reviews_90`: 30 ve 90 günlük inceleme sayısı
- `tail_share`: 90. günden sonra gelen incelemelerin payı (uzun kuyruk göstergesi)
- `median_playtime_at_review`: inceleme anındaki ortanca oynama süresi (tutunma göstergesi)
- `est_revenue_range`: inceleme × 20–40 aralığı ile tahmini gelir. Sadece aralık olarak verilir, 50'den az incelemesi olan oyunlarda ve F2P oyunlarda hesaplanmaz.

**Başarı kademeleri (`reviews_365`):**

| Kademe | Aralık |
|---|---|
| T0 | < 10 |
| T1 | 10–99 |
| T2 | 100–499 |
| T3 | 500–4.999 |
| T4 | ≥ 5.000 |

### 3.2 "Organik örneklem" (pazarlama etkisinin ayrıştırılması)

Pazarlama bütçesi doğrudan gözlenemiyor, bu yüzden dolaylı göstergelerle (proxy) tanımlanır.

**Başlangıç kuralı:** Bir oyun, aşağıdaki iki koşulu birlikte sağlıyorsa organik örnekleme girer.
1. Geliştirici = yayıncı, **veya** yayıncının o tarihe kadar yayınladığı oyun sayısı ≤ 5.
2. Yayıncı, büyük yayıncılar listesinde değil (EA, Ubisoft, Tencent vb.; liste `docs/` altında tutulacak).

**Duyarlılık testi:** Yayıncı oyun eşiği 3 ve 10 alınarak tüm ana bulgular tekrar edilir.

**Sınır:** Pazarlama bütçesi gözlenmediği için bulgular "organik örneklemde ilişki" olarak raporlanır. Sadece M5'te nedensel iddia kurulur.

## 4. Veri kaynakları

| Kaynak | Ne sağlar | Erişim | Sınır / not |
|---|---|---|---|
| Steam `IStoreService/GetAppList` | Tüm uygulama listesi | Ücretsiz API anahtarı | — |
| Steam Store `appdetails` | Fiyat, tür, kategori, dil, platform, geliştirici/yayıncı, çıkış tarihi, demo, DLC, minimum gereksinimler | Herkese açık | Hız limiti yaklaşık 200 istek / 5 dk |
| Steam incelemeler (`appreviews`; yeni uç nokta `IUserReviewsService/GetAppReviews`) | Her inceleme: zaman damgası, olumlu/olumsuz, dil, inceleme anındaki oynama süresi, Early Access sırasında mı yazıldı, ücretsiz mi alındı, metin | Herkese açık, sayfalı | Büyük oyunlarda milyonlarca inceleme var; örnekleme ve sayfa limiti uygulanır |
| SteamSpy API | Kullanıcı etiketleri **ve oy sayıları**, sahip aralığı, ortanca oynama süresi | Herkese açık | Sahip sayısı sadece kaba aralık olarak verilir |
| IGDB API | Tema, oyun modu, oyuncu bakış açısı, anahtar kelimeler, oyun motoru, seri, şirketler, oynama süresi (`game_time_to_beats`) | Twitch geliştirici hesabı (ücretsiz) | Eşleştirme Steam AppID ile yapılır |
| YouTube Data API v3 | Video yayın tarihi, izlenme, kanal abone sayısı | Ücretsiz anahtar | Günlük 10.000 birim kota; arama başına 100 birim. Bu yüzden M8 örneklemle yapılır |
| FronkonGames Steam Games Dataset (Hugging Face / Kaggle) | Başlangıç verisi ve çapraz doğrulama (83 binden fazla oyun) | Açık | Anlık görüntü; tarihini kontrol et |
| PCGamingWiki Cargo API | Motor ve ara yazılım bilgisi (IGDB'de olmayanlar için) | Açık | Opsiyonel |
| Twitch Helix `Get Clips` | Oyun bazında, tarih aralığıyla filtrelenebilen klipler: oluşturulma zamanı, izlenme, yayıncı. Klipler kalıcı olduğu için geçmişe dönük Twitch sinyali sağlar | Twitch geliştirici hesabı | Klip sayısı yayın hacminin dolaylı göstergesidir |
| Twitch Helix `Get Videos` | Oyunun geçmiş yayın kayıtları (VOD) ve izlenmeleri | Twitch geliştirici hesabı | VOD'lar 7–60 gün saklanır; sadece yakın tarihli oyunlarda işe yarar |
| Kaggle / Hugging Face açık setleri | Oyuncu sayısı geçmişi, Twitch görüntülenme özetleri, hazır inceleme arşivleri vb. | Açık | Her setin lisansı, tarihi ve verinin asıl kaynağı veri kataloğunda tek tek kayda geçer |

**Doğrulanacaklar:**
- **Next Fest katılımı:** Doğrudan bir API'si yok. Katılım listesine erişilemezse H3 doğrulayıcı hipotezden keşifsel analize düşürülür.
- **Steam takipçi ve wishlist sayısı:** Resmi API'de yok. Kapsam dışı.

## 5. Nitelik sözlüğü

### 5.1 İçerik (8 boyut)

| Boyut | Örnek nitelikler | Kaynak |
|---|---|---|
| A. Tür hiyerarşisi | Üst tür, tür, alt tür; hibrit kombinasyon (ör. Roguelike + Deckbuilder) | Steam etiketleri, IGDB |
| B. Oynanış mekanikleri | Procedural generation, crafting, base building, permadeath, choices matter, turn-based / real-time | Steam etiketleri, IGDB anahtar kelimeleri |
| C. Görsel ve bakış açısı | 2D / 2.5D / 3D; top-down, izometrik, first-person, side-scroller; pixel, low-poly, hand-drawn, anime, realistic | Steam etiketleri, IGDB perspektif |
| D. Tema ve atmosfer | Sci-fi, fantasy, post-apocalyptic, historical; cozy, horror, funny, atmospheric | Steam etiketleri, IGDB tema |
| E. Oyuncu yapısı | Tek oyunculu, yerel co-op, çevrimiçi co-op (2–4 kişi), PvP, MMO; run-based / açık uçlu / lineer | Steam kategorileri, IGDB oyun modu |
| F. Kapsam ve derinlik | Oynama süresi, dosya boyutu, başarım sayısı, yeniden oynanabilirlik | IGDB, appdetails |
| G. Motivasyon profili | Quantic Foundry'nin 12 motivasyonuna etiketlerden eşlenmiş vektör: Fantasy, Story, Design, Discovery, Destruction, Excitement, Competition, Community, Challenge, Strategy, Completion, Power | Türetilmiş |
| H. Teknik ve erişim | Motor, Steam Deck uyumu, controller desteği, dil sayısı, Basitleştirilmiş Çince desteği, minimum donanım | appdetails, IGDB, PCGamingWiki |

**Türetilmiş içerik metrikleri:**
- **`tag_priority`:** Etiket oyu ÷ oyunun en çok oy alan etiketinin oyu (0–1 arası). Grelier & Kaufmann (2023) yöntemi.
- **`tag_idf`:** Etiketin nadirlik ağırlığı.
- **`novelty_score`:** Oyunun etiket vektörünün, çıkış tarihinden önceki oyunlar içinde en yakın k komşusuna ortalama kosinüs uzaklığı. Sadece o tarihe kadar çıkmış oyunlarla hesaplanır, böylece geleceğe ait bilgi sızmaz.
- **`saturation`:** Aynı etiket kombinasyonunda son 12 ayda çıkan oyun sayısı.
- **`opportunity_score`:** Talep, arz ve başarı oranı üzerinden TOPSIS ile hesaplanan fırsat skoru.

### 5.2 Stüdyo

- Geliştirici = yayıncı mı (`self_published`)
- Stüdyonun kaçıncı oyunu (`studio_title_index`)
- Önceki oyunun `reviews_365` değeri
- Stüdyo yaşı (ilk oyundan bu yana geçen süre)
- Yayıncının o tarihe kadarki oyun sayısı
- Büyük yayıncı bayrağı

### 5.3 Ticari

- Çıkış fiyatı (USD)
- F2P / B2P
- Çıkış indirimi
- Demo var mı
- Next Fest katılımı (doğrulanacak)
- Early Access: giriş tarihi, çıkış tarihi, süre
- DLC sayısı

### 5.4 Zamanlama

- Çıkış yılı, ayı, haftanın günü
- Aynı hafta çıkan oyun sayısı
- Aynı hafta büyük bir yayıncı çıkışı var mı
- Steam büyük indirim dönemine yakınlık

### 5.5 Sonuç

Bölüm 3.1'deki tüm metrikler, artı gün gün inceleme zaman serisi.

## 6. Analiz modülleri

| Modül | Yöntem | Çıktı | Landing bölümü |
|---|---|---|---|
| **M1: Survivorship** | Kademe dağılımları, segment bazında başarı oranları, lojistik regresyon | Başarı hunisi, segment ısı haritası | 1. Galaksi |
| **M2: İçerik DNA'sı** | Etiket taksonomisi, motivasyon eşlemesi, kısmi bağımlılık grafikleri | Motivasyon radarı, içerik etkileri | 2. Oyunun DNA'sı |
| **M3: Yenilik** | Kuadratik ve spline regresyon, Lind–Mehlum U testi | Ters U eğrisi, dönüm noktası | 3. Tanıdık ama farklı |
| **M4: Yörüngeler** | Normalize edilmiş inceleme eğrileri; DTW + k-medoids ya da fonksiyonel PCA; çok sınıflı model | 3–6 yörünge tipi ve belirleyicileri | 4. Yörüngeler |
| **M5: Nedensellik** | Propensity score matching + doubly robust tahmin; denge testleri; Rosenbaum duyarlılık analizi | ATT ve %95 güven aralığı, forest plot | 5. Neden-sonuç |
| **M6: Öğrenme eğrisi** | Stüdyo içi eşleştirilmiş karşılaştırma (Wilcoxon), sabit etkili model | 1. oyundan 2. oyuna değişim | 6. İkinci oyun |
| **M7: Oyuncu sesi** | LLM ile yön tabanlı duygu analizi (aspect-based sentiment), tema kümeleme, insan etiketli doğrulama örneği | Türe göre övgü ve şikâyet haritası | 7. Oyuncular ne diyor |
| **M8: İçerik üreticisi etkisi** | İnceleme sıçraması tespiti (change-point), YouTube videoları ve Twitch klipleriyle olay analizi, sıçrama sonrası kalıcılık | Makro ve mikro üretici karşılaştırması | 8. Üretici etkisi |
| **Model: Çıkış öncesi tahmin** | Gradient boosting; sadece çıkıştan önce bilinebilen nitelikler; zamansal doğrulama (eğitim ≤2023, test 2024–25); SHAP | `hit` olasılığı, nitelik katkıları | Explorer'ın motoru |

**İstatistik kuralları:**
- Doğrulayıcı hipotezlerde α = 0,05; çoklu karşılaştırma için Holm düzeltmesi uygulanır.
- Her bulgu etki büyüklüğü ve %95 güven aralığı ile raporlanır.
- Her ana bulgu için sağlamlık testi yapılır: başarı eşiği, organik örneklem tanımı ve yıl aralığı değiştirilerek.
- Ön kayıtta olmayan analizler "keşifsel" etiketiyle ayrı raporlanır.

## 7. Teslimatlar

1. **Araştırma reposu:** Kod, yöntem belgeleri (`docs/YONTEM_M*.md`), veri raporu (`docs/VERI_RAPORU.md`). Veri Excel ve SQL (DuckDB / SQLite) üzerinden gezilebilir olacak.
2. **Landing page:** design-kit site sistemiyle "Steam Galaksisi" hikâyesi. Etiket benzerliğine göre UMAP ile konumlanmış 3D nokta bulutu üzerinde, scroll ile ilerleyen 8 bölüm. Vercel'de yayınlanacak.
3. **Indie Opportunity Explorer:** Ayrı yayınlanan araç. Etiket kombinasyonu seçilir; fırsat skoru, benzer oyunlar ve tahmini başarı aralığı gösterilir.
4. **Pazar monitörü dashboard'u:** Tableau veya Power BI ile tür, fiyat, yıl ve stüdyo tipi kırılımları.

## 8. Yol haritası

| Faz | Adımlar | Tahmini süre |
|---|---|---|
| **0. Ask** | Kapsam, tanımlar, ön kayıtlı hipotezler | ✅ |
| **1. Prepare** | API anahtarları; uygulama listesi; appdetails, SteamSpy ve IGDB çekimi; inceleme zaman damgaları; ham veri kataloğu | 1–2 hafta |
| **2. Process** | Temizleme, eşleştirme (AppID ↔ IGDB), organik örneklem, öznitelik üretimi, veri raporu, Excel/SQL dışa aktarım | 1–2 hafta |
| **3. Analyze** | M1 → M2 → M3 → M4 → M6 → M5 → M7 → M8, tahmin modeli | 3–4 hafta |
| **4. Share** | Landing page, Explorer, dashboard | 2–3 hafta |
| **5. Act** | Bağımsız stüdyolar için öneri raporu; LinkedIn yazı dizisi | 1 hafta |

## 9. Riskler

| Risk | Önlem |
|---|---|
| İnceleme çekimi çok uzun sürer (büyük oyunlarda milyonlarca inceleme) | Organik örneklemde tam çekim; büyük oyunlarda sadece özet sayılar ve tarih dağılımı |
| İnceleme sayısı satışların gürültülü bir göstergesi | Ana metrik sıralama (ordinal) bazında yorumlanır; gelir sadece aralık olarak verilir |
| Etiketler oyuncular tarafından sonradan değişiyor (tahmin modelinde bilgi sızıntısı) | Tahmin modelinde sadece geliştiricinin çıkışta belirttiği türler ve kategoriler kullanılır; etiket tabanlı analizler betimsel olarak raporlanır |
| Next Fest verisi bulunamaz | H3 keşifsel analize düşürülür |
| YouTube kotası | M8 tabakalı örnekleme ile 300–500 oyunla sınırlandırılır |
