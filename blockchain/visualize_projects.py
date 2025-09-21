import requests
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import os
from dotenv import load_dotenv
from typing import Dict, List
from enum import Enum

class ProjectState(Enum):
    PROPOSED = "Proposed"
    VERIFIED = "Verified"
    REJECTED = "Rejected"
    CANCELED = "Canceled"

class ProjectVisualizer:
    def __init__(self):
        """Initialize the visualizer with API connection"""
        self.api_url = "http://127.0.0.1:9000"
        load_dotenv("test_accounts.env")

        # Color scheme for different project states
        self.state_colors = {
            ProjectState.PROPOSED.value: '#ADD8E6',  # Light blue
            ProjectState.VERIFIED.value: '#90EE90',  # Light green
            ProjectState.REJECTED.value: '#FFB6C1',  # Light red
            ProjectState.CANCELED.value: '#D3D3D3'   # Light gray
        }

    def fetch_projects(self) -> List[dict]:
        """Fetch all projects from the API"""
        try:
            response = requests.get(f"{self.api_url}/projects")
            response.raise_for_status()
            projects = response.json()["projects"]
            
            # Fetch details for each project
            project_details = []
            for project_address in projects:
                details = requests.get(f"{self.api_url}/project/{project_address}")
                if details.status_code == 200:
                    project_data = details.json()["project"]
                    project_data["address"] = project_address
                    project_details.append(project_data)
            
            return project_details
        except requests.exceptions.RequestException as e:
            print(f"Error fetching projects: {str(e)}")
            return []

    def analyze_projects(self) -> Dict:
        """
        Analyzes all projects and their funding relationships
        Returns a tree structure of initiatives and their funders
        """
        projects = self.fetch_projects()
        
        # Initialize data structures
        initiative_tree = defaultdict(lambda: {
            'total_funding': 0,
            'funders': defaultdict(lambda: {'amount': 0.0, 'projects': set()}),
            'projects': [],
            'states': defaultdict(int)
        })

        # Analyze each project
        for project in projects:
            initiative = project.get("initiative", "Unknown Initiative")
            contributors = project.get("contributors", [])  # Expecting a list of contributions
            state = project.get("state", ProjectState.PROPOSED.value)

            initiative_data = initiative_tree[initiative]
            initiative_data['projects'].append({
                'address': project["address"],
                'state': state,
                'goal': project.get("goal", 0)
            })
            initiative_data['states'][state] += 1

            # Analyze funding
            if isinstance(contributors, dict):
                # Handle dict-style contributors
                for funder, contribution in contributors.items():
                    amount = float(contribution.get("amount", 0))
                    initiative_data['funders'][funder]['amount'] += amount
                    initiative_data['funders'][funder]['projects'].add(project["address"])
                    initiative_data['total_funding'] += amount
            else:
                # Handle list-style contributors
                for contribution in contributors:
                    funder = contribution.get("address", "unknown")
                    amount = float(contribution.get("amount", 0))
                    initiative_data['funders'][funder]['amount'] += amount
                    initiative_data['funders'][funder]['projects'].add(project["address"])
                    initiative_data['total_funding'] += amount

        return dict(initiative_tree)

    def visualize_funding_network(self, data: Dict, show: bool = True):
        """Creates a network visualization of funding relationships"""
        G = nx.Graph()
        
        # Add initiative nodes
        for initiative, info in data.items():
            if info['total_funding'] > 0:
                # Calculate dominant state for color
                states = info['states']
                dominant_state = max(states.items(), key=lambda x: x[1])[0]
                node_color = self.state_colors.get(dominant_state, '#ADD8E6')

                node_size = min(15000, max(5000, info['total_funding'] * 200))
                G.add_node(initiative, node_type='initiative',
                          size=node_size, color=node_color,
                          total_funding=info['total_funding'],
                          num_projects=len(info['projects']))
 # Add funder nodes and connections
                for funder, funder_info in info['funders'].items():
                    funder_id = f"funder_{funder[:8]}"
                    if not G.has_node(funder_id):
                        num_projects = len(funder_info['projects'])
                        funder_size = 2000 + (num_projects * 500)
                        G.add_node(funder_id, node_type='funder',
                                 size=funder_size, color='#98FB98')
                    G.add_edge(funder_id, initiative,
                             weight=funder_info['amount'],
                             num_projects=len(funder_info['projects']))

        if len(G.nodes) == 0:
            print("No funded projects found to visualize")
            return

        # Create visualization
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Draw nodes
        initiative_nodes = [n for n in G.nodes if G.nodes[n]['node_type'] == 'initiative']
        funder_nodes = [n for n in G.nodes if G.nodes[n]['node_type'] == 'funder']
        
        nx.draw_networkx_nodes(G, pos, nodelist=initiative_nodes,
                             node_color=[G.nodes[n]['color'] for n in initiative_nodes],
                             node_size=[G.nodes[n]['size'] for n in initiative_nodes])
        nx.draw_networkx_nodes(G, pos, nodelist=funder_nodes,
                             node_color='#98FB98',
                             node_size=[G.nodes[n]['size'] for n in funder_nodes])

        # Draw edges with weights
        edge_weights = [G[u][v]['weight']/3 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.6)

        # Add labels with more info
        labels = {}
        for node in G.nodes:
            if G.nodes[node]['node_type'] == 'initiative':
                total_eth = G.nodes[node]['total_funding']
                num_proj = G.nodes[node]['num_projects']
                labels[node] = f"{node}\n{total_eth:.2f} ETH\n{num_proj} projects"
            else:
                addr = node.split('_')[1]
                num_proj = len([e for e in G.edges(node)])
                labels[node] = f"Funder\n{addr}\n{num_proj} projects"

        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        # Add legend for states
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                    markerfacecolor=color, label=state,
                                    markersize=10)
                         for state, color in self.state_colors.items()]
        plt.legend(handles=legend_elements, loc='upper left', title='Project States')

        plt.title("Carbon Project Funding Network")
        plt.savefig('funding_network.png', dpi=300, bbox_inches='tight')
        plt.close()

    def export_tree_structure(self, data: Dict, output_file: str = 'funding_tree.json'):
        """Exports the funding tree structure to a JSON file"""
        import json
        
        # Convert defaultdict to regular dict and format amounts
        formatted_data = {}
        for initiative, info in data.items():
            formatted_data[initiative] = {
                'total_funding': info['total_funding'],
                'funders': {
                    funder: {
                        'amount': funder_info['amount'],
                        'projects': list(funder_info['projects'])
                    }
                    for funder, funder_info in info['funders'].items()
                },
                'projects': info['projects'],
                'states': dict(info['states'])
            }
            
        with open(output_file, 'w') as f:
            json.dump(formatted_data, f, indent=2)
        print(f"Tree structure exported to {output_file}")

def main():
    visualizer = ProjectVisualizer()
    
    print("Fetching and analyzing project data...")
    funding_data = visualizer.analyze_projects()
    
    print("Creating network visualization...")
    visualizer.visualize_funding_network(funding_data, show=True)
    
    print("Exporting tree structure...")
    visualizer.export_tree_structure(funding_data)
    
    print("\nVisualization complete!")
    print("- Network graph saved as 'funding_network.png'")
    print("- Funding tree structure saved as 'funding_tree.json'")

if __name__ == "__main__":
    main()
