"""K6 (keşifsel) · Boş yıldız bölgeleri: az oyun çıkan ama çıkanların beklenenden sık tuttuğu içerik bölgeleri.

Kullanım: cd analysis && python k6_bos_bolge.py
Tanımlar sonuçlara bakılmadan docs/KESIFSEL_K5_K8.md'de sabitlendi: küresel k-ortalamalar (k = 60, kohort, ≥ 3 içerik etiketi);
başarı = gözlenen ÷ beklenen hit (standart kontrollü lojistik); fırsat = O/B GA alt sınırı > 1 ve 2022–25 arzı medyanın altında;
yalnız ≥ 200 örneklem oyunlu bölgeler.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import IKINCIL, KATEGORIK, KOK, MUREKKEP, SOLUK, baslik, kaydet, orneklem, stil, yukle
from icerik_uzay import etiket_adlari, yukle_uzay
from ortak_model import beklenen_hit, gozlenen_beklenen, hazirla
from sklearn.cluster import KMeans

KAYNAK = "Kaynak: Steam; Discovery Dynamics analizi. Bölge = içerik etiketlerine göre 60 küme. Beklenen = yıl, tür, fiyat, EA, dil kontrollü. Keşifsel."
K, TOHUM, MIN_N = 60, 20261025, 200
CINSEL = ("Sexual Content", "Nudity", "Hentai", "NSFW")  # bu etiketlerle tanımlanan bölgeler fırsat sayılmaz (bkz. KESIFSEL günlüğü)


def tr(v: float, d: int = 1) -> str:
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def bolgeler(t: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    u, X = yukle_uzay(t)
    k = u.kohort.values
    u, X = u[k].reset_index(drop=True), X[k]
    km = KMeans(n_clusters=K, n_init=4, random_state=TOHUM).fit(X)  # birim vektörlerde öklid ≈ kosinüs (küresel k-ortalamalar)
    ad = etiket_adlari(t, X.shape[1])
    fark = km.cluster_centers_ - X.mean(axis=0)
    adlar = [" · ".join(ad[np.argsort(-f)[:3]]) for f in fark]
    return u.assign(bolge=km.labels_, bolge_ad=[adlar[i] for i in km.labels_]), X


def tablo(u: pd.DataFrame, a: pd.DataFrame) -> pd.DataFrame:
    y = u.cikis.dt.year
    arz = u[y.between(2022, 2025)].groupby("bolge").size().rename("arz_22_25")
    eski, yeni = u[y.isin([2020, 2021])].groupby("bolge").size(), u[y.isin([2024, 2025])].groupby("bolge").size()
    genel = yeni.sum() / eski.sum()
    buyume = (yeni / eski / genel).rename("goreli_buyume")  # 1 = Steam geneli kadar büyüdü
    x = a.merge(u[["appid", "bolge"]], on="appid")
    g = x.groupby("bolge").agg(n=("appid", "size"), hit=("y_hit", "sum"), beklenen=("p_hit", "sum"), sevilen=("sevilen", "sum"),
                               ortanca_inceleme=("reviews_365", "median"))  # fmt: skip
    ob = pd.DataFrame([gozlenen_beklenen(int(r.hit), r.beklenen) for r in g.itertuples()], index=g.index)
    g = g.join(ob[["ob", "alt", "ust"]]).join(arz).join(buyume)
    g["hit_oran"] = g.hit / g.n * 100
    g["ad"] = u.drop_duplicates("bolge").set_index("bolge").bolge_ad
    g = g[g.n >= MIN_N].copy()
    g["cinsel_tema"] = g.ad.str.contains("|".join(CINSEL))
    g["firsat"] = (g.alt > 1) & (g.arz_22_25 < g.arz_22_25.median()) & ~g.cinsel_tema
    return g.sort_values("ob", ascending=False)


def ciz_harita(g: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 6.2))
    med = g.arz_22_25.median()
    for f, renk in ((False, SOLUK), (True, KATEGORIK[1])):
        h = g[g.firsat == f]
        ax.errorbar(h.arz_22_25, h.ob, yerr=[h.ob - h.alt, h.ust - h.ob], fmt="none", ecolor=renk, elinewidth=0.8, alpha=0.6)
        ax.scatter(h.arz_22_25, h.ob, s=np.sqrt(h.n) * 2.2, color=renk, edgecolor="white", linewidth=1, zorder=3,
                   label="Fırsat bölgesi" if f else "Diğer bölgeler")  # fmt: skip
    for b, r in g[g.firsat].head(8).iterrows():
        ax.annotate(r.ad, (r.arz_22_25, r.ob), xytext=(6, 4), textcoords="offset points", fontsize=7.8, color=MUREKKEP)
    r = g[g.cinsel_tema].sort_values("ob").iloc[-1]  # en uçtaki nokta açıklamasız kalmasın; kalabalık-başarılı bölgeler K6_2'de
    ax.annotate("cinsel içerik etiketli bölge", (r.arz_22_25, r.ob), xytext=(6, 0), textcoords="offset points", fontsize=7.5, color=IKINCIL)
    ax.axhline(1, color=MUREKKEP, linewidth=0.8)
    ax.axvline(med, color=SOLUK, linestyle="--", linewidth=0.8)
    ax.text(med * 1.03, ax.get_ylim()[1] * 0.98, "ortanca arz", fontsize=8, color=IKINCIL, va="top")
    ax.text(ax.get_xlim()[1], 1.02, "beklenen kadar", fontsize=8, color=IKINCIL, ha="right", va="bottom")
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: tr(v, 0)))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"×{tr(v)}"))
    ax.set_xlabel("2022–2025 arasında bölgeye çıkan oyun (log ölçek)")
    ax.set_ylabel("Hit: gözlenen ÷ beklenen")
    ax.legend(loc="upper right")
    f = g[g.firsat]
    if len(f):
        en = f.iloc[0]
        ana = f"{len(f)} içerik bölgesi hem az kalabalık hem beklenenden sık hit veriyor; en güçlüsü {en.ad.split(' · ')[0]} (×{tr(en.ob)})"
    else:
        ana = "Az kalabalık ve beklenenden başarılı bir içerik bölgesi bulunmadı"
    baslik(fig, ana, f"{len(g)} bölge (her biri ≥ {MIN_N} bağımsız oyun). Nokta boyu = örneklem; çubuk %95 GA. Beklenen = aynı yıl, tür, "
           "fiyat, EA ve dil karışımındaki oyunların hit olasılığı. Cinsel içerik etiketleriyle tanımlı bölgeler fırsat sayılmadı.")  # fmt: skip
    kaydet(fig, "K6_1_bos_bolgeler", g.drop(columns=[]).round(4), KAYNAK)


def ciz_liste(g: pd.DataFrame) -> None:
    """Beklenenden anlamlı sık hit veren tüm bölgeler (O/B GA alt > 1); fırsat (az kalabalık) olanlar vurgulu."""
    f = g[(g.alt > 1) & ~g.cinsel_tema].iloc[::-1]
    if f.empty:
        return
    fig, ax = plt.subplots(figsize=(11, max(3.8, 0.42 * len(f) + 2)))
    y = np.arange(len(f))
    renk = np.where(f.firsat, KATEGORIK[1], SOLUK)
    ax.hlines(y, f.alt, f.ust, color=renk, linewidth=2.5)
    ax.scatter(f.ob, y, color=renk, s=45, zorder=3, edgecolor="white", linewidth=1.2)
    for yi, (_, r) in zip(y, f.iterrows()):
        etiket = f"×{tr(r.ob)}, hit %{tr(r.hit_oran)}, 2022–25'te {tr(r.arz_22_25, 0)} oyun, arz büyümesi Steam'in ×{tr(r.goreli_buyume)}"
        ax.text(r.ust + 0.05, yi, etiket, va="center", fontsize=8.2, color=MUREKKEP if r.firsat else IKINCIL)
    ax.set_yticks(y, f.ad, fontsize=8.8)
    for lbl, fr in zip(ax.get_yticklabels(), f.firsat):
        lbl.set_color(KATEGORIK[1] if fr else IKINCIL)
    ax.axvline(1, color=MUREKKEP, linewidth=0.8)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"×{tr(v)}"))
    ax.set_xlim(0.8, f.ust.max() * 2.3)
    ax.set_xlabel("Hit: gözlenen ÷ beklenen (%95 GA)")
    n_f = int(f.firsat.sum())
    baslik(fig, f"Beklenenden sık hit veren {len(f)} bölge; bunların {n_f} tanesi az kalabalık (turuncu: fırsat)",
           "Gri = arzı ortancanın üstünde (kalabalık ama yine de iyi). Bölge adı = genele göre en belirgin üç içerik etiketi. "
           "Fırsat ≠ garanti: yüksek oran ölçülmeyen kaliteyi de yansıtabilir.")  # fmt: skip
    fig.subplots_adjust(top=1 - 1.15 / fig.get_figheight())
    kaydet(fig, "K6_2_firsat_listesi", f.iloc[::-1].round(4), KAYNAK)


def main() -> None:
    stil()
    t = yukle()
    u, _ = bolgeler(t)
    a = hazirla(orneklem(t))
    a["p_hit"] = beklenen_hit(a)
    a["sevilen"] = (a.basari_sinifi == "sevilen_hit").astype(int)
    g = tablo(u, a)
    ciz_harita(g)
    ciz_liste(g)
    pd.set_option("display.width", 250)
    print(g[["ad", "n", "hit_oran", "ob", "alt", "ust", "arz_22_25", "goreli_buyume", "firsat"]].round(2).to_string())
    u[["appid", "bolge", "bolge_ad"]].to_parquet(KOK / "data" / "interim" / "k6_bolge.parquet", index=False)
    ozet = {"k": K, "degerlendirilen": len(g), "firsat_sayisi": int(g.firsat.sum()), "arz_medyan": float(g.arz_22_25.median()),
            "bolgeler": g.reset_index().round(4).to_dict(orient="records")}  # fmt: skip
    (KOK / "analysis" / "sonuclar" / "K6_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
