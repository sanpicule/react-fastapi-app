import { useEffect, useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { AuditLogs } from './components/AuditLogs';
import { Layout } from './components/Layout';
import { LoginPage } from './components/LoginPage';
import { useAuth } from './hooks/useAuth';
import './App.css';

function App() {
  const { hasRole, isAuthenticated, logout, user } = useAuth();
  const [currentPage, setCurrentPage] = useState('users');
  const canViewAuditLogs = hasRole('admin');

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.substring(1);
      if (!hash || hash === 'login') {
        setCurrentPage('users');
        return;
      }
      if (hash === 'audit-logs' && !canViewAuditLogs) {
        setCurrentPage('users');
        window.location.hash = 'users';
        return;
      }
      setCurrentPage(hash);
    };

    window.addEventListener('hashchange', handleHashChange);
    handleHashChange();

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [canViewAuditLogs]);

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const handleLogout = () => {
    logout();
    window.location.hash = 'login';
  };

  return (
    <Layout currentPage={currentPage} onLogout={handleLogout} user={user}>
      {currentPage === 'users' && <Dashboard />}
      {currentPage === 'audit-logs' && canViewAuditLogs && <AuditLogs />}
    </Layout>
  );
}

export default App;
