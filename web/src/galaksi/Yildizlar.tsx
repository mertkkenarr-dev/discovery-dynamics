/**
 * 92 bin yıldız tek Points nesnesi (tek çizim çağrısı). React state'i yalnız bölüm değişince değişir;
 * geçişler useFrame içinde uniform/buffer güncellemesiyle yapılır (her karede setState yok).
 */
import { useFrame, type ThreeEvent } from '@react-three/fiber'
import { useEffect, useMemo, useRef } from 'react'
import { AdditiveBlending, BufferAttribute, BufferGeometry, ShaderMaterial } from 'three'
import type { Galaksi } from '../veri'
import { fragment, vertex } from './shader'

export const OLCEK = 10 // [-1, 1] → dünya birimi

interface Props {
  g: Galaksi
  maske: Float32Array | null
  yilAnim: boolean
  hareketAzalt: boolean
  etkilesim: boolean
  onIsaret: (i: Isaret | null) => void
  onSec: (i: number) => void
}

export interface Isaret {
  i: number
  x: number
  y: number
}

const yumusat = (hiz: number, dt: number) => 1 - Math.exp(-hiz * dt)

export function Yildizlar({ g, maske, yilAnim, hareketAzalt, etkilesim, onIsaret, onSec }: Props) {
  const malzeme = useRef<ShaderMaterial>(null)
  const durum = useRef({ poz: hareketAzalt ? 1 : 0, t: 1, yilBas: -1 })

  const geo = useMemo(() => {
    const b = new BufferGeometry()
    const p = new Float32Array(g.konum.length)
    for (let i = 0; i < p.length; i++) p[i] = g.konum[i]! * OLCEK
    b.setAttribute('position', new BufferAttribute(p, 3))
    b.setAttribute('aParlak', new BufferAttribute(g.parlaklik, 1))
    b.setAttribute('aKademe', new BufferAttribute(Float32Array.from(g.kademe), 1))
    b.setAttribute('aYil', new BufferAttribute(Float32Array.from(g.yil), 1))
    b.setAttribute('aMaskA', new BufferAttribute(new Float32Array(g.n).fill(1), 1))
    b.setAttribute('aMaskB', new BufferAttribute(new Float32Array(g.n).fill(1), 1))
    b.computeBoundingSphere()
    return b
  }, [g])

  const uniforms = useMemo(() => ({ uT: { value: 1 }, uOdak: { value: 0 }, uYil: { value: 7 }, uPoz: { value: 0 }, uOlcek: { value: 10 } }), [])

  // Bölüm değişince: şimdiki görünen maskeyi A'ya, yenisini B'ye yaz ve geçişi baştan başlat.
  useEffect(() => {
    const A = geo.getAttribute('aMaskA') as BufferAttribute
    const B = geo.getAttribute('aMaskB') as BufferAttribute
    const t = durum.current.t
    const a = A.array as Float32Array
    const b = B.array as Float32Array
    for (let i = 0; i < g.n; i++) a[i] = a[i]! + (b[i]! - a[i]!) * t
    if (maske) b.set(maske)
    A.needsUpdate = true
    B.needsUpdate = true
    durum.current.t = 0
    durum.current.yilBas = yilAnim ? -1 : durum.current.yilBas
  }, [maske, yilAnim, geo, g.n])

  useEffect(() => () => geo.dispose(), [geo])

  useFrame((state, dt) => {
    const m = malzeme.current
    if (!m) return
    const d = durum.current
    const u = m.uniforms as typeof uniforms
    d.poz = Math.min(1, d.poz + dt / 2.6)
    u.uPoz.value = d.poz
    d.t = hareketAzalt ? 1 : Math.min(1, d.t + dt / 0.9)
    u.uT.value = d.t
    // Keşifte seçili yıldız öne çıkar ama komşular okunur kalır: yakınındaki benzer oyunlar da keşfin parçası.
    u.uOdak.value += ((maske ? (etkilesim ? 0.6 : 1) : 0) - u.uOdak.value) * yumusat(4, dt)
    if (yilAnim && !hareketAzalt) {
      if (d.yilBas < 0) d.yilBas = state.clock.elapsedTime
      u.uYil.value = Math.min(7, ((state.clock.elapsedTime - d.yilBas) / 5.5) * 8 - 0.5)
    } else {
      u.uYil.value += (7 - u.uYil.value) * yumusat(3, dt)
    }
    u.uOlcek.value = state.size.height * state.gl.getPixelRatio() * 0.05
  })

  // En yakın yıldız: raycaster eşik içindeki tüm noktaları döndürür, ilk kesişim kameraya en yakın olandır.
  const ilk = (e: ThreeEvent<PointerEvent | MouseEvent>) => e.intersections.find((x) => x.object === e.object)?.index
  const olaylar = etkilesim
    ? {
        onPointerMove: (e: ThreeEvent<PointerEvent>) => {
          const i = ilk(e)
          if (i !== undefined) onIsaret({ i, x: e.nativeEvent.clientX, y: e.nativeEvent.clientY })
        },
        onPointerOut: () => onIsaret(null),
        onClick: (e: ThreeEvent<MouseEvent>) => {
          if (e.delta > 4) return // sürükleyip döndürme bir tıklama değil (delta = basma ile bırakma arası piksel)
          const i = ilk(e)
          if (i !== undefined) onSec(i)
        },
      }
    : {}

  return (
    <points geometry={geo} frustumCulled={false} {...olaylar}>
      <shaderMaterial ref={malzeme} vertexShader={vertex} fragmentShader={fragment} uniforms={uniforms} transparent depthWrite={false} blending={AdditiveBlending} />
    </points>
  )
}
