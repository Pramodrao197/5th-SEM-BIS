
import random
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# STEP 1: INITIALIZE NETWORK
# ==========================================

total_devices = 50
total_cells = 5
total_packets = 5

random.seed(10)

# 1 = Active, 0 = Inactive
network = [random.randint(0, 1) for _ in range(total_devices)]

# Divide 50 devices into 5 cells
cells = [
    network[i * 10:(i + 1) * 10]
    for i in range(total_cells)
]

print("===== PARALLEL CELLULAR NETWORK SIMULATION =====\n")


# ==========================================
# STEP 2: PARALLEL CELL PROCESSING
# ==========================================

def process_cell(cell):
    return len(cell), sum(cell)

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(process_cell, cells))

for i, result in enumerate(results):
    print(f"Cell {i+1}: Total Devices = {result[0]}, Active = {result[1]}")


# ==========================================
# STEP 3: CREATE NETWORK TOPOLOGY
# ==========================================

graph = nx.Graph()
graph.add_nodes_from(range(1, total_devices + 1))

# Random connections
for i in range(1, total_devices + 1):
    for j in range(i + 1, total_devices + 1):
        if random.random() < 0.12:
            graph.add_edge(i, j)

# Connect consecutive active devices to ensure
# an available route between active devices
active_devices = [
    i for i in range(1, total_devices + 1)
    if network[i - 1] == 1
]

for i in range(len(active_devices) - 1):
    graph.add_edge(active_devices[i], active_devices[i + 1])


# ==========================================
# STEP 4: PARALLEL BFS ROUTING
# ==========================================

def find_path(source, destination):

    if source == destination:
        return [source]

    queue = deque([source])
    visited = {source}
    parent = {}

    with ThreadPoolExecutor(max_workers=5) as executor:

        while queue:

            # Process all nodes at the current BFS level
            current_level = list(queue)
            queue.clear()

            # Each worker explores neighbours of one node
            def explore(node):
                return node, sorted(graph[node])

            results = list(executor.map(explore, current_level))

            next_level = []

            # Collect results and update visited nodes safely
            for current, neighbours in results:

                for neighbour in neighbours:

                    if (neighbour not in visited
                        and network[neighbour - 1] == 1):

                        visited.add(neighbour)
                        parent[neighbour] = current

                        if neighbour == destination:
                            path = [destination]

                            while path[-1] != source:
                                path.append(parent[path[-1]])

                            return path[::-1]

                        next_level.append(neighbour)

            queue.extend(next_level)

    return None


# ==========================================
# STEP 5: DEVICE SELECTION
# ==========================================

print("\n===== DEVICE SELECTION =====")

n1 = int(input("Enter Source Device N1 (1-50): "))
n2 = int(input("Enter Destination Device N2 (1-50): "))

path = None

if not (1 <= n1 <= 50 and 1 <= n2 <= 50):
    print("Invalid device number!")

elif network[n1 - 1] == 0:
    print("Source device is INACTIVE.")

elif network[n2 - 1] == 0:
    print("Destination device is INACTIVE.")

else:
    path = find_path(n1, n2)

    if path is None:
        print("\nConnection FAILED!")

    else:
        print("\nCONNECTION ESTABLISHED!")
        print("Source:", n1)
        print("Destination:", n2)
        print("Routing Path:", " -> ".join(map(str, path)))


# ==========================================
# STEP 6: NETWORK VISUALIZATION
# ==========================================

# Arrange devices into 5 cell regions
positions = {}

for device in range(1, total_devices + 1):

    cell = (device - 1) // 10
    local = (device - 1) % 10

    x = cell * 6 + (local % 5)
    y = 1 - (local // 5)

    positions[device] = (x, y)

plt.figure(figsize=(18, 8))

# Draw five cell regions
colors = ['#DCEBFA', '#DDF3E4', '#FFF0D5',
          '#EDE0FA', '#FADFE5']

for i in range(total_cells):
    plt.axvspan(
        i * 6 - 0.5,
        i * 6 + 4.5,
        color=colors[i],
        alpha=0.7
    )

# Draw network connections
nx.draw_networkx_edges(
    graph,
    positions,
    edge_color="gray",
    alpha=0.35,
    width=0.8
)

# Separate active and inactive devices
active = [i for i in graph.nodes if network[i-1] == 1]
inactive = [i for i in graph.nodes if network[i-1] == 0]

nx.draw_networkx_nodes(
    graph, positions,
    nodelist=active,
    node_color="skyblue",
    node_size=350
)

nx.draw_networkx_nodes(
    graph, positions,
    nodelist=inactive,
    node_color="lightgray",
    node_size=350
)

# Highlight BFS path
if path:

    path_edges = list(zip(path[:-1], path[1:]))

    nx.draw_networkx_edges(
        graph,
        positions,
        edgelist=path_edges,
        edge_color="orange",
        width=3
    )

    if len(path) > 2:
        nx.draw_networkx_nodes(
            graph, positions,
            nodelist=path[1:-1],
            node_color="orange",
            node_size=450
        )

    nx.draw_networkx_nodes(
        graph, positions,
        nodelist=[n1],
        node_color="green",
        node_size=550
    )

    nx.draw_networkx_nodes(
        graph, positions,
        nodelist=[n2],
        node_color="red",
        node_size=550
    )

# Display device numbers
nx.draw_networkx_labels(
    graph,
    positions,
    font_size=8
)

# Cell names
for i in range(total_cells):
    plt.text(
        i * 6 + 2,
        2,
        f"CELL {i+1}",
        fontsize=12,
        fontweight="bold",
        ha="center"
    )

# Legend
plt.scatter([], [], color="skyblue", label="Active Device")
plt.scatter([], [], color="lightgray", label="Inactive Device")
plt.scatter([], [], color="green", label="Source")
plt.scatter([], [], color="red", label="Destination")
plt.scatter([], [], color="orange", label="Intermediate / Path")

plt.title(
    "PARALLEL CELLULAR NETWORK - 50 DEVICES",
    fontsize=16,
    fontweight="bold"
)

plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=5)
plt.axis("off")
plt.tight_layout()
plt.show()


# ==========================================
# STEP 7: PACKET TRANSMISSION
# ==========================================

if path:

    print("\n===== PACKET TRANSMISSION =====")

    delivered = 0
    lost = 0
    total_delay = 0

    for packet in range(1, total_packets + 1):

        packet_delay = 0
        success = True

        print(f"\nPacket {packet}:")

        for i in range(len(path) - 1):

            current = path[i]
            next_device = path[i + 1]

            delay = random.uniform(1, 5)
            packet_delay += delay

            if random.random() < 0.2:
                print(f"Packet dropped at Device N{current}")
                success = False
                break

            print(f"N{current} -> N{next_device} : Delivered")

        if success:
            delivered += 1
            total_delay += packet_delay

            print("Packet successfully received!")
            print(f"Packet Delay: {packet_delay:.2f} ms")

        else:
            lost += 1
            print("Packet transmission FAILED!")


    # ==========================================
    # STEP 8: NETWORK PERFORMANCE
    # ==========================================

    print("\n===== NETWORK PERFORMANCE =====")

    print("Total Packets:", total_packets)
    print("Packets Delivered:", delivered)
    print("Packets Lost:", lost)

    pdr = (delivered / total_packets) * 100

    print(f"Packet Delivery Ratio: {pdr:.2f}%")

    if delivered > 0:
        avg_delay = total_delay / delivered
        print(f"Average Delay: {avg_delay:.2f} ms")
    else:
        print("Average Delay: Not available")

print("\nNetwork Simulation Completed!")
