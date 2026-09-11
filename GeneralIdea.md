# Evolution Simulation: Generative Agents (design notes)

This file is the **product vision**, not a checklist of what the code already does.
The running prototype is a hex-grid sim with genetics, survival, trade/steal, and
optional LLM language adoption — see `README.md`.

Inspired by [Generative Agents](https://github.com/joonspk-research/generative_agents).
Focus: generational shifts, selection, and cultural/genetic evolution of agents.

## Core Concepts & Ideas

### 1. Genetics and Reproduction (DNA)
Instead of static personalities, each agent's core identity (their "DNA") is represented as a list of specific traits (e.g., "mimicry", "aggression", "empathy"). 
- **DNA Structure**: A genome is divided into three equal main categories:
  - **Dominant**: Genes that are highly likely to express as an active trait.
  - **Dormant**: Genes that are currently inactive but can become prominent in subsequent generations.
  - **Weak**: Genes that have a lower probability of expressing or being passed on as dominant.
- **Active Traits**: From the combination of dominant, dormant, and weak genes, the system derives the agent's **Active (Passive) Traits**—the actualized genes that straightforwardly and permanently impact the individual's behavior and abilities during its lifetime.
- **Reproduction & Crossover**: When agents reproduce, the offspring inherits a mix of genes from both parents, randomly varying in a 40% to 60% proportion from each parent. During this crossover phase, genes can randomly mutate and change their category (e.g., dormant to dominant, weak to dormant), except for the Active traits, which are only computed *after* the offspring has formed its base three categories.
- **Population Mutation**: During reproduction, there is also a slight chance for the offspring to randomly acquire a trait that is currently the most common within the entire population.
- **Selection**: Agents must gather resources or achieve social standing to "survive" long enough to reproduce. Traits that lead to failure are naturally weeded out.

### 2. Cultural Knowledge Transfer and Memory
Agents learn about their environment and build a memory stream during their lifetime.
- **Data Storage**: Memories and life experiences are efficiently stored and managed using JSON files.
- **Generational Handoff**: When agents age, they pass down a summary of life lessons to their offspring.
- **Information Decay and Myth-making**: The transfer isn't perfect. As knowledge is summarized and passed down across dozens of generations, we can observe the evolution of myths, traditions, or lost technologies, mirroring human cultural evolution.

### 3. Resource Scarcity and Societal Evolution
Introduce fluctuating environments (e.g., harsh winters, droughts, changing biomes) that require different survival strategies.
- Watch how societies evolve from highly cooperative (sharing resources to survive a harsh winter) to highly competitive (hoarding). 
- We can track if certain foundational traits (e.g., "Trusting" vs "Paranoid") have higher survival rates under different environmental pressures.

### 4. Evolution of Communication and Language
Agents must interact to trade, mate, or build.
- **Language Genesis**: Rather than starting with perfect English, agents begin by communicating with simple sounds, grunts, or short random tokens. Over successive generations, as they interact and develop shared meaning, their language natively evolves into more complex, comprehensible sentences.
- **Language Drift**: If agents are geographically separated in the sandbox, their shared concepts and terminology might drift, eventually resulting in two cultural groups that speak different dialects and struggle to cooperate natively.

### 5. Multi-Species Ecosystems
Introduce agents with fundamentally different goals or underlying architectures.
- **Symbiosis**: Some agents might be "Farmers" while others are "Guards". They co-evolve strategies to mutually benefit.
- **Predator/Prey Arms Race**: If one class of agents requires "consuming" the resources held by another, we can observe the evolution of complex hiding, fleeing, or trapping strategies.

## High-Level Architecture
- **Memory Stream**: Inherited conceptually from Generative Agents, with serialized JSON storage utilized for scale.
- **Lifecycle Engine**: A tick-based system that ages agents, depletes energy levels, and triggers reproduction, mutation, or death.
- **Evolution Engine**: Handles the 40-60 genetic crossover, trait category shifting, calculation of Active traits, and population-based mutation checks.
- **The Environment (Sandbox)**: A spatial grid where agents move, interact, leave physical artifacts, and harvest resources.
