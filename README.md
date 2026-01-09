# Graph_and_Mining_Project

This project aims to analyze the **Adventure Works** dataset using graph theory and Neo4j. It involves importing relational data into a graph database and creating bipartite and monopartite representations for further analysis.

## Setup

### Prerequisites

- **Python 3.x**
- **Docker** (to run Neo4j)

### Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

### Database Setup

To run Graph Data Science (GDS) algorithms, you must use the Neo4j Enterprise image and install the GDS plugin. Run the following command in PowerShell (Windows):

```powershell
docker run `
  --name neo4j-gds `
  -p 7474:7474 -p 7687:7687 `
  -e NEO4J_AUTH=neo4j/password `
  -e NEO4J_PLUGINS='[\"graph-data-science\"]' `
  -e NEO4J_ACCEPT_LICENSE_AGREEMENT=eval `
  neo4j:5-enterprise
```

### Data Import

Ensure the CSV files are located in the `data/` directory. Then run the import script:

```bash
python "scripts/import_neo4j.py"
```

### Graph Data Science (GDS) Analysis

Once the data is imported and the GDS plugin is active, you can run the analysis script:

```bash
python "scripts/gds_analysis.py"
```

The results and discussion are available in the [GDS_REPORT.md](GDS_REPORT.md) file.

## Dataset Description

The project uses a subset of the **Adventure Works** dataset, a classic relational database representing a global manufacturing company. The imported data includes:

- **Salespersons**: Information about employees in the sales department.
- **Regions**: Sales territories and geographic groups.
- **Products**: Catalog items sold by the company, including categories and costs.
- **Resellers**: Business partners (e.g., Value Added Resellers, Specialty Shops) that purchase products.

## Graph Implementation

The project implements several graph structures to reveal hidden patterns in the data:

### 1. Bipartite Graphs
Two primary bipartite relationships are established during the import:
- **(Salesperson)-[:ASSIGNED_TO]->(Region)**: Connects two different sets of nodes, allowing us to see which employees cover which territories.
- **(Reseller)-[:SOLD_PRODUCT]->(Product)**: Links business partners to the specific items they purchase, forming a transactional network.

### 2. Monopartite Graphs (Projections)
From the bipartite structures, we project monopartite graphs to focus on relationships within a single set of nodes:

- **Salesperson Network**:
    - **Relationship**: `(s1:Salesperson)-[:WORKS_WITH]->(s2:Salesperson)`
    - **Logic**: Two salespersons are connected if they are assigned to the same sales region.
- **Product Network**:
    - **Relationship**: `(p1:Product)-[:COMMONLY_SOLD_BY_SAME_RESELLER]->(p2:Product)`
    - **Logic**: Two products are connected if they have been sold to the same reseller, suggesting a market basket relationship.
