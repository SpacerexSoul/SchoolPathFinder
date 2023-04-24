import heapq
import tkinter as tk
import sqlite3
from tkinter import ttk

class Node:
    def __init__(self, name):
        self.name = name
        self.neighbors = []

    def add_neighbor(self, neighbor, weight):
        self.neighbors.append((neighbor, weight))

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        self.nodes[node.name] = node

    def dijkstra(self, start, end):
        dist = {node: float('inf') for node in self.nodes}
        dist[start] = 0
        unvisited = list(self.nodes.keys())
        path = {}

        while unvisited:
            # Find the node with the smallest distance in the unvisited nodes
            current_node = min(unvisited, key=lambda node: dist[node])

            # If we've reached the end node, break
            if current_node == end:
                break

            # Remove the current node from the unvisited nodes
            unvisited.remove(current_node)

            for neighbor, weight in self.nodes[current_node].neighbors:
                new_distance = dist[current_node] + weight

                if new_distance < dist[neighbor]:
                    dist[neighbor] = new_distance
                    path[neighbor] = current_node

        if dist[end] == float('inf'):  # No path exists
            return float('inf'), []

        # Reconstruct the path
        current = end
        result_path = [current]
        while current != start:
            current = path[current]
            result_path.append(current)
        result_path.reverse()

        return dist[end], result_path



# Ok so this is all the uh nodes this method creates a graph and what not
def create_graph():
    g = Graph()

    # Connect to the SQLite database
    conn = sqlite3.connect("ESCNav.db")
    cursor = conn.cursor()

    # Query the nodes and neighbors from the database
    cursor.execute("SELECT name, neighbors FROM nodes")
    rows = cursor.fetchall()

    # Create the nodes and add the neighbors
    for row in rows:
        node_name = row[0]
        neighbors = [tuple(neighbor.split(':')) for neighbor in row[1].split(',')]
        neighbors = [(neighbor_name, int(weight)) for neighbor_name, weight in neighbors]

        node = Node(node_name)
        for neighbor, weight in neighbors:
            node.add_neighbor(neighbor, weight)

        g.add_node(node)

    # Add reverse neighbors
    for node_name, node in g.nodes.items():
        for neighbor, weight in node.neighbors:
            g.nodes[neighbor].add_neighbor(node_name, weight)

    # Close the database connection
    conn.close()

    return g


def login(username, password):
    # Implement your login logic here ritvarz
    return True

class EastburyPathfinderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Eastbury Pathfinder")
        self.geometry("400x200")

        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10)

        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=10)

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=10)

        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.grid(row=2, column=1, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        testing = 1

        if testing == 1:
            self.destroy()
            pathfinder = PathfinderWindow()
            pathfinder.mainloop()
        else:
            messagebox.showerror("Error", "Incorrect username or password. Please try again.")

class PathfinderWindow(tk.Tk): # This is just the GUI edit this if you have time and make it look good, so far i have just centered things and what not
    def __init__(self):
        super().__init__()

        self.title("Pathfinder")
        self.geometry("600x400")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.graph = create_graph()

        self.start_label = ttk.Label(self.main_frame, text="Starting position:")
        self.start_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.start_combobox = ttk.Combobox(self.main_frame, values=list(self.graph.nodes.keys()), width=30)
        self.start_combobox.grid(row=0, column=1, padx=10, sticky="w")

        self.destination_label = ttk.Label(self.main_frame, text="Destination:")
        self.destination_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.destination_combobox = ttk.Combobox(self.main_frame, values=list(self.graph.nodes.keys()), width=30)
        self.destination_combobox.grid(row=1, column=1, padx=10, sticky="w")

        self.find_path_button = ttk.Button(self.main_frame, text="Find Path", command=self.find_path)
        self.find_path_button.grid(row=2, column=1, pady=10, sticky="w")

        self.result_label = ttk.Label(self.main_frame, text="Path:")
        self.result_label.grid(row=3, column=0, padx=10, pady=10, sticky="ne")

        self.result_text = tk.Text(self.main_frame, wrap=tk.WORD, width=40, height=4)
        self.result_text.grid(row=3, column=1, padx=10, pady=10, sticky="nw")
        self.result_text.config(state=tk.DISABLED)


    def find_path(self): # This is all the outputs the user is able to get
        start = self.start_combobox.get()
        destination = self.destination_combobox.get()

        if start not in self.graph.nodes:
            messagebox.showerror("Error", "Invalid starting position. Please select a valid position from the dropdown.")
            return

        if destination not in self.graph.nodes or destination == start:
            messagebox.showerror("Error", "Invalid destination. Please select a valid position from the dropdown that is not the starting position.")
            return

        cost, path = self.new_method2(start, destination)
        if cost == float('inf'):
            result_text = f"No path exists between {start} and {destination}."
        else:
            result_text = f"The quickest path from {start} to {destination} is: {' -> '.join(path)} and it will take {cost} minutes."

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text)
        self.result_text.config(state=tk.DISABLED)


    def new_method2(self, start, destination): # Will carry out dijkstra
        cost, path = self.graph.dijkstra(start, destination)
        return cost,path

if __name__ == "__main__": # program / app loop
    app = EastburyPathfinderApp()
    app.mainloop()
