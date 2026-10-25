/**
 * Yıldız shader'ı. Boyut/parlaklık = log10(1 + ilk yıl incelemesi) (kadir ölçeği gibi); renk = başarı kademesine göre sıcaklık.
 * Yalnız T3/T4 renkleri 1'in üstünde (HDR): bloom eşiği 1 olduğundan yalnız hit'ler parlar.
 * Maske geçişi: aMaskA → aMaskB, uT ile; uOdak = 0 iken maske yok sayılır. uYil: bu yıldan sonra çıkanlar gizli.
 * uPoz: açılış pozlaması (0→1); parlak yıldızlar önce, sönükler sonra belirir.
 */
export const vertex = /* glsl */ `
  attribute float aParlak;
  attribute float aKademe;
  attribute float aYil;
  attribute float aMaskA;
  attribute float aMaskB;
  uniform float uT;
  uniform float uOdak;
  uniform float uYil;
  uniform float uPoz;
  uniform float uOlcek;
  varying vec3 vRenk;
  varying float vAlfa;

  vec3 kademeRengi(float k) {
    if (k < 0.5) return vec3(0.20, 0.28, 0.55);   // T0: soğuk toz
    if (k < 1.5) return vec3(0.36, 0.50, 0.88);   // T1: soluk mavi
    if (k < 2.5) return vec3(0.74, 0.80, 0.94);   // T2: beyaz
    if (k < 3.5) return vec3(1.00, 0.70, 0.36) * 1.3; // T3: sıcak (HDR)
    return vec3(1.00, 0.56, 0.18) * 2.4;          // T4: altın (HDR)
  }

  void main() {
    float k = aKademe > 10.0 ? 0.0 : aKademe;
    float m = mix(aMaskA, aMaskB, uT);
    float odak = mix(1.0, m, uOdak);
    float poz = smoothstep(1.0 - aParlak / 5.3, 1.15 - aParlak / 5.3, uPoz * 1.15);
    float gorunur = step(aYil, uYil + 0.5) * poz;

    vec3 renk = kademeRengi(k);
    vec3 sonuk = vec3(0.10, 0.13, 0.22);
    vRenk = mix(sonuk, renk * (1.0 + 0.35 * m * uOdak), odak);
    // Toplamalı karışımda 92 bin nokta üst üste biner; sönük kademelerin alfası düşük tutulmazsa yoğun bölgeler beyaza patlar.
    float taban = k < 0.5 ? 0.42 : (k < 1.5 ? 0.5 : (k < 2.5 ? 0.6 : 0.9));
    vAlfa = gorunur * taban * mix(0.22, 1.0, odak);

    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    float boyut = (1.7 + aParlak * 0.95) * mix(0.8, 1.15, odak);
    // Üst sınır: keşifte kamera bir yıldıza çok yaklaşınca noktalar ekranı kaplayan lekelere dönüşüyordu.
    gl_PointSize = min(boyut * uOlcek / -mv.z, uOlcek * 0.9) * gorunur;
    gl_Position = projectionMatrix * mv;
  }
`

export const fragment = /* glsl */ `
  varying vec3 vRenk;
  varying float vAlfa;
  void main() {
    float d = length(gl_PointCoord - 0.5);
    float cekirdek = smoothstep(0.5, 0.0, d);
    float a = cekirdek * cekirdek * vAlfa;
    if (a < 0.004) discard;
    gl_FragColor = vec4(vRenk * a, a);
  }
`
