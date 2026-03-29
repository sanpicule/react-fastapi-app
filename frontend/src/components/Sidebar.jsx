import { FileText, LogOut, Users } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

export function Sidebar({ currentPage, onLogout, user }) {
  const [showConfirm, setShowConfirm] = useState(false);

  const menuItems = [
    { id: 'users', label: 'ユーザー', icon: Users, href: '#users' },
    ...(user?.roles?.includes('admin')
      ? [{ id: 'audit-logs', label: '監査ログ', icon: FileText, href: '#audit-logs' }]
      : []),
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
      <div className="border-t p-4 space-y-3">
        <div>
          <div className="text-sm font-medium text-gray-900 dark:text-white">{user?.name}</div>
          <div className="text-xs text-gray-500 dark:text-gray-300">{user?.email}</div>
        </div>
        <Button className="w-full" onClick={() => setShowConfirm(true)} type="button" variant="outline">
          <LogOut className="h-4 w-4" />
          ログアウト
        </Button>
      </div>

      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6 w-80 flex flex-col items-center gap-4">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              ログアウトしてもよろしいですか？
            </p>
            <div className="flex justify-center gap-2">
              <Button variant="outline" onClick={() => setShowConfirm(false)}>
                キャンセル
              </Button>
              <Button variant="destructive" onClick={() => { setShowConfirm(false); onLogout(); }}>
                ログアウト
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
