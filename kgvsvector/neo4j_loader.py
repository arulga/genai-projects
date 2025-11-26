# neo4j_loader.py
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

class Neo4jHelper:
    def __init__(self, uri=None, user=None, password=None):
        # Use default values if not passed
        self.uri = URI
        self.user = USER
        self.password = PASSWORD

        # Ensure uri is a string, not bytes
        if isinstance(self.uri, bytes):
            self.uri = self.uri.decode("utf-8")

        # Check if uri is empty
        if not self.uri:
            raise ValueError("Neo4j URI is empty!")

        # Initialize driver
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def create_document_page(self, doc_id, doc_name, page_no, text):
        cypher = """
        MERGE (d:Document {doc_id: $doc_id})
        SET d.name = $doc_name
        MERGE (p:Page {doc_id: $doc_id, page: $page_no})
        SET p.text = $text
        MERGE (d)-[:HAS_PAGE]->(p)
        RETURN d, p
        """
        with self.driver.session() as s:
            s.run(cypher, doc_id=str(doc_id), doc_name=doc_name, page_no=int(page_no), text=text)

    def create_entity_and_rel(self, doc_id, page_no, entity_text, label):
        # create entity node and link to page
        cypher = """
        MERGE (e:Entity {name: $entity})
        SET e.label = $label
        MERGE (p:Page {doc_id: $doc_id, page: $page_no})
        MERGE (p)-[:MENTIONS]->(e)
        RETURN e
        """
        with self.driver.session() as s:
            s.run(cypher, entity=entity_text, label=label, doc_id=str(doc_id), page_no=int(page_no))

    def get_entity_neighbors(self, entity, depth=1, limit=20):
        cypher = f"""
        MATCH (e:Entity {{name: $entity}})-[r*1..{depth}]-(n)
        RETURN e, r, n LIMIT $limit
        """
        with self.driver.session() as s:
            result = s.run(cypher, entity=entity, limit=limit)
            return [rec.data() for rec in result]

    def find_pages_with_entity(self, entity_name, limit=10):
        cypher = """
        MATCH (e:Entity {name: $entity})<-[:MENTIONS]-(p:Page)
        RETURN p.doc_id AS doc_id, p.page AS page, p.text AS text
        LIMIT $limit
        """
        with self.driver.session() as s:
            result = s.run(cypher, entity=entity_name, limit=limit)
            return [r.data() for r in result]

if __name__ == "__main__":
    helper = Neo4jHelper()
    with helper.driver.session() as session:
        result = session.run("RETURN 'Neo4j connection OK' AS message")
        print(result.single()["message"])