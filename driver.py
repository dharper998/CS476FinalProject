from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "asdf"), encrypted=False)

def set_infected(tx, name):
    tx.run("MATCH (p:Person {name: $name}) "
            "SET p.infected = 'Yes'",
            name=name)

def add_user(tx, name, infected, days_since_test):
    tx.run("MERGE (p:Person {name: $name, infected: $infected, daysSinceTest: $daysSinceTest})",
            name=name,
            infected=infected,
            daysSinceTest=days_since_test)

def add_location(tx, name):
    tx.run("MERGE (l:Location {name: $name})",
            name=name)

def add_contact(tx, name1, name2, days_since):
    tx.run("MATCH (a:Person {name: $name1}) "
            "MATCH (b:Person {name: $name2})"
            "CREATE (a)-[:CONTACTED{daysSince: $daysSince}]->(b)",
            name1=name1,
            name2=name2,
            daysSince=days_since)

def get_high_risk(tx):
    high = tx.run("MATCH (p:Person {infected:'Yes'})-[*1]-(high) "
            "RETURN DISTINCT high")
    return high

def get_medium_risk(tx):
    medium = tx.run("MATCH (p:Person {infected:'Yes'})-[*2]-(medium) "
            "RETURN DISTINCT medium")
    return medium

def get_low_risk(tx):
    low = tx.run("MATCH (p:Person {infected:'Yes'})-[*3]-(low) "
            "RETURN DISTINCT low")
    return low

with driver.session() as session:
    session.write_transaction(add_user, "George", "No", 12)
    session.write_transaction(add_location, "Costco")
    session.write_transaction(add_contact, "Drew", "George", 8)
    session.write_transaction(set_infected, "George")
    session.read_transaction(get_high_risk)

driver.close()
