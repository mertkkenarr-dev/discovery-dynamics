"""K8 (keşifsel) · Steam algoritması eşiği: toplam inceleme 10'u (puan görünür olur) ya da 50'yi geçince ilgi sıçrıyor mu?

Kullanım: cd analysis && python k8_esik.py
Tanımlar sonuçlara bakılmadan docs/KESIFSEL_K5_K8.md'de sabitlendi: gözlem = oyun × inceleme dilimi; c = dilim başındaki toplam inceleme;
y = log(1 + dilimdeki inceleme / gün × 30); çıkış dilimi ve ilk 30 gün dışarıda. Eşik t için bant [0,5t, 1,5t), iki taraflı yerel doğrusal,
sıçrama = 1(c ≥ t) katsayısı, oyun düzeyinde kümelenmiş SE. Plasebo eşikler 20, 30, 40, 60, 70, 80.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from grafik import IKINCIL, KATEGORIK, KOK, MUREKKEP, SOLUK, baslik, kaydet, orneklem, stil, yukle

KAYNAK = "Kaynak: Steam inceleme grafiği (aylık/haftalık dilimler); Discovery Dynamics analizi. Keşifsel."
GERCEK, PLASEBO = (10, 50), (20, 30, 40, 60, 70, 80)


def tr(v: float, d: int = 1) -> str:
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gozlemler(t: pd.DataFrame) -> pd.DataFrame:
    a = orneklem(t)[["appid", "cikis"]]
    s = pd.read_parquet(KOK / "data" / "interim" / "inceleme_seri.parquet")
    s = s[s.appid.isin(a.appid)].merge(a, on="appid").sort_values(["appid", "bas"])
    s["n"] = s.up + s.down
    g = s.groupby("appid")
    s["c"] = g.n.cumsum() - s.n  # dilim başındaki toplam (çıkış öncesi incelemeler dahil: Steam puanı onları da sayar)
    s["c_up"] = g.up.cumsum() - s.up
    s["gun"] = (s.son - s.bas).dt.days.clip(lower=1)
    s["y"] = np.log1p(s.n / s.gun * 30)
    s["yas"] = (s.bas - s.cikis.dt.normalize()).dt.days
    s["olumlu"] = (s.c_up / s.c).where(s.c > 0)
    s["toplam"] = g.n.transform("sum")  # serideki ömür boyu inceleme
    return s[s.yas >= 30].copy()  # lansman zirvesi (çıkış dilimi ve ilk 30 gün) dışarıda


def sicrama(s: pd.DataFrame, esik: int, kosul: pd.Series | None = None) -> dict:
    d = s[(s.c >= 0.5 * esik) & (s.c < 1.5 * esik)]
    if kosul is not None:
        d = d[kosul.reindex(d.index).fillna(False)]
    d = d.assign(D=(d.c >= esik).astype(int), x=d.c - esik)
    m = smf.ols("y ~ D + x + D:x", data=d).fit(cov_type="cluster", cov_kwds={"groups": d.appid})
    b, (lo, hi) = m.params["D"], m.conf_int().loc["D"]
    return {"esik": esik, "sicrama": float(b), "alt": float(lo), "ust": float(hi), "p": float(m.pvalues["D"]), "n": int(m.nobs),
            "oyun": int(d.appid.nunique()), "yuzde": float(np.expm1(b) * 100)}  # fmt: skip


def ciz_tahmin(r: pd.DataFrame, secilim: dict) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    renk = [KATEGORIK[1] if e in GERCEK else SOLUK for e in r.esik]
    x = np.arange(len(r))
    ax.vlines(x, r.alt, r.ust, color=renk, linewidth=2.5)
    ax.scatter(x, r.sicrama, color=renk, s=55, zorder=3, edgecolor="white", linewidth=1.2)
    for xi, (_, q) in zip(x, r.iterrows()):
        ax.text(xi + 0.12, q.sicrama, f"{'+' if q.yuzde >= 0 else '−'}%{tr(abs(q.yuzde), 1)}", va="center", fontsize=8.5, color=IKINCIL)
    ax.axhline(0, color=MUREKKEP, linewidth=0.8)
    ax.set_xticks(x, [f"{e}\n{'gerçek' if e in GERCEK else 'plasebo'}" for e in r.esik])
    ax.set_xlabel("Toplam inceleme eşiği")
    ax.set_ylabel("Eşiği geçince inceleme hızındaki sıçrama (log)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: tr(v, 2)))
    p = r.set_index("esik")
    q = p.loc[50]
    yuz = lambda v: f"{'+' if v >= 0 else '−'}%{tr(abs(np.expm1(v) * 100), 1)}"  # noqa: E731
    if q.alt <= 0 <= q.ust:
        ana = f"'50 incelemeyi geç, algoritma seni görsün' veride yok: 50'de sıçrama {yuz(q.sicrama)} (GA {yuz(q.alt)} … {yuz(q.ust)})"
    else:
        ana = f"50 incelemede {'sıçrama' if q.sicrama > 0 else 'düşüş'} var: {yuz(q.sicrama)} (GA {yuz(q.alt)} … {yuz(q.ust)})"
    s30, s100 = secilim["10_omur30"], secilim["10_omur100"]
    baslik(fig, ana,
           f"10'daki düşüş ({yuz(p.loc[10].sicrama)}) seçilimle uyumlu: seri yalnız ömür boyu 10+ incelemeye ulaşan oyunlarda var, eşik altı şişiyor. "
           f"Ömür boyu ≥ 30 şartıyla {yuz(s30['sicrama'])}, ≥ 100 ile {yuz(s100['sicrama'])} (GA {yuz(s100['alt'])} … {yuz(s100['ust'])}). "
           "Gri: plasebo eşikler. Çubuk %95 GA, oyun düzeyinde kümelenmiş; ilk 30 gün dışarıda.")  # fmt: skip
    fig.subplots_adjust(bottom=0.2)
    kaydet(fig, "K8_1_esik_sicramalari", r.set_index("esik").round(5), KAYNAK)


def ciz_kutular(s: pd.DataFrame) -> None:
    fig, eksenler = plt.subplots(1, 2, figsize=(11, 4.6))
    veri = {}
    for ax, e in zip(eksenler, GERCEK):
        d = s[(s.c >= 0.5 * e) & (s.c < 1.5 * e)]
        kova = (d.c // max(1, e // 10)) * max(1, e // 10)
        g = d.groupby(kova).y.agg(["mean", "size"])
        veri[e] = g
        for taraf, renk in ((g.index < e, KATEGORIK[0]), (g.index >= e, KATEGORIK[1])):
            h = g[taraf]
            ax.scatter(h.index, np.expm1(h["mean"]), s=np.sqrt(h["size"]) * 1.2, color=renk, alpha=0.85, edgecolor="white", linewidth=0.6)
            k = np.polyfit(h.index, h["mean"], 1, w=np.sqrt(h["size"]))
            xx = np.linspace(h.index.min(), h.index.max(), 20)
            ax.plot(xx, np.expm1(np.polyval(k, xx)), color=renk, linewidth=1.6)
        ax.axvline(e - 0.5, color=SOLUK, linestyle="--", linewidth=1)
        ax.set_title(f"Eşik {e}" + (" (puan görünür olur)" if e == 10 else " (yaygın kanı)"), fontsize=10.5)
        ax.set_xlabel("Dilim başındaki toplam inceleme")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: tr(v, 2)))
    eksenler[0].set_ylabel("İnceleme hızı (30 günde, kova ortalaması)")
    baslik(fig, "Eşiğin iki yanında inceleme hızı: kovalar ve iki taraflı doğrusal uyum",
           "Mavi: eşik altı, turuncu: eşik üstü. Nokta boyu = gözlem sayısı. Eşikte kırılma varsa iki çizgi birleşmez. "
           "Soldaki dik eşik-altı eğim seçilimden: seride yalnız eninde sonunda 10'u geçen oyunlar var.")
    fig.subplots_adjust(top=0.78)
    kaydet(fig, "K8_2_esik_kovalari", pd.concat(veri, names=["esik", "kova"]).round(4), KAYNAK)


def main() -> None:
    stil()
    s = gozlemler(yukle())
    print(f"gözlem {len(s):,} · oyun {s.appid.nunique():,}")
    r = pd.DataFrame([sicrama(s, e) for e in sorted(GERCEK + PLASEBO)])
    # Seçilim düzeltmesi (sonuç görüldükten sonra eklendi, KESIFSEL günlüğü): seri yalnız ömür boyu ≥ 10 olan oyunlarda var, bu yüzden
    # c < 10 gözlemleri "eninde sonunda 10'u geçecek" oyunlardan; eşik altını şişirir. Ömür boyu ≥ F şartı iki yana da benzer koşul koyar.
    secilim = {f"10_omur{F}": sicrama(s[s.toplam >= F], 10) for F in (15, 30, 100, 300)}
    secilim |= {f"20_omur{F}": sicrama(s[s.toplam >= F], 20) for F in (100, 300)}
    print(pd.DataFrame(secilim).T.round(4).to_string())
    ciz_tahmin(r, secilim)
    ciz_kutular(s)
    alt = {f"{e}_{ad}": sicrama(s, e, kosul) for e in GERCEK for ad, kosul in (("olumlu_80+", s.olumlu >= 0.8), ("olumlu_80-", s.olumlu < 0.8))}
    print(r.round(4).to_string())
    print(pd.DataFrame(alt).T.round(4).to_string())
    ozet = {"gozlem": len(s), "oyun": int(s.appid.nunique()), "tahmin": r.round(5).to_dict(orient="records"), "alt_grup": alt, "secilim": secilim}
    (KOK / "analysis" / "sonuclar" / "K8_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
