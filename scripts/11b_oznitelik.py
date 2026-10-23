"""11b: Türetilmiş nitelikler — organik örneklem, stüdyo deneyimi, demo / Next Fest, fiyat bandı, zamanlama, IGDB bayrakları.

Kullanım: cd scripts && python 11b_oznitelik.py      (10, 10b, 11'den sonra)
Çıktı   : interim/oznitelik.parquet    oyun başına (tüm type=0 oyunlar; kohort bayrağı sonuc.parquet'ten)
          interim/studyo_oyun.parquet  geliştirici × oyun, stüdyo içi sıra (M6 için)
Sızıntı kuralı (R6): her nitelik çıkış anında bilinebilir olmalı. "Önceki" sayımlar yalnız kesin olarak daha önce çıkan
oyunları sayar (aynı gün sayılmaz). Tarih: T14 ile düzeltilmiş ilk_cikis. novelty/saturation: 11c.
Hipotez testi YOK.
"""

from __future__ import annotations

import importlib
import re

import numpy as np
import pandas as pd
from ortak import INTERIM, KOK, KararKaydi, ayarlar

ad_normalize = importlib.import_module("10_temizle_steam").ad_normalize
GUN = pd.Timedelta(days=1)
FIYAT_SINIR = [0, 5, 10, 20, 30, np.inf]
FIYAT_ETIKET = ["<5", "5-10", "10-20", "20-30", ">=30"]


def onceki_sayi(st: pd.DataFrame) -> pd.Series:
    """Her (stüdyo, oyun) satırı için stüdyonun kesin olarak daha önce çıkmış oyun sayısı (eşit tarih sayılmaz)."""
    return st.groupby("studyo_anahtar").t.rank(method="min").sub(1).astype(int)


def main() -> None:
    cfg, K = ayarlar(), KararKaydi("11b_oznitelik")
    o = pd.read_parquet(INTERIM / "oyun_steam.parquet")
    s = pd.read_parquet(INTERIM / "sonuc.parquet", columns=["appid", "ilk_cikis", "ilk_cikis_kaynagi", "kohort"])
    o = o.drop(columns="kohort").merge(s, on="appid", how="left", suffixes=("_steam", ""))
    o["t"] = o.ilk_cikis.fillna(o.ilk_cikis_steam).astype("datetime64[ns]")  # 2018 öncesi oyunlar sonuc'ta yok; Steam tarihi kullanılır
    o["kohort"] = o.kohort.fillna(False).astype(bool)
    o["tarih_duzeltildi"] = o.ilk_cikis_kaynagi.eq("ilk_inceleme")
    o = o[o.t.notna()].copy()
    k = o.kohort
    st = pd.read_parquet(INTERIM / "oyun_studyo.parquet").merge(o[["appid", "t"]], on="appid")

    # --- Organik örneklem (KAPSAM §3.2) -------------------------------------------------------
    yay, gel = st[st.rol == "yayinci"].copy(), st[st.rol == "gelistirici"].copy()
    yay["onceki"] = onceki_sayi(yay)
    gel["onceki"] = onceki_sayi(gel)
    o["yayinci_onceki_oyun"] = o.appid.map(yay.groupby("appid").onceki.max())  # yayıncı yoksa NULL
    yset, gset = yay.groupby("appid").studyo_anahtar.agg(set), gel.groupby("appid").studyo_anahtar.agg(set)
    o["kendi_yayini"] = [(yset[a] <= gset[a]) if a in yset.index and a in gset.index else None for a in o.appid]
    # Sahiplik tarihe bağlı: etiket yalnız geçerlilik aralığında büyük sayılır (ör. Bungie 2022-07 öncesi bağımsız)
    by = pd.read_csv(KOK / "data" / "referans" / "buyuk_yayinci.csv", parse_dates=["gecerli_baslangic", "gecerli_bitis"])
    kurallar = [(re.compile(r.desen), r.gecerli_baslangic, r.gecerli_bitis) for r in by.itertuples()]

    def buyuk_mu(adlar: str, t: pd.Timestamp) -> bool:
        for n in map(ad_normalize, adlar.split(" | ")):
            for d, b, e in kurallar:
                if d.match(n) and (pd.isna(b) or t >= b) and (pd.isna(e) or t < e):
                    return True
        return False

    yay["buyuk"] = [buyuk_mu(a, t) for a, t in zip(yay.ad, yay.t)]
    o["buyuk_yayinci"] = o.appid.map(yay.groupby("appid").buyuk.any()).fillna(False).astype(bool)
    esik = cfg["organik"]["yayinci_max_oyun"]
    for e in [esik, *cfg["organik"]["duyarlilik_max_oyun"]]:
        kucuk = o.yayinci_onceki_oyun.le(e)
        o[f"organik_{e}"] = (o.kendi_yayini.eq(True) | kucuk) & ~o.buyuk_yayinci
    o["organik"] = o[f"organik_{esik}"]
    K.ekle(
        "N01",
        "Yayıncı bilgisi yok (kendi_yayini ve yayinci_onceki_oyun NULL)",
        int(o.yayinci_onceki_oyun.isna()[k].sum()),
        int(k.sum()),
        "organik = False (koşul kanıtlanamıyor)",
        "Bilinmeyen yayıncı organik sayılmaz",
    )
    K.ekle(
        "N02",
        f"Organik örneklem: (kendi yayını veya yayıncının önceki oyunu ≤ {esik}) ve büyük yayıncı değil",
        int(o.organik[k].sum()),
        int(k.sum()),
        f"Duyarlılık: ≤3 → {int(o.organik_3[k].sum()):,}, ≤10 → {int(o.organik_10[k].sum()):,}",
        "KAPSAM §3.2; hedef: kohortun en az %70'i",
    )
    K.ekle(
        "N03",
        "Kendi yayını ama büyük yayıncı (CD Projekt, Larian, Valve…)",
        int((o.kendi_yayini.eq(True) & o.buyuk_yayinci)[k].sum()),
        int(k.sum()),
        "Organik dışı",
        "Kendi yayını kuralı büyük şirketleri organik saymasın",
    )

    # --- Stüdyo deneyimi (§5.2) -----------------------------------------------------------------
    ilk_oyun = gel.groupby("studyo_anahtar").t.transform("min")
    gel["yas_gun"] = (gel.t - ilk_oyun).dt.days
    o["gelistirici_onceki_oyun"] = o.appid.map(gel.groupby("appid").onceki.max())
    o["studyo_yasi_gun"] = o.appid.map(gel.groupby("appid").yas_gun.max())
    o["n_gelistirici"] = o.appid.map(gel.groupby("appid").size()).fillna(0).astype(int)
    gel.assign(sira=gel.onceki + 1)[["studyo_anahtar", "appid", "t", "sira", "ad"]].to_parquet(INTERIM / "studyo_oyun.parquet", index=False)

    # --- Ticari (§5.3) --------------------------------------------------------------------------
    o["fiyat_bandi"] = pd.cut(o.fiyat_liste_usd, FIYAT_SINIR, right=False, labels=FIYAT_ETIKET).astype("string")
    o.loc[o.f2p, "fiyat_bandi"] = "f2p"
    o["demo_cikis_oncesi"] = o.demo_ilk_tarih < o.t
    o["demo_gun_once"] = (o.t - o.demo_ilk_tarih).dt.days.where(o.demo_cikis_oncesi)
    K.ekle(
        "N04",
        "Demo çıkıştan önce yayında (mağazada görünen demolar)",
        int(o.demo_cikis_oncesi[k].sum()),
        int(k.sum()),
        "demo_cikis_oncesi; çıkıştan sonra eklenen demo sayılmaz",
        "H2 çıkış öncesi demoyu ölçer; kaldırılmış demolar görünmez (R13): etki küçük tahmin edilir",
    )
    o["ea_sure_gun"] = (o.tam_surum_tarihi - o.t).dt.days.where(o.ea_ile_basladi & ~o.ea_su_an)

    # --- Next Fest dolaylı göstergesi -----------------------------------------------------------
    ev = pd.read_csv(KOK / "data" / "referans" / "steam_etkinlik.csv", parse_dates=["baslangic", "bitis"])
    fest = ev[ev.tur.isin(["next_fest", "demo_festivali"])]
    aday = pd.Series(False, index=o.index)
    for f in fest.itertuples():
        aday |= (o.demo_ilk_tarih <= f.bitis) & (o.t > f.baslangic)  # demo festivalde mevcut ve oyun henüz çıkmamış
    firsat = o.t > fest.baslangic.min()
    o["nextfest_aday"] = aday.where(firsat)  # ilk festivalden önce çıkan oyunda fırsat yok → NULL
    K.ekle(
        "N05",
        "Next Fest dolaylı göstergesi: çıkış öncesi demo bir festival penceresinde mevcut",
        int(o.nextfest_aday.eq(True)[k].sum()),
        int(firsat[k].sum()),
        "nextfest_aday; Aralık 2019 öncesi çıkanlarda NULL",
        "Resmi katılım listesi yok (H3); demo festival sırasında kaldırılmışsa yanlış pozitif",
    )

    # --- Zamanlama (§5.4) -----------------------------------------------------------------------
    o["yil"], o["ay"], o["haftanin_gunu"] = o.t.dt.year, o.t.dt.month, o.t.dt.day_of_week
    hafta = o.t.dt.to_period("W")
    o["ayni_hafta_cikan"] = hafta.map(hafta.value_counts()) - 1
    o["ayni_hafta_buyuk_yayinci"] = hafta.map(o[o.buyuk_yayinci].groupby(hafta[o.buyuk_yayinci]).size()).fillna(0).sub(o.buyuk_yayinci.astype(int)).gt(0)
    ind = ev[ev.tur == "buyuk_indirim"].sort_values("baslangic")
    bas, bit = ind.baslangic.values.astype("datetime64[ns]"), ind.bitis.values.astype("datetime64[ns]")
    i = np.searchsorted(bas, o.t.values, side="right")
    sonraki = pd.Series(np.where(i < len(bas), bas[np.minimum(i, len(bas) - 1)], np.datetime64("NaT", "ns")), index=o.index)
    onceki_bit = pd.Series(np.where(i > 0, bit[np.maximum(i - 1, 0)], np.datetime64("NaT", "ns")), index=o.index)
    o["gun_sonraki_indirim"] = (sonraki - o.t).dt.days
    o["indirim_icinde"] = (o.t < onceki_bit + GUN) & (i > 0)
    o["indirim_tek_kaynak"] = False
    tek = ind[ind.dogrulama == "tek_kaynak"]
    for r in tek.itertuples():
        o.loc[(o.t >= r.baslangic - pd.Timedelta(days=60)) & (o.t <= r.bitis + GUN), "indirim_tek_kaynak"] = True

    # --- IGDB ----------------------------------------------------------------------------------
    ig = pd.read_parquet(INTERIM / "oyun_igdb.parquet")[["appid", "igdb_tur", "igdb_ilk_cikis", "n_tema", "n_bakis", "n_motor"]]
    o = o.merge(ig, on="appid", how="left")
    o["steam_oncesi_cikis"] = (o.igdb_ilk_cikis < o.t - 365 * GUN).where(o.igdb_ilk_cikis.notna())
    K.ekle(
        "N06",
        "IGDB ilk çıkışı Steam'den 1 yıldan fazla önce (başka platformda önceden çıkmış)",
        int(o.steam_oncesi_cikis.eq(True)[o.kohort].sum()),
        int(o.kohort.sum()),
        "steam_oncesi_cikis; IGDB yoksa NULL",
        "Oyun Steam'e tanınmış olarak gelebilir; organik keşif anlamı farklı",
    )

    cikti = o.drop(columns=["ilk_cikis", "ilk_cikis_steam", "fetched_at"]).rename(columns={"t": "cikis"})
    cikti.to_parquet(INTERIM / "oznitelik.parquet", index=False)
    K.kaydet()
    print(f"\n[ok] oznitelik: {len(cikti):,} oyun (kohort {int(cikti.kohort.sum()):,}) · {cikti.shape[1]} sütun")


if __name__ == "__main__":
    main()
