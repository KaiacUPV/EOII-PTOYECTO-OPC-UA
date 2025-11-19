# udp_bridge.py
import time
import json
import socket
import logging
from threading import Thread
from shared import SharedData

logger = logging.getLogger("udp_bridge")

class UDPBridgeThread(Thread):
    """
    Envía por UDP (JSON) los valores 'counter' y 'random' periódicamente.
    """
    def __init__(self, target_host: str, target_port: int, shared: SharedData, period_s: float = 0.1):
        super().__init__(daemon=True)
        self.host = target_host
        self.port = target_port
        self.shared = shared
        self.period_s = period_s
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        logger.info("UDP bridge iniciando: %s:%d", self.host, self.port)
        while not self.shared.stop_event.is_set():
            # leer counter y random con semáforos
            self.shared.sem_counter.acquire()
            try:
                counter_val = self.shared.counter
            finally:
                self.shared.sem_counter.release()

            self.shared.sem_random.acquire()
            try:
                random_val = self.shared.random
            finally:
                self.shared.sem_random.release()

            if counter_val is not None or random_val is not None:
                payload = {
                    "counter": counter_val,
                    "random": random_val,
                    "ts": time.time()
                }
                try:
                    data = json.dumps(payload).encode('utf-8')
                    self.sock.sendto(data, (self.host, self.port))
                except Exception as e:
                    logger.exception("Error enviando datagrama UDP: %s", e)
            time.sleep(self.period_s)
        logger.info("UDP bridge detenido.")
