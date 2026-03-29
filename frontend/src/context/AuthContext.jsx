import { useState } from 'react';
import { apiFetch } from '@/lib/api';
import { AuthContext } from './auth-context';

const TOKEN_STORAGE_KEY = 'auth.token';
const USER_STORAGE_KEY = 'auth.user';

function loadStoredValue(key) {
  if (typeof window === 'undefined') {
    return null;
  }

  return window.localStorage.getItem(key);
}

function loadStoredUser() {
  const rawUser = loadStoredValue(USER_STORAGE_KEY);
  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser);
  } catch {
    window.localStorage.removeItem(USER_STORAGE_KEY);
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => loadStoredValue(TOKEN_STORAGE_KEY));
  const [user, setUser] = useState(() => loadStoredUser());

  const login = async ({ email, password }) => {
    const result = await apiFetch('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    window.localStorage.setItem(TOKEN_STORAGE_KEY, result.access_token);
    window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(result.user));
    setToken(result.access_token);
    setUser(result.user);

    return result.user;
  };

  const logout = () => {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    window.localStorage.removeItem(USER_STORAGE_KEY);
    setToken(null);
    setUser(null);
  };

  const hasRole = (role) => Boolean(user?.roles?.includes(role));

  const value = {
    token,
    user,
    isAuthenticated: Boolean(token && user),
    login,
    logout,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
