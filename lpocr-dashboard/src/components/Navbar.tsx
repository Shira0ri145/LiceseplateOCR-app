import { useState, useEffect } from 'react';
import { LogOut, Menu } from 'lucide-react';
import Swal from 'sweetalert2';
import axios from 'axios';
import { Link } from 'react-router-dom';

interface NavbarProps {
  toggleSidebar: () => void;
}

export default function Navbar({ toggleSidebar }: NavbarProps) {
  const [isHamburgerActive, setIsHamburgerActive] = useState<boolean>(() => {
    const savedState = localStorage.getItem('isHamburgerActive');
    return savedState ? JSON.parse(savedState) : false;
  });

  const handleHamburgerClick = () => {
    const newState = !isHamburgerActive;
    setIsHamburgerActive(newState);
    toggleSidebar();
    localStorage.setItem('isHamburgerActive', JSON.stringify(newState));
  };

  // Sync localStorage with the state when component mounts
  useEffect(() => {
    localStorage.setItem('isHamburgerActive', JSON.stringify(isHamburgerActive));
  }, [isHamburgerActive]);

  // Function to handle logout
  const handleLogout = async () => {
    const result = await Swal.fire({
      title: 'Are you sure?',
      text: 'You will be logged out!',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Yes, log me out!',
    });

    if (result.isConfirmed) {
      try {
        const response = await axios.get('http://localhost:8000/api/auth/logout', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        });

        // Show success message
        Swal.fire({
          title: 'Logged Out!',
          text: response.data.message, 
          icon: 'success',
          confirmButtonText: 'OK',
        }).then(() => {
          localStorage.removeItem('access_token'); 
          window.location.href = '/'; 
        });
      } catch (error) {
        Swal.fire({
          title: 'Error!',
          text: 'Failed to log out. Please try again.',
          icon: 'error',
          confirmButtonText: 'OK',
        });
      }
    }
  };

  const isLoggedIn = !!localStorage.getItem('access_token');

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

    
        <h2 className="text-2xl font-semibold mr-8">OCR Dashboard</h2>

        
      </div>
      
      <div className="flex items-center space-x-4">
    
        {isLoggedIn ? (
          <button onClick={handleLogout}>
            <LogOut className="w-6 h-6 text-gray-600 cursor-pointer hover:text-gray-900" />
          </button>
        ) : (
          <Link to="/login">
            <button className="bg-gray-200 text-black px-4 py-2 rounded hover:bg-gray-300 transition duration-300">
              Sign-in
            </button>
          </Link>
        )}
      </div>
    </nav>
  );
}