import { createContext, useState, useEffect } from 'react';
import api from '../api/axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for token on refresh
        const token = localStorage.getItem('access_token');
        if (token) {
            setUser({ loggedIn: true }); // TODO: IMPROVE LATER (STORE MORE INFORMATION ON THE USER)
        }
        setLoading(false);
    }, []);

    const login = async (username, password) => {
        const response = await api.post('auth/login/', { username, password });
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        setUser({ loggedIn: true });
    };

    const logout = async () => {
        try {
            const refresh = localStorage.getItem('refresh_token');
            // Blacklisting refresh token
            await api.post('auth/logout/', { refresh });
        } catch (e) {
            console.error("Logout failed", e);
        } finally {
            localStorage.clear();
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};