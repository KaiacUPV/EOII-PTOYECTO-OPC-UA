from asyncua.sync import Client

endpoint = "opc.tcp://DESKTOP-DHM89GC:53530/OPCUA/SimulationServer"

print(f"Conectando a {endpoint}...")

with Client(endpoint) as client:
    print("✔ Conexión OK")
    root = client.nodes.root
    print("Root:", root)
