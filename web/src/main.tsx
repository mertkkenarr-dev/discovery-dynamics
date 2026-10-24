import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './App'
import './site/theme'
import './galaksi.css'

const kok = document.getElementById('kok')
if (!kok) throw new Error('#kok bulunamadı')
createRoot(kok).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
