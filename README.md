# Graph_and_Mining_Project: Adventure Works Semantic Knowledge Graph

This project analyzes the **Adventure Works** dataset using graph theory and Neo4j. It implements a **Semantic Knowledge Graph** capable of advanced Graph Data Science (GDS) analysis, including recommendation paths and weighted market analysis.

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

Ensure the CSV files are located in the `data/` directory. The import script includes **Entity Resolution** and **Schema Enrichment** logic.

```bash
python "scripts/import_neo4j.py"
```

### Graph Data Science (GDS) Analysis

The analysis script leverages weighted projections and multi-node knowledge graphs:

```bash
python "scripts/gds_analysis.py"
```

Detailed results and architectural justifications are available in the [GDS_REPORT.md](GDS_REPORT.md).

## Dataset & Knowledge Graph Schema

The project uses a subset of the **Adventure Works** dataset. The graph schema has been enhanced for higher connectivity and data quality:

- **Salespersons**: Nodes representing sales employees.
- **Regions**: Sales territories and geographic groups.
- **Products & Models**: Individual SKUs are linked to **ProductModel** nodes to resolve duplicates and group variants.
- **Categories**: Full hierarchy modeled via **Category** and **Subcategory** nodes.
- **Resellers & Cities**: Resellers are linked to **City** nodes for geographic co-occurrence analysis.

## Graph Implementation

### 1. Bipartite & Semantic Relationships
- **(Salesperson)-[:ASSIGNED_TO]->(Region)**: Territorial coverage.
- **(Reseller)-[:SOLD_PRODUCT]->(Product)**: Transactional link.
- **(Product)-[:BELONGS_TO_MODEL]->(ProductModel)**: Entity Resolution.
- **(Product)-[:IN_SUBCATEGORY]->(Subcategory)-[:IN_CATEGORY]->(Category)**: Hierarchical backbone.
- **(Reseller)-[:LOCATED_IN]->(City)**: Geographic linkage.

### 2. Monopartite Graphs (Projections)
The project utilizes projected graphs for GDS algorithms:

- **Salesperson Network**:
    - **Relationship**: `(s1:Salesperson)-[:WORKS_WITH]->(s2:Salesperson)` (Co-region).
- **Product Network (Weighted)**:
    - **Relationship**: `(p1:Product)-[:COMMONLY_SOLD_BY_SAME_RESELLER]->(p2:Product)`
    - **Logic**: Weighted by the number of resellers stocking both products. This "strength" property allows for more accurate community detection and centrality scoring.
- **Knowledge Graph (Enriched Pathfinding)**:
    - A multi-node projection that combines Products, Models, Categories, and Cities to allow for cross-domain path discovery (e.g., finding connections between unrelated products via shared categories or regional trends).
