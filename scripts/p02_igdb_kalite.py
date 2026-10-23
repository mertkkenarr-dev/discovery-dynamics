"""IGDB eşleştirme kalitesi: kapsama, çoklu eşleşme, tür uyumu, tarih uyumu, alan doluluğu (hipotez testi YOK).

Kullanım: cd scripts && python p02_igdb_kalite.py
Kohort tanımı 03_histogram.py ile aynı: ilk Steam erişimi (ortak.ilk_steam_erisimi) config aralığında, GetItems type=0.
"""

from __future__ import annotations

import importlib

import pandas as pd
from ortak import RAW, ayarlar, ilk_steam_erisimi, jsonl_gz_oku

igdb = importlib.import_module("05_igdb")
satirlar = igdb.satirlar


def steam_tablosu() -> pd.DataFrame:
    cfg = ayarlar()
    bas, bit = pd.Timestamp(str(cfg["kohort"]["baslangic"])), pd.Timestamp(str(cfg["kohort"]["bitis"]))
    rows = []
    for x in jsonl_gz_oku(RAW / "steam_getitems" / "items.jsonl.gz"):
        if x.get("success") != 1 or x.get("type") != 0:
            continue
        t = ilk_steam_erisimi(x)
        rc = ((x.get("reviews") or {}).get("summary_filtered") or {}).get("review_count") or 0
        rows.append({"appid": x["_istenen_appid"], "steam_tarih": pd.to_datetime(t, unit="s") if t else pd.NaT, "inceleme": rc})
    s = pd.DataFrame(rows)
    s["kohort"] = (s.steam_tarih >= bas) & (s.steam_tarih < bit + pd.Timedelta(days=1))
    return s


def main() -> None:
    s = steam_tablosu()
    eg = pd.DataFrame(satirlar("external_games"))
    eg = eg[eg.uid.str.fullmatch(r"\d+", na=False)].assign(appid=lambda d: d.uid.astype(int))[["appid", "game"]].drop_duplicates()
    eg = eg[eg.appid.isin(s.appid)]
    g = pd.DataFrame(satirlar("games")).rename(columns={"id": "game"})
    ttb = {r["game_id"] for r in satirlar("game_time_to_beats")}

    print("== 1. Çoklu eşleşme ==")
    app_basina = eg.groupby("appid").game.nunique()
    oyun_basina = eg.groupby("game").appid.nunique()
    print(f"appID → >1 IGDB oyunu : {(app_basina > 1).sum():,} appID")
    print(f"IGDB oyunu → >1 appID : {(oyun_basina > 1).sum():,} IGDB oyunu ({oyun_basina[oyun_basina > 1].sum():,} appID)")

    tur_ad = {0: "ana oyun", 1: "dlc", 2: "genişleme", 3: "paket", 4: "bağımsız genişleme", 5: "mod", 6: "bölüm", 7: "sezon",
              8: "remake", 9: "remaster", 10: "genişletilmiş", 11: "port", 12: "fork", 13: "paket(pack)", 14: "güncelleme"}  # fmt: skip
    m = eg.merge(g[["game", "game_type", "first_release_date"]], on="game", how="left").merge(s, on="appid")
    print("\n== 2. IGDB oyun türü (eşleşen Steam oyunları) ==")
    print(m.game_type.map(tur_ad).fillna("IGDB kaydı dönmedi").value_counts().to_string())

    print("\n== 3. Çıkış tarihi uyumu (IGDB ilk çıkış − Steam çıkış, gün) ==")
    fark = (pd.to_datetime(m.first_release_date, unit="s") - m.steam_tarih).dt.days.dropna()
    for etiket, kosul in [
        ("|fark| ≤ 30", fark.abs() <= 30),
        ("|fark| ≤ 365", fark.abs() <= 365),
        ("IGDB > 1 yıl önce", fark < -365),
        ("IGDB > 1 yıl sonra", fark > 365),
    ]:
        print(f"{etiket:20s}: %{kosul.mean() * 100:5.1f}")

    print("\n== 4. Kapsama (Steam oyunlarının yüzde kaçı IGDB'de) ==")
    eslesen = set(eg.appid)
    for ad, alt in [
        ("tüm oyunlar", s),
        ("kohort", s[s.kohort]),
        ("kohort, inceleme ≥ 10 (hedef > %60)", s[s.kohort & (s.inceleme >= 10)]),
        ("kohort, inceleme < 10", s[s.kohort & (s.inceleme < 10)]),
    ]:
        print(f"{ad:38s}: {alt.appid.isin(eslesen).mean() * 100:5.1f}%  (n={len(alt):,})")
    k = s[s.kohort].assign(yil=lambda d: d.steam_tarih.dt.year)
    print("yıllara göre (kohort):", {int(y): round(d.appid.isin(eslesen).mean() * 100, 1) for y, d in k.groupby("yil")})

    print("\n== 5. Alan doluluğu (kohortta eşleşen ana oyunlar) ==")
    km = m[m.kohort & (m.game_type == 0)].drop_duplicates("game")
    gk = g.set_index("game").loc[km.game]
    for alan in ["genres", "themes", "game_modes", "player_perspectives", "keywords", "game_engines", "involved_companies"]:
        print(f"{alan:22s}: %{gk[alan].notna().mean() * 100:5.1f}")
    print(f"{'time_to_beat':22s}: %{km.game.isin(ttb).mean() * 100:5.1f}")
    ic = pd.DataFrame(satirlar("involved_companies"))
    co = pd.DataFrame(satirlar("companies")).rename(columns={"id": "company"})
    gel = ic[ic.developer & ic.game.isin(km.game)].merge(co[["company", "country"]], on="company", how="left")
    print(f"{'geliştirici ülkesi':22s}: %{km.game.isin(gel.loc[gel.country.notna(), 'game']).mean() * 100:5.1f}")


if __name__ == "__main__":
    main()
