# Discovery Dynamics: Analiz Raporu

*Steam'de bağımsız oyunlar nasıl görünür oluyor? Her modül kısa bir bölüm: soru, ne bulduk, ne anlama geliyor, nelere dikkat etmeli.*

**Okumadan önce bilinmesi gerekenler:**
- **Başarı ölçüsü:** Oyunun ilk 365 günde aldığı Steam incelemesi. Steam satış rakamı yayınlamıyor; inceleme sayısı satış sıralamasını iyi izliyor (sıra korelasyonu 0,59). "Hit" = ilk yılda 500+ inceleme.
- **Örneklem:** 2018–2025 arasında çıkan, büyük yayıncı desteği olmayan ("organik") 66.999 oyun. Seri üretim, yetişkin içerik, yazılım ve listelenmemiş oyunlar çıkarıldı.
- **İlişki ≠ neden-sonuç.** Aksi yazılmadıkça bulgular "birlikte görülüyor" demektir. Neden-sonuç iddiası yalnız M5'te (demo ve Next Fest) kurulacak.
- Grafiklerin verileri aynı adla `analysis/sekiller/*.csv` olarak duruyor. Yöntem ayrıntıları: `docs/PILOT_RAPORU.md`, `docs/VERI_RAPORU.md`.

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

### M1 özeti

| Bulgu | Güven | Not |
|---|---|---|
| Bağımsız oyunların %54'ü ilk yılında < 10 inceleme | Yüksek | Yıllar arasında tutarlı |
| Arz 2,9 kat arttı, hit oranı %4–5,5'te sabit | Yüksek | Mutlak hit sayısı 2,6 kat arttı |
| Yüksek fiyat, çok dil ve deneyim başarıyla birlikte görülüyor | Yüksek (ilişki) | Neden-sonuç değil; büyük ihtimalle bütçe ve kapsamı yansıtıyor |
| Simulation ve RPG avantajlı, Sports, Racing ve Casual dezavantajlı | Orta | Tür etiketleri geliştiricinin seçimi; birden çok tür olabilir |
| Yetişkin içerik payı 3,8 katına çıktı | Yüksek | Tüm kohort |
