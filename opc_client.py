# opc_client.py
import time
import logging
from threading import Thread
from asyncua.sync import Client
from shared import SharedData

logger = logging.getLogger("opc_client")

class OPCClientThread(Thread):
    """
    OPC-UA client that reads Counter, Random and Sinusoid from Prosys Simulation Server.
    Now using DIRECT NodeIds to avoid BadNoMatch problems.
    """
    def __init__(self, endpoint: str, node_ids: dict, shared: SharedData, period_s: float = 0.1):
        super().__init__(daemon=True)
        self.endpoint = endpoint
        self.node_ids = node_ids   # dict: name → "ns=3;i=1002"
        self.shared = shared
        self.period_s = period_s

    def run(self):
        logger.info("OPC client thread starting, endpoint=%s", self.endpoint)

        while not self.shared.stop_event.is_set():
            try:
                with Client(self.endpoint) as client:
                    logger.info("Cliente OPC-UA conectado a %s", self.endpoint)

                    # Obtener nodos directamente por NodeId
                    nodes = {
                        "counter": client.get_node(self.node_ids["counter"]),
                        "random": client.get_node(self.node_ids["random"]),
                        "senoidal": client.get_node(self.node_ids["senoidal"]),
                    }

                    while not self.shared.stop_event.is_set():
                        start = time.time()

                        try:
                            val_counter = nodes["counter"].read_value()
                            val_random  = nodes["random"].read_value()
                            val_seno    = nodes["senoidal"].read_value()
                        except Exception as e:
                            logger.exception("Error leyendo nodos: %s", e)
                            break

                        # Guardar valores en SharedData
                        self.shared.sem_counter.acquire()
                        self.shared.counter = val_counter
                        self.shared.sem_counter.release()

                        self.shared.sem_random.acquire()
                        self.shared.random = val_random
                        self.shared.sem_random.release()

                        self.shared.sem_senoidal.acquire()
                        self.shared.senoidal = val_seno
                        self.shared.sem_senoidal.release()

                        elapsed = time.time() - start
                        time.sleep(max(0, self.period_s - elapsed))

            except Exception as e:
                logger.exception("Fallo en conexión OPC client, reintentando en 1s: %s", e)
                time.sleep(1)

        logger.info("OPC client thread detenido.")
