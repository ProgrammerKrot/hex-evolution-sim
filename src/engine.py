import random
import os
from agent import Agent
from grid import HexGrid
import genetics
import language

class SimulationEngine:
    def __init__(self, data_dir, width=20, height=20):
        self.data_dir = data_dir
        self.grid = HexGrid(width, height)
        self.agents = []
        self.food_items = {} # (q, r) -> tick_spawned
        self.tick = 0
        os.makedirs(self.data_dir, exist_ok=True)

    def spawn_initial_population(self, count=10):
        """Spawns initial agents at random locations."""
        for _ in range(count):
            pos = (random.randint(0, self.grid.width - 1), random.randint(0, self.grid.height - 1))
            # Start with some random genes
            initial_dna = {
                "dominant": [random.choice(["aggression", "empathy", "curiosity", "mimicry"])],
                "dormant": [random.choice(["speed", "strength", "stealth"])],
                "weak": [random.choice(["paranoid", "trusting"])]
            }
            active = genetics.calculate_active_traits(initial_dna)
            agent = Agent(data_dir=self.data_dir, position=pos, dna=initial_dna, active_traits=active, language_model=language.generate_initial_language())
            self.agents.append(agent)
            
            # Spawn 2 localized foods nearby so they don't die instantly
            for _ in range(2):
                nearby = (pos[0] + random.choice([-1, 0, 1]), pos[1] + random.choice([-1, 0, 1]))
                if self.grid.is_valid_position(nearby) and nearby not in self.food_items:
                    self.food_items[nearby] = self.tick
            
    def step(self):
        """Advances the simulation by one tick."""
        self.tick += 1
        
        # 0. Update satisfaction and starvation
        survivors = []
        for agent in self.agents:
            agent.satisfaction -= 1
            if agent.satisfaction <= 0:
                if agent.eat(): # Try to eat from inventory
                    agent.memory_stream[-1]['tick'] = self.tick
                    survivors.append(agent)
                else:
                    agent.add_memory("Starved to death.", self.tick)
                    agent.save_core()
            else:
                survivors.append(agent)
                
        self.agents = survivors
        
        # 0.5 Spawn Food (pop + 2 every 3 ticks)
        if self.tick % 3 == 0:
            spawn_count = len(self.agents) + 2
            empty_tiles = set()
            agent_positions = {a.position for a in self.agents}
            
            for agent in self.agents:
                q, r = agent.position
                for dq in range(-3, 4):
                    for dr in range(-3, 4):
                        pos = (q + dq, r + dr)
                        if self.grid.is_valid_position(pos) and pos not in agent_positions and pos not in self.food_items:
                            if self.grid.hex_distance(agent.position, pos) <= 3:
                                empty_tiles.add(pos)
            
            empty_tiles_list = list(empty_tiles)
            
            # Fallback if no reachable empty tiles were found
            if not empty_tiles_list:
                for q in range(self.grid.width):
                    for r in range(self.grid.height):
                        pos = (q, r)
                        if pos not in agent_positions and pos not in self.food_items:
                            empty_tiles_list.append(pos)
                            
            if empty_tiles_list:
                spawns = random.sample(empty_tiles_list, min(spawn_count, len(empty_tiles_list)))
                for pos in spawns:
                    self.food_items[pos] = self.tick
            else:
                # Absolute fallback if map is utterly empty of agents
                for _ in range(spawn_count):
                    q, r = random.randint(0, self.grid.width-1), random.randint(0, self.grid.height-1)
                    if (q, r) not in self.food_items:
                        self.food_items[(q,r)] = self.tick
        
        # 1. Movement on Hex Grid (Seek Food or Random)
        for agent in list(self.agents):
            directions = [
                (1, 0), (1, -1), (0, -1),
                (-1, 0), (-1, 1), (0, 1)
            ]
            
            closest_food = None
            min_dist = 999
            
            # Clean up known_food_locations that are no longer in food_items
            agent.known_food_locations = {pos for pos in agent.known_food_locations if pos in self.food_items}
            
            for food_pos in self.food_items.keys():
                dist = self.grid.hex_distance(agent.position, food_pos)
                # Move towards food if it's within vision radius OR if someone told us about it
                if dist <= 8 or food_pos in agent.known_food_locations:
                    if dist < min_dist:
                        min_dist = dist
                        closest_food = food_pos
            
            best_dq, best_dr = random.choice(directions)
            
            if closest_food:
                best_step_dist = 999
                for dq, dr in directions:
                    step_pos = (agent.position[0] + dq, agent.position[1] + dr)
                    if self.grid.is_valid_position(step_pos):
                        step_dist = self.grid.hex_distance(step_pos, closest_food)
                        if step_dist < best_step_dist:
                            best_step_dist = step_dist
                            best_dq, best_dr = dq, dr
            
            # Simple facing update
            agent.facing = (best_dq, best_dr)
            
            new_pos = (agent.position[0] + best_dq, agent.position[1] + best_dr)
            if self.grid.is_valid_position(new_pos):
                agent.position = new_pos
                
                # Check for food collection
                if agent.position in self.food_items:
                    agent.inventory.append({"tick_collected": self.tick})
                    del self.food_items[agent.position]
                    agent.add_memory("Gathered food off the ground.", self.tick)
                
        # 2. Reproduction Check (Distance <= 1)
        new_agents = []
        ai_repro_calls = 0
        for i, a1 in enumerate(self.agents):
            for a2 in self.agents[i+1:]:
                if self.grid.hex_distance(a1.position, a2.position) <= 1:
                    if a1.satisfaction > 0 and a2.satisfaction > 0: # Requires BOTH to be satisfied
                        # Language Complexity = Reproduction Advantage
                        shared_words_count = 0
                        total_word_length = 0
                        for cat in ["food", "trade", "danger", "greeting"]:
                            shared = set(a1.language_model.get(cat, [])).intersection(set(a2.language_model.get(cat, [])))
                            shared_words_count += len(shared)
                            total_word_length += sum(len(w) for w in shared)
                        
                        # Boost repro chance by complexity (longer words/more complexity = higher chance)
                        repro_chance = 0.05 + min(0.40, shared_words_count * 0.05) + min(0.30, total_word_length * 0.01)
                        
                        # They might reproduce (prevent immediate population explosion)
                        if random.random() < repro_chance: # Scaled by shared vocabulary and complexity
                            # Get most common trait in population
                            all_traits = {}
                            for a in self.agents:
                                for t in a.active_traits.keys():
                                    all_traits[t] = all_traits.get(t, 0) + 1
                            
                            child_dna = genetics.crossover(a1.dna, a2.dna, all_traits)
                            
                            # Safely blend the scaled integers from parents
                            apply_ai = (ai_repro_calls < 1)
                            if apply_ai:
                                ai_repro_calls += 1
                                
                            child_active = genetics.calculate_active_traits(child_dna, apply_ai_trait=apply_ai)
                            parent_traits = set(list(a1.active_traits.keys()) + list(a2.active_traits.keys()))
                            for t in parent_traits:
                                v1 = a1.active_traits.get(t, 0)
                                v2 = a2.active_traits.get(t, 0)
                                base = int((v1 + v2) / 2)
                                if random.random() < 0.3:
                                    base += random.choice([-2, -1, 1, 2])
                                base = max(0, min(10, base)) # Clamp 0-10
                                if base > 0:
                                    child_active[t] = base

                            child_pos = (a1.position[0], a1.position[1]) 
                            child = Agent(data_dir=self.data_dir, position=child_pos, dna=child_dna, active_traits=child_active)
                            
                            # Child inherits a simple version of language from one parent
                            child.language_model = {cat: list(a1.language_model.get(cat, [])) for cat in ["food", "trade", "danger", "greeting"]}
                            
                            new_agents.append(child)
                            
                            a1.add_memory(f"Reproduced with {a2.id}. Child id: {child.id}", self.tick)
                            a2.add_memory(f"Reproduced with {a1.id}. Child id: {child.id}", self.tick)
                            
                            a1.satisfaction = max(0, a1.satisfaction - 1)
                            a2.satisfaction = max(0, a2.satisfaction - 1)

        self.agents.extend(new_agents)
        
        # 3. Interactions (Reproduction & Comm & Steal)
        ai_chat_calls = 0
        for i, a1 in enumerate(self.agents):
            for j, a2 in enumerate(self.agents):
                if i == j: continue
                dist = self.grid.hex_distance(a1.position, a2.position)
                
                # Stealing (Distance == 1, A1 is precisely behind A2)
                if dist == 1 and len(a2.inventory) > 0:
                    behind_a2 = (a2.position[0] - a2.facing[0], a2.position[1] - a2.facing[1])
                    if a1.position == behind_a2:
                        aggression = a1.active_traits.get("aggression", 0)
                        if aggression > 5 and random.random() < (aggression / 10.0):
                            stolen_food = a2.inventory.pop(0)
                            a1.inventory.append(stolen_food)
                            a1.add_memory(f"Successfully stole food from {a2.id}'s back.", self.tick)
                            a2.add_memory(f"My food was stolen from behind by {a1.id}!", self.tick)

                # Communication Check (Distance <= 4)
                if i < j and dist <= 4:
                    # Conversation as a Free Action (scaled by traits)
                    # Base 10%, scaled up to 100% by extroverted traits
                    trait_bonus = (a1.active_traits.get("empathy", 0) + a1.active_traits.get("curiosity", 0) + a1.active_traits.get("mimicry", 0)) / 30.0
                    comm_chance = min(1.0, 0.1 + trait_bonus)
                    
                    if ai_chat_calls < 2 and random.random() < comm_chance:
                        ai_chat_calls += 1
                        sentence = {}
                        for cat in ["food", "trade", "danger", "greeting"]:
                            if a1.language_model.get(cat):
                                # Make sentences using 1 to 3 words from this category
                                sample_size = min(len(a1.language_model[cat]), random.randint(1, 3))
                                sentence[cat] = " ".join(random.sample(a1.language_model[cat], sample_size))
                            else:
                                sentence[cat] = "_"
                                
                        new_vocab, thought, trade, understanding = language.process_language_adoption(a2.language_model, sentence, list(a2.active_traits.keys()), len(a2.inventory), a2.satisfaction)
                        a2.language_model = new_vocab
                        
                        a1.add_memory(f"Communicated sentence {sentence} to {a2.id}", self.tick)
                        a2.add_memory(f"Heard {sentence} from {a1.id}. AI Thought: {thought} (Understanding: {understanding:.2f})", self.tick)
                        
                        # Knowledge / Vision Sharing
                        # Apply Understanding Score as an error rate to the Vision Coordinates
                        shared_food_count = 0
                        for food_pos in self.food_items.keys():
                            original_pos = food_pos
                            # Misunderstanding / Coordinate Corruption
                            if understanding < 1.0:
                                corrupt_chance = 1.0 - understanding
                                if random.random() < corrupt_chance:
                                    # Shift coordinate by 1-2
                                    q_shift = random.choice([-2, -1, 1, 2])
                                    r_shift = random.choice([-2, -1, 1, 2])
                                    food_pos = (food_pos[0] + q_shift, food_pos[1] + r_shift)
                                    
                            if self.grid.hex_distance(a1.position, original_pos) <= 8 and food_pos not in a2.known_food_locations:
                                a2.known_food_locations.add(food_pos)
                                shared_food_count += 1
                            if self.grid.hex_distance(a2.position, original_pos) <= 8 and food_pos not in a1.known_food_locations:
                                a1.known_food_locations.add(food_pos)
                                shared_food_count += 1
                        
                        if shared_food_count > 0:
                            a1.add_memory(f"Shared vision and known food locations with {a2.id}. ({shared_food_count} new locs)", self.tick)
                            a2.add_memory(f"Received vision and known food locations from {a1.id}. ({shared_food_count} new locs)", self.tick)
                        
                        if trade and len(a2.inventory) > 0:
                            traded_food = a2.inventory.pop(0)
                            a1.inventory.append(traded_food)
                            a1.add_memory(f"Traded with {a2.id} and received 1 food.", self.tick)
                            a2.add_memory(f"Gave 1 food to {a1.id} after communication.", self.tick)

        # 4. Save state
        for agent in self.agents:
            agent.save_core()

        return {"tick": self.tick, "population": len(self.agents)}
