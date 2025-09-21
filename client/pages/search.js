import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Navbar from '../components/Navbar';
import styles from '../styles/Search.module.css';

export default function Search() {
  const [countries, setCountries] = useState([]);
  const [methodologies, setMethodologies] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedMethodology, setSelectedMethodology] = useState('');
  const [projectName, setProjectName] = useState('');
  const [projects, setProjects] = useState([]);
  const [cachedProjects, setCachedProjects] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalProjects, setTotalProjects] = useState(0);
  const [hasMoreProjects, setHasMoreProjects] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingCountries, setIsLoadingCountries] = useState(false);
  const [isLoadingMethodologies, setIsLoadingMethodologies] = useState(false);
  const [searchTimeout, setSearchTimeout] = useState(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const PROJECTS_PER_PAGE = 10;

  // Load countries and methodologies on page load
  useEffect(() => {
    loadCountries();
    loadMethodologies();
  }, []);

  // Auto search when country or methodology changes
  useEffect(() => {
    console.log('Auto search triggered - Country:', selectedCountry, 'Methodology:', selectedMethodology);
    setCurrentPage(1); // Reset to first page on new search
    autoSearch();
  }, [selectedCountry, selectedMethodology]);

  // Update displayed projects when page changes
  useEffect(() => {
    updateDisplayedProjects();
  }, [cachedProjects, currentPage]);

  // Search by name with debouncing
  useEffect(() => {
    if (searchTimeout) clearTimeout(searchTimeout);
    
    const timeout = setTimeout(() => {
      searchByName();
    }, 500);
    
    setSearchTimeout(timeout);
    
    return () => clearTimeout(timeout);
  }, [projectName]);

  const loadCountries = async () => {
    setIsLoadingCountries(true);
    try {
      const response = await fetch(`${API_BASE_URL}/search_countries`);
      const data = await response.json();
      setCountries(data.countries || []);
    } catch (error) {
      console.error('Failed to load countries:', error);
    } finally {
      setIsLoadingCountries(false);
    }
  };

  const loadMethodologies = async () => {
    setIsLoadingMethodologies(true);
    try {
      const response = await fetch(`${API_BASE_URL}/search_categories`);
      const data = await response.json();
      setMethodologies(data.categories || []);
    } catch (error) {
      console.error('Failed to load methodologies:', error);
    } finally {
      setIsLoadingMethodologies(false);
    }
  };

  const autoSearch = async () => {
    // Only search if at least one filter is selected
    if (!selectedCountry && !selectedMethodology) {
      setCachedProjects([]);
      setProjects([]);
      return;
    }

    setIsLoading(true);
    
    // Build search URL with only selected parameters
    const searchParams = new URLSearchParams();
    if (selectedCountry) searchParams.append('country', selectedCountry);
    if (selectedMethodology) searchParams.append('methodology', selectedMethodology);
    
    const searchUrl = `${API_BASE_URL}/search?${searchParams.toString()}`;
    console.log('Searching with URL:', searchUrl);
    
    try {
      const response = await fetch(searchUrl);
      const data = await response.json();
      
      console.log('API Response:', data);
      
      // Cache the full results and filter out projects with no price or supply
      const allProjects = data.items || [];
      console.log('Raw projects from API:', allProjects.length);
      
      // Let's see a sample project structure
      if (allProjects.length > 0) {
        console.log('Sample project:', allProjects[0]);
      }
      
      // OPTION 1: Show all projects (no filtering)
      // const projectsData = allProjects;
      
      // OPTION 2: Filter only projects with supply > 0 (ignore price) - ENABLED
      const projectsData = allProjects.filter(project => {
        const hasValidSupply = project.stats && project.stats.totalSupply && project.stats.totalSupply > 0;
        return hasValidSupply;
      });
      
      // OPTION 3: Current strict filtering (price > 0 AND supply > 0)
      // const projectsData = allProjects.filter(project => {
      //   const hasValidPrice = project.price && parseFloat(project.price) > 0;
      //   const hasValidSupply = project.stats && project.stats.totalSupply && project.stats.totalSupply > 0;
      //   
      //   // Debug first few projects to understand the data structure
      //   if (allProjects.indexOf(project) < 3) {
      //     console.log('Debug project structure:', {
      //       name: project.name,
      //       price: project.price,
      //       priceType: typeof project.price,
      //       stats: project.stats,
      //       totalSupply: project.stats?.totalSupply,
      //       hasValidPrice,
      //       hasValidSupply
      //     });
      //   }
      //   
      //   return hasValidPrice && hasValidSupply;
      // });
      
      console.log('Filtered projects:', projectsData.length, 'out of', allProjects.length);
      
      // Sort projects lexicographically
      const sortedProjects = [...projectsData].sort((a, b) => 
        (a.name || '').localeCompare(b.name || '')
      );
      
      setCachedProjects(sortedProjects);
      setTotalProjects(sortedProjects.length);
      // Show "100+" if we got 100 items from API (our limit) and there are more in the database
      setHasMoreProjects(allProjects.length >= 100 && data.itemsCount > allProjects.length);
      setCurrentPage(1);
      
    } catch (error) {
      console.error('Auto search failed:', error);
      setProjects([]);
    } finally {
      setIsLoading(false);
    }
  };

  const updateDisplayedProjects = () => {
    const startIndex = (currentPage - 1) * PROJECTS_PER_PAGE;
    const endIndex = startIndex + PROJECTS_PER_PAGE;
    const currentPageProjects = cachedProjects.slice(startIndex, endIndex);
    setProjects(currentPageProjects);
  };

  const searchByName = () => {
    const searchTerm = projectName.trim().toLowerCase();
    
    if (!searchTerm) {
      // If empty, show the current auto-search results (reset to first page)
      setCurrentPage(1);
      return;
    }

    // First, search in cached results
    const matchingProjects = cachedProjects.filter(project => 
      (project.name || '').toLowerCase().includes(searchTerm)
    );

    if (matchingProjects.length > 0) {
      // Found matches in cache, update cached projects and reset to first page
      const sortedMatches = matchingProjects.sort((a, b) => 
        (a.name || '').localeCompare(b.name || '')
      );
      setCachedProjects(sortedMatches);
      setTotalProjects(sortedMatches.length);
      setHasMoreProjects(false); // Local search, so no more projects
      setCurrentPage(1);
    } else {
      // No matches in cache, wait 2s then do API search
      setProjects([{ name: 'No matches in current results. Searching API in 2 seconds...' }]);
      
      setTimeout(async () => {
        await performAPISearch();
      }, 2000);
    }
  };

  const performAPISearch = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/search?country=${encodeURIComponent(selectedCountry)}&methodology=${encodeURIComponent(selectedMethodology)}&name=${encodeURIComponent(projectName)}`
      );
      const data = await response.json();
      
      // Extract items array from response and filter for Option 2 (supply only)
      const allProjects = data.items || [];
      const projectsData = allProjects.filter(project => {
        const hasValidSupply = project.stats && project.stats.totalSupply && project.stats.totalSupply > 0;
        console.log('API Search - Project:', project.name, 'Supply:', project.stats?.totalSupply, 'Price:', project.price);
        return hasValidSupply;
      });
      
      const sortedProjects = [...projectsData].sort((a, b) => 
        (a.name || '').localeCompare(b.name || '')
      );
      
      setCachedProjects(sortedProjects);
      setTotalProjects(sortedProjects.length);
      // Show "100+" if we got 100 items from API (our limit) and there are more in the database
      setHasMoreProjects(allProjects.length >= 100 && data.itemsCount > allProjects.length);
      setCurrentPage(1);
      
    } catch (error) {
      console.error('API search failed:', error);
      setProjects([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchTimeout) clearTimeout(searchTimeout);
    performAPISearch();
  };

  return (
    <>
      <Head>
        <title>Carbon Project Search</title>
        <meta name="description" content="Search carbon offset projects" />
      </Head>

      <Navbar />

      <div className={styles.container}>
        <header className={styles.header}>
          <h1>Carbon Project Search</h1>
          <Link href="/">
            <button className={styles.homeButton}>← Home</button>
          </Link>
        </header>

        <form onSubmit={handleSubmit} className={styles.searchForm}>
          <div className={styles.formGroup}>
            <label htmlFor="country">Country:</label>
            <div className={styles.selectContainer}>
              <select
                id="country"
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                className={styles.select}
              >
                <option value="">
                  {isLoadingCountries ? 'Loading countries...' : 'Select a country'}
                </option>
                {countries.map((country, index) => (
                  <option key={`${country}-${index}`} value={country}>
                    {country}
                  </option>
                ))}
              </select>
              {isLoadingCountries && <div className={styles.loader}></div>}
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="methodology">Methodology:</label>
            <div className={styles.selectContainer}>
              <select
                id="methodology"
                value={selectedMethodology}
                onChange={(e) => setSelectedMethodology(e.target.value)}
                className={styles.select}
              >
                <option value="">
                  {isLoadingMethodologies ? 'Loading methodologies...' : 'Select a methodology'}
                </option>
                {methodologies.map((methodology, index) => (
                  <option key={`${methodology}-${index}`} value={methodology}>
                    {methodology}
                  </option>
                ))}
              </select>
              {isLoadingMethodologies && <div className={styles.loader}></div>}
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="projectName">Project Name:</label>
            <input
              type="text"
              id="projectName"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Enter project name"
              className={styles.input}
            />
          </div>

          <button type="submit" disabled={isLoading} className={styles.searchButton}>
            {isLoading ? 'Searching...' : 'Search'}
            {isLoading && <div className={styles.loader}></div>}
          </button>
        </form>

        <div className={styles.results}>
          {projects.length === 0 && !isLoading ? (
            <p>No projects found.</p>
          ) : (
            <>
              {projects.length > 0 && (
                <div className={styles.resultsHeader}>
                  <h3>
                    Found {hasMoreProjects ? `${totalProjects}+` : totalProjects} projects
                    {totalProjects > PROJECTS_PER_PAGE && (
                      <span className={styles.pageInfo}>
                        {' '}(Page {currentPage} of {Math.ceil(totalProjects / PROJECTS_PER_PAGE)})
                      </span>
                    )}
                  </h3>
                  
                  {totalProjects > PROJECTS_PER_PAGE && (
                    <div className={styles.pagination}>
                      <button 
                        onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                        disabled={currentPage === 1}
                        className={styles.paginationButton}
                      >
                        ← Previous
                      </button>
                      
                      <span className={styles.pageNumbers}>
                        {Array.from({ length: Math.min(5, Math.ceil(totalProjects / PROJECTS_PER_PAGE)) }, (_, i) => {
                          const startPage = Math.max(1, currentPage - 2);
                          const pageNum = startPage + i;
                          const maxPage = Math.ceil(totalProjects / PROJECTS_PER_PAGE);
                          
                          if (pageNum > maxPage) return null;
                          
                          return (
                            <button
                              key={pageNum}
                              onClick={() => setCurrentPage(pageNum)}
                              className={`${styles.pageNumber} ${currentPage === pageNum ? styles.currentPage : ''}`}
                            >
                              {pageNum}
                            </button>
                          );
                        })}
                      </span>
                      
                      <button 
                        onClick={() => setCurrentPage(prev => Math.min(Math.ceil(totalProjects / PROJECTS_PER_PAGE), prev + 1))}
                        disabled={currentPage >= Math.ceil(totalProjects / PROJECTS_PER_PAGE)}
                        className={styles.paginationButton}
                      >
                        Next →
                      </button>
                    </div>
                  )}
                </div>
              )}
              {projects.map((project, index) => (
                <Link 
                  key={project.key || project.projectID || index} 
                  href={`/project?id=${encodeURIComponent(project.key || project.projectID || index)}&name=${encodeURIComponent(project.name || 'Unnamed Project')}`}
                  className={styles.projectItemLink}
                >
                  <div className={styles.projectItem}>
                    <div className={styles.projectHeader}>
                      <div className={styles.projectName}>
                        {project.name || 'Unnamed Project'}
                      </div>
                    {project.registry && (
                      <div className={styles.certificationBadge}>
                        <div className={styles.badgeIcon}>
                          <span className={styles.checkmark}>✓</span>
                          <div className={styles.logoPlaceholder}></div>
                        </div>
                        <span className={styles.badgeText}>
                          {project.registry} Certified
                        </span>
                      </div>
                    )}
                  </div>
                  {project.country || project.methodologies ? (
                    <div className={styles.projectDetails}>
                      <div className={styles.detailRow}>
                        <strong>Location:</strong> {project.country}{project.region ? `, ${project.region}` : ''}
                      </div>
                      {project.methodologies && project.methodologies.length > 0 && (
                        <div className={styles.detailRow}>
                          <strong>Category:</strong> {project.methodologies[0].category} ({project.methodologies[0].name})
                        </div>
                      )}
                      {project.price && (
                        <div className={styles.detailRow}>
                          <strong>Price:</strong> 
                          {parseFloat(project.price) > 0 
                            ? `$${project.price}` 
                            : `$${project.price} (Not Currently Trading)`
                          }
                        </div>
                      )}
                      {project.stats && project.stats.totalSupply && (
                        <div className={styles.detailRow}>
                          <strong>Total Supply:</strong> {project.stats.totalSupply.toLocaleString()} tons CO₂
                        </div>
                      )}
                      {project.projectID && (
                        <div className={styles.detailRow}>
                          <strong>Project ID:</strong> {project.projectID}
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>
                </Link>
              ))}
            </>
          )}
        </div>
      </div>
    </>
  );
}