/**
 * Kaydırmalı anlatı. Hangi bölümün etkin olduğunu IntersectionObserver belirler (ekranın ortasındaki şerit);
 * kaydırma olayına abone olunmaz, böylece kaydırma ana iş parçacığını meşgul etmez.
 */
import { useEffect, type ReactNode } from 'react'
import type { Bolum } from './bolumler'
import { PlotFrame } from './site/charts'
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
function kunye(b: Bolum, h: Ozet['hipotez']): string {
  if (!b.hipotez) return 'Keşifsel analiz'
  return `Ön kayıtlı hipotez ${b.hipotez}: ${h[b.hipotez]?.sonuc ?? 'bilinmiyor'}`
}

export function Anlati({ liste, etkin, hipotezler }: { liste: Bolum[]; etkin: string; hipotezler: Ozet['hipotez'] }) {
  return (
    <section className="anlati" aria-label="Bulgular">
      {liste.map((b) => (
        <article key={b.id} id={b.id} className="adim" data-bolum={b.id} data-etkin={etkin === b.id}>
          <div className="metin">
            <p className="katalog" data-hipotez={b.hipotez ? (hipotezler[b.hipotez]?.sonuc.startsWith('desteklendi') ? 'evet' : 'hayir') : undefined}>
              {kunye(b, hipotezler)}
            </p>
            <h2>{b.baslik}</h2>
            <div className="govde">{b.govde}</div>
            <p className="harita-notu">
              <span>Haritada:</span> {b.harita}
            </p>
            {b.grafikler?.map((gr) => (
              <figure key={gr.etiket} className="grafik">
                <figcaption>{gr.baslik}</figcaption>
                <PlotFrame build={gr.kur} label={gr.etiket} height={gr.yukseklik} />
              </figure>
            ))}
            <p className="yontem">
              <span>Yöntem:</span> {b.yontem}
            </p>
          </div>
        </article>
      ))}
    </section>
  )
}

export function Dizin({ liste, etkin }: { liste: { id: string; kisa: string }[]; etkin: string }) {
  return (
    <nav className="dizin" aria-label="Bölümler">
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
  const kademeler = [
    ['t0', '10’dan az'],
    ['t1', '10–99'],
    ['t2', '100–499'],
    ['t3', '500–4.999'],
    ['t4', '5.000+'],
  ] as const
  return (
    <figure className="anahtar">
      <figcaption>İlk yıldaki Steam incelemesi</figcaption>
      <ul>
        {kademeler.map(([k, ad]) => (
          <li key={k}>
            <span className={`nokta ${k}`} aria-hidden="true" />
            {ad}
          </li>
        ))}
      </ul>
      <p>Hit: ilk yılda 500 ve üstü inceleme. Büyük ve parlak yıldız, daha çok inceleme demek.</p>
    </figure>
  )
}
