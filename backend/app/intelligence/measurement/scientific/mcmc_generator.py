import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

class MarkovChainCorpusGenerator:
    def __init__(self):
        # The Transition Matrix: P(Next_State | Current_State)
        self.transition_matrix = {
            'idle': {'commit': 0.1, 'pr_open': 0.05, 'idle': 0.85},
            'commit': {'commit': 0.6, 'pr_open': 0.3, 'idle': 0.1},
            'pr_open': {'review_request': 0.8, 'commit': 0.15, 'pr_close': 0.05},
            'review_request': {'pr_approved': 0.6, 'pr_rejected': 0.3, 'commit': 0.1},
            'pr_rejected': {'commit': 0.8, 'pr_close': 0.2},
            'pr_approved': {'pr_merge': 0.9, 'commit': 0.1},
            'pr_merge': {'idle': 0.8, 'commit': 0.2},
            'pr_close': {'idle': 0.9, 'commit': 0.1}
        }
        
    def generate_synthetic_history(self, num_events: int = 100, start_time: datetime = None) -> List[Any]:
        """
        Walks the Markov Chain to generate a mathematically valid, 
        yet entirely novel, sequence of engineering events.
        """
        history = []
        current_state = 'idle'
        current_time = start_time or datetime.utcnow()
        
        # Mock Developers and Files for correlation testing
        developers = ['dev_A', 'dev_B', 'dev_C']
        files = ['auth.py', 'router.ts', 'api.go']
        
        for _ in range(num_events):
            # 1. Look up the probabilities for the current state
            probabilities = self.transition_matrix.get(current_state, {'idle': 1.0})
            
            # 2. Roll the weighted dice to find the next state
            next_state = random.choices(
                population=list(probabilities.keys()),
                weights=list(probabilities.values())
            )[0]
            
            # 3. Advance time based on state transition
            # e.g., A commit takes longer than a review click
            time_delta = timedelta(minutes=random.randint(5, 120)) if next_state == 'commit' else timedelta(minutes=random.randint(1, 15))
            current_time += time_delta
            
            # 4. Construct the Mock Event
            # Assuming a standard mock structure compatible with your Observation Layer
            event = self._build_mock_observation(next_state, current_time, random.choice(developers), random.choice(files))
            history.append(event)
            
            current_state = next_state
            
        return history

    def _build_mock_observation(self, state: str, timestamp: datetime, developer: str, file: str) -> Any:
        """Helper to construct the event object."""
        # Replace with your actual Observation/Mock logic
        class MockObservation:
            def __init__(self, s, t, d, f):
                self.id = str(uuid.uuid4())
                self.type = s
                self.timestamp = t
                self.target_entity = d
                self.metadata = {"file": f, "status": s}
        return MockObservation(state, timestamp, developer, file)
