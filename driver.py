from neo4j import GraphDatabase

driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "asdf"))

def set_infected(tx, name):
    tx.run("MATCH (p:Person {name: $name}) "
            "SET p.infected = 'Yes' "
            "RETURN p",
            name=name)

def print_friends(tx, name):
    for record in tx.run("MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
                         "RETURN friend.name ORDER BY friend.name", name=name):
        print(record["friend.name"])

with driver.session() as session:
    session.write_transaction(add_friend, "Arthur", "Guinevere")
    session.write_transaction(add_friend, "Arthur", "Lancelot")
    session.write_transaction(add_friend, "Arthur", "Merlin")
    session.read_transaction(print_friends, "Arthur")

driver.close()

def main():
    in = input("> ")
    while(in != "exit" and in != "quit"):
        words = input.split().lower()
        if words[0] == "add":
            #add users/locations
            pass
        elif words[0] == "delete" or words[0] == "remove":
            pass
        elif words[0] == "get" or words[0] == "show":
            #find a person's risk level
            #get each risk level
            pass
        elif words[1] == "contacted":
            #add relationships
            pass
        elif words[1] == "went" and words[2] == "to":
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


main()
