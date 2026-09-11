import os
import shutil
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from engine import SimulationEngine
import language

app = Flask(__name__, static_folder='static')
CORS(app)

# Global engine instance
engine = None
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "agents")

def reset_engine():
    global engine
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    engine = SimulationEngine(data_dir=DATA_DIR, width=25, height=25)
    engine.spawn_initial_population(count=20)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/state', methods=['GET'])
def get_state():
    if not engine:
        reset_engine()
        
    agents_data = []
    for a in engine.agents:
        agents_data.append({
            "id": a.id,
            "q": a.position[0],
            "r": a.position[1],
            "dna": a.dna,
            "active_traits": a.active_traits, # Now a dictionary
            "language": a.language_model if hasattr(a, 'language_model') and a.language_model else [],
            "recent_memories": a.load_memory()[-5:] if os.path.exists(a.memory_filepath) else [],
            "food_count": len(a.inventory),
            "satisfaction": a.satisfaction,
            "age": a.age,
            "lifespan": a.lifespan
        })
        
    return jsonify({
        "tick": engine.tick,
        "width": engine.grid.width,
        "height": engine.grid.height,
        "population": len(engine.agents),
        "agents": agents_data,
        "food": [{"q": int(pos[0]), "r": int(pos[1])} for pos in engine.food_items.keys()],
        "ai_mode": language.last_mode_used
    })

@app.route('/api/step', methods=['POST'])
def step_simulation():
    if not engine:
        reset_engine()
    
    # Use request.get_json(silent=True) to avoid 400 bad request on empty body
    data = request.get_json(silent=True)
    steps = data.get('steps', 1) if data else 1
    
    for _ in range(steps):
        engine.step()
        
    return jsonify({"status": "success", "tick": engine.tick})

@app.route('/api/reset', methods=['POST'])
def reset_simulation():
    reset_engine()
    return jsonify({"status": "success", "message": "Simulation reset."})

if __name__ == '__main__':
    reset_engine()
    app.run(host='0.0.0.0', port=5000, debug=True)
