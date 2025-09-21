import Link from 'next/link';
import Image from 'next/image';
import Button from './button.jsx';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function MenuBar() {
  const [isLogoHovered, setIsLogoHovered] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  // Check authentication status on component mount
  useEffect(() => {
    try {
      const userData = localStorage.getItem('user');
      if (userData) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setIsLoggedIn(true);
      } else {
        setIsLoggedIn(false);
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      setIsLoggedIn(false);
    }
  }, []);

  // Handle logout
  const handleLogout = () => {
    try {
      // Clear user data from localStorage
      localStorage.removeItem('user');
      setUser(null);
      setIsLoggedIn(false);
      
      // Redirect to home page
      router.push('/');
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  const menuBarStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    height: '60px',
    background: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 40px',
    zIndex: 1000,
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    backdropFilter: 'blur(10px)'
  };

  const logoStyle = {
    display: 'flex',
    alignItems: 'center',
    textDecoration: 'none',
    transition: 'opacity 0.3s ease'
  };

  const navLinksStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '30px'
  };

  const menuItemStyle = {
    color: 'var(--textcolor)',
    textDecoration: 'none',
    fontSize: '1rem',
    fontWeight: '500',
    padding: '8px 16px',
    borderRadius: '20px',
    transition: 'all 0.3s ease',
    border: '1px solid transparent'
  };

  const buttonStyle = {
    ...menuItemStyle,
    background: 'var(--maincolor)',
    color: 'white',
    fontWeight: '600'
  };

  return (
    <div style={menuBarStyle}>
      {/* Logo */}
      <Link 
        href="/" 
        style={logoStyle}
        onMouseEnter={(e) => {
          e.currentTarget.style.opacity = '0.8';
          setIsLogoHovered(true);
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.opacity = '1';
          setIsLogoHovered(false);
        }}
      >
        <Image 
          src={isLogoHovered ? "/assets/logo-highlight.svg" : "/assets/horizontal-logo.svg"}
          alt="CarbonChain Logo"
          width={200}
          height={50}
        />
      </Link>

      {/* Navigation Links */}
      <div style={navLinksStyle}>
        <Link 
          href="/search" 
          style={menuItemStyle}
          onMouseEnter={(e) => {
            e.target.style.background = 'rgba(0,0,0,0.1)';
            e.target.style.borderColor = 'rgba(0,0,0,0.3)';
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'transparent';
            e.target.style.borderColor = 'transparent';
          }}
        >
            Search Projects
        </Link>
        
        <Link 
          href="/funding-network"
          style={menuItemStyle}
          onMouseEnter={(e) => {
            e.target.style.background = 'rgba(0,0,0,0.1)';
            e.target.style.borderColor = 'rgba(0,0,0,0.3)';
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'transparent';
            e.target.style.borderColor = 'transparent';
          }}
        >
          View Network
        </Link>

        <Link
          href="/learn-more"
          style={menuItemStyle}
          onMouseEnter={(e) => {
            e.target.style.background = 'rgba(0,0,0,0.1)';
            e.target.style.borderColor = 'rgba(0,0,0,0.3)';
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'transparent';
            e.target.style.borderColor = 'transparent';
          }}
        >
          About Us
        </Link>

        {isLoggedIn ? (
          <Button text="Logout" onClick={handleLogout} />
        ) : (
          <Button text="Login" link="/login" />
        )}
      </div>
    </div>
  );
}