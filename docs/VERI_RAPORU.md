# Discovery Dynamics: Veri Raporu

*Otomatik üretildi: `13_yayinla.py` · 2026-10-23T23:05:11Z · Elle düzenlemeyin.*

## Kontroller

47 / 47 kontrol geçti. Ayrıntı: `meta_kontrol` tablosu.

## Örneklem hunisi

| Aşama | Oyun |
|---|---|
| Tüm oyunlar (type = 0, tarihli) | 113,564 |
| Kohort (2018-01-01 – 2025-12-31) | 95,647 |
| Organik örneklem | 84,131 |
| Organik, reviews_365 dolu | 76,673 |
| Organik, reviews_365 dolu, bayraksız (seri üretici, yetişkin, yazılım, listelenmemiş hariç) | 66,999 |

## Yıllara göre

| Yıl | Oyun | Organik | reviews_365 dolu |
|---|---|---|---|
| 2018 | 7,398 | 6,474 | %99.6 |
| 2019 | 7,141 | 6,214 | %99.7 |
| 2020 | 8,757 | 7,635 | %99.6 |
| 2021 | 10,249 | 8,954 | %99.4 |
| 2022 | 11,294 | 9,771 | %99.1 |
| 2023 | 12,977 | 11,223 | %98.8 |
| 2024 | 17,468 | 15,554 | %97.3 |
| 2025 | 20,363 | 18,306 | %64.3 |

## T13: Eksikliğin başarı kademesine göre dağılımı (kohort, % NULL)

Eksiklik kademeye göre değişiyorsa o alana dayanan bulgular yanlı olabilir; analizde eksiklik göstergesi ya da duyarlılık testi gerekir. Bu bir veri kalitesi testidir. `fiyat_liste_usd` satırı yalnız ücretli oyunlarda fiyatın bilinmemesini sayar (F2P'de fiyat tanım gereği NULL).

| Sütun | T0 | T1 | T2 | T3 | T4 |
|---|---|---|---|---|---|
| `igdb_tur` | 9.8 | 4.9 | 5.8 | 4.5 | 0.7 |
| `n_tema` | 48.9 | 37.2 | 29.5 | 17.9 | 5.6 |
| `n_bakis` | 75.5 | 59.7 | 42.6 | 25.6 | 6.1 |
| `n_motor` | 67.7 | 48.4 | 34.3 | 24.0 | 11.2 |
| `novelty_k10` | 5.5 | 2.2 | 0.4 | 0.0 | 0.0 |
| `kombo_12ay` | 15.3 | 10.0 | 5.0 | 2.9 | 1.3 |
| `fiyat_liste_usd` | 1.2 | 1.0 | 1.4 | 1.7 | 3.5 |
| `yayinci_onceki_oyun` | 0.3 | 0.4 | 0.3 | 0.1 | 0.4 |

## Temizlik kararları

| Kod | Betik | Sorun | Etkilenen | Karar |
|---|---|---|---|---|
| T09 | 10_temizle_steam | GetItems'ta başarısız (kaldırılmış / erişilemiyor) evren kaydı | 300 / 124,146 | `kaldirilmis.parquet`'e ayrılır, analizden çıkar |
| T01 | 10_temizle_steam | Evrende oyun dışı kayıtlar: {'playtest': 8262, 'yazılım': 1872, 'dlc/paket': 112, 'mod/genişleme': 1} | 10,247 / 124,146 | Sadece type=0 kalır; demo ve playtest'ler parent_appid ile ana oyuna nitelik olarak bağlanır |
| T02 | 10_temizle_steam | Geçerli ilk Steam erişim tarihi yok (boş ya da 1990 öncesi yer tutucu) | 35 / 113,599 | ilk_cikis = NULL; kohort dışında kalır |
| T02b | 10_temizle_steam | İlk erişim tarihi çekim anından sonra (henüz çıkmamış) | 2 / 113,599 | Kohort dışında kalır |
| T02c | 10_temizle_steam | EA'dan çıkmış oyunda steam_release_date tam sürüm tarihi (EA başlangıcı değil) | 7,358 / 113,599 | ilk_cikis = min(steam_release_date, original_steam_release_date) |
| T03 | 10_temizle_steam | Ücretli oyunda satın alma seçeneği yok (fiyat bilinmiyor) | 1,195 / 95,706 | fiyat_liste_usd = NULL (0 değil) |
| T03b | 10_temizle_steam | Çekim anında indirimde olan oyun | 8,220 / 113,599 | İndirimsiz liste fiyatı kullanılır; fiyat 'mevcut liste fiyatı'dır, çıkış fiyatı değil |
| T06 | 10_temizle_steam | Yetişkin cinsel içerik uyarısı (Steam içerik kimliği 3 veya 4) | 6,776 / 95,706 | Çıkarılmaz; yetiskin bayrağı. Ana analiz hariç, duyarlılıkta dahil |
| T15 | 10_temizle_steam | Listelenmemiş (mağaza aramasında görünmeyen) oyun | 1,069 / 95,706 | Çıkarılmaz; listelenmemis bayrağı |
| T04 | 10_temizle_steam | Kimliksiz stüdyo adı yazım farkları (ham 68,637 → normalize 66,685 farklı ad) | 1,952 / 68,637 | Küçük harf, Unicode NFKC, noktalama ve yasal ek (Inc, LLC, Ltd…) temizliği |
| T04b | 10_temizle_steam | Kimliksiz satır, normalize adı tek bir sabit kimlikle eşleşiyor | 9,717 / 152,088 | O kimliğe bağlanır |
| T04c | 10_temizle_steam | Stüdyo adı boş | 0 / 242,759 | Satır atılır (stüdyo bilinmiyor) |
| T04d | 10_temizle_steam | Aynı oyunda aynı stüdyo aynı rolde birden fazla satır (ör. LucasArts + Lucasfilm, Aspyr (Mac) + Aspyr (Linux)) | 1,447 / 242,759 | Tek satıra indirilir; farklı adlar ' | ' ile birleşir |
| T05 | 10_temizle_steam | Seri üretici: bir yılda > 12 oyun çıkaran geliştiricinin oyunu (140 geliştirici) | 6,465 / 95,706 | Çıkarılmaz; seri_uretici bayrağı. Analiz dahil/hariç iki kez |
| T13 | 10_temizle_steam | Hiç etiketi olmayan oyun | 32 / 113,599 | n_etiket = 0 (veri var, etiket yok); etiket köprüsünde satırı olmaz |
| T16 | 10_temizle_steam | Dil listesinde aynı dil birden fazla kez | 0 / 664,815 | İlk kayıt tutulur |
| T17 | 10_temizle_steam | Dil spam'i: ≥ 40 ek dil iddiası (72 ek dilin tamamı: 1,978 oyun) | 1,918 / 95,706 | dil_spam bayrağı; n_dil yalnız Steam ana dillerini sayar, ek diller n_ek_dil'de |
| T10 | 10b_temizle_igdb | Bir appID birden fazla IGDB oyununa bağlı | 0 / 104,647 | Eşleşme kullanılmaz (belirsiz) |
| T10b | 10b_temizle_igdb | Steam bağlantısı var ama IGDB oyun kaydı dönmedi | 16 / 104,647 | Eşleşmesiz sayılır |
| T10c | 10b_temizle_igdb | Aynı IGDB oyunu birden fazla appID'ye bağlı (aynı oyunun farklı Steam sürümleri) | 257 / 104,631 | Nitelikler her appID'ye kopyalanır; igdb_paylasimli bayrağı |
| T10e | 10b_temizle_igdb | IGDB anahtar kelimesi çıkıştan sonra oluşan bilgi (ödül, Netflix/PS Plus/Game Pass, bedava dağıtım): 116 farklı kelime | 1,220 / 225,515 | sonradan_bilgi bayrağı; tahmin modeline hiçbir anahtar kelime girmez, betimsel analizde bunlar çıkarılır |
| T10d | 10b_temizle_igdb | Sözlükte adı bulunmayan IGDB kimliği | 0 / 798,214 | Kimlik tutulur, ad NULL |
| T18 | 10c_temizle_tur | Steam türü yok (FronkonGames'te boş ya da kayıt yok) | 83 / 95,647 | Tür köprüsünde satırı olmaz; analizde 'tür bilinmiyor' |
| T01b | 10c_temizle_tur | type=0 ama oyun dışı yazılım işareti (yalnız yazılım türü, ya da yazılım türü + en güçlü etiket yazılım) | 12 / 95,647 | yazilim_suphe bayrağı; ana analizden çıkarılır, duyarlılıkta dahil |
| S01 | 11_sonuc | Ömür boyu < 10 inceleme: histogram çekilmedi | 40,852 / 97,436 | reviews_365 = ömür boyu sayı (üst sınır), sadece ≥ 396 gün gözlenenlerde |
| S02 | 11_sonuc | ≥ 10 inceleme ama histogram yok (çekim eksik / boş cevap) | 0 / 97,436 | Sonuç NULL; tamamlanınca 03_histogram.py tekrar çalıştırılır |
| S03 | 11_sonuc | 365 gün penceresi tam gözlenmemiş (sağdan sansür, R2) | 9,798 / 97,436 | reviews_365, kademe ve hit = NULL |
| S04 | 11_sonuc | R12: histogram ömür toplamı ÷ GetItems özeti 0,95–1,30 dışında | 1,423 / 56,584 | r12_uyumsuz bayrağı; ana analizde tutulur, duyarlılıkta çıkarılır |
| T14 | 11_sonuc | Steam çıkış ayından önce ≥ 10 inceleme (yeniden yayında sıfırlanan tarih / kayıtsız EA); 154 tanesi gerçekte 2018 öncesi | 962 / 56,584 | ilk_cikis = ilk inceleme günü (histogram start_date); pencereler ve kohort yeni tarihle hesaplanır; 2018 öncesine düşenler kohort=False |
| N01 | 11b_oznitelik | Yayıncı bilgisi yok (kendi_yayini ve yayinci_onceki_oyun NULL) | 313 / 95,647 | organik = False (koşul kanıtlanamıyor) |
| N02 | 11b_oznitelik | Organik örneklem: (kendi yayını veya yayıncının önceki oyunu ≤ 5) ve büyük yayıncı değil | 84,131 / 95,647 | Duyarlılık: ≤3 → 83,006, ≤10 → 85,913 |
| N03 | 11b_oznitelik | Kendi yayını ama büyük yayıncı (CD Projekt, Larian, Valve…) | 356 / 95,647 | Organik dışı |
| N04 | 11b_oznitelik | Demo çıkıştan önce yayında (mağazada görünen demolar) | 10,267 / 95,647 | demo_cikis_oncesi; çıkıştan sonra eklenen demo sayılmaz |
| N05 | 11b_oznitelik | Next Fest dolaylı göstergesi: çıkış öncesi demo bir festival penceresinde mevcut | 8,071 / 81,455 | nextfest_aday; Aralık 2019 öncesi çıkanlarda NULL |
| N06 | 11b_oznitelik | IGDB ilk çıkışı Steam'den 1 yıldan fazla önce (başka platformda önceden çıkmış) | 3,357 / 95,647 | steam_oncesi_cikis; IGDB yoksa NULL |
| C01 | 11c_icerik | İçerik etiketi < 3 (vektör güvenilmez) | 3,155 / 95,647 | novelty ve benzer_12ay = NULL |
| C02 | 11c_icerik | Alt tür etiketi yok (tür kombinasyonu tanımsız) | 10,624 / 95,647 | kombo_12ay = NULL |
| B01 | 11d_basari | 2. yıl penceresi tam gözlenmemiş | 4,496 / 20,377 | kalicilik = NULL |
| B02 | 11d_basari | Ticari ölçü tanımsız (F2P ya da fiyat bilinmiyor) | 14,911 / 87,488 | brut_gelir ve ticari_basari = NULL |

## Sütun sözlüğü (`oyun_tablosu`)

`ÖNCE` = çıkış anında bilinebilir, tahmin modelinde kullanılabilir (R6). `ÖNCE*` = mevcut durum, çıkış anındaki değer olmayabilir.

| Sütun | Tür | Kohortta dolu | Açıklama |
|---|---|---|---|
| `appid` | gözlem | %100.0 | Steam uygulama kimliği |
| `ad` | gözlem | %100.0 | Oyun adı (GetItems) |
| `cikis` | türetilmiş | %100.0 | ÖNCE · Çıkış = ilk Steam erişimi; T14'te ilk inceleme gününe düzeltilmiş olabilir (UTC) |
| `ilk_cikis_kaynagi` | türetilmiş | %100.0 | cikis kaynağı: steam / ilk_inceleme (T14 düzeltmesi) |
| `tarih_duzeltildi` | türetilmiş | %100.0 | cikis T14 ile düzeltildi mi |
| `tam_surum_tarihi` | gözlem | %100.0 | Steam steam_release_date (EA'dan çıkan oyunda tam sürüm) |
| `yil` | türetilmiş | %100.0 | ÖNCE · Çıkış yılı |
| `ay` | türetilmiş | %100.0 | ÖNCE · Çıkış ayı |
| `haftanin_gunu` | türetilmiş | %100.0 | ÖNCE · Çıkış günü (0 = Pazartesi, UTC) |
| `kohort` | türetilmiş | %100.0 | 2018-01-01 ≤ cikis < 2026-01-01 |
| `gozlem_gun` | türetilmiş | %100.0 | Çekim anı − cikis (gün); düzeltilmiş tarihe göre |
| `fetched_at` | gözlem | %100.0 | GetItems çekim anı (gözlem tarihi kontrolü) |
| `inceleme_omur` | gözlem | %100.0 | GetItems ömür boyu inceleme sayısı (summary_filtered) |
| `olumlu_yuzde_omur` | gözlem | %100.0 | GetItems ömür boyu olumlu yüzde |
| `omur_hist` | gözlem | %58.2 | Histogram ömür boyu toplam (Steam puanına giren incelemeler) |
| `reviews_30` | türetilmiş | %58.0 | İlk 30 gün inceleme (aylık kovada yaklaşık; cozunurluk) |
| `reviews_90` | türetilmiş | %57.8 | İlk 90 gün inceleme |
| `reviews_365` | türetilmiş | %91.5 | BİRİNCİL SONUÇ · İlk 365 gün inceleme; < 10 ömür boyu ise üst sınır (sonuc_kaynagi) |
| `olumlu_oran_365` | türetilmiş | %52.9 | İlk 365 gün olumlu oranı |
| `tail_share` | türetilmiş | %52.9 | (r365 − r90) / r365: ilk yıl içindeki geç kuyruk payı (H4) |
| `kademe` | türetilmiş | %91.5 | T0 <10 · T1 10–99 · T2 100–499 · T3 500–4.999 · T4 ≥5.000 (yuvarlanmış r365) |
| `hit` | türetilmiş | %91.5 | reviews_365 ≥ 500 |
| `sonuc_kaynagi` | türetilmiş | %100.0 | histogram / omur_ust_sinir |
| `cozunurluk` | gözlem | %100.0 | Histogram kovası: month / week / yok |
| `onceden_inceleme` | türetilmiş | %58.2 | Steam çıkış ayından önceki kovalardaki inceleme (T14 ölçütü) |
| `r12_oran` | türetilmiş | %58.2 | omur_hist / inceleme_omur (R12) |
| `r12_uyumsuz` | türetilmiş | %100.0 | r12_oran 0,95–1,30 dışında |
| `begeni_wilson` | türetilmiş | %52.9 | Beğeni · İlk yıl olumlu oranının %95 Wilson alt sınırı (az incelemede temkinli) |
| `reviews_2yil` | türetilmiş | %41.6 | Kalıcılık · 366.–730. gün incelemeleri (2. yıl tam gözlenmişse) |
| `kalicilik` | türetilmiş | %16.6 | Kalıcılık · reviews_2yil / reviews_365 (reviews_365 ≥ 50) |
| `brut_gelir_alt` | varsayım | %16.0 | Ticari · reviews_365 × 20 × fiyat (USD, reviews_365 ≥ 50, ücretli) |
| `brut_gelir_orta` | varsayım | %75.9 | Ticari · reviews_365 × 30 × fiyat (USD, ücretli). Fiyat içerdiği için K1'de sonuç olarak kullanılmaz |
| `brut_gelir_ust` | varsayım | %16.0 | Ticari · reviews_365 × 40 × fiyat (USD, reviews_365 ≥ 50, ücretli) |
| `ticari_basari` | varsayım | %75.9 | Ticari · brut_gelir_orta ≥ 100.000 USD |
| `ana_tur` | türetilmiş | %100.0 | En güçlü 'ana' tür etiketi (göreli sıra grubu için) |
| `goreli_yuzdelik` | türetilmiş | %91.5 | Göreli · aynı yıl × ana tür içinde reviews_365 yüzdeliği (0–1) |
| `basari_sinifi` | türetilmiş | %91.5 | gorunmez · orta · sessiz_basari · sevilen_hit · hit · tartismali_hit |
| `f2p` | gözlem | %100.0 | ÖNCE · Ücretsiz |
| `fiyat_liste_usd` | gözlem | %83.3 | ÖNCE* · Mevcut liste fiyatı (indirimsiz, USD). *Çıkış fiyatı değil (T03) |
| `fiyat_kaynagi` | türetilmiş | %100.0 | f2p / mevcut_liste / yok |
| `fiyat_bandi` | türetilmiş | %98.8 | ÖNCE* · f2p, <5, 5-10, 10-20, 20-30, >=30 |
| `ea_ile_basladi` | türetilmiş | %100.0 | ÖNCE · Early Access ile çıktı |
| `ea_su_an` | gözlem | %100.0 | Çekim anında hâlâ Early Access |
| `ea_sure_gun` | türetilmiş | %6.9 | EA süresi (EA'dan çıkmışlarda) |
| `demo_var_su_an` | gözlem | %100.0 | Mağazada şu an görünen demo var (R13: kaldırılmış demolar görünmez) |
| `demo_ilk_tarih` | gözlem | %14.2 | En eski görünen demonun çıkış tarihi |
| `demo_cikis_oncesi` | türetilmiş | %100.0 | ÖNCE · Demo çıkıştan önce yayında (R13 sınırı) |
| `demo_gun_once` | türetilmiş | %10.7 | ÖNCE · Demo çıkıştan kaç gün önce |
| `playtest_var` | gözlem | %100.0 | ÖNCE · Playtest uygulaması var |
| `nextfest_aday` | türetilmiş | %85.2 | ÖNCE · Dolaylı Next Fest göstergesi; IGDB 2025'e göre duyarlılık ~%53 (R13) |
| `indirim_icinde` | türetilmiş | %100.0 | ÖNCE · Büyük Steam indirimi sırasında çıktı |
| `gun_sonraki_indirim` | türetilmiş | %99.4 | ÖNCE · Bir sonraki büyük indirimin başlangıcına gün |
| `indirim_tek_kaynak` | türetilmiş | %100.0 | İndirim nitelikleri tek kaynaklı bir tarihe dayanıyor |
| `ayni_hafta_cikan` | türetilmiş | %100.0 | ÖNCE · Aynı ISO haftasında çıkan diğer oyun sayısı |
| `ayni_hafta_buyuk_yayinci` | türetilmiş | %100.0 | ÖNCE · Aynı hafta büyük yayıncı çıkışı var |
| `yayinci_onceki_oyun` | türetilmiş | %99.7 | ÖNCE · Yayıncının kesin olarak önce çıkmış oyun sayısı (en büyük yayıncı) |
| `kendi_yayini` | türetilmiş | %99.6 | ÖNCE · Tüm yayıncılar geliştiriciler arasında |
| `buyuk_yayinci` | türetilmiş | %100.0 | ÖNCE · Yayıncı, çıkış tarihinde buyuk_yayinci.csv'de geçerli |
| `organik` | türetilmiş | %100.0 | ANA ÖRNEKLEM · (kendi yayını veya yayıncı önceki ≤ 5) ve büyük yayıncı değil |
| `organik_5` | türetilmiş | %100.0 | organik ile aynı (eşik 5) |
| `organik_3` | türetilmiş | %100.0 | Duyarlılık: eşik 3 |
| `organik_10` | türetilmiş | %100.0 | Duyarlılık: eşik 10 |
| `gelistirici_onceki_oyun` | türetilmiş | %99.9 | ÖNCE · Geliştiricinin kesin olarak önce çıkmış oyun sayısı (en deneyimli) |
| `studyo_yasi_gun` | türetilmiş | %99.9 | ÖNCE · Geliştiricinin ilk oyunundan bu yana gün |
| `n_gelistirici` | gözlem | %100.0 | Geliştirici sayısı |
| `seri_steam` | gözlem | %15.6 | Steam seri adı |
| `seri_uretici` | varsayım | %100.0 | Geliştirici bir yılda > 12 oyun çıkarmış (T05) |
| `yetiskin` | gözlem | %100.0 | Steam içerik uyarısı 3 veya 4 (T06) |
| `listelenmemis` | gözlem | %100.0 | Mağaza aramasında görünmüyor (T15) |
| `yazilim_suphe` | varsayım | %100.0 | Oyun olarak kayıtlı yazılım (T01b) |
| `dil_spam` | varsayım | %100.0 | ≥ 40 ek dil iddiası (T17) |
| `steam_oncesi_cikis` | türetilmiş | %89.7 | ÖNCE · IGDB ilk çıkışı Steam'den > 1 yıl önce |
| `schinese` | gözlem | %100.0 | ÖNCE* · Basitleştirilmiş Çince arayüz (elanguage 6). *Mevcut durum |
| `n_dil` | gözlem | %100.0 | ÖNCE* · Steam ana dil sayısı |
| `n_ek_dil` | gözlem | %100.0 | Ek dil sayısı (elanguage = -1) |
| `win` | gözlem | %100.0 | Windows |
| `mac` | gözlem | %100.0 | macOS |
| `linux` | gözlem | %100.0 | Linux / SteamOS |
| `deck_uyum` | gözlem | %100.0 | Steam Deck uyumu (0 bilinmiyor, 1 desteklenmiyor, 2 oynanabilir, 3 doğrulanmış) |
| `n_etiket` | gözlem | %100.0 | Steam etiket sayısı (ilk 20) |
| `n_steam_tur` | gözlem | %100.0 | ÖNCE · Geliştiricinin seçtiği içerik türü sayısı (meta ve yazılım türleri hariç) |
| `igdb_tur` | gözlem | %91.2 | IGDB oyun türü (ana_oyun, remaster, port…) |
| `igdb_ilk_cikis` | gözlem | %89.7 | IGDB ilk çıkış (tüm platformlar) |
| `n_tema` | gözlem | %58.3 | IGDB tema sayısı (NULL = alan boş) |
| `n_bakis` | gözlem | %36.5 | IGDB bakış açısı sayısı (NULL = alan boş) |
| `n_motor` | gözlem | %44.7 | IGDB motor sayısı (NULL = alan boş) |
| `n_icerik_etiket` | türetilmiş | %100.0 | İçerik boyutlarındaki (A–F) etiket sayısı |
| `novelty_k10` | türetilmiş | %96.7 | H1 · Etiket kombinasyonu yeniliği: 1 − önceki en yakın 10 oyuna ortalama kosinüs (betimsel; R4) |
| `novelty_k5` | türetilmiş | %96.7 | Duyarlılık: k = 5 |
| `novelty_k20` | türetilmiş | %96.7 | Duyarlılık: k = 20 |
| `en_yakin_benzerlik` | türetilmiş | %96.7 | Önceki en benzer oyunla kosinüs |
| `tur_kombo` | türetilmiş | %88.9 | En güçlü 2 alt tür etiketi |
| `kombo_12ay` | türetilmiş | %88.9 | H7 · Aynı tur_kombo'da son 365 günde çıkan oyun |
| `benzer_12ay` | türetilmiş | %96.7 | H7 duyarlılık · Son 365 günde kosinüs ≥ 0,6 olan oyun |
| `benzer_12ay_t40` | türetilmiş | %96.7 | Eşik 0,4 |
| `benzer_12ay_t50` | türetilmiş | %96.7 | Eşik 0,5 |
| `benzer_12ay_t60` | türetilmiş | %96.7 | Eşik 0,6 (= benzer_12ay) |
| `benzer_12ay_t70` | türetilmiş | %96.7 | Eşik 0,7 |
