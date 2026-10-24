#!/usr/bin/env node
// 3B'ye özgü "stok görünüm" taraması. Salt-okunur, yalnız fs+path. detect.mjs'i tamamlar (o, UI/CSS kalıplarına bakar).
// Bulgu = kimsenin bilerek seçmediği varsayılan. Bilerek seçtiysen satıra ekle:  // slop3d-ignore: <KURAL>
// Kullanım: node scripts/slop3d.mjs src [--strict]   (--strict: bulgu varsa çıkış kodu 1)
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { extname, join } from 'node:path'

const root = process.argv[2] ?? 'src'
const strict = process.argv.includes('--strict')

const RULES = [
  { id: 'env-preset', sev: 'P1', test: (s) => /<Environment[^>]*\bpreset=/.test(s), msg: 'Hazır Environment preset\'i: herkesin kullandığı ışık. Lightformer ile özel ortam kur veya kendi HDRI\'ını yükle.' },
  { id: 'bloom-no-threshold', sev: 'P1', test: (s) => /<Bloom\b(?![^>]*luminanceThreshold)/.test(s), msg: 'Bloom eşiksiz: her şey parlar. luminanceThreshold={1} ver, yalnız HDR emissive parlasın.' },
  { id: 'stock-blob', sev: 'P1', test: (s) => /MeshDistortMaterial|MeshWobbleMaterial/.test(s), msg: 'Drei stok "blob" malzemesi. Okunur bir bilgi taşımıyorsa çıkar.' },
  { id: 'floating-glass', sev: 'P1', test: (s) => /<Float\b/.test(s) && /MeshTransmissionMaterial/.test(s), msg: 'Havada süzülen cam nesne: en tanınır AI-3B kalıbı. Nesnenin sahnede bir yeri/işlevi olsun.' },
  { id: 'tailwind-violet', sev: 'P2', test: (s) => /#(6366f1|8b5cf6|a855f7|7c3aed|4f46e5|9333ea)\b/i.test(s), msg: 'Tailwind indigo/violet varsayılan renkleri. tokens.ts\'teki paletten renk kullan.' },
  { id: 'autorotate', sev: 'P2', test: (s) => /autoRotate(?!=\{false\})/.test(s), msg: 'OrbitControls autoRotate: demo hissi. Yönetilmiş kamera çekimi (CameraShots) kullan.' },
  { id: 'composer-no-tonemap', sev: 'P1', test: (s) => /<EffectComposer/.test(s) && !/ToneMapping/.test(s), msg: 'EffectComposer var ama ToneMapping yok: renk sıkıştırılmamış, soluk/patlak çıkar. GameStack kullan.' },
  { id: 'math-random', sev: 'P2', test: (s) => /Math\.random\(/.test(s), msg: 'Math.random: tohumsuz, yeniden üretilemez. lib/prng.ts mulberry32 kullan.' },
  { id: 'em-dash', sev: 'P2', test: (s, f) => f.includes('/site/') && /[\u2014]/.test(s), msg: 'Em-dash (—) site metninde: en bilinen AI yazım izi. Cümleyi böl ya da iki nokta/virgül kullan.' },
  { id: 'default-font', sev: 'P1', test: (s) => /font-family:[^;]*\b(Inter|Roboto|Poppins|Open Sans)\b/i.test(s) || /['"](Inter|Roboto|Poppins)['" ]/.test(s), msg: 'Varsayılan yazı tipi (Inter/Roboto/Poppins). theme.ts içinde bilerek seçilmiş bir aile ver.' },
  { id: 'accent-stripe', sev: 'P2', test: (s) => /border-left:\s*\d+px solid var\(--accent\)/.test(s), msg: 'Sol kenar vurgu şeridi: AI kart kalıbı. Üst kural, boşluk ya da tipografiyle hiyerarşi kur.' },
  { id: 'default-standard-only', sev: 'P2', test: (s) => (s.match(/<meshStandardMaterial\b/g)?.length ?? 0) >= 4 && !/useMaterials|createMaterials/.test(s), msg: '4+ satır içi meshStandardMaterial ve kit malzemesi yok: stok görünüm. useMaterials() kullan.' },
]

function* walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) yield* walk(p)
    else if (['.ts', '.tsx', '.jsx', '.js', '.css'].includes(extname(p))) yield p
  }
}

const findings = []
let scanned = 0
for (const file of walk(root)) {
  scanned++
  const src = readFileSync(file, 'utf8')
  for (const r of RULES) {
    if (src.includes(`slop3d-ignore: ${r.id}`)) continue
    if (r.test(src, file)) findings.push({ file, ...r })
  }
}

console.log(`slop3d · ${scanned} dosya tarandı`)
for (const f of findings) console.log(`  ${f.sev} ${f.id}  ${f.file}\n     ${f.msg}`)
console.log(`\n${findings.length} bulgu`)
if (strict && findings.length) process.exit(1)
