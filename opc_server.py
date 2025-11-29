# opc_server.py
import time
import logging
from threading import Thread
from asyncua.sync import Server
from shared import SharedData
logging.getLogger("asyncua.server").setLevel(logging.ERROR)
logging.getLogger("asyncua.uaprotocol").setLevel(logging.ERROR)
logging.getLogger("asyncua.server.address_space").setLevel(logging.ERROR)

logger = logging.getLogger("opc_server")

class OPCServerThread(Thread):
    """
    Servidor OPC-UA sencillo que expone una variable 'Senoidal' y la actualiza leyendo
    desde SharedData protegido por semáforos.
    """
    def __init__(self, endpoint: str, namespace_uri: str, shared: SharedData, var_name: str = "Senoidal", update_period_s: float = 0.1):
        super().__init__(daemon=True)
        self.endpoint = endpoint
        self.namespace_uri = namespace_uri
        self.shared = shared
        self.var_name = var_name
        self.update_period_s = update_period_s
        self.server = None
        self.seno_node = None

    def run(self):
        logger.info("Arrancando OPC-UA server en %s", self.endpoint)
        server = Server()
        server.set_endpoint(self.endpoint)
        idx = server.register_namespace(self.namespace_uri)
        
        #server.init()


        # crear objeto y variable
        myobj = server.nodes.objects.add_object(idx, "PythonBridge")
        self.seno_node = myobj.add_variable(idx, self.var_name, 0.0)
        self.seno_node.set_writable(False)

        self.server = server
        server.start()
        logger.info("Servidor OPC-UA iniciado en %s - namespace %s (idx=%s)", self.endpoint, self.namespace_uri, idx)

        try:
            while not self.shared.stop_event.is_set():
                # leer valor protegido y actualizar nodo
                self.shared.sem_senoidal.acquire()
                try:
                    val = self.shared.senoidal
                finally:
                    self.shared.sem_senoidal.release()

                if val is not None:
                    try:
                        self.seno_node.set_value(val)
                    except Exception as e:
                        logger.exception("Error escribiendo valor en servidor OPC-UA: %s", e)
                time.sleep(self.update_period_s)
        finally:
            logger.info("Deteniendo servidor OPC-UA...")
            try:
                server.stop()
            except Exception:
                pass
            logger.info("Servidor OPC-UA detenido.")
