#!/usr/bin/env python3
# Code to analyse the best offensive matchups in pokemon

import csv
import json
from collections import defaultdict
from functools import reduce
import subprocess
import sys

# How different effectivenesses map to scores
VALUE_MAP = {
    0: -3,
    0.25: -2,
    0.5: -1,
    1: 0,
    2: 1,
    4: 2,
}

# Load type matchups
with open("types.csv") as fp:
    r = csv.reader(fp)
    order = next(r)[1:]
    lookup = dict(map(lambda x: (x[1], x[0]), enumerate(order)))
    # print(lookup)
    matchups = []
    for defensive_type in r:
        matchups.append(tuple(map(float, defensive_type[1:])))
    # print(matchups)
n_types = len(order)


# Load what types pokemon have
pokemon_data = {}
with open("pokemon.json") as fp:
    data = json.load(fp)
    for pokemon in data.values():
        name = pokemon["name"]
        types = tuple(map(lambda x: lookup[x], pokemon["types"]))
        pokemon_data[name] = types


# Load in the usage statistics for a given format
# Instead of associating usage with pokemon, associate it with types
# Hence, usage for hatterene and scream tail would be combined as they have the same type, and I only care about the frequencies of type combos
try:
    format = sys.argv[1]
    usage_dict = defaultdict(float)
    # There is no reason to use subprocess.run, but i wrote this part in shell and wasn't bothered to write it again
    usage = subprocess.run(["./gen_short.sh", format], text=True, capture_output=True)
    for line in usage.stdout.splitlines():
        pokemon, usage = line.strip().rstrip("%").rsplit("|", maxsplit=1)
        pokemon = pokemon.strip()
        usage = float(usage.strip())
        types = pokemon_data[pokemon]
        # print(*map(lambda x: order[x], types))
        # print(*zip(order, supereffectiveness))
        usage_dict[types] += usage
except Exception as e:
    sys.stderr.write(f"usage: {sys.argv[0]} <smogon usage file>\n")
    raise e



# Save on computation later by pre-calculating efffectiveness of various types of moves when attacking a given type combo
usage_se = []
for types, usage in usage_dict.items():
    # Sorry
    supereffectiveness = tuple(map(lambda x: reduce(lambda a, b: a * b, map(lambda z: matchups[x][z], types)), range(n_types)))
    usage_se.append((usage, supereffectiveness))



# Actually calculate scores
values = []
for t1 in range(n_types):
    for t2 in range(t1 + 1, n_types):
        # If you wanted to check for mons with three types, add an extra nested loop here
        score = 0
        for usage, se in usage_se:
            best_effectiveness = max(se[t1], se[t2])
            base_value = VALUE_MAP[best_effectiveness]
            weighted_val = base_value * usage
            # usage stats are percentage and you have 6 mons on a team, so i divide by 600 to counteract this. 
            # It might be technically better to do this later to save on computation and floating point errors but i don't care
            score += weighted_val / 600
        values.append((score, (order[t1], order[t2])))

print("| Rank | Offensive Type | Score |")
print("|------|----------------|-------|")
for i, (perc, (type1, type2)) in enumerate(sorted(values)[::-1]):
    print(f"|{i+1}| {type1}/{type2}| {perc}|")
        
# This ought to add up to something around 600
# print(sum(map(lambda x: x[0], usage_se)))