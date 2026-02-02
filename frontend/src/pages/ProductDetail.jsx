import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, TrendingDown } from 'lucide-react'
import { API_BASE_URL, pageFade } from '../constants'

const ProductDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [product, setProduct] = useState(location.state?.product || null)
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(!product)

  useEffect(() => {
    const fetch = async () => {
      if (!product) {
        try {
          const { data } = await axios.get(`${API_BASE_URL}/product/${id}`)
          setProduct(data)
        } catch (e) { console.error(e) }
      }
      try {
        const { data } = await axios.get(`${API_BASE_URL}/recommend/${id}`)
        setRecs(data)
      } catch (e) { console.error(e) }
      setLoading(false)
    }
    fetch()
  }, [id])

  if (loading) return <div className="container" style={{ padding: '10rem 0', textAlign: 'center' }}>Feeling the pulse...</div>
  if (!product) return <div className="container">No Pulse Found.</div>

  const prices = [...(product.all_prices || [])].sort((a,b) => a.price - b.price)

  return (
    <motion.div {...pageFade} className="container" style={{ padding: '4rem 1.5rem' }}>
      <button className="back-btn" onClick={() => navigate(-1)} style={{ background: 'white', padding: '0.75rem 1.5rem', borderRadius: '30px', boxShadow: 'var(--shadow-sm)', marginBottom: '3rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <ArrowLeft size={18} /> Back to Search
      </button>

      <div className="detail-layout" style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '4rem' }}>
        <div style={{ background: 'white', borderRadius: '32px', padding: '3rem', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: 'var(--shadow-md)' }}>
          <img src={product.image_url} style={{ width: '100%', maxHeight: '450px', objectFit: 'contain' }} alt="" />
        </div>

        <div>
          <span style={{ color: 'var(--primary)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em' }}>{product.brand}</span>
          <h1 style={{ fontSize: '3rem', margin: '0.5rem 0 1.5rem' }}>{product.name}</h1>
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '3rem' }}>
            <span style={{ background: '#f0fdf4', padding: '0.5rem 1rem', borderRadius: '20px', fontSize: '0.85rem', fontWeight: 700 }}>{product.category}</span>
            <span style={{ background: '#f0fdf4', padding: '0.5rem 1rem', borderRadius: '20px', fontSize: '0.85rem', fontWeight: 700 }}>{product.quantity} {product.unit}</span>
          </div>

          <div style={{ background: 'white', borderRadius: '24px', padding: '2rem', boxShadow: 'var(--shadow-md)', border: '1px solid #f0fdf4' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
              <TrendingDown color="var(--primary)" /> Store Comparison
            </h3>
            {prices.map((st, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '1.25rem 0', borderBottom: i < prices.length -1 ? '1px solid #f1f5f9' : 'none', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>{st.store_name}</div>
                  {i === 0 && <span style={{ fontSize: '0.7rem', color: 'var(--primary)', fontWeight: 800 }}>⭐ BEST VALUE</span>}
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>Rs. {st.price.toLocaleString()}</div>
                  <a href={st.url} target="_blank" style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 700, textDecoration: 'underline' }}>Visit Store</a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <section style={{ marginTop: '6rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '2rem' }}>Smart Recommendations 🤖</h2>
        <div className="results-grid">
          {recs.map(rec => (
            <div key={rec.id} className="product-card" onClick={() => navigate(`/product/${rec.id}`, { state: { product: rec } })}>
              <div className="product-image-box" style={{ height: '180px' }}>
                <img src={rec.image_url} alt="" />
              </div>
              <div className="card-info">
                <div className="product-title" style={{ height: '3rem' }}>{rec.name}</div>
                <div style={{ fontWeight: 800, color: 'var(--primary)', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Rs. {rec.price}</span>
                  <span style={{ color: 'var(--accent)', fontSize: '0.7rem' }}>{rec.recommendation_reasons?.split('|')[0]}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </motion.div>
  )
}

export default ProductDetail
