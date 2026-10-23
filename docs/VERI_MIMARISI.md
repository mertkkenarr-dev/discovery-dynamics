# Discovery Dynamics: Veri Mimarisi ve Temizlik Protokolü

*Sürüm 1.0 · 2026-10-18*

İstanbul 72 Saat'te kullandığımız standart aynen uygulanıyor:
- Numaralı betikler ve tek komutla baştan sona çalışan bir hat
- DuckDB ve Parquet ile depolama
- Kayıtlı temizlik kararları
- Otomatik kontroller
- Otomatik üretilen bir veri raporu

## 1. Veri katmanları

```
data/raw/        DOKUNULMAZ. API cevapları ve indirilen dosyalar olduğu gibi durur (JSONL.gz / orijinal format).
                 Her dosya data/raw/_manifest.csv'ye işlenir: kaynak, URL, çekim zamanı (UTC), sha256, lisans.
data/interim/    Kaynak başına tipli ve düzleştirilmiş tablolar (Parquet). Henüz birleştirilmemiş, kararlar uygulanmamış.
data/processed/  discovery.duckdb (ilişkisel şema) + Parquet dışa aktarımları + Excel özet kitabı.
```

**Kurallar:**
- Ham veri asla elle düzenlenmez. Her dönüşüm bir betikle yapılır, böylece hat baştan çalıştırıldığında aynı sonuç çıkar.
- Ham veri repoya girmez, sadece indirme ve çekim betikleri repoda durur.
- Tüm zamanlar UTC olarak saklanır. Para birimi USD; değerler ABD mağazasından (`cc=us`) alınır.

## 2. Çekim ilkeleri

| İlke | Uygulama |
|---|---|
| Kaldığı yerden devam edebilme | Her çekici, tamamlanan kimlikleri bir kontrol noktası dosyasına yazar; kesilirse kaldığı yerden sürer |
| Hız limitine saygı | Kaynak başına sabit istek aralığı. 429/5xx hatalarında üstel geri çekilme ile yeniden dener |
| Önbellek | Aynı istek iki kez gönderilmez: ham cevap varsa yeniden çekilmez |
| Anlık görüntü tarihi | Her kayıtta `fetched_at` alanı tutulur. Etiket, fiyat ve inceleme sayısı zamanla değiştiği için analizde "gözlem tarihi" kontrol değişkeni olarak kullanılır |
| Anahtarlar | `.env` dosyasında tutulur (repoya girmez); `.env.example` repoda şablon olarak durur |

**Yük azaltma:**
- **Önce açık set kullanılır.** Omurga Hugging Face ve Kaggle setlerinden gelir; API sadece eksik alanlar ve 2018–2025 kohortu için çağrılır.
- **İnceleme eğrileri için önce `appreviewhistogram` uç noktası denenir.** Steam'in mağaza sayfasındaki inceleme grafiği bu uç noktadan geliyor: tek istekte oyunun ömür boyu haftalık/aylık olumlu ve olumsuz inceleme sayılarını veriyor. Doğrulanırsa milyonlarca inceleme yerine oyun başına tek istek yeterli olur.
- **Tek tek inceleme kayıtları** (oynama süresi, dil, Early Access bayrağı, metin) sadece organik örneklem ve M7/M8 örneklemleri için çekilir.

## 3. Şema (`discovery.duckdb`)

### Boyut tabloları
| Tablo | Anahtar | İçerik |
|---|---|---|
| `oyun` | `appid` | Ad, tür (game/dlc/demo), çıkış tarihi, fiyat, F2P, yaş sınırı, platformlar, başarım sayısı, DLC sayısı, demo appid, Early Access tarihleri |
| `studyo` | `studyo_id` | Normalize edilmiş ad, ilk oyun tarihi, oyun sayısı, ülke (varsa) |
| `igdb_oyun` | `igdb_id` | `appid` eşlemesi, temalar, oyun modları, bakış açıları, motor, oynama süresi |
| `yt_kanal`, `twitch_yayinci` | kanal / yayıncı kimliği | Abone veya takipçi sayısı, gözlem tarihi |

### Köprü tabloları (çoka çok)
`oyun_gelistirici`, `oyun_yayinci`, `oyun_etiket` (oy, sıra, `tag_priority`), `oyun_tur`, `oyun_kategori`, `oyun_dil` (arayüz / ses / altyazı)

### Olay tabloları
| Tablo | Satır | Not |
|---|---|---|
| `inceleme_seri` | oyun × dönem | Histogram uç noktasından gelen olumlu/olumsuz sayılar |
| `inceleme` | tek inceleme | Zaman damgası, olumlu mu, dil, inceleme anındaki ve toplam oynama süresi, Steam'den mi satın alındı, ücretsiz mi alındı, Early Access'te mi yazıldı, Steam Deck'te mi oynandı |
| `inceleme_metin` | tek inceleme | Sadece M7 örneklemi için; ayrı tutulur, çünkü büyük |
| `yt_video` | video | appid, kanal, yayın zamanı, izlenme, eşleşme güveni |
| `twitch_klip` | klip | Oyun, yayıncı, oluşturulma zamanı, izlenme |

### Referans tabloları
| Tablo | Rol |
|---|---|
| `ref_buyuk_yayinci` | Büyük yayıncılar listesi ve hangi kaynağa dayandığı |
| `ref_etiket_taksonomi` | Etiket → içerik boyutu (A–H) eşlemesi ve Quantic Foundry motivasyon ağırlıkları |
| `ref_steam_etkinlik` | Next Fest ve büyük indirim tarihleri |

### Analiz tablosu
`oyun_tablosu`: Her satır bir oyun. Tüm nitelikler ve sonuç metrikleri tek tabloda; modeller bu tablodan beslenir.

Her sütunun türü belgelenir:
- **gözlem:** doğrudan kaynaktan geldi
- **türetilmiş:** bizim hesapladığımız bir değer
- **model çıktısı:** bir modelin tahmini
- **varsayım:** bir kurala dayalı değer

### Meta tablolar
| Tablo | İçerik |
|---|---|
| `meta_karar` | Temizlik kararları: sorun, etkilenen kayıt sayısı, karar, gerekçe |
| `meta_kontrol` | Otomatik kontroller ve sonuçları |
| `meta_kaynak` | Kaynak ve lisans kaydı (VERI_KATALOGU.md ile eşleşir) |

**Excel:** `discovery_veri.xlsx` dosyasında oyun tablosu (yaklaşık 120 bin satır, Excel'in sınırına sığıyor), sözlük, karar kaydı ve kontrol sonuçları yer alır. Milyonlarca satırlık inceleme tabloları Excel'e konmaz, sadece DuckDB ve Parquet üzerinden okunur.

## 4. Temizlik protokolü

Her karar `meta_karar` tablosuna aynı biçimde işlenir: **sorun → etkilenen kayıt sayısı → karar → gerekçe**. Öngörülen ana sorunlar:

| # | Sorun | Ön karar |
|---|---|---|
| T01 | Uygulama türü karışık: oyun, DLC, demo, soundtrack, yazılım | `type = game` filtresi; demolar `fullgame` alanıyla ana oyuna bağlanır ve `demo_var` niteliği türetilir |
| T02 | Çıkış tarihi metin olarak ve farklı biçimlerde geliyor ("Coming soon", "Q3 2025", "18 Oct, 2026") | `cc=us&l=english` ile çekilir ve biçim biçim ayrıştırılır. Ayrıştırılamayanlar kayda geçer ve dışarıda bırakılır |
| T03 | Fiyat: mevcut fiyat çıkış fiyatından farklı olabilir | Çıkış fiyatı için en eski anlık görüntü (açık setler) kullanılır; yoksa mevcut fiyat alınır ve `fiyat_kaynagi` bayrağıyla işaretlenir |
| T04 | Geliştirici ve yayıncı adları tutarsız ("Studio X", "Studio X, Inc.", "STUDIO X LLC") | Ek ve büyük/küçük harf normalizasyonu ve bulanık eşleştirme. Eşleşmeler örnek üzerinden elle doğrulanır |
| T05 | Seri üreticiler (yılda onlarca neredeyse aynı oyun çıkaran hesaplar) organik örneklemi bozar | `seri_uretici` bayrağı: bir yılda > N oyun çıkaran hesap. N değeri dağılıma bakılarak seçilir ve gerekçesi yazılır; analiz bu hesaplar dahil ve hariç olarak iki kez yapılır |
| T06 | Yetişkin içerikli oyunlar: dönüşüm ve keşif dinamikleri farklı | Çıkarılmaz, `yetiskin` bayrağı konur. Ana analiz bu oyunlar hariç yapılır, duyarlılık testinde dahil edilir |
| T07 | Ücretsiz anahtarla yazılmış ve Steam dışı alımlı incelemeler | `received_for_free` olan incelemeler sonuç metriklerinden çıkarılır; Steam dışı alımlar ayrı sayılır |
| T08 | Review bombing (konu dışı toplu inceleme dalgaları) | Steam'in konu dışı aktivite filtresi açık tutulur; M8'deki sıçrama tespitinde olumsuz sıçramalar ayrı işaretlenir |
| T09 | Kaldırılmış veya erişilemeyen oyunlar | Açık setlerde olup API'de olmayan oyunlar `kaldirilmis` bayrağıyla tutulur ve betimsel olarak raporlanır |
| T10 | IGDB eşleştirmesi | Sadece IGDB'nin Steam kimliği alanı (`external_games`) üzerinden yapılır, ad üzerinden eşleştirme yapılmaz. Eşleşmeyenlerin oranı raporlanır |
| T11 | YouTube'da ad belirsizliği ("Hades" adlı oyun mu, mitoloji videosu mu?) | Eşleşme güveni puanı: başlıkta tam ad, "steam" veya "gameplay" kelimeleri, yayın tarihinin çıkışa yakınlığı. 200 videoluk elle etiketlenmiş bir örnekle eşleştirmenin isabet oranı ölçülür |
| T12 | Uç değerler (milyonlarca incelemesi olan dev oyunlar) | Silinmez; analizde log dönüşümü kullanılır. Organik örneklem tanımı bu oyunların çoğunu zaten dışarıda bırakır |
| T13 | Eksik değerler | Her sütunun eksiklik oranı raporlanır. Nitelik yoksa `0`, veri yoksa `NULL` (ikisi birbirine karıştırılmaz). Eksikliğin rastgele olup olmadığı başarı kademelerine göre karşılaştırılarak test edilir |

## 5. Otomatik kontroller (`meta_kontrol`)

Hat her çalıştığında kontrol edilenler:
- Birincil anahtarlar benzersiz mi?
- Köprü tablolarındaki her `appid`, `oyun` tablosunda var mı?
- Değerler mantıklı aralıkta mı? Fiyat ≥ 0, olumlu ≤ toplam, oran 0–1 arası.
- Tarihler kapsam aralığında mı? Early Access olmayan bir oyunda çıkıştan önce yazılmış inceleme var mı?
- Kaynaklar arası tutarlılık: açık setteki ile API'deki inceleme sayısı arasındaki fark tolerans içinde mi?
- Kohort büyüklükleri ve organik örneklem boyutu beklenen aralıkta mı?

Bir kontrol başarısız olursa hat durur. Sonuçlar veri raporunun başında özetlenir.

## 6. Betik sırası (öngörülen)

```
scripts/
  00_indir.py           Açık setleri indir (HF, Kaggle) → raw + manifest
  01_uygulama_listesi.py  Steam uygulama listesi
  02_appdetails.py      Eksik oyun ayrıntıları (kohort)
  03_steamspy.py        Etiket oyları
  04_inceleme_seri.py   Histogram uç noktasıyla inceleme zaman serisi
  05_inceleme.py        Tek tek incelemeler (örneklem)
  06_igdb.py            IGDB zenginleştirme
  07_youtube.py         M8 örneklemi videoları
  08_twitch_klip.py     M8 örneklemi klipleri
  10_temizle.py         interim → kararlar uygulanır (T01–T13)
  11_oznitelik.py       Türetilmiş nitelikler (tag_priority, novelty, saturation...)
  12_kontrol.py         Otomatik kontroller
  13_yayinla.py         DuckDB + Parquet + Excel + VERI_RAPORU.md (otomatik)
  hat.py                Hepsini sırayla çalıştırır
config.yaml             Tarih aralığı, eşikler, hız limitleri (tek kaynak)
```

## 7. Ortam

- Python 3.12+, sanal ortam `.venv`. Sürümler ilk kurulumda `requirements.txt` dosyasına sabitlenir.
- Kod stili için `ruff` (İstanbul 72 Saat ile aynı ayarlar).
- **Uzun çekimler** (saatler sürebilir) Mac'te arka planda çalıştırılır: `caffeinate -i .venv/bin/python scripts/hat.py --adim 04`. Kaldığı yerden devam edebildiği için kesinti sorun değil.
