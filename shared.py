# shared.py
from threading import Semaphore, Event
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SharedData:
    counter: Optional[float] = None
    random: Optional[float] = None
    senoidal: Optional[float] = None
    # semáforos para proteger acceso
    sem_counter: Semaphore = field(default_factory=lambda: Semaphore(1))
    sem_random: Semaphore = field(default_factory=lambda: Semaphore(1))
    sem_senoidal: Semaphore = field(default_factory=lambda: Semaphore(1))
    # evento para parada limpia
    stop_event: Event = field(default_factory=Event)
