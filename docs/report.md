<center>

<div style="text-align: right">
Gliwice, 23.04.2026
</div>

<br><br><br><br><br><br>

# Report

## Biologically Inspired Artificial Intelligence

### Wild Life Simulator

<br><br><br><br><br><br><br><br><br><br><br><br>

<div style="text-align: right">
<u>Group members:</u><br>
Zuzanna Micorek<br>
Piotr Copek
</div>

</center>

<div style="page-break-after: always;"></div>

#### Introduction

#### Task analysis

#### Task analysis

 - **Possible approaches**
 - **Selected methodology**
 Creating initial population in separate locations. Both species main goal is to survive. There are two of them: `hunters` and `preys`. Hunters live depends on eating the prey, where prey live depends mostly on avoiding hunters and eating plants. 
 To make the chances equal for both `hunters` and `preys` equal, we introduces such animal stats:
    ```batch
    size
    speed
    stamina
    hunger
    ```
 To make it impossible to max out all the stats, there will be general score limit that will determine if some stats can be upgraded, or at what cost, e.g.: `Individual A` has big size which will make impossible at some point, to increase speed. Upgrading stamina will make `Individual A` hungry way faster. Also based on type of individual, they will try to create special "ability" for self defense in case of `prey` or hunting mechanism in case of `hunter`.
 - **Tech stack**
     - Python
     - Pygame
 - **Approach**
     - **OOP** - Blueprints for both `prey` and `hunter` implementation. Each object (individual) will be trying to survive as long as possible. After killing the least adapted individuals, we will be creating new ones with mixed genes of the strongest ones.
     - **Data classes**
     - **toml** - configuration file with initial specifications e.g.: initial population sizes, parameters, optionally initial population/save file.

#### Software architecture

 - **Classes**
```python
class Specie:
    def __init__(self,
        size: int,
        speed: float,
        stamina: int,
        hunger: float,
        generation: int
    ):
        self.stats = Stats(size, speed, stamina, hunger)
        self.population_segment = PopulationSegment(
            birth=generation,
            age=0
        )

class Hunter(Specie):
    def __init__(self,
        size: int,
        speed: float,
        stamina: int,
        hunger: float,
        generation: int
    ):
        super().__init__(size, speed, stamina, hunger, generation)

class Prey(Specie):
    def __init__(self,
        size: int,
        speed: float,
        stamina: int,
        hunger: float,
        generation: int
    ):
        super().__init__(size, speed, stamina, hunger, generation)
```
 - **Data structures**
```python
@dataclass
class Stats:
    size: int
    speed: float
    stamina: int
    hunger: float

@dataclass
class PopulationSegment:
    birth: int
    age: int
```
 - **GUI**
 Minimalistic Graphical Interface will be created using `pygame`. The `hunters` and `preys` will be indicated by colored shapes on the screen. Plants will be a green circles. Basic statistics like the individuals count, generation timer etc.

#### Experiments
<!-- TODO: We have to do some graphs -->

#### Summary

#### References

 - [Game of Life Wikipedia page](https://en.wikipedia.org/wiki/Conway's_Game_of_Life)

#### Repository
