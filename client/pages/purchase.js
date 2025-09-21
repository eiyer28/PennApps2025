import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import Head from 'next/head';
import Navbar from '../components/Navbar';
import styles from '../styles/Purchase.module.css';

const Purchase = () => {
  const router = useRouter();
  const { id, name } = router.query;
  const [loading, setLoading] = useState(true);
  const [projectData, setProjectData] = useState(null);
  const [error, setError] = useState(null);
  const [quantity, setQuantity] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [priceUpdateCountdown, setPriceUpdateCountdown] = useState(60);
  const [supplyExceeded, setSupplyExceeded] = useState(false);
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  
  // Retirement certificate fields
  const [certificateFirstName, setCertificateFirstName] = useState('');
  const [certificateLastName, setCertificateLastName] = useState('');
  const [retirementMessage, setRetirementMessage] = useState('');
  
  // Input mode switching
  const [inputMode, setInputMode] = useState('tons'); // 'tons' or 'usd'
  const [usdAmount, setUsdAmount] = useState('');

  // Quote state
  const [quote, setQuote] = useState(null);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [quoteError, setQuoteError] = useState(null);
  const [hasQuote, setHasQuote] = useState(false);
  const [showQuoteModal, setShowQuoteModal] = useState(false);

  // Purchase flow state
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [purchaseLoading, setPurchaseLoading] = useState(false);
  const [purchaseError, setPurchaseError] = useState(null);
  const [purchaseSuccess, setPurchaseSuccess] = useState(false);
  const [orderData, setOrderData] = useState(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Check authentication status
  useEffect(() => {
    try {
      const userData = localStorage.getItem('user');
      if (userData) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        
        // Auto-populate certificate fields with user data
        setCertificateFirstName(parsedUser.first_name || '');
        setCertificateLastName(parsedUser.last_name || '');
        
        setAuthChecked(true);
      } else {
        // No user found, redirect to login
        router.push('/login?message=Please log in to access the purchase page.');
        return;
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      router.push('/login?message=Please log in to access the purchase page.');
      return;
    }
    setAuthChecked(true);
  }, [router]);

  // Fetch project data
  const fetchProjectData = async () => {
    if (!id) return;

    try {
      setError(null);
      const response = await fetch(`${API_BASE_URL}/project/${encodeURIComponent(id)}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch project: ${response.status}`);
      }

      const data = await response.json();
      setProjectData(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching project data:', err);
      setError(err.message);
    }
  };

  // Initial data fetch
  useEffect(() => {
    const initialFetch = async () => {
      // Only fetch if user is authenticated
      if (!authChecked || !user) return;
      
      setLoading(true);
      await fetchProjectData();
      setLoading(false);
    };

    initialFetch();
  }, [id, authChecked, user]);

  // Price update timer (every 60 seconds)
  useEffect(() => {
    if (!projectData) return;

    const priceUpdateInterval = setInterval(() => {
      fetchProjectData();
      setPriceUpdateCountdown(60);
    }, 60000);

    return () => clearInterval(priceUpdateInterval);
  }, [projectData, id]);

  // Countdown timer for next price update
  useEffect(() => {
    if (!lastUpdated) return;

    const countdownInterval = setInterval(() => {
      setPriceUpdateCountdown(prev => {
        if (prev <= 1) return 60;
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(countdownInterval);
  }, [lastUpdated]);

  // Handle quantity input with supply validation
  const handleQuantityChange = (e) => {
    const inputValue = e.target.value;
    const maxSupply = projectData?.stats?.totalSupply || 0;
    
    // Allow empty string for better UX while typing
    if (inputValue === '') {
      setQuantity('');
      setSupplyExceeded(false);
      return;
    }
    
    // Parse numeric value
    const numericValue = parseFloat(inputValue);
    
    // Ignore invalid input (non-numeric or negative)
    if (isNaN(numericValue) || numericValue < 0) {
      return; // Don't update quantity, effectively blocking the input
    }
    
    // Limit to 2 decimal places, rounding down
    const roundedValue = Math.floor(numericValue * 100) / 100;
    
    // Check if it exceeds available supply
    if (roundedValue > maxSupply && maxSupply > 0) {
      const cappedSupply = Math.floor(maxSupply * 100) / 100;
      setQuantity(cappedSupply.toString());
      setSupplyExceeded(true);
    } else {
      setQuantity(roundedValue.toString());
      setSupplyExceeded(roundedValue === Math.floor(maxSupply * 100) / 100 && maxSupply > 0);
    }
  };

  // Handle USD input - keep as separate value without automatic conversion
  const handleUsdChange = (e) => {
    const inputValue = e.target.value;
    
    // Allow empty string for better UX while typing
    if (inputValue === '') {
      setUsdAmount('');
      setSupplyExceeded(false);
      return;
    }
    
    // Parse numeric value
    const numericValue = parseFloat(inputValue);
    
    // Ignore invalid input (non-numeric or negative)
    if (isNaN(numericValue) || numericValue < 0) {
      return;
    }
    
    // Limit to 2 decimal places
    const roundedValue = Math.floor(numericValue * 100) / 100;
    setUsdAmount(roundedValue.toString());
    
    // Check if this USD amount would exceed supply when converted to tons
    const price = parseFloat(projectData?.price) || 0;
    if (price > 0) {
      const equivalentTons = roundedValue / price;
      const maxSupply = projectData?.stats?.totalSupply || 0;
      
      if (equivalentTons > maxSupply && maxSupply > 0) {
        const cappedUsd = Math.floor(maxSupply * price * 100) / 100;
        setUsdAmount(cappedUsd.toString());
        setSupplyExceeded(true);
      } else {
        setSupplyExceeded(false);
      }
    }
  };

  // Switch input mode - NO conversions, just switch the active mode
  const switchInputMode = (mode) => {
    setInputMode(mode);
    // No conversions! Each input maintains its own value independently
  };

  // Get the current effective quantity in tons (for calculations)
  const getEffectiveQuantity = () => {
    if (inputMode === 'tons') {
      return parseFloat(quantity) || 0;
    } else {
      // USD mode: convert USD to tons for display/calculation only
      const price = parseFloat(projectData?.price) || 0;
      if (price > 0 && usdAmount) {
        return parseFloat(usdAmount) / price;
      }
      return 0;
    }
  };

  // Calculate order total based on current input mode
  const calculateTotal = () => {
    const price = parseFloat(projectData?.price) || 0;
    
    if (inputMode === 'tons') {
      const qty = parseFloat(quantity) || 0;
      return qty * price;
    } else {
      return parseFloat(usdAmount) || 0;
    }
  };

  // Get available supply
  const getAvailableSupply = () => {
    return projectData?.stats?.totalSupply || 0;
  };

  // Format seconds ago for last updated
  const getLastUpdatedText = () => {
    if (!lastUpdated) return '';
    const secondsAgo = Math.floor((new Date() - lastUpdated) / 1000);
    if (secondsAgo < 60) return `${secondsAgo} seconds ago`;
    const minutesAgo = Math.floor(secondsAgo / 60);
    return `${minutesAgo} minute${minutesAgo !== 1 ? 's' : ''} ago`;
  };

  // Check if certificate fields are valid for purchase
  const isCertificateValid = () => {
    return certificateFirstName.trim().length > 0 && 
           certificateLastName.trim().length > 0 &&
           retirementMessage.trim().length > 0;
  };

  // Check if basic quote parameters are ready (just quantity and price)
  const isBasicQuoteReady = () => {
    const hasValidInput = (inputMode === 'tons' && quantity && parseFloat(quantity) > 0) ||
                         (inputMode === 'usd' && usdAmount && parseFloat(usdAmount) > 0);
    
    return hasValidInput && 
           projectData?.price && 
           parseFloat(projectData.price) > 0;
  };

  // Check if quote is ready (includes certificate fields for full quote)
  const isQuoteReady = () => {
    return isBasicQuoteReady() && isCertificateValid();
  };

  // Check if order is ready for purchase (quote + certificate)
  const isOrderReady = () => {
    return isQuoteReady() && isCertificateValid();
  };

  // Check if purchase is ready (has quote + certificate)
  const isPurchaseReady = () => {
    return hasQuote && isCertificateValid();
  };

  // Prepare retirement data for API call (for future implementation)
  const getRetirementData = () => {
    return {
      quantity: getEffectiveQuantity(),
      certificateFirstName: certificateFirstName.trim(),
      certificateLastName: certificateLastName.trim(),
      retirementMessage: retirementMessage.trim(),
      projectId: projectData?.key || id,
      totalCost: calculateTotal()
    };
  };

  // Handle unified purchase workflow - begins with quote generation
  const handleBeginPurchase = async () => {
    if (!isBasicQuoteReady()) return;
    
    // If we don't have a quote yet, get one first
    if (!hasQuote) {
      await handleGetQuote();
      return; // handleGetQuote will show the modal when complete
    }
    
    // If we already have a quote, show the quote modal
    setShowQuoteModal(true);
  };

  // Handle get quote button click
  const handleGetQuote = async () => {
    if (!isBasicQuoteReady()) return;
    
    setQuoteLoading(true);
    setQuoteError(null);
    setQuote(null);

    try {
      const quoteData = getRetirementData();
      
      const response = await fetch(`${API_BASE_URL}/get_quote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...quoteData,
          userId: user?.id || user?.email,
          projectData: {
            id: projectData?.key || id,
            name: projectData?.name || name,
            price: projectData?.price,
            registry: projectData?.registry
          }
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Quote request failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Quote result:', result);
      console.log('Quote structure analysis:');
      console.log('- result.quote:', result.quote);
      console.log('- result.supplierSelection:', result.supplierSelection);
      console.log('- selectedSources in quote:', result.quote?.selectedSources);
      console.log('- selectedSources in supplierSelection:', result.supplierSelection?.selectedSources);
      
      setQuote(result);
      setHasQuote(true);
      setShowQuoteModal(true); // Show the quote modal after successful quote generation
    } catch (err) {
      console.error('Quote error:', err);
      setQuoteError(err.message);
    } finally {
      setQuoteLoading(false);
    }
  };

  // Handle refresh quote button click (from within quote modal)
  const handleRefreshQuote = async () => {
    if (!isBasicQuoteReady()) return;
    
    setQuoteLoading(true);
    setQuoteError(null);

    try {
      const quoteData = getRetirementData();
      
      const response = await fetch(`${API_BASE_URL}/get_quote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...quoteData,
          userId: user?.id || user?.email,
          projectData: {
            id: projectData?.key || id,
            name: projectData?.name || name,
            price: projectData?.price,
            registry: projectData?.registry
          }
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Quote request failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Refreshed quote result:', result);
      
      setQuote(result);
      setHasQuote(true);
    } catch (err) {
      console.error('Quote refresh error:', err);
      setQuoteError(err.message);
    } finally {
      setQuoteLoading(false);
    }
  };

  // Handle purchase confirmation (show confirmation modal)
  const handlePurchaseClick = () => {
    if (!hasQuote) return;
    setPurchaseError(null);
    setShowQuoteModal(false); // Close quote modal
    setShowConfirmModal(true);
  };

  // Handle purchase confirmation (call backend)
  const handlePurchaseConfirm = async () => {
    setPurchaseLoading(true);
    setPurchaseError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/purchase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          quoteId: quote.quoteId,
          certificateFirstName: certificateFirstName.trim(),
          certificateLastName: certificateLastName.trim(),
          retirementMessage: retirementMessage.trim(),
          userId: user?.id || user?.email
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Purchase failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Purchase result:', result);
      
      // Store the order data for the receipt
      setOrderData(result);
      setPurchaseSuccess(true);
      setShowConfirmModal(false);
    } catch (err) {
      console.error('Purchase error:', err);
      setPurchaseError(err.message);
    } finally {
      setPurchaseLoading(false);
    }
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowConfirmModal(false);
    setPurchaseError(null);
  };

  // Handle quote modal close
  const handleQuoteModalClose = () => {
    setShowQuoteModal(false);
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>
          <div className={styles.spinner}></div>
          <p>Loading purchase page...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <Link href={`/project?id=${encodeURIComponent(id || '')}&name=${encodeURIComponent(name || '')}`} className={styles.backButton}>
            ← Back to Project
          </Link>
          <h1 className={styles.title}>Unable to Load Purchase Page</h1>
        </div>
        <div className={styles.content}>
          <div className={styles.errorCard}>
            <div className={styles.errorIcon}>⚠️</div>
            <h2>Error Loading Project Data</h2>
            <p>{error}</p>
            <Link href="/search" className={styles.backToSearchButton}>
              Return to Search
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <Navbar />
      <div className={styles.header}>
        <Link href={`/project?id=${encodeURIComponent(id || '')}&name=${encodeURIComponent(name || '')}`} className={styles.backButton}>
          ← Back to Project
        </Link>
        <h1 className={styles.title}>Purchase Carbon Credits</h1>
      </div>

      <div className={styles.content}>
        <div className={styles.purchaseLayout}>
          {/* Left Column - Order Calculator */}
          <div className={styles.orderSection}>
            <div className={styles.purchaseCard}>
              <div className={styles.projectInfo}>
                <h2 className={styles.projectName}>
                  {projectData?.name || (name ? decodeURIComponent(name) : 'Project Name')}
                </h2>
                <div className={styles.projectId}>
                  <strong>Project ID:</strong> {projectData?.key || id || 'N/A'}
                </div>
                {projectData?.registry && (
                  <div className={styles.certificationBadge}>
                    <span className={styles.checkmark}>✓</span>
                    <span>{projectData.registry} Certified</span>
                  </div>
                )}
              </div>

              {/* Quantity Input - Main Focus */}
              <div className={styles.quantitySection}>
                <h3>📊 Order Calculator</h3>
                
                {/* Current Price Display */}
                <div className={styles.priceTicket}>
                  <div className={styles.priceLabel}>Estimated Current Price</div>
                  <div className={styles.priceAmount}>
                    {projectData?.price && parseFloat(projectData.price) > 0 
                      ? `$${projectData.price}` 
                      : 'Not Available'
                    }
                    <span className={styles.priceUnit}> per ton CO₂</span>
                  </div>
                  {lastUpdated && (
                    <div className={styles.priceUpdate}>
                      Updated {getLastUpdatedText()}
                    </div>
                  )}
                  <div className={styles.priceDisclaimer}>
                    ⚠️ Final quote price may vary from estimates
                  </div>
                </div>

                {/* Input Mode Toggle */}
                <div className={styles.inputModeToggle}>
                  <button
                    className={`${styles.toggleButton} ${inputMode === 'tons' ? styles.active : ''}`}
                    onClick={() => switchInputMode('tons')}
                  >
                    Enter Tons CO₂
                  </button>
                  <button
                    className={`${styles.toggleButton} ${inputMode === 'usd' ? styles.active : ''}`}
                    onClick={() => switchInputMode('usd')}
                  >
                    Enter USD Amount
                  </button>
                </div>

                {/* Input Field */}
                <div className={styles.inputGroup}>
                  {inputMode === 'tons' ? (
                    <>
                      <label htmlFor="quantity">Tons of CO₂ to Purchase/Retire:</label>
                      <input
                        type="number"
                        id="quantity"
                        value={quantity}
                        onChange={handleQuantityChange}
                        placeholder="Enter quantity..."
                        min="0"
                        max={getAvailableSupply()}
                        step="0.01"
                        className={styles.quantityInput}
                      />
                    </>
                  ) : (
                    <>
                      <label htmlFor="usdAmount">USD Amount to Spend:</label>
                      <input
                        type="number"
                        id="usdAmount"
                        value={usdAmount}
                        onChange={handleUsdChange}
                        placeholder="Enter amount in USD..."
                        min="0"
                        step="0.01"
                        className={styles.quantityInput}
                      />
                    </>
                  )}
                  
                  <div className={styles.supplyInfo}>
                    <span>Available Supply: {getAvailableSupply().toLocaleString()} tons CO₂</span>
                  </div>
                  {supplyExceeded && (
                    <div className={styles.supplyWarning}>
                      ⚠️ Maximum available supply reached
                    </div>
                  )}
                </div>
                
                {/* Price Calculation Bubble */}
                {((inputMode === 'tons' && quantity && parseFloat(quantity) > 0) || 
                  (inputMode === 'usd' && usdAmount && parseFloat(usdAmount) > 0)) && 
                 projectData?.price && parseFloat(projectData.price) > 0 && (
                  <div className={styles.calculationBubble}>
                    {inputMode === 'tons' ? (
                      <>
                        <div className={styles.calcRow}>
                          <span>{parseFloat(quantity).toLocaleString()} tons CO₂</span>
                          <span>×</span>
                          <span>${projectData.price}/ton</span>
                          <span>=</span>
                          <span className={styles.calcResult}>${calculateTotal().toFixed(2)}</span>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className={styles.calcRow}>
                          <span>${parseFloat(usdAmount).toLocaleString()}</span>
                          <span>÷</span>
                          <span>${projectData.price}/ton</span>
                          <span>=</span>
                          <span className={styles.calcResult}>{getEffectiveQuantity().toFixed(2)} tons CO₂</span>
                        </div>
                      </>
                    )}
                  </div>
                )}
                
                {((inputMode === 'tons' && quantity) || (inputMode === 'usd' && usdAmount)) && 
                 (!projectData?.price || parseFloat(projectData.price) <= 0) && (
                  <div className={styles.noTradingWarning}>
                    ⚠️ This project is not currently trading. Price calculation unavailable.
                  </div>
                )}
              </div>

              {/* Retirement Certificate Information */}
              <div className={styles.certificateSection}>
                <h3>📜 Retirement Certificate Details</h3>
                <p className={styles.certificateNote}>
                  These details will appear on your retirement certificate and are public records.
                </p>
                
                <div className={styles.certificateForm}>
                  <div className={styles.nameRow}>
                    <div className={styles.inputGroup}>
                      <label htmlFor="certificateFirstName">First Name:</label>
                      <input
                        type="text"
                        id="certificateFirstName"
                        value={certificateFirstName}
                        onChange={(e) => setCertificateFirstName(e.target.value)}
                        placeholder="Enter first name for certificate"
                        className={styles.certificateInput}
                        maxLength={50}
                      />
                    </div>
                    <div className={styles.inputGroup}>
                      <label htmlFor="certificateLastName">Last Name:</label>
                      <input
                        type="text"
                        id="certificateLastName"
                        value={certificateLastName}
                        onChange={(e) => setCertificateLastName(e.target.value)}
                        placeholder="Enter last name for certificate"
                        className={styles.certificateInput}
                        maxLength={50}
                      />
                    </div>
                  </div>
                  
                  <div className={styles.inputGroup}>
                    <label htmlFor="retirementMessage">Message for Certificate:</label>
                    <textarea
                      id="retirementMessage"
                      value={retirementMessage}
                      onChange={(e) => setRetirementMessage(e.target.value)}
                      placeholder="Enter a message for your retirement certificate (ex: 'In honor of Earth Day 2025')"
                      className={styles.messageInput}
                      rows={3}
                      maxLength={200}
                      required
                    />
                    <div className={styles.characterCount}>
                      {retirementMessage.length}/200 characters (required)
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className={styles.actionSection}>
                {(!quantity || parseFloat(quantity) <= 0) && (!usdAmount || parseFloat(usdAmount) <= 0) ? (
                  <div className={`${styles.validationMessage} ${styles.validationWarning}`}>
                    ⚠️ Please enter a {inputMode === 'tons' ? 'quantity' : 'USD amount'} to get quote
                  </div>
                ) : !projectData?.price || parseFloat(projectData.price) <= 0 ? (
                  <div className={`${styles.validationMessage} ${styles.validationWarning}`}>
                    ⚠️ This project is not currently trading
                  </div>
                ) : null}
                
                {/* Quote Error Display */}
                {quoteError && (
                  <div className={styles.errorMessage}>
                    <strong>Quote Error:</strong> {quoteError}
                  </div>
                )}
                
                {/* Unified Begin Purchase Button */}
                {!hasQuote && (
                <button 
                  className={isBasicQuoteReady() ? styles.purchaseButton : styles.purchaseButtonDisabled}
                  disabled={!isBasicQuoteReady() || quoteLoading}
                  onClick={handleBeginPurchase}
                >
                  {quoteLoading ? '⏳ Getting Quote...' : '� Begin Purchase'}
                </button>
                )}

                {/* Quote Status (shown after quote is generated) */}
                {hasQuote && (
                  <div className={styles.quoteStatus}>
                    <h4>✅ Quote Ready</h4>
                    <p>Expected: ${calculateTotal().toFixed(2)} | Actual: ${quote?.supplierSelection?.totalCost?.toFixed(2) || 'N/A'}</p>
                    <p>Suppliers: {quote?.quote?.selectedSources?.length || quote?.supplierSelection?.selectedSources?.length || 0}</p>
                    <button 
                      className={styles.purchaseButton}
                      onClick={() => setShowQuoteModal(true)}
                    >
                      📋 Review Quote & Continue
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Project Information Dashboard */}
          <div className={styles.infoSection}>
            <div className={styles.infoDashboard}>
              <h3>� Project Information</h3>
              
              {/* Quick Overview */}
              {projectData?.description && (
                <div className={styles.infoCard}>
                  <h4>Project Overview</h4>
                  <p className={styles.infoDescription}>
                    {projectData.description.length > 150 
                      ? projectData.description.substring(0, 150) + '...'
                      : projectData.description
                    }
                  </p>
                </div>
              )}

              {/* Location & Methodology */}
              <div className={styles.infoCard}>
                <h4>🌍 Location & Methodology</h4>
                <div className={styles.infoGrid}>
                  {projectData?.country && (
                    <div className={styles.infoItem}>
                      <strong>Location:</strong> {projectData.country}
                      {projectData.region && `, ${projectData.region}`}
                    </div>
                  )}
                  {projectData?.methodologies && projectData.methodologies.length > 0 && (
                    <div className={styles.infoItem}>
                      <strong>Category:</strong> {projectData.methodologies[0].category}
                    </div>
                  )}
                  {projectData?.methodologies && projectData.methodologies.length > 0 && (
                    <div className={styles.infoItem}>
                      <strong>Methodology:</strong> {projectData.methodologies[0].name}
                    </div>
                  )}
                  {projectData?.vintage && (
                    <div className={styles.infoItem}>
                      <strong>Vintage:</strong> {projectData.vintage}
                    </div>
                  )}
                </div>
              </div>

              {/* Supply Information */}
              {projectData?.stats && (
                <div className={styles.infoCard}>
                  <h4>📊 Supply Information</h4>
                  <div className={styles.infoGrid}>
                    {projectData.stats.totalSupply && (
                      <div className={styles.infoItem}>
                        <strong>Total Supply:</strong> {projectData.stats.totalSupply.toLocaleString()} tons CO₂
                      </div>
                    )}
                    {projectData.stats.totalRetired && (
                      <div className={styles.infoItem}>
                        <strong>Total Retired:</strong> {projectData.stats.totalRetired.toLocaleString()} tons CO₂
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* View Full Details Link */}
              <div className={styles.viewDetailsSection}>
                <Link 
                  href={`/project?id=${encodeURIComponent(id || '')}&name=${encodeURIComponent(name || '')}`}
                  className={styles.viewDetailsButton}
                >
                  📖 View Full Project Details
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Debug Information */}
        <div className={styles.debugInfo}>
          <h4>Debug Information:</h4>
          <p><strong>Project ID:</strong> {projectData?.key || id || 'Not provided'}</p>
          <p><strong>Project Name:</strong> {projectData?.name || (name ? decodeURIComponent(name) : 'Not provided')}</p>
          <p><strong>Estimated Current Price:</strong> ${projectData?.price || 'N/A'}</p>
          <p><strong>Last Updated:</strong> {lastUpdated ? lastUpdated.toLocaleString() : 'Never'}</p>
          <p><strong>Input Mode:</strong> {inputMode}</p>
          <p><strong>Quantity (tons):</strong> {quantity || 'None'}</p>
          <p><strong>USD Amount:</strong> {usdAmount || 'None'}</p>
          <p><strong>Effective Quantity:</strong> {getEffectiveQuantity().toFixed(2)} tons</p>
          <p><strong>Certificate Name:</strong> {certificateFirstName} {certificateLastName}</p>
          <p><strong>Retirement Message:</strong> {retirementMessage || 'None'}</p>
          <p><strong>Order Ready:</strong> {isOrderReady() ? 'Yes' : 'No'}</p>
          {isOrderReady() && (
            <p><strong>Retirement Data:</strong> {JSON.stringify(getRetirementData(), null, 2)}</p>
          )}
        </div>

        {/* Quote Modal */}
        {showQuoteModal && (
          <div className={styles.modalOverlay}>
            <div className={styles.modal}>
              <div className={styles.modalHeader}>
                <h3>📊 Quote Details</h3>
                <button 
                  className={styles.modalClose}
                  onClick={handleQuoteModalClose}
                  disabled={quoteLoading}
                >
                  ×
                </button>
              </div>
              
              <div className={styles.modalContent}>
                <div className={styles.orderSummary}>
                  <h4>Quote Summary</h4>
                  
                  {/* Cost Comparison - Emphasized */}
                  <div className={styles.costComparison}>
                    <div className={styles.costItem}>
                      <span className={styles.costLabel}>Expected Cost:</span>
                      <span className={styles.costValue}>${calculateTotal().toFixed(2)}</span>
                    </div>
                    <div className={styles.costItem}>
                      <span className={styles.costLabel}>Actual Total Cost:</span>
                      <span className={styles.costValue}>${quote?.supplierSelection?.totalCost?.toFixed(2) || 'N/A'}</span>
                    </div>
                    {quote?.supplierSelection?.costExceedsExpected && (
                      <div className={styles.costDifference}>
                        <span className={styles.costLabel}>Difference:</span>
                        <span className={styles.costDifferenceValue}>
                          +${(quote.supplierSelection.totalCost - calculateTotal()).toFixed(2)}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className={styles.summaryGrid}>
                    <div className={styles.summaryItem}>
                      <strong>Project:</strong> {projectData?.name || (name ? decodeURIComponent(name) : 'N/A')}
                    </div>
                    <div className={styles.summaryItem}>
                      <strong>Quantity:</strong> {getEffectiveQuantity().toLocaleString()} tons CO₂
                    </div>
                    <div className={styles.summaryItem}>
                      <strong>Suppliers:</strong> {quote?.quote?.selectedSources?.length || quote?.supplierSelection?.selectedSources?.length || 0}
                    </div>
                  </div>
                  
                  {/* Less Prominent IDs */}
                  <div className={styles.technicalDetails}>
                    <div className={styles.techItem}>
                      Quote ID: {quote?.quoteId || 'N/A'}
                    </div>
                  </div>
                  
                  {/* Quote Supplier Details */}
                  {quote?.quote?.selectedSources && (
                    <div className={styles.supplierDetails}>
                      <h5>Supplier Breakdown</h5>
                      {quote.quote.selectedSources.map((source, index) => (
                        <div key={index} className={styles.supplierDetailItem}>
                          <div>
                            <strong>{source.poolName || 'Pool'}:</strong> {source.quantity?.toFixed(2) || 'N/A'} tons @ ${source.pricePerTon?.toFixed(4) || 'N/A'}/ton
                          </div>
                          <div className={styles.supplierDetailCost}>
                            ${source.totalCost?.toFixed(2) || 'N/A'}
                          </div>
                          <div className={styles.supplierTechDetails}>
                            ID: {source.sourceId || 'N/A'}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {quote?.supplierSelection?.costExceedsExpected && (
                    <div className={styles.costWarning}>
                      ⚠️ Final cost exceeds initial estimate
                    </div>
                  )}
                </div>

                {quoteError && (
                  <div className={styles.modalError}>
                    <strong>Error:</strong> {quoteError}
                  </div>
                )}
              </div>
              
              <div className={styles.modalActions}>
                <button 
                  className={styles.refreshQuoteButton}
                  onClick={handleRefreshQuote}
                  disabled={quoteLoading}
                >
                  {quoteLoading ? '⏳ Refreshing...' : '🔄 Refresh Quote'}
                </button>
                {isPurchaseReady() ? (
                  <button 
                    className={styles.confirmButton}
                    onClick={handlePurchaseClick}
                    disabled={quoteLoading}
                  >
                    Confirm Purchase
                  </button>
                ) : (
                  <div className={styles.purchaseRequirement}>
                    Please fill in certificate details below to continue
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Purchase Confirmation Modal */}
        {showConfirmModal && (
          <div className={styles.modalOverlay}>
            <div className={styles.modal}>
              <div className={styles.modalHeader}>
                <h3>🛒 Final Purchase Confirmation</h3>
                <button 
                  className={styles.modalClose}
                  onClick={handleModalClose}
                  disabled={purchaseLoading}
                >
                  ×
                </button>
              </div>
              
              <div className={styles.modalContent}>
                <div className={styles.orderSummary}>
                  <h4>Order Summary</h4>
                  <div className={styles.summaryGrid}>
                    <div className={styles.summaryItem}>
                      <strong>Project:</strong> {projectData?.name || (name ? decodeURIComponent(name) : 'N/A')}
                    </div>
                    <div className={styles.summaryItem}>
                      <strong>Project ID:</strong> {projectData?.key || id || 'N/A'}
                    </div>
                    <div className={styles.summaryItem}>
                      <strong>Quantity:</strong> {getEffectiveQuantity().toLocaleString()} tons CO₂
                    </div>
                    <div className={styles.summaryItem}>
                      <strong>Quote ID:</strong> {quote?.quoteId || 'N/A'}
                    </div>
                    <div className={styles.summaryItem}>
                      <strong>Total Cost:</strong> ${quote?.supplierSelection?.totalCost?.toFixed(2) || 'N/A'}
                    </div>
                    <div className={styles.summaryItem}>
                      <strong>Suppliers:</strong> {quote?.quote?.selectedSources?.length || quote?.supplierSelection?.selectedSources?.length || 0}
                    </div>
                  </div>
                  
                  {/* Quote Supplier Details */}
                  {quote?.quote?.selectedSources && (
                    <div className={styles.supplierDetails}>
                      <h5>Supplier Breakdown</h5>
                      {quote.quote.selectedSources.map((source, index) => (
                        <div key={index} className={styles.supplierDetailItem}>
                          <div>
                            <strong>{source.poolName || 'Pool'}:</strong> {source.quantity?.toFixed(2) || 'N/A'} tons @ ${source.pricePerTon?.toFixed(4) || 'N/A'}/ton
                          </div>
                          <div className={styles.supplierDetailCost}>
                            ${source.totalCost?.toFixed(2) || 'N/A'}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className={styles.certificateInfo}>
                    <h5>Retirement Certificate</h5>
                    <div className={styles.summaryItem}>
                      <strong>Certificate Name:</strong> {certificateFirstName} {certificateLastName}
                    </div>
                    <div className={styles.summaryItem}>
                      <strong>Message:</strong> "{retirementMessage}"
                    </div>
                  </div>
                </div>

                {purchaseError && (
                  <div className={styles.modalError}>
                    <strong>Error:</strong> {purchaseError}
                  </div>
                )}
              </div>
              
              <div className={styles.modalActions}>
                <button 
                  className={styles.cancelButton}
                  onClick={handleModalClose}
                  disabled={purchaseLoading}
                >
                  Cancel
                </button>
                <button 
                  className={styles.confirmButton}
                  onClick={handlePurchaseConfirm}
                  disabled={purchaseLoading}
                >
                  {purchaseLoading ? '⏳ Processing...' : `Confirm Purchase - $${quote?.supplierSelection?.totalCost?.toFixed(2) || 'N/A'}`}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Purchase Receipt Modal */}
        {purchaseSuccess && orderData && (
          <div className={styles.modalOverlay}>
            <div className={styles.modal}>
              <div className={styles.modalHeader}>
                <h3>🧾 Purchase Receipt</h3>
              </div>
              
              <div className={styles.modalContent}>
                <div className={styles.receiptContainer}>
                  <div className={styles.receiptHeader}>
                    <h4>✅ Order Executed Successfully</h4>
                    <p className={styles.receiptDate}>{new Date().toLocaleDateString()}</p>
                  </div>
                  
                  <div className={styles.receiptDetails}>
                    <div className={styles.receiptSection}>
                      <h5>Order Information</h5>
                      <div className={styles.receiptItem}>
                        <span>Order ID:</span>
                        <span className={styles.orderId}>{orderData.orderId}</span>
                      </div>
                      <div className={styles.receiptItem}>
                        <span>Order Status:</span>
                        <span className={styles.orderStatus}>{orderData.carbonmarkOrder?.orderStatus || 'Processing'}</span>
                      </div>
                      <div className={styles.receiptItem}>
                        <span>Created:</span>
                        <span>{orderData.carbonmarkOrder?.createdAt ? new Date(orderData.carbonmarkOrder.createdAt).toLocaleString() : new Date().toLocaleString()}</span>
                      </div>
                    </div>
                  
                    <div className={styles.receiptSection}>
                      <h5>Project Details</h5>
                      <div className={styles.receiptItem}>
                        <span>Project:</span>
                        <span>{projectData?.name || (name ? decodeURIComponent(name) : 'N/A')}</span>
                      </div>
                      <div className={styles.receiptItem}>
                        <span>Carbon Quantity:</span>
                        <span>{orderData.carbonmarkOrder?.totalCarbonQuantity || getEffectiveQuantity().toLocaleString()} tons CO₂</span>
                      </div>
                    </div>
                    
                    <div className={styles.receiptSection}>
                      <h5>Payment Details</h5>
                      <div className={styles.receiptItem}>
                        <span>Total Price:</span>
                        <span className={styles.receiptTotal}>${orderData.carbonmarkOrder?.totalPrice || orderData.data?.totalPrice || quote?.supplierSelection?.totalCost?.toFixed(2) || 'N/A'}</span>
                      </div>
                      <div className={styles.receiptItem}>
                        <span>Suppliers Used:</span>
                        <span>{orderData.carbonmarkOrder?.items?.length || quote?.quote?.selectedSources?.length || 0}</span>
                      </div>
                      {(quote?.quote?.selectedSources || quote?.supplierSelection?.selectedSources) && (
                        <div className={styles.receiptItem}>
                          <span>Supplier Names:</span>
                          <span>
                            {(quote?.quote?.selectedSources || quote?.supplierSelection?.selectedSources)
                              ?.map(source => source.poolName || 'Unknown Pool')
                              .join(', ') || 'N/A'}
                          </span>
                        </div>
                      )}
                    </div>
                    
                    <div className={styles.receiptSection}>
                      <h5>Certificate Information</h5>
                      <div className={styles.receiptItem}>
                        <span>Certificate Name:</span>
                        <span>{orderData.data?.certificateName || `${certificateFirstName} ${certificateLastName}`}</span>
                      </div>
                      <div className={styles.receiptItem}>
                        <span>Retirement Message:</span>
                        <span>"{orderData.data?.retirementMessage || retirementMessage}"</span>
                      </div>
                    </div>
                    
                    <div className={styles.receiptTechnical}>
                      <div className={styles.techItem}>Quote ID: {orderData.data?.quoteId || quote?.quoteId || 'N/A'}</div>
                      <div className={styles.techItem}>Transaction Status: {orderData.success ? 'Completed' : 'Failed'}</div>
                    </div>
                  </div>
                  
                  <div className={styles.receiptFooter}>
                    <p className={styles.receiptNote}>
                      <strong>Success!</strong> Your carbon credits have been ordered and are being processed. 
                      Your retirement certificate will be issued once the order is complete.
                    </p>
                    {orderData.message && (
                      <p className={styles.receiptMessage}>
                        {orderData.message}
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
              <div className={styles.modalActions}>
                <button 
                  className={styles.confirmButton}
                  onClick={() => {
                    setPurchaseSuccess(false);
                    setOrderData(null);
                    router.push('/search');
                  }}
                >
                  🏠 Return to Projects
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Purchase;