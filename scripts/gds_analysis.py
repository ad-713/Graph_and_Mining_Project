from graphdatascience import GraphDataScience
import pandas as pd
import os

# Configuration
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password"

class GDSAnalysis:
    def __init__(self, uri, user, password):
        self.gds = GraphDataScience(uri, auth=(user, password))
        
    def close(self):
        self.gds.close()

    def setup_projections(self):
        print("Setting up graph projections...")
        # Drop existing projections if they exist
        self.gds.run_cypher("CALL gds.graph.drop('salesperson-graph', false)")
        self.gds.run_cypher("CALL gds.graph.drop('product-graph', false)")
        self.gds.run_cypher("CALL gds.graph.drop('knowledge-graph', false)")

        # Salesperson projection
        self.gds.graph.project(
            "salesperson-graph",
            "Salesperson",
            "WORKS_WITH"
        )

        # Product projection (Weighted)
        self.gds.graph.project(
            "product-graph",
            ["Product", "ProductModel"],
            {
                "COMMONLY_SOLD_BY_SAME_RESELLER": {"orientation": "UNDIRECTED", "properties": "weight"},
                "BELONGS_TO_MODEL": {"orientation": "UNDIRECTED", "properties": {"weight": {"defaultValue": 1.0}}}
            }
        )

        # Knowledge Graph projection (Hierarchical)
        self.gds.graph.project(
            "knowledge-graph",
            ["Product", "Subcategory", "Category", "Reseller", "City"],
            {
                "IN_SUBCATEGORY": {"orientation": "UNDIRECTED"},
                "IN_CATEGORY": {"orientation": "UNDIRECTED"},
                "SOLD_PRODUCT": {"orientation": "UNDIRECTED"},
                "LOCATED_IN": {"orientation": "UNDIRECTED"}
            }
        )

    def run_path_finding(self):
        print("\n--- Path Finding ---")
        # 1. Salesperson: Shortest Path
        res = self.gds.run_cypher("""
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
        """)
        print("Salesperson Shortest Path:")
        print(res)

        # 2. Product: Shortest Path (using Knowledge Graph for better connectivity)
        print("Product Shortest Path (via Knowledge Graph):")
        res = self.gds.run_cypher("""
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
        """)
        print(res)

    def run_communities(self):
        print("\n--- Community Detection ---")
        # 1. Salesperson: Louvain
        res = self.gds.run_cypher("""
            CALL gds.louvain.stream('salesperson-graph')
            YIELD nodeId, communityId
            RETURN gds.util.asNode(nodeId).name AS name, communityId
            ORDER BY communityId ASC LIMIT 10
        """)
        print("Salesperson Communities (Louvain):")
        print(res)

        # 2. Product: Louvain (Weighted)
        res = self.gds.run_cypher("""
            CALL gds.louvain.stream('product-graph', {
                relationshipWeightProperty: 'weight'
            })
            YIELD nodeId, communityId
            RETURN gds.util.asNode(nodeId).name AS name, communityId
            ORDER BY communityId ASC LIMIT 10
        """)
        print("Product Communities (Louvain, Weighted):")
        print(res)

    def run_centralities(self):
        print("\n--- Centrality Measures ---")
        # 1. Salesperson: PageRank
        res = self.gds.run_cypher("""
            CALL gds.pageRank.stream('salesperson-graph')
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).name AS name, score
            ORDER BY score DESC LIMIT 5
        """)
        print("Salesperson Top Centrality (PageRank):")
        print(res)

        # 2. Product: PageRank (Weighted)
        res = self.gds.run_cypher("""
            CALL gds.pageRank.stream('product-graph', {
                relationshipWeightProperty: 'weight'
            })
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).name AS name, score
            ORDER BY score DESC LIMIT 5
        """)
        print("Product Top Centrality (PageRank, Weighted):")
        print(res)

    def run_link_prediction(self):
        print("\n--- Link Prediction / Similarity ---")
        # 1. Salesperson: Node Similarity (Jaccard)
        # Since we projected WORKS_WITH, we can look for nodes with similar neighbors
        res = self.gds.run_cypher("""
            CALL gds.nodeSimilarity.stream('salesperson-graph')
            YIELD node1, node2, similarity
            RETURN gds.util.asNode(node1).name AS person1, 
                   gds.util.asNode(node2).name AS person2, 
                   similarity
            ORDER BY similarity DESC LIMIT 5
        """)
        print("Salesperson Similarity:")
        print(res)

        # 2. Product: Node Similarity
        res = self.gds.run_cypher("""
            CALL gds.nodeSimilarity.stream('product-graph')
            YIELD node1, node2, similarity
            RETURN gds.util.asNode(node1).name AS product1, 
                   gds.util.asNode(node2).name AS product2, 
                   similarity
            ORDER BY similarity DESC LIMIT 5
        """)
        print("Product Similarity:")
        print(res)

    def generate_report(self):
        # This would ideally capture outputs and write to MD
        # For now, I'll run it and then manually write the report based on logic
        pass

if __name__ == "__main__":
    analysis = GDSAnalysis(URI, USER, PASSWORD)
    try:
        analysis.setup_projections()
        analysis.run_path_finding()
        analysis.run_communities()
        analysis.run_centralities()
        analysis.run_link_prediction()
    finally:
        analysis.close()
