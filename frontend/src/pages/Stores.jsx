import React from 'react'
import { motion } from 'framer-motion'
import { Store } from 'lucide-react'
import { STORES_LIST, pageFade } from '../constants'

const Stores = () => (
  <motion.div {...pageFade} className="container" style={{ padding: '6rem 1.5rem' }}>
    <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
      <h1 style={{ fontSize: '3rem' }}>Our Partner <span>Stores 🏪</span></h1>
      <p style={{ color: 'var(--text-muted)' }}>We track 6 of Pakistan's biggest retailers to find you the best deals.</p>
    </div>
    <div className="store-grid">
      {STORES_LIST.map(st => (
        <div key={st.id} className="store-card">
          <div className="store-logo-placeholder">
            <Store size={40} style={{ color: st.color }} />
          </div>
          <h2 style={{ marginBottom: '1rem' }}>{st.name}</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>{st.desc}</p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
             <span style={{ background: '#f8fafc', padding: '0.4rem 1rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>4,000+ Items</span>
             <span style={{ background: '#f8fafc', padding: '0.4rem 1rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>Live Data</span>
          </div>
        </div>
      ))}
    </div>
  </motion.div>
)

export default Stores
