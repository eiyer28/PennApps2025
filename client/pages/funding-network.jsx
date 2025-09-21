import { useEffect, useState, useRef } from 'react';
import Head from 'next/head';
import MenuBar from './menu-bar.jsx';
import styles from '../styles/Project.module.css';
import * as d3 from 'd3';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function transformFundingTreeToGraph(data) {
  const nodes = [];
  const links = [];
  const addedNodes = new Set();

  Object.entries(data).forEach(([initiative, info]) => {
    // Add initiative node with verifier and beneficiary info
    if (!addedNodes.has(initiative)) {
      const verifiers = info.verifiers ? info.verifiers.join(', ') : 'Unknown Verifier';
      const beneficiaries = info.beneficiaries ? info.beneficiaries.join(', ') : 'Unknown Beneficiary';

      nodes.push({
        id: initiative,
        type: 'initiative',
        name: initiative,
        title: initiative,
        funding: info.total_funding_usd,
        verifiers: verifiers,
        beneficiaries: beneficiaries,
        label: `${initiative}\n$${info.total_funding_usd} USD\nVerifier: ${verifiers}\nBeneficiary: ${beneficiaries}`,
        width: Math.max(200, initiative.length * 8 + 40), // Added 40px more width for padding
        height: 100 // Increased from 80 to 100 for more padding
      });
      addedNodes.add(initiative);
    }

    // Add funder nodes and links
    Object.entries(info.funders).forEach(([funder, funderInfo]) => {
      // Use the display_name from the API response, fallback to shortened address
      const displayName = funderInfo.display_name || `${funder.substring(0, 8)}...`;
      const email = funderInfo.email || funder;

      if (!addedNodes.has(funder)) {
        nodes.push({
          id: funder,
          type: 'funder',
          name: displayName,
          title: displayName,
          email: email,
          funding: funderInfo.amount_usd,
          label: `${displayName}\n${email}\n$${funderInfo.amount_usd} USD`,
          width: Math.max(140, displayName.length * 10 + 40), // Added 20px more width for padding
          height: 90 // Increased from 70 to 90 for more padding
        });
        addedNodes.add(funder);
      }

      links.push({
        source: funder,
        target: initiative,
        value: funderInfo.amount_usd
      });
    });
  });

  return { nodes, links };
}

export default function FundingNetwork() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const svgRef = useRef();

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE_URL}/funding_tree`);
        if (!res.ok) throw new Error('Failed to fetch funding tree');
        const data = await res.json();
        setGraphData(transformFundingTreeToGraph(data));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  useEffect(() => {
    if (!graphData.nodes.length || loading || error) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous render

    // Make canvas 1700x1000
    const containerWidth = 1700;
    const containerHeight = 750;

    svg.attr("width", containerWidth).attr("height", containerHeight)
       .style("background-color", "var(--background)");

    // Set initial positions to spread nodes out and prevent overlap
    graphData.nodes.forEach((node, i) => {
      const angle = (i / graphData.nodes.length) * 2 * Math.PI;
      const radius = Math.min(containerWidth, containerHeight) * 0.3;
      node.x = containerWidth / 2 + Math.cos(angle) * radius;
      node.y = containerHeight / 2 + Math.sin(angle) * radius;

      // Pre-fix initial positions to prevent bouncing
      node.fx = node.x;
      node.fy = node.y;
    });

    // Create simulation with gentler forces and lower alpha
    const simulation = d3.forceSimulation(graphData.nodes)
      .alpha(0.01) // Lower starting energy (default is 1)
      .alphaDecay(0.05) // Slower decay for smoother transitions
      .velocityDecay(1) // Higher value creates more friction (default is 0.4)
      .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(200))
      .force("charge", d3.forceManyBody().strength(-100)) // Further reduced from -800 to -600
      .force("center", d3.forceCenter(containerWidth / 2, containerHeight / 2))
      .force("collision", d3.forceCollide().radius(d => Math.max(d.width, d.height) / 2 + 40))
      .force("x", d3.forceX(containerWidth / 2).strength(0.03)) // Gentler centering force
      .force("y", d3.forceY(containerHeight / 2).strength(0.03)); // Gentler centering force



    // Create arrow markers for links
    svg.append("defs").selectAll("marker")
      .data(["arrow"])
      .enter().append("marker")
      .attr("id", d => d)
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 25)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#666");

    // Create links
    const link = svg.append("g")
      .selectAll("line")
      .data(graphData.links)
      .enter().append("line")
      .attr("stroke", "#666")
      .attr("stroke-opacity", 0.8)
      .attr("stroke-width", d => Math.max(2, d.value / 2))
      .attr("marker-end", "url(#arrow)");

    // Create node groups
    const nodeGroup = svg.append("g")
      .selectAll("g")
      .data(graphData.nodes)
      .enter().append("g")
      .style("cursor", "pointer")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Add rounded rectangles with palette colors
    nodeGroup.append("rect")
      .attr("width", d => d.width)
      .attr("height", d => d.height)
      .attr("x", d => -d.width/2)
      .attr("y", d => -d.height/2)
      .attr("rx", 15)
      .attr("ry", 15)
      .attr("fill", d => d.type === 'initiative' ? '#7aceb5' : '#ffd182') // Use --maincolor and --subcolor from palette
      .attr("stroke", "none") // Removed black border
      .attr("stroke-width", 0);

    // Add title text with consistent font - vertically centered
    nodeGroup.append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "-0.8em") // Adjusted for better vertical centering
      .attr("font-size", "16px")
      .attr("font-weight", "bold")
      .attr("font-family", "Helvetica")
      .attr("fill", "#142233")
      .style("pointer-events", "none")
      .text(d => d.title);

    // Add funding text - vertically centered
    nodeGroup.append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "0.3em") // Adjusted for better vertical centering
      .attr("font-size", "14px")
      .attr("font-family", "Helvetica")
      .attr("fill", "#142233")
      .style("pointer-events", "none")
      .text(d => `$${d.funding} USD`);

    // Add verifier text for initiatives - vertically centered
    nodeGroup.filter(d => d.type === 'initiative')
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "1.4em") // Adjusted for better vertical centering
      .attr("font-size", "12px")
      .attr("font-family", "Helvetica")
      .attr("fill", "#142233")
      .style("pointer-events", "none")
      .text(d => `Verifier: ${d.verifiers}`);

    // Add beneficiary text for initiatives - vertically centered
    nodeGroup.filter(d => d.type === 'initiative')
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "2.4em") // Adjusted for better vertical centering
      .attr("font-size", "12px")
      .attr("font-family", "Helvetica")
      .attr("fill", "#142233")
      .style("pointer-events", "none")
      .text(d => `Beneficiary: ${d.beneficiaries}`);

    // Add email text for funders - vertically centered
    nodeGroup.filter(d => d.type === 'funder')
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "1.6em") // Adjusted for better vertical centering
      .attr("font-size", "12px")
      .attr("font-family", "Helvetica")
      .attr("fill", "#142233")
      .style("pointer-events", "none")
      .text(d => d.email);

    // Add tooltips
    nodeGroup.append("title")
      .text(d => d.label);

    // Add click handlers
    nodeGroup.on("click", function(event, d) {
      alert(d.label);
    });

    // Update positions on tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      nodeGroup
        .attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // Drag functions - no spring back behavior
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      // Don't reset fx and fy - this prevents spring back
      // d.fx = null;
      // d.fy = null;
    }

    return () => {
      simulation.stop();
    };
  }, [graphData, loading, error]);

  return (
    <div className={styles.container}>
      <Head>
        <title>Funding Network Visualization</title>
      </Head>
      <MenuBar />
      <h1>Funding Network Visualization</h1>
      {loading && <p>Loading network...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {!loading && !error && graphData.nodes.length === 0 && (
        <p>No funding data available to visualize.</p>
      )}
      {!loading && !error && graphData.nodes.length > 0 && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          border: '1px solid #ccc',
          borderRadius: '8px',
          padding: '20px',
          margin: '20px 0',
          backgroundColor: 'var(--background)' // Use same background as index page
        }}>
          <svg ref={svgRef}></svg>

          {/* Legend moved inside the container */}
          <div style={{
            marginTop: '20px',
            fontSize: '12px',
            color: '#666',
            maxWidth: '1100px',
            textAlign: 'left',
            lineHeight: '1.4'
          }}>
            <p><strong>Legend:</strong></p>
            <p>🟢 <strong>Teal boxes</strong> = Initiatives (projects receiving funding with verifier and beneficiary info)</p>
            <p>🟨 <strong>Gold boxes</strong> = Funders (users providing funding with contact details)</p>
          </div>
        </div>
      )}
    </div>
  );
}
