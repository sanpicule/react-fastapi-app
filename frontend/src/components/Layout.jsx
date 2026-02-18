import { Sidebar } from './Sidebar';

export function Layout({ children, currentPage }) {
  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950">
      <Sidebar currentPage={currentPage} />
      <div className="flex-1 flex flex-col w-full h-full">
        {children}
      </div>
    </div>
  );
}
