"""M1 · Survivorship: Steam'de oyunların ne kadarı görünür oluyor, bu tür / fiyat / yıl / stüdyoya göre nasıl değişiyor?

Kullanım: python analysis/m1_gorunurluk.py
Örneklem: grafik.orneklem (kohort, organik, reviews_365 dolu, bayraksız). Arz ve gürültü grafikleri tüm kohort.
Yöntem (KAPSAM §6): kademe dağılımları, segment başarı oranları, lojistik regresyon (yıl sabit etkili, HC1 standart hata).
M1'de doğrulayıcı hipotez yok; bulgular betimsel ve "ilişki" olarak raporlanır (nedensellik iddiası yok).
Çıktı: analysis/sekiller/M1_*.png + aynı adlı .csv, analysis/sonuclar/M1_ozet.json
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from grafik import IKINCIL, KADEME_AD, KADEME_RAMPA, KATEGORIK, KOK, MUREKKEP, SOLUK, YUZEY, baslik, kaydet, orneklem, stil, wilson, yukle

KAYNAK = "Kaynak: Steam (GetItems, inceleme grafiği), Discovery Dynamics analizi. Başarı = ilk 365 günde alınan inceleme."
TURLER = ["Action", "Adventure", "Casual", "RPG", "Simulation", "Strategy", "Sports", "Racing"]
FIYAT_SIRA = ["f2p", "<5", "5-10", "10-20", "20-30", ">=30"]
FIYAT_AD = {
    "f2p": "Ücretsiz",
    "<5": r"<5 \$",
    "5-10": r"5–10 \$",
    "10-20": r"10–20 \$",
    "20-30": r"20–30 \$",
    ">=30": r"30 \$+",
}  # \$: matematik kipi açılmasın


def f1_kademe_yil(a: pd.DataFrame) -> dict:
    p = pd.crosstab(a.yil, a.kademe, normalize="index")[list(KADEME_AD)] * 100
    n = a.groupby("yil").size()
    fig, ax = plt.subplots(figsize=(9, 5.2))
    sol = np.zeros(len(p))
    for i, k in enumerate(KADEME_AD):
        ax.barh(p.index.astype(str), p[k], left=sol, color=KADEME_RAMPA[i], height=0.62, edgecolor=YUZEY, linewidth=1.5, label=KADEME_AD[k])
        for y, (s, v) in enumerate(zip(sol, p[k])):
            if v >= 6:
                ax.text(s + v / 2, y, f"%{v:.0f}", ha="center", va="center", fontsize=8.5, color="white" if i >= 2 else MUREKKEP)
        sol += p[k].values
    ax.set_yticks(range(len(p)), [f"{y}{'*' if y == 2025 else ''}  (n={n[y]:,})" for y in p.index])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Oyunların yüzdesi")
    ax.grid(axis="y", visible=False)
    ax.legend(ncol=5, loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=8.5, handlelength=1.2)
    t0 = (a.kademe == "T0").mean() * 100
    baslik(fig, f"Her iki oyundan biri ilk yılında 10 inceleme bile alamıyor (%{t0:.0f})",
           "Bağımsız oyunların ilk 365 gündeki inceleme sayısına göre dağılımı. Koyu mavi = daha başarılı.\n*2025: yalnız yılın ilk aylarında çıkanlar (365 gün dolmadı).")  # fmt: skip
    fig.subplots_adjust(top=0.8, bottom=0.12)
    kaydet(fig, "M1_1_kademe_yil", p.round(2).assign(n=n), KAYNAK)
    return {"T0_yuzde": round(t0, 1), "hit_yuzde": round(a.hit.astype(float).mean() * 100, 2), "n": len(a)}


def f2_arz_hit(t: pd.DataFrame, a: pd.DataFrame) -> dict:
    arz = t[t.kohort].groupby("yil").size()
    g = a.groupby("yil").agg(k=("hit", lambda v: v.astype(int).sum()), n=("hit", "size"))
    g["oran"] = g.k / g.n * 100
    alt, ust = wilson(g.k, g.n)
    g["alt"], g["ust"] = alt * 100, ust * 100
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.4))
    a1.bar(arz.index, arz.values, color=KATEGORIK[0], width=0.62)
    for x, v in arz.items():
        a1.text(x, v, f"{v / 1000:.1f}b", ha="center", va="bottom", fontsize=8, color=IKINCIL)
    a1.set_title("Steam'e çıkan oyun sayısı (bin)", fontsize=10.5)
    a1.set_yticks([])
    a1.grid(False)
    a2.plot(g.index, g.oran, color=KATEGORIK[0], marker="o", markersize=6)
    a2.fill_between(g.index, g.alt, g.ust, color=KATEGORIK[0], alpha=0.15, linewidth=0)
    for x in (g.index.min(), g.index.max()):
        a2.annotate(f"%{g.oran[x]:.1f}", (x, g.oran[x]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=MUREKKEP)
    a2.set_ylim(0, max(12, g.ust.max() * 1.2))
    a2.set_title("Hit oranı: ilk yılında 500+ inceleme alanlar (%)", fontsize=10.5)
    a2.set_ylabel("%")
    for ax in (a1, a2):
        ax.set_xticks(arz.index)
    kat = arz.max() / arz.min()
    baslik(fig, f"Steam'e çıkan oyun {kat:.1f} katına çıktı; bağımsız oyunların hit oranı %{g.oran.min():.0f}–{g.oran.max():.1f} bandında kaldı",
           "Sol: tüm kohort. Sağ: bağımsız oyunlar; gölge = %95 güven aralığı. 2025 kısmi (365 gün dolmadı).")  # fmt: skip
    fig.subplots_adjust(top=0.78, wspace=0.25)
    kaydet(fig, "M1_2_arz_ve_hit", pd.DataFrame({"cikan_oyun": arz}).join(g.round(3)), KAYNAK)
    return {"arz": arz.to_dict(), "hit_yil": g.oran.round(2).to_dict()}


def turleri_ekle(a: pd.DataFrame) -> pd.DataFrame:
    tr = pd.read_parquet(KOK / "data" / "interim" / "oyun_steam_tur.parquet")
    tr = tr[tr.tur.isin(TURLER)]
    d = pd.crosstab(tr.appid, tr.tur).clip(upper=1).reindex(columns=TURLER, fill_value=0)
    return a.merge(d, left_on="appid", right_index=True, how="left").fillna({t: 0 for t in TURLER})


def f3_tur_fiyat(a: pd.DataFrame) -> dict:
    satir = []
    for tur in TURLER:
        s = a[a[tur] == 1]
        for f in FIYAT_SIRA:
            h = s[s.fiyat_bandi == f]
            satir.append({"tur": tur, "fiyat": f, "n": len(h), "hit": h.hit.astype(float).mean() * 100 if len(h) else np.nan})
    d = pd.DataFrame(satir)
    m = d.pivot(index="tur", columns="fiyat", values="hit").reindex(index=TURLER, columns=FIYAT_SIRA)
    n = d.pivot(index="tur", columns="fiyat", values="n").reindex(index=TURLER, columns=FIYAT_SIRA)
    goster = m.where(n >= 100)
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    im = ax.imshow(goster.values, cmap="Blues", vmin=0, vmax=np.nanpercentile(goster.values, 95), aspect="auto")
    for i in range(len(TURLER)):
        for j in range(len(FIYAT_SIRA)):
            v, k = goster.iat[i, j], n.iat[i, j]
            if np.isnan(v):
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color="#f0efec"))
                ax.text(j, i, "az veri", ha="center", va="center", fontsize=7.5, color=SOLUK)
            else:
                renk = "white" if v / np.nanpercentile(goster.values, 95) > 0.55 else MUREKKEP
                ax.text(j, i, f"%{v:.1f}", ha="center", va="center", fontsize=9.5, color=renk, fontweight="bold")
                ax.text(j, i + 0.3, f"n={int(k):,}", ha="center", va="center", fontsize=6.5, color=renk)
    ax.set_xticks(range(len(FIYAT_SIRA)), [FIYAT_AD[f] for f in FIYAT_SIRA])
    ax.set_yticks(range(len(TURLER)), TURLER)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
    cb.outline.set_visible(False)
    cb.set_label("Hit oranı (%)", color=IKINCIL)
    baslik(fig, "Başarı şansı türe ve fiyata göre birkaç kat değişiyor",
           "Her hücre: o tür ve fiyat bandındaki bağımsız oyunların yüzde kaçı ilk yılında 500+ inceleme aldı. Bir oyun birden çok türde olabilir. 100'den az oyunlu hücreler gri.")  # fmt: skip
    fig.subplots_adjust(top=0.82)
    kaydet(fig, "M1_3_tur_fiyat", d.round(3), KAYNAK + " Fiyat: mevcut liste fiyatı (çıkış fiyatı değil).")
    return {"hucre": d.dropna().query("n >= 100").sort_values("hit", ascending=False).head(5).round(2).to_dict("records")}


def f4_model(a: pd.DataFrame) -> dict:
    d = a.copy()
    d["hit_i"] = d.hit.astype(int)
    d["ea"] = d.ea_ile_basladi.astype(int)
    d["deneyimli"] = (d.gelistirici_onceki_oyun >= 1).astype(int)
    d["kendi"] = d.kendi_yayini.eq(True).astype(int)
    d["log_dil"] = np.log1p(d.n_dil)
    d = d[d.fiyat_bandi.notna() & ~d.f2p].copy()  # R8: F2P'de inceleme/oyuncu oranı farklı → ayrı; fiyatı bilinmeyenler de çıkar
    d["fiyat"] = d.fiyat_bandi.astype(str)  # kategorik tip boş kategoriyi tutar → tekil matris; düz metin kullan
    f = "hit_i ~ C(fiyat, Treatment('5-10')) + ea + deneyimli + kendi + log_dil + " + " + ".join(TURLER) + " + C(yil)"
    m = smf.logit(f, data=d).fit(disp=0, cov_type="HC1")
    tablo = pd.DataFrame({"OR": np.exp(m.params), "alt": np.exp(m.conf_int()[0]), "ust": np.exp(m.conf_int()[1]), "p": m.pvalues})
    tablo = tablo[~tablo.index.str.startswith(("C(yil)", "Intercept"))]
    ad = {"ea": "Early Access ile çıkış", "deneyimli": "Geliştiricinin önceki oyunu var", "kendi": "Kendi yayını",
          "log_dil": "Dil sayısı (log, +1 birim)"} | {t: f"Tür: {t}" for t in TURLER}  # fmt: skip
    ad |= {f"C(fiyat, Treatment('5-10'))[T.{f}]": f"Fiyat: {FIYAT_AD[f]} (5–10 \\$ yerine)" for f in FIYAT_SIRA}
    tablo.index = [ad.get(i, i) for i in tablo.index]
    tablo = tablo.sort_values("OR")
    fig, ax = plt.subplots(figsize=(9, 6.4))
    y = np.arange(len(tablo))
    renk = [KATEGORIK[0] if o > 1 else KATEGORIK[1] for o in tablo.OR]
    ax.hlines(y, tablo.alt, tablo.ust, color=renk, linewidth=2)
    ax.scatter(tablo.OR, y, color=renk, s=40, zorder=3, edgecolor=YUZEY, linewidth=1.5)
    ax.axvline(1, color=SOLUK, linewidth=1)
    ax.set_xscale("log")
    ax.set_xticks([0.25, 0.5, 1, 2, 4, 8], ["×0,25", "×0,5", "×1", "×2", "×4", "×8"])
    ax.set_yticks(y, tablo.index)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Hit olma ihtimali (diğer her şey sabitken, kaç kat?)")
    ax.text(1.03, len(tablo) - 0.5, "daha olası →", color=KATEGORIK[0], fontsize=8.5, va="center")
    ax.text(0.97, len(tablo) - 0.5, "← daha az olası", color=KATEGORIK[1], fontsize=8.5, va="center", ha="right")
    baslik(fig, "Diğer her şey sabitken hangi özellikler başarıyla birlikte görülüyor?",
           f"Lojistik regresyon, çıkış yılı sabit, n={int(m.nobs):,} ücretli bağımsız oyun (F2P ayrı, R8). Nokta = tahmin, çizgi = %95 güven aralığı. İlişkidir, neden-sonuç değildir.")  # fmt: skip
    fig.subplots_adjust(top=0.86)
    tablo.index = tablo.index.str.replace("\\$", "$", regex=False)  # CSV'de kaçış karakteri görünmesin
    kaydet(fig, "M1_4_model", tablo.round(4), KAYNAK)
    return {"n": int(m.nobs), "pseudo_r2": round(m.prsquared, 4), "OR": tablo.OR.round(3).to_dict()}


def f5_gurultu(t: pd.DataFrame) -> dict:
    k = t[t.kohort]
    g = k.groupby("yil")[["seri_uretici", "yetiskin", "dil_spam"]].mean() * 100
    ad = {"seri_uretici": "Seri üretici (yılda 12+ oyun)", "yetiskin": "Yetişkin cinsel içerik", "dil_spam": "Dil spam'i (40+ ek dil)"}
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for i, c in enumerate(g.columns):
        ax.plot(g.index, g[c], color=KATEGORIK[i], marker="o", markersize=5)
        ax.annotate(
            f"{ad[c]}  %{g[c].iloc[-1]:.1f}", (g.index[-1], g[c].iloc[-1]), xytext=(8, 0), textcoords="offset points", va="center", fontsize=8.5, color=IKINCIL
        )
    ax.set_xticks(g.index)
    ax.set_xlim(g.index.min() - 0.3, g.index.max() + 2.6)
    ax.set_ylabel("Çıkan oyunların yüzdesi")
    ax.set_ylim(0, None)
    baslik(fig, f"Yetişkin içerikli oyunların payı {g.yetiskin.iloc[-1] / g.yetiskin.iloc[0]:.1f} katına çıktı; seri üretim her yıl %5–9",
           "Her yıl çıkan oyunlar içinde bayraklı grupların payı (tüm kohort). Bu oyunlar ana analizden çıkarıldı.")  # fmt: skip
    fig.subplots_adjust(top=0.8)
    kaydet(fig, "M1_5_gurultu", g.round(2), KAYNAK)
    return {"pay_son_yil": g.iloc[-1].round(2).to_dict(), "pay_ilk_yil": g.iloc[0].round(2).to_dict()}


def main() -> None:
    stil()
    t = yukle()
    a = turleri_ekle(orneklem(t))
    ozet = {"orneklem": f1_kademe_yil(a), "arz_hit": f2_arz_hit(t, a), "tur_fiyat": f3_tur_fiyat(a), "model": f4_model(a), "gurultu": f5_gurultu(t)}
    (KOK / "analysis" / "sonuclar").mkdir(parents=True, exist_ok=True)
    (KOK / "analysis" / "sonuclar" / "M1_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(ozet, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
