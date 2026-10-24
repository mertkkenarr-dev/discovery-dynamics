"""Ön kayıtlı hipotezlerin durumu ve Holm düzeltmesi (H1–H7 ailesi). Modül JSON çıktılarından okur, kendi hesap yapmaz.

Kullanım: python analysis/hipotez_ozeti.py   (M2, M3, M4, M6 çalıştıktan sonra)
Kurallar (HIPOTEZLER): α = 0,05; H1–H7 Holm ailesi; H8 ayrı. Hipotezler yönlü → Holm'a öngörülen yöndeki TEK YÖNLÜ p girer
(ters yönde anlamlı bir sonuç desteklemez; ör. H7). H2/H3 Steam API anahtarı, H8 ek veri bekliyor → aile tamamlanınca yeniden çalıştır;
ek test düzeltilmiş p'leri yalnız büyütebilir.
"""

from __future__ import annotations

import json

from grafik import KOK
from ortak_model import holm

S = KOK / "analysis" / "sonuclar"


def tek_yonlu(p_iki: float, tahmin_dogru_yonde: bool) -> float:
    return p_iki / 2 if tahmin_dogru_yonde else 1 - p_iki / 2


def main() -> None:
    m2, m3, m4, m6 = (json.loads((S / f"{m}_ozet.json").read_text(encoding="utf-8")) for m in ("M2", "M3", "M4", "M6"))
    h6, h7, h4 = m2["H6"]["ols_log"], m2["H7"]["kombo_OR"], m4["H4"]["OR"]
    satir = {
        "H1": ("Yenilik ters U (M3)", m3["H1"]["p_LM"], m3["H1"]["karar"], "β₂ anlamsız; eğim iki uçta negatif (ilişki azalan)"),
        "H4": ("Early Access → uzun kuyruk (M4)", tek_yonlu(h4["p"], h4["tahmin"] > 1), m4.get("H4_karar", "desteklendi" if h4["tahmin"] > 1 and h4["p"] < 0.05 else "desteklenmedi"),
               f"OR {h4['tahmin']:.2f} ({h4['alt']:.2f}–{h4['ust']:.2f}); PSM +{m4['H4']['psm']['ATT'] * 100:.1f} puan"),
        "H5": ("İkinci oyun daha başarılı (M6)", m6["H5"]["wilcoxon_p"], m6["H5"]["karar"], f"FD {m6['H5']['fd_yuzde']:+.0f}%; en temiz ölçümde {m6['duyarlilik']['sadece_tam_seri']['fd_yuzde']:+.0f}%"),
        "H6": ("Çince desteği (M2)", tek_yonlu(h6["p"], h6["tahmin"] > 0), "desteklendi" if h6["tahmin"] > 0 and h6["p"] < 0.05 else "desteklenmedi",
               "+%57–75; ters nedensellik payı var (M2b)"),
        "H7": ("Doygunluk (M2)", tek_yonlu(h7["p"], h7["tahmin"] < 1), "desteklendi" if h7["tahmin"] < 1 and h7["p"] < 0.05 else "desteklenmedi",
               f"OR {h7['tahmin']:.2f}: ters yönde (aynı tür içinde kalabalık dezavantaj değil)"),
    }  # fmt: skip
    duz = holm({k: v[1] for k, v in satir.items()})
    tablo = ["| Hipotez | Konu | Tek yönlü p | Holm p (geçici, 5 test) | Sonuç | Not |", "|---|---|---|---|---|---|"]
    for k, (konu, p, karar, notu) in satir.items():
        son = karar if (karar != "desteklendi" or duz[k] < 0.05) else "desteklenmedi (Holm)"
        tablo.append(f"| {k} | {konu} | {p:.2g} | {duz[k]:.2g} | **{son}** | {notu} |")
    tablo += ["| H2 | Demo etkisi (M5) | — | — | bekliyor | Steam API anahtarı (kaldırılmış demolar, R13) |",
              "| H3 | Next Fest etkisi (M5) | — | — | bekliyor | Steam API anahtarı; dolaylı gösterge duyarlılığı ~%53 |",
              "| H8 | Mikro/makro içerik üreticisi (M8, ayrı aile) | — | — | test edilemiyor (şimdilik) | Steam tam inceleme geçmişini kapattı; seçenekler HIPOTEZLER'de |"]  # fmt: skip
    md = "\n".join(tablo)
    (S / "hipotez_ozeti.md").write_text(md + "\n", encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
