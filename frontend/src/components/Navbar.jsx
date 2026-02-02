import React from 'react'
import { Link, NavLink } from 'react-router-dom'
import { Zap } from 'lucide-react'

const Navbar = () => (
  <header className="main-header">
    <div className="container nav-content">
      <Link to="/" className="brand">
        <Zap size={32} fill="var(--primary)" />
        <span>PricePulse PK</span>
      </Link>
      <nav className="nav-links">
        <NavLink to="/" end>Home</NavLink>
        <NavLink to="/stores">Stores</NavLink>
        <NavLink to="/insights">Insights</NavLink>
        <NavLink to="/contact">Contact</NavLink>
      </nav>
      <div className="nav-actions">
        <button className="search-btn" style={{ padding: '0.6rem 1.5rem', height: '48px', fontSize: '0.9rem' }}>
          Compare Now
        </button>
      </div>
    </div>
  </header>
)

export default Navbar
