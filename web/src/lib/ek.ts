/**
 * Sayılara Türkçe ek: "%54'ü", "2025'te". Metindeki sayılar veriden geldiği için ek de sayıyla birlikte hesaplanmalı;
 * sabit yazılan ek ("'i") sayı değişince yanlış okunur. Ek, sayının okunuşundaki son kelimeye göre seçilir.
 */
type Son = { unlu: 'a' | 'e' | 'ı' | 'i' | 'o' | 'ö' | 'u' | 'ü'; unluBiter: boolean; sert: boolean }

const birler: Record<string, Son> = {
  '1': { unlu: 'i', unluBiter: false, sert: false }, // bir
  '2': { unlu: 'i', unluBiter: true, sert: false }, // iki
  '3': { unlu: 'ü', unluBiter: false, sert: true }, // üç
  '4': { unlu: 'ö', unluBiter: false, sert: true }, // dört
  '5': { unlu: 'e', unluBiter: false, sert: true }, // beş
  '6': { unlu: 'ı', unluBiter: true, sert: false }, // altı
  '7': { unlu: 'i', unluBiter: true, sert: false }, // yedi
  '8': { unlu: 'i', unluBiter: false, sert: false }, // sekiz
  '9': { unlu: 'u', unluBiter: false, sert: false }, // dokuz
}
const onlar: Record<string, Son> = {
  '1': { unlu: 'o', unluBiter: false, sert: false }, // on
  '2': { unlu: 'i', unluBiter: true, sert: false }, // yirmi
  '3': { unlu: 'u', unluBiter: false, sert: false }, // otuz
  '4': { unlu: 'ı', unluBiter: false, sert: true }, // kırk
  '5': { unlu: 'i', unluBiter: true, sert: false }, // elli
  '6': { unlu: 'ı', unluBiter: false, sert: true }, // altmış
  '7': { unlu: 'i', unluBiter: false, sert: true }, // yetmiş
  '8': { unlu: 'e', unluBiter: false, sert: false }, // seksen
  '9': { unlu: 'a', unluBiter: false, sert: false }, // doksan
}
const YUZ: Son = { unlu: 'ü', unluBiter: false, sert: false }
const BIN: Son = { unlu: 'i', unluBiter: false, sert: false }
const SIFIR: Son = { unlu: 'ı', unluBiter: false, sert: false }

/** Biçimlenmiş sayının ("54", "4,8", "20.363") okunuşundaki son kelime. */
function son(metin: string): Son {
  const r = metin.replace(/[^\d,]/g, '')
  const [tam = '0', kesir] = r.split(',')
  const k = kesir?.replace(/0+$/, '')
  if (k) return son(k)
  const t = tam.replace(/^0+/, '') || '0'
  if (t === '0') return SIFIR
  const b = t[t.length - 1]!
  if (b !== '0') return birler[b]!
  const o = t[t.length - 2]
  if (o && o !== '0') return onlar[o]!
  if (t.length >= 4 && t.slice(-3) === '000') return BIN
  return YUZ
}

const kalin = (u: string) => 'aıou'.includes(u)

/** Belirtme/iyelik: 54'ü, 4,8'i, 2'si, 50'si */
export function ekI(metin: string): string {
  const s = son(metin)
  const u = { a: 'ı', ı: 'ı', o: 'u', u: 'u', e: 'i', i: 'i', ö: 'ü', ü: 'ü' }[s.unlu]
  return `${metin}'${s.unluBiter ? 's' : ''}${u}`
}

/** Bulunma: 2018'de, 2025'te, 40'ta */
export function ekDe(metin: string): string {
  const s = son(metin)
  return `${metin}'${s.sert ? 't' : 'd'}${kalin(s.unlu) ? 'a' : 'e'}`
}
