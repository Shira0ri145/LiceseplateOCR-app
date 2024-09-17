import { useState, useEffect } from 'react'
import { Search, LogOut, Menu } from 'lucide-react'
import { Link } from 'react-router-dom';

interface NavbarProps {
  toggleSidebar: () => void;
}

export default function Navbar({ toggleSidebar }: NavbarProps) {
  // Get initial state from localStorage or default to false
  const [isHamburgerActive, setIsHamburgerActive] = useState<boolean>(() => {
    const savedState = localStorage.getItem('isHamburgerActive')
    return savedState ? JSON.parse(savedState) : false
  })

  const handleHamburgerClick = () => {
    const newState = !isHamburgerActive
    setIsHamburgerActive(newState)
    toggleSidebar()
    // Save the active state in localStorage
    localStorage.setItem('isHamburgerActive', JSON.stringify(newState))
  }

  // Sync localStorage with the state when component mounts
  useEffect(() => {
    localStorage.setItem('isHamburgerActive', JSON.stringify(isHamburgerActive))
  }, [isHamburgerActive])

  return (
    <nav className="flex items-center justify-between bg-white shadow p-4">
      <div className="flex items-center">
        {/* Hamburger Button */}
        <button
          onClick={handleHamburgerClick}
          className={`p-2 mr-4 rounded transition-colors duration-300 ${
            isHamburgerActive ? 'bg-black text-white' : 'text-black hover:bg-gray-200'
          }`}
        >
          <Menu className="w-6 h-6" />
        </button>

        {/* OCR Dashboard Title */}
        <h2 className="text-2xl font-semibold mr-8">OCR Dashboard</h2>

        {/* Search Bar */}
        <div className="relative">
          <input 
            type="text" 
            placeholder="Search..." 
            className="p-2 pl-10 bg-gray-100 rounded-md border border-gray-300 w-64"
          />
          <Search className="absolute left-2 top-2 text-gray-400 w-5 h-5" />
        </div>
      </div>

      {/* Logout Button */}
      <Link to="/login">
        <LogOut className="w-6 h-6 text-gray-600 cursor-pointer hover:text-gray-900" />
      </Link>
    </nav>
  )
}
