import { Home, Users, Settings, FileText } from 'lucide-react';

export function Sidebar({ currentPage }) {
  const menuItems = [
    { id: 'users', label: 'ユーザー', icon: Users, href: '#users' },
    { id: 'audit-logs', label: '監査ログ', icon: FileText, href: '#audit-logs' },
  ];

  return (
    <div className="hidden md:flex flex-col w-64 bg-gray-100 dark:bg-gray-800 border-r">
      <div className="flex items-center justify-center h-16 border-b">
        <h1 className="text-xl font-bold">Dashboard</h1>
      </div>
      <nav className="flex-grow p-4">
        <ul>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <li key={item.id} className="mt-2">
                <a
                  href={item.href}
                  className={`flex items-center p-2 rounded-lg text-gray-800 dark:text-white ${
                    isActive
                      ? 'bg-gray-200 dark:bg-gray-700 font-semibold'
                      : 'hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {item.label}
                </a>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}
