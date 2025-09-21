import { useState } from 'react';
import Link from 'next/link';

export default function MenuButton() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const menuButtonStyle = {
    position: 'fixed',
    top: '20px',
    right: '20px',
    width: '50px',
    height: '50px',
    background: 'white',
    borderRadius: '8px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    transition: 'all 0.3s ease'
  };

  const hamburgerStyle = {
    display: 'flex',
    flexDirection: 'column',
    width: '20px',
    height: '15px',
    justifyContent: 'space-between'
  };

  const hamburgerLineStyle = {
    width: '100%',
    height: '2px',
    background: 'var(--maincolor)',
    borderRadius: '1px',
    transition: 'all 0.3s ease'
  };

  const slideMenuStyle = {
    position: 'fixed',
    top: 0,
    right: isMenuOpen ? '0' : '-300px',
    width: '300px',
    height: '100vh',
    background: 'white',
    boxShadow: '-2px 0 10px rgba(0,0,0,0.1)',
    zIndex: 999,
    transition: 'right 0.3s ease',
    borderLeft: '1px solid #e0e0e0'
  };

  const menuHeaderStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px',
    borderBottom: '1px solid #e0e0e0',
    background: 'var(--maincolor)',
    color: 'white'
  };

  const closeButtonStyle = {
    background: 'none',
    border: 'none',
    color: 'white',
    fontSize: '24px',
    cursor: 'pointer',
    width: '30px',
    height: '30px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '50%',
    transition: 'background 0.2s ease'
  };

  const menuContentStyle = {
    padding: '20px 0'
  };

  const menuItemStyle = {
    display: 'block',
    padding: '15px 20px',
    textDecoration: 'none',
    color: '#333',
    borderBottom: '1px solid #f0f0f0',
    transition: 'background 0.2s ease'
  };

  const overlayStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    background: 'rgba(0,0,0,0.5)',
    zIndex: 998
  };

  return (
    <>
      {/* Menu Button */}
      <div 
        style={menuButtonStyle} 
        onClick={toggleMenu}
        onMouseEnter={(e) => {
          e.target.style.background = '#f0fffbff';
          e.target.style.transform = 'scale(1.05)';
        }}
        onMouseLeave={(e) => {
          e.target.style.background = 'white';
          e.target.style.transform = 'scale(1)';
        }}
      >
        <div style={hamburgerStyle}>
          <span style={hamburgerLineStyle}></span>
          <span style={hamburgerLineStyle}></span>
          <span style={hamburgerLineStyle}></span>
        </div>
      </div>

      {/* Sliding Menu */}
      <div style={slideMenuStyle}>
        <div style={menuHeaderStyle}>
          <h3 style={{ margin: 0, fontSize: '1.2rem' }}>Menu</h3>
          <button 
            style={closeButtonStyle} 
            onClick={toggleMenu}
            onMouseEnter={(e) => e.target.style.background = 'rgba(255,255,255,0.2)'}
            onMouseLeave={(e) => e.target.style.background = 'none'}
          >
            ×
          </button>
        </div>
        <div style={menuContentStyle}>
          <Link 
            href="/" 
            style={menuItemStyle}
            onMouseEnter={(e) => {
              e.target.style.background = '#f8f9fa';
              e.target.style.color = '#4CAF50';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'transparent';
              e.target.style.color = '#333';
            }}
          >
            <span>🏠 Home</span>
          </Link>
          <Link 
            href="/search" 
            style={menuItemStyle}
            onMouseEnter={(e) => {
              e.target.style.background = '#f8f9fa';
              e.target.style.color = '#4CAF50';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'transparent';
              e.target.style.color = '#333';
            }}
          >
            <span>🔍 Search Projects</span>
          </Link>
          <Link 
            href="/projects" 
            style={menuItemStyle}
            onMouseEnter={(e) => {
              e.target.style.background = '#f8f9fa';
              e.target.style.color = 'var(--maincolor)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'transparent';
              e.target.style.color = '#333';
            }}
          >
            <span>📊 Browse Projects</span>
          </Link>
          <Link 
            href="/supply-projects" 
            style={menuItemStyle}
            onMouseEnter={(e) => {
              e.target.style.background = '#f8f9fa';
              e.target.style.color = 'var(--maincolor)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'transparent';
              e.target.style.color = '#333';
            }}
          >
            <span>Supply Projects</span>
          </Link>
        </div>
      </div>

      {/* Menu Overlay */}
      {isMenuOpen && <div style={overlayStyle} onClick={toggleMenu}></div>}
    </>
  );
}
