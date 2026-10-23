# Discovery Dynamics

**Determinants of Organic Success for Independent Games on Steam**
*Steam'de Bağımsız Oyunların Organik Başarı Belirleyicileri*

Steam'de her yıl ~20.000 oyun çıkıyor ve büyük çoğunluğu neredeyse hiç görülmüyor. Bu proje, büyük yayıncı ve pazarlama bütçesi etkisini örneklemden ayırdıktan sonra, bağımsız stüdyoların organik görünürlüğe (inceleme, oyuncu tutunması, viralleşme) nasıl ulaştığını veriye dayalı ve bilimsel yöntemlerle inceler.

Çerçeve: Google Data Analytics (Ask → Prepare → Process → Analyze → Share → Act).

## Durum

| Faz | Durum |
|---|---|
| 0. Kapsam ve hipotezler | ✅ Tamamlandı (2026-10-18) |
| 1. Prepare: veri toplama | 🔄 GetItems ✅ · IGDB ✅ · inceleme serileri çekiliyor · referans tabloları bekliyor |
| 2. Process: temizleme ve öznitelik üretimi | 🔄 Steam temizliği (`10`) ✅ · sonuç metrikleri (`11`) yazıldı, tam veriyle yeniden çalışacak |
| 3. Analyze: analiz modülleri M1–M8 | — |
| 4. Share: landing page, Explorer, dashboard | — |
| 5. Act: öneriler ve yayın | — |

## Belgeler

- [docs/KAPSAM_VE_PLAN.md](docs/KAPSAM_VE_PLAN.md): kapsam, tanımlar, veri kaynakları, nitelik sözlüğü, analiz modülleri, yol haritası
- [docs/HIPOTEZLER.md](docs/HIPOTEZLER.md): veri görülmeden önce yazılmış, tarihli hipotezler (ön kayıt)
- [docs/VERI_KATALOGU.md](docs/VERI_KATALOGU.md): aday açık veri setleri, lisans ve kaynak kaydı
- [docs/ANALIZ_PLANI.md](docs/ANALIZ_PLANI.md): ilk inceleme bulguları, veri ihtiyaç matrisi, saçma sonuç risk kaydı, pilot ve yol haritası
- [docs/PILOT_RAPORU.md](docs/PILOT_RAPORU.md): 1.000 oyunluk pilotun veri kalitesi bulguları
- [docs/VERI_MIMARISI.md](docs/VERI_MIMARISI.md): veri katmanları, şema, temizlik protokolü (T01–T13), otomatik kontroller

## Klasör yapısı

```
discovery-dynamics/
├── docs/        Kapsam, hipotezler, yöntem ve veri raporları
├── data/        raw/ (dokunulmaz ham veri) · interim/ · processed/
├── scripts/     Veri toplama ve temizleme betikleri
├── analysis/    Analiz modülleri (M1–M8)
├── web/         Landing page (design-kit site sistemi)
├── explorer/    Indie Opportunity Explorer (ayrı yayınlanan araç)
└── dashboard/   Tableau / Power BI pazar monitörü
```
