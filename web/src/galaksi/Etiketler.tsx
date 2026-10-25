/**
 * Haritadaki adlı işaretler: anlatıda öncü oyunlar ve fırsat bölgeleri, keşifte seçili yıldız.
 * drei Html ile DOM'da çizilir (metin keskin kalır, ekran okuyucuya kapalı: aynı bilgi bölüm metninde var).
 */
import { Html } from '@react-three/drei'
import { OLCEK } from './Yildizlar'

export interface Etiket {
  konum: [number, number, number]
  ad: string
  tur: 'yildiz' | 'bolge' | 'secim'
}

export function Etiketler({ liste }: { liste: Etiket[] }) {
  return (
    <>
      {liste.map((e) => (
        <Html
          key={`${e.tur}-${e.ad}`}
          position={[e.konum[0] * OLCEK, e.konum[1] * OLCEK, e.konum[2] * OLCEK]}
          center
          zIndexRange={[2, 0]}
          style={{ pointerEvents: 'none' }}
        >
          <div className={`isaret isaret-${e.tur}`} aria-hidden="true">
            {e.tur !== 'bolge' && <span className="halka" />}
            <span className="ad">{e.ad}</span>
          </div>
        </Html>
      ))}
    </>
  )
}
