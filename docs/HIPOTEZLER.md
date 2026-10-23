# Discovery Dynamics: Ön Kayıtlı Hipotezler

**Kayıt tarihi:** 2026-10-18
**Durum:** Veri henüz toplanmadı. Bu hipotezler veri görülmeden önce yazıldı.

Bu belge kilitli. Değişiklik gerekirse bu dosya düzenlenmez. Değişiklik, gerekçesi ve tarihiyle birlikte en alttaki "Değişiklik günlüğü" bölümüne eklenir. Sonuçlar raporlanırken her hipotez için "desteklendi / desteklenmedi / test edilemedi" durumu açıkça yazılır.

## Ortak kurallar

- **Örneklem:** Organik örneklem (KAPSAM_VE_PLAN.md §3.2), 2018–2025 çıkışlı oyunlar.
- **Birincil sonuç:** `log(1 + reviews_365)`. İkili analizlerde `hit` (`reviews_365 ≥ 500`).
- **Standart kontroller:** Çıkış yılı, ana tür, fiyat bandı, F2P, Early Access ile çıkış, dil sayısı.
- **Anlamlılık:** α = 0,05; H1–H7 için Holm düzeltmesi uygulanır. Etki büyüklüğü ve %95 güven aralığı her zaman raporlanır.

## Doğrulayıcı hipotezler

### H1: Yenilik ters U eğrisi (M3)
- **Hipotez:** `novelty_score` ile sonuç arasında ters U biçiminde bir ilişki var. Ne çok sıradan ne çok aykırı olmak, orta düzey yenilikçilik en iyi sonucu alıyor.
- **Test:** Kontrollü regresyonda kuadratik terim negatif olmalı. Lind–Mehlum U testi anlamlı çıkmalı ve dönüm noktası verinin 5. ile 95. yüzdelikleri arasında olmalı.
- **Çürütme:** Kuadratik terim anlamsız çıkarsa, ilişki monoton (sürekli artan veya azalan) çıkarsa ya da dönüm noktası veri aralığının dışında kalırsa hipotez reddedilir.

### H2: Demo etkisi (M5)
- **Hipotez:** Çıkıştan önce demo yayınlayan oyunların `hit` olasılığı, benzer özellikli demosuz oyunlara göre daha yüksek (ATT > 0).
- **Test:** Propensity score matching ve doubly robust tahmin. Standartlaştırılmış ortalama farkı < 0,1 ise eşleştirme dengeli kabul edilir. Rosenbaum Γ değeri raporlanır.
- **Çürütme:** ATT'nin %95 güven aralığı 0'ı içeriyorsa hipotez desteklenmez.

### H3: Next Fest etkisi (M5)
- **Hipotez:** Next Fest'e katılan oyunların `hit` olasılığı, demosu olan ama Next Fest'e katılmayan benzer oyunlara göre daha yüksek.
- **Test:** H2 ile aynı yöntem; karşılaştırma grubu demosu olup Next Fest'e katılmayan oyunlar.
- **Not:** Katılım verisine erişilemezse "test edilemedi" olarak raporlanır ve analiz keşifsel bölüme taşınır.

### H4: Early Access ve uzun kuyruk (M4)
- **Hipotez:** Early Access ile çıkan oyunların `tail_share` değeri, doğrudan tam sürümle çıkanlara göre daha yüksek. Yani Early Access oyunları zamana daha yayılmış bir başarı eğrisi gösteriyor.
- **Test:** `tail_share` için fractional logit modeli ile kontrollü karşılaştırma ve eşleştirilmiş örneklemde tekrar.

### H5: İkinci oyun etkisi (M6)
- **Hipotez:** En az iki oyun çıkarmış stüdyolarda ikinci oyunun `reviews_365` değeri, ilk oyununkinden yüksek.
- **Test:** Stüdyo içi eşleştirilmiş Wilcoxon testi ve yıl ile tür kontrollü sabit etkili model.
- **Kontrol:** Sadece ilk oyunu başarılı olan stüdyoların ikinci oyun çıkarması bir seçim yanlılığı yaratabilir. Bunu kontrol etmek için ilk oyunun başarı kademesine göre tabakalı analiz yapılır.

### H6: Çince yerelleştirme (M2)
- **Hipotez:** Basitleştirilmiş Çince desteği, kontroller sabitken daha yüksek `reviews_365` ile ilişkili.
- **Test:** Kontrollü regresyon ve propensity score matching ile duyarlılık analizi. Yan kanıt olarak Çince desteği olan oyunlarda Çince yazılmış incelemelerin payı raporlanır.

### H7: Doygunluk (M1, M2)
- **Hipotez:** Aynı etiket kombinasyonunda son 12 ayda çıkan oyun sayısı (`saturation`) arttıkça `hit` olasılığı düşüyor.
- **Test:** Lojistik regresyonda `log(saturation)` katsayısı negatif olmalı; tür sabit etkileri modelde yer alır.

### H8: Mikro ve makro içerik üreticisi (M8)
- **Hipotez:** Çok sayıda küçük kanalın (< 100 bin abone) videolarından sonra gelen inceleme sıçramaları, tek bir büyük kanalın (≥ 1 milyon abone) videosundan sonra gelen sıçramalara göre daha kalıcı.
- **Kalıcılık ölçütü:** Sıçramadan 30 gün sonraki günlük inceleme hızının, sıçrama öncesi taban seviyeye oranı.
- **Test:** İki grup arasında Mann–Whitney U testi ve sıçrama büyüklüğü ile tür kontrollü regresyon.
- **Not:** Bu hipotez YouTube kotası nedeniyle 300–500 oyunluk tabakalı bir örneklemle test edilir, bu yüzden Holm düzeltmesi ailesinin dışında, ayrı raporlanır.

## Keşifsel analizler (ön kayıt dışı)

- İnceleme eğrisi yörünge tipleri ve sayıları (M4)
- Motivasyon haritası ve karşılanmamış oyuncu ihtiyaçları (M2)
- LLM tabanlı oyuncu sesi analizi (M7)
- Fiyat, çıkış günü ve rekabet yoğunluğu etkileri
- Çıkış öncesi tahmin modeli ve SHAP açıklamaları

## Değişiklik günlüğü

| Tarih | Değişiklik | Gerekçe |
|---|---|---|
| 2026-10-18 | İlk kayıt | — |
| 2026-10-18 | H8'e Twitch klip verisi ek kanıt olarak eklendi (hipotez ve test değişmedi) | Twitch Get Clips geçmişe dönük veri sağlıyor |
