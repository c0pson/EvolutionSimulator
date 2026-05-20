<center>

# BIAI Report

<br><br><br><br><br><br><br><br>

#### Topic: Evolution Simulator Using Genetic Algorithm
**06/05/2026**

</center>

<br><br><br><br><br><br><br><br><br><br><br><br>

<div style="text-align: right;">

**Group Members:**

Piotr Copek
Zuzanna Micorek

</div>

<div style="page-break-after: always;"></div>

## 1. Selection of Topic

Our group selected the topic of designing an Evolution Simulator based on a Genetic Algorithm. The simulator models predator-prey dynamics where two species evolve their behavior across generations. The motivation behind this choice is to explore how simple genetic rules can produce complex, emergent strategies without any hardcoded intelligence. The topic falls under computational intelligence and bio inspired optimization.

## 2. Work Plan

**Phase 1 (Completed):** Core simulation framework - built the Pygame environment, defined species classes, implemented movement, collision detection, and a basic food system.
**Phase 2 (Completed):** Genetic algorithm implementation - designed the Genes dataclass with eight evolvable traits (size, speed, stamina, fov, turn_rate, aggression, caution, perception), implemented per-gene crossover, Gaussian mutation, tournament selection, elitism, and fitness-based ranking.
**Phase 3 (In Progress):** Behavioral AI - integrated gene-driven decision-making for both species (target lock-on with intercept prediction for hunters; flee/forage/school priority stack for prey). Tuning fitness functions and balancing energy costs.
**Phase 4 (Upcoming):** Evaluation and analysis - run multi-generation experiments, collect statistics, visualize evolutionary trends, and document findings.

## 3. Basic Working of the Algorithm

The genetic algorithm operates on a population of individuals, each carrying a set of genes that determine their physical and behavioral traits. Each generation runs for a fixed time window during which hunters attempt to catch prey and prey try to survive and forage for food.

The cycle proceeds as follows:

 1. **Fitness Evaluation:** At the end of each generation, every individual receives a fitness score. Hunters are evaluated on kills, damage dealt, and energy efficiency. Prey are evaluated on survival time, food gathered, and energy conservation. The fitness function uses multiplicative components so that zero performance in any critical area collapses overall fitness.
 
 2. **Selection:** Individuals are ranked by fitness. The top performers are selected using tournament selection. The top ~10% are preserved through elitism to carry strong traits forward.
 
 3. **Crossover:** Selected parents are paired and produce offspring. For each gene, the child randomly inherits the value from one parent (per-gene selection rather than averaging, which preserves diversity).
 
 4. **Mutation:** Small Gaussian perturbations are applied to offspring genes, introducing variation. Additionally, ~5% of each new generation consists of randomly generated individuals to inject fresh genetic material.
 
 5. **Replacement:** The new population replaces the old one, the environment resets with fresh food, and the next generation begins.

Over successive generations, this process drives both species to adapt: hunters evolve better pursuit strategies while prey develop improved evasion and foraging behaviors, demonstrating the core principle of natural selection through computational simulation.
