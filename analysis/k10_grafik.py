"""K10 grafikleri: alt tür risk-ödül haritası, hibrit türler, eğilimler. Başlıklar sonuçtan üretilir."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import IKINCIL, KATEGORIK, MUREKKEP, SOLUK, baslik, kaydet, stil

KAYNAK = "Kaynak: Steam; Discovery Dynamics analizi. Alt tür = oyunun ilk 10 etiketindeki tür etiketi (oyuncu oylu, R4). Keşifsel."


def tr(v: float, d: int = 1) -> str:
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def ciz_karne(k: pd.DataFrame, ort_hit: float, ort_gor: float) -> None:
    stil()
    fig, ax = plt.subplots(figsize=(11, 7))
    hizli = k.goreli_buyume >= 1.5
    for h, renk, ad in ((False, KATEGORIK[0], "Arzı Steam'den yavaş ya da benzer büyüyen"), (True, KATEGORIK[1], "Arzı Steam'in ≥ 1,5 katı hızla büyüyen (2022–23 → 2024–25)")):
        x = k[hizli == h]
        ax.scatter(x.gorunmez, x.hit, s=np.sqrt(x.n) * 3, color=renk, alpha=0.8, edgecolor="white", linewidth=1, label=ad, zorder=3)
    ax.axhline(ort_hit, color=SOLUK, linestyle="--", linewidth=0.8)
    ax.axvline(ort_gor, color=SOLUK, linestyle="--", linewidth=0.8)
    ax.text(k.gorunmez.min(), ort_hit + 0.3, f"örneklem ortalaması %{tr(ort_hit)}", fontsize=8, color=IKINCIL)
    etiket = pd.concat([k.nlargest(9, "hit"), k.nsmallest(4, "hit"), k.nsmallest(3, "gorunmez")]).drop_duplicates("tur")
    for _, r in etiket.iterrows():
        ax.annotate(r.tur, (r.gorunmez, r.hit), xytext=(5, 3), textcoords="offset points", fontsize=8, color=MUREKKEP)
    ax.set_xlabel("Risk: ilk yılında 10'dan az inceleme alan oyunların payı")
    ax.set_ylabel("Ödül: hit olan oyunların payı")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"%{v:.0f}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"%{v:.0f}"))
    ax.legend(loc="upper right", fontsize=8.5)
    en, dusuk = k.iloc[0], k.loc[k.gorunmez.idxmin()]
    baslik(fig, f"En ödüllü alt tür {en.tur} (hit %{tr(en.hit)}); en az riskli {dusuk.tur} (görünmez %{tr(dusuk.gorunmez)})",
           f"2021–2025 çıkışlı bağımsız oyunlar (öncesinde etiket kapsamı seçilimli). {len(k)} alt tür, her biri ≥ 500 oyun; nokta boyu = oyun sayısı. Sol üst = düşük risk, yüksek ödül. Ham oranlar (fiyat ve kapsam "
           "farkı içerir); kontrollü karşılaştırma K10_ozet.json'da (O/B).")  # fmt: skip
    kaydet(fig, "K10_1_tur_karnesi", k.set_index("tur").round(4), KAYNAK)


def ciz_hibrit(h: pd.DataFrame) -> None:
    stil()
    a = h[h.q < 0.05]
    g = pd.concat([h.head(10), h.tail(6)]).drop_duplicates("cift").sort_values("ob")  # anlamlı olsun olmasın en uç çiftler, GA'larıyla
    fig, ax = plt.subplots(figsize=(10.5, 0.42 * len(g) + 2.2))
    y = np.arange(len(g))
    renk = np.where(g.q >= 0.05, SOLUK, np.where(g.ob > 1, KATEGORIK[1], KATEGORIK[0]))
    ax.hlines(y, g.alt, g.ust, color=renk, linewidth=2.5)
    ax.scatter(g.ob, y, color=renk, s=45, zorder=3, edgecolor="white", linewidth=1.2)
    for yi, (_, r) in zip(y, g.iterrows()):
        ax.text(r.ust * 1.03, yi, f"×{tr(r.ob)}  (hit %{tr(r.hit)}, {tr(r.n, 0)} oyun)", va="center", fontsize=8, color=IKINCIL)
    ax.set_yticks(y, g.cift, fontsize=8.8)
    ax.axvline(1, color=MUREKKEP, linewidth=0.8)
    ax.set_xscale("log")
    ax.set_xticks([0.25, 0.5, 1, 2, 4], ["×0,25", "×0,5", "×1", "×2", "×4"])
    ax.minorticks_off()
    ax.set_xlim(max(g.alt.min(), 0.05) * 0.8, g.ust.max() * 3)
    ax.set_xlabel("Hit: gözlenen ÷ türlerin tek tek öngördüğü (log ölçek)")
    if len(a):
        en = a.iloc[0]
        ana = f"En iyi tür karışımı {en.cift}: parçalarının öngördüğünün {tr(en.ob)} katı hit"
    else:
        ana = f"Tür karışımları parçalarının toplamı kadar: {len(h)} çiftin hiçbiri çoklu test sonrası beklenenden farklı değil"
    baslik(fig, ana, f"{len(h)} çiftten O/B'si en yüksek 10 ve en düşük 6 tanesi; gri = Benjamini–Hochberg q ≥ 0,05 (anlamsız). Beklenen: yıl, tür, fiyat, "
           "EA, dil ve tüm alt türlerin ayrı etkileri. Eş anlamlı çiftler hariç. 2021–2025 çıkışlı oyunlar.")  # fmt: skip
    fig.subplots_adjust(top=1 - 1.25 / fig.get_figheight(), left=0.32)
    kaydet(fig, "K10_2_hibrit_turler", g.set_index("cift").round(4), KAYNAK)


def ciz_egilim(k: pd.DataFrame) -> None:
    stil()
    x = k.dropna(subset=["egilim"])
    g = pd.concat([x.nlargest(8, "egilim"), x.nsmallest(8, "egilim")]).drop_duplicates("tur").sort_values("egilim")
    fig, ax = plt.subplots(figsize=(10, 0.42 * len(g) + 2.2))
    y = np.arange(len(g))
    anl = (g.egilim_alt > 0) | (g.egilim_ust < 0)
    for yi, (_, r), a_ in zip(y, g.iterrows(), anl):
        renk = (KATEGORIK[1] if r.egilim > 0 else KATEGORIK[0]) if a_ else SOLUK
        ax.annotate("", xy=(r.hit_gec, yi), xytext=(r.hit_erken, yi), arrowprops={"arrowstyle": "->", "color": renk, "lw": 2})
        ax.text(max(r.hit_gec, r.hit_erken) + 0.6, yi, f"%{tr(r.hit_erken)} → %{tr(r.hit_gec)}", va="center", fontsize=8, color=IKINCIL)
    ax.set_yticks(y, g.tur, fontsize=8.8)
    ax.set_ylim(-0.7, len(g) - 0.3)
    ax.set_xlim(0, max(g.hit_gec.max(), g.hit_erken.max()) * 1.3)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"%{v:.0f}"))
    ax.set_xlabel("Hit oranı: 2021–2022 → 2023–2024")
    puan = lambda v: f"{'+' if v >= 0 else '−'}{tr(abs(v))} puan"  # noqa: E731
    yuk = x[x.egilim_alt > 0].sort_values("egilim", ascending=False)
    dus = x[x.egilim_ust < 0].sort_values("egilim")
    parca = [f"anlamlı yükselen: {', '.join(f'{r.tur} ({puan(r.egilim)})' for r in yuk.head(3).itertuples())}" if len(yuk) else "anlamlı yükselen alt tür yok",
             f"anlamlı düşen: {', '.join(f'{r.tur} ({puan(r.egilim)})' for r in dus.head(3).itertuples())}" if len(dus) else "anlamlı düşen yok"]  # fmt: skip
    baslik(fig, "Alt türlerde hit oranı eğilimi: " + "; ".join(parca),
           "Ok: aynı alt türde 2021–22 ve 2023–24 çıkışlı bağımsız oyunların hit oranı. Gri: fark %95 GA'sı 0'ı içeriyor (Newcombe).")
    fig.subplots_adjust(top=1 - 1.2 / fig.get_figheight(), left=0.25)
    kaydet(fig, "K10_3_tur_egilimleri", g.set_index("tur")[["hit_erken", "hit_gec", "egilim", "egilim_alt", "egilim_ust"]].round(4), KAYNAK)
