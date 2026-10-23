"""10: Steam meta verisi (GetItems) temizliği → data/interim/ tabloları. Her karar KararKaydi ile ekrana ve meta_karar'a yazılır.

Kullanım: cd scripts && python 10_temizle_steam.py
Çıktı   : interim/oyun_steam.parquet   oyun başına bir satır (type=0, success=1)
          interim/oyun_etiket.parquet  appid, tagid, ad, agirlik, sira, tag_priority
          interim/oyun_dil.parquet     appid, dil_anahtar (elanguage; ek dillerde 100+eadditionallanguage), ek_dil, arayuz, tam_ses, altyazi
          interim/oyun_kategori.parquet appid, grup, kategori_id
          interim/oyun_studyo.parquet  appid, rol (gelistirici|yayinci), studyo_anahtar, ad, kimlik_var
          interim/kaldirilmis.parquet  GetItems'ta success != 1 olan evren kayıtları (T09)
Hipotez testi YOK: bu betik başarı metriğine bakmaz.
"""

from __future__ import annotations

import json
import re
import unicodedata

import pandas as pd
from ortak import INTERIM, RAW, KararKaydi, ayarlar, ilk_steam_erisimi, jsonl_gz_oku

TUR_AD = {0: "oyun", 1: "demo", 4: "mod/genişleme", 6: "yazılım", 12: "playtest", 14: "dlc/paket"}
YASAL_EK = re.compile(
    r"[\s,.]+(inc|llc|l\.l\.c|ltd|limited|co|corp|corporation|gmbh|s\.?r\.?o|s\.?a|s\.?l|s\.?r\.?l|sas|oy|ab|bv|b\.v|pty|kft|ug|k\.?k|sp\.? z o\.?o)\.?$"
)


def ad_normalize(ad: str) -> str:
    """'Studio X, Inc.' / 'STUDIO X LLC' / 'Studio X' → 'studio x'. Sadece yasal ekler atılır; 'Games', 'Studio' gibi kelimeler kalır."""
    s = unicodedata.normalize("NFKC", ad or "").lower().strip()
    for _ in range(2):  # 'X Co., Ltd.' gibi çift ekler
        s = YASAL_EK.sub("", s)
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).strip()


def oku() -> tuple[list[dict], list[dict], list[dict]]:
    oyun, diger, basarisiz = [], [], []
    for x in jsonl_gz_oku(RAW / "steam_getitems" / "items.jsonl.gz"):
        if x.get("success") != 1:
            basarisiz.append(x)
        elif x.get("type") == 0:
            oyun.append(x)
        else:
            diger.append(x)
    return oyun, diger, basarisiz


def main() -> None:
    cfg, K = ayarlar(), KararKaydi("10_temizle_steam")
    oyun, diger, basarisiz = oku()
    print(f"Ham GetItems: {len(oyun) + len(diger) + len(basarisiz):,} kayıt → oyun {len(oyun):,} · oyun dışı {len(diger):,} · başarısız {len(basarisiz):,}\n")
    evren = set(pd.read_parquet(INTERIM / "evren.parquet").appid.astype(int))
    diger_evren = [x for x in diger if x["_istenen_appid"] in evren]  # demo çekimi (02 --liste demolar) evren dışından gelir

    # T09: kaldırılmış / erişilemeyen
    pd.DataFrame([{"appid": x["_istenen_appid"], "success": x.get("success")} for x in basarisiz]).to_parquet(INTERIM / "kaldirilmis.parquet", index=False)
    K.ekle(
        "T09",
        "GetItems'ta başarısız (kaldırılmış / erişilemiyor) evren kaydı",
        len(basarisiz),
        len(evren),
        "`kaldirilmis.parquet`'e ayrılır, analizden çıkar",
        "İçerik ve sonuç verisi yok; R10 için yıl yıl sayı raporlanır",
    )

    # T01: oyun dışı kayıtlar → ana oyuna bağlanan nitelikler
    tur = pd.Series([TUR_AD.get(x.get("type"), f"tip{x.get('type')}") for x in diger_evren]).value_counts().to_dict()
    K.ekle(
        "T01",
        f"Evrende oyun dışı kayıtlar: {tur}",
        len(diger_evren),
        len(evren),
        "Sadece type=0 kalır; demo ve playtest'ler parent_appid ile ana oyuna nitelik olarak bağlanır",
        "R1: playtest/yazılım 'görünmez oyun' oranını şişirir (pilot: %8,8)",
    )
    demo_tarih: dict[int, int] = {}
    playtest_parent: set[int] = set()
    for x in diger:
        parent = (x.get("related_items") or {}).get("parent_appid")
        if not parent:
            continue
        if x.get("type") == 1 and (t := (x.get("release") or {}).get("steam_release_date")):
            demo_tarih[parent] = min(t, demo_tarih.get(parent, t))
        elif x.get("type") == 12:
            playtest_parent.add(parent)

    # Ana tablo
    yetiskin_id = set(cfg["temizlik"]["yetiskin_icerik_id"])
    rows, etiket, dil, kategori, studyo = [], [], [], [], []
    for x in oyun:
        a, r = x["_istenen_appid"], x.get("release") or {}
        b, bi = x.get("best_purchase_option") or {}, x.get("basic_info") or {}
        ilk, tam = ilk_steam_erisimi(x), r.get("steam_release_date")
        liste = b.get("original_price_in_cents") or b.get("final_price_in_cents")
        langs = x.get("supported_languages") or []
        rows.append(
            {
                "appid": a,
                "ad": x.get("name"),
                "ilk_cikis": pd.to_datetime(ilk, unit="s") if ilk else pd.NaT,
                "tam_surum_tarihi": pd.to_datetime(tam, unit="s") if tam and tam >= 631152000 else pd.NaT,
                "ea_ile_basladi": bool(x.get("is_early_access"))
                or bool(r.get("original_steam_release_date") and tam and r["original_steam_release_date"] < tam),
                "ea_su_an": bool(x.get("is_early_access")),
                "f2p": bool(x.get("is_free")),
                "fiyat_liste_usd": None if x.get("is_free") else (int(liste) / 100 if liste else None),
                "fiyat_kaynagi": "f2p" if x.get("is_free") else ("mevcut_liste" if liste else "yok"),
                "yetiskin": bool(yetiskin_id & set(x.get("content_descriptorids") or [])),
                "listelenmemis": bool(x.get("unlisted")),
                "demo_var_su_an": bool((x.get("related_items") or {}).get("demo_appid")),
                "demo_ilk_tarih": pd.to_datetime(demo_tarih[a], unit="s") if a in demo_tarih else pd.NaT,
                "playtest_var": a in playtest_parent,
                "schinese": any(l.get("elanguage") == 6 and l.get("supported") for l in langs),
                "win": bool((x.get("platforms") or {}).get("windows")),
                "mac": bool((x.get("platforms") or {}).get("mac")),
                "linux": bool((x.get("platforms") or {}).get("steamos_linux")),
                "deck_uyum": (x.get("platforms") or {}).get("steam_deck_compat_category"),
                "inceleme_omur": ((x.get("reviews") or {}).get("summary_filtered") or {}).get("review_count") or 0,
                "olumlu_yuzde_omur": ((x.get("reviews") or {}).get("summary_filtered") or {}).get("percent_positive"),
                "seri_steam": "|".join(f.get("name", "") for f in bi.get("franchises") or []) or None,
                "fetched_at": pd.to_datetime(x["_fetched_at"]).tz_convert(None),  # tüm zamanlar etiketsiz UTC
            }
        )
        tags = sorted(x.get("tags") or [], key=lambda t: -t.get("weight", 0))
        mx = tags[0]["weight"] if tags and tags[0].get("weight") else None
        etiket += [
            {"appid": a, "tagid": t["tagid"], "agirlik": t.get("weight", 0), "sira": i + 1, "tag_priority": t.get("weight", 0) / mx if mx else None}
            for i, t in enumerate(tags)
        ]
        dil += [
            {
                "appid": a,
                # elanguage = -1 ise dil eadditionallanguage alanındadır (ayrı numaralandırma; oradaki 6 Çince DEĞİL)
                "dil_anahtar": l["elanguage"] if l["elanguage"] >= 0 else 100 + l.get("eadditionallanguage", -1),
                "ek_dil": l["elanguage"] < 0,
                "arayuz": bool(l.get("supported")),
                "tam_ses": bool(l.get("full_audio")),
                "altyazi": bool(l.get("subtitles")),
            }
            for l in langs
        ]
        for grup, ids in (x.get("categories") or {}).items():
            kategori += [{"appid": a, "grup": grup.removesuffix("_categoryids"), "kategori_id": i} for i in ids]
        for rol, alan in (("gelistirici", "developers"), ("yayinci", "publishers")):
            studyo += [{"appid": a, "rol": rol, "ad": s.get("name", ""), "kimlik": s.get("creator_clan_account_id")} for s in bi.get(alan) or []]
    o = pd.DataFrame(rows)
    n = len(o)

    # T02: tarih
    gecersiz = o.ilk_cikis.isna()
    K.ekle(
        "T02",
        "Geçerli ilk Steam erişim tarihi yok (boş ya da 1990 öncesi yer tutucu)",
        int(gecersiz.sum()),
        n,
        "ilk_cikis = NULL; kohort dışında kalır",
        "Sıfır noktası olmadan reviews_365 hesaplanamaz",
    )
    gelecek = o.ilk_cikis > o.fetched_at
    K.ekle("T02b", "İlk erişim tarihi çekim anından sonra (henüz çıkmamış)", int(gelecek.sum()), n, "Kohort dışında kalır", "Gözlem yok")
    bas, bit = pd.Timestamp(str(cfg["kohort"]["baslangic"])), pd.Timestamp(str(cfg["kohort"]["bitis"])) + pd.Timedelta(days=1)
    o["kohort"] = (o.ilk_cikis >= bas) & (o.ilk_cikis < bit) & ~gelecek
    o["gozlem_gun"] = (o.fetched_at - o.ilk_cikis).dt.days
    ea_fark = o.ea_ile_basladi & ~o.ea_su_an
    K.ekle(
        "T02c",
        "EA'dan çıkmış oyunda steam_release_date tam sürüm tarihi (EA başlangıcı değil)",
        int(ea_fark.sum()),
        n,
        "ilk_cikis = min(steam_release_date, original_steam_release_date)",
        "İncelemeler EA ile başlar; bkz. PILOT_RAPORU 'Çıkış tarihi tanımı'",
    )

    # T03: fiyat
    k = o[o.kohort]
    K.ekle(
        "T03",
        "Ücretli oyunda satın alma seçeneği yok (fiyat bilinmiyor)",
        int((k.fiyat_kaynagi == "yok").sum()),
        len(k),
        "fiyat_liste_usd = NULL (0 değil)",
        "T13: veri yok ≠ ücretsiz",
    )
    K.ekle(
        "T03b",
        "Çekim anında indirimde olan oyun",
        int(sum(1 for x in oyun if (x.get("best_purchase_option") or {}).get("original_price_in_cents"))),
        len(oyun),
        "İndirimsiz liste fiyatı kullanılır; fiyat 'mevcut liste fiyatı'dır, çıkış fiyatı değil",
        "İndirim geçici; çıkış fiyatı geçmişi açık konu (ANALIZ_PLANI §7)",
    )
    K.ekle(
        "T06",
        "Yetişkin cinsel içerik uyarısı (Steam içerik kimliği 3 veya 4)",
        int(k.yetiskin.sum()),
        len(k),
        "Çıkarılmaz; yetiskin bayrağı. Ana analiz hariç, duyarlılıkta dahil",
        "Keşif ve inceleme dinamikleri farklı",
    )
    K.ekle(
        "T15",
        "Listelenmemiş (mağaza aramasında görünmeyen) oyun",
        int(k.listelenmemis.sum()),
        len(k),
        "Çıkarılmaz; listelenmemis bayrağı",
        "Organik keşif imkânı kısıtlı; duyarlılık analizinde hariç tutulur",
    )

    # T04: stüdyo anahtarı
    s = pd.DataFrame(studyo)
    s["ad_norm"] = s.ad.map(ad_normalize)
    s["kimlik_var"] = s.kimlik.notna()
    ad_kimlik = s[s.kimlik_var].groupby("ad_norm").kimlik.agg(lambda v: set(v))
    tek = {ad: next(iter(ids)) for ad, ids in ad_kimlik.items() if len(ids) == 1}
    birlesen = ~s.kimlik_var & s.ad_norm.isin(tek)
    s.loc[birlesen, "kimlik"] = s.loc[birlesen, "ad_norm"].map(tek)
    s["studyo_anahtar"] = s.kimlik.map(lambda v: f"id:{int(v)}", na_action="ignore").fillna("ad:" + s.ad_norm)
    bos = s.ad_norm.eq("") & s.kimlik.isna()
    ham_ad = s.loc[~s.kimlik_var, "ad"].nunique()
    norm_ad = s.loc[~s.kimlik_var, "ad_norm"].nunique()
    K.ekle(
        "T04",
        f"Kimliksiz stüdyo adı yazım farkları (ham {ham_ad:,} → normalize {norm_ad:,} farklı ad)",
        ham_ad - norm_ad,
        ham_ad,
        "Küçük harf, Unicode NFKC, noktalama ve yasal ek (Inc, LLC, Ltd…) temizliği",
        "'Studio X, Inc.' ile 'STUDIO X' aynı stüdyo",
    )
    K.ekle(
        "T04b",
        "Kimliksiz satır, normalize adı tek bir sabit kimlikle eşleşiyor",
        int(birlesen.sum()),
        int((~s.kimlik_var).sum()),
        "O kimliğe bağlanır",
        "Aynı stüdyo bazı oyunlarda kimlikli, bazılarında kimliksiz görünüyor",
    )
    K.ekle("T04c", "Stüdyo adı boş", int(bos.sum()), len(s), "Satır atılır (stüdyo bilinmiyor)", "Boş ad tüm bilinmeyenleri tek sahte stüdyoda toplardı")
    s = s[~bos]
    cift = s.duplicated(["appid", "rol", "studyo_anahtar"])
    K.ekle(
        "T04d",
        "Aynı oyunda aynı stüdyo aynı rolde birden fazla satır (ör. LucasArts + Lucasfilm, Aspyr (Mac) + Aspyr (Linux))",
        int(cift.sum()),
        len(s),
        "Tek satıra indirilir; farklı adlar ' | ' ile birleşir",
        "Stüdyo başına oyun sayısı aynı oyunu iki kez saymasın",
    )
    s = s.groupby(["appid", "rol", "studyo_anahtar"], as_index=False).agg(ad=("ad", lambda v: " | ".join(dict.fromkeys(v))), kimlik_var=("kimlik_var", "max"))
    s[["appid", "rol", "studyo_anahtar", "ad", "kimlik_var"]].to_parquet(INTERIM / "oyun_studyo.parquet", index=False)

    # T05: seri üretici (bir takvim yılında > N oyun)
    N = cfg["temizlik"]["seri_uretici_yillik"]
    g = s[s.rol == "gelistirici"].merge(o[["appid", "ilk_cikis"]], on="appid").dropna(subset=["ilk_cikis"])
    yillik = g.assign(yil=g.ilk_cikis.dt.year).groupby(["studyo_anahtar", "yil"]).appid.nunique()
    zirve = yillik.groupby(level=0).max()
    print("\n      Geliştirici başına en yoğun yıldaki oyun sayısı (dağılım):", zirve.quantile([0.5, 0.9, 0.99, 0.999]).to_dict(), "max", int(zirve.max()))
    print(
        "      Eşik adayları → seri üretici geliştirici / kohort oyunu:",
        {e: (int((zirve > e).sum()), int(o.kohort[o.appid.isin(g[g.studyo_anahtar.isin(zirve[zirve > e].index)].appid)].sum())) for e in (4, 6, 8, 12, 20)},
    )
    seri = set(zirve[zirve > N].index)
    o["seri_uretici"] = o.appid.isin(g[g.studyo_anahtar.isin(seri)].appid)
    K.ekle(
        "T05",
        f"Seri üretici: bir yılda > {N} oyun çıkaran geliştiricinin oyunu ({len(seri):,} geliştirici)",
        int(o.seri_uretici[o.kohort].sum()),
        int(o.kohort.sum()),
        "Çıkarılmaz; seri_uretici bayrağı. Analiz dahil/hariç iki kez",
        "R7: binlerce sıfır organik oranları çarpıtır",
    )

    tl = {t["tagid"]: t["name"] for t in json.loads((RAW / "steam_getitems" / "taglist.json").read_text())["response"]["tags"]}
    e = pd.DataFrame(etiket).assign(ad=lambda d: d.tagid.map(tl))
    K.ekle(
        "T13",
        "Hiç etiketi olmayan oyun",
        int((~o.appid.isin(e.appid)).sum()),
        n,
        "n_etiket = 0 (veri var, etiket yok); etiket köprüsünde satırı olmaz",
        "NULL ile 0 ayrımı",
    )
    o["n_etiket"] = o.appid.map(e.groupby("appid").size()).fillna(0).astype(int)

    d = pd.DataFrame(dil)
    tekrar = d.duplicated(["appid", "dil_anahtar"])
    K.ekle("T16", "Dil listesinde aynı dil birden fazla kez", int(tekrar.sum()), len(d), "İlk kayıt tutulur", "Köprü anahtarı (appid, dil) benzersiz olmalı")
    d = d[~tekrar]
    destek = d[d.arayuz]
    o["n_dil"] = o.appid.map(destek[~destek.ek_dil].groupby("appid").size()).fillna(0).astype(int)
    o["n_ek_dil"] = o.appid.map(destek[destek.ek_dil].groupby("appid").size()).fillna(0).astype(int)
    esik = cfg["temizlik"]["dil_spam_ek_dil"]
    o["dil_spam"] = o.n_ek_dil >= esik
    K.ekle(
        "T17",
        f"Dil spam'i: ≥ {esik} ek dil iddiası (72 ek dilin tamamı: {int((o.n_ek_dil >= 72).sum()):,} oyun)",
        int(o.dil_spam[o.kohort].sum()),
        int(o.kohort.sum()),
        "dil_spam bayrağı; n_dil yalnız Steam ana dillerini sayar, ek diller n_ek_dil'de",
        "Ek dil sayısı dağılımı iki tepeli: gerçek yerelleştirme 0–20, sonra boşluk, 72'de yığılma; tüm kutuları işaretleme davranışı",
    )

    o.to_parquet(INTERIM / "oyun_steam.parquet", index=False)
    e.to_parquet(INTERIM / "oyun_etiket.parquet", index=False)
    d.to_parquet(INTERIM / "oyun_dil.parquet", index=False)
    pd.DataFrame(kategori).to_parquet(INTERIM / "oyun_kategori.parquet", index=False)
    K.kaydet()
    print(
        f"\n[ok] oyun_steam: {n:,} satır (kohort {int(o.kohort.sum()):,}) · etiket {len(e):,} · dil {len(dil):,} · kategori {len(kategori):,} · stüdyo {len(s):,}"
    )


if __name__ == "__main__":
    main()
