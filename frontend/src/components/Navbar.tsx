import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/stocks', label: 'Screener' },
  { path: '/portfolio', label: 'Portfolio' },
  { path: '/mutual-funds', label: 'Mutual Funds' },
  { path: '/tax-harvesting', label: 'Tax Harvest' },
]

export default function Navbar() {
  const location = useLocation()
  const logout = useAuthStore((s) => s.logout)
  const user = useAuthStore((s) => s.user)

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-14">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-lg font-bold text-primary-700">Ekphrasis</Link>
            <div className="hidden md:flex space-x-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === item.path
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {user && <span className="text-sm text-gray-500">{user.full_name}</span>}
            <button onClick={logout} className="text-sm text-gray-500 hover:text-gray-700">Logout</button>
          </div>
        </div>
      </div>
    </nav>
  )
}
