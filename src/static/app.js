const canvas = document.getElementById('hex-canvas');
const ctx = canvas.getContext('2d');
let cw = canvas.width = window.innerWidth - 350;
let ch = canvas.height = window.innerHeight - 60;

// Hexagon rendering settings
const hexRadius = 15;
const hexWidth = Math.sqrt(3) * hexRadius;
const hexHeight = 2 * hexRadius;
// Axial to Pixel mapping values
const qBasisX = Math.sqrt(3) * hexRadius;
const qBasisY = 0;
const rBasisX = Math.sqrt(3) / 2 * hexRadius;
const rBasisY = 3 / 2 * hexRadius;

let isPlaying = false;
let loopInterval = null;
let simulationState = null;
let selectedAgentId = null;

// Controls
document.getElementById('btn-step').addEventListener('click', stepSimulation);
document.getElementById('btn-play').addEventListener('click', togglePlay);
document.getElementById('btn-pause').addEventListener('click', () => { isPlaying = true; togglePlay(); });
document.getElementById('btn-reset').addEventListener('click', resetSimulation);

window.addEventListener('resize', () => {
    cw = canvas.width = window.innerWidth - 350;
    ch = canvas.height = window.innerHeight - 60;
    draw();
});

canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Simple click detection by finding closest agent to pixel coords
    if (!simulationState) return;

    let closestAgent = null;
    let minDist = Infinity;

    // Calculate grid center offset
    const offsetX = cw / 2 - (simulationState.width * hexWidth) / 2;
    const offsetY = ch / 2 - (simulationState.height * hexHeight) / 2;

    for (const agent of simulationState.agents) {
        const px = offsetX + agent.q * qBasisX + agent.r * rBasisX;
        const py = offsetY + agent.q * qBasisY + agent.r * rBasisY;

        const dist = Math.sqrt(Math.pow(px - x, 2) + Math.pow(py - y, 2));
        if (dist < hexRadius && dist < minDist) {
            minDist = dist;
            closestAgent = agent;
        }
    }

    if (closestAgent) {
        selectedAgentId = closestAgent.id;
        updateAgentPanel();
        draw(); // redraw to highlight
    } else {
        selectedAgentId = null;
        updateAgentPanel();
        draw();
    }
});

async function fetchState() {
    try {
        const res = await fetch('/api/state');
        simulationState = await res.json();
        updateStats();
        draw();
        if (selectedAgentId) updateAgentPanel();
    } catch (e) {
        console.error("Error fetching state:", e);
    }
}

async function stepSimulation() {
    try {
        await fetch('/api/step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        await fetchState();
    } catch (e) {
        console.error("Error stepping:", e);
    }
}

async function resetSimulation() {
    isPlaying = false;
    togglePlay();
    selectedAgentId = null;
    try {
        await fetch('/api/reset', { method: 'POST' });
        await fetchState();
    } catch (e) {
        console.error("Error resetting:", e);
    }
}

function togglePlay() {
    isPlaying = !isPlaying;
    const playBtn = document.getElementById('btn-play');

    if (isPlaying) {
        playBtn.textContent = 'Playing...';
        playBtn.style.backgroundColor = '#45a049';
        playLoop();
    } else {
        playBtn.textContent = 'Play';
        playBtn.style.backgroundColor = 'var(--accent)';
    }
}

async function playLoop() {
    if (!isPlaying) return;
    await stepSimulation();
    if (isPlaying) {
        setTimeout(playLoop, 200);
    }
}

function updateStats() {
    if (!simulationState) return;
    document.getElementById('stat-tick').textContent = simulationState.tick;
    document.getElementById('stat-pop').textContent = simulationState.population;

    const modeLabel = document.getElementById('ai-mode-label');
    if (simulationState.ai_mode && modeLabel) {
        modeLabel.textContent = simulationState.ai_mode;
        if (simulationState.ai_mode === "real testing") {
            modeLabel.className = "mode-label real";
        } else {
            modeLabel.className = "mode-label";
        }
    }
}

function updateAgentPanel() {
    const panel = document.getElementById('agent-info');
    if (!selectedAgentId || !simulationState) {
        panel.innerHTML = '<p>Select an agent on the grid to view details.</p>';
        return;
    }

    const agent = simulationState.agents.find(a => a.id === selectedAgentId);
    if (!agent) {
        panel.innerHTML = '<p>Agent died or not found.</p>';
        selectedAgentId = null;
        draw(); // remove highlight
        return;
    }

    let html = `
        <p><strong>ID:</strong> ${agent.id.substring(0, 8)}...</p>
        <p><strong>Pos:</strong> (${agent.q}, ${agent.r})</p>
        <p><strong>Age:</strong> ${agent.age} / ${agent.lifespan} ticks</p>
        
        <h3 style="margin-top: 15px; margin-bottom: 8px;">Active Traits (0-10)</h3>
        <div>
            ${Object.entries(agent.active_traits).map(([trait, val]) => `<span class="trait-tag active">${trait}: ${val}</span>`).join('')}
            ${Object.keys(agent.active_traits).length === 0 ? '<em>None</em>' : ''}
        </div>
        
        <h3 style="margin-top: 15px; margin-bottom: 8px;">Genetics (DNA)</h3>
        <p><strong>Dominant:</strong> ${agent.dna.dominant.map(t => `<span class="trait-tag dominant">${t}</span>`).join('') || '<em>None</em>'}</p>
        <p><strong>Dormant:</strong> ${agent.dna.dormant.map(t => `<span class="trait-tag dormant">${t}</span>`).join('') || '<em>None</em>'}</p>
        <p><strong>Weak:</strong> ${agent.dna.weak.map(t => `<span class="trait-tag weak">${t}</span>`).join('') || '<em>None</em>'}</p>
        
        <h3 style="margin-top: 15px; margin-bottom: 8px;">Semantic Dictionary</h3>
        <div class="vocab-list" style="padding: 8px; background: rgba(0,0,0,0.2); border-radius: 5px; color: #a5d6a7; font-size: 0.9em; line-height: 1.4;">
            ${agent.language && Object.keys(agent.language).length > 0 ?
            Object.entries(agent.language).map(([cat, words]) =>
                `<div style="margin-bottom: 2px;"><strong>${cat}:</strong> ${words && words.length > 0 ? words.map(w => `"${w}"`).join(', ') : '<em>_</em>'}</div>`
            ).join('')
            : '<em>Silent</em>'}
        </div>
        
        <h3 style="margin-top: 15px; margin-bottom: 8px;">Recent Memories</h3>
        <div class="memories">
    `;

    if (agent.recent_memories && agent.recent_memories.length > 0) {
        // Reverse to show newest on top
        const mems = [...agent.recent_memories].reverse();
        mems.forEach(m => {
            html += `<div class="log-entry"><strong>Tick ${m.tick}:</strong> ${m.event}</div>`;
        });
    } else {
        html += `<p><em>No memories yet.</em></p>`;
    }
    html += `</div>`;

    panel.innerHTML = html;
}

function drawHexagon(x, y, radius, color, isHighlighted) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
        // Flat topped hexagons
        const angle_deg = 60 * i;
        const angle_rad = Math.PI / 180 * angle_deg;
        const hx = x + radius * Math.cos(angle_rad);
        const hy = y + radius * Math.sin(angle_rad);
        if (i === 0) {
            ctx.moveTo(hx, hy);
        } else {
            ctx.lineTo(hx, hy);
        }
    }
    ctx.closePath();

    ctx.fillStyle = color;
    ctx.fill();

    if (isHighlighted) {
        ctx.strokeStyle = "white";
        ctx.lineWidth = 3;
    } else {
        ctx.strokeStyle = "var(--hex-border)";
        ctx.lineWidth = 1;
    }
    ctx.stroke();
}

function draw() {
    // Clear canvas
    ctx.clearRect(0, 0, cw, ch);

    // Helper function to string-to-color
    function stringToColor(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        let color = '#';
        for (let i = 0; i < 3; i++) {
            const value = (hash >> (i * 8)) & 0xFF;
            color += ('00' + value.toString(16)).substr(-2);
        }
        return color;
    }

    if (!simulationState) return;

    // We want to center the grid
    const mapW = simulationState.width * hexWidth;
    const mapH = simulationState.height * hexHeight;
    const offsetX = cw / 2 - mapW / 2;
    const offsetY = ch / 2 - mapH / 2;

    // Draw base grid (we draw a rectangular bound of hexes for simplicity)
    for (let r = 0; r < simulationState.height; r++) {
        for (let q = 0; q < simulationState.width; q++) {
            // Axial to Pixel mapping
            const px = offsetX + q * qBasisX + r * rBasisX;
            const py = offsetY + q * qBasisY + r * rBasisY;

            drawHexagon(px, py, hexRadius - 1, "var(--hex-fill)", false);
        }
    }

    // Draw food
    if (simulationState.food) {
        ctx.fillStyle = "#A5D6A7"; // Light green for food
        ctx.font = "bold 14px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        for (const f of simulationState.food) {
            const px = offsetX + f.q * qBasisX + f.r * rBasisX;
            const py = offsetY + f.q * qBasisY + f.r * rBasisY;
            ctx.fillText("F", px, py);
        }
    }

    // Draw agents
    // If multiple agents on same tile, we'll draw a badge or slightly offset them
    const tileCounts = {};

    for (const agent of simulationState.agents) {
        const px = offsetX + agent.q * qBasisX + agent.r * rBasisX;
        const py = offsetY + agent.q * qBasisY + agent.r * rBasisY;

        const key = `${agent.q},${agent.r}`;
        tileCounts[key] = (tileCounts[key] || 0) + 1;

        const isSelected = agent.id === selectedAgentId;

        // Define color based on the first dominant trait (for species clustering visual)
        let rootTrait = "default";
        if (agent.dna && agent.dna.dominant && agent.dna.dominant.length > 0) {
            rootTrait = agent.dna.dominant[0];
        }
        let agentColor = stringToColor(rootTrait + "offset"); // added offset to make colors pop

        const color = isSelected ? '#ffeb3b' : agentColor;

        drawHexagon(px, py, hexRadius - 3, color, isSelected);

        // Label if multiple
        if (tileCounts[key] > 1 && !isSelected) {
            ctx.fillStyle = "white";
            ctx.font = "10px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(tileCounts[key], px, py);
        }
    }
}

// Initial load
fetchState();
