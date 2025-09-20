import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import styles from '../styles/Search.module.css';

export default function Search() {
  const [countries, setCountries] = useState([]);
  const [methodologies, setMethodologies] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedMethodology, setSelectedMethodology] = useState('');
  const [projectName, setProjectName] = useState('');
  const [projects, setProjects] = useState([]);
  const [cachedProjects, setCachedProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingCountries, setIsLoadingCountries] = useState(false);
  const [isLoadingMethodologies, setIsLoadingMethodologies] = useState(false);
  const [searchTimeout, setSearchTimeout] = useState(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Load countries and methodologies on page load
  useEffect(() => {
    loadCountries();
    loadMethodologies();
  }, []);

  // Auto search when country or methodology changes
  useEffect(() => {
    autoSearch();
  }, [selectedCountry, selectedMethodology]);

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
    try {
      const response = await fetch(
        `${API_BASE_URL}/search?country=${encodeURIComponent(selectedCountry)}&methodology=${encodeURIComponent(selectedMethodology)}`
      );
      const data = await response.json();
      
      // Cache the full results
      const projectsData = data.items || [];
      setCachedProjects(projectsData);
      
      // Display top 10 lexicographically
      const sortedProjects = [...projectsData].sort((a, b) => 
        (a.name || '').localeCompare(b.name || '')
      );
      setProjects(sortedProjects.slice(0, 10));
      
    } catch (error) {
      console.error('Auto search failed:', error);
      setProjects([]);
    } finally {
      setIsLoading(false);
    }
  };

  const searchByName = () => {
    const searchTerm = projectName.trim().toLowerCase();
    
    if (!searchTerm) {
      // If empty, show the current auto-search results
      const sortedProjects = [...cachedProjects].sort((a, b) => 
        (a.name || '').localeCompare(b.name || '')
      );
      setProjects(sortedProjects.slice(0, 10));
      return;
    }

    // First, search in cached results
    const matchingProjects = cachedProjects.filter(project => 
      (project.name || '').toLowerCase().includes(searchTerm)
    );

    if (matchingProjects.length > 0) {
      // Found matches in cache, display them
      const sortedMatches = matchingProjects.sort((a, b) => 
        (a.name || '').localeCompare(b.name || '')
      );
      setProjects(sortedMatches.slice(0, 10));
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
      
      // Extract items array from response
      const projectsData = data.items || [];
      const sortedProjects = [...projectsData].sort((a, b) => 
        (a.name || '').localeCompare(b.name || '')
      );
      setProjects(sortedProjects.slice(0, 10));
      
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
                {countries.map(country => (
                  <option key={country} value={country}>
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
                {methodologies.map(methodology => (
                  <option key={methodology} value={methodology}>
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
                <h3>Found {projects.length} projects:</h3>
              )}
              {projects.map((project, index) => (
                <div key={project.id || index} className={styles.projectItem}>
                  <div className={styles.projectName}>
                    {project.name || 'Unnamed Project'}
                  </div>
                  {project.country && (
                    <div className={styles.projectDetails}>
                      Country: {project.country || 'N/A'} | 
                      Category: {project.category || 'N/A'} | 
                      ID: {project.id || 'N/A'}
                    </div>
                  )}
                </div>
              ))}
            </>
          )}
        </div>
      </div>
    </>
  );
}