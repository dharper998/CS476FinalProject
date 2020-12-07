from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "asdf"), encrypted=False)

def set_infected(tx, name, days_since_test):
    tx.run("MATCH (p:Person {name: $name}) "
            "SET p.infected = 'Yes' "
            "SET p.daysSinceTest = $daysSince",
            name=name,
            daysSince=days_since_test)

def update_status(tx):
    tx.run("MATCH (p:Person) "
            "WHERE p.daysSinceTest >= 14 "
            "SET p.infected = 'No' "
            "SET p.daysSinceTest = -1")

def tick(tx):
    tx.run("MATCH (p:Person) "
            "WHERE NOT p.daysSinceTest = -1 "
            "SET p.daysSinceTest += 1")
    tx.run("MATCH (c:CONTACTED) "
            "SET c.daysSince += 1")
    tx.run("MATCH (v:VISITED) "
            "SET v.daysSince += 1")
    tx.run("MATCH (c:CONTACTED) "
            "WHERE c.daysSince >= 14 "
            "DETACH DELETE c")
    tx.run("MATCH (v:VISITED) "
            "WHERE v.daysSince >= 14 "
            "DETACH DELETE v")

def add_user(tx, name):
    tx.run("MERGE (p:Person {name: $name, infected: 'No', daysSinceTest: -1})",
            name=name)

def add_location(tx, name):
    tx.run("MERGE (l:Location {name: $name})",
            name=name)

def add_contact(tx, name1, name2, days_since):
    tx.run("MATCH (a:Person {name: $name1}) "
            "MATCH (b:Person {name: $name2}) "
            "CREATE (a)-[:CONTACTED{daysSince: $daysSince}]->(b)",
            name1=name1,
            name2=name2,
            daysSince=days_since)

def add_visited(tx, name, location, days_since):
    tx.run("MATCH (a:Person {name: $name}) "
            "MATCH (b:Location {name: $location}) "
            "CREATE (a)-[:VISITED{daysSince: $daysSince}]->(b)",
            name=name,
            location=location,
            daysSince=days_since)

def get_high_risk(tx):
    high = tx.run("MATCH (p:Person {infected:'Yes'})-[*1]-(high) "
            "RETURN DISTINCT high")
    for item in high.data():
        print(item['high']['name'])

def get_medium_risk(tx):
    medium = tx.run("MATCH (p:Person {infected:'Yes'})-[*2]-(medium) "
            "RETURN DISTINCT medium")
    for item in medium.data():
        print(item['medium']['name'])

def get_low_risk(tx):
    low = tx.run("MATCH (p:Person {infected:'Yes'})-[*3]-(low) "
            "RETURN DISTINCT low")
    for item in low.data():
        print(item['low']['name'])

def main():
    inp = input("> ")
    with driver.session() as session:
        while(inp != "exit" and inp != "quit"):
            words = inp.lower().split()
            if words[0] == "add":
                if words[1] == "person":
                    session.write_transaction(add_user, words[2])
                elif words[1] == "location" or words[1] == "place":
                    session.write_transaction(add_location, " ".join(words[2:]))
                else:
                    print("input not recognized")
            elif words[0] == "get" or words[0] == "show":
                if words[2] == "risk":
                    if words[1] == "low":
                        session.read_transaction(get_low_risk)
                    elif words[1] == "medium":
                        session.read_transaction(get_medium_risk)
                    elif words[1] == "high":
                        session.read_transaction(get_high_risk)
                    else:
                        print("input not recognized")
                else:
                    print("input not recognized")
            elif words[1] == "contacted":
                session.write_transaction(add_contact, words[0], words[2], int(words[3]))
            elif words[1] == "visited":
                session.write_transaction(add_visited, words[0], " ".join(words[2:-1]), int(words[-1]))
            elif (words[1] == "tested" and words[2] == "positive") or (words[1] == "is" and words[2] == "infected"):
                session.write_transaction(set_infected, words[0], int(words[3]))
            elif words[0] == "tick":
                session.write_transaction(tick)
            else:
                print("input not recognized")
            inp = input("> ")
    driver.close()


main()
