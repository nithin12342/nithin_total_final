import { useState, useContext, createContext } from 'react';

const authContext = createContext();

export function AuthProvider({ children }) {
  const auth = useProvideAuth();
  return <authContext.Provider value={auth}>{children}</authContext.Provider>;
}

export const useAuth = () => {
  return useContext(authContext);
};

function useProvideAuth() {
  const [user, setUser] = useState(null);

  const login = (credentials) => {
    // For now, we'll just simulate a login
    return new Promise((resolve) => {
      setTimeout(() => {
        setUser({ email: credentials.email });
        resolve();
      }, 1000);
    });
  };

  const logout = () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        setUser(null);
        resolve();
      }, 500);
    });
  };

  return {
    user,
    login,
    logout,
  };
}
