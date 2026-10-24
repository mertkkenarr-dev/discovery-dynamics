/**
 * Canvas + efekt yığını. Bloom eşiği 1: yalnız HDR renkli hit yıldızları ışır (shader.ts).
 * Gren yalnız yüksek kalitede; zayıf GPU'da QualityMonitor kademeyi düşürür.
 */
import { Canvas } from '@react-three/fiber'
import { Bloom, EffectComposer, Noise, ToneMapping, Vignette } from '@react-three/postprocessing'
import { BlendFunction, ToneMappingMode } from 'postprocessing'
import { QualityMonitor, useQuality } from '../kit/quality'
import type { Cift, Galaksi } from '../veri'
import { Cizgiler } from './Cizgiler'
import { Kamera } from './Kamera'
import type { Maske } from './maske'
import { Yildizlar, type Isaret } from './Yildizlar'

export interface SahneDurumu {
  maske: Maske | null
  yilAnim: boolean
  cizgiler: boolean
  uzaklik: number
  kesif: boolean
  ucus: [number, number, number] | null
}

interface Props {
  g: Galaksi
  ciftler: Cift[]
  durum: SahneDurumu
  hareketAzalt: boolean
  onIsaret: (i: Isaret | null) => void
  onSec: (i: number) => void
}

const MERKEZ: [number, number, number] = [0, 0, 0]
const RAYCASTER = { params: { Points: { threshold: 0.07 }, Mesh: {}, Line: { threshold: 0 }, LOD: {}, Sprite: {} } }

export function Sahne({ g, ciftler, durum, hareketAzalt, onIsaret, onSec }: Props) {
  const { settings } = useQuality()
  return (
    <Canvas
      className="sahne"
      dpr={settings.dpr}
      camera={{ position: [0, 6, 24], fov: 42, near: 0.05, far: 200 }}
      gl={{ antialias: false, powerPreference: 'high-performance' }}
      raycaster={RAYCASTER}
      aria-hidden="true"
    >
      <color attach="background" args={['#0b1020']} />
      <QualityMonitor />
      <Yildizlar
        g={g}
        maske={durum.maske?.dizi ?? null}
        yilAnim={durum.yilAnim}
        hareketAzalt={hareketAzalt}
        etkilesim={durum.kesif}
        onIsaret={onIsaret}
        onSec={onSec}
      />
      <Cizgiler g={g} ciftler={ciftler} gorunur={durum.cizgiler} />
      <Kamera merkez={durum.maske?.merkez ?? MERKEZ} uzaklik={durum.uzaklik} kesif={durum.kesif} ucus={durum.ucus} hareketAzalt={hareketAzalt} />
      <EffectComposer multisampling={0} enableNormalPass={false}>
        {settings.bloom ? <Bloom luminanceThreshold={1} luminanceSmoothing={0.2} intensity={0.6} mipmapBlur radius={0.72} /> : <></>}
        <Vignette offset={0.28} darkness={0.72} />
        {settings.grain ? <Noise premultiply blendFunction={BlendFunction.SCREEN} opacity={0.22} /> : <></>}
        <ToneMapping mode={ToneMappingMode.NEUTRAL} />
      </EffectComposer>
    </Canvas>
  )
}
