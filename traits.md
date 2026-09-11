# Agent Traits Reference

This document outlines the standard traits available in the genetic pool. Agents have a mix of 3 dominant, 3 dormant, and 3 weak genes. Their `active_traits` are drawn from these genetic pools upon birth and govern their behavior.

## Standard Traits

### Social & Interaction
- **aggression**: High likelihood of stealing food, fighting, or refusing to trade.
- **empathy**: High likelihood of giving or trading food to starving neighbors.
- **extroversion**: High desire to move towards others and communicate.
- **isolationism**: Tendency to move away from groups and avoid communication.

### Survival & Gathering
- **gluttony**: Will hoard food even when currently satisfied; prioritizes eating over reproducing.
- **foraging**: Moves efficiently towards the nearest food source.
- **mimicry**: High chance to instantly adopt a new word perfectly without mutation.
- **stubbornness**: Very low chance to adopt words; ignores communication intents.

### Movement
- **agility**: Chance to move 2 tiles instead of 1 per tick.
- **sluggishness**: High chance to skip movement on a tick.

## Implementation Details
You can use these trait strings directly in the engine configuration when we implement the interaction logic for stealing/trading. The OpenAI prompt also receives these strings directly to influence how the agent interprets language.
