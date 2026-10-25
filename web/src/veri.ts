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

export const BAYRAK = { organik: 1, cokOyunculu: 2, ea: 4, yapayZeka: 8, sevilen: 16, cince: 32, gizli: 64, firsat: 128 } as const

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
  k5: {
    dalga: { oncu: Aralik & { n_merkez: number }; plasebo: Aralik & { n_merkez: number } }
    oncul: HitOzet
    takipci: HitOzet
    takipci_dilim: Record<string, { n: number; oran: number; alt: number; ust: number }>
    plasebo: HitOzet
    dalgalar: { ad: string; yil: number; oncu: number[]; takipci: number[]; orneklem: number; hit: number; diger: string[] }[]
  }
  k6: {
    k: number
    bolgeler: { ad: string; n: number; hit_oran: number; ob: number; alt: number; ust: number; arz_22_25: number; goreli_buyume: number; firsat: boolean }[]
    etiketler: { ad: string; merkez: [number, number, number] }[]
  }
  k7: { n_gizli: number; n_gorunur: number; cok_begenilen: number; farklar: Record<string, { gorunur: number; gizli: number; smd: number }> }
  hipotez: Record<string, { konu: string; sonuc: string; p_holm?: number }>
  k9: { n_test: number; modeller: Record<string, { pr_auc: number; alt: number; ust: number; roc_auc: number; fark: number; fark_alt: number; fark_ust: number }>; uslup_or: Record<string, { tahmin: number; alt: number; ust: number }> }
  k10: {
    karne: TurKarne[]
    merkez: [number, number, number][]
    ort_hit: number
    ort_gorunmez: number
    n_cift: number
    n_anlamli: number
    n_p05: number
    hibrit_uc: { cift: string; a: string; b: string; n: number; hit: number; ob: number; alt: number; ust: number; q: number }[]
  }
  duyarlilik: { K6: Record<string, { ob: number; alt: number; ust: number; n: number }> }
  k8: { gozlem: number; oyun: number; tahmin: { esik: number; sicrama: number; alt: number; ust: number; yuzde: number }[]; secilim: Record<string, { sicrama: number; alt: number; ust: number }> }
}

interface Aralik {
  oran: number
  alt: number
  ust: number
}

interface HitOzet {
  n: number
  hit_oran: number
  wilson: [number, number]
  ob: number
}

export interface TurKarne {
  tur: string
  n: number
  hit: number
  hit_alt: number
  hit_ust: number
  gorunmez: number
  ob: number
  ob_alt: number
  ob_ust: number
  arz_22_25: number
  goreli_buyume: number
  tatli_fiyat: string | null
  tatli_fiyat_hit: number | null
  hit_erken: number
  hit_gec: number
  egilim: number
  egilim_alt: number
  egilim_ust: number
  ortanca_fiyat: number
}

export type Cift = [number, number, number]

/** turler.bin (scripts/14_web_veri.turler_yaz): uint16 tür sayısı | uint32 yıldız | tür başına yıldız-bitlik üyelik (LSB önce). */
export async function turlerYukle(n: number): Promise<Uint8Array[]> {
  const r = await fetch('/veri/turler.bin')
  if (!r.ok) throw new Error(`Tür verisi yüklenemedi (HTTP ${r.status}).`)
  const buf = await r.arrayBuffer()
  const v = new DataView(buf)
  const [nt, ny] = [v.getUint16(0, true), v.getUint32(2, true)]
  const bayt = Math.ceil(ny / 8)
  if (ny !== n || buf.byteLength !== 6 + nt * bayt) throw new Error(`Tür verisi galaksiyle uyuşmuyor (${ny} / ${n} yıldız, ${buf.byteLength} bayt).`)
  return Array.from({ length: nt }, (_, k) => new Uint8Array(buf, 6 + k * bayt, bayt))
}

export const uyeMi = (bit: Uint8Array, i: number) => ((bit[i >> 3]! >> (i & 7)) & 1) === 1

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
