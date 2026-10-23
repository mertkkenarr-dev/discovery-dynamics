# Discovery Dynamics: Claude çalışma notu

Steam'de bağımsız oyunların organik başarı belirleyicileri. Bir veri analizi / araştırma projesi (Python + DuckDB). Çerçeve: Google Data Analytics (Ask → Prepare → Process → Analyze → Share → Act). Dil: belgeler ve kod tanımlayıcıları Türkçe.

## Önce oku

| Ne için | Belge |
|---|---|
| Soru, tanımlar, modüller M1–M8, yol haritası | `docs/KAPSAM_VE_PLAN.md` |
| Ön kayıtlı hipotezler H1–H8 (**kilitli**) | `docs/HIPOTEZLER.md` |
| Veri ihtiyaç matrisi, "saçma sonuç" riskleri R1–R13, adım tablosu | `docs/ANALIZ_PLANI.md` |
| Katmanlar, şema, temizlik protokolü T01–T13, kontroller | `docs/VERI_MIMARISI.md` |
| Pilot ve tam GetItems bulguları | `docs/PILOT_RAPORU.md` |
| Kaynak ve lisans kaydı | `docs/VERI_KATALOGU.md` |

Güncel durum için `README.md`'deki "Durum" tablosuna ve `ANALIZ_PLANI.md §6`'ya bak; her adım bitince ikisini de güncelle.

## Değişmez kurallar

- **Hipotezler kilitli.** `HIPOTEZLER.md` düzenlenmez; değişiklik sadece en alttaki değişiklik günlüğüne tarih ve gerekçeyle eklenir. Veriye bakılıp hipotez uydurulmaz; ön kayıtta olmayan her analiz "keşifsel" etiketlenir.
- **Process bitmeden nitelik ve başarı ilişkisine bakılmaz.** Pilot ve kalite raporları sadece veri yapısını inceler.
- **`data/raw/` dokunulmaz.** API cevabı olduğu gibi `jsonl.gz` olarak yazılır, her satırda `_fetched_at` olur. Her dönüşüm betikle yapılır; indirilen dosyalar `_manifest.csv`'ye işlenir.
- **Her temizlik kararı kayda geçer:** sorun → etkilenen kayıt sayısı → karar → gerekçe (`meta_karar`). Önce/sonra sayıları raporlanır.
- **Nitelik yoksa `0`, veri yoksa `NULL`.** İkisi karıştırılmaz.
- **Sızıntı yok:** tahmin modelinde sadece çıkıştan önce bilinebilen nitelikler; kullanıcı etiketleri modele girmez (R4, R6). `novelty_score` ve `saturation` sadece o tarihe kadar çıkmış oyunlarla hesaplanır.
- **Sonuçlar etki büyüklüğü + %95 GA ile verilir**, p-değeri tek başına değil (R11).
- **Ana sonuç tanımı:** `reviews_365` = `appreviewhistogram` uç noktasının saydığı (Steam puanına giren) incelemelerin ilk 365 gündeki toplamı. Sadece ≥ 13 tam ay gözlenen oyunlarda hesaplanır (R2).

## Sabitler (tek kaynak: `config.yaml`)

Kohort 2018-01-01 – 2025-12-31 · hit ≥ 500 (duyarlılık 100 / 1.000) · organik: yayıncı ≤ 5 oyun (duyarlılık 3 / 10) · mağaza `cc=us`, `l=english` · kaynak başına hız limitleri.

## Betikler ve çalıştırma

- `scripts/NN_ad.py` numaralı sırayla. Ortak yardımcılar `scripts/ortak.py` içinde: yollar, `ayarlar()`, `http_json` (429/5xx'te üstel geri çekilme), `Hiz`, `jsonl_gz_oku/ekle`, `manifeste_ekle`.
- Her çekici **kaldığı yerden devam eder**: önce çıktıdaki tamamlanmış kimlikleri okur.
- Ortam: `uv run --no-project --python 3.12 --with ...` (bkz. `scripts/hat.sh`). zsh'de komut dizisini değişkende tutma, kelimelere bölünmez. Stil: `ruff` (`ruff.toml`).
- **Claude'un Bash ortamı uzun işleri öldürür.** Dakikalar süren çekimler kullanıcının Terminal panelinde `caffeinate -i` ile, **mutlak yolla** başlatılır (`cd /Users/mert/Desktop/Projeler/discovery-dynamics && ...`).
- Anahtarlar `.env` dosyasında. Değerleri asla ekrana yazdırma ya da loglama.

## Bilinen veri gerçekleri

- **Çıkış tarihi = ilk Steam erişimi** (`ortak.ilk_steam_erisimi`): `steam_release_date` EA'dan çıkmış oyunlarda tam sürüm tarihidir, EA başlangıcı `original_steam_release_date`'tedir. `original_release_date` güvenilmez (1970 yer tutucuları), kullanılmaz. Ayrıntı: PILOT_RAPORU.md.
- Evren: FronkonGames (124.146 kayıt). Oyun olmayan kayıtlar `GetItems type` ile atılır (oyun = 0, demo = 1). Kohortta 95.706 oyun, bunların 55.563'ünde ömür boyu ≥ 10 inceleme var (histogram sadece bunlar için çekilir; < 10 olanlarda T0 ve hit=0 kesin).
- IGDB eşleştirmesi `external_game_source = 1` ile (eski `category` alanı kaldırıldı). Oynama süresi (%3,5) ve stüdyo ülkesi (%15) kullanılamayacak kadar seyrek.
- Stüdyo sabit kimliği oyunların sadece ~%40'ında var → kimlik + ad normalizasyonu (T04).
- R12 kontrol aralığı: histogram toplamı ÷ GetItems özet sayısı **0,95–1,30**.
- FronkonGames parquet'inde etiketler boş; etiket ağırlıkları GetItems'tan gelir.
- Steam dil listesi: `elanguage = -1` satırlarında dil `eadditionallanguage`'da (ayrı numaralandırma). `n_dil` = ana diller, `n_ek_dil` ayrı; ≥ 40 ek dil = `dil_spam`.

## Kaldığımız yer (2026-10-23 gece)

- ✅ Prepare tamam: GetItems, IGDB, histogram (57.107), referans tabloları (`data/referans/`).
- ✅ Process: `10_temizle_steam.py`, `10b_temizle_igdb.py`, `11_sonuc.py` tam veriyle çalıştı. Kesin kohort **95.647**, `reviews_365` %91,5 dolu, hit %6,5.
- ✅ `12_kontrol.py`: 32/32 geçti (dil anahtarı ve stüdyo tekrarı düzeltildikten sonra; bkz. PILOT_RAPORU 'Process 3').
- ✅ `11b_oznitelik.py`: organik örneklem 84.131 (%88); büyük yayıncı listesi tarihe duyarlı (`gecerli_baslangic/bitis`). R8: inceleme ~ sahip aralığı Spearman 0,585.
- ✅ İçerik katmanları: `10c_temizle_tur.py` (Steam türleri, yazilim_suphe), `r01_etiket_taksonomi.py` (429 etiket → boyut + motivasyon taslağı), IGDB `sonradan_bilgi` sızıntı bayrağı. 36/36 kontrol.
- ⚠️ R13 büyük: Next Fest göstergesi IGDB 2025 etiketlerine göre katılımcıların ~%53'ünü yakalıyor; kaçanların demoları kaldırılmış. Çözüm Steam Web API anahtarı (kullanıcı alacak) → tam uygulama listesinden demo → parent eşlemesi.
- ⏭ Sıradaki: (a) kullanıcı STEAM_API_KEY'i .env'e ekleyince `04_demolar.py`; (b) ✅ `11c_icerik.py` tamam (novelty_k5/10/20, kombo_12ay, benzer_12ay; 42/42 kontrol; H1 = etiket kombinasyonu yeniliği); (c) motivasyon ikinci kodlayıcı (Mert); (d) ✅ `13_yayinla.py` + `scripts/hat.sh` (tüm Process hattı tek komut). Sıradaki: Analyze fazı (M1 → M2 → M3 → M4 → M6 → M5 → M7 → M8); başlamadan önce kullanıcıyla analiz sırasını teyit et.
- Git deposu kuruldu (main). Commit yazarı Mert; Claude ortak yazar satırı eklenmez.
