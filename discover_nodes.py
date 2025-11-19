import asyncio
from asyncua import Client

ENDPOINT = "opc.tcp://DESKTOP-DHM89GC:53530/OPCUA/SimulationServer/"

async def explore():
    async with Client(ENDPOINT) as client:
        print(f"Conectado a {ENDPOINT}\n")

        root = client.nodes.root
        objects = client.nodes.objects

        print("=== ROOT CHILDREN ===")
        for c in await root.get_children():
            print(" -", await c.read_display_name(), "| NodeId:", c.nodeid)

        print("\n=== OBJECTS CHILDREN ===")
        objects_children = await objects.get_children()
        for c in objects_children:
            name = (await c.read_display_name()).Text
            print(" -", name, "| NodeId:", c.nodeid)

        # Buscar carpeta Simulation
        sim_node = None
        for c in objects_children:
            name = (await c.read_display_name()).Text
            if "Simulation" in name:   # Prosys suele usar "Simulation"
                sim_node = c
                break

        if sim_node:
            print("\n=== SIMULATION CHILDREN ===")
            for c in await sim_node.get_children():
                name = (await c.read_display_name()).Text
                print(" -", name, "| NodeId:", c.nodeid)
        else:
            print("\nNo se encontró ninguna carpeta llamada Simulation.")

if __name__ == "__main__":
    asyncio.run(explore())
