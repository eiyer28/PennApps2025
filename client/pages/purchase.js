import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import Link from 'next/link';
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

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
      setLoading(true);
      await fetchProjectData();
      setLoading(false);
    };

    initialFetch();
  }, [id]);

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

  // Calculate order total
  const calculateTotal = () => {
    const qty = parseFloat(quantity) || 0;
    const price = parseFloat(projectData?.price) || 0;
    return qty * price;
  };

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

              {/* Pricing Information */}
              <div className={styles.pricingSection}>
                <h3>💰 Current Price</h3>
                <div className={styles.priceDisplay}>
                  <div className={styles.priceValue}>
                    {projectData?.price && parseFloat(projectData.price) > 0 
                      ? `$${projectData.price}` 
                      : 'Not Available'
                    }
                    <span className={styles.priceUnit}> per ton CO₂</span>
                  </div>
                  <div className={styles.priceUpdate}>
                    {lastUpdated ? (
                      <span>Last updated: {getLastUpdatedText()}</span>
                    ) : (
                      <span>Loading price data...</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Quantity Input - Main Focus */}
              <div className={styles.quantitySection}>
                <h3>📊 Order Calculator</h3>
                <div className={styles.inputGroup}>
                  <label htmlFor="quantity">Tons of CO₂ to Purchase/Retire:</label>
                  <input
                    type="number"
                    id="quantity"
                    value={quantity}
                    onChange={handleQuantityChange}
                    placeholder="Enter quantity..."
                    min="0"
                    max={getAvailableSupply()}
                    step="0.1"
                    className={styles.quantityInput}
                  />
                  <div className={styles.supplyInfo}>
                    <span>Available Supply: {getAvailableSupply().toLocaleString()} tons CO₂</span>
                  </div>
                  {supplyExceeded && (
                    <div className={styles.supplyWarning}>
                      ⚠️ Maximum available supply reached
                    </div>
                  )}
                </div>
                
                {quantity && projectData?.price && parseFloat(projectData.price) > 0 && (
                  <div className={styles.orderSummary}>
                    <div className={styles.summaryRow}>
                      <span>Quantity:</span>
                      <span>{parseFloat(quantity).toLocaleString()} tons CO₂</span>
                    </div>
                    <div className={styles.summaryRow}>
                      <span>Price per ton:</span>
                      <span>${projectData.price}</span>
                    </div>
                    <div className={styles.summaryRow}>
                      <span>Available Supply:</span>
                      <span>{getAvailableSupply().toLocaleString()} tons CO₂</span>
                    </div>
                    <div className={styles.summaryRow + ' ' + styles.totalRow}>
                      <span>Total Order Value:</span>
                      <span>${calculateTotal().toFixed(2)}</span>
                    </div>
                  </div>
                )}

                {quantity && (!projectData?.price || parseFloat(projectData.price) <= 0) && (
                  <div className={styles.noTradingWarning}>
                    ⚠️ This project is not currently trading. Price calculation unavailable.
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className={styles.actionSection}>
                <button 
                  className={styles.purchaseButtonDisabled}
                  disabled={true}
                >
                  🛒 Purchase (Coming Soon)
                </button>
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
          <p><strong>Current Price:</strong> ${projectData?.price || 'N/A'}</p>
          <p><strong>Last Updated:</strong> {lastUpdated ? lastUpdated.toLocaleString() : 'Never'}</p>
        </div>
      </div>
    </div>
  );
};

export default Purchase;