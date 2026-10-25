/**
 * İki dil (Türkçe / İngilizce). Seçim sırası: adres (?lang=en), sonra bu tarayıcıda son seçilen, sonra tarayıcı dili.
 * Sayı biçimi dile bağlı: TR 92.492 · %54,3 ; EN 92,492 · 54.3%. Türkçe ek hesabı (lib/ek.ts) yalnız TR metinlerinde kullanılır.
 */
import { createContext, useContext } from 'react'

export type Dil = 'tr' | 'en'

export const DilBaglam = createContext<Dil>('tr')
export const useDil = () => useContext(DilBaglam)

const ANAHTAR = 'steam-galaksisi-dil'

export function ilkDil(): Dil {
  const q = new URLSearchParams(window.location.search).get('lang')
  if (q === 'tr' || q === 'en') return q
  try {
    const kayitli = window.localStorage.getItem(ANAHTAR)
    if (kayitli === 'tr' || kayitli === 'en') return kayitli
  } catch {
    // depolama kapalıysa (gizli pencere) tarayıcı diline düş
  }
  return navigator.language.toLowerCase().startsWith('tr') ? 'tr' : 'en'
}

export function dilKaydet(d: Dil): void {
  document.documentElement.lang = d
  const u = new URL(window.location.href)
  u.searchParams.set('lang', d)
  window.history.replaceState(null, '', u)
  try {
    window.localStorage.setItem(ANAHTAR, d)
  } catch {
    // kalıcı tercih yalnız kolaylık; kaydedilemezse adres parametresi yine çalışır
  }
}

export interface Bicim {
  sayi: (v: number, ondalik?: number) => string
  yuzde: (v: number, ondalik?: number) => string
}

export function bicim(d: Dil): Bicim {
  const yerel = d === 'tr' ? 'tr-TR' : 'en-US'
  const sayi = (v: number, ondalik = 0) => v.toLocaleString(yerel, { minimumFractionDigits: ondalik, maximumFractionDigits: ondalik })
  return { sayi, yuzde: (v, ondalik = 0) => (d === 'tr' ? `%${sayi(v, ondalik)}` : `${sayi(v, ondalik)}%`) }
}

/** İki dilli kısa metin seçici: t(dil, 'Türkçe', 'English'). */
export const t = (d: Dil, tr: string, en: string) => (d === 'tr' ? tr : en)
