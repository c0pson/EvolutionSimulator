from enum import IntEnum, Enum

class SIZE(IntEnum):
    # WINDOW
    WIDTH = 1080
    HEIGHT = 720
    # GENETIC ALGORITHM
    POPULATION = 30

class ENERGY(float, Enum):
    IDLE_COST = 0.002
    MOVE_COST_BASE = 0.005
    SIZE_COST_EXP = 1.5
    HUNT_COST_MULT = 1.8
    FLEE_COST_MULT = 1.6
    FOOD_ENERGY = 3.0
    KILL_ENERGY = 5.0
    STAMINA_TO_ENERGY = 1.0

FPS = 60
