"""K3 (keşifsel) · Erken uyarı: ilk 30 / 90 günün incelemesi, yılın nasıl kapanacağını ne kadar söylüyor?

Kullanım: python analysis/k3_erken_uyari.py
Örneklem: analiz örneklemi. Ömür boyu < 10 incelemeli oyunlarda (histogram yok) r30 ≤ ömür boyu < 10 kesin → "<10" aralıkları.
Aralıklar (sonuçlara bakılmadan sabitlendi): 0–4, 5–9, 10–19, 20–49, 50–99, 100–199, 200–499, 500+.
Not: aylık çözünürlükte reviews_30 yaklaşık (göreli hata %2–8, PILOT_RAPORU Process 2); aralık analizi için yeterli.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import IKINCIL, KATEGORIK, KOK, MUREKKEP, baslik, kaydet, orneklem, stil, wilson, yukle
from scipy import stats

KAYNAK = "Kaynak: Steam inceleme grafiği; Discovery Dynamics analizi."
SINIR = [-np.inf, 4.5, 9.5, 19.5, 49.5, 99.5, 199.5, 499.5, np.inf]
AD = ["0–4", "5–9", "10–19", "20–49", "50–99", "100–199", "200–499", "500+"]


def tablo(a: pd.DataFrame, sutun: str) -> pd.DataFrame:
    x = a.copy()
    az = x.sonuc_kaynagi == "omur_ust_sinir"
    x.loc[az, sutun] = x.loc[az, "inceleme_omur"]  # r_N ≤ ömür boyu < 10: aralık kesin
    x = x[x[sutun].notna()]
    x["aralik"] = pd.cut(x[sutun].round(), SINIR, labels=AD)
    x["sevilen"] = x.basari_sinifi == "sevilen_hit"
    x["carpan"] = (x.reviews_365 / x[sutun]).where(x[sutun] >= 10)
    g = x.groupby("aralik", observed=True).agg(n=("appid", "size"), hit=("hit", lambda v: v.astype(int).sum()), sevilen=("sevilen", "sum"),
                                                carpan=("carpan", "median"), carpan_ust=("carpan", lambda v: v.quantile(0.9)))  # fmt: skip
    for c in ("hit", "sevilen"):
        lo, hi = wilson(g[c], g.n)
        g[f"{c}_oran"], g[f"{c}_alt"], g[f"{c}_ust"] = g[c] / g.n * 100, lo * 100, hi * 100
    return g


def main() -> None:
    stil()
    a = orneklem(yukle())
    g30, g90 = tablo(a, "reviews_30"), tablo(a, "reviews_90")
    h = a[a.sonuc_kaynagi == "histogram"]
    rho30 = stats.spearmanr(h.reviews_30, h.reviews_365, nan_policy="omit")[0]
    rho90 = stats.spearmanr(h.reviews_90, h.reviews_365, nan_policy="omit")[0]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(AD))
    for i, (g, ad) in enumerate([(g30, "İlk 30 gün"), (g90, "İlk 90 gün")]):
        g = g.reindex(AD)
        ax.bar(x + (i - 0.5) * 0.38, g.hit_oran, width=0.36, color=KATEGORIK[i], label=f"{ad} bu aralıktaysa",
               yerr=[(g.hit_oran - g.hit_alt).clip(lower=0), (g.hit_ust - g.hit_oran).clip(lower=0)], error_kw={"elinewidth": 1, "ecolor": IKINCIL})  # fmt: skip
        if i == 0:
            for xi, v, hu in zip(x[:-1], g.hit_oran[:-1], g.hit_ust[:-1]):  # 500+ etiketsiz (tanım gereği)
                ax.text(xi - 0.19, hu + 2, f"%{v:.0f}" if v >= 1 else f"%{v:.1f}", ha="center", fontsize=8.5, color=MUREKKEP)
    for bar in ax.patches[-1:] + [ax.patches[len(AD) - 1]]:  # 500+: tanım gereği %100 (zaten hit eşiğinde) → bulgu değil
        bar.set_facecolor("#c3c2b7")
    ax.text(len(AD) - 1, 104, "tanım gereği", ha="center", fontsize=8.5, color=IKINCIL)
    ax.set_xticks(x, AD)
    ax.set_xlabel("Belirtilen sürede alınan inceleme sayısı")
    ax.set_ylabel("Yıl sonunda hit olanlar (%)")
    ax.set_ylim(0, 108)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="x", visible=False)
    esik = g30.reindex(AD).hit_oran
    yari = next((AD[i] for i, v in enumerate(esik) if v >= 50), None)
    baslik(fig, f"İlk ay her şeyi söylemiyor ama çok şey söylüyor: ilk 30 günde {yari} inceleme alanların yarıdan fazlası yılı hit kapatıyor",
           f"Bağımsız oyunlar; hit = ilk yılda 500+ inceleme. Sıra korelasyonu (ilk 30 gün → ilk yıl): {rho30:.2f}; ilk 90 gün: {rho90:.2f}. Çizgiler %95 GA.")  # fmt: skip
    fig.subplots_adjust(top=0.82)
    kaydet(fig, "K3_1_erken_uyari", pd.concat({"ilk30": g30, "ilk90": g90}).round(3), KAYNAK)

    c = g30.reindex(AD[2:])
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.bar(np.arange(len(c)), c.carpan, color=KATEGORIK[0], width=0.6)
    for xi, (v, u) in enumerate(zip(c.carpan, c.carpan_ust)):
        ax.text(xi, v + 0.1, f"×{v:.1f}\n(en iyi %10: ×{u:.1f}+)", ha="center", va="bottom", fontsize=8.5, color=MUREKKEP)
    ax.set_xticks(np.arange(len(c)), AD[2:])
    ax.set_xlabel("İlk 30 günde alınan inceleme")
    ax.set_ylabel("İlk yıl ÷ ilk 30 gün (ortanca)")
    ax.set_ylim(0, c.carpan.max() * 1.6)
    ax.grid(axis="x", visible=False)
    baslik(fig, f"Tipik bir oyun ilk yılını ilk ayının ~{c.carpan.median():.1f} katıyla kapatıyor",
           "İlk 30 günde 10+ inceleme alan bağımsız oyunlar. Ortanca çarpan; parantez içi: en iyi %10'un ulaştığı çarpan.")  # fmt: skip
    fig.subplots_adjust(top=0.8)
    kaydet(fig, "K3_2_ilk_ay_carpani", c.round(3), KAYNAK)

    ozet = {"spearman_30": rho30, "spearman_90": rho90, "ilk30": g30.round(3).to_dict("index"), "ilk90": g90.round(3).to_dict("index")}
    (KOK / "analysis" / "sonuclar" / "K3_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"rho30": round(rho30, 3), "rho90": round(rho90, 3), "hit30": g30.hit_oran.round(1).to_dict(), "hit90": g90.hit_oran.round(1).to_dict(),
                      "carpan": g30.carpan.round(2).to_dict(), "n30": g30.n.to_dict()}, ensure_ascii=False, indent=1, default=str))  # fmt: skip


if __name__ == "__main__":
    main()
