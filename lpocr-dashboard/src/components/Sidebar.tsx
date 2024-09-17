import { BarChart, Users, FileText, Settings } from 'lucide-react'

interface SidebarProps {
  isSidebarOpen: boolean;
}


export default function Sidebar({ isSidebarOpen } :SidebarProps) {
  const sidebarItems = [
    { icon: BarChart, label: 'Dashboard' },
    { icon: Users, label: 'Users' },
    { icon: FileText, label: 'Reports' },
    { icon: Settings, label: 'Settings' },
  ]

  return (
    <aside
      className={`h-screen bg-white-800 text-black flex flex-col transition-all duration-300 
        ${isSidebarOpen ? 'w-64' : 'w-16'}`}
    >
      <nav className="mt-8 flex-1">
        {sidebarItems.map((item, index) => (
          <a
            key={index}
            href="#"
            className="flex items-center px-6 py-3 hover:bg-zinc-400 transition-colors duration-200"
          >
            <item.icon className="w-6 h-6" />
            {isSidebarOpen && <span className="ml-4">{item.label}</span>}
          </a>
        ))}
      </nav>
    </aside>
  )
}
