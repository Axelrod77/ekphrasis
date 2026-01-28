import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import StockScreener from './pages/StockScreener'
import StockDetail from './pages/StockDetail'
import Portfolio from './pages/Portfolio'
import MutualFunds from './pages/MutualFunds'
import TaxHarvesting from './pages/TaxHarvesting'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token)
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="stocks" element={<StockScreener />} />
          <Route path="stocks/:symbol" element={<StockDetail />} />
          <Route path="portfolio" element={<Portfolio />} />
          <Route path="mutual-funds" element={<MutualFunds />} />
          <Route path="tax-harvesting" element={<TaxHarvesting />} />
        </Route>
      </Routes>
    </>
  )
}
