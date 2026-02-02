import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Award } from 'lucide-react'
import { API_BASE_URL, pageFade, stagger } from '../constants'

const Home = () => {
  const [query, setQuery] = useState(() => sessionStorage.getItem('pp_query') || '')
  const [results, setResults] = useState(() => {
    const saved = sessionStorage.getItem('pp_results')
    return saved ? JSON.parse(saved) : []
  })
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query) return
    setLoading(true)
    try {
      const { data } = await axios.get(`${API_BASE_URL}/search?query=${query}`)
      setResults(data)
      sessionStorage.setItem('pp_results', JSON.stringify(data))
      sessionStorage.setItem('pp_query', query)
    } catch (err) { console.error(err) }
    setLoading(false)
  }

  return (
    <motion.div {...pageFade} className="main-content">
      <section className="hero-section">
        <div className="container">
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.6 }}>
            <h1>Compare Grocery Prices <span>Instantly 🛒</span></h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '1.25rem', maxWidth: '700px', margin: '0 auto 3rem' }}>
              Find the pulse of 1,000+ products across Pakistan's top retailers in seconds.
            </p>
          </motion.div>
          
          <form className="search-wrapper" onSubmit={handleSearch}>
            <Search className="search-icon" style={{ color: '#94a3b8' }} />
            <input 
              type="text" 
              placeholder="Search (e.g. Milk, Coke, Shampoo)..." 
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
            <button type="submit" className="search-btn">Compare 🚀</button>
          </form>

          <div style={{ marginTop: '4rem', display: 'flex', justifyContent: 'center', gap: '4rem' }}>
            <div className="stat-box">
              <h3 style={{ fontSize: '2rem', color: 'var(--primary)' }}>6</h3>
              <p style={{ fontSize: '0.8rem', fontWeight: 700 }}>Stores</p>
            </div>
            <div className="stat-box">
              <h3 style={{ fontSize: '2rem', color: 'var(--secondary)' }}>47K+</h3>
              <p style={{ fontSize: '0.8rem', fontWeight: 700 }}>Products</p>
            </div>
            <div className="stat-box">
              <h3 style={{ fontSize: '2rem', color: 'var(--accent)' }}>Live</h3>
              <p style={{ fontSize: '0.8rem', fontWeight: 700 }}>Pulse</p>
            </div>
          </div>
        </div>
      </section>

      <div className="container" style={{ paddingBottom: '6rem' }}>
        {results.length > 0 && (
          <div className="results-header" style={{ marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '1.8rem' }}>🔥 Pulse Results ({results.length})</h2>
          </div>
        )}

        <AnimatePresence mode="wait">
          {loading ? (
            <div className="results-grid">
              {[1,2,3,4,5,6].map(i => (
                <div key={i} className="product-card shimmer" style={{ height: '400px', border: 'none' }} />
              ))}
            </div>
          ) : (
            <motion.div variants={stagger} initial="initial" animate="animate" className="results-grid">
              {results.map((product) => (
                <motion.div 
                  key={product.id} 
                  className="product-card"
                  variants={{ initial: { opacity: 0, scale: 0.9 }, animate: { opacity: 1, scale: 1 } }}
                  onClick={() => navigate(`/product/${product.id}`, { state: { product } })}
                >
                  {product.all_prices?.length > 1 && (
                    <div className="savings-badge">Save Rs. {(Math.max(...product.all_prices.map(p => p.price)) - Math.min(...product.all_prices.map(p => p.price))).toLocaleString()} 💰</div>
                  )}
                  <div className="product-image-box">
                    <img src={product.image_url} alt="" onError={e => e.target.src = 'https://via.placeholder.com/400x400?text=PricePulse'} />
                  </div>
                  <div className="card-info">
                    <div className="brand-tag">{product.brand || 'Local Brand'}</div>
                    <div className="product-title">{product.name}</div>
                    <div className="price-pulse">
                      {product.all_prices?.slice(0, 3).map((st, i) => (
                        <div key={i} className={`pulse-row ${i === 0 ? 'cheapest' : ''}`}>
                          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            {i === 0 && <Award size={14} />} {st.store_name}
                          </span>
                          <span>Rs. {st.price.toLocaleString()}</span>
                        </div>
                      ))}
                      {product.all_prices?.length > 3 && (
                        <div style={{ textAlign: 'center', color: 'var(--primary)', fontSize: '0.75rem', marginTop: '0.5rem', fontWeight: 700 }}>
                          +{product.all_prices.length - 3} more stores...
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

export default Home
