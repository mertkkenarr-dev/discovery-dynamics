"""14: Steam Galaksisi web verisi — 3B UMAP konumları + yıldız nitelikleri → web/public/veri/ (ikili, sıkıştırılabilir).

Kullanım: cd scripts && python 14_web_veri.py         (13_yayinla ve analiz betiklerinden sonra)
Konum   : 11c_icerik ile AYNI içerik vektörleri (ilk 10 içerik etiketi, sıra × 2018 öncesi IDF). Galaksideki uzaklık = M3'teki yenilik.
          UMAP (kosinüs, n_neighbors=30, min_dist=0.15, 3B, tohum 20261024). Kohort oyunları; <3 içerik etiketli oyunlar dışarıda.
Çıktı   : galaksi.bin  Float32 x,y,z (n×3, %98 yarıçap = 1) | Float32 log10(1+r365) | Uint8 kademe(0–4, 255 bilinmiyor) | Uint8 yıl-2018 |
                       Uint8 fiyat bandı (0 f2p,1 <5,2 5–10,3 10–20,4 20–30,5 30+,255 yok) | Uint8 bayrak (bit0 organik, bit1 çok oyunculu/co-op,
                       bit2 EA, bit3 yapay zekâ beyanı, bit4 sevilen hit, bit5 Çince, bit6 gizli hazine (K7), bit7 fırsat bölgesi (K6)) | Uint8 yenilik (0–255, 255=yok)
          adlar.json   [appid, ad] (galaksi.bin ile aynı sıra; arama için, tembel yüklenir)
          ikinci.json  M6 çiftleri: [i_ilk, i_ikinci, Δlog] (indeksler galaksi sırası)
          ozet.json    sayfa metnindeki rakamlar (analiz JSON'larından, elle yazılmaz)
"""

from __future__ import annotations

import importlib
import json
import math
import struct

import numpy as np
import pandas as pd
from ortak import INTERIM, KOK, PROCESSED, ayarlar

WEB = KOK / "web" / "public" / "veri"
FIYAT = {"f2p": 0, "<5": 1, "5-10": 2, "10-20": 3, "20-30": 4, ">=30": 5}
COK = {"Multiplayer", "Online Co-Op", "Co-op", "Local Co-Op", "Massively Multiplayer", "PvP", "Local Multiplayer"}


def main() -> None:
    import umap

    cfg = ayarlar()
    t = pd.read_parquet(PROCESSED / "oyun_tablosu.parquet")
    o = t[t.cikis.notna()].sort_values("cikis", kind="stable").reset_index(drop=True)
    X, n_et = importlib.import_module("11c_icerik").vektorler(o, cfg)
    sec = (o.kohort & (n_et >= cfg["icerik"]["min_etiket"])).values
    g, Xs = o[sec].reset_index(drop=True), X[sec]
    print(f"UMAP: {len(g):,} oyun × {Xs.shape[1]} boyut", flush=True)
    onbellek = INTERIM / "umap3d.npz"  # pahalı adım: oyun kimlikleri aynıysa yeniden hesaplanmaz
    if onbellek.exists() and np.array_equal(np.load(onbellek)["appid"], g.appid.values):
        emb = np.load(onbellek)["emb"]
        print("UMAP önbellekten", flush=True)
    else:
        emb = umap.UMAP(n_components=3, n_neighbors=30, min_dist=0.15, metric="cosine", random_state=20261024, low_memory=True, verbose=True).fit_transform(Xs)
        np.savez(onbellek, appid=g.appid.values, emb=emb)
    # Sağlam ölçek: ortanca merkez, %98'lik yarıçap = 1. En uzak birkaç küme ölçeği belirlerse çekirdek ekranda nokta kadar kalıyordu
    # (ortanca yarıçap 0,21). Uç kümeler 1'in dışına taşabilir; sahne bunu kaldırır.
    emb = emb - np.median(emb, axis=0)
    emb = emb / np.quantile(np.linalg.norm(emb, axis=1), 0.98)

    e = pd.read_parquet(INTERIM / "oyun_etiket.parquet", columns=["appid", "ad", "sira"])
    cok = set(e[e.ad.isin(COK) & (e.sira <= 10)].appid)
    oz = pd.read_parquet(INTERIM / "oyun_igdb_ozellik.parquet")
    ai = set(oz[(oz.alan == "anahtar") & oz.ad.str.contains(r"\bai[- ]generat", case=False, regex=True, na=False)].appid)
    kad = g.kademe.astype(str).map({"T0": 0, "T1": 1, "T2": 2, "T3": 3, "T4": 4}).fillna(255).astype(np.uint8)  # kategorik → metin (255 eklenemiyordu)
    # bit6 gizli hazine: K7 ile aynı tanım (analiz örneklemi + fiyatı bilinen; 10 ≤ r365 < 100, beğeni Wilson ≥ 0,80).
    ornek = g.kohort & g.organik & g.reviews_365.notna() & ~(g.seri_uretici | g.yetiskin | g.yazilim_suphe | g.listelenmemis) & g.fiyat_bandi.notna()
    gizli = ornek & g.reviews_365.between(10, 100, inclusive="left") & (g.begeni_wilson >= 0.80)
    # bit7 fırsat bölgesi: K6'nın fırsat işaretlediği içerik bölgelerinin üyeleri.
    k6 = json.loads((KOK / "analysis" / "sonuclar" / "K6_ozet.json").read_text(encoding="utf-8"))
    bolge = pd.read_parquet(INTERIM / "k6_bolge.parquet").set_index("appid").bolge
    firsat_b = [b["bolge"] for b in k6["bolgeler"] if b["firsat"]]
    firsat = g.appid.map(bolge).isin(firsat_b)
    bitler = [g.organik, g.appid.isin(cok), g.ea_ile_basladi, g.appid.isin(ai), g.basari_sinifi == "sevilen_hit", g.schinese, gizli, firsat]
    bay = sum(b.astype(int).values * (1 << i) for i, b in enumerate(bitler)).astype(np.uint8)  # pandas serisi << desteklemiyor
    nov = g.novelty_k10.clip(0, 0.6).div(0.6).mul(254).round().fillna(255).astype(np.uint8)
    WEB.mkdir(parents=True, exist_ok=True)
    with open(WEB / "galaksi.bin", "wb") as f:
        f.write(struct.pack("<I", len(g)))
        f.write(emb.astype(np.float32).tobytes())
        f.write(np.log10(1 + g.reviews_365.fillna(g.inceleme_omur).clip(lower=0)).astype(np.float32).values.tobytes())
        for a in (kad, (g.yil - 2018).clip(0, 7).astype(np.uint8), g.fiyat_bandi.map(FIYAT).fillna(255).astype(np.uint8), bay, nov):
            f.write(np.asarray(a, dtype=np.uint8).tobytes())
    (WEB / "adlar.json").write_text(json.dumps([[int(a), str(n)] for a, n in zip(g.appid, g.ad)], ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    idx = {int(a): i for i, a in enumerate(g.appid)}
    so = pd.read_parquet(INTERIM / "studyo_oyun.parquet")
    so = so[so.sira <= 2]
    say = so.groupby(["studyo_anahtar", "sira"]).appid.transform("size")
    p = so[say == 1].pivot(index="studyo_anahtar", columns="sira", values="appid").dropna().astype(int)
    p = p[p[1].isin(idx) & p[2].isin(idx)]
    y = g.set_index("appid").reviews_365
    cift = [[idx[a], idx[b], round(float(np.log1p(y[b]) - np.log1p(y[a])), 2)] for a, b in zip(p[1], p[2]) if pd.notna(y[a]) and pd.notna(y[b])]
    (WEB / "ikinci.json").write_text(json.dumps(cift, separators=(",", ":")), encoding="utf-8")
    # allow_nan=False: tarayıcının JSON.parse'ı NaN kabul etmez; NaN'lar null'a çevrilir, kaçan olursa yazım burada patlar.
    oz = ozet(len(g))
    oz["k6"]["etiketler"] = [{"ad": b["ad"], "merkez": np.median(emb[(g.appid.map(bolge) == b["bolge"]).values], axis=0).round(4).tolist()}
                             for b in k6["bolgeler"] if b["firsat"]]  # fmt: skip
    oz["k5"]["dalgalar"] = dalgalar(idx)
    (WEB / "ozet.json").write_text(json.dumps(nan_temizle(oz), ensure_ascii=False, indent=1, allow_nan=False), encoding="utf-8")
    print(f"[ok] galaksi {len(g):,} yıldız · ikinci oyun çifti {len(cift):,} → {WEB.relative_to(KOK)}")


def nan_temizle(v: object) -> object:
    if isinstance(v, float) and not math.isfinite(v):
        return None
    if isinstance(v, dict):
        return {k: nan_temizle(x) for k, x in v.items()}
    if isinstance(v, list | tuple):
        return [nan_temizle(x) for x in v]
    return v


def dalgalar(idx: dict[int, int], n: int = 3) -> list[dict]:
    """K5'in en kalabalık n akımı: öncüler (ilk öncü adı akımın adı) ve takipçiler, galaksi sırasındaki indeksleriyle."""
    d = pd.read_parquet(INTERIM / "k5_dalga.parquet")
    k5 = json.loads((KOK / "analysis" / "sonuclar" / "K5_ozet.json").read_text(encoding="utf-8"))["en_buyuk_dalgalar"]
    sat = []
    for gr in range(n):
        x = d[d.grup == gr]
        oncu = [idx[a] for a in x[x.rol == "oncu"].appid if a in idx]
        sat.append({"ad": k5[gr]["ilk_oncu"], "yil": k5[gr]["yil"], "oncu": oncu, "takipci": [idx[a] for a in x[x.rol == "takipci"].appid if a in idx],
                    "orneklem": k5[gr]["orneklem"], "hit": k5[gr]["hit"], "diger": k5[gr]["diger_oncular"][:3]})  # fmt: skip
    return sat


def ozet(n_yildiz: int) -> dict:
    """Sayfa metnindeki her rakam buradan gelir (analiz sonuç dosyaları); metinde elle rakam yazılmaz."""
    S = KOK / "analysis" / "sonuclar"
    j = {m: json.loads((S / f"{m}_ozet.json").read_text(encoding="utf-8")) for m in ("M1", "M1b", "M2", "M2b", "M3", "M4", "M6", "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9")}
    arz = pd.read_csv(KOK / "analysis" / "sekiller" / "M1_2_arz_ve_hit.csv", index_col=0)
    kum = {v["ad"]: v for v in j["M4"]["yorunge"]["kumeler"].values()}
    k30 = j["K3"]["ilk30"]
    return {
        "yildiz": n_yildiz,
        "orneklem": j["M1"]["orneklem"]["n"],
        "gorunmez_yuzde": j["M1"]["orneklem"]["T0_yuzde"],
        "hit_yuzde": j["M1"]["orneklem"]["hit_yuzde"],
        "arz": {str(k): int(v) for k, v in arz.cikan_oyun.items()},
        "hit_yil": {str(k): round(float(v), 2) for k, v in arz.oran.items()},
        "hit_sayisi": {str(k): int(v) for k, v in arz.k.items()},
        "fiyat_hit": {k: round(v["hit_oran"], 1) for k, v in j["K1"]["noktalar"].items()},
        "yenilik": {"b2_p": j["M3"]["H1"]["p_b2"], "egim_alt_t": j["M3"]["H1"]["egimler"]["alt"]["t"], "egim_ust_t": j["M3"]["H1"]["egimler"]["ust"]["t"]},
        "etiket_en_olumlu": j["M2"]["etiket"]["en_olumlu"],
        "motivasyon": j["M2"]["motivasyon"],
        "cince": {
            "ana": round(j["M2"]["H6"]["yuzde_tablo"]["tahmin"]["Ana model (tüm bağımsız oyunlar)"], 0),
            "temkinli": round(j["M2"]["H6"]["yuzde_tablo"]["tahmin"]["Çıkışa en yakın dil durumu (2025)"], 0),
            "ekleme_T0": j["M2b"]["ekleme_kademe"]["ekleyen"]["T0"],
            "ekleme_T4": j["M2b"]["ekleme_kademe"]["ekleyen"]["T4"],
        },  # fmt: skip
        "yorunge": {ad: {"pay": round(v["pay"], 1), "hit": round(v["hit"] * 100, 1), "ikinci_yil": round(v["ikinci_yil"], 1)} for ad, v in kum.items()},
        "ea_kuyruk": {"or": j["M4"]["H4"]["OR"]["tahmin"], "ortanca": j["M4"]["H4"]["ham_ortanca"]},
        "ikinci_oyun": {
            "n": j["M6"]["H5"]["n_cift"],
            "iyilesen": j["M6"]["H5"]["iyilesen_pay"],
            "temiz_yuzde": j["M6"]["duyarlilik"]["sadece_tam_seri"]["fd_yuzde"],
            "T0_kalan": j["M6"]["gecis"]["T0"]["T0"],
        },  # fmt: skip
        "ilk_ay": {
            "rho": j["K3"]["spearman_30"],
            "hit": {k: round(v["hit_oran"], 1) for k, v in k30.items()},
            "carpan": {k: v["carpan"] for k, v in k30.items()},
        },
        "yapay_zeka": {"gorunmez": j["K2"]["tablo"], "or": j["K2"]["OR"]["gorunmez"]["tahmin"], "pay_yil": j["K2"]["pay_yil"]},
        "model": {"pr_auc": j["K4"]["C_dilsiz"]["pr_auc"], "taban": j["K4"]["C_dilsiz"]["taban"], "ust_dilim": j["K4"]["lift"]["10"]},
        "siniflar": j["M1b"]["siniflar"]["sinif_yuzde"],
        "k5": {
            "dalga": j["K5"]["dalga"],
            "oncul": j["K5"]["oncul"]["tum"],
            "takipci": j["K5"]["esik"]["0.7"]["oncu"]["tum"],
            "takipci_dilim": j["K5"]["esik"]["0.7"]["oncu"]["dilim"],
            "plasebo": j["K5"]["esik"]["0.7"]["plasebo"]["tum"],
        },
        "k6": {"k": j["K6"]["k"], "bolgeler": [{k: b[k] for k in ("ad", "n", "hit_oran", "ob", "alt", "ust", "arz_22_25", "goreli_buyume", "firsat")}
                            for b in j["K6"]["bolgeler"] if b["alt"] > 1 and not b["cinsel_tema"]]},
        "k7": {"n_gizli": j["K7"]["n_gizli"], "n_gorunur": j["K7"]["n_gorunur"], "cok_begenilen": j["K7"]["cok_begenilen_toplam"],
               "farklar": {k: j["K7"]["smd"][k] for k in ("Tür: Simulation", "Early Access ile çıkış", "Playtest", "Stüdyonun önceki oyunu var",
                                                          "Çıkıştan önce demo", "Kendi yayını")}},
        "hipotez": json.loads((S / "hipotez_ozeti.json").read_text(encoding="utf-8")),
        "k9": {k: j["K9"][k] for k in ("modeller", "uslup_or", "n_test")},
        "k8": {"tahmin": j["K8"]["tahmin"], "secilim": j["K8"]["secilim"], "gozlem": j["K8"]["gozlem"], "oyun": j["K8"]["oyun"]},
    }  # fmt: skip


if __name__ == "__main__":
    main()
