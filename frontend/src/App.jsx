import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'

// Components
import Navbar from './components/Navbar'
import Footer from './components/Footer'

// Pages
import Home from './pages/Home'
import ProductDetail from './pages/ProductDetail'
import Stores from './pages/Stores'
import Insights from './pages/Insights'
import Contact from './pages/Contact'

// Styles
import './App.css'

// Helper to scroll to top on route change
function ScrollToTop() {
  const location = useLocation()
  useEffect(() => {
    window.scrollTo(1, 1);
    window.scrollTo(0, 0);
  }, [location.key])
  return null
}

// Helper to update document title dynamically
function DynamicTitle() {
  const location = useLocation()
  
  useEffect(() => {
    const path = location.pathname
    let title = 'PricePulse PK'
    
    if (path === '/') title = 'Compare Grocery Prices | PricePulse PK'
    else if (path === '/stores') title = 'Our Partner Stores | PricePulse PK'
    else if (path === '/insights') title = 'Smart Grocery Insights | PricePulse PK'
    else if (path === '/contact') title = 'Contact Us | PricePulse PK'
    else if (path.startsWith('/product/')) {
      const productName = location.state?.product?.name || 'Product Detail'
      title = `${productName} | PricePulse PK`
    }
    
    document.title = title
  }, [location])

  return null
}

function App() {
  return (
    <Router>
      <ScrollToTop />
      <DynamicTitle />
      <div className="app-layout">
        <Navbar />
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/product/:id" element={<ProductDetail />} />
            <Route path="/stores" element={<Stores />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/contact" element={<Contact />} />
          </Routes>
        </AnimatePresence>
        <Footer />
      </div>
    </Router>
  )
}

export default App
