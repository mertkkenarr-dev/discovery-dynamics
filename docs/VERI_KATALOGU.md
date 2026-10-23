# Discovery Dynamics: Veri Kataloğu

*Sürüm 0.1 · 2026-10-18 · Durum: ön tarama (sayfa açıklamalarından; dosyalar henüz indirilip doğrulanmadı)*

Her set indirildiğinde şu alanlar doldurulacak: satır sayısı, gerçek sütunlar, toplama tarihi, lisans ve **verinin asıl kaynağı**.

**Kullanım kuralı:** Asıl kaynağı ve lisansı doğrulanmayan setler sadece çapraz doğrulama için kullanılır, analize girmez.

## Rol tanımları

| Rol | Anlamı |
|---|---|
| **Omurga** | Analizin dayandığı ana veri |
| **Zenginleştirme** | Omurgaya eklenen ek nitelikler |
| **Doğrulama** | Kendi çektiğimiz verinin bağımsız bir kaynakla karşılaştırılması |
| **Elendi** | Kullanılmayacak (gerekçesiyle) |

## A. Oyun metadata setleri

| Set | Platform | Boyut | Sütunlar (öne çıkan) | Lisans | Asıl kaynak | Rol | Not |
|---|---|---|---|---|---|---|---|
| [FronkonGames/steam-games-dataset](https://huggingface.co/datasets/FronkonGames/steam-games-dataset) | HF + [Kaggle](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset) | 83 bin+ oyun; Parquet 192 MB (CSV 401 MB, JSON 970 MB) | ~40 alan: fiyat, diller, geliştirici/yayıncı, kategoriler, türler, etiketler, olumlu/olumsuz, sahip aralığı, peak CCU, ortalama/ortanca oynama süresi | **MIT** (HF etiketi) | Steam API + SteamSpy (scraper reposu açık) | **Omurga (seçildi)** | HF son güncelleme **2026-10-15**. Sadece Parquet indirilecek |
| [Z02Z/steam-games-dataset](https://huggingface.co/datasets/Z02Z/steam-games-dataset) | HF | ~123 bin satır; Parquet 190 MB | FronkonGames ile aynı şema (~40 sütun) | CC BY 4.0 | Belirtilmemiş | Doğrulama | HF son güncelleme 2026-02-02; FronkonGames daha güncel olduğu için omurga değil |
| [steam-dataset-2025 (vintagedon)](https://github.com/vintagedon/steam-dataset-2025) | GitHub + [Kaggle](https://www.kaggle.com/datasets/crainbramp/steam-dataset-2025-multi-modal-gaming-analytics) | 239 bin uygulama (oyun + DLC + yazılım) | appdetails alanları, tür/kategori tabloları, açıklama embedding'leri | CC BY 4.0 (veri), MIT (kod) | Resmi Steam API'leri (Ağu–Eyl 2025) | **Zenginleştirme / doğrulama** | Kaynağı ve lisansı en temiz set. Kullanıcı etiketleri yok |
| [hubertsidorowicz/steam-games-dataset-daily-updates](https://www.kaggle.com/datasets/hubertsidorowicz/steam-games-dataset-daily-updates) | Kaggle | 144 bin+ oyun, günlük güncelleniyor | Doğrulanacak | Doğrulanacak | Doğrulanacak | Doğrulama adayı | Günlük güncelleniyorsa en taze anlık görüntü |
| [artermiloff/steam-games-dataset](https://www.kaggle.com/datasets/artermiloff/steam-games-dataset) | Kaggle | 90 bin+ oyun | Doğrulanacak | Doğrulanacak | Doğrulanacak | Doğrulama adayı | — |
| [sibamsamanta07/130k-steam-games](https://www.kaggle.com/datasets/sibamsamanta07/130k-steam-games-prices-tags-reviews-ccu) | Kaggle | 130 bin+ oyun | Fiyat, tür, etiket, oynama süresi, inceleme, CCU, sahip tahmini | Doğrulanacak | Doğrulanacak | Doğrulama adayı | — |
| [nikdavis/steam-store-games](https://www.kaggle.com/datasets/nikdavis/steam-store-games) | Kaggle | ~27 bin oyun (2019) | Steam + SteamSpy | Doğrulanacak | Steam + SteamSpy | Elendi | 2019'dan kalma, güncel değil |

## B. İnceleme setleri

| Set | Platform | Boyut | Öne çıkan alanlar | Lisans | Rol | Not |
|---|---|---|---|---|---|---|
| [forgemaster/steam-reviews-dataset](https://www.kaggle.com/datasets/forgemaster/steam-reviews-dataset) | Kaggle | ~15 milyon inceleme, 8.183 oyun | Doğrulanacak | Doğrulanacak | **M7 (metin analizi) adayı** | 2021 civarı; zaman damgası alanı kontrol edilecek |
| [najzeko/steam-reviews-2021](https://www.kaggle.com/datasets/najzeko/steam-reviews-2021) | Kaggle | Büyük (doğrulanacak) | Doğrulanacak | Doğrulanacak | M7 adayı | — |
| [UCSD McAuley Steam (HF kopyası)](https://huggingface.co/datasets/recommender-system/steam-review-and-bundle-dataset) | HF | 7,8 milyon inceleme, 32 bin oyun, bundle verisi | İnceleme tarihi, oynama saati, Early Access bayrağı, metin; kullanıcı kütüphaneleri | Akademik (asıl kaynaktan doğrulanacak) | Doğrulama | 2018'e kadar; akademik olarak sık atıf alan bir set |
| [steam-dataset-2025 incelemeleri](https://github.com/vintagedon/steam-dataset-2025) | GitHub | 1 milyon inceleme (uygulama başına yaklaşık 10) | Metin, oy, embedding; **tarih yok** | CC BY 4.0 | Elendi (M4 için) | Zaman damgası yok, uygulama başına sadece ~10 inceleme |

**Sonuç:** Hiçbir açık sette 2018–2025 kohortu için tam inceleme zaman damgaları yok. M4 (yörüngeler) ve M8 (içerik üreticisi) için incelemeler Steam API'den kendimiz çekilecek. Kaggle setleri M7 ve doğrulama için kullanılacak.

## C. Oyuncu sayısı geçmişi

| Set | Boyut | Kapsam | Rol | Not |
|---|---|---|---|---|
| [lunthu/steam-monthly-average-players](https://www.kaggle.com/datasets/lunthu/steam-monthly-average-players) | 6 bin+ oyun | Aylık ortalama oyuncu | **Zenginleştirme adayı** | Asıl kaynak doğrulanacak (büyük ihtimalle SteamCharts) |
| [michau96/popularity-of-games-on-steam](https://www.kaggle.com/datasets/michau96/popularity-of-games-on-steam) | Doğrulanacak | Aylık popülerlik | Zenginleştirme adayı | — |
| [jackogozaly/steam-player-data](https://www.kaggle.com/datasets/jackogozaly/steam-player-data/data) | İlk 100 oyun, 2012–2021 | — | Elendi | Sadece en büyük oyunlar var, organik örneklemle örtüşmüyor |

## D. Twitch

| Set | Kapsam | Rol | Not |
|---|---|---|---|
| [rankirsh/evolution-of-top-games-on-twitch](https://www.kaggle.com/datasets/rankirsh/evolution-of-top-games-on-twitch) | 2016–2023, her ay ilk 200 oyun | Makro bağlam (Katman 1) | Bağımsız oyunların çoğu ilk 200'de yer almaz |
| [nivecoolz/Top-Games-on-Twitch-2016-2024](https://github.com/nivecoolz/Top-Games-on-Twitch-2016---2024) | 2016–2024, aylık ilk 200: izleyici, yayıncı sayısı | Makro bağlam | Lisans ve asıl kaynak belirsiz |
| Twitch Helix `Get Clips` (kendi çekimimiz) | Oyun ve tarih bazlı klipler | **M8 omurgası** | — |

## E. İçerik zenginleştirme

| Kaynak | Ne sağlıyor | Rol |
|---|---|---|
| IGDB API (kendi çekimimiz) | Tema, oyun modu, bakış açısı, anahtar kelimeler, motor, oynama süresi | **Zenginleştirme** |
| SteamSpy API (kendi çekimimiz) | Etiket **oy sayıları** (`tag_priority` için zorunlu) | **Omurga** |
| HowLongToBeat | Kaggle'da güncel ve lisanslı bir set bulunamadı | Elendi; yerine IGDB `game_time_to_beats` kullanılacak |

## Doğrulanan uç nokta: `appreviewhistogram` (2026-10-18)

- Test edilen oyun: Hades (appid 1145360).
- Cevapta oyunun ömür boyu **aylık** olumlu/olumsuz rollup'ları geliyor (83 ay). Ayrıca son 30 günün günlük değerleri ve bir `weeks` alanı var.
- Rollup'ların toplamı 302.281, `appreviews` uç noktasının verdiği toplam 310.114. Fark yaklaşık %2,5 ve büyük ihtimalle dil ya da satın alma filtresinden kaynaklanıyor; çekim sırasında kontrol edilecek.
- **Sonuç:** `reviews_365` ve aylık yörüngeler oyun başına tek istekle hesaplanabiliyor. Günlük çözünürlük gereken analizlerde (M8 sıçramaları) tek tek inceleme kayıtları örneklem üzerinden çekilecek.

## Prepare aşaması için çıkan karar

1. **Omurga:** FronkonGames (MIT, 2026-10-15 güncel). SteamSpy ile etiket oyları eklenecek.
2. **Kendi çekimimiz zorunlu:** İnceleme zaman damgaları (2018–2025 kohortu), IGDB, YouTube, Twitch Clips.
3. **Doğrulama:** steam-dataset-2025 ve hubertsidorowicz.
4. **M7:** forgemaster / najzeko inceleme metinleri, artı kendi çektiğimiz metinler.

## Güncelleme · 2026-10-22 (indirme ve ilk inceleme)

- **İndirilenler:**
  - FronkonGames Parquet (192 MB, 124.146 kayıt)
  - Z02Z Parquet (190 MB, 122.876 kayıt; tamamı FronkonGames'in alt kümesi)
  - lunthu: SteamCharts aylık verisi (6.729 oyun, Eylül 2025'e kadar)
  - michau96: SteamCharts verisi (2021'e kadar)
  - rankirsh: Twitch'te ilk 200 oyun, 2016–2023
- **Kaggle lisansları:** Üç Kaggle setinin metadata'sında lisans alanı boş. Bu yüzden sadece "bağlam / doğrulama" rolünde kullanılır, ham hali yeniden yayımlanmaz.
- **FronkonGames Parquet'te `tags` ve `movies` sütunları boş** (tip `list<null>`). JSON sürümünde etiket oyları var. Ancak etiket ağırlıkları Steam `IStoreBrowseService/GetItems` ile daha güncel ve resmi biçimde alınabildiği için JSON indirilmedi.
- **Yeni omurga kaynağı:** `IStoreBrowseService/GetItems` (resmi Steam Web API, anahtarsız, tek istekte 100 oyun). Ayrıntılar ANALIZ_PLANI.md B8'de.
- **SteamSpy'ın rolü:** "Omurga"dan "çapraz doğrulama"ya indi.


## Düzeltme (2026-10-24): FronkonGames oyun başına alanları Şubat 2026'da donmuş

FronkonGames (HF commit 2026-10-15) ile Z02Z (2026-02-02) karşılaştırıldı. 122.876 ortak oyunda dil listeleri **ve** olumlu/olumsuz inceleme sayıları **%100 aynı**. Yani FronkonGames yeni oyun eklemeyi Şubat 2026'da bıraktığı gibi (B4) mevcut oyunların alanlarını da güncellememiş; Z02Z onun kopyası.

**Sonuçları:**
- FronkonGames'ten alınan her alan (Steam türleri `10c`, dil metinleri, SteamSpy sahip aralıkları) **Şubat 2026 anlık görüntüsüdür.**
- Steam türleri için bu çıkış anına daha yakın olduğundan avantaj.
- Z02Z bağımsız bir doğrulama kaynağı **değildir.**
- Ekim 2026 durumu yalnız kendi GetItems çekimimizden gelir.
