/**
 * Giriş ekranı: başlık, proje cümlesi, künye (veri / yaklaşım), yıldız anahtarı. Başlık ve sayılar veriden, metin seçili dilde.
 */
import { Anahtar } from './Anlati'
import { arayuz } from './arayuz'
import { bicim, useDil } from './dil'
import type { Galaksi, Ozet } from './veri'

type Durum = { durum: 'yukleniyor' } | { durum: 'hata'; mesaj: string } | { durum: 'hazir'; g: Galaksi; oz: Ozet }

export function Giris({ d, ilkBolum }: { d: Durum; ilkBolum: string }) {
  const dil = useDil()
  const m = arayuz(dil)
  const { sayi } = bicim(dil)
  return (
    <section id="giris" className="giris" data-bolum="giris">
      {d.durum === 'yukleniyor' && <p className="durum">{m.yukleniyor}</p>}
      {d.durum === 'hata' && (
        <p className="durum hata" role="alert">
          {d.mesaj} {m.hataEk}
        </p>
      )}
      {d.durum === 'hazir' && (
        <>
          {/* avoid-ai-design-ignore: SD5 (iki tam cümle, 300 / 750 ağırlık; tek kelime vurgusu değil) */}
          <h1>
            <span className="ince">{m.baslik1}</span>
            <span className="kalin">{d.oz.gorunmez_yuzde > 50 ? m.baslik2Cogu : m.baslik2Yarisi}</span>
          </h1>
          <p className="giris-metin">{m.giris(sayi(d.g.n))}</p>
          <dl className="kunye-proje">
            <div>
              <dt>{m.veri}</dt>
              <dd>{m.veriDeger(sayi(d.oz.yildiz), sayi(Math.floor(d.oz.k8.gozlem / 1e6)))}</dd>
            </div>
            <div>
              <dt>{m.yaklasim}</dt>
              <dd>{m.yaklasimDeger(Object.keys(d.oz.hipotez).length)}</dd>
            </div>
          </dl>
          <Anahtar />
          <a className="asagi" href={`#${ilkBolum}`}>
            {m.bulgularaGec}
          </a>
        </>
      )}
    </section>
  )
}
