import React from 'react'
import { motion } from 'framer-motion'
import { Mail } from 'lucide-react'
import { pageFade } from '../constants'

const Contact = () => (
  <motion.div {...pageFade} className="container" style={{ padding: '6rem 1.5rem', maxWidth: '800px' }}>
    <div style={{ background: 'white', padding: '4rem', borderRadius: '40px', boxShadow: 'var(--shadow-md)', textAlign: 'center' }}>
      <Mail size={60} color="var(--primary)" style={{ marginBottom: '2rem' }} />
      <h1>Get in <span>Touch ✉️</span></h1>
      <p style={{ marginBottom: '3rem' }}>Have a suggestion or want to list your store? Drop us a line!</p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', textAlign: 'left' }}>
        <div>
          <label style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.5rem', display: 'block' }}>Name</label>
          <input type="text" placeholder="Your Name" style={{ width: '100%', padding: '1rem 1.5rem', borderRadius: '16px', border: '1px solid #e2e8f0', outline: 'none' }} />
        </div>
        <div>
          <label style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.5rem', display: 'block' }}>Email</label>
          <input type="email" placeholder="hello@pulse.pk" style={{ width: '100%', padding: '1rem 1.5rem', borderRadius: '16px', border: '1px solid #e2e8f0', outline: 'none' }} />
        </div>
        <div>
          <label style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.5rem', display: 'block' }}>Message</label>
          <textarea placeholder="Type your pulse..." rows="4" style={{ width: '100%', padding: '1rem 1.5rem', borderRadius: '16px', border: '1px solid #e2e8f0', outline: 'none', resize: 'none' }} />
        </div>
        <button className="search-btn" style={{ width: '100%', justifyContent: 'center', marginTop: '1rem' }}>Send Message ✨</button>
      </div>
    </div>
  </motion.div>
)

export default Contact
