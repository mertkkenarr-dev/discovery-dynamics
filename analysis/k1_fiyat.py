"""K1 (keşifsel) · Fiyatın tatlı noktası: fiyat noktası ve bandına göre başarı, türe göre, ve fiyat–beğeni ilişkisi.

Kullanım: python analysis/k1_fiyat.py
Örneklem: analiz örneklemi, ücretli ve fiyatı bilinen oyunlar (F2P ayrı, R8).
Sonuç: hit ve sevilen hit. Ticari başarı KULLANILMAZ: fiyat gelir formülünün içinde (döngüsellik, HIPOTEZLER 2026-10-24).
Sınır: fiyat Ekim 2026 liste fiyatı (çıkış fiyatı değil; başarısız oyunlar sonradan indirmiş olabilir) ve oyunun kapsamını/bütçesini
    yansıtır. "Bu fiyatı koy" değil, "bu fiyattaki oyunlar nasıl performans gösteriyor" sorusunu cevaplar.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import KATEGORIK, KOK, MUREKKEP, YUZEY, baslik, kaydet, orneklem, stil, wilson, yukle
from ortak_model import TURLER, hazirla

KAYNAK = "Kaynak: Steam (Ekim 2026 liste fiyatı, indirimsiz); Discovery Dynamics analizi. Fiyat çıkış fiyatı değildir."
BANT = ["<5", "5-10", "10-20", "20-30", ">=30"]
BANT_AD = {"<5": "<5", "5-10": "5–10", "10-20": "10–20", "20-30": "20–30", ">=30": "30+"}


def main() -> None:
    stil()
    a = hazirla(orneklem(yukle()))
    p = a[a.fiyat != "f2p"].copy()
    p["sevilen"] = (p.basari_sinifi == "sevilen_hit").astype(int)
    p["nokta"] = p.fiyat_liste_usd.round(2)

    say = p.nokta.value_counts()
    noktalar = sorted(say[say >= 300].index)
    g = p[p.nokta.isin(noktalar)].groupby("nokta").agg(n=("appid", "size"), hit=("y_hit", "sum"), sevilen=("sevilen", "sum"))
    for c in ("hit", "sevilen"):
        lo, hi = wilson(g[c], g.n)
        g[f"{c}_oran"], g[f"{c}_alt"], g[f"{c}_ust"] = g[c] / g.n * 100, lo * 100, hi * 100
    fig, ax = plt.subplots(figsize=(10, 4.8))
    x = np.arange(len(g))
    for i, (c, ad) in enumerate([("hit", "Hit (500+ inceleme)"), ("sevilen", "Sevilen hit (+%80 olumlu)")]):
        ax.errorbar(x + (i - 0.5) * 0.22, g[f"{c}_oran"], yerr=[g[f"{c}_oran"] - g[f"{c}_alt"], g[f"{c}_ust"] - g[f"{c}_oran"]],
                    fmt="o", color=KATEGORIK[i], ms=6, elinewidth=1.5, capsize=0, label=ad, markeredgecolor=YUZEY)  # fmt: skip
    ax.set_xticks(x, [f"{v:.2f}".replace(".", ",") for v in g.index], rotation=0, fontsize=8.5)
    ax.set_xlabel("Liste fiyatı (USD); en az 300 oyunun kullandığı fiyat noktaları")
    ax.set_ylabel("Oyunların yüzdesi")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8.8)
    en = g.hit_oran.idxmax()
    baslik(fig, f"Hit oranı fiyatla birlikte artıyor; en yüksek {en:.2f} USD'de (%{g.hit_oran.max():.0f})".replace(".", ","),
           "Ücretli bağımsız oyunlar; her nokta en az 300 oyun (sayılar CSV'de). Çizgiler %95 GA. Fiyat oyunun kapsamını da yansıtır: neden-sonuç değil.")  # fmt: skip
    fig.subplots_adjust(top=0.78)
    kaydet(fig, "K1_1_fiyat_noktalari", g.round(3), KAYNAK)

    tt = []
    for tur in TURLER:
        s = p[p[tur] == 1].groupby("fiyat").agg(n=("appid", "size"), hit=("y_hit", "mean"), sevilen=("sevilen", "mean")).reindex(BANT)
        tt.append(s.assign(tur=tur))
    tt = pd.concat(tt).reset_index()
    fig, eksen = plt.subplots(2, 4, figsize=(11, 5.6), sharey=True)
    enler = {}
    for ax, tur in zip(eksen.flat, TURLER):
        s = tt[tt.tur == tur].set_index("fiyat").loc[BANT]
        gecerli = s.n >= 100
        renk = [KATEGORIK[0] if g_ else "#e1e0d9" for g_ in gecerli]
        ax.bar(range(5), (s.hit * 100).where(gecerli, 0), color=renk, width=0.65)
        if gecerli.any():
            eniyi = (s.hit.where(gecerli)).idxmax()
            enler[tur] = BANT_AD[eniyi]
            j = BANT.index(eniyi)
            ax.text(j, s.hit[eniyi] * 100 + 1.5, f"%{s.hit[eniyi] * 100:.0f}", ha="center", fontsize=8.5, color=MUREKKEP, fontweight="bold")
        ax.set_title(tur, fontsize=10)
        ax.set_xticks(range(5), [BANT_AD[b] for b in BANT], fontsize=7.5)
        ax.grid(axis="x", visible=False)
    for ax in eksen[:, 0]:
        ax.set_ylabel("Hit oranı (%)")
    ust = [t_ for t_, v in enler.items() if v in ("20–30", "30+")]
    diger = [f"{t_} ({v})" for t_, v in enler.items() if v not in ("20–30", "30+")]
    baslik(fig, f"{len(ust)}/{len(enler)} türde hit oranı en yüksek 20 USD üstünde" + (f"; istisna: {', '.join(diger)}" if diger else ""),
           "Ücretli bağımsız oyunlar, fiyat bandı (USD) × Steam türü. Boş = 100'den az oyun. Bir oyun birden çok türde olabilir.")  # fmt: skip
    fig.subplots_adjust(top=0.82, hspace=0.45, wspace=0.08)
    kaydet(fig, "K1_2_tur_fiyat_bandi", tt.round(4).set_index(["tur", "fiyat"]), KAYNAK)

    b = p[p.reviews_365 >= 50].groupby("fiyat").agg(n=("appid", "size"), olumlu=("olumlu_oran_365", "median"),
                                                     cok_olumlu=("olumlu_oran_365", lambda v: (v >= 0.8).mean())).reindex(BANT)  # fmt: skip
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.plot(range(5), b.cok_olumlu * 100, color=KATEGORIK[0], marker="o", markersize=8)
    for j, (v, n) in enumerate(zip(b.cok_olumlu * 100, b.n)):
        ax.text(j, v + 3, f"%{v:.0f}  (n={n:,})", ha="center", va="bottom", fontsize=9, color=MUREKKEP)
    ax.set_xticks(range(5), [f"{BANT_AD[x]} USD" for x in BANT])
    ax.set_xlim(-0.5, 4.5)
    ax.set_ylim(0, 100)
    ax.set_ylabel("İncelemelerinin %80+'ı olumlu olanlar (%)")
    yon = "daha sert" if b.cok_olumlu.iloc[-1] < b.cok_olumlu.iloc[1] else "daha sert değil"
    baslik(fig, f"Pahalı oyunlar {yon} yargılanıyor: 'çok olumlu' oranı fiyat bandına göre",
           "İlk yılında 50+ inceleme alan ücretli bağımsız oyunlar. Olumlu oran: ilk yılın incelemeleri. Ortanca olumlu oranlar CSV'de.")  # fmt: skip
    fig.subplots_adjust(top=0.8)
    kaydet(fig, "K1_3_fiyat_begeni", b.round(4), KAYNAK)

    ozet = {"n": len(p), "noktalar": g.round(3).to_dict("index"), "tur_en_iyi_bant": enler, "begeni": b.round(4).to_dict("index")}
    (KOK / "analysis" / "sonuclar" / "K1_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(
        json.dumps(
            {"n": ozet["n"], "tur_en_iyi_bant": enler, "begeni": ozet["begeni"], "noktalar_hit": g.hit_oran.round(2).to_dict()}, ensure_ascii=False, indent=1
        )
    )


if __name__ == "__main__":
    main()
