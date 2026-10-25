# Keşifsel analizler K5–K8: tanımlar (sonuçlara bakılmadan, 2026-10-25)

Bu dört analiz ön kayıtta yok; hepsi **keşifsel**. Hipotez testi değil, ama "veriye bakıp tanım uydurma" riskini azaltmak için
tanımlar, eşikler ve karşılaştırmalar kod çalışmadan önce burada sabitlendi. Sonradan değişen her şey en alttaki günlüğe
tarih ve gerekçeyle yazılır.

Ortak: analiz örneklemi = `grafik.orneklem()` (kohort, organik, bayraksız, reviews_365 dolu). Başarı = hit (ilk yıl ≥ 500
inceleme); her bulgu `sevilen_hit` ve log(1 + reviews_365) ile de kontrol edilir. İçerik benzerliği = 11c'deki içerik vektörlerinin
kosinüsü (ilk 10 içerik etiketi, sıra × 2018 öncesi IDF). Oranlar Wilson %95 GA ile verilir.

## K5: Klon dalgaları

**Soru:** Bir oyun büyük hit olunca arkasından benzerleri geliyor mu? Gelenler kazanıyor mu, erken gelen mi kazanıyor?

- **Öncü:** Kohortta, 2018-01-01 – 2024-03-31 arasında çıkmış (takipçilerin 18 ayı ve sonuçları gözlenebilsin diye), ilk yılda
  ≥ 5.000 inceleme (T4) almış, en az 3 içerik etiketli oyun. Organik şartı yok: dalgayı büyük yayıncının hit'i de başlatabilir.
- **Takipçi:** Öncüden sonraki 0–24 ay içinde çıkan ve öncüye kosinüs benzerliği **≥ 0,70** olan kohort oyunu. Duyarlılık: 0,60 / 0,80.
  Bir oyun birden çok öncüye benziyorsa en benzer öncüye atanır.
- **Plasebo öncü:** Her öncü için aynı çıkış ayından, aynı ana türde, ilk yılı 100–499 inceleme (T2) olan rastgele bir oyun
  (sabit tohum). Dalga ölçüsü plaseboyla kıyaslanır: "hit'in etrafı zaten kalabalık bir bölge mi?" sorusunu ayırır.
- **Dalga ölçüsü:** Öncü çıkışına göre −12 … +24 ay boyunca her ay çıkan benzer (≥ 0,70) oyun sayısı ÷ o ay Steam'e çıkan toplam
  oyun (arz büyümesini nötrler). Öncü ve plasebo için ortalama eğri; "sonrası/öncesi" oranı.
- **Takipçi başarısı:** Takipçilerin (analiz örneklemindeki) hit oranı, öncüden sonraki zamana göre: 0–6, 6–12, 12–24 ay.
  Karşılaştırma: plasebo öncülerin aynı benzerlikteki "takipçileri" ve örneklem ortalaması.
- **Web için:** En kalabalık 10 dalga (öncü adı + takipçi sayısı + takipçi hit oranı).
- **Dikkat:** Etiketler çıkıştan sonra oylanıyor (R4); "Survivors-like" gibi etiketler öncüden sonra doğabilir. Bu, benzerliği
  dalga yönünde şişirebilir. Takipçi = "benzer etiketli sonraki oyun", ilham aldığı kanıtlanmış oyun değil.

## K6: Boş yıldız bölgeleri (az rakip, çok başarı)

**Soru:** İçerik uzayında, az oyun çıkan ama çıkanların beklenenden sık tuttuğu bölgeler var mı?

- **Bölgeler:** Kohort oyunlarının içerik vektörleri üzerinde küresel k-ortalamalar (L2 normalize, k = **60**, `random_state=20261025`,
  ≥ 3 içerik etiketi). Bölge adı = bölge ortalamasında genel ortalamaya göre en belirgin 3 etiket.
- **Arz:** Bölgeye 2022–2025 arasında çıkan oyun sayısı (tüm kohort) ve 2020–21 → 2024–25 büyümesi.
- **Başarı:** Analiz örnekleminde gözlenen hit sayısı ÷ **beklenen** hit sayısı (O/B). Beklenen = standart kontrollerle (yıl, ana tür,
  fiyat bandı, EA, log dil sayısı; `ortak_model.KONTROL`) kurulan lojistik modelin tahmini olasılıklarının toplamı. Böylece "bölge iyi
  çünkü pahalı oyunlar var" etkisi ayrılır. Ham hit oranı da raporlanır.
- **Fırsat bölgesi:** O/B'nin %95 GA alt sınırı > 1 **ve** arz payı medyanın altında. GA: Poisson (gözlenen hit sayısı üzerinden).
- **Yalnız ≥ 200 örneklem oyunu olan bölgeler** değerlendirilir.
- **Dikkat:** Fırsat ≠ boş alan garantisi. O/B yüksekliği talep kadar bölgedeki oyunların ölçülmeyen kalitesini de yansıtabilir.
  Ayrıca etiketler başarıdan etkilenir (R4).

## K7: Gizli hazineler

**Soru:** Çok beğenilen ama kimsenin görmediği oyunlar, çok beğenilip görünür olanlardan neyle ayrılıyor?

- **Gizli hazine:** 10 ≤ reviews_365 < 100 ve beğeni Wilson alt sınırı (365 gün) ≥ 0,80. (Wilson şartı fiilen ≥ ~20 inceleme gerektirir.)
- **Görünür hazine:** reviews_365 ≥ 500 ve beğeni Wilson alt sınırı ≥ 0,80.
- **Karşılaştırma:** Çıkış öncesi bilinen nitelikler: fiyat bandı, F2P, dil sayısı, Çince, EA, ana tür, demo (çıkış öncesi), stüdyonun
  önceki oyunu, kendi yayını, içerik etiket sayısı, yenilik, çıkış ayı, aynı hafta çıkan oyun sayısı. İki grup arası standartlaştırılmış
  fark (SMD) + tek lojistik model (görünür = 1) ile kontrollü olasılık oranları.
- **Web için:** Rastgele değil, en yüksek Wilson alt sınırlı 12 gizli hazine (ad + yıl + tür).
- **Dikkat:** Az incelemeli oyunlarda olumlu oran arkadaş/aile incelemeleriyle şişebilir; "gizli hazine" listesi kalite garantisi değil.
  Demo bilgisi şu an mağazada olanı gösterir (kaldırılmış demolar R13: Steam API anahtarı gelince düzelir).

## K8: Steam algoritması eşiği

**Soru:** Bir oyun belli bir toplam inceleme sayısını geçince ilgisi sıçrıyor mu?

- **Eşikler:** **10** (Steam mağazada inceleme puanını 10 kullanıcı incelemesinden sonra gösterir; olgu) ve **50** (geliştirici
  topluluğunda yaygın kanı). Plasebo eşikler: 20, 30, 40, 60, 70, 80.
- **Veri:** İnceleme serisi (aylık/haftalık dilimler). Gözlem = oyun-dilim; çalışan değişken c = dilim başındaki toplam inceleme;
  sonuç = dilimdeki inceleme hızı, log(1 + inceleme / gün × 30). Çıkış dilimi ve çıkıştan sonraki ilk 30 gün dışarıda (lansman zirvesi).
- **Tahmin:** Her eşik t için bant [0,5t, 1,5t) içinde yerel doğrusal regresyon, iki tarafta ayrı eğim; sıçrama = c ≥ t kuklasının
  katsayısı. Standart hata oyun düzeyinde kümelenmiş. Sonuç: gerçek eşiklerdeki sıçrama, plasebo dağılımının dışında mı?
- **Alt grup:** Eşiği yüksek beğeniyle (olumlu ≥ %80) ve düşük beğeniyle geçenler: puanın görünmesi iyi puana yarar, kötüye zarar
  verirse sıçrama yönleri ayrışmalı.
- **Dikkat:** Seri yalnız ömür boyu ≥ 10 incelemeli oyunlar için çekildi: 10 eşiğinin altındaki gözlemler "eninde sonunda 10'u geçen"
  oyunlardan oluşur, bu da eşik altını şişirip sıçramayı küçültür (temkinli yönde yanlılık). 50 eşiğinde bu sorun yok. Aylık dilimlerde
  eşik ay içinde geçilir; etki kısmen aynı dilime düşer (yine temkinli yön).

## K9: Mağaza açıklaması ne söylüyor? (eklendi 2026-10-25, sonuçlara bakılmadan)

**Soru:** Oyunun mağaza metni (ne vaat ettiği, nasıl anlattığı) başarıyla birlikte görülüyor mu, ve K4'ün çıkış öncesi modeline bilgi katıyor mu?

- **Metin:** FronkonGames anlık görüntüsündeki (Şubat 2026) kısa açıklama + uzun açıklamanın HTML'siz ilk 1.500 karakteri. Yalnız
  analiz örneklemi; harflerinin ≥ %80'i Latin olan (İngilizce ağırlıklı) metinler.
- **Sızıntı koruması (en önemli kısım):** Metin bugünkü hâli; başarılı oyunlar sayfalarına ödül, satış, puan ve basın alıntısı ekliyor.
  Şu kalıpları içeren **cümleler metinden atılır**: award / winner / nominee / nominated, sold / copies / million / players worldwide,
  best seller / bestselling, overwhelmingly / very positive / review(s), rating / score / metacritic, tırnak içi alıntı + basın adı
  (IGN, PC Gamer, Rock Paper Shotgun, Polygon, Kotaku, GameSpot, Eurogamer, Destructoid), "out now" / "now available" / "update" /
  "DLC" / "1.0" / "full release". Tanı: kalıp oranı hit'lerde ve diğerlerinde ayrı raporlanır.
- **Ön tanımlı üslup ölçüleri:** uzunluk (log karakter), ünlem sayısı (1.000 karakterde), BÜYÜK HARF kelime payı, "you/your" payı,
  somut içerik sayısı ("50 levels", "100+ weapons" gibi sayı + isim kalıbı), abartı sıfatları (unique, innovative, revolutionary,
  epic, amazing, ultimate, best, incredible, stunning, masterpiece, first ever, never before) 1.000 karakterde.
- **Modeller (zamansal bölme K4 ile aynı: eğitim ≤ 2023, test 2024–2025, ölçü PR-AUC + ROC-AUC, %95 GA paired bootstrap):**
  (a) TF-IDF (1–2 kelime, min_df 20) + lojistik regresyon; C, 2023'ü doğrulama yılı alarak seçilir.
  (b) Cümle gömmesi (yerel `sentence-transformers/all-MiniLM-L6-v2`, 384 boyut) + lojistik regresyon.
  (c) K4 ana model nitelikleri + metin skoru (eğitimde 5 katlı katlar-dışı tahmin, sızıntısız yığınlama) LightGBM; K4 ana modeliyle
  aynı test kümesinde karşılaştırılır. Fark GA'sı 0'ı içeriyorsa "metin ek bilgi katmıyor".
- **Yorum:** TF-IDF modelinin en güçlü olumlu/olumsuz kelimeleri ve üslup ölçülerinin hit oranıyla ilişkisi (kontrollü lojistik).
- **Dikkat:** Sızıntı filtresi kusursuz değil; metin sonradan baştan yazılmış da olabilir. Bu yüzden (c)'deki artış üst sınır sayılır.

## Değişiklik günlüğü

- 2026-10-25: İlk sürüm.
- 2026-10-25 (K5, ilk çalıştırmadan sonra): Öncü ve takipçi evreninden bayraklı oyunlar (yetişkin, seri üretici, yazılım şüphesi,
  listelenmemiş) çıkarıldı. Gerekçe: analiz örneklemi bunları zaten dışlıyor; ilk çalıştırmada en kalabalık "dalgaların" yetişkin
  içerik ve seri üretim (hidden object) kümeleri olduğu görüldü, bunlar klon dalgası değil üretim kalıbı. Bu, sonucun yönünü görerek
  yapılmış bir değişikliktir; ilk çalıştırmanın sayıları da kayda geçti: dalga oranı öncü 1,06 (0,96–1,16), plasebo 0,89; takipçi hit
  oranı (0,70) %15,4, plasebo benzerleri %7,7. "En büyük dalgalar" listesi artık her öncünün kendi dalgasını sayıyor (en benzer öncüye
  atama yalnız başarı karşılaştırmasında kullanılıyor; listede atama dalgaları bölüyordu).
- 2026-10-25 (K6, ilk çalıştırmadan sonra): Tanımlayıcı etiketleri Sexual Content / Nudity / Hentai olan bölgeler "fırsat" sayılmıyor
  (grafikte gri kalıyor, tabloda duruyor). Gerekçe: ilk çalıştırmada en yüksek O/B bu bölgelerdeydi (×5,2 ve ×2,0). Projenin yetişkin
  tanımı (T06) Steam içerik uyarısına (3, 4) dayanıyor; analiz örnekleminde 2.324 oyun (%3,5) uyarısız ama bu etiketleri taşıyor.
  Etiket temiz bir yetişkin göstergesi değil (Train Sim World 2 gibi oyunlarda da var), bu yüzden örneklem değiştirilmedi; yalnız
  geliştiriciye "fırsat" diye sunulacak listeden çıkarıldı. Değer yargısıdır, sonuç görülerek yapıldı.
- 2026-10-25 (K8, ilk çalıştırmadan sonra): 10 eşiğinde −%6,6 düşüş çıktı; plandaki "Dikkat" notunda öngörülen seçilim (seri yalnız
  ömür boyu ≥ 10 oyunlarda) bunu üretebilir. Ek duyarlılık eklendi: yalnız ömür boyu ≥ F (15, 30, 100, 300) incelemeli oyunlar; F büyüdükçe
  iki yanın koşulu eşitlenir. Sonuç: F = 30'da −%4,8, F = 100'de +%0,5 (geniş GA). 10'daki düşüş yorumlanmaz; ana sonuç 50 eşiği.
- 2026-10-25 (K9, ilk çalıştırmadan sonra): TF-IDF belirteç deseni düzeltildi; varsayılan desen "co-op"u "co" + "op" diye bölüyordu (en güçlü
  terim "op" çıktı). Tireli kelimeler artık bütün. İlk çalıştırma: K4 0,268 → K4 + metin 0,314 (fark +0,046; GA +0,028…+0,064). Ayrıca
  kelime grafiğinde çıkıştan sonra eklenmesi olası ifadeler (new, edition, discord, community, free…) gri ve yıldızlı gösteriliyor;
  modelden çıkarılmadılar (plan dışı müdahale olurdu), artış zaten üst sınır olarak raporlanıyor.
