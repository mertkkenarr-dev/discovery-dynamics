"""K9 grafikleri: model karşılaştırması, en belirgin kelimeler, üslup ölçüleri. Başlıklar sonuçtan üretilir."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import IKINCIL, KATEGORIK, MUREKKEP, SOLUK, baslik, kaydet, stil

# Sonuç görüldükten sonra işaretlendi (KESIFSEL günlüğü): çıkıştan sonra sayfaya eklenmesi olası ifadeler; modelden çıkarılmadı, yalnız işaretli.
SONRADAN_SUPHE = {"new", "edition", "discord", "community", "free", "update", "updates", "content"}
KAYNAK = "Kaynak: Steam (mağaza metni Şubat 2026 anlık görüntüsü, başarı sonrası eklenen cümleler atıldı); Discovery Dynamics analizi. Keşifsel."


def tr(v: float, d: int = 2) -> str:
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def ciz_modeller(s: pd.DataFrame, taban: float, n: int) -> None:
    stil()
    fig, ax = plt.subplots(figsize=(10, 4.6))
    y = np.arange(len(s))[::-1]
    renk = [KATEGORIK[1] if "metin" in a and "K4" in a else KATEGORIK[0] if a.startswith("K4") else SOLUK for a in s.index]
    ax.hlines(y, s.alt, s.ust, color=renk, linewidth=3)
    ax.scatter(s.pr_auc, y, color=renk, s=60, zorder=3, edgecolor="white", linewidth=1.2)
    for yi, (_, r) in zip(y, s.iterrows()):
        ax.text(r.ust + 0.005, yi, f"{tr(r.pr_auc)}  (ROC-AUC {tr(r.roc_auc)})", va="center", fontsize=8.8, color=IKINCIL)
    ax.axvline(taban / 100, color=SOLUK, linestyle="--", linewidth=1)
    ax.text(taban / 100 + 0.003, -0.6, "rastgele tahmin", fontsize=8, color=IKINCIL)
    ax.set_yticks(y, s.index)
    ax.set_xlabel("PR-AUC (test: 2024–2025; yüksek = daha iyi)")
    ax.set_xlim(0, s.ust.max() * 1.35)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: tr(v)))
    f = s.loc["K4 + metin"]
    if f.fark_alt > 0:
        ana = f"Mağaza metni tahmine bilgi katıyor: K4 nitelikleri {tr(s.loc['K4 nitelikleri'].pr_auc)} → metinle {tr(f.pr_auc)}"
    else:
        ana = f"Mağaza metni, çıkış öncesi niteliklere anlamlı bilgi katmıyor (fark {tr(f.fark)}; GA {tr(f.fark_alt)} … {tr(f.fark_ust)})"
    baslik(fig, ana, f"Aynı {tr(n, 0)} test oyunu (2024–25), eğitim ≤ 2023. Çubuk: PR-AUC %95 bootstrap GA. Metin skoru eğitimde katlar-dışı tahminle "
           "eklendi (sızıntısız yığınlama). Sayfa metni bugünkü hâli: artış bir üst sınır.")  # fmt: skip
    fig.subplots_adjust(top=0.8)
    kaydet(fig, "K9_1_metin_modelleri", s.round(5), KAYNAK)


def ciz_kelimeler(k: pd.DataFrame) -> None:
    stil()
    k = k.sort_values("katsayi")
    fig, ax = plt.subplots(figsize=(10, 7.4))
    y = np.arange(len(k))
    supheli = k.terim.isin(SONRADAN_SUPHE).values
    ax.barh(y, k.katsayi, color=np.where(supheli, SOLUK, np.where(k.katsayi > 0, KATEGORIK[1], KATEGORIK[0])), height=0.65)
    ax.set_yticks(y, [f"{t} *" if s_ else t for t, s_ in zip(k.terim, supheli)], fontsize=9)
    ax.axvline(0, color=MUREKKEP, linewidth=0.8)
    ax.set_xlabel("Lojistik katsayı (sağ: hit olasılığıyla birlikte artıyor)")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: tr(v, 1)))
    temiz = k[~supheli]
    ust, alt = temiz.terim.iloc[-1], temiz.terim.iloc[0]
    baslik(fig, f"Mağaza metninde hit'le en çok birlikte görülen ifade '{ust}', en az görülen '{alt}'",
           "TF-IDF (1–2 kelime) + lojistik regresyon, eğitim oyunları (≤ 2023). İlişki, neden-sonuç değil: kelime çoğu zaman türü ve kapsamı taşıyor. "
           "* Gri: çıkıştan sonra sayfaya eklenmiş olabilecek ifade (yeni içerik, sürüm, topluluk).")
    kaydet(fig, "K9_2_metin_kelimeler", k.round(4).set_index("terim"), KAYNAK)


def ciz_uslup(u: pd.DataFrame) -> None:
    stil()
    u = u.sort_values("tahmin")
    fig, ax = plt.subplots(figsize=(10, 4.6))
    y = np.arange(len(u))
    anl = (u.alt > 1) | (u.ust < 1)
    renk = np.where(~anl, SOLUK, np.where(u.tahmin > 1, KATEGORIK[1], KATEGORIK[0]))
    ax.hlines(y, u.alt, u.ust, color=renk, linewidth=2.5)
    ax.scatter(u.tahmin, y, color=renk, s=50, zorder=3, edgecolor="white", linewidth=1.2)
    for yi, (_, r) in zip(y, u.iterrows()):
        ax.text(r.ust * 1.01, yi, f"×{tr(r.tahmin)}", va="center", fontsize=8.8, color=IKINCIL)
    ax.set_yticks(y, u.index)
    ax.axvline(1, color=MUREKKEP, linewidth=0.8)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"×{tr(v)}"))
    ax.set_xlabel("Hit olasılığı oranı (ölçü 1 standart sapma artınca)")
    en = u.tahmin.idxmax() if (u.tahmin.max() - 1) >= (1 - u.tahmin.min()) else u.tahmin.idxmin()
    baslik(fig, f"Üslupta en güçlü işaret: {en.lower()} (×{tr(u.loc[en].tahmin)})",
           "Her ölçü ayrı modelde; yıl, tür, fiyat, EA ve dil sayısı sabit. Gri: %95 GA 1'i içeriyor.")
    fig.subplots_adjust(left=0.3)
    kaydet(fig, "K9_3_metin_uslup", u.round(4), KAYNAK)
