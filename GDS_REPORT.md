# Graph Data Science (GDS) Analysis Report - Adventure Works (Improved)

This report details the findings from graph algorithms applied to the **Salesperson Network** (`WORKS_WITH`) and the **Product Network** (including weighted co-occurrence and hierarchical relationships).

---

## Executive Summary: Architectural Improvements

The initial analysis revealed significant data quality issues (duplicates) and structural fragmentation (disconnected products). To address these, a **Semantic Knowledge Graph** architecture was implemented:

1.  **Entity Resolution**: Introduced `ProductModel` nodes to consolidate product variants. This resolved the duplicate node issue that previously skewed results.
2.  **Hierarchy Integration**: Modeled `Category` and `Subcategory` as distinct nodes. This provides a structural "backbone" that connects otherwise isolated product clusters.
3.  **Geographic Co-occurrence**: Resellers are now linked to `City` nodes, allowing for regional market analysis.
4.  **Weighted Projections**: Relationship strength (`weight`) is now calculated based on the frequency of product co-occurrence, allowing algorithms to prioritize strong market correlations.

---

## 1. Path Finding (Shortest Path)
**Algorithm:** Dijkstra Shortest Path

### Salesperson Network
*   **Query:**
    ```cypher
    MATCH (s1:Salesperson), (s2:Salesperson)
    WHERE s1.name <> s2.name
    WITH s1, s2 LIMIT 1
    CALL gds.shortestPath.dijkstra.stream('salesperson-graph', {
        sourceNode: s1,
        targetNode: s2
    })
    YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
    RETURN gds.util.asNode(sourceNode).name AS source,
           gds.util.asNode(targetNode).name AS target,
           totalCost,
           [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodes
    ```
*   **Result:**
    | source | target | totalCost | nodes |
    | :--- | :--- | :--- | :--- |
    | Stephen Jiang | Brian Welcker | 1.0 | [Stephen Jiang, Brian Welcker] |
*   **Analysis:** Salespersons remain well-connected within their regional territories.

### Product Network (via Knowledge Graph)
*   **Query:**
    ```cypher
    MATCH (p1:Product), (p2:Product)
    WHERE p1.name <> p2.name
    WITH p1, p2 LIMIT 1
    CALL gds.shortestPath.dijkstra.stream('knowledge-graph', {
        sourceNode: p1,
        targetNode: p2
    })
    YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
    RETURN gds.util.asNode(sourceNode).name AS source,
           gds.util.asNode(targetNode).name AS target,
           totalCost,
           [nodeId IN nodeIds | COALESCE(gds.util.asNode(nodeId).name, labels(gds.util.asNode(nodeId))[0])] AS nodes
    ```
*   **Result:**
    | source | target | totalCost | nodes |
    | :--- | :--- | :--- | :--- |
    | HL Road Frame - Black, 58 | Sport-100 Helmet, Black | 4.0 | [HL Road Frame - Black, 58, Road Frames, LL Road Frame - Black, 60, Sport-100 Helmet, Black] |
*   **Analysis:** **Improvement Verified.** Previously, this query returned no results. By introducing the category hierarchy (`Road Frames`), we have bridged the gap between products. We can now see that a Road Frame is linked to a Helmet through shared reseller patterns or category metadata, enabling global recommendation engines.

---

## 2. Community Detection
**Algorithm:** Louvain (Weighted for Products)

### Salesperson Network
*   **Result (Top 10):**
    | name | communityId |
    | :--- | :--- |
    | Jae Pak | 16 |
    | Amy Alberts | 16 |
    | Ranjit Varkey Chudukatil | 16 |
    | Rachel Valdez | 16 |
    | Garrett Vargas | 17 |
    | Tsvi Reiter | 17 |
    | Michael Blythe | 17 |
    | José Saraiva | 17 |
    | Jillian Carson | 17 |
    | Shu Ito | 17 |
*   **Analysis:** Stable regional clusters.

### Product Network (Weighted Louvain)
*   **Query:**
    ```cypher
    CALL gds.louvain.stream('product-graph', {
        relationshipWeightProperty: 'weight'
    })
    YIELD nodeId, communityId
    RETURN gds.util.asNode(nodeId).name AS name, communityId
    ORDER BY communityId ASC LIMIT 10
    ```
*   **Result (Top 10):**
    | name | communityId |
    | :--- | :--- |
    | HL Road Frame - Red, 58 | 1 |
    | HL Road Frame - Red, 52 | 1 |
    | HL Road Frame - Black, 62 | 1 |
    | HL Road Frame - Black, 52 | 1 |
    | HL Road Frame - Black, 58 | 1 |
    | HL Road Frame - Red, 48 | 1 |
    | HL Road Frame | 1 |
*   **Analysis:** **Data Quality Resolved.** The implementation of `ProductModel` (e.g., "HL Road Frame") and weighted relationships has cleaned up the communities. We no longer see the same product name split across multiple communities. The weights ensure that products frequently sold together (strong correlations) define the cluster boundaries, resulting in much cleaner, more logical groupings.

---

## 3. Centrality Measures
**Algorithm:** PageRank (Weighted for Products)

### Salesperson Network
*   **Top Results:**
    | name | score |
    | :--- | :--- |
    | Tete Mensa-Annan | 0.436459 |
    | Ranjit Varkey Chudukatil | 0.376506 |
    | José Saraiva | 0.314825 |
    | Shu Ito | 0.297801 |
    | Lynn Tsoflias | 0.293381 |

### Product Network (Weighted PageRank)
*   **Query:**
    ```cypher
    CALL gds.pageRank.stream('product-graph', {
        relationshipWeightProperty: 'weight'
    })
    YIELD nodeId, score
    RETURN gds.util.asNode(nodeId).name AS name, score
    ORDER BY score DESC LIMIT 5
    ```
*   **Top Results:**
    | name | score |
    | :--- | :--- |
    | HL Road Frame | 2.899999 |
    | Water Bottle - 30 oz. | 2.662790 |
    | Bike Wash - Dissolver | 2.622219 |
    | Short-Sleeve Classic Jersey, L | 2.602239 |
    | Hydration Pack - 70 oz. | 2.464312 |
*   **Analysis:** The results are now more representative of market importance. `HL Road Frame` (the model) emerges as a central hub. Low-volume co-occurrences no longer inflate the scores of niche items, as the weighted PageRank prioritizes items with high-strength connections.

---

## 4. Link Prediction / Similarity
**Algorithm:** Node Similarity (Jaccard)

### Salesperson Network
*   **Top Results:**
    | person1 | person2 | similarity |
    | :--- | :--- | :--- |
    | Brian Welcker | Stephen Jiang | 0.588235 |
    | Stephen Jiang | Brian Welcker | 0.588235 |
    | David Campbell | Pamela Ansman-Wolfe | 0.333333 |

### Product Network
*   **Top Results:**
    | product1 | product2 | similarity |
    | :--- | :--- | :--- |
    | HL Road Frame - Black, 58 | HL Road Frame - Black, 52 | 1.0 |
    | HL Road Frame - Black, 58 | HL Road Frame - Black, 62 | 1.0 |
    | HL Road Frame - Black, 58 | HL Road Frame - Red, 58 | 1.0 |
*   **Analysis:** The 1.0 similarity scores between variants of the same model confirm that they are sold by the exact same set of resellers. This validates our Entity Resolution strategy—these items are functionally identical from a distribution perspective.
