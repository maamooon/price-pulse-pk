import React from 'react'
import { motion } from 'framer-motion'
import { BarChart3, Award, Clock } from 'lucide-react'
import { pageFade } from '../constants'

const Insights = () => (
  <motion.div {...pageFade} className="container" style={{ padding: '6rem 1.5rem' }}>
    <div style={{ textAlign: 'center', marginBottom: '5rem' }}>
      <h1>Smart <span>Insights 🤖</span></h1>
      <p>How we help you save thousands on every grocery run.</p>
    </div>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '3rem' }}>
      <div style={{ background: 'white', padding: '3rem', borderRadius: '32px', boxShadow: 'var(--shadow-md)' }}>
        <div style={{ color: 'var(--primary)', marginBottom: '1.5rem' }}><BarChart3 size={48} /></div>
        <h3>Fuzzy Grouping</h3>
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Our algorithm intelligently identifies the same product even if different stores use different names or spellings.</p>
      </div>
      <div style={{ background: 'white', padding: '3rem', borderRadius: '32px', boxShadow: 'var(--shadow-md)' }}>
        <div style={{ color: 'var(--secondary)', marginBottom: '1.5rem' }}><Award size={48} /></div>
        <h3>Best Value Ranking</h3>
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>We don't just show prices; we rank them based on unit costs to ensure you truly get the most for your money.</p>
      </div>
      <div style={{ background: 'white', padding: '3rem', borderRadius: '32px', boxShadow: 'var(--shadow-md)' }}>
        <div style={{ color: 'var(--accent)', marginBottom: '1.5rem' }}><Clock size={48} /></div>
        <h3>Real-time Pulse</h3>
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Our scrapers work around the clock to ensure the pulse you see reflects the exact shelf price right now.</p>
      </div>
    </div>
  </motion.div>
)

export default Insights
