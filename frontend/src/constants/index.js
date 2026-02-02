export const API_BASE_URL = 'http://localhost:8000'

export const STORES_LIST = [
  { id: 1, name: 'Jalal Sons', color: '#bf1e2e', desc: 'Premium quality groceries across Lahore.' },
  { id: 2, name: 'Metro Pakistan', color: '#003a70', desc: 'Wholesale prices for everyone.' },
  { id: 3, name: 'Al-Fatah', color: '#81bc06', desc: 'Premium shopping experience.' },
  { id: 4, name: 'GrocerApp', color: '#f48020', desc: 'Fresh groceries delivered to your doorstep.' },
  { id: 5, name: 'Rahim Store', color: '#059669', desc: 'Reliable grocery shopping since decades.' },
  { id: 6, name: 'Green Valley', color: '#0d9488', desc: 'Hypermarket with global standards.' }
]

export const pageFade = {
  initial: { opacity: 0, y: 15 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -15 },
  transition: { duration: 0.4, ease: "easeOut" }
}

export const stagger = {
  initial: {},
  animate: { transition: { staggerChildren: 0.05 } }
}
