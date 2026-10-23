"""Ortak grafik stili ve analiz örneklemi. Tüm modüller (M1–M8, K1–K4) buradan çizer.

Renkler dataviz referans paletinden; doğrulandı (validate_palette.js, 2026-10-24):
  ordinal mavi rampa (kademeler) → ALL PASS · kategorik ilk 4 slot → PASS, yeşil/sarı < 3:1 kontrast → doğrudan etiket + CSV zorunlu.
Kurallar: tek eksen (çift y ekseni yok), başlık sonucu düz cümleyle söyler, her grafiğin verisi aynı adla CSV olarak da kaydedilir.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

KOK = Path(__file__).resolve().parents[1]
SEKIL = KOK / "analysis" / "sekiller"
YUZEY, MUREKKEP, IKINCIL, SOLUK, IZGARA, EKSEN = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
KATEGORIK = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
KADEME_RAMPA = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]  # T0 → T4 (ordinal, doğrulandı)
SIRALI = "Blues"
KADEME_AD = {"T0": "T0 · 10'dan az", "T1": "T1 · 10–99", "T2": "T2 · 100–499", "T3": "T3 · 500–4.999", "T4": "T4 · 5.000+"}


def stil() -> None:
    plt.rcParams.update(
        {
            "font.family": ["Helvetica Neue", "Helvetica", "DejaVu Sans"],
            "font.size": 10,
            "figure.facecolor": YUZEY,
            "axes.facecolor": YUZEY,
            "axes.edgecolor": EKSEN,
            "axes.linewidth": 0.6,
            "axes.labelcolor": IKINCIL,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlecolor": MUREKKEP,
            "axes.titlelocation": "left",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": IZGARA,
            "grid.linewidth": 0.5,
            "grid.linestyle": "-",
            "xtick.color": SOLUK,
            "ytick.color": SOLUK,
            "xtick.labelcolor": IKINCIL,
            "ytick.labelcolor": IKINCIL,
            "legend.frameon": False,
            "legend.labelcolor": IKINCIL,
            "lines.linewidth": 2,
            "savefig.dpi": 200,
        }
    )


def baslik(fig: plt.Figure, ana: str, alt: str) -> None:
    """Ana başlık sonucu söyler; alt başlık örneklemi ve okuma yönergesini verir."""
    fig.text(0.01, 0.995, ana, ha="left", va="top", fontsize=14, fontweight="bold", color=MUREKKEP)
    fig.text(0.01, 0.945, alt, ha="left", va="top", fontsize=9.5, color=IKINCIL, wrap=True)


def kaydet(fig: plt.Figure, ad: str, veri: pd.DataFrame, kaynak: str) -> Path:
    SEKIL.mkdir(parents=True, exist_ok=True)
    if fig.subplotpars.bottom < 0.14:  # kaynak satırı x ekseni başlığıyla çakışmasın
        fig.subplots_adjust(bottom=0.14)
    fig.text(0.01, 0.005, kaynak, ha="left", va="bottom", fontsize=7.5, color=SOLUK)
    yol = SEKIL / f"{ad}.png"
    fig.savefig(yol, facecolor=YUZEY, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    veri.to_csv(SEKIL / f"{ad}.csv", index=True)  # tablo karşılığı (erişilebilirlik)
    return yol


def yukle() -> pd.DataFrame:
    return pd.read_parquet(KOK / "data" / "processed" / "oyun_tablosu.parquet")


def orneklem(t: pd.DataFrame) -> pd.DataFrame:
    """Ana analiz örneklemi: kohort · organik · reviews_365 dolu · bayraksız (seri üretici, yetişkin, yazılım, listelenmemiş hariç)."""
    return t[t.kohort & t.organik & t.reviews_365.notna() & ~t.seri_uretici & ~t.yetiskin & ~t.yazilim_suphe & ~t.listelenmemis].copy()


def wilson(k: pd.Series, n: pd.Series, z: float = 1.96) -> tuple[pd.Series, pd.Series]:
    p = k / n
    m = z * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5) / (1 + z**2 / n)
    c = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    return c - m, c + m
