import pandas as pd
from neo4j import GraphDatabase
import os

class Neo4jImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def import_salespersons(self, csv_path):
        print(f"Reading {csv_path}")
        df = pd.read_csv(csv_path, sep="\t")
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (s:Salesperson {employeeKey: $key})
                    SET s.employeeId = $id,
                        s.name = $name,
                        s.title = $title
                """, key=int(row['EmployeeKey']), id=int(row['EmployeeID']), 
                    name=row['Salesperson'], title=row['Title'])

    def import_regions(self, csv_path):
        print(f"Reading {csv_path}")
        df = pd.read_csv(csv_path, sep="\t")
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (r:Region {salesTerritoryKey: $key})
                    SET r.name = $name,
                        r.country = $country,
                        r.group = $group
                """, key=int(row['SalesTerritoryKey']), name=row['Region'], 
                    country=row['Country'], group=row['Group'])

    def import_salesperson_regions(self, csv_path):
        print(f"Reading {csv_path}")
        df = pd.read_csv(csv_path, sep="\t")
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MATCH (s:Salesperson {employeeKey: $eKey})
                    MATCH (r:Region {salesTerritoryKey: $rKey})
                    MERGE (s)-[:ASSIGNED_TO]->(r)
                """, eKey=int(row['EmployeeKey']), rKey=int(row['SalesTerritoryKey']))

    def import_products(self, csv_path):
        print(f"Reading {csv_path}")
        df = pd.read_csv(csv_path, sep="\t")
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (p:Product {productKey: $key})
                    SET p.name = $name,
                        p.standardCost = $cost,
                        p.color = $color,
                        p.subcategory = $subcat,
                        p.category = $cat
                """, key=int(row['ProductKey']), name=row['Product'], 
                    cost=row['Standard Cost'], color=row['Color'], 
                    subcat=row['Subcategory'], cat=row['Category'])

    def import_resellers(self, csv_path):
        print(f"Reading {csv_path}")
        df = pd.read_csv(csv_path, sep="\t")
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (res:Reseller {resellerKey: $key})
                    SET res.name = $name,
                        res.businessType = $type,
                        res.city = $city,
                        res.state = $state,
                        res.country = $country
                """, key=int(row['ResellerKey']), name=row['Reseller'], 
                    type=row['Business Type'], city=row['City'], 
                    state=row['State-Province'], country=row['Country-Region'])

    def import_sales_relationships(self, csv_path):
        print(f"Reading {csv_path}")
        df = pd.read_csv(csv_path, sep="\t")
        with self.driver.session() as session:
            session.execute_write(self._create_reseller_product_batch, df)
            
    @staticmethod
    def _create_reseller_product_batch(tx, df):
        batch = df[['ResellerKey', 'ProductKey']].drop_duplicates()
        for _, row in batch.iterrows():
            tx.run("""
                MATCH (res:Reseller {resellerKey: $resKey})
                MATCH (p:Product {productKey: $pKey})
                MERGE (res)-[:SOLD_PRODUCT]->(p)
            """, resKey=int(row['ResellerKey']), pKey=int(row['ProductKey']))

    def create_monopartite_graph(self):
        # Salespersons working in the same region
        with self.driver.session() as session:
            session.run("""
                MATCH (s1:Salesperson)-[:ASSIGNED_TO]->(r:Region)<-[:ASSIGNED_TO]-(s2:Salesperson)
                WHERE id(s1) < id(s2)
                MERGE (s1)-[:WORKS_WITH]->(s2)
            """)

    def create_product_monopartite(self):
        # Products commonly sold by the same reseller
        with self.driver.session() as session:
            session.run("""
                MATCH (p1:Product)<-[:SOLD_PRODUCT]-(res:Reseller)-[:SOLD_PRODUCT]->(p2:Product)
                WHERE id(p1) < id(p2)
                MERGE (p1)-[:COMMONLY_SOLD_BY_SAME_RESELLER]->(p2)
            """)

if __name__ == "__main__":
    # Configuration
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = "password"
    
    # Files are now in 'data/' directory at the project root
    # Corrected path logic
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    
    importer = Neo4jImporter(URI, USER, PASSWORD)
    
    try:
        print("Clearing database...")
        importer.clear_database()
        
        print("Importing Salespersons...")
        importer.import_salespersons(os.path.join(DATA_DIR, "Salesperson.csv"))
        
        print("Importing Regions...")
        importer.import_regions(os.path.join(DATA_DIR, "Region.csv"))
        
        print("Creating Bipartite Relationships (Salesperson-Region)...")
        importer.import_salesperson_regions(os.path.join(DATA_DIR, "SalespersonRegion.csv"))
        
        print("Importing Products...")
        importer.import_products(os.path.join(DATA_DIR, "Product.csv"))
        
        print("Importing Resellers...")
        importer.import_resellers(os.path.join(DATA_DIR, "Reseller.csv"))
        
        print("Importing Sales relationships (Reseller-Product Bipartite)...")
        importer.import_sales_relationships(os.path.join(DATA_DIR, "Sales.csv"))
        
        print("Creating Monopartite Graph (Salesperson-Salesperson projection)...")
        importer.create_monopartite_graph()
        
        print("Creating Monopartite Graph (Product-Product projection)...")
        importer.create_product_monopartite()
        
        print("Import successful!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        importer.close()
