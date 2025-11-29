# main.py
import logging
import signal
import sys

from shared import SharedData
from opc_client import OPCClientThread
from opc_server import OPCServerThread
from udp_bridge import UDPBridgeThread



logging.getLogger("asyncua").setLevel(logging.ERROR)
logging.getLogger("asyncua.client").setLevel(logging.ERROR)
logging.getLogger("asyncua.server").setLevel(logging.ERROR)
logging.getLogger("asyncua.common").setLevel(logging.ERROR)
logging.getLogger("asyncua.ua").setLevel(logging.ERROR)

# Endpoints
OPC_SOURCE_ENDPOINT = "opc.tcp://RedMi_LZH:53530/OPCUA/SimulationServer"
OPC_SERVER_ENDPOINT = "opc.tcp://localhost:4841/freeopcua/python_bridge/"
OPC_SERVER_NAMESPACE = "http://localhost/pythonbridge"

UDP_TARGET_HOST = "127.0.0.1"
UDP_TARGET_PORT = 9000

# NodeIds directos del Prosys Simulation Server Mirar la configuración del servidor
NODE_IDS = {
    "counter": "ns=3;i=1001",
    "random": "ns=3;i=1002",
    "senoidal": "ns=3;i=1004"
}

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def main():
    setup_logging()
    logger = logging.getLogger("main")
    shared = SharedData()

    client_thread = OPCClientThread(OPC_SOURCE_ENDPOINT, NODE_IDS, shared, period_s=0.1)
    server_thread = OPCServerThread(OPC_SERVER_ENDPOINT, OPC_SERVER_NAMESPACE, shared,
                                    var_name="Sinusoid", update_period_s=0.1)
    udp_thread = UDPBridgeThread(UDP_TARGET_HOST, UDP_TARGET_PORT, shared, period_s=0.1)

    def sigint_handler(signum, frame):
        logger.info("Signal received, stopping...")
        shared.stop_event.set()

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    logger.info("Iniciando threads...")
    server_thread.start()
    client_thread.start()
    udp_thread.start()

    try:
        while not shared.stop_event.is_set():
            shared.stop_event.wait(1.0)
    finally:
        logger.info("Esperando finalización...")
        server_thread.join(timeout=2.0)
        client_thread.join(timeout=2.0)
        udp_thread.join(timeout=2.0)
        logger.info("Aplicación finalizada.")

if __name__ == "__main__":
    main()
