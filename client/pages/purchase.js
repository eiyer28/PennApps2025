import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import styles from '../styles/Purchase.module.css';

const Purchase = () => {
  const router = useRouter();
  const { id, name } = router.query;
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading time for now
    const timer = setTimeout(() => {
      setLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

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

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Link href={`/project?id=${encodeURIComponent(id || '')}&name=${encodeURIComponent(name || '')}`} className={styles.backButton}>
          ← Back to Project
        </Link>
        <h1 className={styles.title}>Purchase Carbon Credits</h1>
      </div>

      <div className={styles.content}>
        <div className={styles.purchaseCard}>
          <div className={styles.projectInfo}>
            <h2 className={styles.projectName}>
              {name ? decodeURIComponent(name) : 'Project Name'}
            </h2>
            <div className={styles.projectId}>
              <strong>Project ID:</strong> {id || 'N/A'}
            </div>
          </div>

          <div className={styles.placeholderSection}>
            <div className={styles.placeholderIcon}>🛒</div>
            <h3>Purchase Feature Coming Soon</h3>
            <p>
              We're building a comprehensive carbon credit purchasing system. This page will include:
            </p>
            <ul className={styles.featureList}>
              <li>💰 Real-time pricing and availability</li>
              <li>📊 Quantity selection and price calculation</li>
              <li>💳 Secure payment processing</li>
              <li>📄 Digital certificate generation</li>
              <li>📈 Portfolio tracking and management</li>
              <li>🔐 Blockchain verification and transparency</li>
            </ul>
          </div>

          <div className={styles.debugInfo}>
            <h4>Debug Information:</h4>
            <p><strong>Project ID:</strong> {id || 'Not provided'}</p>
            <p><strong>Project Name:</strong> {name ? decodeURIComponent(name) : 'Not provided'}</p>
            <p><strong>Current URL:</strong> {router.asPath}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Purchase;