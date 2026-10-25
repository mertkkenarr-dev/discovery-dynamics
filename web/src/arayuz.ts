/**
 * Arayüz metinleri (iki dil). Bölüm metinleri burada değil: onlar veriden cümle kurduğu için bolumler*.tsx dosyalarında.
 */
import type { Dil } from './dil'

const TR = {
  marka: 'Steam Galaksisi',
  sayfa: 'Sayfa',
  bulgular: 'Bulgular',
  yontem: 'Yöntem',
  kesfet: 'Haritayı keşfet',
  dilDugme: 'EN',
  dilEtiket: 'Switch to English',
  yukleniyor: 'Plaka banyo ediliyor: 92 bin oyunun konumu yükleniyor…',
  hataEk: 'Sayfayı yenileyin; sorun sürerse veri dosyaları eksik olabilir.',
  baslik1: 'Bu gökyüzündeki her yıldız bir Steam oyunu.',
  baslik2Cogu: 'Çoğu hiç parlamadı.',
  baslik2Yarisi: 'Neredeyse yarısı hiç parlamadı.',
  giris: (n: string) =>
    `Discovery Dynamics, Steam'de bağımsız bir oyunu görünür kılan şeyin ne olduğunu araştıran bir veri analizi projesi. 2018–2025 arasında çıkan ${n} oyun, içerik benzerliğine göre bu haritaya yerleştirildi: yakın yıldızlar benzer oyunlar, parlaklık ilk yılın inceleme sayısı.`,
  veri: 'Veri',
  veriDeger: (n: string, m: string) => `${n} oyun; ${m} milyonu aşkın aylık inceleme kaydı`,
  yaklasim: 'Yaklaşım',
  yaklasimDeger: (h: number) => `${h} ön kayıtlı hipotez testi, nedensel çıkarım, makine öğrenmesi ve metin analizi`,
  anahtarBaslik: 'İlk yıldaki Steam incelemesi',
  anahtar: ['10’dan az', '10–99', '100–499', '500–4.999', '5.000+'],
  anahtarNot: 'Hit: ilk yılda 500 ve üstü inceleme. Büyük ve parlak yıldız, daha çok inceleme demek.',
  bulgularaGec: 'Bulgulara geç',
  bolumler: 'Bölümler',
  kesifsel: 'Keşifsel analiz',
  onKayitli: (h: string, s: string) => `Ön kayıtlı hipotez ${h}: ${s}`,
  haritada: 'Haritada:',
  yontemEtiket: 'Yöntem:',
  etkilesimli: 'Etkileşimli',
  turBaslik: 'Bir türü incele.',
  turAciklama: 'Bir alt tür seçin: oyunları haritada yanar, karnesi açılır. Değerler 2021–2025 arasında çıkan bağımsız oyunlardan.',
  turPaneli: 'Tür paneli',
  kesifBaslik: 'Bir oyunu haritada bul.',
  kesifAciklama: 'Haritayı sürükleyerek döndürün, tekerlekle yakınlaşın. Bir yıldızın üzerine gelince oyunun adı görünür; tıklayınca künyesi açılır.',
  kesfetKisa: 'Keşfet',
}

type Arayuz = typeof TR

const EN: Arayuz = {
  marka: 'Steam Galaxy',
  sayfa: 'Page',
  bulgular: 'Findings',
  yontem: 'Method',
  kesfet: 'Explore the map',
  dilDugme: 'TR',
  dilEtiket: 'Türkçeye geç',
  yukleniyor: 'Developing the plate: loading the positions of 92 thousand games…',
  hataEk: 'Reload the page; if the problem persists, data files may be missing.',
  baslik1: 'Every star in this sky is a Steam game.',
  baslik2Cogu: 'Most never shone.',
  baslik2Yarisi: 'Nearly half never shone.',
  giris: (n: string) =>
    `Discovery Dynamics is a data analysis project asking what makes an indie game visible on Steam. ${n} games released between 2018 and 2025 are placed on this map by content similarity: nearby stars are similar games, and brightness is the number of first-year reviews.`,
  veri: 'Data',
  veriDeger: (n: string, m: string) => `${n} games; over ${m} million monthly review records`,
  yaklasim: 'Approach',
  yaklasimDeger: (h: number) => `${h} pre-registered hypothesis tests, causal inference, machine learning and text analysis`,
  anahtarBaslik: 'Steam reviews in the first year',
  anahtar: ['Fewer than 10', '10–99', '100–499', '500–4,999', '5,000+'],
  anahtarNot: 'Hit: 500 or more reviews in the first year. A bigger, brighter star means more reviews.',
  bulgularaGec: 'Go to the findings',
  bolumler: 'Chapters',
  kesifsel: 'Exploratory analysis',
  onKayitli: (h: string, s: string) => `Pre-registered hypothesis ${h}: ${s}`,
  haritada: 'On the map:',
  yontemEtiket: 'Method:',
  etkilesimli: 'Interactive',
  turBaslik: 'Explore a genre.',
  turAciklama: 'Pick a subgenre: its games light up on the map and its report card opens. Figures are for indie games released 2021–2025.',
  turPaneli: 'Genre panel',
  kesifBaslik: 'Find a game on the map.',
  kesifAciklama: 'Drag to rotate the map and scroll to zoom. Hover over a star to see the game’s name; click to open its details.',
  kesfetKisa: 'Explore',
}

export const arayuz = (d: Dil): Arayuz => (d === 'tr' ? TR : EN)

/** Hipotez sonuçları ve konuları (veri Türkçe gelir). */
export function hipotezMetni(d: Dil, kod: string, konu: string, sonuc: string): { konu: string; sonuc: string } {
  if (d === 'tr') return { konu: konu.replace(/\s*\(M\d\)$/, ''), sonuc }
  const KONU: Record<string, string> = { H1: 'Novelty: inverted U', H4: 'Early Access → long tail', H5: 'Second game is more successful', H6: 'Simplified Chinese support', H7: 'Saturation' }
  const SONUC: Record<string, string> = { desteklendi: 'supported', desteklenmedi: 'not supported', 'desteklenmedi (Holm)': 'not supported (Holm)' }
  return { konu: KONU[kod] ?? konu, sonuc: SONUC[sonuc] ?? sonuc }
}
