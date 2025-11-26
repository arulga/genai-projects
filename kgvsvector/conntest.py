from neo4j import GraphDatabase

# Replace with your actual Aura credentials
NEO4J_URI = "neo4j+s:"  # Neo4j Aura URI
NEO4J_USER = "neo4j"                                 # default username for Aura
NEO4J_PASSWORD = "H4"               # your Aura password

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Test connection
with driver.session() as session:
    result = session.run("RETURN 'Connection Successful' AS message")
    print(result.single()["message"])