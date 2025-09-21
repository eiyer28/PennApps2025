import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import Head from 'next/head';
import MenuBar from './menu-bar.jsx';
import styles from '../styles/Project.module.css';

const ProjectDetails = () => {
  const router = useRouter();
  const { id, name } = router.query;
  const [loading, setLoading] = useState(true);
  const [projectData, setProjectData] = useState(null);
  const [error, setError] = useState(null);
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
  const [user, setUser] = useState(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Check user authentication status
  useEffect(() => {
    try {
      const userData = localStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
    }
  }, []);

  useEffect(() => {
    const fetchProjectData = async () => {
      if (!id) return;

      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${API_BASE_URL}/project/${encodeURIComponent(id)}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch project: ${response.status}`);
        }

        const data = await response.json();
        setProjectData(data);
      } catch (err) {
        console.error('Error fetching project data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProjectData();
  }, [id, API_BASE_URL]);

  // Helper function to truncate description to 3 lines (approximately 200 characters)
  const truncateDescription = (text, maxLength = 200) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>
          <div className={styles.spinner}></div>
          <p>Loading project details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <Link href="/search" className={styles.backButton}>
            ← Back to Search
          </Link>
          <h1 className={styles.title}>Project Not Found</h1>
        </div>
        <div className={styles.content}>
          <div className={styles.errorCard}>
            <div className={styles.errorIcon}>⚠️</div>
            <h2>Unable to Load Project</h2>
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
    <>
      <Head>
        <title>Project Details - Carbon Chain</title>
        <meta name="description" content="View carbon project details" />
      </Head>

      <MenuBar />

      <div className={styles.container} style={{paddingTop: '100px'}}>
        <div className={styles.header}>
          <Link href="/search" className={styles.backButton}>
            ← Back to Search
          </Link>
          <h1 className={styles.title}>Project Details</h1>
        </div>

      <div className={styles.content}>
        <div className={styles.projectCard}>
          <div className={styles.projectHeader}>
            <div className={styles.projectTitleRow}>
              <h2 className={styles.projectName}>
                {projectData?.name || name ? decodeURIComponent(name) : 'Project Name'}
              </h2>
              {user ? (
                <Link 
                  href={`/purchase?id=${encodeURIComponent(projectData?.key || id || '')}&name=${encodeURIComponent(projectData?.name || name || 'Unnamed Project')}`}
                  className={styles.purchaseButton}
                >
                  🛒 Purchase Credits
                </Link>
              ) : (
                <Link 
                  href="/login?message=Please log in to purchase carbon credits."
                  className={styles.purchaseButtonDisabled}
                >
                  🔒 Login to Purchase
                </Link>
              )}
            </div>
            <div className={styles.projectId}>
              <strong>Project ID:</strong> {projectData?.key || projectData?.projectID || id || 'N/A'}
            </div>
            {projectData?.registry && (
              <div className={styles.certificationBadge}>
                <span className={styles.checkmark}>✓</span>
                <span>{projectData.registry} Certified</span>
              </div>
            )}
          </div>

          {/* Project Overview */}
          {projectData?.description && (
            <div className={styles.section}>
              <h3>📋 Project Overview</h3>
              <div className={styles.descriptionContainer}>
                <p className={styles.description}>
                  {isDescriptionExpanded 
                    ? projectData.description 
                    : truncateDescription(projectData.description)
                  }
                </p>
                {projectData.description.length > 200 && (
                  <button 
                    className={styles.expandButton}
                    onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                  >
                    {isDescriptionExpanded ? '📖 Show Less' : '📖 Read More'}
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Location & Methodology */}
          <div className={styles.section}>
            <h3>🌍 Location & Methodology</h3>
            <div className={styles.detailGrid}>
              {projectData?.country && (
                <div className={styles.detailItem}>
                  <strong>Country:</strong> {projectData.country}
                  {projectData.region && `, ${projectData.region}`}
                </div>
              )}
              {projectData?.methodologies && projectData.methodologies.length > 0 && (
                <div className={styles.detailItem}>
                  <strong>Category:</strong> {projectData.methodologies[0].category}
                </div>
              )}
              {projectData?.methodologies && projectData.methodologies.length > 0 && (
                <div className={styles.detailItem}>
                  <strong>Methodology:</strong> {projectData.methodologies[0].name}
                </div>
              )}
              {projectData?.vintage && (
                <div className={styles.detailItem}>
                  <strong>Vintage:</strong> {projectData.vintage}
                </div>
              )}
            </div>
          </div>

          {/* Trading Information */}
          <div className={styles.section}>
            <h3>💰 Trading Information</h3>
            <div className={styles.detailGrid}>
              {projectData?.price !== undefined && (
                <div className={styles.detailItem}>
                  <strong>Current Price:</strong>
                  <span className={styles.price}>
                    {parseFloat(projectData.price) > 0 
                      ? ` $${projectData.price}` 
                      : ` $${projectData.price} (Not Currently Trading)`
                    }
                  </span>
                </div>
              )}
              {projectData?.stats?.totalSupply && (
                <div className={styles.detailItem}>
                  <strong>Total Supply:</strong> {projectData.stats.totalSupply.toLocaleString()} tons CO₂
                </div>
              )}
              {projectData?.stats?.totalRetired && (
                <div className={styles.detailItem}>
                  <strong>Total Retired:</strong> {projectData.stats.totalRetired.toLocaleString()} tons CO₂
                </div>
              )}
            </div>
          </div>

          {/* Project Images */}
          {projectData?.images && projectData.images.length > 0 && (
            <div className={styles.section}>
              <h3>� Project Images</h3>
              <div className={styles.imageGrid}>
                {projectData.images.map((image, index) => (
                  <div key={index} className={styles.imageContainer}>
                    <img 
                      src={image.url} 
                      alt={image.caption || `Project image ${index + 1}`}
                      className={styles.projectImage}
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                    {image.caption && (
                      <p className={styles.imageCaption}>{image.caption}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Additional Information */}
          {(projectData?.developer || projectData?.url) && (
            <div className={styles.section}>
              <h3>ℹ️ Additional Information</h3>
              <div className={styles.detailGrid}>
                {projectData?.developer && (
                  <div className={styles.detailItem}>
                    <strong>Developer:</strong> {projectData.developer}
                  </div>
                )}
                {projectData?.url && (
                  <div className={styles.detailItem}>
                    <strong>Project Website:</strong>
                    <a 
                      href={projectData.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className={styles.externalLink}
                    >
                      Visit Project Site →
                    </a>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Debug Information */}
          <div className={styles.debugInfo}>
            <h4>Debug Information:</h4>
            <p><strong>Project ID:</strong> {projectData?.projectID || id || 'Not provided'}</p>
            <p><strong>Project Name:</strong> {projectData?.name || (name ? decodeURIComponent(name) : 'Not provided')}</p>
            <p><strong>API Response Keys:</strong> {projectData ? Object.keys(projectData).join(', ') : 'No data'}</p>
          </div>
        </div>
      </div>
      </div>
    </>
  );
};

export default ProjectDetails;