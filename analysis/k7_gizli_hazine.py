"""K7 (keşifsel) · Gizli hazineler: çok beğenilen ama görülmeyen oyunlar, çok beğenilip görülenlerden neyle ayrılıyor?

Kullanım: cd analysis && python k7_gizli_hazine.py
Tanımlar sonuçlara bakılmadan docs/KESIFSEL_K5_K8.md'de sabitlendi: gizli = 10 ≤ reviews_365 < 100 ve beğeni Wilson alt sınırı ≥ 0,80;
görünür = reviews_365 ≥ 500 ve Wilson ≥ 0,80. Karşılaştırma yalnız çıkış öncesi bilinen niteliklerle: SMD + tek lojistik model.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import IKINCIL, KATEGORIK, KOK, MUREKKEP, SOLUK, baslik, kaydet, orneklem, stil, yukle
from ortak_model import TURLER, hazirla, katsayi, logit

KAYNAK = "Kaynak: Steam; Discovery Dynamics analizi. Beğeni = ilk yıl olumlu inceleme oranının Wilson %95 alt sınırı. Keşifsel."
ESIK = 0.80
# Mağazadaki BUGÜNKÜ değer: başarılı oyunlar dil (özellikle Çince) sonradan ekliyor (M2b, K4 sızıntısı) → ters nedensellik şüphesi.
SONRADAN = {"Çince destek", "Dil sayısı"}

# (sütun, okunur ad); hepsi çıkıştan önce bilinebilir. Çince sonradan eklenebiliyor (M2b) → yorumda dikkat.
NITELIK = [
    ("log_fiyat", "Fiyat"), ("f2p_i", "Ücretsiz"), ("log_dil", "Dil sayısı"), ("cince", "Çince destek"),
    ("ea", "Early Access ile çıkış"), ("demo_once", "Çıkıştan önce demo"), ("deneyimli", "Stüdyonun önceki oyunu var"),
    ("kendi", "Kendi yayını"), ("yenilik", "Yenilik (etiket kombinasyonu)"), ("log_ayni_hafta", "Aynı hafta çıkan oyun"),
    ("buyuk_rakip", "Aynı hafta büyük yayıncı çıkışı"), ("mac_linux", "Mac ya da Linux desteği"), ("playtest", "Playtest"),
    *[(t, f"Tür: {t}") for t in TURLER],
]  # fmt: skip


def tr(v: float, d: int = 1) -> str:
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def hazirla_k7(t: pd.DataFrame) -> pd.DataFrame:
    d = hazirla(orneklem(t))
    r, w = d.reviews_365, d.begeni_wilson
    d["grup"] = np.select([(r >= 10) & (r < 100) & (w >= ESIK), (r >= 500) & (w >= ESIK)], ["gizli", "gorunur"], "")
    d = d[d.grup != ""].copy()
    d["gorunur"] = (d.grup == "gorunur").astype(int)
    d["log_fiyat"] = np.log1p(d.fiyat_liste_usd.fillna(0))
    d["f2p_i"] = d.f2p.astype(int)
    d["cince"] = d.schinese.fillna(False).astype(int)
    d["demo_once"] = d.demo_cikis_oncesi.fillna(False).astype(int)
    d["yenilik"] = d.novelty_k10
    d["log_ayni_hafta"] = np.log1p(d.ayni_hafta_cikan)
    d["buyuk_rakip"] = d.ayni_hafta_buyuk_yayinci.fillna(False).astype(int)
    d["mac_linux"] = (d.mac.fillna(False) | d.linux.fillna(False)).astype(int)
    d["playtest"] = d.playtest_var.fillna(False).astype(int)
    return d


def smd(d: pd.DataFrame) -> pd.DataFrame:
    sat = []
    for c, ad in NITELIK:
        a, b = d.loc[d.gorunur == 1, c].dropna(), d.loc[d.gorunur == 0, c].dropna()
        s = np.sqrt((a.var() + b.var()) / 2)
        sat.append({"nitelik": ad, "gorunur": a.mean(), "gizli": b.mean(), "smd": (a.mean() - b.mean()) / s if s > 0 else 0.0})
    return pd.DataFrame(sat).set_index("nitelik").sort_values("smd")


def model(d: pd.DataFrame, dilsiz: bool = False) -> pd.DataFrame:
    x = d.dropna(subset=["yenilik"])
    sutun = [c for c, a in NITELIK if not (dilsiz and a in SONRADAN)]
    m = logit("gorunur ~ " + " + ".join(sutun) + " + C(yil)", x)
    ad = dict(NITELIK)
    return pd.DataFrame({ad[c]: katsayi(m, c, us=True) for c in sutun}).T


def ciz(s: pd.DataFrame, n_gizli: int, n_gorunur: int) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 7.2))
    y = np.arange(len(s))
    renk = np.where(s.index.isin(SONRADAN), SOLUK, np.where(s.smd > 0, KATEGORIK[1], KATEGORIK[0]))
    ax.hlines(y, 0, s.smd, color=renk, linewidth=2.5)
    ax.scatter(s.smd, y, color=renk, s=40, zorder=3, edgecolor="white", linewidth=1)
    for yi, (ad, r) in zip(y, s.iterrows()):
        # log ortalaması → geometrik ortalama (okunur birim); log1p olduğu için exp − 1
        if ad.startswith("Fiyat"):
            metin = f"≈ {tr(np.expm1(r.gizli))} → {tr(np.expm1(r.gorunur))} USD"  # "$" matplotlib'te matematik kipini açar
        elif ad.startswith("Dil"):
            metin = f"≈ {tr(np.expm1(r.gizli))} → {tr(np.expm1(r.gorunur))} dil"
        elif ad.startswith("Aynı hafta çıkan"):
            metin = f"≈ {tr(np.expm1(r.gizli), 0)} → {tr(np.expm1(r.gorunur), 0)} oyun"
        elif ad.startswith("Yenilik"):
            metin = f"{tr(r.gizli, 2)} → {tr(r.gorunur, 2)}"
        else:
            metin = f"%{tr(r.gizli * 100, 0)} → %{tr(r.gorunur * 100, 0)}"
        ax.text(r.smd + (0.03 if r.smd >= 0 else -0.03), yi, metin, va="center", ha="left" if r.smd >= 0 else "right", fontsize=7.8, color=IKINCIL)
    ax.set_yticks(y, [f"{a} *" if a in SONRADAN else a for a in s.index], fontsize=8.8)
    ax.axvline(0, color=MUREKKEP, linewidth=0.8)
    ax.axvspan(-0.1, 0.1, color=SOLUK, alpha=0.08)
    lo, hi = s.smd.min(), s.smd.max()
    ax.set_xlim(lo - 0.45, hi + 0.45)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: tr(v, 2)))
    ax.set_xlabel("Standartlaştırılmış fark (sağ: görünür hazinelerde daha yaygın / yüksek)")
    g = s[~s.index.isin(SONRADAN)]
    ust, alt = g.index[-1], g.index[0]
    oku = lambda a: f"{a[5:]} türü" if a.startswith("Tür: ") else a.lower()  # noqa: E731
    baslik(fig, f"Görünür hazineyi gizliden en çok ayıran {oku(ust)} (fark {tr(g.smd.iloc[-1], 2)}); gizlilerde daha yaygın: {oku(alt)}",
           f"{tr(n_gizli, 0)} gizli hazine (ilk yıl 10–99 inceleme) ve {tr(n_gorunur, 0)} görünür hazine (500+), ikisinde de beğeni alt sınırı ≥ %80. "
           "Etiketler 'gizli → görünür' (fiyat, dil ve aynı hafta için geometrik ortalama); gri bant |fark| < 0,1. * Bugünkü mağaza değeri: başarılı oyunlar dili sonradan ekliyor, "
           "bu yüzden fark büyük ölçüde sonucun kendisi olabilir.")  # fmt: skip
    kaydet(fig, "K7_1_gizli_hazine_farklar", s.round(4), KAYNAK)


def main() -> None:
    stil()
    t = yukle()
    d = hazirla_k7(t)
    n_gizli, n_gorunur = int((d.gorunur == 0).sum()), int(d.gorunur.sum())
    s = smd(d)
    ciz(s, n_gizli, n_gorunur)
    m, m2 = model(d), model(d, dilsiz=True)
    print(s.round(3).to_string())
    print(m2.round(3).to_string())
    liste = d[d.gorunur == 0].nlargest(12, "begeni_wilson")[["appid", "ad", "yil", "ana_tur", "fiyat_liste_usd", "reviews_365", "olumlu_oran_365"]]
    print(liste.to_string())
    a = orneklem(t)
    cok_begenilen = int((a.begeni_wilson >= ESIK).sum())
    ozet = {"n_gizli": n_gizli, "n_gorunur": n_gorunur, "cok_begenilen_toplam": cok_begenilen, "smd": s.round(4).to_dict(orient="index"),
            "model_or": m.round(4).to_dict(orient="index"), "model_or_dilsiz": m2.round(4).to_dict(orient="index"), "ornek_liste": liste.round(3).to_dict(orient="records")}  # fmt: skip
    (KOK / "analysis" / "sonuclar" / "K7_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
