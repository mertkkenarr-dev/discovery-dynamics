/**
 * Kamera iki modda çalışır. Anlatıda kamera bölümün maskesinin ağırlık merkezine döner ve yavaşça yörüngede gezer;
 * keşifte kontrol kullanıcıya (OrbitControls) geçer ve yalnız arama sonucuna "uçuş" otomatiktir.
 * Anlatıdan keşfe geçişte OrbitControls son hedefle bağlanır, böylece görüntü sıçramaz.
 */
import { OrbitControls } from '@react-three/drei'
import { useFrame, useThree } from '@react-three/fiber'
import { useEffect, useRef } from 'react'
import { Vector3 } from 'three'
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib'
import { OLCEK } from './Yildizlar'

interface Props {
  merkez: [number, number, number]
  uzaklik: number
  kesif: boolean
  ucus: [number, number, number] | null
  hareketAzalt: boolean
}

const gecici = new Vector3()
const yon = new Vector3()

export function Kamera({ merkez, uzaklik, kesif, ucus, hareketAzalt }: Props) {
  const hedef = useRef(new Vector3())
  const aci = useRef(0.6)
  const ucusKalan = useRef(0)
  const kayma = useRef(0)
  const kaymaY = useRef(0)
  const controls = useThree((s) => s.controls) as OrbitControlsImpl | null

  const geriKalan = useRef(0)
  const onceki = useRef<typeof ucus>(null)
  useEffect(() => {
    if (ucus) ucusKalan.current = 2.4
    else if (onceki.current) geriKalan.current = 2 // seçim kalkınca yıldızın dibinden genel görünüme geri çekil
    onceki.current = ucus
  }, [ucus])

  useFrame(({ camera, size }, dt) => {
    if (!('setViewOffset' in camera)) return
    const k = hareketAzalt ? 1 : 1 - Math.exp(-1.6 * dt)
    if (!kesif) {
      if (!hareketAzalt) aci.current += dt * 0.035
      gecici.set(merkez[0] * OLCEK * 0.6, merkez[1] * OLCEK * 0.6, merkez[2] * OLCEK * 0.6)
      hedef.current.lerp(gecici, k)
      const r = uzaklik * (size.width < size.height ? 1.45 : 1)
      const phi = 1.12
      gecici.set(Math.sin(phi) * Math.cos(aci.current), Math.cos(phi), Math.sin(phi) * Math.sin(aci.current)).multiplyScalar(r).add(hedef.current)
      camera.position.lerp(gecici, k)
      camera.lookAt(hedef.current)
      // Geniş ekranda metin solda: görüntü penceresini kaydırıp galaksiyi sağ yarıya al (perspektif bozulmaz).
      // Dar ekranda metin altta: galaksiyi üst yarıya al.
      const genis = size.width > size.height * 1.15
      const kay = genis ? -size.width * (size.width > size.height * 1.6 ? 0.29 : 0.24) : 0 // çok geniş ekranda başlık galaksiye binmesin
      const dikey = genis ? 0 : size.height * 0.28
      kayma.current += (kay - kayma.current) * k
      kaymaY.current += (dikey - kaymaY.current) * k
      camera.setViewOffset(size.width, size.height, kayma.current, kaymaY.current, size.width, size.height)
      return
    }
    if (controls && !ucus && geriKalan.current > 0) {
      geriKalan.current -= dt
      yon.copy(camera.position).sub(controls.target).normalize().multiplyScalar(uzaklik * 0.8).add(controls.target)
      camera.position.lerp(yon, k * 1.6)
      controls.update()
      return
    }
    if (!controls || !ucus || ucusKalan.current <= 0) return
    ucusKalan.current -= dt
    gecici.set(ucus[0] * OLCEK, ucus[1] * OLCEK, ucus[2] * OLCEK)
    controls.target.lerp(gecici, k * 1.6)
    yon.copy(camera.position).sub(controls.target).normalize().multiplyScalar(5)
    camera.position.lerp(gecici.add(yon), k * 1.6)
    controls.update()
  })

  if (!kesif) return null
  return (
    <OrbitControls
      makeDefault
      target={hedef.current.toArray()}
      enableDamping
      dampingFactor={0.08}
      minDistance={1.2}
      maxDistance={40}
      rotateSpeed={0.5}
      zoomSpeed={0.7}
      enablePan
    />
  )
}
