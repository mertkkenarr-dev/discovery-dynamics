"""12: Otomatik kontroller (VERI_MIMARISI.md §5) → interim/meta_kontrol.parquet. Kritik kontrol başarısızsa çıkış kodu 1 (hat durur).

Kullanım: cd scripts && python 12_kontrol.py      (10, 10b, 11'den sonra)
Durum   : gecti | kaldi (kritik, hattı durdurur) | uyari (raporlanır, durdurmaz)
"""

from __future__ import annotations

import sys

import pandas as pd
from ortak import INTERIM, ayarlar

SONUC: list[dict] = []


def kontrol(kod: str, ad: str, deger, gecti: bool, beklenen: str, kritik: bool = True) -> None:
    durum = "gecti" if gecti else ("kaldi" if kritik else "uyari")
    SONUC.append({"kod": kod, "kontrol": ad, "deger": str(deger), "beklenen": beklenen, "durum": durum})
    print(f"[{'✔' if gecti else ('✘' if kritik else '!')}] {kod:5s} {ad:62s} {str(deger):>14s}   beklenen: {beklenen}")


def main() -> None:
    cfg = ayarlar()
    oku = lambda ad: pd.read_parquet(INTERIM / f"{ad}.parquet")
    o, s, ig = oku("oyun_steam"), oku("sonuc"), oku("oyun_igdb")
    et, dl, kt, st, oz = oku("oyun_etiket"), oku("oyun_dil"), oku("oyun_kategori"), oku("oyun_studyo"), oku("oyun_igdb_ozellik")
    k = s[s.kohort]

    print("— Anahtarlar")
    for ad, df, cols in [("oyun_steam", o, ["appid"]), ("sonuc", s, ["appid"]), ("oyun_igdb", ig, ["appid"]), ("oyun_etiket", et, ["appid", "tagid"]),
                         ("oyun_dil", dl, ["appid", "dil_anahtar"]), ("oyun_kategori", kt, ["appid", "grup", "kategori_id"])]:  # fmt: skip
        n = int(df.duplicated(cols).sum())
        kontrol("K01", f"{ad}: ({', '.join(cols)}) benzersiz", n, n == 0, "0 tekrar")
    n = int(st.duplicated(["appid", "rol", "studyo_anahtar"]).sum())
    kontrol("K01b", "oyun_studyo: (appid, rol, studyo_anahtar) benzersiz", n, n == 0, "0 tekrar")

    print("— Köprü bütünlüğü")
    for ad, df in [("sonuc", s), ("oyun_igdb", ig), ("oyun_etiket", et), ("oyun_dil", dl), ("oyun_kategori", kt), ("oyun_studyo", st)]:
        n = int((~df.appid.isin(o.appid)).sum())
        kontrol("K02", f"{ad}.appid ⊂ oyun_steam.appid", n, n == 0, "0 yetim")
    n = int((~oz.appid.isin(ig.appid)).sum())
    kontrol("K02", "oyun_igdb_ozellik.appid ⊂ oyun_igdb.appid", n, n == 0, "0 yetim")

    print("— Aralıklar")
    kontrol("K03", "fiyat_liste_usd < 0", int((o.fiyat_liste_usd < 0).sum()), (o.fiyat_liste_usd.dropna() >= 0).all(), "0")
    kontrol("K03", "F2P oyunda fiyat dolu", int((o.f2p & o.fiyat_liste_usd.notna()).sum()), not (o.f2p & o.fiyat_liste_usd.notna()).any(), "0 (F2P → NULL)")
    kontrol(
        "K03",
        "olumlu_yuzde_omur ∉ [0,100]",
        int((~o.olumlu_yuzde_omur.dropna().between(0, 100)).sum()),
        o.olumlu_yuzde_omur.dropna().between(0, 100).all(),
        "0",
    )
    kontrol(
        "K03",
        "tag_priority ∉ (0,1]",
        int((~et.tag_priority.dropna().between(0, 1, inclusive="right")).sum()),
        et.tag_priority.dropna().between(0, 1, inclusive="right").all(),
        "0",
    )
    sira = (s.reviews_30 > s.reviews_90 + 1e-6) | (s.reviews_90 > s.reviews_365 + 1e-6) | (s.reviews_365 > s.omur_hist + 1e-6)
    kontrol("K03", "r30 ≤ r90 ≤ r365 ≤ ömür boyu ihlali", int(sira.sum()), not sira.any(), "0")
    for c in ("olumlu_oran_365", "tail_share"):
        kontrol("K03", f"{c} ∉ [0,1]", int((~s[c].dropna().between(0, 1)).sum()), s[c].dropna().between(0, 1).all(), "0")
    tut = (s.kademe.isin(["T3", "T4"]) == s.hit.fillna(False).astype(bool))[s.hit.notna()]
    kontrol("K03", "kademe ↔ hit uyuşmazlığı", int((~tut).sum()), tut.all(), "0")

    print("— Tarihler")
    kontrol("K04", "ilk_cikis > çekim anı (kohortta)", int((k.ilk_cikis > k.fetched_at).sum()), not (k.ilk_cikis > k.fetched_at).any(), "0")
    bas, bit = pd.Timestamp(str(cfg["kohort"]["baslangic"])), pd.Timestamp(str(cfg["kohort"]["bitis"])) + pd.Timedelta(days=1)
    kontrol(
        "K04",
        "kohort oyunu tarih aralığı dışında",
        int((~k.ilk_cikis.between(bas, bit, inclusive="left")).sum()),
        k.ilk_cikis.between(bas, bit, inclusive="left").all(),
        "0",
    )
    ters = o.tam_surum_tarihi < o.ilk_cikis
    kontrol("K04", "tam sürüm tarihi < ilk erişim", int(ters.sum()), not ters.any(), "0")
    yeni = k.reviews_365.notna() & (k.gozlem_gun < 365)
    kontrol("K04", "365 günden kısa gözlenmiş ama reviews_365 dolu (R2)", int(yeni.sum()), not yeni.any(), "0")

    print("— Kaynaklar arası ve boyut")
    y25 = int((k.ilk_cikis.dt.year == 2025).sum())
    kontrol("K05", "R1: 2025 oyun sayısı (takipçiler 20.008–20.558)", y25, 0.95 * 20008 <= y25 <= 1.05 * 20558, "19.008–21.586")
    h = k[k.sonuc_kaynagi == "histogram"]
    oran = float(h.r12_uyumsuz.mean())
    kontrol("K05", "R12: kaynak uyumsuzluğu payı", f"%{oran * 100:.1f}", oran <= 0.05, "≤ %5")
    eksik = int(((k.inceleme_omur >= 10) & (k.sonuc_kaynagi != "histogram")).sum())
    kontrol("K06", "≥10 incelemeli kohort oyununda histogram eksik", eksik, eksik == 0, "0")
    kontrol("K06", "kohort büyüklüğü", f"{len(k):,}", 90_000 <= len(k) <= 100_000, "90–100 bin")
    kap = float(k[k.inceleme_omur >= 10].appid.isin(ig.appid).mean())
    kontrol("K06", "IGDB kapsaması (kohort, ≥10 inceleme)", f"%{kap * 100:.1f}", kap > 0.60, "> %60")
    dolu = float(k.reviews_365.notna().mean())
    kontrol("K06", "reviews_365 doluluğu (kohort)", f"%{dolu * 100:.1f}", dolu > 0.85, "> %85", kritik=False)

    pd.DataFrame(SONUC).assign(zaman=pd.Timestamp.now(tz="UTC").tz_convert(None)).to_parquet(INTERIM / "meta_kontrol.parquet", index=False)
    kalan = [r for r in SONUC if r["durum"] == "kaldi"]
    uyari = sum(r["durum"] == "uyari" for r in SONUC)
    print(f"\n{len(SONUC)} kontrol · {len(SONUC) - len(kalan) - uyari} geçti · {uyari} uyarı · {len(kalan)} kaldı")
    if kalan:
        sys.exit(1)


if __name__ == "__main__":
    main()
