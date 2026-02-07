import { Home, Users, Settings } from 'lucide-react';

export function Sidebar() {
  return (
    <div className="hidden md:flex flex-col w-64 bg-gray-100 dark:bg-gray-800 border-r">
      <div className="flex items-center justify-center h-16 border-b">
        <h1 className="text-xl font-bold">Dashboard</h1>
      </div>
      <nav className="flex-grow p-4">
        <ul>
          <li className="mt-2">
            <a href="#" className="flex items-center p-2 bg-gray-200 dark:bg-gray-700 rounded-lg text-gray-800 dark:text-white font-semibold">
              <Users className="w-5 h-5 mr-3" />
              Users
            </a>
          </li>
        </ul>
      </nav>
    </div>
  );
}
