import random
import language

def calculate_active_traits(dna, apply_ai_trait=False):
    """
    Active traits are calculated based on dominant genes (high chance), 
    dormant genes (can sometimes slip in), and weak genes (very low chance).
    Returns a dictionary mapping trait strings to magnitudes (0-10).
    """
    active = {}
    
    # Dominant genes have an 80% chance of expressing
    for gene in dna.get("dominant", []):
        if random.random() < 0.8:
            active[gene] = random.randint(7, 10)
            
    # Dormant genes have a 10% chance of randomly becoming active directly
    # (Though primarily they wait to crossover into dominant in next gen)
    for gene in dna.get("dormant", []):
        if random.random() < 0.1:
            active[gene] = random.randint(3, 7)
            
    # Weak genes have a 2% chance
    for gene in dna.get("weak", []):
        if random.random() < 0.02:
            active[gene] = random.randint(1, 4)
            
    if apply_ai_trait:
        # LLM invents one unique social trait contextually
        ai_name, ai_mag = language.generate_ai_trait(active)
        active[ai_name] = ai_mag
        
    return active

def crossover(parent1_dna, parent2_dna, all_population_traits=None):
    """
    Reproduces DNA from two parents. Random 40-60 split.
    Gene categories can mutate (e.g., dormant -> dominant).
    Possibility to receive the most common trait in the population.
    """
    child_dna = {"dominant": [], "dormant": [], "weak": []}
    
    # Pool all genes from both parents
    p1_genes = [(g, "parent1") for cat in parent1_dna.values() for g in cat]
    p2_genes = [(g, "parent2") for cat in parent2_dna.values() for g in cat]
    
    all_genes = p1_genes + p2_genes
    # Shuffle to ensure randomness before picking
    random.shuffle(all_genes)
    
    # Determine split proportion (40 to 60 percent from parent 1)
    split_ratio = random.uniform(0.4, 0.6)
    target_p1_count = int(len(all_genes) * split_ratio)
    
    selected_genes = []
    p1_selected = 0
    p2_selected = 0
    
    for gene, source in all_genes:
        if source == "parent1" and p1_selected < target_p1_count:
            selected_genes.append(gene)
            p1_selected += 1
        elif source == "parent2" and p2_selected < (len(all_genes) - target_p1_count):
            selected_genes.append(gene)
            p2_selected += 1
            
    # Now assign the selected genes randomly to new categories (mutation chance)
    for gene in selected_genes:
        # Default behavior: 20% dominant, 40% dormant, 40% weak
        chosen_cat = random.choices(["dominant", "dormant", "weak"], weights=[0.2, 0.4, 0.4], k=1)[0]
        if gene not in child_dna[chosen_cat]:
            child_dna[chosen_cat].append(gene)
            
    # Slight chance to receive the most common trait in population
    if all_population_traits and random.random() < 0.1: # 10% chance
        if all_population_traits:
            most_common = max(all_population_traits, key=all_population_traits.get)
            if most_common not in child_dna["dominant"]:
                child_dna["dominant"].append(most_common)
                
    return child_dna
