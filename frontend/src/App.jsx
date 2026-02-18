import { useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { AuditLogs } from './components/AuditLogs';
import { Layout } from './components/Layout';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('users');

  // ハッシュ変更を監視
  useState(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.substring(1);
      setCurrentPage(hash || 'users');
    };

    window.addEventListener('hashchange', handleHashChange);
    handleHashChange(); // 初期読み込み時

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  return (
    <Layout currentPage={currentPage}>
      {currentPage === 'users' && <Dashboard />}
      {currentPage === 'audit-logs' && <AuditLogs />}
    </Layout>
  );
}

export default App;
