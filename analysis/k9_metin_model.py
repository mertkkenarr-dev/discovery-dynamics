"""K9 (keşifsel) · 2/2 Mağaza metni modelleri: metin başarıyı tahmin ediyor mu, K4'e bilgi katıyor mu, hangi kelimeler ve üslup?

Kullanım: cd analysis && python k9_metin_model.py        (önce k9_metin_hazirla.py)
Tanımlar docs/KESIFSEL_K5_K8.md §K9: zamansal bölme (eğitim ≤ 2023, test 2024–25), TF-IDF + lojistik, gömme + lojistik,
K4 nitelikleri + katlar-dışı metin skoru (LightGBM). Karşılaştırma aynı test kümesinde, paired bootstrap %95 GA.
"""

from __future__ import annotations

import json

import lightgbm as lgb
import numpy as np
import pandas as pd
from grafik import KOK
from k4_tahmin_modeli import KESIN, PARAM, YAKLASIK, veri
from k9_grafik import ciz_kelimeler, ciz_modeller, ciz_uslup
from ortak_model import KONTROL, hazirla, katsayi, logit
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

TOHUM = 20261025
CLER = (0.03, 0.1, 0.3, 1.0, 3.0)
OZ = KESIN + [c for c in YAKLASIK if c not in ("schinese", "n_dil")]  # K4 ana model (dilsiz)
USLUP = {"uzunluk": "Metin uzunluğu (log)", "unlem": "Ünlem sıklığı", "buyuk_harf": "BÜYÜK HARF kelime payı", "sen": "'You/your' payı",
         "somut": "Somut içerik sayısı ('50 levels')", "abarti": "Abartı sıfatları (unique, epic…)"}  # fmt: skip


def tfidf() -> TfidfVectorizer:
    # Tireli kelimeler bütün kalır: varsayılan desen "co-op"u "co" + "op" diye bölüyordu (ilk çalıştırmada en güçlü terim "op" çıktı).
    return TfidfVectorizer(ngram_range=(1, 2), min_df=20, max_features=50000, sublinear_tf=True, stop_words="english",
                           token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9]*(?:-[a-zA-Z0-9]+)*\b")  # fmt: skip


def lr(C: float) -> LogisticRegression:
    return LogisticRegression(C=C, max_iter=3000, solver="liblinear")


def sec_C(Xic, yic, Xdg, ydg) -> float:
    """C'yi 2023 doğrulama yılında PR-AUC'ye göre seç (test yılı hiç görülmez)."""
    return max(CLER, key=lambda C: average_precision_score(ydg, lr(C).fit(Xic, yic).predict_proba(Xdg)[:, 1]))


def metin_modeli(tr: pd.DataFrame, te: pd.DataFrame, X_tr, X_te, ic_m: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Döner: test olasılıkları, eğitim için 5 katlı katlar-dışı olasılıklar (yığınlama), seçilen C."""
    C = sec_C(X_tr[ic_m], tr.y.values[ic_m], X_tr[~ic_m], tr.y.values[~ic_m])
    p_te = lr(C).fit(X_tr, tr.y).predict_proba(X_te)[:, 1]
    oof = np.zeros(len(tr))
    for i, j in StratifiedKFold(5, shuffle=True, random_state=TOHUM).split(X_tr, tr.y):
        oof[j] = lr(C).fit(X_tr[i], tr.y.values[i]).predict_proba(X_tr[j])[:, 1]
    return p_te, oof, C


def lgbm(tr: pd.DataFrame, te: pd.DataFrame, oz: list[str]) -> np.ndarray:
    ic, dg = tr[tr.yil <= 2022], tr[tr.yil == 2023]
    m0 = lgb.train(PARAM, lgb.Dataset(ic[oz], ic.y), 2000, valid_sets=[lgb.Dataset(dg[oz], dg.y)], callbacks=[lgb.early_stopping(100, verbose=False)])
    return lgb.train(PARAM, lgb.Dataset(tr[oz], tr.y), m0.best_iteration).predict(te[oz])


def bootstrap(y: np.ndarray, p: dict[str, np.ndarray], taban: str) -> pd.DataFrame:
    """Her model için PR-AUC %95 GA ve tabana (K4 nitelikleri) göre fark GA'sı; aynı yeniden örneklemler (paired)."""
    rng = np.random.default_rng(TOHUM)
    idx = [rng.integers(0, len(y), len(y)) for _ in range(1000)]
    sat = {}
    for ad, q in p.items():
        b = np.array([average_precision_score(y[i], q[i]) for i in idx])
        f = np.array([average_precision_score(y[i], q[i]) - average_precision_score(y[i], p[taban][i]) for i in idx])
        sat[ad] = {"pr_auc": average_precision_score(y, q), "alt": np.percentile(b, 2.5), "ust": np.percentile(b, 97.5), "roc_auc": roc_auc_score(y, q),
                   "fark": average_precision_score(y, q) - average_precision_score(y, p[taban]), "fark_alt": np.percentile(f, 2.5), "fark_ust": np.percentile(f, 97.5)}  # fmt: skip
    return pd.DataFrame(sat).T


def main() -> None:
    m = pd.read_parquet(KOK / "data" / "interim" / "k9_metin.parquet")
    g = np.load(KOK / "data" / "interim" / "k9_gomme.npz")
    assert np.array_equal(g["appid"], m.appid.values), "gömme ile metin tablosu hizasız: k9_metin_hazirla.py'yi yeniden çalıştır"
    a = veri().merge(m, on="appid").reset_index(drop=True)
    E = pd.DataFrame(g["emb"], index=g["appid"]).loc[a.appid].values
    tr_m, te_m = (a.yil <= 2023).values, (a.yil >= 2024).values
    tr, te = a[tr_m].reset_index(drop=True), a[te_m].reset_index(drop=True)
    ic_m = (tr.yil <= 2022).values
    print(f"eğitim {len(tr):,} · test {len(te):,} · test hit %{te.y.mean() * 100:.1f}")

    v = tfidf().fit(tr.metin)
    p_tf, oof_tf, C_tf = metin_modeli(tr, te, v.transform(tr.metin), v.transform(te.metin), ic_m)
    p_em, oof_em, C_em = metin_modeli(tr, te, E[tr_m], E[te_m], ic_m)
    tr = tr.assign(p_tfidf=oof_tf, p_gomme=oof_em)
    te = te.assign(p_tfidf=p_tf, p_gomme=p_em)
    p_k4 = lgbm(tr, te, OZ)
    p_k4m = lgbm(tr, te, OZ + ["p_tfidf", "p_gomme"])
    p = {"Yalnız metin (TF-IDF)": p_tf, "Yalnız metin (gömme)": p_em, "K4 nitelikleri": p_k4, "K4 + metin": p_k4m}
    sonuc = bootstrap(te.y.values, p, "K4 nitelikleri")
    print(sonuc.round(4).to_string())

    sozluk = tfidf().fit(tr.metin)
    k = lr(C_tf).fit(sozluk.transform(tr.metin), tr.y).coef_[0]
    ad = sozluk.get_feature_names_out()
    sira = np.argsort(k)
    kelime = pd.DataFrame({"terim": np.r_[ad[sira[-15:]], ad[sira[:15]]], "katsayi": np.r_[k[sira[-15:]], k[sira[:15]]]})

    d = hazirla(a.drop(columns=[c for c in ("fiyat", "ea") if c in a.columns]))
    for c in USLUP:
        d[c] = (d[c] - d[c].mean()) / d[c].std()
    us = pd.DataFrame({USLUP[c]: katsayi(logit(f"y_hit ~ {c} + {KONTROL}", d), c, us=True) for c in USLUP}).T
    tani = a.groupby("y").sizinti.mean().rename({0: "hit_degil", 1: "hit"}) * 100

    ciz_modeller(sonuc, te.y.mean() * 100, len(te))
    ciz_kelimeler(kelime)
    ciz_uslup(us)
    ozet = {"n_egitim": len(tr), "n_test": len(te), "C": {"tfidf": C_tf, "gomme": C_em}, "modeller": sonuc.round(5).to_dict(orient="index"),
            "kelimeler": kelime.round(4).to_dict(orient="records"), "uslup_or": us.round(4).to_dict(orient="index"),
            "sizinti_yuzde": tani.round(2).to_dict(), "test_hit": float(te.y.mean() * 100)}  # fmt: skip
    print(json.dumps({k: v for k, v in ozet.items() if k in ("C", "uslup_or", "sizinti_yuzde")}, ensure_ascii=False, indent=1))
    (KOK / "analysis" / "sonuclar" / "K9_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
