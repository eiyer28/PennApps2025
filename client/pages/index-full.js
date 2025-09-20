import Head from "next/head";
import Link from "next/link";
import { useState, useEffect } from 'react';
import { useUser } from '@auth0/nextjs-auth0';
import axios from 'axios';

export default function Home() {
  const [authMode, setAuthMode] = useState(null); // null, 'demo', or 'auth0'
  const [demoUser, setDemoUser] = useState(null);
  const [userAccount, setUserAccount] = useState(null);
  const [isRegistering, setIsRegistering] = useState(false);
  const [registrationError, setRegistrationError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Auth0 user
  const { user: auth0User, error, isLoading: auth0Loading } = useUser();

  // Demo user data
  const demoDemoUser = {
    name: "Demo User",
    email: "demo@example.com",
    sub: "demo-user-123"
  };

  // Get current user based on auth mode
  const getCurrentUser = () => {
    if (authMode === 'demo') return demoUser;
    if (authMode === 'auth0') return auth0User;
    return null;
  };

  const currentUser = getCurrentUser();

  // Check if user is registered in our system
  useEffect(() => {
    if (currentUser && authMode) {
      checkUserRegistration();
    }
  }, [currentUser, authMode]);

  const checkUserRegistration = async () => {
    // In demo mode, skip backend API calls since we don't have real Auth0 tokens
    if (authMode === 'demo') {
      // Simulate checking - user is not registered initially
      setUserAccount(null);
      return;
    }

    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/me`,
        {
          headers: {
            Authorization: `Bearer ${await getAccessToken()}`,
          },
        }
      );
      setUserAccount(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        // User not registered in our system
        setUserAccount(null);
      } else {
        console.error('Error checking user registration:', error);
      }
    }
  };

  const getAccessToken = async () => {
    // In demo mode, return a mock token
    if (authMode === 'demo') {
      return "demo-access-token";
    }
    try {
      const response = await fetch('/api/auth/token');
      const { accessToken } = await response.json();
      return accessToken;
    } catch (error) {
      console.error('Error getting access token:', error);
      return null;
    }
  };

  const startDemoMode = () => {
    setAuthMode('demo');
    setDemoUser(demoDemoUser);
  };

  const startAuth0Mode = () => {
    setAuthMode('auth0');
  };

  const logout = () => {
    if (authMode === 'demo') {
      setAuthMode(null);
      setDemoUser(null);
      setUserAccount(null);
    } else if (authMode === 'auth0') {
      // Auth0 logout will be handled by the logout link
      window.location.href = '/api/auth/logout';
    }
  };

  const registerUser = async () => {
    setIsRegistering(true);
    setRegistrationError(null);

    try {
      if (authMode === 'demo') {
        // Simulate registration delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Mock successful registration with demo data
        const mockUserAccount = {
          name: currentUser.name,
          email: currentUser.email,
          created_at: new Date().toISOString(),
          wallet_address: "0x" + Math.random().toString(16).substr(2, 40).padStart(40, '0')
        };
        setUserAccount(mockUserAccount);
        return;
      }

      const accessToken = await getAccessToken();
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/register`,
        {
          email: currentUser.email,
          auth0_id: currentUser.sub,
          name: currentUser.name,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        }
      );
      setUserAccount(response.data);
    } catch (error) {
      console.error('Registration error:', error);
      setRegistrationError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setIsRegistering(false);
    }
  };

  if (isLoading) return <div style={styles.container}>Loading...</div>;

  return (
    <>
      <Head>
        <title>CarbonChain - Transparent Funding for Sustainable Projects</title>
        <meta name="description" content="Connect investors with sustainable development projects through blockchain transparency" />
      </Head>

      <div style={styles.container}>
        <header style={styles.header}>
          <div style={styles.headerContent}>
            <div>
              <h1 style={styles.title}>🌱 CarbonChain</h1>
              <p style={styles.subtitle}>Transparent Funding for Sustainable Projects</p>
            </div>
            <Link href="/search">
              <button style={styles.searchButton}>
                🔍 Search Projects
              </button>
            </Link>
          </div>
        </header>

        {!authMode ? (
          // No auth mode selected yet
          <div style={styles.loginSection}>
            <div style={styles.valueProposition}>
              <h2>Connect Capital with Climate Solutions</h2>
              <p>Fund sustainable projects directly through blockchain-verified impact tracking.</p>
              <ul style={styles.features}>
                <li>✅ Transparent milestone-based funding</li>
                <li>✅ Immutable proof-of-impact certificates</li>
                <li>✅ No greenwashing - verified carbon savings</li>
                <li>✅ Automatic crypto wallet generation</li>
              </ul>
            </div>

            <div style={styles.authOptions}>
              <div style={styles.authOptionCard}>
                <h3>🚀 Demo Mode</h3>
                <p>Try CarbonChain instantly without creating an account</p>
                <button onClick={startDemoMode} style={styles.demoButton}>
                  Get Started (Demo Mode)
                </button>
              </div>

              <div style={styles.authOptionCard}>
                <h3>🔒 Auth0 Account</h3>
                <p>Create a secure account with OAuth integration</p>
                <button onClick={startAuth0Mode} style={styles.auth0Button}>
                  Get Started with Auth0
                </button>
              </div>
            </div>
          </div>
        ) : authMode === 'auth0' && !auth0User ? (
          // Auth0 mode selected but not logged in
          <div style={styles.loginSection}>
            <div style={styles.valueProposition}>
              <h2>Sign in to CarbonChain</h2>
              <p>Access your secure account to fund sustainable projects</p>
            </div>

            <div style={styles.auth0Actions}>
              <a href="/api/auth/login" style={styles.loginButton}>
                🔑 Log In
              </a>
              <a href="/api/auth/login?screen_hint=signup" style={styles.signupButton}>
                📝 Sign Up
              </a>
              <button onClick={() => setAuthMode(null)} style={styles.backButton}>
                ← Back to Options
              </button>
            </div>
          </div>
        ) : !currentUser ? (
          // Loading state for auth0
          <div style={styles.loginSection}>
            <div style={styles.valueProposition}>
              <h2>Loading...</h2>
              <p>Please wait while we authenticate you.</p>
            </div>
          </div>
        ) : !userAccount ? (
          // Logged in but not registered
          <div style={styles.registrationSection}>
            <h2>Welcome, {currentUser.name}! 👋</h2>
            <p>Complete your account setup to start funding sustainable projects.</p>

            <div style={styles.userInfo}>
              <p><strong>Email:</strong> {currentUser.email}</p>
              <p><strong>ID:</strong> {currentUser.sub}</p>
              <p><strong>Mode:</strong> {authMode === 'demo' ? 'Demo Mode' : 'Auth0 Account'}</p>
            </div>

            {registrationError && (
              <div style={styles.error}>
                Error: {registrationError}
              </div>
            )}

            <button
              onClick={registerUser}
              disabled={isRegistering}
              style={styles.registerButton}
            >
              {isRegistering ? 'Creating Account...' : 'Create CarbonChain Account'}
            </button>

            <button onClick={logout} style={styles.logoutLink}>
              {authMode === 'demo' ? 'Exit Demo' : 'Logout'}
            </button>
          </div>
        ) : (
          // Fully registered user dashboard
          <div style={styles.dashboard}>
            <div style={styles.userHeader}>
              <h2>Welcome back, {userAccount.name}! 🎉</h2>
              <button onClick={logout} style={styles.logoutLink}>
                {authMode === 'demo' ? 'Exit Demo' : 'Logout'}
              </button>
            </div>

            <div style={styles.accountInfo}>
              <div style={styles.card}>
                <h3>📧 Account Details</h3>
                <p><strong>Name:</strong> {userAccount.name}</p>
                <p><strong>Email:</strong> {userAccount.email}</p>
                <p><strong>Member since:</strong> {new Date(userAccount.created_at).toLocaleDateString()}</p>
              </div>

              <div style={styles.card}>
                <h3>💰 Your Crypto Wallet</h3>
                <p><strong>Address:</strong></p>
                <code style={styles.walletAddress}>{userAccount.wallet_address}</code>
                <p style={styles.walletNote}>
                  This wallet was automatically generated for you and is ready to fund sustainable projects!
                </p>
              </div>

              <div style={styles.card}>
                <h3>🚀 Next Steps</h3>
                <ul>
                  <li>Browse available sustainable projects</li>
                  <li>Fund projects with milestone-based escrow</li>
                  <li>Track your impact with blockchain certificates</li>
                  <li>View your carbon offset portfolio</li>
                </ul>
                <p style={styles.comingSoon}>🔧 Project marketplace coming soon!</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

// Simple inline styles for the demo
const styles = {
  container: {
    minHeight: '100vh',
    padding: '2rem',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    backgroundColor: '#f8fffe',
    color: '#2d3748',
  },
  header: {
    textAlign: 'center',
    marginBottom: '3rem',
  },
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    maxWidth: '1200px',
    margin: '0 auto',
    flexWrap: 'wrap',
    gap: '1rem',
  },
  searchButton: {
    backgroundColor: '#22c55e',
    color: 'white',
    border: 'none',
    padding: '0.75rem 1.5rem',
    borderRadius: '8px',
    fontSize: '1rem',
    cursor: 'pointer',
    textDecoration: 'none',
    transition: 'background-color 0.2s',
    fontWeight: '600',
  },
  title: {
    fontSize: '3rem',
    margin: '0 0 0.5rem 0',
    color: '#22c55e',
  },
  subtitle: {
    fontSize: '1.2rem',
    color: '#64748b',
    margin: 0,
  },
  loginSection: {
    maxWidth: '800px',
    margin: '0 auto',
    textAlign: 'center',
  },
  authOptions: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '2rem',
    marginTop: '2rem',
  },
  authOptionCard: {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '12px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    border: '1px solid #e2e8f0',
    textAlign: 'center',
  },
  demoButton: {
    display: 'inline-block',
    padding: '1rem 2rem',
    backgroundColor: '#22c55e',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1.1rem',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    marginTop: '1rem',
  },
  auth0Button: {
    display: 'inline-block',
    padding: '1rem 2rem',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1.1rem',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    marginTop: '1rem',
  },
  auth0Actions: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    alignItems: 'center',
    marginTop: '2rem',
  },
  signupButton: {
    display: 'inline-block',
    padding: '1rem 2rem',
    backgroundColor: '#10b981',
    color: 'white',
    textDecoration: 'none',
    borderRadius: '8px',
    fontSize: '1.1rem',
    fontWeight: 'bold',
    transition: 'background-color 0.2s',
  },
  backButton: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#6b7280',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  valueProposition: {
    marginBottom: '2rem',
  },
  features: {
    textAlign: 'left',
    maxWidth: '400px',
    margin: '1rem auto',
  },
  loginButton: {
    display: 'inline-block',
    padding: '1rem 2rem',
    backgroundColor: '#22c55e',
    color: 'white',
    textDecoration: 'none',
    borderRadius: '8px',
    fontSize: '1.1rem',
    fontWeight: 'bold',
    transition: 'background-color 0.2s',
  },
  registrationSection: {
    maxWidth: '500px',
    margin: '0 auto',
    textAlign: 'center',
  },
  userInfo: {
    backgroundColor: '#f1f5f9',
    padding: '1rem',
    borderRadius: '8px',
    margin: '1rem 0',
    textAlign: 'left',
  },
  registerButton: {
    padding: '1rem 2rem',
    backgroundColor: '#22c55e',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1.1rem',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginBottom: '1rem',
  },
  error: {
    backgroundColor: '#fee2e2',
    color: '#dc2626',
    padding: '0.75rem',
    borderRadius: '6px',
    margin: '1rem 0',
  },
  logoutLink: {
    color: '#64748b',
    textDecoration: 'underline',
    fontSize: '0.9rem',
  },
  dashboard: {
    maxWidth: '1000px',
    margin: '0 auto',
  },
  userHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
  },
  accountInfo: {
    display: 'grid',
    gap: '1.5rem',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
  },
  card: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    border: '1px solid #e2e8f0',
  },
  walletAddress: {
    backgroundColor: '#f1f5f9',
    padding: '0.5rem',
    borderRadius: '4px',
    fontSize: '0.9rem',
    wordBreak: 'break-all',
    display: 'block',
    margin: '0.5rem 0',
  },
  walletNote: {
    fontSize: '0.9rem',
    color: '#64748b',
    marginTop: '0.5rem',
  },
  comingSoon: {
    color: '#22c55e',
    fontWeight: 'bold',
    fontSize: '0.9rem',
  },
};
