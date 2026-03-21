import random


def should_explore(exploration_rate=0.2):
    return random.random() < exploration_rate


def pick_variant(results, exploration_rate=0.2):
    if not results:
        return None

    # sort best → worst
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    if should_explore(exploration_rate):
        # 🔥 explore: pick random NON-best if possible
        if len(results) > 1:
            return random.choice(results[1:])
        return results[0]

    # 🔥 exploit
    return results[0]
