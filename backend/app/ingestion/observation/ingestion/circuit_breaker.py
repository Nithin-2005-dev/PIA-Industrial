import time
import logging
import threading
from enum import Enum, auto

from pydantic import ValidationError
from app.ingestion.observation.ingestion.normalizer import SchemaMismatchError

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()

class CircuitOpenException(Exception):
    """Raised when the circuit is OPEN, preventing network calls."""
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout_sec: float = 60.0):
        self.state = CircuitState.CLOSED
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.probing = False
        self.lock = threading.Lock()

    def is_open(self) -> bool:
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return False
                
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout_sec:
                    # Time to probe, but don't change state here. Just return False to let call() handle it.
                    return False
                return True
                
            if self.state == CircuitState.HALF_OPEN:
                if self.probing:
                    return True
                return False
                
        return False

    def record_success(self):
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                logger.info("CircuitBreaker probe succeeded. Entering CLOSED state.")
                self.state = CircuitState.CLOSED
                self.probing = False
            self.failure_count = 0

    def record_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
                logger.warning("CircuitBreaker tripped to OPEN state.")
                self.state = CircuitState.OPEN
                self.probing = False

    def call(self, func, *args, **kwargs):
        """Execute a function protected by the circuit breaker."""
        with self.lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout_sec:
                    self.state = CircuitState.HALF_OPEN
                    self.probing = True
                else:
                    raise CircuitOpenException(f"Circuit is OPEN. Try again after {self.recovery_timeout_sec}s.")
            elif self.state == CircuitState.HALF_OPEN:
                if self.probing:
                    raise CircuitOpenException(f"Circuit is HALF_OPEN and currently probing. Wait.")
                self.probing = True
                
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except (SchemaMismatchError, ValidationError) as logic_error:
            # Poison Pill Storm protection: business logic errors should NOT trip the circuit.
            # We record a success for the network request itself, then re-raise the logic error.
            self.record_success()
            raise logic_error
        except Exception as e:
            self.record_failure()
            raise e
