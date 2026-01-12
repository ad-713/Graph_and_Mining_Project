# Business Context & Use Cases: Adventure Works Semantic Knowledge Graph

This document outlines the strategic value of the Graph & Mining Project and details specific business use cases for the implemented graph algorithms.

---

## 🏢 Business Situation: Strategic Overhaul

**Context:**
Adventure Works is a global bicycle manufacturer and distributor that sells products through a vast network of resellers (retail shops) and employs a distributed team of sales representatives.

**The Problem:**
The company sits on a mountain of transactional data (SQL tables) but lacks *structural* insight. They know *how much* they sold, but they struggle to answer relational questions:
*   "Why does a reseller in Seattle buy specific combinations of frames and helmets?"
*   "Which products drive the sales of other products?"
*   "Are our sales territories actually aligned with how our teams collaborate?"

**The Solution:**
This project ingests flat transactional data into a **Neo4j Semantic Knowledge Graph**. By modeling relationships (e.g., `COMMONLY_SOLD_BY_SAME_RESELLER`, `WORKS_WITH`), the company can move beyond simple aggregation and start performing **Graph Data Science (GDS)** to uncover hidden patterns in their supply chain and sales network.

---

## 💡 Graph-Driven Use Cases

The following use cases leverage the specific algorithms and projections implemented in the project.

### 1. Inventory & Bundle Optimization
*   **Algorithm:** **Weighted Louvain Community Detection** on the **Product Graph**.
    *   *Relationship:* [`COMMONLY_SOLD_BY_SAME_RESELLER`](scripts/import_neo4j.py:128)
    *   *Weight:* Number of resellers stocking both items.
*   **Business Application:**
    *   **Bundle Creation:** The algorithm identifies natural clusters of products (e.g., grouping specific frames with matching bottle cages and tires). Marketing can package these as "Road Ready Starter Kits."
    *   **Inventory Placement:** If a warehouse stocks a primary product, it should also stock the associated accessories identified in its community to minimize shipping splits and logistical overhead.

### 2. Supply Chain Criticality Analysis
*   **Algorithm:** **Weighted PageRank** on the **Product Graph**.
*   **Business Application:**
    *   **Risk Mitigation:** Identifies "Anchor Products" (nodes with high centrality like the "HL Road Frame"). These items are the structural hubs of the sales network.
    *   **Priority Management:** Operations must prioritize the supply chain for these items. A stockout of an Anchor Product risks breaking the sales chain for all peripheral accessories connected to it.

### 3. Sales Territory Re-Alignment
*   **Algorithm:** **Louvain Community Detection** & **PageRank** on the **Salesperson Network**.
    *   *Relationship:* [`WORKS_WITH`](scripts/import_neo4j.py:121) (based on shared regions).
*   **Business Application:**
    *   **Team Structuring:** Reveals organic collaboration clusters. If a salesperson is isolated from their assigned cluster, it may indicate a territory misalignment or a need for mentorship.
    *   **Identifying Leaders:** PageRank identifies key influencers within the sales force who can lead training initiatives or pilot new sales strategies.

### 4. Intelligent Product Substitution & Recommendation
*   **Algorithm:** **Dijkstra Shortest Path** on the **Knowledge Graph**.
    *   *Path:* `(Product A) -> (Subcategory) -> (Category) -> (Subcategory) -> (Product B)`
*   **Business Application:**
    *   **Stockout Handling:** If a specific model is out of stock, the graph finds the shortest path to a functionally identical substitute (e.g., same model, different color) via shared metadata nodes.
    *   **Cross-Selling:** Discovers non-obvious connections between disparate products (e.g., connecting a "Mountain Bike" to a specific "Road Helmet" via shared category hierarchies or regional trends).

### 5. SKU Rationalization
*   **Algorithm:** **Node Similarity (Jaccard)** on the **Product Graph**.
*   **Business Application:**
    *   **Catalog Cleanup:** Identifies products with a similarity score of 1.0 (indicating they are sold to the exact same set of resellers).
    *   **Consolidation:** The company can consolidate these SKUs or simplify tracking for variants that the market treats as functionally identical, reducing administrative and storage costs.
