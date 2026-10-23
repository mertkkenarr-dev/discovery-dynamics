# Pilot Raporu: 1.000 oyun

*2026-10-22 · Betikler: `01_evren.py`, `02_getitems.py`, `03_histogram.py`, `p01_pilot_ozet.py`*

**Kapsam notu:** Bu rapor sadece veri yapısını ve kalitesini inceliyor. Nitelikler ile başarı arasındaki ilişkilere bakılmadı, çünkü hipotezler kilitli.

## Örneklem

- Evrenden (FronkonGames, 124.146 kayıt) 2018–2025 arası çıkış yılı × 5 başarı kademesi = 40 tabaka oluşturuldu. Her tabakadan 25 oyun seçildi, toplam 1.000 oyun (tohum 20261022).
- Kademeler setteki inceleme sayısına göre belirlendi; bu sayı sadece tabakalama için kullanıldı.
- Örneklem eşit tabakalı olduğu için oran tahminleri tabaka büyüklükleriyle **ağırlıklandırıldı**.

## Sonuçlar

| Kontrol | Sonuç | Yorum / Karar |
|---|---|---|
| GetItems başarı oranı | 999/1.000 başarılı, 1 kayıt kaldırılmış | Çekim sorunsuz; 100 uygulama ≈ 1 saniye |
| **Oyun dışı kayıtlar (R1)** | Ağırlıklı **%8,8**: Playtest %7,5, yazılım %1,3. Yıllara göre %3–15 (2022'de %14,9, 2025'te %14,0) | **Doğrulandı.** Filtrelenmeseydi görünmez oyun oranı şişecek ve yıllar arası karşılaştırma bozulacaktı. `type = 0` filtresi zorunlu |
| Çıkış yılı (set ve Steam karşılaştırması) | %98,9 uyumlu | Set tarihi güvenilir; yine de Steam tarihi kullanılır |
| Stüdyo sabit kimliği | Oyunların sadece **%39,8'inde** var | ANALIZ_PLANI B8'deki "stüdyo adı sorunu kendiliğinden çözülüyor" beklentisi **kısmen doğru çıktı**. Kimlik varsa kimlik, yoksa normalize edilmiş ad kullanılır (T04 hâlâ gerekli) |
| Geliştirici = yayıncı | %59,6 | Organik örneklemin büyük kısmı bu kuraldan geliyor |
| Early Access ile başlamış | %14,2 (şu an hâlâ EA: %7,0) | H4 için yeterli örnek var |
| Mağazada görünen demo | %14,6 | Kaldırılmış demolar (R13) nedeniyle gerçek oranın altında |
| Etiket sayısı | Ortanca 20 | Etiket verisi tam |
| Basitleştirilmiş Çince desteği | %50,9 (ağırlıksız) | Beklenenden yüksek. Dil kodu eşlemesi (`elanguage = 6`) Process aşamasında bilinen oyunlarla doğrulanacak |
| İnceleme grafiği | 963/963 başarılı; 761 oyunda aylık, 202 oyunda haftalık seri | Tüm oyunlar için seri var |
| **Kaynaklar arası tutarlılık (R12)** | Grafik toplamı ÷ GetItems özet sayısı: ortanca **1,05**; %10–90 aralığı 1,00–1,17 | Grafik, özetten biraz fazla sayıyor (özet bazı incelemeleri filtreliyor). Plandaki kontrol aralığı (0,8–1,05) **gerçekçi değildi**; pilot dağılımına göre **0,95–1,30** olarak güncellendi |
| Gözlem süresi (R2) | %97,7'si 13 aydan uzun gözlenmiş; 2025 çıkışlılarda %89,7 | Eylül 2025 sonrası çıkışlar `reviews_365` için dışarıda kalır |
| `reviews_365` kademeleri (ağırlıklı) | T0 %49,4 · T1 %35,0 · T2 %8,8 · T3 %6,0 · T4 %0,8 | Her iki oyundan biri ilk yılında 10'dan az inceleme alıyor. `hit` oranı yıllara göre %4–10 arasında değişiyor; R3'teki yıl kontrolünün gerekli olduğunu gösteriyor |
| Hız | Grafik uç noktası ~0,8 sn/istek | Tam kohort (~97 bin oyun) yaklaşık **21–22 saat** sürer |

## Yeni sınırlar ve kararlar

1. **Evrenin kendisinde survivorship var (R10).** FronkonGames'te kaldırılmış oyunlar neredeyse hiç yok (pilotta 1/1.000). Setin toplamaya başlamasından önce kaldırılan oyunlar evrende hiç görünmüyor. Bunu ölçmek için yıllık oyun sayıları sektör takipçilerinin sayılarıyla karşılaştırılacak (2025: set 24.973 × %86 oyun payı ≈ 21,5 bin; takipçiler 20,0–20,5 bin). Fark raporda "evren kapsama oranı" olarak verilecek.
2. **R12 kontrol aralığı:** 0,95–1,30 (pilot dağılımından kalibre edildi).
3. **Stüdyo kimliği:** Kimlik + ad normalizasyonu birlikte kullanılacak.
4. **Uzun çekimlerin yeri:** Çalışma ortamımdaki komutlar 3 dakikayla sınırlı ve arka planda bırakılan işler sonlanıyor. Tam kohort çekimi (~22 saat) **senin Mac'inde Terminal'den** çalıştırılacak. Betikler kaldığı yerden devam ettiği için Mac uyusa da sorun olmuyor.

## Sonraki adımlar

1. GetItems'ı tüm evren için çalıştırmak (~20 dk, burada yapılabilir) + demo uygulamaları
2. İnceleme grafiklerini tam kohort için çekmek (Mac'te, ~22 saat)
3. IGDB eşleştirmesi (~1 saat)
4. Referans tabloları: indirim ve Next Fest tarihleri, büyük yayıncı listesi

## Ek: Tam evren GetItems çekimi (2026-10-23)

- **Kapsama:** 124.146/124.146 kayıt çekildi; tekrar eden kayıt yok, dosya bütünlüğü kontrol edildi.
- **Başarısız kayıtlar:** 297 kayıt kaldırılmış ya da erişilemiyor (`success = 15`), 3 kayıt dönmedi. Toplam %0,24; bunlar `kaldirilmis` olarak işaretlenecek.
- **Uygulama türü:** oyun 113.599 · Playtest 8.262 · yazılım 1.872 · diğer 113.
- **R1 kontrolü geçti.** Oyun filtresinden sonra 2025 çıkışlı oyun sayısı **20.808**; sektör takipçileri 20.008–20.558 sayıyor. Filtre öncesi setteki sayı 24.973'tü.
- **Kohort:** 2018–2025 arasında çıkan 95.473 oyun. Bunların **55.512**'sinin ömür boyu en az 10 incelemesi var; inceleme grafiği bu oyunlar için çekilecek.
- **Mağazada görünen demo oranı:** %14,0.
- **Demolar:** 15.633 demo uygulaması çekildi (hepsi `type = 1`). 15.623'ünde ana oyun bağlantısı var; demo çıkış tarihleri bu kayıtlardan alınacak.

## Ek: IGDB eşleştirmesi (2026-10-23)

*Betikler: `05_igdb.py` (çekim), `p02_igdb_kalite.py` (bu tablo). Sadece veri kalitesi; başarı ile ilişkiye bakılmadı.*

- **API notu:** IGDB 2025'te `external_games.category` alanını kaldırdı; eşleştirme `external_game_source = 1` (Steam) ile yapılıyor. Eski alanla yazılmış bir sorgu hata vermeden sıfır sonuç döndürürdü.
- **Çekim:** 179.359 Steam bağlantısının tamamı (IGDB sayımıyla birebir), 104.518 oyun kaydı (16'sı dönmedi), oynama süresi, 75.224 şirket ilişkisi, 27.972 şirket, sözlükler.

| Kontrol | Sonuç | Karar |
|---|---|---|
| Kapsama: kohort, inceleme ≥ 10 | **%94,7** (hedef > %60) | Yeterli |
| Kapsama: yıllara göre | 2018 %99,4 → 2025 %80,9 | Eksiklik yıla bağlı (yeni oyunlar IGDB'ye geç giriyor). Yıl kontrolü ile ele alınır, raporda belirtilir |
| appID → birden fazla IGDB oyunu | 0 | Temiz |
| IGDB oyunu → birden fazla appID | 128 oyun / 257 appID | Aynı oyunun farklı Steam sürümleri; nitelikler her appID'ye kopyalanır |
| IGDB türü ana oyun değil | ~2.300 (remaster 520, genişletilmiş 485, paket 359, port 353, remake 328…) | Yeni nitelik `igdb_tur`; ilk çıkış olmayanlar Process'te bayraklanır |
| IGDB ilk çıkışı Steam'den > 1 yıl önce | %6,2 | Yeni nitelik `steam_oncesi_cikis`: oyun Steam'e başka platformdan "tanınmış" geliyor olabilir |
| Alan doluluğu (kohort, ana oyun) | tür %95,9 · mod %99,8 · tema %63,5 · motor %48,9 · bakış açısı %39,3 · anahtar kelime %38,8 · oynama süresi **%3,5** · geliştirici ülkesi **%15,0** | Oynama süresi ve ülke analizde kullanılmaz (F boyutu için Steam başarım sayısı / dosya boyutu değerlendirilecek). Seyrek alanlarda `NULL` ≠ `0` (T13); eksikliğin başarı kademesine bağlı olup olmadığı Process'te test edilir |

## Ek: Çıkış tarihi tanımı düzeltildi (2026-10-23)

**Sorun:** Kohort ve `reviews_365`'in sıfır noktası `steam_release_date` ile tanımlanmıştı. Early Access geçmişi bilinen oyunlarla yapılan testte bu alanın EA'dan çıkmış oyunlarda **tam sürüm** tarihi olduğu görüldü. EA başlangıcı ise `original_steam_release_date` alanında duruyor.

| Oyun | `steam_release_date` | `original_steam_release_date` | Gerçek |
|---|---|---|---|
| Slay the Spire | 2019-01-23 | 2017-11-15 | Steam EA 2017-11 ✔ |
| Hades | 2020-09-17 | 2019-12-10 | Steam EA 2019-12 (Epic'te 2018) ✔ |
| Vampire Survivors | 2022-10-20 | 2021-12-17 | Steam EA 2021-12 ✔ |
| Valheim | 2026-09-09 | 2021-02-02 | Steam EA 2021-02 ✔ |

**Karar:** Çıkış tarihi = **ilk Steam erişimi** = min(`steam_release_date`, `original_steam_release_date`); 1990 öncesi değerler geçersiz (`ortak.ilk_steam_erisimi`). Gerekçe: incelemeler EA ile birlikte gelmeye başlıyor; tam sürüm tarihinden saymak EA oyunlarının ilk yılını yok sayar ve H4'ü (EA ile uzun kuyruk) yanlı hale getirir.

**Etki:** Kohort 95.473 → **95.706**. 833 oyun giriyor (Valheim gibi EA'dan 2025 sonrasında çıkmış oyunlar; 564'ünde en az 10 inceleme var, histogram'ları ek olarak çekilecek). 600 oyun çıkıyor (Steam'e 2018'den önce EA ile gelmiş olanlar). Kohortta en az 10 incelemesi olan oyun sayısı: **55.563**.

**Kalan sınır:** EA geçmişi her zaman kayıtlı değil. Örneğin Baldur's Gate 3'te `original_steam_release_date` boş, oysa 2020'de EA'ya girmişti. Bu oyunlar, histogram'da çıkış tarihinden önce inceleme bulunmasıyla tespit edilecek (temizlik kuralı T14).

**`original_release_date` kullanılmaz:** Dolu olan kayıtların çeyreği 1970'lere düşüyor (yer tutucu). Başka platformda önceden çıkış bilgisi IGDB'den alınıyor (`steam_oncesi_cikis`).

## Process 1: Steam meta verisi temizliği (2026-10-23)

*Betik: `10_temizle_steam.py`. Kararlar `data/interim/meta_karar.parquet` tablosunda. Sayılar kohort (95.706 oyun) üzerinden, aksi belirtilmedikçe.*

| Kod | Sorun | Etkilenen | Karar |
|---|---|---|---|
| T09 | GetItems'ta kaldırılmış / erişilemeyen | 300 / 124.146 evren | `kaldirilmis.parquet`'e ayrılır |
| T01 | Evrende oyun dışı kayıt (playtest 8.262, yazılım 1.872, DLC 112, mod 1) | 10.247 / 124.146 | Sadece `type=0`; demo ve playtest'ler ana oyuna nitelik olur |
| T02 | Geçerli tarih yok (boş / 1970 yer tutucu) · henüz çıkmamış | 35 · 2 / 113.599 | `NULL`, kohort dışı |
| T02c | EA'dan çıkmış oyunda `steam_release_date` tam sürüm tarihi | 7.358 / 113.599 | `ilk_cikis` = ilk Steam erişimi |
| T03 | Ücretli ama satın alma seçeneği yok | 1.195 | Fiyat `NULL` (0 değil) |
| T03b | Çekim anında indirimde | 8.220 / 113.599 | İndirimsiz liste fiyatı; "mevcut liste fiyatı" olarak etiketli |
| T04 | Kimliksiz stüdyo adlarında yazım farkı | 68.637 → 66.685 farklı ad | Unicode, büyük/küçük harf, noktalama, yasal ek temizliği |
| T04b | Kimliksiz satırın normalize adı tek bir kimlikle eşleşiyor | 9.717 satır | O kimliğe bağlanır |
| T05 | Seri üretici: bir yılda > 12 oyun (140 geliştirici) | 6.465 (%6,8) | Bayrak; analiz dahil/hariç |
| T06 | Yetişkin cinsel içerik (Steam içerik kimliği 3/4) | 6.776 (%7,1) | Bayrak; ana analiz hariç |
| T15 | Listelenmemiş oyun | 1.069 (%1,1) | Bayrak; duyarlılıkta hariç |
| T13 | Hiç etiketi yok | 32 | `n_etiket = 0` |

**T05 eşiği nasıl seçildi:** Seçimde sadece üretim hacmine bakıldı, başarıya bakılmadı. Geliştiricinin en yoğun yılındaki oyun sayısı dağılımı: ortanca 1, %99'luk dilim 4, %99,9'luk dilim 18, en fazla 135. Eşik "ayda birden fazla oyun" (> 12/yıl) olarak seçildi; gerçekçi bir bağımsız geliştirme temposunun belirgin biçimde üstünde. Eşik adayları (geliştirici / kohort oyunu): > 4: 731 / 13.491 · > 6: 387 / 10.191 · > 8: 257 / 8.535 · **> 12: 140 / 6.465** · > 20: 63 / 4.426. En büyük 10 seri üreticinin 8'i yetişkin ya da şablon içerik hesabı; diğerleri casual "fabrika" stüdyolar (Elephant Games, Creobit). Bayrak niyeti değil hacmi ölçer.

**Örnek kontrolleri:**
- Stüdyo birleşmeleri doğru ('Sickhead Games, LLC' = 'Sickhead Games'; 'NEXION X INC.' = 'NEXION X'). **Sınır:** Steam'in sabit kimliği bazen bir yayın etiketini temsil ediyor; Targem Games ile yayıncılık kolu Star Gem aynı kimliği paylaşıyor. Birden fazla yazımı olan anahtar sayısı: 3.035.
- `elanguage = 6` = Basitleştirilmiş Çince: FronkonGames'in metin dil listesiyle **%99,3 uyum**. Diğer kodlar Steam'in dil numaralandırmasıyla tutarlı (Almanca 1, Geleneksel Çince 7, Rusça 8, Japonca 10). Kohortta Çince desteği %32,3 (pilottaki %50,9 tabakalı örneklemden geliyordu).

## Process 2: Sonuç metrikleri (2026-10-23)

*Betik: `11_sonuc.py`. Çıktılar: `interim/sonuc.parquet`, `interim/inceleme_seri.parquet`.*

**Pencere hesabı.** Histogram eski oyunlarda aylık, yeni oyunlarda haftalık kova veriyor; gün bazlı veri yok. Çıkışın düştüğü kova çıkış gününden başlatılır (çıkıştan önce inceleme olmaz). Pencere sınırındaki kova gün oranıyla bölünür. `reviews_N` sadece sınır kovası tamamen gözlenmişse hesaplanır (R2).

**Yöntem doğrulaması.** Haftalık verisi olan ve 365 günü tam gözlenen 4.477 oyunun haftaları aylara toplanıp aynı yöntem uygulandı; sonuç gerçek (haftalık) değerle karşılaştırıldı:

| Metrik | Göreli hata, ortanca | Mutlak hata, %50 | Mutlak hata, %90 |
|---|---|---|---|
| `reviews_365` | %0,0 | %0,1 | %1,9 |
| `reviews_90` | +%0,2 | %0,8 | %4,2 |
| `reviews_30` | %0,0 | %2,0 | %7,6 |

`hit` sınıfı %99,98 uyumlu (4.477 oyunda 1 ayrışma). **Birincil sonuç güvenilir; `reviews_30` aylık oyunlarda gürültülü.** `cozunurluk` sütunu analizde kontrol olarak kullanılabilir.

**Tanımlar:**
- `tail_share` = (r365 − r90) / r365, yani **ilk yıl içindeki** 90 gün sonrası pay. Ömür boyu oran oyunun yaşına bağlı olurdu.
- Kademe ve hit, yuvarlanmış `reviews_365` üzerinden hesaplanır (sınır kovası kesirli pay verir).
- < 10 inceleme: `reviews_365` = ömür boyu sayı (üst sınır), en az 396 gün gözlenmişse.

**T14: Steam yeniden yayında tarihi sıfırlıyor.** Çıkış ayından önce ≥ 10 inceleme bulunan oyunlar incelendi. Bunlar sadece kayıtsız EA'lar değil, yeniden yayınlanmış eski oyunlar da (Rust: Steam tarihi 2018, gerçekte 2013; GTA IV Complete: 2020, gerçekte 2008). Histogram'ın `start_date` alanının **ilk inceleme günü** olduğu doğrulandı: normal oyunlarda Steam tarihine farkın ortancası −1 gün, %95'i 4 gün içinde.
**Karar:** Bu oyunlarda `ilk_cikis` = ilk inceleme günü (`ilk_cikis_kaynagi = 'ilk_inceleme'`); pencereler ve kohort yeni tarihle hesaplanır. Doğrulama: Satisfactory → 2020-06-08, The Outlast Trials → 2023-05-18, Gunfire Reborn → 2020-05-22 (hepsi gerçek EA başlangıçları). Rust ve GTA IV kohorttan çıkar.
**Ters yön de var:** Tarihi 2026'ya sıfırlanmış 874 oyun (≥ 10 inceleme) kohort dışında kalıyordu. Örnekler: Enshrouded (EA 2024), Microsoft Flight Simulator 2020, RuneScape: Dragonwilds (EA 2025), Soulmask, GROUND BRANCH. **Karar:** Histogram hedef listesinin üst sınırı kaldırıldı; kohort `11_sonuc.py`'de düzeltilmiş tarihle belirlenir. Alt sınır güvenli, çünkü düzeltme tarihi sadece geriye çeker.

## Referans tabloları (2026-10-23)

Elle derlenir, her satır kaynaklıdır, `data/referans/` altında durur ve repoya girer (ham veri değil, küçük ve kaynaklı).

### `steam_etkinlik.csv`: 49 etkinlik

- **Demo festivalleri ve Next Fest:** Aralık 2019'daki The Game Festival'dan Ekim 2026'ya kadar 22 edisyon.
- **Büyük indirimler:** 2018–2025 arası 27 dönem (yaz, sonbahar, kış; 2023'ten itibaren bahar).
- **Doğrulama düzeyi:** 11 satır Valve'ın kendisi, 35 satır birden fazla basın kaynağı, **3 satır tek kaynak** (2018 sonbahar ve kış indirimleri sızıntıya dayalı; 2022 yaz indirimi önceki yıllardan tahmin). Bu üçünü kullanan analizler duyarlılık testinde bu satırlar hariç tekrarlanır.
- **Çözülen çelişkiler:**
  - Haziran 2020 festivali 9–14 Haziran'dan 16–22 Haziran'a ertelenmişti. Tek bir kaynak eski tarihi veriyordu.
  - Şubat 2026 Next Fest: bir izleme aracı 24 Şubat diyordu, Valve takvimi 23 Şubat.
  - Yaz 2024 indirimi: bir tablo 28 Haziran diyordu, Valve 27 Haziran.
- **Kaynak politikası:** SteamDB, kullanım şartları nedeniyle kaynak olarak kullanılmadı.

### `buyuk_yayinci.csv`: 35 şirket grubu

- **Ölçüt (sonuca bakılmadan, şirket büyüklüğüne göre):** [Wikipedia "gelire göre en büyük 50 oyun şirketi"](https://en.wikipedia.org/wiki/List_of_largest_video_game_companies_by_revenue) ∪ kohort yıllarından birinde oyun geliri ≥ 500 milyon USD olan şirketler. Bu ikinci koşulla CD Projekt (2020: ~561 milyon USD) ve Warner Bros. Games (geliri ayrı raporlanmıyor; doğrulama dolaylı) eklendi.
- Her grup için Steam'deki yayın etiketlerini yakalayan kesin eşleşme deseni var. Bağımsız oyun etiketleri de dahil: EA Originals, Private Division, Epic Games Publishing, Square Enix Collective, Smilegate STOVE. Gerekçe: bunların arkasında büyük şirket pazarlaması var.
- **Kontrol:** Anahtar kelime içeren ama desene uymayan 24 yayıncı adı tek tek incelendi. 14'ü eklendi (bölge, alt etiket ve yazım varyantları). 10'u reddedildi; örneğin "Sony" adıyla yayın yapan iki ilgisiz bağımsız hesap ve Sony Pictures VR. Desenlerin kesin eşleşme olması bu tür yanlış pozitifleri önlüyor.
- **Sonuç:** 995 kohort oyunu büyük yayıncı etiketi taşıyor. miHoYo, Garena ve NetDragon'un Steam'de kohort oyunu yok.
- **Sınır:** Sahiplik bugünkü (2026) duruma göre. Embracer 2024'te Saber ve Gearbox'tan ayrıldı; Activision Blizzard 2023'ten önce bağımsızdı ama zaten ilk 50'deydi. Yıl bazlı sahiplik ayrıntısına girilmedi.

### Process 2: tam veri sonuçları (2026-10-23)

- **Histogram çekimi:** 57.107 kayıt, hepsi `success = 1`, tekrar eden appID yok. Sonuç metriği için gereken ama histogram'ı eksik oyun sayısı 0 (S02).
- **Kesin kohort: 95.647 oyun.** Tanım düzeltmesi öncesi 95.706'ydı. T14 düzeltmesiyle 149 oyun çıktı (gerçek çıkış 2018 öncesi), 90 oyun girdi (tarihi 2026'ya sıfırlanmış). Toplam 808 kohort oyununun tarihi ilk inceleme gününe çekildi; Baldur's Gate 3 → 2020-10-06 ve Enshrouded → 2024-01-24, gerçek EA başlangıçlarıyla aynı.
- **Sonuç kaynağı:** 55.651 oyun histogram'dan, 39.996 oyun ömür boyu sayının üst sınırından (< 10 inceleme).
- **`reviews_365` dolu: %91,5.** Yıllara göre 2018–2023 arası %98,8–99,7; 2024'te %97,3; 2025'te **%64,3**. Ekim 2026 çekiminde 2025 sonu çıkışlıların 365 günü henüz dolmadı (R2). 2025 kohortu kısmi; ana bulgular 2018–2024 ile de tekrarlanacak.
- **R12:** Oran ortancası 1,058, %10–90 aralığı 1,00–1,18. Pilotla aynı. Aralık dışı 1.423 oyun (%2,5) `r12_uyumsuz` bayrağı taşıyor.
- **Bütünlük kontrolleri:** Negatif değer yok. r30 ≤ r90 ≤ r365 ≤ ömür boyu sıralaması her oyunda tutuyor. Oranlar [0,1] içinde. Kademe ile hit tutarlı.
- **Betimsel dağılım** (kohort, `reviews_365` dolu): T0 %50,5 · T1 %33,1 · T2 %10,0 · T3 %5,3 · T4 %1,2. **Hit oranı %6,5.** Hipotez testi değil, sadece sonuç dağılımı.
- **Not:** `11_sonuc.py` oyun başına pandas işlemleri yaptığı için yavaş (yarım veride ~50 sn). Hat sık çalıştırılacaksa vektörleştirilmeli.

## Process 3: Otomatik kontroller (2026-10-23)

*Betik: `12_kontrol.py`. Sonuçlar `interim/meta_kontrol.parquet` tablosunda. Kritik kontrol başarısızsa betik çıkış kodu 1 verir ve hat durur.*

İlk çalıştırmada hat **durdu** ve iki gerçek sorun yakaladı:

| Kod | Sorun | Etkilenen | Karar |
|---|---|---|---|
| T16 | Dil tablosunda (oyun, dil) tekrarı: 147.045 satır. **Neden:** Steam'de `elanguage = -1` olan satırlarda dil `eadditionallanguage` alanında ve bu ayrı bir numaralandırma (oradaki 6 Çince değil). Hepsi aynı dil sayılıyordu, `n_dil` şişiyordu | 147.045 → 0 | Dil anahtarı = `elanguage` (≥ 0) ya da 100 + `eadditionallanguage`. `n_dil` yalnızca Steam ana dillerini sayar, ek diller `n_ek_dil`'de. Çince bayrağı etkilenmedi (yalnızca `elanguage = 6`'ya bakıyordu) |
| T17 | **Dil spam'i:** 72 ek dilin hepsini iddia eden 1.978 oyun. Ek dil sayısı dağılımı iki tepeli: gerçek yerelleştirme 0–20, 20–40 arası neredeyse boş, 72'de yığılma | 1.918 kohort oyunu (%2,0) | `dil_spam` bayrağı (≥ 40 ek dil; eşik `config.yaml`'da) |
| T04d | Aynı oyunda aynı stüdyo aynı rolde birden fazla satır (LucasArts + Lucasfilm aynı kimlik; Aspyr (Mac) + Aspyr (Linux)) | 1.447 satır | Tek satır; adlar birleşir. Stüdyo başına oyun sayısı iki kez saymaz |

**Düzeltmeden sonra: 32 / 32 kontrol geçti.**
- Anahtar benzersizliği: 7 tablo.
- Köprü bütünlüğü: 7 ilişki, yetim kayıt yok.
- Aralıklar: fiyat, oranlar, `tag_priority`, r30 ≤ r90 ≤ r365 ≤ ömür boyu, kademe ↔ hit.
- Tarihler: çekimden sonra çıkış yok; tam sürüm ilk erişimden önce değil; kısa gözlenip sonuç verilmiş oyun yok.
- R1: 2025 oyun sayısı 20.363, takipçi aralığı içinde.
- R12: uyumsuzluk %2,5 (≤ %5).
- Kapsama: histogram eksiği 0; IGDB %94,7; `reviews_365` doluluğu %91,5.

## R8: İnceleme sayısı satışın vekili olarak (2026-10-23)

Steam satış veya indirme sayısı yayınlamıyor. Tek açık tahmin SteamSpy'ın sahip aralıkları (FronkonGames'te `estimated_owners`). Kohortta:
- Oyunların **%83'ü aynı en alt aralıkta** ("0–20 bin"), 12.839'u "0–0". Ayırt edici değil; birincil metrik olamaz.
- Ayırt edilebilen 16.299 oyunda ömür boyu inceleme ile sahip aralığı arasındaki **Spearman sıra korelasyonu 0,585**. İnceleme ile eşzamanlı oyuncu zirvesi arasında 0,698 (n = 14.002).
- Sahip aralığına göre ortanca inceleme monoton artıyor: 11 → 41 → 234 → 941 → 3.029 → 9.700 → 23.000 → 70.000 → … (tek istisna: birkaç oyunluk 50–100 milyon aralığı).

**Sonuç:** İnceleme sayısı satışın sırasını iyi izliyor ve zaman damgalı tek sinyal. Ana metrik `reviews_365` olarak kalır, sonuçlar sıralama üzerinden yorumlanır, tür kontrolü kullanılır, gelir yalnızca aralık olarak verilir (KAPSAM §3.1).

## Process 4: Türetilmiş nitelikler (2026-10-23)

*Betik: `11b_oznitelik.py` → `interim/oznitelik.parquet` (113.564 oyun, 60 sütun), `interim/studyo_oyun.parquet`.*

**Sızıntı kuralı (R6):** Her nitelik çıkış anında bilinebilir olmalı. "Önceki oyun" sayımları yalnızca kesin olarak daha önce çıkan oyunları sayar (aynı gün sayılmaz). Tarih olarak T14 ile düzeltilmiş çıkış kullanılır.

| Kod | Nitelik | Kohort sonucu |
|---|---|---|
| N01 | Yayıncı bilgisi yok | 313 (%0,3) → organik = False |
| N02 | **Organik örneklem** (kendi yayını veya yayıncının önceki oyunu ≤ 5, ve büyük yayıncı değil) | **84.131 (%88,0)**; duyarlılık ≤ 3: 83.006, ≤ 10: 85.913. Hedef (≥ %70) karşılandı |
| N03 | Kendi yayını ama büyük yayıncı | 356 → organik dışı |
| N04 | Demo çıkıştan önce yayında | 10.267 (%10,7). R13: kaldırılmış demolar görünmez |
| N05 | Next Fest dolaylı göstergesi | Aralık 2019 sonrası çıkan 81.455 oyunun 8.071'i (%9,9) |
| N06 | Steam'den 1 yıldan fazla önce başka platformda çıkmış (IGDB) | 3.357 (%3,5) |

**Büyük yayıncı listesi tarihe duyarlı hale getirildi.** Organik sayılan en çok incelenen oyunlara bakılarak (analiz planındaki "veriden kontrol" adımı) üç eksik bulundu: büyük grupların kendi oyununu yayınlayan stüdyoları (Bungie, Quantic Dream), oyun geliri ilk 50'ye girmeyen dev şirketler (Amazon) ve zamanla değişen sahiplik. Çözüm:
- IGDB'nin üst şirket zinciriyle büyük gruplara bağlı 37 aday stüdyo bulundu. IGDB'de hatalı bağlantılar var (Gravity ve GungHo "NetEase" altında görünüyor); bunlar reddedildi.
- `buyuk_yayinci.csv`'ye `gecerli_baslangic` / `gecerli_bitis` eklendi. 22 yeni satır, satın alma tarihleri kaynaklı: Milestone 2019-08-14, Vertigo 2020-09-16, inXile 2018-12-19, Double Fine 2019-06-09, Unknown Worlds 2021-10-29, Quantic Dream 2022-08-31, Grasshopper 2021-10-21, Bungie 2022-07-15 vb. Saber (2020-02 → 2024-03) gibi ayrılmalar da tarihli.
- Üçüncü ölçüt `buyuk_teknoloji_medya`: Fortune Global 500 şirketlerinin oyun yayın kolları (Amazon Games, Sony Pictures VR).
- Doğrulama: Subnautica: Below Zero (2019, satın alma öncesi) organik; Psychonauts 2 (2021, Microsoft sonrası) organik değil.
- **Açık konu:** Tarihi doğrulanamayan düşük etkili adaylar (Grove Street Games, 3D Realms, Amplitude; toplam 9 oyun) eklenmedi.

**Bilinen sınır, büyük bağımsız stüdyolar:** Destiny 2 (Bungie, 2019) ve Detroit: Become Human (Quantic Dream, 2020) çıktıkları tarihte bağımsız oldukları için kural gereği organik. Black Myth: Wukong (Game Science), Crytek ve TaleWorlds da öyle. Stüdyo büyüklüğü gözlenmediği için kural elle bükülmedi. Ana bulgular T4 hariç tutularak da tekrarlanacak.
