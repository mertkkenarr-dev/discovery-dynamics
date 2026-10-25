"""K5 (keşifsel) · Klon dalgaları: büyük bir hit'in arkasından benzerleri geliyor mu, gelenler kazanıyor mu?

Kullanım: cd analysis && python k5_klon.py
Tanımlar sonuçlara bakılmadan docs/KESIFSEL_K5_K8.md'de sabitlendi: öncü = 2018-01 – 2024-03 çıkışlı T4; takipçi = sonraki 0–24 ayda
kosinüs ≥ 0,70 (duyarlılık 0,60 / 0,80), en benzer öncüye atanır; plasebo öncü = aynı ay + aynı ana tür + T2.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import IKINCIL, KATEGORIK, KOK, MUREKKEP, SOLUK, baslik, kaydet, orneklem, stil, wilson, yukle
from icerik_uzay import yukle_uzay
from ortak_model import beklenen_hit, gozlenen_beklenen, hazirla

KAYNAK = "Kaynak: Steam; Discovery Dynamics analizi. Benzerlik = ilk 10 içerik etiketinin kosinüs benzerliği. Keşifsel."
ESIK, ESIKLER = 0.70, (0.60, 0.70, 0.80)
AY = 30.44
DILIM = [(0, 6), (6, 12), (12, 24)]
TOHUM = 20261025


def tr(v: float, d: int = 1) -> str:
    """Türkçe sayı: 1.234,5"""
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def oncu_ve_plasebo(u: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    kos = u.kohort & u.cikis.between("2018-01-01", "2024-03-31 23:59:59")
    oncu = np.flatnonzero(kos & (u.kademe.astype(str) == "T4"))
    rng = np.random.default_rng(TOHUM)
    aday = u[kos & (u.kademe.astype(str) == "T2")]
    havuz = {k: g.index.values for k, g in aday.groupby([aday.cikis.dt.year, aday.cikis.dt.month, aday.ana_tur.fillna("?")])}
    plasebo = []
    for i in oncu:
        r = u.loc[i]
        v = havuz.get((r.cikis.year, r.cikis.month, r.ana_tur if pd.notna(r.ana_tur) else "?"))
        plasebo.append(rng.choice(v) if v is not None and len(v) else -1)
    return oncu, np.array(plasebo)


def takipciler(u: pd.DataFrame, X: np.ndarray, merkez: np.ndarray, esik: float, yon: int = 1) -> pd.DataFrame:
    """Her oyun için: kendinden önce (yon=1; takipçi) ya da sonra (yon=−1; öncül) 0–24 ay içinde çıkmış, benzerliği ≥ eşik olan
    en benzer merkez (öncü ya da plasebo). sonra_ay her iki yönde de mutlak uzaklık."""
    t = u.cikis.values.astype("datetime64[s]").astype(np.int64) / 86400
    tm = t[merkez]
    en_iyi, en_s, gun = np.full(len(u), -1), np.full(len(u), -np.inf), np.full(len(u), np.nan)
    for a in range(0, len(u), 4096):
        b = min(a + 4096, len(u))
        S = X[a:b] @ X[merkez].T
        fark = (t[a:b, None] - tm[None, :]) * yon
        S[(fark <= 0) | (fark > 24 * AY) | (S < esik)] = -np.inf
        j = S.argmax(axis=1)
        s = S[np.arange(b - a), j]
        ok = np.isfinite(s)
        en_iyi[a:b][ok], en_s[a:b][ok], gun[a:b][ok] = merkez[j[ok]], s[ok], fark[np.arange(b - a), j][ok]
    return pd.DataFrame({"merkez": en_iyi, "benzerlik": en_s, "sonra_ay": gun / AY}).where(lambda d: d.merkez >= 0)


def dalga(u: pd.DataFrame, X: np.ndarray, merkez: np.ndarray) -> pd.DataFrame:
    """−12…+23 aylık pencerelerde benzer (≥ ESIK) çıkışların, aynı penceredeki tüm çıkışlara oranı (binde). Arz büyümesi paydada."""
    t = u.cikis.values.astype("datetime64[s]").astype(np.int64) / 86400
    ts = np.sort(t)
    aylar = np.arange(-12, 24)
    sat = []
    for a in range(0, len(merkez), 256):
        parti = merkez[a : a + 256]
        S = X @ X[parti].T
        for c, m in enumerate(parti):
            j = np.flatnonzero(S[:, c] >= ESIK)
            j = j[j != m]
            f = np.floor((t[j] - t[m]) / AY).astype(int)
            f = f[(f >= -12) & (f < 24)]
            benzer = np.bincount(f + 12, minlength=36)
            sinir = np.searchsorted(ts, t[m] + np.arange(-12, 25) * AY)
            toplam = np.diff(sinir)
            sat.append(pd.DataFrame({"merkez": m, "ay": aylar, "benzer": benzer, "toplam": toplam}))
    d = pd.concat(sat, ignore_index=True)
    d["pay"] = d.benzer / d.toplam.where(d.toplam > 0) * 1000
    return d


def artis(d: pd.DataFrame) -> pd.Series:
    """Merkez başına: sonraki 12 ayın (1…12) ortalama payı ÷ önceki 12 ayın (−12…−1). Sıfıra bölme olmasın diye toplamlar üzerinden."""
    g = d.assign(donem=np.select([d.ay.between(-12, -1), d.ay.between(1, 12)], ["once", "sonra"], "")).query("donem != ''")
    p = g.groupby(["merkez", "donem"])[["benzer", "toplam"]].sum().unstack()
    return p
def basari(a: pd.DataFrame, tk: pd.DataFrame, u: pd.DataFrame) -> pd.DataFrame:
    x = a.merge(u[["appid"]].assign(**tk.reset_index(drop=True)), on="appid").dropna(subset=["merkez"])
    x["dilim"] = pd.cut(x.sonra_ay, [d[0] for d in DILIM] + [DILIM[-1][1]], labels=[f"{d[0]}–{d[1]} ay" for d in DILIM], include_lowest=True)
    g = x.groupby("dilim", observed=False).agg(n=("appid", "size"), hit=("y_hit", "sum"), beklenen=("p_hit", "sum"))
    lo, hi = wilson(g.hit, g.n)
    g["oran"], g["alt"], g["ust"] = g.hit / g.n * 100, lo * 100, hi * 100
    tum = gozlenen_beklenen(int(x.y_hit.sum()), float(x.p_hit.sum()))
    w = wilson(pd.Series([x.y_hit.sum()]), pd.Series([len(x)]))
    g.attrs["tum"] = {**tum, "n": len(x), "hit_oran": float(x.y_hit.mean() * 100), "wilson": [float(w[0].iloc[0] * 100), float(w[1].iloc[0] * 100)]}
    return g


def en_buyuk(u: pd.DataFrame, X: np.ndarray, oncu: np.ndarray, a: pd.DataFrame, n: int = 10) -> list[dict]:
    """Her öncünün KENDİ dalgası (sonraki 0–24 ayda kosinüs ≥ ESIK kohort oyunları). Survivors-like gibi bir akımda birçok öncü aynı
    takipçileri paylaşır; takipçilerinin ≥ %30'u mevcut bir grupla örtüşen öncü o gruba katılır. Grup adı = gruptaki en erken öncü."""
    t = u.cikis.values.astype("datetime64[s]").astype(np.int64) / 86400
    hit = u[["appid"]].merge(a[["appid", "y_hit"]], on="appid", how="left").y_hit.values
    kumeler = {}
    for a0 in range(0, len(oncu), 256):
        parti = oncu[a0 : a0 + 256]
        S = X @ X[parti].T
        for c, m in enumerate(parti):
            f = t - t[m]
            kumeler[m] = set(np.flatnonzero((S[:, c] >= ESIK) & (f > 0) & (f <= 24 * AY) & u.kohort.values))
    gruplar: list[dict] = []
    for m in sorted(kumeler, key=lambda k: -len(kumeler[k])):
        k = kumeler[m]
        if not k:
            continue
        hedef = next((g for g in gruplar if len(k & g["takipci"]) >= 0.3 * len(k)), None)
        if hedef is None:
            gruplar.append({"oncu": [m], "takipci": set(k)})
        else:
            hedef["oncu"].append(m)
            hedef["takipci"] |= k
    sat, uye = [], []
    for sira, g in enumerate(sorted(gruplar, key=lambda g: -len(g["takipci"]))[:n]):
        uyeler = sorted(g["oncu"], key=lambda m: t[m])
        idx = np.fromiter(g["takipci"] - set(uyeler), dtype=int)
        h = hit[idx]
        uye += [{"grup": sira, "appid": int(u.appid[m]), "rol": "oncu"} for m in uyeler]
        uye += [{"grup": sira, "appid": int(u.appid[m]), "rol": "takipci"} for m in idx]
        sat.append({"ilk_oncu": u.ad[uyeler[0]], "ilk_oncu_appid": int(u.appid[uyeler[0]]), "yil": int(u.cikis.dt.year[uyeler[0]]),
                    "oncu_sayisi": len(uyeler), "diger_oncular": [u.ad[m] for m in uyeler[1:6]], "takipci": len(idx),
                    "orneklem": int(np.isfinite(h).sum()), "hit": int(np.nansum(h))})  # fmt: skip
    pd.DataFrame(uye).to_parquet(KOK / "data" / "interim" / "k5_dalga.parquet", index=False)  # web haritası için
    return sat


def artis_orani(p: pd.DataFrame, rng: np.random.Generator) -> dict:
    """Havuzlanmış oran (sonra payı ÷ önce payı) ve merkezler üzerinden bootstrap %95 GA."""

    def oran(q: pd.DataFrame) -> float:
        s = q.sum()
        return float((s[("benzer", "sonra")] / s[("toplam", "sonra")]) / (s[("benzer", "once")] / s[("toplam", "once")]))

    boot = [oran(p.iloc[rng.integers(0, len(p), len(p))]) for _ in range(1000)]
    return {"oran": oran(p), "alt": float(np.percentile(boot, 2.5)), "ust": float(np.percentile(boot, 97.5)), "n_merkez": len(p)}


def ciz_dalga(do: pd.DataFrame, dp: pd.DataFrame, ao: dict, ap: dict) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    for d, ad, renk in ((do, "Büyük hit sonrası (öncü)", KATEGORIK[1]), (dp, "Sıradan oyun sonrası (plasebo)", KATEGORIK[0])):
        g = d.groupby("ay")[["benzer", "toplam"]].sum()
        y = g.benzer / g.toplam * 1000
        ax.plot(g.index, y, color=renk, label=ad)
        ax.text(23.4, y.iloc[-1], ad.split(" (")[0], color=renk, va="center", fontsize=9)
    ax.axvline(0, color=SOLUK, linewidth=1)
    ax.text(0.3, ax.get_ylim()[1] * 0.97, "oyunun çıkışı", color=IKINCIL, fontsize=8.5, va="top")
    ax.set_xlabel("Oyunun çıkışından önce / sonra (ay)")
    ax.set_ylabel("Çok benzer çıkışlar (o ay çıkan 1.000 oyunda)")
    ax.set_xlim(-12, 30)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: tr(v)))
    if ao["alt"] > 1:
        ana = f"Büyük bir hit'ten sonraki yıl ona çok benzeyen oyunların çıkışı {tr(ao['oran'])} katına çıkıyor"
    elif ao["ust"] < 1:
        ana = f"Büyük bir hit'ten sonraki yıl ona çok benzeyen oyunların çıkışı azalıyor ({tr(ao['oran'])} kat)"
    else:
        ana = f"Büyük hit'ten sonra 'klon seli' görünmüyor: benzer oyun çıkışı aynı hızda sürüyor (×{tr(ao['oran'])})"
    baslik(fig, ana,
           f"Sıradan bir oyunun çevresinde aynı dönemde: ×{tr(ap['oran'], 2)} (plasebo: aynı ay ve türde, ilk yılı 100–499 inceleme). Öncü: 2018 – Mart 2024 arası "
           f"ilk yılında 5.000+ inceleme alan {ao['n_merkez']} oyun. Benzer = içerik etiketleri kosinüs ≥ {tr(ESIK, 2)}.")  # fmt: skip
    kaydet(fig, "K5_1_klon_dalgasi", pd.concat({"oncu": do.groupby("ay")[["benzer", "toplam"]].sum(), "plasebo": dp.groupby("ay")[["benzer", "toplam"]].sum()}, axis=1), KAYNAK)


def ciz_basari(go: pd.DataFrame, gk: pd.DataFrame, gp: pd.DataFrame, ort: float) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.2))
    x = np.arange(len(go))
    seriler = ((gk, "Hit'ten önce aynı bölgeye çıkanlar", KATEGORIK[2]), (go, "Hit'ten sonra gelenler (takipçi)", KATEGORIK[1]),
               (gp, "Sıradan oyunun benzerleri", KATEGORIK[0]))  # fmt: skip
    for k, (g, ad, renk) in enumerate(seriler):
        xx = x + (k - 1) * 0.28
        ax.bar(xx, g.oran, width=0.26, color=renk, label=ad)
        ax.errorbar(xx, g.oran, yerr=[g.oran - g.alt, g.ust - g.oran], fmt="none", ecolor=MUREKKEP, elinewidth=1, capsize=3)
        for xi, (_, r) in zip(xx, g.iterrows()):
            ax.text(xi, r.ust + 0.4, f"%{tr(r.oran)}", ha="center", fontsize=8, color=IKINCIL)
    ax.axhline(ort, color=SOLUK, linestyle="--", linewidth=1)
    ax.text(-0.45, ort + 0.25, f"tüm örneklem %{tr(ort)}", va="bottom", ha="left", fontsize=8.5, color=IKINCIL)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"%{v:.0f}"))
    ax.set_xticks(x, [f"Hit'ten {d} önce / sonra" for d in go.index.astype(str)])
    ax.set_ylabel("Hit olma oranı")
    ax.set_ylim(0, max(gk.ust.max(), go.ust.max()) * 1.25)
    ax.legend(loc="upper right", ncols=3, fontsize=8.5)
    to, tk = go.attrs["tum"], gk.attrs["tum"]
    if to["wilson"][0] > tk["wilson"][1]:
        ana = f"Hit'in takipçileri, hit'ten önce aynı bölgeye çıkanlardan daha sık tutuyor (%{tr(to['hit_oran'])} / %{tr(tk['hit_oran'])})"
    elif to["wilson"][1] < tk["wilson"][0]:
        ana = f"Hit'in takipçileri, hit'ten önce aynı bölgeye çıkanlardan daha az tutuyor (%{tr(to['hit_oran'])} / %{tr(tk['hit_oran'])})"
    else:
        ana = f"Avantaj hit'i takip etmekten değil bölgeden: hit'ten önce gelenler de (%{tr(tk['hit_oran'])}) sonra gelenler kadar (%{tr(to['hit_oran'])}) tutuyor"
    baslik(fig, ana, f"Analiz örneklemindeki bağımsız oyunlar; çubuklar %95 Wilson aralığı. Bölge = hit'e kosinüs ≥ {tr(ESIK, 2)}. "
           f"Takipçilerde erken gelen %{tr(go.oran.iloc[0])}, 12–24 ay sonra gelen %{tr(go.oran.iloc[-1])}.")  # fmt: skip
    kaydet(fig, "K5_2_takipci_basari", pd.concat({"oncul": gk, "takipci": go, "plasebo": gp}), KAYNAK)


def main() -> None:
    stil()
    t = yukle()
    u, X = yukle_uzay(t)
    # Bayraklı oyunlar (yetişkin, seri üretici, yazılım, listelenmemiş) ne öncü ne takipçi: analiz örneklemiyle aynı dışlama.
    temiz = ~(u.yetiskin | u.seri_uretici | u.yazilim_suphe | u.listelenmemis).values
    u, X = u[temiz].reset_index(drop=True), X[temiz]
    oncu, plasebo = oncu_ve_plasebo(u)
    plasebo = plasebo[plasebo >= 0]
    print(f"öncü {len(oncu)} · plasebo {len(plasebo)} · uzay {len(u):,} oyun")
    rng = np.random.default_rng(TOHUM)

    do, dp = dalga(u, X, oncu), dalga(u, X, plasebo)
    ao, ap = artis_orani(artis(do), rng), artis_orani(artis(dp), rng)
    ciz_dalga(do, dp, ao, ap)

    a = hazirla(orneklem(t))
    a["p_hit"] = beklenen_hit(a)
    sonuc = {"oncu_n": len(oncu), "plasebo_n": len(plasebo), "dalga": {"oncu": ao, "plasebo": ap}, "esik": {}}
    for e in ESIKLER:
        go, gp = basari(a, takipciler(u, X, oncu, e), u), basari(a, takipciler(u, X, plasebo, e), u)
        sonuc["esik"][str(e)] = {"oncu": {"dilim": go.round(4).to_dict(orient="index"), "tum": go.attrs["tum"]},
                                 "plasebo": {"dilim": gp.round(4).to_dict(orient="index"), "tum": gp.attrs["tum"]}}  # fmt: skip
        if e == ESIK:
            # Ek kontrol (planda yok): aynı bölgede öncüden ÖNCE çıkanlar. Takipçiler kadar iyiyse fark "takip"ten değil bölgeden.
            gk = basari(a, takipciler(u, X, oncu, e, yon=-1), u)
            sonuc["oncul"] = {"dilim": gk.round(4).to_dict(orient="index"), "tum": gk.attrs["tum"]}
            ciz_basari(go, gk, gp, float(a.y_hit.mean() * 100))

    sonuc["en_buyuk_dalgalar"] = en_buyuk(u, X, oncu, a)
    top = pd.DataFrame(sonuc["en_buyuk_dalgalar"])
    print(top.to_string())
    print(json.dumps({k: v for k, v in sonuc.items() if k != "en_buyuk_dalgalar"}, ensure_ascii=False, indent=1, default=str)[:3000])
    (KOK / "analysis" / "sonuclar" / "K5_ozet.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
