/**
 * Galaksi verisi: scripts/14_web_veri.py üretir. İkili düzen (küçük-endian):
 *   uint32 n | float32 x,y,z (n×3) | float32 log10(1+r365) (n) | uint8 kademe | uint8 yıl-2018 | uint8 fiyat | uint8 bayrak | uint8 yenilik
 * Boyut, başlıktaki n ile tutmazsa hata fırlatılır (yarım indirme sessizce yanlış çizilmesin).
 */
export interface Galaksi {
  n: number
  konum: Float32Array
  parlaklik: Float32Array
  kademe: Uint8Array
  yil: Uint8Array
  fiyat: Uint8Array
  bayrak: Uint8Array
  yenilik: Uint8Array
}

export const BAYRAK = { organik: 1, cokOyunculu: 2, ea: 4, yapayZeka: 8, sevilen: 16, cince: 32 } as const

export interface Ozet {
  yildiz: number
  orneklem: number
  gorunmez_yuzde: number
  hit_yuzde: number
  arz: Record<string, number>
  hit_yil: Record<string, number>
  hit_sayisi: Record<string, number>
  fiyat_hit: Record<string, number>
  yenilik: { b2_p: number; egim_alt_t: number; egim_ust_t: number }
  etiket_en_olumlu: [string, number][]
  motivasyon: Record<string, { arz: number; hit: number; sevilen: number }>
  cince: { ana: number; temkinli: number; ekleme_T0: number; ekleme_T4: number }
  yorunge: Record<string, { pay: number; hit: number; ikinci_yil: number }>
  ea_kuyruk: { or: number; ortanca: Record<string, number> }
  ikinci_oyun: { n: number; iyilesen: number; temiz_yuzde: number; T0_kalan: number }
  ilk_ay: { rho: number; hit: Record<string, number>; carpan: Record<string, number | null> }
  yapay_zeka: { gorunmez: Record<string, { n: number; gorunmez: number; hit: number }>; or: number; pay_yil: Record<string, number> }
  model: { pr_auc: number; taban: number; ust_dilim: number }
  siniflar: Record<string, number>
}

export type Cift = [number, number, number]

export async function galaksiYukle(): Promise<Galaksi> {
  const r = await fetch('/veri/galaksi.bin')
  if (!r.ok) throw new Error(`Galaksi verisi yüklenemedi (HTTP ${r.status}).`)
  const buf = await r.arrayBuffer()
  const n = new DataView(buf).getUint32(0, true)
  const beklenen = 4 + n * 12 + n * 4 + n * 5 // başlık + konum (3×f32) + parlaklık (f32) + 5 × u8
  if (buf.byteLength !== beklenen) throw new Error(`Galaksi verisi bozuk: ${buf.byteLength} bayt, beklenen ${beklenen}.`)
  let o = 4
  const al = <T>(Ctor: new (b: ArrayBuffer, o: number, n: number) => T, adet: number, bayt: number): T => {
    const a = new Ctor(buf, o, adet)
    o += adet * bayt
    return a
  }
  const konum = al(Float32Array, n * 3, 4)
  const parlaklik = al(Float32Array, n, 4)
  return { n, konum, parlaklik, kademe: al(Uint8Array, n, 1), yil: al(Uint8Array, n, 1), fiyat: al(Uint8Array, n, 1), bayrak: al(Uint8Array, n, 1), yenilik: al(Uint8Array, n, 1) }
}

export async function jsonYukle<T>(ad: string): Promise<T> {
  const r = await fetch(`/veri/${ad}`)
  if (!r.ok) throw new Error(`${ad} yüklenemedi (HTTP ${r.status}).`)
  return (await r.json()) as T
}

/** Türkçe sayı biçimi: 95.647 · %54,3 */
export const sayi = (v: number, ondalik = 0) => v.toLocaleString('tr-TR', { minimumFractionDigits: ondalik, maximumFractionDigits: ondalik })
export const yuzde = (v: number, ondalik = 0) => `%${sayi(v, ondalik)}`
