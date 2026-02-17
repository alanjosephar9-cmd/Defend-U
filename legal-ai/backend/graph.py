import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

try:
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))
    )
except Exception as e:
    print(f"Warning: Could not connect to Neo4j: {e}")
    driver = None

def store(query, concepts):
    if driver is None:
        return
        
    try:
        with driver.session() as session:
            session.run("MERGE (q:Query {text:$query})", parameters={"query": query})

            for c, terms in concepts.items():
                session.run("MERGE (c:Concept {name:$c})", parameters={"c": str(c)})

                for t in terms:
                    session.run("""
                        MERGE (t:Term {name:$t})
                        MERGE (q:Query {text:$query})
                        MERGE (c:Concept {name:$c})
                        MERGE (q)-[:HAS_CONCEPT]->(c)
                        MERGE (c)-[:HAS_TERM]->(t)
                    """, parameters={"t": t, "query": query, "c": str(c)})
    except Exception as e:
        print(f"Error storing in Neo4j: {e}")
