from asyncua.sync import Client

endpoint = "opc.tcp://RedMi_LZH:53530/OPCUA/SimulationServer"

# NodeIds reales del Prosys Simulation Server
NODE_COUNTER = "ns=3;i=1001"
NODE_RANDOM = "ns=3;i=1002"
NODE_SINUS = "ns=3;i=1004"

with Client(endpoint) as client:
    print("Conectado correctamente.\n")

    n_counter = client.get_node(NODE_COUNTER)
    n_random = client.get_node(NODE_RANDOM)
    n_sinus = client.get_node(NODE_SINUS)

    print("Leyendo nodos...\n")

    print("Counter :", n_counter.read_value())
    print("Random  :", n_random.read_value())
    print("Sinusoid:", n_sinus.read_value())
