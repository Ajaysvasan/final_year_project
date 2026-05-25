if __name__ == "__main__":
    print(
        "Initializing Hierarchical Project Memory Retrieval And Research Assistant System"
    )
    try:
        while True:
            query = input("Enter the query (Press ctrl + c to exit) : ")
            if query.lower() == "exit":
                print("Exiting the system. Goodbye!")
                break
            print(f"Processing query: {query}")
            # some stuff
    except KeyboardInterrupt:
        print("\nExiting the system. Goodbye!")
