/**
 * Bölüm maskeleri: her yıldız için 0/1. Maskeler istemcide bayt dizilerinden üretilir (ayrı dosya indirmeye gerek yok)
 * ve ilk istekte bir kez hesaplanıp önbelleğe alınır.
 */
import { BAYRAK, type Galaksi } from '../veri'

export type MaskeAdi = 'gorunmez' | 'hit' | 'pahali' | 'tanidik' | 'birlikte' | 'ea' | 'cince' | 'yapayZeka' | 'hicbiri'

export interface Maske {
  dizi: Float32Array
  adet: number
  /** Maskeli yıldızların ağırlık merkezi ([-1, 1] uzayında); kamera buraya döner. */
  merkez: [number, number, number]
}

const BILINMIYOR = 255

function kur(g: Galaksi, kosul: (i: number) => boolean): Maske {
  const dizi = new Float32Array(g.n)
  let adet = 0
  let x = 0
  let y = 0
  let z = 0
  for (let i = 0; i < g.n; i++) {
    if (!kosul(i)) continue
    dizi[i] = 1
    adet++
    x += g.konum[i * 3]!
    y += g.konum[i * 3 + 1]!
    z += g.konum[i * 3 + 2]!
  }
  const b = Math.max(adet, 1)
  return { dizi, adet, merkez: [x / b, y / b, z / b] }
}

/** Yeniliği en düşük %25'lik dilim: "tanıdık" kombinasyonlar. Eşik veriden hesaplanır, sabit yazılmaz. */
function tanidikEsigi(g: Galaksi): number {
  const sayac = new Uint32Array(255)
  let toplam = 0
  for (let i = 0; i < g.n; i++) {
    const v = g.yenilik[i]!
    if (v === BILINMIYOR) continue
    sayac[v]!++
    toplam++
  }
  let birikim = 0
  for (let v = 0; v < 255; v++) {
    birikim += sayac[v]!
    if (birikim >= toplam * 0.25) return v
  }
  return 254
}

export function maskeUretici(g: Galaksi) {
  const onbellek = new Map<MaskeAdi, Maske>()
  return (ad: MaskeAdi): Maske => {
    const var_ = onbellek.get(ad)
    if (var_) return var_
    let m: Maske
    switch (ad) {
      case 'gorunmez':
        m = kur(g, (i) => g.kademe[i] === 0)
        break
      case 'hit':
        m = kur(g, (i) => g.kademe[i] === 3 || g.kademe[i] === 4)
        break
      case 'pahali':
        m = kur(g, (i) => g.fiyat[i] === 4 || g.fiyat[i] === 5)
        break
      case 'tanidik': {
        const esik = tanidikEsigi(g)
        m = kur(g, (i) => g.yenilik[i]! <= esik)
        break
      }
      case 'birlikte':
        m = kur(g, (i) => (g.bayrak[i]! & BAYRAK.cokOyunculu) !== 0)
        break
      case 'ea':
        m = kur(g, (i) => (g.bayrak[i]! & BAYRAK.ea) !== 0)
        break
      case 'cince':
        m = kur(g, (i) => (g.bayrak[i]! & BAYRAK.cince) !== 0)
        break
      case 'yapayZeka':
        m = kur(g, (i) => (g.bayrak[i]! & BAYRAK.yapayZeka) !== 0)
        break
      case 'hicbiri':
        m = kur(g, () => false)
        break
    }
    onbellek.set(ad, m)
    return m
  }
}

/** Tek yıldızı öne çıkaran maske (keşif modunda arama sonucu). Önbelleğe alınmaz. */
export function tekYildiz(g: Galaksi, i: number): Maske {
  const dizi = new Float32Array(g.n)
  dizi[i] = 1
  return { dizi, adet: 1, merkez: [g.konum[i * 3]!, g.konum[i * 3 + 1]!, g.konum[i * 3 + 2]!] }
}
