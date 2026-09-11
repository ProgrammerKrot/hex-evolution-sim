import json
import os
import random

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

HAS_OPENAI = False
client = None
last_mode_used = "mockup testing"


def _configure_openai():
    """Use OPENAI_API_KEY from the environment. No key -> mock mode."""
    global HAS_OPENAI, client
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key or OpenAI is None:
        HAS_OPENAI = False
        client = None
        return
    client = OpenAI(api_key=api_key)
    HAS_OPENAI = True


_configure_openai()


def mock_llm_language_adoption(agent_vocabulary, heard_sentence, food_count):
    """
    Mocks an LLM deciding how to interpret a new sentence.
    Returns new_vocab, thought, trade_food, understanding_score
    """
    new_vocab = {k: list(v) for k, v in agent_vocabulary.items()}

    if random.random() < 0.3:
        return new_vocab, "Mocking: Ignored", False, 0.0

    understanding_score = random.uniform(0.1, 1.0)

    for concept, word in heard_sentence.items():
        if word == "_":
            continue
        if random.random() < 0.2:
            chars = list(word)
            if chars:
                idx = random.randint(0, len(chars) - 1)
                chars[idx] = random.choice("abcdefghijklmnopqrstuvwxyz")
            word = "".join(chars)

        if word and word not in new_vocab.get(concept, []):
            if concept not in new_vocab:
                new_vocab[concept] = []
            new_vocab[concept].append(word)

    trade = understanding_score > 0.5 and food_count > 0
    return new_vocab, "Mocking: Processed semantic sentence.", trade, understanding_score


def generate_ai_trait(base_traits):
    """
    Asks the LLM to invent one novel social, psychological, or abstract
    trait. Returns a tuple: (trait_name_string, magnitude_0_10).
    """
    if HAS_OPENAI:
        try:
            prompt = (
                f"You are part of an evolution simulation creating a new creature. "
                f"Its baseline genetic traits are: {', '.join(base_traits.keys())}.\n"
                "Invent exactly ONE entirely new, creative, social or psychological abstract "
                "trait that isn't on the list (like 'paranoia', 'superstition', 'altruism', "
                "'gregariousness', 'deception').\n"
                "Also assign it a magnitude from 0 to 10.\n"
                "Respond in JSON format with exactly two keys: 'trait_name' (string, one word) "
                "and 'magnitude' (integer 0-10)."
            )

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creature simulation engine. Output perfectly formatted JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=60,
                temperature=0.9,
            )

            data = json.loads(response.choices[0].message.content.strip())
            name = str(data.get("trait_name", "eccentricity")).lower().strip().replace(" ", "_")
            mag = int(data.get("magnitude", random.randint(3, 8)))
            return name, max(0, min(10, mag))
        except Exception as e:
            print(f"OpenAI error on trait gen: {e}")
            return random.choice(["curiosity", "paranoia", "altruism"]), random.randint(1, 10)
    return random.choice(["curiosity", "paranoia", "altruism"]), random.randint(1, 10)


def process_language_adoption(agent_vocabulary, heard_sentence, active_traits, food_count, satisfaction):
    global last_mode_used
    if HAS_OPENAI:
        try:
            prompt = (
                f"You are a creature in a simulation. Your traits are: {', '.join(active_traits)}.\n"
                f"You have {food_count} food and {satisfaction}/3 satisfaction until you starve.\n"
                f"Another creature spoke to you. Their semantic sentence is: {heard_sentence}.\n"
                f"Your current semantic vocabulary is: {agent_vocabulary}.\n"
                "Do you adopt these words into your vocabulary categories? Do you trade 1 food "
                "(if you have it)?\n"
                "Most importantly, generate an 'understanding_score' from 0.0 to 1.0 based on how "
                "well their words match your vocabulary in each category.\n"
                "Respond in JSON format: 'thought' (reasoning), 'adopted_vocab' (a JSON object "
                "mapping categories like 'food', 'danger' to a list of ALL words you now know for "
                "them, including new ones adopted), 'trade_food' (boolean), and "
                "'understanding_score' (float 0.0 to 1.0)."
            )

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creature simulation engine. Output perfectly formatted JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=150,
                temperature=0.7,
            )

            ans_data = json.loads(response.choices[0].message.content.strip())
            new_vocab = ans_data.get("adopted_vocab", agent_vocabulary)
            thought = ans_data.get("thought", "I decided instinctively.")
            trade = bool(ans_data.get("trade_food", False)) and food_count > 0
            score = float(ans_data.get("understanding_score", 0.5))

            last_mode_used = "real testing"

            safe_vocab = {"food": [], "trade": [], "danger": [], "greeting": []}
            if isinstance(new_vocab, dict):
                for k in safe_vocab.keys():
                    if k in new_vocab and isinstance(new_vocab[k], list):
                        safe_vocab[k] = [
                            str(w).lower() for w in new_vocab[k] if isinstance(w, str)
                        ]
                    elif k in agent_vocabulary:
                        safe_vocab[k] = list(agent_vocabulary[k])
            else:
                safe_vocab = agent_vocabulary

            return safe_vocab, thought, trade, max(0.0, min(1.0, score))
        except Exception as e:
            print(f"OpenAI error: {e}")
            last_mode_used = "mockup testing"
            return mock_llm_language_adoption(agent_vocabulary, heard_sentence, food_count)

    last_mode_used = "mockup testing"
    return mock_llm_language_adoption(agent_vocabulary, heard_sentence, food_count)


def generate_initial_language():
    """Generate simple random letter sounds to start."""
    consonants = "bcdfghjklmnpqrstvwxyz"
    vowels = "aeiou"

    vocab = {}
    for concept in ["food", "trade", "danger", "greeting"]:
        sounds = []
        for _ in range(random.randint(2, 3)):
            sound = random.choice(consonants) + random.choice(vowels)
            if random.random() > 0.5:
                sound += random.choice(consonants)
            sounds.append(sound)
        vocab[concept] = sounds
    return vocab
