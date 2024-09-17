import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Navbar from './components/Navbar'
import Content from './pages/Content'
import Footer from './components/Footer'

function App() {
  // Corrected typing for the sidebar state
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(() => {
    const savedState = localStorage.getItem('isSidebarOpen')
    return savedState ? JSON.parse(savedState) : true
  })

  // Function to toggle sidebar and save state in localStorage
  const toggleSidebar = () => {
    setIsSidebarOpen((prevState: boolean) => {
      const newState = !prevState
      localStorage.setItem('isSidebarOpen', JSON.stringify(newState))
      return newState
    })
  }

  useEffect(() => {
    localStorage.setItem('isSidebarOpen', JSON.stringify(isSidebarOpen))
  }, [isSidebarOpen])

  return (
    <div className="flex flex-col min-h-screen">
      {/* Navbar */}
      <Navbar toggleSidebar={toggleSidebar} />

      <div className="flex flex-1">
        {/* Sidebar */}
        <div>
        <Sidebar isSidebarOpen={isSidebarOpen} />
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 bg-gray-100">
          <Content />
        </div>
      </div>

      {/* Footer */}
      <div className="">
        <Footer />
      </div>
    </div>
  )
}

export default App
