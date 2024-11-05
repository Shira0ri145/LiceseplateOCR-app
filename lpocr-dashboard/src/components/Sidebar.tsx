import { BarChart, Users, FileText, CarFront } from 'lucide-react';
import { Link } from 'react-router-dom';

interface SidebarProps {
  isSidebarOpen: boolean;
}

export default function Sidebar({ isSidebarOpen }: SidebarProps) {
  // ตรวจสอบสถานะการล็อกอิน
  const isLoggedIn = !!localStorage.getItem('access_token');

  // กำหนดรายการ Sidebar ที่แตกต่างกันไปตามสถานะการล็อกอิน
  const sidebarItems = [
    { icon: BarChart, label: 'Predict Camera', path: '/' },
    { icon: CarFront, label: 'Predict File', path: '/file-predict' },
    ...(isLoggedIn
      ? [
          { icon: FileText, label: 'Upload History', path: '/history' },
          { icon: Users, label: 'Profile', path: '/profile' },
        ]
      : []), // ไม่แสดงเมื่อไม่ได้ล็อกอิน
  ];

  return (
    <aside
      className={`h-screen bg-white-800 text-black flex flex-col transition-all duration-300 
        ${isSidebarOpen ? 'w-64' : 'w-16'}`}
    >
      <nav className="mt-8 flex-1">
        {sidebarItems.map((item, index) => (
          <Link
            key={index}
            to={item.path}
            className="flex items-center px-6 py-3 hover:bg-zinc-400 transition-colors duration-200"
          >
            <item.icon className="w-6 h-6" />
            {isSidebarOpen && <span className="ml-4">{item.label}</span>}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
