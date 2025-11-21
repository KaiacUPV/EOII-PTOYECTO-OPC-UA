from asyncua.sync import Client

endpoint = "opc.tcp://DESKTOP-DHM89GC:53530/OPCUA/SimulationServer"

print("Intentando conectar a:", endpoint)

try:
    with Client(endpoint) as client:
        print("¡¡CONECTADO!!")
except Exception as e:
    print("ERROR:", e)
