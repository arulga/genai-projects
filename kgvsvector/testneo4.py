from neo4j import GraphDatabase

# Use your Aura credentials
URI = "neo4j+s:"
USER = "neo4j"
PASSWORD = "H4"

# Initialize driver
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# Test query
with driver.session() as session:
    result = session.run("RETURN 'Connection successful' AS message")
    print(result.single()["message"])

# Close driver
driver.close()
