import Head from "next/head";
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Home() {
  const [demoMode, setDemoMode] = useState(true);
  const [user, setUser] = useState(null);
  const [userAccount, setUserAccount] = useState(null);
  const [isRegistering, setIsRegistering] = useState(false);
  const [registrationError, setRegistrationError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Demo user data
  const demoUser = {
    name: "Demo User",
    email: "demo@example.com",
    sub: "demo-user-123"
  };

  // Check if user is registered in our system
  useEffect(() => {
    if (user) {
      checkUserRegistration();
    }
  }, [user]);

  const checkUserRegistration = async () => {
    // In demo mode, skip backend API calls since we don't have real Auth0 tokens
    if (demoMode) {
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
    if (demoMode) {
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

  const demoLogin = () => {
    setUser(demoUser);
  };

  const demoLogout = () => {
    setUser(null);
    setUserAccount(null);
  };

  const registerUser = async () => {
    setIsRegistering(true);
    setRegistrationError(null);

    try {
      if (demoMode) {
        // Simulate registration delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Mock successful registration with demo data
        const mockUserAccount = {
          name: user.name,
          email: user.email,
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
          email: user.email,
          auth0_id: user.sub,
          name: user.name,
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
          <h1 style={styles.title}>🌱 CarbonChain</h1>
          <p style={styles.subtitle}>Transparent Funding for Sustainable Projects</p>
        </header>

        {!user ? (
          // Not logged in
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
            <button onClick={demoLogin} style={styles.loginButton}>
              Get Started (Demo Mode)
            </button>
          </div>
        ) : !userAccount ? (
          // Logged in but not registered
          <div style={styles.registrationSection}>
            <h2>Welcome, {user.name}! 👋</h2>
            <p>Complete your account setup to start funding sustainable projects.</p>

            <div style={styles.userInfo}>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Auth0 ID:</strong> {user.sub}</p>
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

            <button onClick={demoLogout} style={styles.logoutLink}>
              Logout
            </button>
          </div>
        ) : (
          // Fully registered user dashboard
          <div style={styles.dashboard}>
            <div style={styles.userHeader}>
              <h2>Welcome back, {userAccount.name}! 🎉</h2>
              <button onClick={demoLogout} style={styles.logoutLink}>
                Logout
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
    maxWidth: '600px',
    margin: '0 auto',
    textAlign: 'center',
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
