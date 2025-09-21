import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import styles from '../styles/Navbar.module.css';

const Navbar = () => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in on component mount
    checkAuthStatus();
  }, []);

  const checkAuthStatus = () => {
    try {
      const userData = localStorage.getItem('user');
      if (userData) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      localStorage.removeItem('user'); // Clear invalid data
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    // Clear user data from localStorage
    localStorage.removeItem('user');
    setUser(null);
    
    // Redirect to login page
    router.push('/login?message=You have been logged out successfully.');
  };

  const getUserDisplayName = () => {
    if (!user) return '';
    return `${user.first_name} ${user.last_name}`;
  };

  if (isLoading) {
    return (
      <nav className={styles.navbar}>
        <div className={styles.navContainer}>
          <div className={styles.navBrand}>
            <Link href="/" className={styles.brandLink}>
              Carbon Chain
            </Link>
          </div>
          <div className={styles.authPanel}>
            <div className={styles.loadingAuth}>Loading...</div>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className={styles.navbar}>
      <div className={styles.navContainer}>
        {/* Company Brand */}
        <div className={styles.navBrand}>
          <Link href="/" className={styles.brandLink}>
            Carbon Chain
          </Link>
        </div>

        {/* Authentication Panel */}
        <div className={styles.authPanel}>
          {user ? (
            // Logged in state
            <div className={styles.loggedInPanel}>
              <span className={styles.welcomeText}>
                Welcome, {getUserDisplayName()}
              </span>
              <button 
                className={styles.authButton}
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          ) : (
            // Logged out state
            <div className={styles.loggedOutPanel}>
              <Link href="/signup" className={styles.authButton}>
                Sign Up
              </Link>
              <Link href="/login" className={styles.authButton}>
                Login
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
