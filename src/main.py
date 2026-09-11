import time
import os
import shutil
from engine import SimulationEngine

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "agents")
    
    # Clean up old data for testing purposes
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        
    engine = SimulationEngine(data_dir=data_dir, width=25, height=15)
    engine.spawn_initial_population(count=20)
    
    print("Starting Evolution Simulation...")
    time.sleep(1)
    
    try:
        while True:
            # Step the simulation
            stats = engine.step()
            
            # Draw the grid
            clear_console()
            print(f"Generation / Tick: {stats['tick']} | Population: {stats['population']}")
            print("-" * (engine.grid.width + 2))
            
            grid_display = [[" " for _ in range(engine.grid.width)] for _ in range(engine.grid.height)]
            for agent in engine.agents:
                x, y = agent.position
                # Simple display check boundaries just in case
                if 0 <= x < engine.grid.width and 0 <= y < engine.grid.height:
                    if grid_display[y][x] == " ":
                        grid_display[y][x] = "A"
                    elif grid_display[y][x] == "A":
                        grid_display[y][x] = "2"
                    elif grid_display[y][x].isdigit():
                        count = int(grid_display[y][x]) + 1
                        grid_display[y][x] = str(count) if count < 10 else "+"
                    
            for row in grid_display:
                print("|" + "".join(row) + "|")
            print("-" * (engine.grid.width + 2))
            print("\nPress Ctrl+C to stop.")
            
            # Brief pause
            time.sleep(0.1)
            
            # Stop condition for automated basic test run
            if stats['tick'] >= 30: 
                break

    except KeyboardInterrupt:
        pass
        
    print("\nSimulation Paused/Ended.")
    print("Sample vocabulary of top 3 surviving agents:")
    for agent in engine.agents[:3]:
        print(f"Agent {agent.id}: {agent.language_model.get('vocabulary')}")

if __name__ == "__main__":
    main()
