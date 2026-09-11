import uuid
import json
import os
import random

import language

class Agent:
    def __init__(self, data_dir, id=None, position=(0,0), dna=None, active_traits=None, language_model=None, inventory=None, satisfaction=3, facing=(1,0), age=0, lifespan=None):
        self.id = id if id else str(uuid.uuid4())
        self.position = position
        self.facing = facing # Direction last moved (q_diff, r_diff)
        
        # DNA is split into dominant, dormant, weak
        self.dna = dna if dna else {"dominant": [], "dormant": [], "weak": []}
        # Dictionary mapping trait_name -> integer_value (0-10)
        self.active_traits = active_traits if active_traits else {}
        
        # Language model: dictionary mapping concept -> list of sounds
        if isinstance(language_model, list):
            self.language_model = {"food": [], "trade": [], "danger": [], "greeting": language_model}
        else:
            self.language_model = language_model if language_model else {"food": [], "trade": [], "danger": [], "greeting": []}
        
        # Survival
        self.inventory = inventory if inventory else [] # elements: {"tick_collected": int}
        self.satisfaction = satisfaction
        self.known_food_locations = set()
        
        # Aging
        self.age = age
        self.lifespan = lifespan if lifespan else random.randint(6, 12)
        
        # Memory is kept in a separate property but flushed to memory.json
        self.memory_stream = []
        
        # Path setup
        self.agent_dir = os.path.join(data_dir, self.id)
        os.makedirs(self.agent_dir, exist_ok=True)
        self.core_filepath = os.path.join(self.agent_dir, "core.json")
        self.memory_filepath = os.path.join(self.agent_dir, "memory.json")
        
        # Only save if creating a new agent (i.e. if memory file doesn't exist)
        if not os.path.exists(self.core_filepath):
            self.save_core()
            self._init_memory()

    def save_core(self):
        core_data = {
            "id": self.id,
            "position": self.position,
            "facing": self.facing,
            "dna": self.dna,
            "active_traits": self.active_traits,
            "language_model": self.language_model,
            "inventory": self.inventory,
            "satisfaction": self.satisfaction,
            "age": self.age,
            "lifespan": self.lifespan
        }
        os.makedirs(self.agent_dir, exist_ok=True)
        with open(self.core_filepath, 'w') as f:
            json.dump(core_data, f, indent=4)

    def eat(self):
        """Attempts to consume 1 food from inventory to restore satisfaction to 3."""
        if self.satisfaction < 3 and len(self.inventory) > 0:
            self.inventory.pop(0) # Eat oldest food
            self.satisfaction = 3
            self.add_memory("Ate 1 food from inventory.", -1) # Tick updated in engine loop
            return True
        return False

    def _init_memory(self):
        """Initialize the memory JSON if it doesn't exist."""
        with open(self.memory_filepath, 'w') as f:
            json.dump([], f)

    def add_memory(self, event, tick):
        """Append an event to the memory stream and save to file."""
        memory_entry = {
            "tick": tick,
            "event": event
        }
        self.memory_stream.append(memory_entry)
        
        os.makedirs(self.agent_dir, exist_ok=True)
        
        # Load, append, and save
        if os.path.exists(self.memory_filepath):
            try:
                with open(self.memory_filepath, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []
        else:
            data = []
            
        data.append(memory_entry)
        
        with open(self.memory_filepath, 'w') as f:
            json.dump(data, f, indent=4)
            
    def load_memory(self):
        """Load the entire memory stream into memory_stream var."""
        if os.path.exists(self.memory_filepath):
            with open(self.memory_filepath, 'r') as f:
                self.memory_stream = json.load(f)
        return self.memory_stream

    @classmethod
    def load(cls, data_dir, agent_id):
        core_filepath = os.path.join(data_dir, agent_id, "core.json")
        with open(core_filepath, 'r') as f:
            data = json.load(f)
        
        agent = cls(
            data_dir=data_dir,
            id=data["id"],
            position=tuple(data["position"]),
            facing=tuple(data.get("facing", (1,0))),
            dna=data.get("dna"),
            active_traits=data.get("active_traits", {}),
            language_model=data.get("language_model", {"food": [], "trade": [], "danger": [], "greeting": []}),
            inventory=data.get("inventory", []),
            satisfaction=data.get("satisfaction", 3),
            age=data.get("age", 0),
            lifespan=data.get("lifespan")
        )
        return agent
