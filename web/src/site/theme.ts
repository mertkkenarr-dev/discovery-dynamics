/**
 * Tek tema: gece gökyüzü fotoğraf plakası. Renk değişkenleri galaksi.css'te; grafikler bunları buradan okur.
 * Kit'in çok temalı sistemi burada gereksiz (site tek kimlikle yayınlanır); charts.tsx'in beklediği arayüz korunuyor.
 */
import '@fontsource-variable/literata/opsz.css'
import '@fontsource-variable/literata/opsz-italic.css'
import '@fontsource-variable/familjen-grotesk/index.css'
import '@fontsource/ibm-plex-mono/400.css'

const SABIT = { id: 'plaka' } as const

export function useTheme(): typeof SABIT {
  return SABIT
}

export function readColors(): Record<'ground' | 'ink' | 'muted' | 'rule' | 'accent' | 's1' | 's2' | 's3' | 'font' | 'mono', string> {
  const cs = getComputedStyle(document.documentElement)
  const v = (n: string) => cs.getPropertyValue(n).trim()
  return {
    ground: v('--ground'),
    ink: v('--ink'),
    muted: v('--muted'),
    rule: v('--rule'),
    accent: v('--accent'),
    s1: v('--series-1'),
    s2: v('--series-2'),
    s3: v('--series-3'),
    font: v('--font-ui'),
    mono: v('--font-mono'),
  }
}
