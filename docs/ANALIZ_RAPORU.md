# Discovery Dynamics: Analiz Raporu

*Steam'de bağımsız oyunlar nasıl görünür oluyor? Her modül kısa bir bölüm: soru, ne bulduk, ne anlama geliyor, nelere dikkat etmeli.*

**Okumadan önce bilinmesi gerekenler:**
- **Başarı ölçüsü:** Oyunun ilk 365 günde aldığı Steam incelemesi. Steam satış rakamı yayınlamıyor; inceleme sayısı satış sıralamasını iyi izliyor (sıra korelasyonu 0,59). "Hit" = ilk yılda 500+ inceleme. Her bulgu ayrıca beğeni, tahmini gelir ve göreli sıra ölçüleriyle kontrol ediliyor (bkz. M1 §6).
- **Örneklem:** 2018–2025 arasında çıkan, büyük yayıncı desteği olmayan ("organik") 66.999 oyun. Seri üretim, yetişkin içerik, yazılım ve listelenmemiş oyunlar çıkarıldı.
- **İlişki ≠ neden-sonuç.** Aksi yazılmadıkça bulgular "birlikte görülüyor" demektir. Neden-sonuç iddiası yalnız M5'te (demo ve Next Fest) kurulacak.
- Grafiklerin verileri aynı adla `analysis/sekiller/*.csv` olarak duruyor. Yöntem ayrıntıları: `docs/PILOT_RAPORU.md`, `docs/VERI_RAPORU.md`.

---

## Kısa özet (2026-10-24)

### Ön kayıtlı hipotezler

| Hipotez | Konu | Tek yönlü p | Holm p (geçici, 5 test) | Sonuç | Not |
|---|---|---|---|---|---|
| H1 | Yenilik ters U (M3) | 1 | 1 | **desteklenmedi** | β₂ anlamsız; eğim iki uçta negatif (ilişki azalan) |
| H4 | Early Access → uzun kuyruk (M4) | 6.2e-46 | 2.5e-45 | **desteklendi** | OR 1.27 (1.23–1.31); PSM +6.7 puan |
| H5 | İkinci oyun daha başarılı (M6) | 1 | 1 | **desteklenmedi** | FD -12%; en temiz ölçümde -5% |
| H6 | Çince desteği (M2) | 2.2e-158 | 1.1e-157 | **desteklendi** | +%57–75; ters nedensellik payı var (M2b) |
| H7 | Doygunluk (M2) | 1 | 1 | **desteklenmedi** | OR 1.06: ters yönde (aynı tür içinde kalabalık dezavantaj değil) |
| H2 | Demo etkisi (M5) | — | — | bekliyor | Steam API anahtarı (kaldırılmış demolar, R13) |
| H3 | Next Fest etkisi (M5) | — | — | bekliyor | Steam API anahtarı; dolaylı gösterge duyarlılığı ~%53 |
| H8 | Mikro/makro içerik üreticisi (M8, ayrı aile) | — | — | test edilemiyor (şimdilik) | Steam tam inceleme geçmişini kapattı; seçenekler HIPOTEZLER'de |

*Hipotezler yönlü olduğu için Holm düzeltmesine öngörülen yöndeki tek yönlü p girer; ters yönde anlamlı bir sonuç (H7) desteklemez. Aile tamamlanınca (H2, H3) düzeltme yeniden hesaplanacak; desteklenen iki hipotezin p değerleri kararı değiştirmeyecek kadar küçük. Üretim: `analysis/hipotez_ozeti.py`.*

### En önemli 10 bulgu

1. **Görünmezlik yaygın ama sabit:** Bağımsız oyunların %54'ü ilk yılında 10'dan az inceleme alıyor, %5'i hit oluyor. Steam'e çıkan oyun 2,9 katına çıktığı halde bu oranlar 2018–2024 arasında değişmedi (M1).
2. **Başarı türe ve fiyata göre 10 kattan fazla değişiyor:** 5 USD altında her türde hit oranı %0,4–2; 20 USD üstünde Action, RPG, Strategy ve Simulation'da %28–42. Fiyat büyük ihtimalle kapsamı ve bütçeyi yansıtıyor (M1, K1).
3. **Tanıdık kazanıyor:** Ön kayıttaki "orta düzeyde yenilik en iyisi" (ters U) hipotezi tutmadı. Etiket kombinasyonu ne kadar alışılmadıksa beklenen inceleme o kadar az (M3).
4. **Kalabalık tür dezavantaj değil:** Aynı tür içinde kalabalık alt türler biraz daha iyi; muhtemelen talep işareti (M2, H7).
5. **Birlikte oynanan oyunlar öne çıkıyor:** Multiplayer, Online Co-op ve Co-op etiketleri ×2,7–3,4. Motivasyon haritasında "Design" ve "Community" az arz ve yüksek başarı bölgesinde (M2, keşifsel).
6. **Çince desteği güçlü biçimde başarıyla birlikte, ama bir kısmı ters nedensellik:** Başarılı oyunlar Çince'yi sonradan 13 kat daha sık ekliyor; en temkinli tahmin +%57 (M2).
7. **Uzun soluklu ilgi kazandırıyor:** Early Access oyunlarının ilgisi zamana daha yayılmış (H4). İlgisi iki yıl süren oyunların hit oranı, patlayıp sönenlerin 2 katı (M4).
8. **İkinci oyun ilkinden iyi değil:** İlk oyunu görünmez kalan stüdyoların %77'si ikincide de görünmez (M6).
9. **Lansman ayı yılı belirliyor:** İlk 30 gün ile ilk yıl arasındaki sıra korelasyonu 0,93; tipik oyun yılı ilk ayının ~2,2 katıyla kapatıyor (K3).
10. **Yapay zekâ beyan eden oyunların %65'i görünmez kalıyor, beyan etmeyenlerde %39** (kontrollü odds oranı ×3,0; 2024–2025; ilişki, neden-sonuç değil) (K2).

### Ek keşifsel bulgular (K5–K8, 2026-10-25)

11. **Hit'i taklit etmek ek avantaj sağlamıyor:** Takipçilerin %15,5'i hit, ama hit'ten *önce* aynı bölgeye çıkanların da %16,7'si. Avantaj bölgeden; 12–24 ay geç kalan takipçiler %13,7'ye düşüyor. "Klon seli" de yok (K5).
12. **İki sağlam fırsat bölgesi:** Cozy/Wholesome (beklenenin 2,3 katı hit, ama arzı Steam'in 6,9 katı hızla büyüyor) ve Dating Sim/Visual Novel (×2,0). Üçüncü aday Dedektif/Gizem (×1,5) yalnız 2021+ oyunlarla bakınca anlamlılığını yitiriyor (K6, duyarlılık).
13. **Çok beğenilen oyunların %44'ü gizli kalıyor:** Görünür hazineleri ayıranlar Simulation türü, daha yüksek fiyat, Early Access, Playtest ve deneyim; demo ayırmıyor (K7).
14. **"50 incelemeyi geç, algoritma seni görsün" veride yok:** Eşikte sıçrama −%1,0 (GA −%2,4 … +%0,4); ilgi pürüzsüz büyüyor (K8).
15. **Türlerin risk-ödül karnesi:** Management, Dating Sim, City Builder ve Sandbox hem az riskli hem ödüllü (hit %10–12); Runner, Precision Platformer ve Logic en zor (hit < %2). Tür karışımları ise parçalarının toplamı kadar: 176 çiftin hiçbiri beklenenden farklı değil. Anlamlı eğilimlerin hepsi düşüş: Auto Battler, Idler, Roguelike (K10).
16. **Veri kalitesi:** Oyuncu etiketleri 2021 öncesi seçilimli (eski yıllarda başarılı oyunlar daha çok etiket taşıyor). Etiket tabanlı bulgular 2021+ ile yeniden hesaplandı; Dedektif/Gizem fırsatı dışında hepsi geçerli (duyarlılık bölümü).

### Bu analizlerde bulunup düzeltilen önemli hatalar

Steam'in yeniden yayınlarda sıfırladığı çıkış tarihleri; eşleştirme dengesizliği; dondurulmuş açık veri setinin "bağımsız" sanılması; log eksende sessizce kaybolan veri noktası; Early Access'in kendisiyle tahmin edilmeye çalışılması; sonradan eklenen dil bilgisinin tahmin modeline sızması; ölçüm artefaktının "ikinci oyun daha kötü" gibi görünmesi. Her biri ilgili bölümde ve commit geçmişinde.

---

## M1: Görünürlük: oyunların ne kadarı fark ediliyor?

*Betik: `analysis/m1_gorunurluk.py` · 2026-10-24*

### 1. Her iki bağımsız oyundan biri ilk yılında 10 inceleme bile alamıyor

![Kademe dağılımı](../analysis/sekiller/M1_1_kademe_yil.png)

- Bağımsız oyunların **%54'ü** ilk yılında 10'dan az inceleme aldı. Bu, kabaca birkaç yüz satış demek.
- Yalnız **%5'i** hit oldu (500+ inceleme, kabaca on binlerce satış).
- Tablo 2018'den 2024'e şaşırtıcı derecede sabit. Her yıl kabaca aynı dağılım tekrarlanıyor.

### 2. Steam'e çıkan oyun 2,9 katına çıktı, ama öne çıkma şansı azalmadı

![Arz ve hit oranı](../analysis/sekiller/M1_2_arz_ve_hit.png)

- Yıllık çıkan oyun 7,1 binden 20,4 bine çıktı.
- Bağımsız oyunların hit oranı ise **%4–5,5 bandında kaldı.** Mutlak hit sayısı 2018'de 231'den 2024'te 595'e çıktı.
- **Anlamı:** "Steam artık çok kalabalık, şans kalmadı" algısı veride görünmüyor. Kalabalık büyüdükçe görünür olan oyun sayısı da büyüyor. Rekabet artıyor, ama pay sabit.

### 3. Tür ve fiyat birlikte başarı şansını 10 kattan fazla değiştiriyor

![Tür ve fiyat](../analysis/sekiller/M1_3_tur_fiyat.png)

- 5 USD altı oyunlarda hit oranı her türde %0,4–2. 20 USD üstünde Action, RPG, Strategy ve Simulation'da **%28–42**.
- Casual oyunlar fiyat artınca diğerleri kadar yükselmiyor (20–30 USD'de %16,5).
- Ücretsiz (F2P) oyunlar %7–10 bandında. Ama bedava oyunun oyuncu başına inceleme oranı farklı olduğundan ücretli oyunlarla doğrudan karşılaştırılmamalı.

### 4. Diğer her şey sabitken: fiyat, yerelleştirme ve deneyim öne çıkıyor

![Model](../analysis/sekiller/M1_4_model.png)

54.371 ücretli bağımsız oyunla yıl sabit lojistik regresyon. Değerler "hit olma ihtimali kaç kat":
- **Fiyat:** 20 USD üstü ×7, 10–20 USD ×2,5, 5 USD altı ×0,4 (hepsi 5–10 USD'ye göre).
- **Dil sayısı:** Daha çok dil desteği ×2,6 (log ölçek).
- **Geliştiricinin önceki oyunu var:** ×1,6. Ayrıntısı M6'da.
- **Tür:** Simulation ×1,8 ve RPG ×1,7 avantajlı; Sports ×0,5, Racing ×0,6 ve Casual ×0,8 dezavantajlı.
- **Kendi yayını:** ×0,63. Küçük bir yayıncıyla çıkan oyunlar daha sık başarılı.
- **Early Access ile çıkış:** ×1,2.

**Bunu nasıl okumamalı:** "Fiyatını artır, şansın 7 katına çıksın" **değil.** Fiyat büyük ihtimalle oyunun kapsamını, üretim kalitesini ve geliştiricinin özgüvenini yansıtıyor. 30 USD'lik bağımsız oyun genelde daha büyük bir projedir. Aynı şekilde çok dil desteği bütçeyi, küçük yayıncı da yayıncının iyi projeleri seçmesini yansıtabilir. Fiyatın veriyle izin verilen ölçüde ayrıntılı incelemesi K1'de yapılacak.

**Fiyat hakkında not:** Kullanılan fiyat çıkış fiyatı değil, Ekim 2026'daki liste fiyatı. Başarısız oyunlar sonradan fiyat düşürmüş olabilir; bu da ilişkiyi kısmen şişirebilir.

### 5. Steam'deki "gürültü" büyüyor

![Gürültü](../analysis/sekiller/M1_5_gurultu.png)

- Yetişkin cinsel içerikli oyunların çıkan oyunlar içindeki payı 2018'de %2,2'den 2025'te **%8,3'e** çıktı (3,8 kat).
- Yılda 12'den fazla oyun çıkaran seri üreticiler her yıl %5–9.
- 40'tan fazla dili desteklediğini iddia eden "dil spam'i" oyunları %0,8'den %2,4'e çıktı.
- Bunlar analizden çıkarıldı. Çıkarılmasalardı "görünmez oyun" oranı olduğundan yüksek, başarı oranı olduğundan düşük görünürdü.

### 6. Başarının dört yüzü: "hit" tek başına yetmiyor

*Betik: `analysis/m1b_basari_yuzleri.py`. Ölçüler sonuçlara bakılmadan tanımlandı (HIPOTEZLER, 2026-10-24).*

Başarıyı tek bir sayıyla ölçmek yerine dört açıdan bakıyoruz: **görünürlük** (inceleme sayısı), **beğeni** (olumlu oran), **ticari** (tahmini gelir) ve **göreli** (aynı yıl ve türdeki rakiplere göre sıra).

![Başarı sınıfları](../analysis/sekiller/M1_6_basari_siniflari.png)

- Hit'lerin **%74'ü gerçekten sevilen oyunlar** (%80+ olumlu). "Çok satıp sevilmeyen" tartışmalı hit'ler nadir: oyunların %0,5'i.
- **Sessiz başarı** (50–499 inceleme ama çok beğenilmiş) oyunların %4,7'si; sevilen hit'ler (%3,6) kadar yaygın. Bu oyunlar küçük ama sadık bir kitle bulmuş. "Hit değil" diye başarısız sayılmamalı.

![Görünürlük ve para](../analysis/sekiller/M1_7_gorunurluk_para.png)

- Tahmini brüt geliri 100 bin USD'yi geçen 3.310 ücretli bağımsız oyunun **%35'i (1.166) "hit" sayılmıyor.** Bunlar 10–40 USD'ye satılan, 150–500 inceleme alan oyunlar: görünürlükleri orta, ama fiyatları sayesinde muhtemelen ayakta kalıyorlar.
- Tersi de var: 194 hit 100 bin USD'nin altında kalıyor; neredeyse hepsi 5 USD ve altındaki oyunlar.
- **Anlamı:** Geliştirici açısından "hit olmak" ile "geçimini çıkarmak" farklı hedefler. Düşük fiyatla çok görünür olmak, yüksek fiyatla orta görünürlükten daha az kazandırabiliyor.
- **Dikkat:** Gelir kaba bir tahmin (inceleme × 30 × fiyat; ×20–40 aralığı). Steam'in %30 payı, indirimler, bölgesel fiyatlar ve iadeler öncesi brüt değer. Net gelir kabaca bunun yarısı. Fiyat formülün içinde olduğu için bu ölçü fiyat analizinde sonuç olarak kullanılmayacak.

![Sağlamlık](../analysis/sekiller/M1_8_saglamlik.png)

- M1 modeli üç farklı başarı tanımıyla yeniden kuruldu: hit, sevilen hit, yılı ve türünde ilk %10. **9 etkenin 8'inin yönü üç tanımda da aynı.** Dil sayısı, önceki oyun deneyimi, küçük yayıncıyla çıkmak, Early Access, Simulation ve RPG her tanımda olumlu; Sports ve Racing her tanımda olumsuz.
- Tek fark Casual'da: "yılı ve türünde ilk %10" ölçüsünde nötr çıkıyor. Bu beklenen bir sonuç, çünkü bu ölçü oyunu kendi türündeki rakipleriyle karşılaştırıyor ve türler arası farkı tanım gereği siliyor. Yani Casual oyunlar genel olarak daha az hit oluyor, ama Casual içinde başarılı olmanın koşulları diğer türlerden farklı değil.
- **Sonuç:** M1'in bulguları "başarıyı nasıl tanımladığımıza" bağlı değil. Bu, bulgulara güveni artırıyor.

### M1 özeti

| Bulgu | Güven | Not |
|---|---|---|
| Bağımsız oyunların %54'ü ilk yılında < 10 inceleme | Yüksek | Yıllar arasında tutarlı |
| Arz 2,9 kat arttı, hit oranı %4–5,5'te sabit | Yüksek | Mutlak hit sayısı 2,6 kat arttı |
| Yüksek fiyat, çok dil ve deneyim başarıyla birlikte görülüyor | Yüksek (ilişki) | Neden-sonuç değil; büyük ihtimalle bütçe ve kapsamı yansıtıyor |
| Simulation ve RPG avantajlı, Sports, Racing ve Casual dezavantajlı | Orta | Tür etiketleri geliştiricinin seçimi; birden çok tür olabilir |
| Yetişkin içerik payı 3,8 katına çıktı | Yüksek | Tüm kohort |
| Hit'lerin %74'ü sevilen hit; sessiz başarı (%4,7) sevilen hit (%3,6) kadar yaygın | Yüksek | Steam'in puan ölçeğine göre |
| 100 bin USD'yi geçenlerin %35'i hit değil | Orta | Gelir kaba tahmin (×20–40 aralığı) |
| Etkenlerin 8/9'u üç farklı başarı tanımında aynı yönde | Yüksek | Casual farkı ölçünün yapısından |

---

## M2: İçerik DNA'sı: neyin içinde olduğu fark yaratıyor mu?

*Betikler: `analysis/m2_icerik.py`, `analysis/m2b_cince_ters_nedensellik.py` · 2026-10-24. Doğrulayıcı testler: H6, H7. Holm düzeltmesi H1–H7 ailesi tamamlanınca uygulanacak; p değerleri şimdilik ham.*

### H6: Basitleştirilmiş Çince desteği: **desteklendi (ilişki), ama bir kısmı ters nedensellik**

![H6](../analysis/sekiller/M2_1_H6_cince.png)

- Diğer her şey sabitken Çince arayüz desteği olan oyunlar ilk yılında **%75 daha fazla inceleme** alıyor (%95 GA: 68–83). Eğilim skoru eşleştirmesiyle +%64 (58–71); eşleştirme dengesi bütün kontrollerde iyi (en büyük fark 0,056 < 0,1).
- **Ama başarılı oyunlar Çince'yi sonradan ekliyor:**

![Ters nedensellik](../analysis/sekiller/M2_5_H6_ters_nedensellik.png)

- Şubat'tan Ekim 2026'ya, sadece 8 ayda, en başarılı oyunların %6,1'i Çince ekledi; en alttakilerin %0,5'i (13 kat fark). Yani "Çince → başarı" ilişkisinin bir kısmı aslında "başarı → Çince".
- Çıkışa en yakın dil durumunu kullanan en temkinli tahmin **+%57** (41–74). Bu da çıkıştan 5–13 ay sonrasını yansıttığı için bir **üst sınır** olarak okunmalı.
- **Geliştirici için anlamı:** Çince desteği güçlü biçimde başarıyla birlikte görülüyor ve etki ters nedensellik ayıklandıktan sonra da büyük kalıyor. Yine de "Çince ekle, %57 daha çok inceleme al" demek için neden-sonuç tasarımı gerekir. Bu veriyle mümkün değil, çünkü çıkış günündeki dil listesi gözlenmiyor.
- Ön kayıttaki yan kanıt (Çince yazılmış incelemelerin payı) inceleme dili verisi gerektiriyor; **test edilemedi.**

**Bu analizde düzeltilen iki hata:**
1. İlk eşleştirme yalnız eğilim skoruyla yapılmıştı ve Action/RPG türlerinde denge ölçütünü tutturamadı (fark 0,17). Tür kombinasyonu ve fiyat bandında birebir eşleştirme eklenince düzeldi.
2. Ters nedensellik testinin ilk sürümünde "Şubat" ve "Ekim" için iki farklı açık veri seti kullanılmıştı ve test sıfır değişiklik buldu. Kontrol edince iki setin 122.876 oyunda birebir aynı olduğu anlaşıldı: FronkonGames'in oyun bilgileri Şubat 2026'da donmuş. Test, Ekim durumu için kendi Steam çekimimizle yeniden kuruldu.

### H7: Doygunluk: **desteklenmedi**

![H7](../analysis/sekiller/M2_2_H7_doygunluk.png)

- Ham tabloda kalabalık kombinasyonlarda hit oranı biraz düşük (%5,5'ten %4,7'ye).
- Ama ön kayıtlı test (tür sabit etkisi ve kontrollerle) ilişkinin **tersine** döndüğünü gösteriyor: aynı ana tür içinde daha kalabalık kombinasyonlarda başarı ihtimali biraz **daha yüksek** (log birim başına OR 1,06; %95 GA 1,03–1,09). Diğer doygunluk ölçüsüyle de aynı (OR 1,05).
- **Yorum:** Düşüş türler arası farktan geliyor: kalabalık türler (Casual, Action) zaten daha az hit veriyor. Aynı tür içinde ise kalabalık bir alt tür, büyük ihtimalle oyuncu talebinin işareti. "Kalabalık alandan kaç" tavsiyesi veriyle desteklenmiyor; "talebin olduğu yerde ol" daha yakın.

### Keşifsel: Hangi içerik etiketleri başarıyla birlikte görülüyor?

![Etiketler](../analysis/sekiller/M2_3_etiket_etkileri.png)

- 66 mekanik, görsel ve oyuncu yapısı etiketi test edildi; 36'sı çoklu test düzeltmesinden (BH, q < 0,05) sonra da anlamlı.
- **En güçlü olumlu ilişkiler oyuncu yapısında:** Multiplayer ×3,4, Online Co-Op ×3,2, Co-op ×2,7, eSports ×2,1. Hikâye mekanikleri de olumlu: Multiple Endings ×2,05, Choices Matter ×1,7. Görselde Anime ×1,8 ve Cinematic ×1,7.
- **Olumsuz:** Grid-Based Movement ×0,29, Comic Book ×0,42, 4 Player Local ×0,43, Score Attack ×0,44, Abstract ×0,46. Ayrıca yaygın görsel tercihler (Top-Down, Colorful, Side Scroller, 2.5D) ×0,55–0,63.
- **Dikkat:** Çok oyunculu oyunlar oyuncu başına daha çok inceleme alıyor olabilir (arkadaşlarla oynanır, topluluk büyür). Ayrıca etiketler oyuncu oyuyla şekillendiği için başarı etiketleri de etkileyebilir (R4). Bunlar keşifsel ilişkiler.

### Keşifsel: Oyuncu motivasyonu haritası

![Motivasyon](../analysis/sekiller/M2_4_motivasyon_haritasi.png)

- **"Fırsat bölgesi"** (az arz, yüksek başarı): **Design** (yaratma, inşa, kişiselleştirme; oyunların %1,2'si, hit oranı %14) ve **Community** (birlikte oynama; %3,7 arz, %13 hit).
- **En kalabalık ve en zor:** **Excitement** (aksiyon heyecanı; oyunların %25'inin baskın motivasyonu, hit oranı %3) ve **Challenge** (zorluk; %9 arz, %3,2 hit).
- **Dikkat:** Ham oranlar (tür ve fiyat kontrolü yok). Etiket–motivasyon eşlemesi tek kodlayıcı taslağı; ikinci kodlayıcı (Mert) beklendiği için bu harita **ön bulgu**.

### M2 özeti

| Bulgu | Sonuç | Not |
|---|---|---|
| H6 · Çince desteği | **Desteklendi (ilişki)**: +%57 ile +%75 arası | Ters nedensellik kanıtlandı; +%57 en temkinli, yine de üst sınır |
| H7 · Doygunluk | **Desteklenmedi**: aynı tür içinde katsayı pozitif (OR 1,06) | Ham düşüş türler arası farktan |
| Çok oyunculu / co-op | ×2,7–3,4 (keşifsel) | Oyuncu başına inceleme farkı olabilir |
| Fırsat motivasyonları: Design, Community | Az arz, ~%13–14 hit (keşifsel, ham) | Eşleme taslak |

---

## M3: Yenilik: "tanıdık ama farklı" mı kazanıyor?

*Betik: `analysis/m3_yenilik.py` · 2026-10-24. Doğrulayıcı test: H1. Yenilik ölçüsü = oyunun etiket kombinasyonunun, kendisinden önce çıkmış en benzer 10 oyuna uzaklığı (mekanik buluşu değil, etiket kombinasyonunu ölçer).*

### H1: Ters U: **desteklenmedi**

![H1](../analysis/sekiller/M3_1_H1_yenilik.png)

- Ön kayıt, orta düzeyde yenilikçi oyunların en iyi sonucu alacağını (ters U) öngörüyordu. Veri bunu desteklemiyor: test penceresinde (oyunların %90'ı) ilişki **tek yönlü ve azalan.**
  - Eğim pencerenin iki ucunda da negatif ve anlamlı (t = −11,1 ve −9,2).
  - Kuadratik terim anlamsız (p = 0,39).
  - Lind–Mehlum p = 1.
- **Büyüklük:** Diğer her şey sabitken tipik bir oyunun beklenen ilk yıl incelemesi, yenilik skoru 0,11'den 0,44'e çıkınca kabaca **yarıya** iniyor.
- **Duyarlılık:** Komşu sayısı 5 ya da 20 alındığında, sonuç hit olarak ölçüldüğünde ve az oylanmış oyunlarda (R4) sonuç değişmiyor: ters U hiçbirinde yok. Az oylanmış oyunlarda yüksek yenilikteki düşüş de sürüyor (t = −2,6); bulgu etiket oylamasının bir yan ürünü değil.
- **Keşifsel ayrıntı:** Esnek eğri, test penceresinin altında (oyunların en tanıdık %5'i) bir tepe ve sonra düşüş gösteriyor. Etiketleri önceki oyunlarla neredeyse birebir aynı olan oyunlar da iyi yapmıyor olabilir. Bu bölgede veri az; ön kayıtlı test kapsamında değil.

![Ham](../analysis/sekiller/M3_2_yenilik_ham.png)

- Ham tabloda hafif bir tepe var (yenilik 0,21'de %5,9 hit), ama tür, fiyat ve yıl kontrol edilince kayboluyor. Ham tepe büyük ihtimalle tür karışımından geliyor.

**Geliştirici için anlamı:** "Biraz farklı ol" tavsiyesi veride görünmüyor. Etiket kombinasyonu olarak **tanıdık** oyunlar daha iyi yapıyor: oyuncular aradıkları türü bulabildiklerinde satın alıyor. Ama bu bulgu iki sınırla birlikte okunmalı:
1. Ölçü mekanik buluşu yakalamıyor. Vampire Survivors gibi türü değiştiren oyunlar etiket olarak "tanıdık" görünüyor (bkz. veri raporu).
2. Alışılmadık etiket kombinasyonu bazen sadece niş ya da deneysel bir projeye işaret ediyor olabilir.

En doğru özet: "Tanıdık bir kalıbın içinde fark yaratmak", "alışılmadık bir kalıp kurmaktan" daha güvenli görünüyor.

---

## M4: Yörüngeler: oyunların ilgisi zaman içinde nasıl değişiyor?

*Betik: `analysis/m4_yorunge.py` · 2026-10-24. Doğrulayıcı test: H4. Ölçüm ayrıntısı test öncesi kayda geçti (HIPOTEZLER).*

### H4: Early Access ve uzun kuyruk: **desteklendi**

![H4](../analysis/sekiller/M4_1_H4_early_access.png)

- İlk yılında 50+ inceleme alan 13.276 bağımsız oyunda, Early Access ile çıkanların incelemeleri zamana daha yayılmış. İlk yılın incelemelerinin 90. günden sonra gelen payının ortancası: **%42** (Early Access), **%37** (doğrudan tam sürüm).
- **Kontrollü model:** OR 1,27 (%95 GA 1,23–1,31). **Eşleştirilmiş karşılaştırma:** +6,7 puan (5,8–7,6). Eşleştirme dengesi çok iyi (en büyük fark 0,02).
- **Mekanizma:** Early Access oyunları genellikle ilk yıl içinde tam sürüme (1.0) geçiyor ve bu ikinci bir ilgi dalgası yaratıyor. Hipotezin öngördüğü "zamana yayılmış başarı" büyük ölçüde bu ikinci lansmanın etkisi olabilir.
- **Not:** Steam'in EA kaydı tutmadığı ve tarihini bizim düzelttiğimiz 808 oyunun bir kısmı aslında EA'ydı ama "EA değil" sayılıyor. Bu, farkı küçültme yönünde çalışır.

### Keşifsel: İnceleme eğrisi tipleri

![Yörüngeler](../analysis/sekiller/M4_2_yorunge_tipleri.png)

- 2 yılı gözlenmiş 10.333 oyunun aylık inceleme eğrisi kümelendi. Net ayrık tipler yok (siluet 0,15), eğriler bir süreklilik oluşturuyor. Üç tip bunun kaba bir özeti:
  - **Patlayıp sönen (%26):** İncelemelerin yarısından fazlası ilk ayda; ikinci yılda neredeyse hiç (%9). Hit oranı **%16**.
  - **Hızlı başlangıç (%48):** İlk ay güçlü, sonra yavaşça azalan. Hit oranı %24.
  - **Uzun soluklu (%26):** İlk ay görece küçük, sonra iki yıl boyunca düz ve kalıcı; ikinci yıl iki yıllık incelemelerin %36'sı. Hit oranı **%33**, sevilen hit oranı %27; üç grubun en yükseği. Early Access payı da en yüksek (%30).
- **Anlamı:** En başarılı oyunlar büyük bir lansman patlamasıyla değil, **kalıcı ilgiyle** başarıya ulaşıyor. Lansman haftasına her şeyi yatırmak yerine güncellemeler, içerik ve topluluk ile ilgiyi sürdürmek daha iyi sonuçla birlikte görülüyor.
- **Sınır:** Örneklem ilk yılında 50+ inceleme alanlarla sınırlı. Kümeleme yöntemi ön kayıttan saptı: DTW yerine aylık profillerde k-means (gerekçesi HIPOTEZLER'de).

---

## M6: İkinci oyun: stüdyolar ikinci denemede daha mı başarılı?

*Betik: `analysis/m6_ikinci_oyun.py` · 2026-10-24. Doğrulayıcı test: H5.*

### H5: İkinci oyun etkisi: **desteklenmedi**

![H5](../analysis/sekiller/M6_2_H5_ikinci_oyun.png)

- İlk iki oyunu da analiz örnekleminde olan 7.774 stüdyoda ikinci oyun ilkinden **daha başarılı değil.** Stüdyoların %41'i ikinci oyununda daha çok inceleme aldı. Birinci farklar modeli (stüdyo sabit etkisine denk; arada geçen süre, tür, fiyat, dil ve EA farkları kontrol edildi) ortalama **−%12** gösteriyor (%95 GA: −15 ile −8).
- **Sağlamlık:**

| Örneklem | Değişim | İyileşen |
|---|---|---|
| Ana | −%12 [−15, −8] | %41 |
| İkinci oyun büyük yayıncıyla da olabilir | −%12 [−16, −8] | %42 |
| Yalnız Steam sabit kimlikli stüdyolar (ad eşleşme hatası yok) | −%9 [−15, −1] | %44 |
| **Yalnız iki oyunu da tam seriyle ölçülenler** | **−%5 [−12, +2]** | %48 |

- Negatif farkın bir kısmı ölçümden geliyor. 10'dan az incelemeli oyunlarda ilk yıl değeri ömür boyu sayının üst sınırı; eski ilk oyun daha uzun süre biriktirmiş oluyor. En temiz ölçümde fark sıfırdan ayırt edilemiyor. **Doğru özet: ikinci oyunun daha iyi olduğuna dair kanıt yok.**
- **Kademeye göre:** İlk oyunu ne kadar başarılıysa ikinci oyun o kadar geride kalıyor (T2'de −%66, T4'te −%87). Bu büyük ölçüde **ortalamaya dönüş**: çok iyi giden bir ilk oyun kısmen şansla da iyi gitmiştir ve bunu tekrarlamak zordur.

![Geçişler](../analysis/sekiller/M6_1_kademe_gecis.png)

- İlk oyunu görünmez kalan (T0) stüdyoların **%77'si ikinci oyunda da görünmez** kalıyor. Sadece %3'ü 100+ incelemeye çıkıyor.
- İlk oyunu hit olan (T3) stüdyoların üçte biri yine hit yapıyor (%32 + %7). Bu, rastgele bir oyunun hit olma ihtimalinin (%5) yaklaşık 8 katı. **Başarı tekrarlanmıyor, ama tamamen şans da değil:** başarılı stüdyolar başarılı kalma eğiliminde.

**M1 ile çelişiyor mu?** M1'de "geliştiricinin önceki oyunu var" ×1,6 olumlu çıkmıştı. Çelişki yok, çünkü iki bulgu farklı şeyler ölçüyor:
- **M1 stüdyolar arası karşılaştırma:** ikinci oyun çıkaran stüdyolar, ilk oyunu iyi gittiği için devam eden seçilmiş bir grup.
- **M6 aynı stüdyonun içi:** aynı stüdyonun ikinci oyunu ortalamada ilkini geçmiyor.

**Geliştirici için anlamı:** "İlk oyun deneme, ikincide tutar" beklentisi veriyle desteklenmiyor. İlk oyunu görünmez kalan stüdyoların büyük çoğunluğu ikincide de görünmez kalıyor. Bir şeyin değişmesi gerekiyor: tür, kapsam, pazarlama, ya da M2–M4'teki etkenler.

---

## Keşifsel analizler (K1–K4)

*Ön kayıtta yoktu; sonuçlara bakılmadan 2026-10-24'te kayda geçirildi (HIPOTEZLER). Holm ailesinin dışında, "keşifsel" etiketiyle raporlanır.*

### K2: Yapay zekâ içerik beyanı

*Betik: `analysis/k2_yapay_zeka.py`*

![Yapay zekâ](../analysis/sekiller/K2_1_yapay_zeka.png)

- Steam Ocak 2024'ten beri oyunlarda yapay zekâ kullanımının beyan edilmesini istiyor. IGDB bu beyanları anahtar kelime olarak aktarıyor (görsel, müzik, ses, çeviri, pazarlama, kod; Steam'in kategorileriyle birebir). IGDB'de anahtar kelimesi kodlanmış oyunlar içinde beyan oranı 2023'te %0,5, 2024'te **%6,9**, 2025'te **%15,5.**
- 2024–2025 çıkışlı 8.185 bağımsız oyunda, yapay zekâ beyan eden 1.001 oyun:
  - **%65'i görünmez kaldı** (beyan etmeyenlerde %39). Kontrollü OR **×3,0** (2,6–3,5).
  - %3,4'ü hit oldu (beyan etmeyenlerde %10,5). OR ×0,31.
  - %2,4'ü sevilen hit oldu (%7,8'e karşı).
  - 50+ incelemeli olanların ortanca olumlu oranı **5,6 puan daha düşük.**
- **Nasıl okunmalı:** Bu bir neden-sonuç değil. Yapay zekâ beyanı büyük ihtimalle düşük bütçeli, hızlı üretilmiş projelerle birlikte görülüyor. Ama oyuncuların beyanı görüp tepki vermesi (daha düşük beğeni) de mümkün. İki açıklama bu veriyle ayrılamaz.
- **Sınırlar:**
  - Steam API'leri beyanı döndürmüyor (doğrudan kontrol edildi). Mağaza sayfalarını HTML olarak taramak kaynak politikasına aykırı olduğu için kullanılmadı.
  - Yalnız **beyan eden** oyunlar ölçülüyor; kullanıp beyan etmeyenler "beyan yok" grubunda. Bu, farkı küçültme yönünde çalışır.
  - IGDB'nin anahtar kelime kodladığı oyunlar genelden daha başarılı (bu alt örneklemde görünmezlik %39, tüm kohortta %54). Mutlak oranlar değil, fark yorumlanmalı.

### K1: Fiyatın tatlı noktası

*Betik: `analysis/k1_fiyat.py`. Ücretli bağımsız oyunlar (54.371). Ticari başarı sonuç olarak kullanılmadı, çünkü fiyat gelir formülünün içinde.*

![Fiyat noktaları](../analysis/sekiller/K1_1_fiyat_noktalari.png)

- **Hit oranı fiyatla neredeyse düzenli artıyor:**

| Fiyat (USD) | 0,99 | 4,99 | 9,99 | 14,99 | 19,99 | 24,99 | 29,99 |
|---|---|---|---|---|---|---|---|
| Hit oranı | %0,7 | %1,7 | %3,9 | %8,2 | %17 | %26 | %28 |

- Belirgin sıçramalar 9,99 → 10,99 (%3,9 → %5,6) ve 14,99 → 17,99 (%8 → %14) geçişlerinde.

![Tür ve fiyat](../analysis/sekiller/K1_2_tur_fiyat_bandi.png)

- 8 türün 7'sinde hit oranı 20 USD üstünde en yüksek. **Racing** istisna: en iyi bant 10–20 USD (%9), daha pahalı Racing oyunu zaten çok az.
- Casual, Simulation ve Sports 20–30 USD'de tepe yapıp 30 USD üstünde düşüyor. Action, RPG ve Strategy'de 30 USD üstü de iyi.

![Fiyat ve beğeni](../analysis/sekiller/K1_3_fiyat_begeni.png)

- **Pahalı oyunlar daha sert yargılanıyor.** İlk yılında 50+ inceleme alan oyunlarda "çok olumlu" (%80+) oranı 5 USD altında %73, 30 USD üstünde %53. Oyuncular yüksek fiyat karşılığında daha çok bekliyor.
- **Dikkat:** 50+ inceleme şartı ucuz oyunlarda daha seçici bir alt grup bırakıyor (5 USD altında 50+ inceleme almak zaten istisnai başarı). Bu farkın bir kısmını açıklayabilir.

**Geliştirici için anlamı ve sınırları:**
- **Bu bir "fiyatını artır" tavsiyesi değil.** Fiyat büyük ölçüde oyunun kapsamını, üretim değerini ve geliştiricinin güvenini yansıtıyor; 25 USD'lik bağımsız oyun genelde daha büyük bir projedir.
- Kullanılan fiyat çıkış fiyatı değil, Ekim 2026 liste fiyatı. Başarısız oyunların sonradan fiyat düşürmesi ucuz oyunların dezavantajını kısmen şişirebilir.
- Güvenle söylenebilecek olan: **5 USD altı bir "görünürlük tuzağı" gibi duruyor** (her türde hit oranı %0,4–2). Ayrıca daha yüksek fiyat, beğeni çıtasını da yükseltiyor.

### K3: Erken uyarı: ilk ay yılı ne kadar söylüyor?

*Betik: `analysis/k3_erken_uyari.py`. Aralık sınırları sonuçlara bakılmadan sabitlendi.*

![Erken uyarı](../analysis/sekiller/K3_1_erken_uyari.png)

- **İlk 30 gün yılın büyük kısmını belirliyor.** İlk 30 günün inceleme sayısı ile ilk yıl arasındaki sıra korelasyonu **0,93**, ilk 90 gün için 0,96.
- **İlk 30 günde X inceleme alan bir oyunun yılı hit kapatma olasılığı:**

| İlk 30 gün | 10–19 | 20–49 | 50–99 | 100–199 | 200–499 |
|---|---|---|---|---|---|
| Yıl sonunda hit | %0,1 | %0,5 | %3 | **%17** | **%75** |

- Bağımsız oyunların %67'si ilk ayında 10'dan az inceleme alıyor. Bunların ilk yılında hit olanı neredeyse yok.

![İlk ay çarpanı](../analysis/sekiller/K3_2_ilk_ay_carpani.png)

- **Tipik bir oyun ilk yılını ilk ayının ~2,2 katıyla kapatıyor.** Bu çarpan her büyüklükte şaşırtıcı derecede sabit (×1,8–2,2). En iyi %10'luk dilim ×3,6–4,6'ya ulaşıyor.

**Geliştirici için anlamı:**
- **Kaba hesap kuralı:** İlk ayın inceleme sayısını 2 ile çarp, ilk yılın kabaca nereye varacağını gör. Uzun kuyruğu iyi olan oyunlar 4 katına kadar çıkabiliyor. Uzun soluklu ilginin değeri M4'te görülmüştü.
- **Lansman ayı belirleyici.** İlk 30 günde 100'ün altında kalan bir oyunun yılı hit kapatma ihtimali %3'ün altında. Pazarlama, wishlist toplama ve demo çalışmasının büyük kısmı **çıkıştan önce** yapılmalı. Çıkıştan sonra kurtarmak istisnai.
- **Not:** Aylık çözünürlükteki oyunlarda ilk 30 gün yaklaşık hesaplanıyor (hata %2–8); aralık bazlı sonuçları etkilemiyor.

### K4: Çıkış öncesi tahmin modeli

*Betik: `analysis/k4_tahmin_modeli.py`. LightGBM; eğitim ≤ 2023, test 2024–2025 (23.465 oyun).*

**Sızıntıya karşı alınan önlemler:**
- Oyuncu etiketleri ve onlardan türetilen yenilik/doygunluk ölçüleri modele girmedi (sonradan oylanıyor).
- **IGDB'nin hiçbir alanı** girmedi. IGDB başarılı oyunları daha ayrıntılı kodluyor (T13); model "kaydın ne kadar dolu olduğundan" başarıyı öğrenebilirdi.

![Tahmin isabeti](../analysis/sekiller/K4_1_tahmin_isabeti.png)

| Model | İçerik | PR-AUC | ROC-AUC |
|---|---|---|---|
| Rastgele tahmin | — | 0,05 | 0,50 |
| B (katı) | Yalnız kesin çıkış öncesi bilgiler | 0,19 | 0,76 |
| **Ana model** | + liste fiyatı ve platformlar | **0,26** | **0,81** |
| A | + dil bilgisi (Çince, dil sayısı) | 0,34 | 0,85 |

- Ana modelin "en umut verici" bulduğu %10'luk dilimde gerçek hit oranı **%22**, ortalamanın (%4,8) **4,6 katı.** En alttaki %10'da ise %0,5.
- **Neden ana model "dilsiz"?** Dil bilgisi eklenince PR-AUC 0,26'dan 0,34'e çıkıyor, ama M2'de başarılı oyunların Çince'yi sonradan eklediği gösterildi. Bu artışın bir kısmı sızıntı. A bir üst sınır, B bir alt sınır.

![Katkılar](../analysis/sekiller/K4_2_tahmin_katkilari.png)

- **Tahmine en çok katkı yapan bilgiler:** fiyat (açık ara), yayıncının deneyimi, stüdyo yaşı, macOS desteği, Simulation/RPG türü, aynı hafta çıkan oyun sayısı. "Kendi yayını" ve "geliştiricinin önceki oyunları" düşük olasılık yönünde; M1 ve M6 bulgularıyla tutarlı.

**Anlamı:** Çıkış öncesi bilgilerle oyunların "umut verici" ve "riskli" olanlarını kabaca ayırmak mümkün; en riskli %50'de hit oranı %2'nin altında. Ama tahmin gücü sınırlı: en umut verici dilimdeki oyunların bile %78'i hit olmuyor. Lansman sonrası (K3: ilk ay) ve içerik (M2) çok daha belirleyici. Bu model Indie Opportunity Explorer'ın motoru olacak; çıktısı bir "kesin tahmin" değil, "benzer oyunların geçmişte ne yaptığı" olarak sunulmalı.

---

## Keşifsel analizler (K5–K8): akımlar, boş bölgeler, gizli hazineler, algoritma eşiği

*Tanımlar sonuçlar görülmeden `docs/KESIFSEL_K5_K8.md`'de sabitlendi; sonradan yapılan her değişiklik (ve nedeni) oradaki günlükte. Hepsi keşifsel.*

### K5: Klon dalgaları: bir hit'in arkasından gitmek işe yarıyor mu?

*Betik: `analysis/k5_klon.py`*

![Klon dalgası](../analysis/sekiller/K5_1_klon_dalgasi.png)

- **Öncü:** 2018 – Mart 2024 arasında ilk yılında 5.000+ inceleme alan 682 oyun. **Takipçi:** öncüden sonraki 24 ayda çıkan ve içerik etiketleri ona çok benzeyen (kosinüs ≥ 0,70) oyun.
- **"Klon seli" yok.** Bir hit'ten sonraki yıl ona çok benzeyen oyunların payı yerinde sayıyor (×1,05; GA 0,97–1,14). Sıradan bir oyunun çevresi aynı dönemde küçülüyor (×0,83). Yani hit'in bölgesi Steam'le aynı hızda büyümeyi sürdürüyor, ama patlama yok.

![Takipçi başarısı](../analysis/sekiller/K5_2_takipci_basari.png)

- Takipçilerin %15,5'i hit oluyor (örneklem ortalaması %4,8), sıradan bir oyunun benzerlerinin %7,8'i.
- **Ama avantaj takipten değil bölgeden.** Hit'ten *önce* aynı bölgeye çıkan oyunların da %16,7'si hit olmuş. Hit, verimli bir bölgenin göstergesi; onu taklit etmek ek bir şey katmıyor.
- **Geç kalan kaybediyor:** ilk 6 ayda gelen takipçilerin %18'i, 12–24 ay sonra gelenlerin %13,7'si hit oluyor; ikincisi bölgenin olağan oranının (%16,7) altında.
- **En büyük akımlar:** Vampire Survivors (2021) ve onu izleyen 20 Minutes Till Dawn, Brotato, Soulstone Survivors grubunun ardından 407 oyun geldi; bağımsızlarda hit oranı yalnız %7,8 (322'de 25). Ardından Wildfrost/Balatro deste kurma dalgası (181 oyun), hayatta kalma-zanaat (SCUM, Subnautica: Below Zero, Forager) ve korku (Poppy Playtime, FNAF: Security Breach).
- **Dikkat:** Etiketler çıkıştan sonra oylanıyor (R4): "Survivors-like" gibi etiketler öncüden sonra doğabilir. Takipçi = "benzer etiketli sonraki oyun", ilham aldığı kanıtlanmış oyun değil. İlk çalıştırmada en büyük "dalgalar" yetişkin içerik ve seri üretim kümeleri çıktığı için bayraklı oyunlar öncü/takipçi evreninden çıkarıldı (günlükte).

### K6: Boş yıldız bölgeleri: az rakip, çok başarı

*Betik: `analysis/k6_bos_bolge.py`*

![Boş bölgeler](../analysis/sekiller/K6_1_bos_bolgeler.png)

- Oyunlar içerik etiketlerine göre 60 bölgeye ayrıldı (59'unda ≥ 200 bağımsız oyun). Her bölgede **gözlenen hit ÷ beklenen hit** hesaplandı; beklenen, aynı yıl, tür, fiyat, EA ve dil karışımındaki oyunların hit olasılığı. Yani "bölge iyi çünkü pahalı oyunlar var" etkisi ayrıldı.
- **Fırsat bölgesi** (2022–25 arzı ortancanın altında ve O/B'nin GA alt sınırı > 1): üç bölge.

![Fırsat listesi](../analysis/sekiller/K6_2_firsat_listesi.png)

| Bölge | Hit (gözlenen ÷ beklenen) | Hit oranı | 2022–25 arz | Arz büyümesi (Steam = 1) |
|---|---|---|---|---|
| Cozy · Wholesome · Cats | ×2,3 (1,8–2,8) | %17,2 | 646 | **×6,9** |
| Dating Sim · Visual Novel · Romance | ×2,0 (1,6–2,5) | %10,8 | 915 | ×1,2 |
| Detective · Mystery · Investigation | ×1,5 (1,05–2,0) | %8,6 | 439 | ×0,9 |

- **Cozy fırsatı kapanıyor:** bölgeye çıkan oyun Steam'in 6,9 katı hızla artıyor. Dedektif/gizem bölgesi hem başarılı hem büyümüyor, ama bu sonuç sağlam değil: yalnız 2021+ çıkışlı oyunlarla O/B ×1,29 (GA 0,83–1,93).
- **Kalabalık ama yine de iyi:** psikolojik korku (×2,0), idle/incremental (×1,85), yerel/PvP çok oyunculu (×1,8). Bunlar M2'deki "kalabalık dezavantaj değil, talep işareti" bulgusuyla tutarlı.
- **En zayıf bölgeler:** genel aksiyon-macera, 2D platform, arcade (×0,3–0,5).
- **Dikkat:** Yüksek O/B, bölgedeki oyunların ölçülmeyen kalitesini de yansıtabilir; fırsat ≠ garanti. Cinsel içerik etiketleriyle tanımlı iki bölge (×5,2 ve ×2,0) fırsat sayılmadı: Steam içerik uyarısı olmadığı için yetişkin bayrağına (T06) takılmıyorlar; örneklemde bu etiketleri taşıyan 2.324 oyun (%3,5) var.

### K7: Gizli hazineler: çok beğenilip görülmeyenler

*Betik: `analysis/k7_gizli_hazine.py`*

![Gizli hazineler](../analysis/sekiller/K7_1_gizli_hazine_farklar.png)

- **Gizli hazine:** ilk yılında 10–99 inceleme alan, beğeni alt sınırı ≥ %80 olan oyun. **Görünür hazine:** aynı beğeni, 500+ inceleme.
- **Çok beğenilen oyunların %44'ü gizli kalıyor** (9.112 çok beğenilen oyundan 3.991'i); her görünür hazineye karşılık ~1,8 gizli hazine var.
- Çıkış öncesi nitelikler içinde görünür hazineyi ayıranlar: **Simulation türü** (%15 → %33), **fiyat** (geometrik ortalama ~3,6 → 6,0 USD), **Early Access** (%13 → %23; kontrollü OR 1,28), **Playtest** (%5 → %10; OR 1,93), **stüdyonun önceki oyunu** (%41 → %50; OR 1,53). Gizlilerde daha yaygın: **kendi yayını** (%84 → %78; OR 0,71) ve Casual tür.
- **Demo ayırmıyor:** iki grupta da çıkış öncesi demo oranı ~%15 (kaldırılmış demolar R13 yüzünden kesin değil).
- **Dil ve Çince en büyük farklar** (%31 → %66 Çince), ama bunlar mağazanın bugünkü değeri; başarılı oyunlar dili sonradan ekliyor (M2b). Bu farkın büyük bölümü sonucun kendisi olabilir, bu yüzden ayrı işaretlendi.
- **Dikkat:** Az incelemeli oyunda olumlu oran arkadaş/aile incelemeleriyle şişebilir; liste (K7_ozet.json) kalite garantisi değil.

### K8: "50 incelemeyi geç, algoritma seni görsün" doğru mu?

*Betik: `analysis/k8_esik.py`*

![Eşik sıçramaları](../analysis/sekiller/K8_1_esik_sicramalari.png)

- 36.148 oyunun 1 milyon aylık/haftalık inceleme diliminde, toplam inceleme bir eşiği geçince inceleme hızının sıçrayıp sıçramadığı test edildi (süreksizlik regresyonu; plasebo eşiklerle karşılaştırma).
- **50 eşiğinde sıçrama yok:** −%1,0 (GA −%2,4 … +%0,4). Test hassas: +%0,4'ten büyük bir sıçrama veriyle dışlanıyor. Plasebo eşiklerin (20–80) hepsi de ~0.
- **10 eşiği** (Steam puanı görünür olur): ham tahmin −%6,6, ama bu büyük ölçüde seçilim: seri yalnız eninde sonunda 10'u geçen oyunlar için var, bu da eşik altını şişiriyor. Oyunları ömür boyu ≥ 30 incelemeyle sınırlayınca −%4,8, ≥ 100 ile +%0,5 (geniş GA). 10 eşiği için kesin bir şey söylenemez.

![Eşik kovaları](../analysis/sekiller/K8_2_esik_kovalari.png)

- **Anlamı:** Steam'in görünürlüğü belirli bir inceleme sayısında "açılan" bir kapı gibi davranmıyor; ilgi sürekli ve pürüzsüz büyüyor. "50'ye ulaşmak için ne gerekiyorsa yap" tavsiyesinin veride karşılığı yok.
- **Dikkat:** Aylık dilimler kaba; ay içinde gerçekleşen kısa bir sıçrama kısmen gizlenebilir (haftalık dilimli oyunlar da dahil). Etki varsa da küçük.

### K9: Mağaza açıklaması başarıyı ele veriyor mu?

*Betikler: `analysis/k9_metin_hazirla.py`, `analysis/k9_metin_model.py` · tanımlar `docs/KESIFSEL_K5_K8.md` §K9*

![Metin modelleri](../analysis/sekiller/K9_1_metin_modelleri.png)

- 65.555 bağımsız oyunun mağaza metni (kısa açıklama + uzun açıklamanın ilk 1.500 karakteri) üç yolla modellendi: TF-IDF + lojistik regresyon, cümle gömmesi (all-MiniLM-L6-v2) + lojistik regresyon, ve K4'ün çıkış öncesi nitelikleri + metin skoru (LightGBM, sızıntısız yığınlama). Zamansal bölme K4 ile aynı: eğitim ≤ 2023, test 2024–2025.
- **Metin bilgi katıyor:** Aynı 22.996 test oyununda K4 nitelikleri PR-AUC 0,27; metin eklenince **0,31** (fark +0,045; %95 GA +0,028 … +0,063). ROC-AUC 0,81 → 0,85. Metin tek başına da 0,19 alıyor (rastgele 0,05).
- **Sızıntı koruması gerekliydi:** Ödül, satış, puan ve basın alıntısı içeren cümleler metinden atıldı; bu cümleler hit'lerin %14,2'sinde, diğerlerinin %7,8'inde vardı. Metin bugünkü hâli olduğundan artış bir **üst sınır**.

![Kelimeler](../analysis/sekiller/K9_2_metin_kelimeler.png)

- **Hit'le birlikte görülen ifadeler:** co-op, wishlist (çıkış öncesi pazarlama izi), "from the creators of" (stüdyo geçmişi), idle, roguelite, ranked, Touhou (hazır hayran kitlesi). **Ters yönde:** VR, arcade, levels, obstacles, difficult. Kelimeler çoğu zaman türü ve kapsamı taşıyor; "new", "edition", "discord" gibi çıkış sonrası eklenmiş olabilecek ifadeler grafikte ayrıca işaretli.

![Üslup](../analysis/sekiller/K9_3_metin_uslup.png)

- **Üslup:** En güçlü işaret uzunluk (1 standart sapma daha uzun metin: hit olasılığı ×1,31; tür, fiyat, yıl sabit). Somut içerik sayıları ("50 levels") hafif olumlu (×1,04). "Unique, epic, revolutionary" gibi abartı sıfatlarının ilişkisi yok (×1,02, anlamsız).
- **Anlamı:** Mağaza sayfasına emek vermek (uzun, somut, topluluğa çağıran metin) başarıyla birlikte görülüyor; büyük kelimeler değil. Bu, bütçe ve ekip büyüklüğünün de işareti olabilir.

### K10: Türler: risk-ödül karnesi, hibrit türler, eğilimler

*Betikler: `analysis/k10_tur.py`, `analysis/k10_grafik.py` · tanımlar `docs/KESIFSEL_K5_K8.md` §K10*

- **Alt tür:** oyunun ilk 10 etiketindeki tür etiketi (Roguelike, Metroidvania, Visual Novel…). Örneklemde ≥ 500 oyunu olan 67 alt tür. **Yalnız 2021–2025 çıkışlı oyunlar** (aşağıdaki veri kalitesi notu).

![Tür karnesi](../analysis/sekiller/K10_1_tur_karnesi.png)

- **Az riskli ve ödüllü:** Management (hit %11,8, görünmez %37), Dating Sim (%11,2 / %33), City Builder, Sandbox, Life Sim. **En zor:** Runner (%1,2 / %70), Precision Platformer, Logic, 2D Platformer, Education.
- **Fiyat ve tür karışımı ayrılınca (O/B):** beklenenin en üstünde Dating Sim (×2,0), Word Game, Idler, Visual Novel ve Survival Horror; en altında Education (×0,37), Runner, Logic, Puzzle Platformer. Yani Management'ın yüksek oranının bir kısmı fiyat ve kapsamdan geliyor (O/B ×1,17).

![Hibrit türler](../analysis/sekiller/K10_2_hibrit_turler.png)

- **Hibrit türler parçalarının toplamı kadar.** 176 tür çiftinin hiçbiri, türlerin ayrı ayrı öngördüğünden çoklu test sonrası farklı değil (yalnız 8'i p < 0,05; şans beklentisi ~9). "Doğru türleri birleştir, sinerji yakala" fikrinin veride karşılığı yok: karışımın başarısını bileşen türler belirliyor.

![Eğilimler](../analysis/sekiller/K10_3_tur_egilimleri.png)

- **Anlamlı eğilimlerin hepsi düşüş:** Auto Battler (%13,4 → %5,1), Idler (%10,3 → %6,4), Roguelike (%8,1 → %5,1); 2021–22'den 2023–24'e. Üçü de son yılların patlayan türleri; K5'teki "geç kalan kaybediyor" bulgusuyla tutarlı.

### Veri kalitesi: etiket kapsamı ve 2021+ duyarlılığı

*Betik: `analysis/duyarlilik_2021.py` · sonuçlar `analysis/sonuclar/duyarlilik_2021.json`*

- **Bulgu:** Oyuncu etiketleri 2021 öncesi seçilimli. Analiz örnekleminde alt tür etiketi olan oyun payı 2018'de %52, 2019'da %55, 2021'den itibaren %91–93. 2018–19'da hit'ler ortalama iki kat fazla tür etiketi taşıyor; 2021'den itibaren fark yok. Yani eski yıllarda "etiketli olmak" başarıyla ilişkili ve etiket tabanlı ölçüler o yıllarda başarılı oyunlara kayıyor.
- **Etkisi:** K10'un ilk çalıştırmasında her alt tür "düşüşte" göründü (yapay). K10 2021+ ile yapıldı; etiket tabanlı önceki bulgular 2021+ ile yeniden hesaplandı:

| Bulgu | Tam örneklem | Yalnız 2021–2025 | Sonuç |
|---|---|---|---|
| H1 yenilik (ters U) | desteklenmedi; eğim iki uçta negatif | desteklenmedi; düşüş yüksek yenilikte yavaşlıyor | geçerli |
| H7 doygunluk | OR 1,06 (1,03–1,09) | OR 1,07 (1,03–1,10) | geçerli |
| Multiplayer / Online Co-op / Co-op | ×3,6 / ×3,2 / ×2,7 | ×3,1 / ×2,8 / ×2,6 | geçerli (biraz zayıf) |
| K5 takipçi / öncül / plasebo hit | %15,5 / %16,7 / %7,8 | %14,2 / %14,5 / %7,6 | geçerli |
| K6 Cozy / Dating Sim O/B | ×2,25 / ×1,98 | ×2,26 / ×1,93 | geçerli |
| K6 Detective / Mystery O/B | ×1,48 (1,05–2,02) | ×1,29 (0,83–1,93) | **sağlam değil** |

- Ön kayıtlı hipotez kararları tam örneklemle verildi ve değişmiyor; tablo bir sağlamlık kontrolü.
