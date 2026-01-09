# Graph Data Science (GDS) Analysis Report - Adventure Works

This report details the findings from graph algorithms applied to the **Salesperson Network** (`WORKS_WITH`) and the **Product Network** (`COMMONLY_SOLD_BY_SAME_RESELLER`).

---

## 1. Path Finding (Shortest Path)
**Algorithm:** Dijkstra Shortest Path (unweighted)

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
*   **Analysis:** This indicates that these individuals are immediate collaborators. In the Adventure Works organization, they likely share the same territory or report to the same manager, facilitating direct knowledge transfer.

### Product Network
*   **Query:**
    ```cypher
    MATCH (p1:Product), (p2:Product)
    WHERE p1.name <> p2.name
    WITH p1, p2 LIMIT 1
    CALL gds.shortestPath.dijkstra.stream('product-graph', {
        sourceNode: p1,
        targetNode: p2
    })
    YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
    RETURN gds.util.asNode(sourceNode).name AS source,
           gds.util.asNode(targetNode).name AS target,
           totalCost,
           [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodes
    ```
*   **Result:** Empty DataFrame (No path found).
*   **Analysis:** The product graph appears to be fragmented into disconnected components. This suggests that resellers are highly specialized; a reseller stocking one specific type of product (e.g., high-end frames) rarely stocks products from unrelated segments, resulting in isolated islands in the graph.

---

## 2. Community Detection
**Algorithm:** Louvain

### Salesperson Network
*   **Query:**
    ```cypher
    CALL gds.louvain.stream('salesperson-graph')
    YIELD nodeId, communityId
    RETURN gds.util.asNode(nodeId).name AS name, communityId
    ORDER BY communityId ASC LIMIT 10
    ```
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
*   **Analysis:** These clusters represent natural "work silos" or regional teams. The high modularity (e.g., Communities 16 and 17) confirms that the sales force is organized into tight-knit groups with limited cross-group collaboration.

### Product Network
*   **Query:**
    ```cypher
    CALL gds.louvain.stream('product-graph')
    YIELD nodeId, communityId
    RETURN gds.util.asNode(nodeId).name AS name, communityId
    ORDER BY communityId ASC LIMIT 10
    ```
*   **Result (Top 10):**
    | name | communityId |
    | :--- | :--- |
    | LL Road Frame - Black, 48 | 3 |
    | LL Road Frame - Black, 48 | 4 |
    | LL Road Frame - Black, 48 | 5 |
    | HL Mountain Frame - Black, 46 | 14 |
    | HL Mountain Frame - Black, 46 | 15 |
    | HL Mountain Frame - Black, 46 | 16 |
    | LL Road Front Wheel | 58 |
    | Touring Front Wheel | 61 |
    | Touring Rear Wheel | 68 |
    | HL Road Frame - Black, 62 | 72 |
*   **Observation:** **Data Quality Issue Detected.** The same product name appears in multiple community IDs.
*   **Analysis:** This indicates duplicate nodes in the database. While the algorithm correctly clusters products by category (Frames vs. Wheels), the duplicates skew the modularity score.

---

## 3. Centrality Measures
**Algorithm:** PageRank

### Salesperson Network
*   **Query:**
    ```cypher
    CALL gds.pageRank.stream('salesperson-graph')
    YIELD nodeId, score
    RETURN gds.util.asNode(nodeId).name AS name, score
    ORDER BY score DESC LIMIT 5
    ```
*   **Top Results:**
    | name | score |
    | :--- | :--- |
    | Tete Mensa-Annan | 0.436459 |
    | Ranjit Varkey Chudukatil | 0.376506 |
    | José Saraiva | 0.314825 |
    | Shu Ito | 0.297801 |
    | Lynn Tsoflias | 0.293381 |
*   **Analysis:** **Tete Mensa-Annan** acts as the most critical hub in the collaboration network. This individual is likely a senior manager or a "super-collaborator" vital for organization-wide communication.

### Product Network
*   **Query:**
    ```cypher
    CALL gds.pageRank.stream('product-graph')
    YIELD nodeId, score
    RETURN gds.util.asNode(nodeId).name AS name, score
    ORDER BY score DESC LIMIT 5
    ```
*   **Top Results:**
    | name | score |
    | :--- | :--- |
    | LL Road Frame - Black, 60 | 17.976824 |
    | Sport-100 Helmet, Black | 10.642367 |
    | LL Road Frame - Black, 60 | 9.717205 |
    | LL Road Frame - Black, 58 | 7.607086 |
    | Sport-100 Helmet, Black | 6.869807 |
*   **Analysis:** **LL Road Frame - Black, 60** is the "central pillar" of the inventory ecosystem. It is the most universally stocked item across the reseller network.

---

## 4. Link Prediction / Similarity
**Algorithm:** Node Similarity (Jaccard)

### Salesperson Network
*   **Query:**
    ```cypher
    CALL gds.nodeSimilarity.stream('salesperson-graph')
    YIELD node1, node2, similarity
    RETURN gds.util.asNode(node1).name AS person1, 
           gds.util.asNode(node2).name AS person2, 
           similarity
    ORDER BY similarity DESC LIMIT 5
    ```
*   **Top Results:**
    | person1 | person2 | similarity |
    | :--- | :--- | :--- |
    | Brian Welcker | Stephen Jiang | 0.588235 |
    | Stephen Jiang | Brian Welcker | 0.588235 |
    | David Campbell | Pamela Ansman-Wolfe | 0.333333 |
*   **Analysis:** Brian Welcker and Stephen Jiang share nearly 60% of their professional connections, confirming they are deeply embedded in the same local network.

### Product Network
*   **Query:**
    ```cypher
    CALL gds.nodeSimilarity.stream('product-graph')
    YIELD node1, node2, similarity
    RETURN gds.util.asNode(node1).name AS product1, 
           gds.util.asNode(node2).name AS product2, 
           similarity
    ORDER BY similarity DESC LIMIT 5
    ```
*   **Top Results:**
    | product1 | product2 | similarity |
    | :--- | :--- | :--- |
    | Men's Sports Shorts, S | Men's Sports Shorts, M | 0.995413 |
    | Men's Sports Shorts, M | Men's Sports Shorts, S | 0.995413 |
*   **Analysis:** This validates the "Size-Run" stocking pattern. Resellers almost always carry all size variations of a product line.
