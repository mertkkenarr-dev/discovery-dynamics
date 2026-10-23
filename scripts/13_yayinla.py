"""13: Yayın — processed/discovery.duckdb, processed/oyun_tablosu.parquet, processed/discovery_veri.xlsx, docs/VERI_RAPORU.md.

Kullanım: cd scripts && python 13_yayinla.py        (12_kontrol.py geçtikten sonra)
Kurallar: meta_kontrol'de 'kaldi' varsa durur. oyun_tablosu'nun her sütunu sozluk.SOZLUK'ta olmalı (iki yönlü; eksik/fazla → durur).
Çakışan sütunlar açıkça seçilir: gozlem_gun sonuc'tan (T14 düzeltilmiş tarih), kohort / ilk_cikis_kaynagi oznitelik'ten (2018 öncesi
oyunlar için doldurulmuş hali).
"""

from __future__ import annotations

import sys

import duckdb
import pandas as pd
from ortak import INTERIM, KOK, PROCESSED, ayarlar, simdi_utc
from sozluk import SOZLUK

TABLOLAR = ["oyun_etiket", "oyun_dil", "oyun_kategori", "oyun_studyo", "oyun_steam_tur", "oyun_igdb", "oyun_igdb_ozellik", "inceleme_seri",
            "studyo_oyun", "kaldirilmis", "meta_karar", "meta_kontrol"]  # fmt: skip
REFERANS = ["steam_etkinlik", "buyuk_yayinci", "etiket_taksonomi"]
EKSIKLIK_TESTI = ["igdb_tur", "n_tema", "n_bakis", "n_motor", "novelty_k10", "kombo_12ay", "fiyat_liste_usd", "yayinci_onceki_oyun"]


def oyun_tablosu() -> pd.DataFrame:
    oku = lambda ad: pd.read_parquet(INTERIM / f"{ad}.parquet")
    o = oku("oznitelik").drop(columns=["gozlem_gun", "inceleme_omur"])  # gozlem_gun: düzeltilmemiş tarihe göre → sonuc'tan alınır
    s = oku("sonuc").drop(columns=["ilk_cikis", "kohort", "ilk_cikis_kaynagi"])  # cikis, kohort, kaynak oznitelik'te (aynı kaynak, doldurulmuş)
    t = o.merge(s, on="appid", how="left", validate="1:1").merge(oku("icerik"), on="appid", how="left", validate="1:1")
    eksik, fazla = sorted(set(t.columns) - set(SOZLUK)), sorted(set(SOZLUK) - set(t.columns))
    if eksik or fazla:
        sys.exit(f"Sözlük uyuşmuyor. Sözlükte olmayan sütun: {eksik} · tabloda olmayan sözlük girdisi: {fazla}")
    return t[list(SOZLUK)]


def excel_icin(df: pd.DataFrame) -> pd.DataFrame:
    return df.astype(object).where(df.notna(), None)


def rapor(t: pd.DataFrame, karar: pd.DataFrame, kontrol: pd.DataFrame) -> str:
    cfg, k = ayarlar(), t[t.kohort]
    org = k[k.organik]
    sat = [f"# Discovery Dynamics: Veri Raporu\n\n*Otomatik üretildi: `13_yayinla.py` · {simdi_utc()} · Elle düzenlemeyin.*\n"]
    gecti = int((kontrol.durum == "gecti").sum())
    sat.append(f"## Kontroller\n\n{gecti} / {len(kontrol)} kontrol geçti. Ayrıntı: `meta_kontrol` tablosu.\n")
    huni = [("Tüm oyunlar (type = 0, tarihli)", len(t)), (f"Kohort ({cfg['kohort']['baslangic']} – {cfg['kohort']['bitis']})", len(k)),
            ("Organik örneklem", len(org)), ("Organik, reviews_365 dolu", int(org.reviews_365.notna().sum())),
            ("Organik, reviews_365 dolu, bayraksız (seri üretici, yetişkin, yazılım, listelenmemiş hariç)",
             int((org.reviews_365.notna() & ~org.seri_uretici & ~org.yetiskin & ~org.yazilim_suphe & ~org.listelenmemis).sum()))]  # fmt: skip
    sat.append("## Örneklem hunisi\n\n| Aşama | Oyun |\n|---|---|\n" + "\n".join(f"| {a} | {n:,} |" for a, n in huni) + "\n")
    y = k.groupby("yil").agg(oyun=("appid", "size"), organik=("organik", "sum"), r365_dolu=("reviews_365", lambda v: v.notna().mean()))
    sat.append("## Yıllara göre\n\n| Yıl | Oyun | Organik | reviews_365 dolu |\n|---|---|---|---|\n"
               + "\n".join(f"| {i} | {int(r.oyun):,} | {int(r.organik):,} | %{r.r365_dolu * 100:.1f} |" for i, r in y.iterrows()) + "\n")  # fmt: skip
    ks = k[k.kademe.notna()].copy()
    ks["fiyat_liste_usd"] = ks.fiyat_liste_usd.mask(ks.f2p, 0)  # F2P'de fiyat tanım gereği NULL; gerçek eksiklik yalnız ücretli + fiyat yok
    ek = pd.DataFrame({c: ks.groupby("kademe", observed=True)[c].apply(lambda v: v.isna().mean() * 100) for c in EKSIKLIK_TESTI}).T.round(1)
    sat.append("## T13: Eksikliğin başarı kademesine göre dağılımı (kohort, % NULL)\n\nEksiklik kademeye göre değişiyorsa o alana dayanan "
               "bulgular yanlı olabilir; analizde eksiklik göstergesi ya da duyarlılık testi gerekir. Bu bir veri kalitesi testidir. "
               "`fiyat_liste_usd` satırı yalnız ücretli oyunlarda fiyatın bilinmemesini sayar (F2P'de fiyat tanım gereği NULL).\n\n"
               "| Sütun | " + " | ".join(ek.columns) + " |\n|---|" + "---|" * len(ek.columns) + "\n"
               + "\n".join(f"| `{c}` | " + " | ".join(f"{v:.1f}" for v in r) + " |" for c, r in ek.iterrows()) + "\n")  # fmt: skip
    sat.append("## Temizlik kararları\n\n| Kod | Betik | Sorun | Etkilenen | Karar |\n|---|---|---|---|---|\n"
               + "\n".join(f"| {r.kod} | {r.betik} | {r.sorun} | {int(r.etkilenen):,} / {int(r.toplam):,} | {r.karar} |" for r in karar.itertuples()) + "\n")  # fmt: skip
    sat.append("## Sütun sözlüğü (`oyun_tablosu`)\n\n`ÖNCE` = çıkış anında bilinebilir, tahmin modelinde kullanılabilir (R6). "
               "`ÖNCE*` = mevcut durum, çıkış anındaki değer olmayabilir.\n\n| Sütun | Tür | Kohortta dolu | Açıklama |\n|---|---|---|---|\n"
               + "\n".join(f"| `{c}` | {tur} | %{k[c].notna().mean() * 100:.1f} | {ac.replace('|', '/')} |" for c, (tur, ac) in SOZLUK.items()) + "\n")  # fmt: skip
    return "\n".join(sat)


def main() -> None:
    kontrol = pd.read_parquet(INTERIM / "meta_kontrol.parquet")
    if (kontrol.durum == "kaldi").any():
        sys.exit("meta_kontrol'de başarısız kontrol var; önce 12_kontrol.py'yi geçir.")
    t = oyun_tablosu()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    t.to_parquet(PROCESSED / "oyun_tablosu.parquet", index=False)
    sozluk = pd.DataFrame([(c, tur, ac) for c, (tur, ac) in SOZLUK.items()], columns=["sutun", "tur", "aciklama"])

    yol = PROCESSED / "discovery.duckdb"
    yol.unlink(missing_ok=True)  # her çalıştırmada baştan kurulur (yeniden üretilebilirlik)
    with duckdb.connect(str(yol)) as db:
        db.register("t_oyun", t)
        db.execute("CREATE TABLE oyun_tablosu AS SELECT * FROM t_oyun")
        db.register("t_sozluk", sozluk)
        db.execute("CREATE TABLE meta_sozluk AS SELECT * FROM t_sozluk")
        for ad in TABLOLAR:
            db.execute(f"CREATE TABLE {ad} AS SELECT * FROM read_parquet('{INTERIM / ad}.parquet')")
        for ad in REFERANS:
            db.execute(f"CREATE TABLE ref_{ad} AS SELECT * FROM read_csv_auto('{KOK / 'data' / 'referans' / ad}.csv', header=true)")
        satir = {r[0]: db.execute(f'SELECT COUNT(*) FROM "{r[0]}"').fetchone()[0] for r in db.execute("SHOW TABLES").fetchall()}
    print("DuckDB tabloları:", satir)

    karar = pd.read_parquet(INTERIM / "meta_karar.parquet")
    with pd.ExcelWriter(PROCESSED / "discovery_veri.xlsx", engine="openpyxl") as x:
        excel_icin(t[t.kohort]).to_excel(x, sheet_name="oyun_tablosu_kohort", index=False)
        sozluk.to_excel(x, sheet_name="sozluk", index=False)
        karar.to_excel(x, sheet_name="kararlar", index=False)
        kontrol.to_excel(x, sheet_name="kontroller", index=False)
        pd.read_csv(KOK / "data" / "referans" / "etiket_taksonomi.csv").to_excel(x, sheet_name="etiket_taksonomi", index=False)
    (KOK / "docs" / "VERI_RAPORU.md").write_text(rapor(t, karar, kontrol), encoding="utf-8")
    print(f"[ok] oyun_tablosu {len(t):,} × {t.shape[1]} · Excel (kohort {int(t.kohort.sum()):,} satır) · docs/VERI_RAPORU.md")


if __name__ == "__main__":
    main()
