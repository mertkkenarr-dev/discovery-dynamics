/**
 * İkinci oyun çizgileri: aynı stüdyonun ilk oyunundan ikincisine. Sıcak = ikinci oyun daha çok inceleme aldı, soğuk = daha az.
 * Renk tonu yönü, parlaklık farkın büyüklüğünü taşır. Normal karışım: toplamalı karışımda 10 bin çizgi üst üste binip
 * beyaza dönüyor ve sıcak/soğuk ayrımı kayboluyordu.
 */
import { useFrame } from '@react-three/fiber'
import { useEffect, useMemo, useRef } from 'react'
import { BufferAttribute, BufferGeometry, LineBasicMaterial, NormalBlending } from 'three'
import type { Cift, Galaksi } from '../veri'
import { OLCEK } from './Yildizlar'

const SICAK: [number, number, number] = [1.0, 0.5, 0.12]
const SOGUK: [number, number, number] = [0.22, 0.42, 1.0]
export const ESIK = 0.5

export function Cizgiler({ g, ciftler, gorunur }: { g: Galaksi; ciftler: Cift[]; gorunur: boolean }) {
  const malzeme = useRef<LineBasicMaterial>(null)

  const geo = useMemo(() => {
    // Yalnız belirgin farklar (|Δlog10| ≥ 0,5, yani ~3 kat): küçük farklar çizgi yığınında okunamıyor, yalnız yoğunluk ekliyor.
    const secili = ciftler.filter(([, , d]) => Math.abs(d) >= ESIK)
    const b = new BufferGeometry()
    const p = new Float32Array(secili.length * 6)
    const c = new Float32Array(secili.length * 6)
    secili.forEach(([a, z, d], k) => {
      const renk = d >= 0 ? SICAK : SOGUK
      // Uzun çizgiler gözü yanıltıyor (çiftlerin çoğu birbirine yakın: ortanca uzaklık, rastgele iki oyununkinin ~yarısı); uzunluğa göre sönükleşir.
      const boy = Math.hypot(g.konum[a * 3]! - g.konum[z * 3]!, g.konum[a * 3 + 1]! - g.konum[z * 3 + 1]!, g.konum[a * 3 + 2]! - g.konum[z * 3 + 2]!) * OLCEK
      const guc = (0.4 + 0.6 * Math.min(1, Math.abs(d) / 2)) * Math.max(0.15, 1 - boy / 12)
      for (let u = 0; u < 2; u++) {
        const i = u === 0 ? a : z
        for (let e = 0; e < 3; e++) {
          p[k * 6 + u * 3 + e] = g.konum[i * 3 + e]! * OLCEK
          c[k * 6 + u * 3 + e] = renk[e]! * guc * (u === 0 ? 0.35 : 1)
        }
      }
    })
    b.setAttribute('position', new BufferAttribute(p, 3))
    b.setAttribute('color', new BufferAttribute(c, 3))
    return b
  }, [g, ciftler])

  useEffect(() => () => geo.dispose(), [geo])

  useFrame((_, dt) => {
    const m = malzeme.current
    if (!m) return
    m.opacity += ((gorunur ? 0.42 : 0) - m.opacity) * (1 - Math.exp(-3 * dt))
    m.visible = m.opacity > 0.005
  })

  return (
    <lineSegments geometry={geo} frustumCulled={false}>
      <lineBasicMaterial ref={malzeme} vertexColors transparent opacity={0} depthWrite={false} blending={NormalBlending} />
    </lineSegments>
  )
}
