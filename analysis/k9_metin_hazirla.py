"""K9 (keşifsel) · 1/2 Mağaza metni hazırlığı: temizlik, sızıntı cümlelerinin atılması, üslup ölçüleri, cümle gömmeleri.

Kullanım: cd analysis && python k9_metin_hazirla.py        (gömme adımı uzun sürer; kaldığı yerden devam eder)
Tanımlar sonuçlara bakılmadan docs/KESIFSEL_K5_K8.md §K9'da sabitlendi.
Çıktı: data/interim/k9_metin.parquet (appid, metin, sizinti, üslup ölçüleri) · data/interim/k9_gomme.npz (appid, 384 boyutlu gömme)
"""

from __future__ import annotations

import html
import re

import numpy as np
import pandas as pd
from grafik import KOK, orneklem, yukle

INTERIM = KOK / "data" / "interim"
UZUN_KARAKTER = 1500
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Başarıdan sonra sayfaya eklenen içerik: bu kalıbı taşıyan cümle metinden atılır (§K9 "Sızıntı koruması").
SIZINTI = re.compile(
    r"\b(award|awards|winner|winning|nominee|nominated|sold|copies|million|players worldwide|best[- ]?sell|overwhelmingly positive|"
    r"very positive|reviews?|rating|metacritic|score of|ign|pc gamer|rock paper shotgun|polygon|kotaku|gamespot|eurogamer|destructoid|"
    r"out now|now available|update|dlc|1\.0|full release)\b",
    re.IGNORECASE,
)
ABARTI = re.compile(r"\b(unique|innovative|revolutionary|epic|amazing|ultimate|best|incredible|stunning|masterpiece|first[- ]ever|never[- ]before)\b", re.I)
SOMUT = re.compile(r"\b\d{1,4}\+?\s+(?:unique\s+|different\s+|hand[- ]crafted\s+)?[a-z]{3,}", re.I)  # "50 levels", "100+ unique weapons"


def temizle(h: str | None) -> str:
    if not h:
        return ""
    t = re.sub(r"<(br|p|li|h\d)[^>]*>", ". ", h, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def cumleler(t: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<=[.!?])\s+|\s*\.\s*\.\s*", t) if c.strip()]


def hazirla() -> pd.DataFrame:
    a = orneklem(yukle())[["appid"]]
    f = pd.read_parquet(sorted((KOK / "data" / "raw" / "fronkongames").glob("*/games.parquet"))[-1], columns=["appID", "short_description", "detailed_description"])
    f["appid"] = pd.to_numeric(f.pop("appID"), errors="coerce")  # FronkonGames'te kimlik metin
    d = a.merge(f.dropna(subset=["appid"]).astype({"appid": "int64"}).drop_duplicates("appid"), on="appid")
    ham = (d.short_description.fillna("").map(temizle) + ". " + d.detailed_description.fillna("").map(temizle).str[:UZUN_KARAKTER]).str.strip(". ")
    sat = []
    for appid, t in zip(d.appid, ham):
        cc = cumleler(t)
        kalan = [c for c in cc if not SIZINTI.search(c)]
        metin = " ".join(kalan)
        harf = re.findall(r"[^\W\d_]", metin)
        latin = sum(ch.isascii() for ch in harf) / max(len(harf), 1)
        n = max(len(metin), 1)
        kelime = re.findall(r"[A-Za-z']+", metin)
        sat.append({
            "appid": appid, "metin": metin, "latin": latin, "sizinti": len(kalan) < len(cc), "n_atilan": len(cc) - len(kalan),
            "uzunluk": np.log1p(len(metin)), "unlem": metin.count("!") / n * 1000,
            "buyuk_harf": sum(w.isupper() and len(w) > 2 for w in kelime) / max(len(kelime), 1),
            "sen": sum(w.lower() in ("you", "your", "you're", "yourself") for w in kelime) / max(len(kelime), 1),
            "somut": len(SOMUT.findall(metin)), "abarti": len(ABARTI.findall(metin)) / n * 1000,
        })  # fmt: skip
    m = pd.DataFrame(sat)
    m = m[(m.latin >= 0.8) & (m.metin.str.len() >= 40)].reset_index(drop=True)
    print(f"metin: {len(m):,} oyun (örneklem {len(a):,}; FronkonGames eşleşen {len(d):,}); sızıntı cümlesi atılan oyun %{m.sizinti.mean() * 100:.1f}")
    return m


def gom(m: pd.DataFrame) -> None:
    from sentence_transformers import SentenceTransformer

    yol = INTERIM / "k9_gomme.npz"
    if yol.exists():
        eski = np.load(yol)
        if np.array_equal(eski["appid"], m.appid.values):
            print("gömme önbellekten")
            return
    model = SentenceTransformer(MODEL)
    E = model.encode(m.metin.tolist(), batch_size=128, show_progress_bar=True, normalize_embeddings=True, convert_to_numpy=True)
    np.savez(yol, appid=m.appid.values, emb=E.astype(np.float32))


def main() -> None:
    m = hazirla()
    m.to_parquet(INTERIM / "k9_metin.parquet", index=False)
    gom(m)
    print("[ok] k9 metin + gömme")


if __name__ == "__main__":
    main()
