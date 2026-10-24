/**
 * Kalite kademeleri. Tek ayar (low | medium | high) hem çözünürlüğü hem efekt yığınını yönetir.
 * PerformanceMonitor kare hızı düşerse kademeyi kendisi indirir (mobil / zayıf GPU).
 */
import { PerformanceMonitor } from '@react-three/drei'
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'

export type Tier = 'low' | 'medium' | 'high'

export interface QualitySettings {
  /** Canvas dpr aralığı. Üst sınır 2: dpr 3 = 1x'in 9 katı piksel. */
  dpr: [number, number]
  ao: false | { quality: 'performance' | 'low' | 'medium' | 'high'; halfRes: boolean }
  bloom: boolean
  smaa: boolean
  grain: boolean
  shadowMap: number
}

const SETTINGS: Record<Tier, QualitySettings> = {
  low: { dpr: [1, 1], ao: false, bloom: false, smaa: false, grain: false, shadowMap: 512 },
  medium: { dpr: [1, 1.5], ao: { quality: 'performance', halfRes: true }, bloom: true, smaa: true, grain: false, shadowMap: 1024 },
  high: { dpr: [1, 2], ao: { quality: 'medium', halfRes: false }, bloom: true, smaa: true, grain: true, shadowMap: 2048 },
}

const ORDER: Tier[] = ['low', 'medium', 'high']

interface QualityApi {
  tier: Tier
  settings: QualitySettings
  setTier: (t: Tier) => void
}

const Ctx = createContext<QualityApi | null>(null)

/** Başlangıç kademesi: ?q=low|medium|high ile zorlanabilir, yoksa dokunmatik cihazda medium. */
function initialTier(): Tier {
  const q = new URLSearchParams(window.location.search).get('q')
  if (q === 'low' || q === 'medium' || q === 'high') return q
  return window.matchMedia('(pointer: coarse)').matches ? 'medium' : 'high'
}

/** Canvas'ın DIŞINDA kullan: dpr'ı Canvas'a verebilmek için. */
export function QualityProvider({ children }: { children: ReactNode }) {
  const [tier, setTier] = useState<Tier>(initialTier)
  const value = useMemo(() => ({ tier, settings: SETTINGS[tier], setTier }), [tier])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useQuality(): QualityApi {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useQuality yalnızca QualityProvider içinde kullanılabilir')
  return ctx
}

/** Canvas'ın İÇİNE koy. Kare hızı düşerse bir kademe iner, düzelirse çıkar. */
export function QualityMonitor() {
  const { tier, setTier } = useQuality()
  const step = useCallback(
    (d: -1 | 1) => {
      const next = ORDER[ORDER.indexOf(tier) + d]
      if (next) setTier(next)
    },
    [tier, setTier],
  )
  return <PerformanceMonitor onDecline={() => step(-1)} onIncline={() => step(1)} flipflops={3} />
}
