from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "asdf"), encrypted=False)

#Working
def set_infected(tx, name, status, days_since_test):
    tx.run("MATCH (p:Person {name: $name}) "
            "SET p.infected = $status "
            "SET p.daysSinceTest = $daysSince",
            name=name,
            status=status,
            daysSince=days_since_test)

#Working
def tick(tx):
    tx.run("MATCH (p:Person) "
            "WHERE NOT p.daysSinceTest = -1 "
            "SET p.daysSinceTest = p.daysSinceTest + 1")
    tx.run("MATCH (p:Person) "
            "WHERE p.daysSinceTest >= 14 "
            "SET p.infected = 'No' "
            "SET p.daysSinceTest = -1")
    tx.run("MATCH ()-[c:CONTACTED]->() "
            "SET c.daysSince = c.daysSince + 1")
    tx.run("MATCH ()-[v:VISITED]->() "
            "SET v.daysSince = v.daysSince + 1")
    tx.run("MATCH ()-[c:CONTACTED]->() "
            "WHERE c.daysSince >= 14 "
            "DETACH DELETE c")
    tx.run("MATCH ()-[v:VISITED]->() "
            "WHERE v.daysSince >= 14 "
            "DETACH DELETE v")

#Working
def add_user(tx, name):
    tx.run("MERGE (p:Person {name: $name, infected: 'No', daysSinceTest: -1})",
            name=name)

#Working
def add_location(tx, name):
    tx.run("MERGE (l:Location {name: $name})",
            name=name)

#Working
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
        if('infected' in item['high'].keys()):
            print("Person: ", item['high']['name'])
        else:
            print("Location: ", item['high']['name'])

def get_medium_risk(tx):
    medium = tx.run("MATCH (p:Person {infected:'Yes'})-[c]-(high)-[d]-(medium) "
                    "WHERE d.daysSince <= c.daysSince "
                    "RETURN DISTINCT medium")
    for item in medium.data():
        if('infected' in item['medium'].keys()):
            print("Person: ", item['medium']['name'])
        else:
            print("Location: ", item['medium']['name'])

def get_low_risk(tx):
    low = tx.run("MATCH (p:Person {infected:'Yes'})-[c]-(high)-[d]-(medium)-[e]-(low) "
                    "WHERE e.daysSince <= d.daysSince <= c.daysSince "
                    "RETURN DISTINCT low")
    for item in low.data():
        if('infected' in item['low'].keys()):
            print("Person: ", item['low']['name'])
        else:
            print("Location: ", item['low']['name'])

def get_individual_risk(tx, name):
    status = tx.run("MATCH (p {name: $name}) "
                    "RETURN p",
                    name=name)
    data = status.data()
    if('infected' in data[0]['p'].keys()):
        if(data[0]['p']['infected'] == 'Yes'):
            print("Infected")
            return
    high = tx.run("MATCH (p:Person {infected:'Yes'})-[*1]-(high) "
            "RETURN DISTINCT high")
    medium = tx.run("MATCH (p:Person {infected:'Yes'})-[c]-(high)-[d]-(medium) "
                    "WHERE d.daysSince <= c.daysSince "
                    "RETURN DISTINCT medium")
    low = tx.run("MATCH (p:Person {infected:'Yes'})-[c]-(high)-[d]-(medium)-[e]-(low) "
                    "WHERE e.daysSince <= d.daysSince <= c.daysSince "
                    "RETURN DISTINCT low")
    for item in high.data():
        if(item['high']['name'] == name):
            print("High")
            return
    for item in medium.data():
        if(item['medium']['name'] == name):
            print("Medium")
            return
    for item in low.data():
        if(item['low']['name'] == name):
            print("Low")
            return
    print("Not at risk")

def main():
    inp = input("> ")
    with driver.session() as session:
        while(inp != "exit" and inp != "quit"):
            words = inp.split()
            if words[0] == "tick":
                session.write_transaction(tick)
            elif words[0] == "add":
                if words[1] == "person":
                    session.write_transaction(add_user, words[2])
                elif words[1] == "location":
                    session.write_transaction(add_location, " ".join(words[2:]))
                else:
                    print("input not recognized")
            elif words[0] == "get":
                if words[1] == "risk":
                    if words[2] == "low":
                        session.read_transaction(get_low_risk)
                    elif words[2] == "medium":
                        session.read_transaction(get_medium_risk)
                    elif words[2] == "high":
                        session.read_transaction(get_high_risk)
                    else:
                        session.read_transaction(get_individual_risk, " ".join(words[2:]))
                else:
                    print("input not recognized")
            elif words[1] == "contacted":
                session.write_transaction(add_contact, words[0], words[2], int(words[3]))
            elif words[1] == "visited":
                session.write_transaction(add_visited, words[0], " ".join(words[2:-1]), int(words[-1]))
            elif (words[1] == "tested" and words[2] == "positive") or (words[1] == "is" and words[2] == "infected"):
                session.write_transaction(set_infected, words[0], "Yes", int(words[3]))
            elif (words[1] == "tested" and words[2] == "negative"):
                session.write_transaction(set_infected, words[0], "No", -1)
            else:
                print("input not recognized")
            inp = input("> ")
    driver.close()


main()
