import React from 'react'
import { Link } from 'react-router-dom'
import { Zap } from 'lucide-react'

const Footer = () => (
  <footer className="main-footer">
    <div className="container">
      <div className="brand" style={{ marginBottom: '1.5rem', justifyContent: 'center' }}>
        <Zap size={28} fill="var(--primary)" />
        <span>PricePulse PK</span>
      </div>
      <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Feel the Pulse of Grocery Prices Across Pakistan 🇵🇰</p>
      <div className="footer-nav" style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginBottom: '2rem' }}>
        <Link to="/">Explore</Link>
        <Link to="/stores">Retailers</Link>
        <Link to="/insights">How it Works</Link>
        <Link to="/contact">Support</Link>
      </div>
      <div style={{ padding: '2rem 0', borderTop: '1px solid #f0fdf4', fontSize: '0.875rem' }}>
        © 2026 PricePulse Pakistan. Built for the modern Pakistani shopper. 🛒✨
      </div>
    </div>
  </footer>
)

export default Footer
