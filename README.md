# Discovery Dynamics

**Determinants of Organic Success for Independent Games on Steam**
*Steam'de Bağımsız Oyunların Organik Başarı Belirleyicileri*

Steam'de her yıl ~20.000 oyun çıkıyor ve büyük çoğunluğu neredeyse hiç görülmüyor. Bu proje, büyük yayıncı ve pazarlama bütçesi etkisini örneklemden ayırdıktan sonra, bağımsız stüdyoların organik görünürlüğe (inceleme, oyuncu tutunması, viralleşme) nasıl ulaştığını veriye dayalı ve bilimsel yöntemlerle inceler.

Çerçeve: Google Data Analytics (Ask → Prepare → Process → Analyze → Share → Act).

## Durum

| Faz | Durum |
|---|---|
| 0. Kapsam ve hipotezler | ✅ Tamamlandı (2026-10-18) |
| 1. Prepare: veri toplama | ✅ GetItems, IGDB, inceleme serileri, referans tabloları · ⏳ kaldırılmış demolar (Steam API anahtarı bekliyor) |
| 2. Process: temizleme ve öznitelik üretimi | ✅ 2026-10-24: `bash scripts/hat.sh` · 47/47 kontrol · docs/VERI_RAPORU.md |
| 3. Analyze: analiz modülleri M1–M8 | 🔄 M1–M4, M6, K1–K8 ✅ · M5 (Steam API anahtarı), M7, M8 bekliyor · [ANALIZ_RAPORU](docs/ANALIZ_RAPORU.md) |
| 4. Share: landing page, Explorer, dashboard | 🔄 Steam Galaksisi taslağı: [web/](web/README.md) (2026-10-24) |
| 5. Act: öneriler ve yayın | — |

## Belgeler

- [docs/KAPSAM_VE_PLAN.md](docs/KAPSAM_VE_PLAN.md): kapsam, tanımlar, veri kaynakları, nitelik sözlüğü, analiz modülleri, yol haritası
- [docs/HIPOTEZLER.md](docs/HIPOTEZLER.md): veri görülmeden önce yazılmış, tarihli hipotezler (ön kayıt)
- [docs/VERI_KATALOGU.md](docs/VERI_KATALOGU.md): aday açık veri setleri, lisans ve kaynak kaydı
- [docs/ANALIZ_PLANI.md](docs/ANALIZ_PLANI.md): ilk inceleme bulguları, veri ihtiyaç matrisi, saçma sonuç risk kaydı, pilot ve yol haritası
- [docs/PILOT_RAPORU.md](docs/PILOT_RAPORU.md): 1.000 oyunluk pilotun veri kalitesi bulguları
- [docs/VERI_MIMARISI.md](docs/VERI_MIMARISI.md): veri katmanları, şema, temizlik protokolü (T01–T13), otomatik kontroller
- [docs/VERI_RAPORU.md](docs/VERI_RAPORU.md): otomatik veri raporu (huni, kararlar, eksiklik testi, sütun sözlüğü)
- [docs/ANALIZ_RAPORU.md](docs/ANALIZ_RAPORU.md): **analiz bulguları, grafiklerle, sade dille** (M1 →)

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
