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

def main():
    in = input("> ")
    with driver.session() as session:
        while(in != "exit" and in != "quit"):
            words = input.split().lower()
            if words[0] == "add":
                if words[1] == "person":
                    session.write_transaction(add_user, words[2])
                elif words[1] == "location" or words[1] == "place":
                    session.write_transaction(add_location, words[2])
                else:
                    print("input not recognized")
            elif words[0] == "get" or words[0] == "show":
                if words[2] == "risk":
                    if words[1] == "low"
                        session.write_transaction(get_low_risk)
                    elif words[1] == "medium":
                        session.write_transaction(get_medium_risk)
                    elif words[1] == "high"
                        session.write_transaction(get_high_risk)
                    else:
                        print("input not recognized")
                else:
                    print("input not recognized")
            elif words[1] == "contacted":
                #add relationships
                pass
            elif words[1] == "visited":
                #add relationships
                pass
            elif (words[1] == "tested" and words[2] == "positive") or (words[1] == "is" and words[2] == "infected"):
                #set to infected
                pass
            elif words[0] == "tick":
                pass
            else:
                print("input not recognized")
            in = input("> ")
    driver.close()


main()
