import { Sidebar } from './Sidebar';

export function Layout({ children }) {
  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 flex flex-col w-full h-full">
        {children}
      </div>
    </div>
  );
}
