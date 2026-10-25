/**
 * Kaydırmalı anlatı. Hangi bölümün etkin olduğunu IntersectionObserver belirler (ekranın ortasındaki şerit);
 * kaydırma olayına abone olunmaz, böylece kaydırma ana iş parçacığını meşgul etmez.
 */
import { useEffect, type ReactNode } from 'react'
import type { Bolum } from './bolumler'
import { PlotFrame } from './site/charts'
import { arayuz, hipotezMetni } from './arayuz'
import { useDil, type Dil } from './dil'
import type { Ozet } from './veri'

export function useEtkinBolum(onDegis: (id: string) => void, hazir: boolean) {
  useEffect(() => {
    if (!hazir) return
    const ob = new IntersectionObserver(
      (girdiler) => {
        for (const g of girdiler) if (g.isIntersecting) onDegis((g.target as HTMLElement).dataset.bolum ?? '')
      },
      { rootMargin: '-48% 0px -48% 0px' },
    )
    document.querySelectorAll<HTMLElement>('[data-bolum]').forEach((el) => ob.observe(el))
    return () => ob.disconnect()
  }, [onDegis, hazir])
}

/** Bölüm künyesi: ön kayıtlı hipotez mi (sonucuyla), keşifsel analiz mi. Okur bulgunun kanıt düzeyini başlıktan önce görür. */
function kunye(b: Bolum, h: Ozet['hipotez'], dil: Dil): string {
  const m = arayuz(dil)
  if (!b.hipotez) return m.kesifsel
  const v = h[b.hipotez]
  return m.onKayitli(b.hipotez, v ? hipotezMetni(dil, b.hipotez, v.konu, v.sonuc).sonuc : '?')
}

export function Anlati({ liste, etkin, hipotezler }: { liste: Bolum[]; etkin: string; hipotezler: Ozet['hipotez'] }) {
  const dil = useDil()
  const m = arayuz(dil)
  return (
    <section className="anlati" aria-label={m.bulgular}>
      {liste.map((b) => (
        <article key={b.id} id={b.id} className="adim" data-bolum={b.id} data-etkin={etkin === b.id}>
          <div className="metin">
            <p className="katalog" data-hipotez={b.hipotez ? (hipotezler[b.hipotez]?.sonuc.startsWith('desteklendi') ? 'evet' : 'hayir') : undefined}>
              {kunye(b, hipotezler, dil)}
            </p>
            <h2>{b.baslik}</h2>
            <div className="govde">{b.govde}</div>
            <p className="harita-notu">
              <span>{m.haritada}</span> {b.harita}
            </p>
            {b.grafikler?.map((gr) => (
              <figure key={gr.etiket} className="grafik">
                <figcaption>{gr.baslik}</figcaption>
                <PlotFrame build={gr.kur} label={gr.etiket} height={gr.yukseklik} />
              </figure>
            ))}
            <p className="yontem">
              <span>{m.yontemEtiket}</span> {b.yontem}
            </p>
          </div>
        </article>
      ))}
    </section>
  )
}

export function Dizin({ liste, etkin }: { liste: { id: string; kisa: string }[]; etkin: string }) {
  const m = arayuz(useDil())
  return (
    <nav className="dizin" aria-label={m.bolumler}>
      <ol>
        {liste.map((b) => (
          <li key={b.id}>
            <a href={`#${b.id}`} aria-current={etkin === b.id ? 'step' : undefined}>
              {b.kisa}
            </a>
          </li>
        ))}
      </ol>
    </nav>
  )
}

export function Anahtar(): ReactNode {
  const m = arayuz(useDil())
  return (
    <figure className="anahtar">
      <figcaption>{m.anahtarBaslik}</figcaption>
      <ul>
        {m.anahtar.map((ad, k) => (
          <li key={ad}>
            <span className={`nokta t${k}`} aria-hidden="true" />
            {ad}
          </li>
        ))}
      </ul>
      <p>{m.anahtarNot}</p>
    </figure>
  )
}
