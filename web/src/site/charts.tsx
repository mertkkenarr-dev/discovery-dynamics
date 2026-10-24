/**
 * Observable Plot sarmalayıcısı. Renk ve yazı tipi çalışan temadan okunur; tema değişince grafik yeniden çizilir.
 * Kural: grafiğin kendisi sonucu söylemeli (doğrudan etiket, sıfır çizgisi, dışarıda kalan değer notu).
 * Hover ikinci katmandır: kimse görmeyecek diye bütün bilgi statik notlarda.
 */
import * as Plot from '@observablehq/plot'
import { useEffect, useRef, useState } from 'react'
import { readColors, useTheme } from './theme'

export type Colors = ReturnType<typeof readColors>

export function PlotFrame({ build, label, height = 340 }: { build: (o: { width: number; colors: Colors }) => (SVGSVGElement | HTMLElement); label: string; height?: number }) {
  const host = useRef<HTMLDivElement>(null)
  const theme = useTheme()
  const [width, setWidth] = useState(0)

  useEffect(() => {
    const el = host.current
    if (!el) return
    const ro = new ResizeObserver(([e]) => setWidth(Math.floor(e?.contentRect.width ?? 0)))
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  useEffect(() => {
    const el = host.current
    if (!el || width < 10) return
    const chart = build({ width, colors: readColors() })
    el.replaceChildren(chart)
    return () => chart.remove()
  }, [build, width, theme.id])

  return <div ref={host} role="img" aria-label={label} style={{ minHeight: height }} />
}

/** Ortak Plot ayarları: şeffaf zemin, tema yazı tipi, tablo rakamları, hafif ızgara. */
export function baseOptions(width: number, c: Colors, height = 340) {
  return {
    width,
    height,
    marginLeft: 44,
    marginRight: 14,
    marginTop: 30,
    marginBottom: 46,
    style: { background: 'transparent', color: c.ink, fontFamily: c.font, fontSize: '13px' },
  } as const
}

/** Metin etiketine zemin renginde halo: çizgilerin üstünde okunur kalır. */
export const halo = (c: Colors) => ({ stroke: c.ground, strokeWidth: 4, paintOrder: 'stroke' }) as const

/** Eksenler: ok işareti yok, etiket ekseni ezmeden altta. */
export const axis = { labelArrow: 'none', labelAnchor: 'center', labelOffset: 40 } as const

export { Plot }
