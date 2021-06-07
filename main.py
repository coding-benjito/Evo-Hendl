#!/usr/bin/env python3

import random
from minecraft_pb2 import *
import numpy as np
import utils

"""
Constants
"""
REQUIRED_TOTAL_RICHNESS = 3
RICHNESS = 10
REPRODUCTION_RATE = 0.7  # probability of reproduction per tick
RECOMBINATION_RATE = 0.2  # probability of recombination per tick
MUTATION_RATE = 0.3  # probability of mutation per tick
NUMBER_OF_GENERATIONS = 100
BLOCK_TYPES = [AIR, SAND, STONE, SLIME, REDSTONE_BLOCK, PISTON, STICKY_PISTON]
BLOCK_TYPES_TO_INDEX = {
    AIR: 0,
    SAND: 1,
    STONE: 2,
    SLIME: 3,
    REDSTONE_BLOCK: 4,
    PISTON: 5,
    STICKY_PISTON: 6
}
BLOCK_TYPES_TO_STR = {
    AIR: "AIR",
    SAND: "SAND",
    STONE: "STONE",
    SLIME: "SLIME",
    REDSTONE_BLOCK: "REDSTONE_BLOCK",
    PISTON: "PISTON",
    STICKY_PISTON: "STICKY_PISTON"
}
BLOCK_ORIENTATIONS = [NORTH, WEST, SOUTH, EAST, UP, DOWN]  # absolute orientations
BLOCK_ORIENTATIONS_RELATIVE = ["up", "down", "front", "left", "back", "right"]  # relative orientations
BAUPLAN_AXES = ["up-down", "front-back", "left-right"]  # von Neumann neighborhood axes
START_COORD = [1, 1, 1]  # start of game section
END_COORD = [100, 10, 100]  # end of game section
BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX = {
    "up": (1, 0, 1),
    "down": (1, 2, 1),
    "front": (2, 1, 1),
    "left": (1, 1, 2),
    "back": (0, 1, 1),
    "right": (1, 1, 0)
}
"""
Explanation of BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX:
array([[['', '', ''],
        ['', 'b', ''],
        ['', '', '']],
       [['', 'u', ''],
        ['r', '', 'l'],
        ['', 'd', '']],
       [['', '', ''],
        ['', 'f', ''],
        ['', '', '']]], dtype='<U1')
"""

"""
Util functions
"""


def give_manhattan_distance(tuple_1, tuple_2):
    """
    Returns integer Manhattan distance between two n-tuples.
    """
    assert len(tuple_1) == len(tuple_2)
    acc = 0
    for i, j in zip(tuple_1, tuple_2):
        acc += abs(i - j)
    return round(acc)


def give_section_dict(section):
    """
    Transforms the Minecraft section response to a more useful dict with coordinate keys.
    Leaves coords with AIR empty (no key). Unfortunately, one cannot retrieve the orientation from Minecraft.
    """
    section_dict = dict()
    for cube in section:
        if cube.type != AIR and cube.type in BLOCK_TYPES:  # else there also emerges other stuff (like LAVA)
            section_dict[(cube.position.x, cube.position.y, cube.position.z)] = cube.type
    return section_dict


def change_cube_orientation(before_rel, reference_abs):
    """
    Modification from relative to absolute orientation of a single cube.

    Axes:
        (0) the first axis is directed along west-to-east (x)
        (1) the second axis is directed along down-to-up (y)
        (2) the third axis is directed along north-to-south (z)
    """
    assert before_rel in BLOCK_ORIENTATIONS_RELATIVE  # ["up", "down", "front", "left", "back", "right"]
    assert reference_abs in BLOCK_ORIENTATIONS  # [NORTH, WEST, SOUTH, EAST, UP, DOWN]

    # UP and DOWN
    if reference_abs == UP:
        if before_rel == "up":
            return WEST
        elif before_rel == "down":
            return EAST
        elif before_rel == "front":
            return UP
        elif before_rel == "left":
            return NORTH
        elif before_rel == "back":
            return DOWN
        elif before_rel == "right":
            return SOUTH
    elif reference_abs == DOWN:
        if before_rel == "up":
            return WEST
        elif before_rel == "down":
            return EAST
        elif before_rel == "front":
            return DOWN
        elif before_rel == "left":
            return SOUTH
        elif before_rel == "back":
            return UP
        elif before_rel == "right":
            return NORTH
    # NORTH and SOUTH
    elif reference_abs == NORTH:
        if before_rel == "up":
            return UP
        elif before_rel == "down":
            return DOWN
        elif before_rel == "front":
            return NORTH
        elif before_rel == "left":
            return WEST
        elif before_rel == "back":
            return SOUTH
        elif before_rel == "right":
            return EAST
    elif reference_abs == SOUTH:
        if before_rel == "up":
            return UP
        elif before_rel == "down":
            return DOWN
        elif before_rel == "front":
            return SOUTH
        elif before_rel == "left":
            return EAST
        elif before_rel == "back":
            return NORTH
        elif before_rel == "right":
            return WEST
    # EAST and WEST
    elif reference_abs == EAST:
        if before_rel == "up":
            return UP
        elif before_rel == "down":
            return DOWN
        elif before_rel == "front":
            return EAST
        elif before_rel == "left":
            return EAST
        elif before_rel == "back":
            return WEST
        elif before_rel == "right":
            return WEST
    elif reference_abs == WEST:
        if before_rel == "up":
            return UP
        elif before_rel == "down":
            return DOWN
        elif before_rel == "front":
            return WEST
        elif before_rel == "left":
            return NORTH
        elif before_rel == "back":
            return EAST
        elif before_rel == "right":
            return SOUTH
    else:
        print("Error in single cube rotations.")


"""
Class definitions
"""


class BauplanBlock:
    """
    Single block has a type and a relative orientation in a bauplan.
    """

    def __init__(self, block_type, orientation_relative):
        self.block_type = block_type
        self.orientation_relative = orientation_relative

    def __repr__(self):
        return f"{BLOCK_TYPES_TO_STR[self.block_type]}_{self.orientation_relative}"


class Bauplan:
    """
    Every block has a surrounding (von Neumann) neighborhood (bauplan) it tries to create.
    """

    def __init__(self):
        self.arr = np.repeat(None, 27).reshape((3, 3, 3))  # any bauplan is oriented such that they you are looking
        # through the tensor (eyes are outwards of 3rd slice)
        for direction in BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX.keys():
            self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX[direction]] = BauplanBlock(
                block_type=AIR if random.random() < 0.5 else random.choice(BLOCK_TYPES),
                orientation_relative=random.choice(BLOCK_ORIENTATIONS_RELATIVE))

    def mutate(self):
        """
        Always yields a single block change: differently oriented blocks are always "different" blocks.
        Some orientation changes will be silent mutations. This only alters the bauplan.
        """
        rnd_neighbor = BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX[random.choice(BLOCK_ORIENTATIONS_RELATIVE)]
        rnd_type = self.arr[rnd_neighbor].block_type
        rnd_orientation_relative = self.arr[rnd_neighbor].orientation_relative
        while (rnd_type, rnd_orientation_relative) == (self.arr[rnd_neighbor].block_type,
                                                       self.arr[rnd_neighbor].orientation_relative):
            rnd_type = random.choice(BLOCK_TYPES)
            rnd_orientation_relative = random.choice(BLOCK_ORIENTATIONS_RELATIVE)
        self.arr[rnd_neighbor].block_type = rnd_type
        self.arr[rnd_neighbor].orientation_relative = rnd_orientation_relative

    def recombine(self):
        """
        To be more precise, this mechanism is gene conversion and not sexual recombination, within a single individual.
        """
        rnd_axis = random.choice(BAUPLAN_AXES)
        if rnd_axis == "up-down":
            temp = self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["up"]]
            self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["up"]] = \
                self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["down"]]
            self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["down"]] = temp
        elif rnd_axis == "front-back":
            temp = self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["front"]]
            self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["front"]] = \
                self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["back"]]
            self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["back"]] = temp
        else:  # rnd_axis == "left-right"
            temp = self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["left"]]
            self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["left"]] = \
                self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["right"]]
            self.arr[BLOCK_ORIENTATIONS_RELATIVE_TO_INDEX["right"]] = temp


class Entity:
    """
    An entity is smallest "physically representable" unit of evolution in this particular framework.
    It is an alive block which has a position (i.e., the coord of the occupied cube), hereditary information
    (i.e., the bauplan) and can mutate (consuming a resource), recombine (conversion) as well as mutate.
    - The position is given as a discrete point composed out of a positive integer 3-tuple, i.e., (x, y, z).
    - The bauplan is given as a collection of block types/orientations for all directions in the von Neumann
    neighborhood.
    - The resources required for reproduction is collected from the environment (not "physically represented").

    Obtaining food is not simulated within the Minecraft server, as it is rather slow, but within the Python script.
    This means, an entity position at (x, y, z) at tick t can 'harvest' f(x, y, z, t) resources, where the value is a
    vector-result across all BLOCK_TYPES. In this version, at the start all resources are present at all coords, and
    are used up over time inducing a resource competition, i.e., motivating movement, and environment-to-phenotype
    interactions, because in an environment with only PISTON the replicator can not use other resources.
    An entity can reproduce (i.e., clonally): Given the resource it just obtained, any of each bauplan fields which is
    occupied by this same block type can be randomly chosen and constructed. Therefore, as in biological evolution,
    development (bauplan execution) is equivalent to reproduction, i.e., the smallest unit is the alive block. Selection
    occurs on this smallest unit of evolution.
    """

    def __init__(self, coord: (int, int, int), block_type: int, orientation_abs: str, bauplan: Bauplan, resources,
                 block_buffer: utils.BlockBuffer):
        self.coord = coord
        self.block_type = block_type
        self.orientation_abs = orientation_abs  # absolute orientation
        self.bauplan = bauplan  # bauplan in relative orientation
        self.resources = resources
        self.bauplan_transformed = self.transform_bauplan()  # bauplan in absolute orientation (only array)
        self.block_buffer = block_buffer
        self.block_buffer.add_block(coord=coord, orientation=orientation_abs, block_type=block_type)

    def __repr__(self):
        return f"{self.coord}\n{self.bauplan}"

    def transform_bauplan(self):
        """
        self.bauplan is oriented such that we are looking into the relative orientation (front) of the central block
        self.bauplan_transformed is created by rotating self.bauplan such that the axis back-front now lies in the
        absolute orientation of the entity, entity.orientation.abs
        I verified all orientations with a rotating cube on June 5, 2021
        A significant drawback is, that we cannot get the absolute orientations of blocks from the Minecraft. Thus,
        the power of this algorithm is hampered drastically.
        :return: The transformed bauplan (a numpy array) with axes as in the game section of Minecraft:
            (0) the first axis is directed along west-to-east (x)
            (1) the second axis is directed along down-to-up (y)
            (2) the third axis is directed along north-to-south (z)
        """
        # (1, 2) West-to-east axis:
        # (1) If orientation_abs is west-to-east, nothing has to be changed.
        if self.orientation_abs == "east":
            bauplan_transformed = self.bauplan.arr
        # (2) If orientation_abs is east-to-west, the bauplan has to be flipped twice.
        elif self.orientation_abs == "west":
            bauplan_transformed = np.flip(np.flip(self.bauplan.arr, 0), 2)

        # (3, 4) Down-to-up axis:
        # (3) If orientation_abs is down-to-up, the bauplan has to be mirrored and flipped.
        elif self.orientation_abs == "up":
            bauplan_transformed = np.flip(self.bauplan.arr.swapaxes(0, 1), 1)
        # (4) If orientation_abs is up-to-down, the bauplan has to be mirrored and flipped.
        elif self.orientation_abs == "down":
            bauplan_transformed = np.flip(self.bauplan.arr.swapaxes(0, 1), 2)

        # (5, 6) North-to-south axis:
        # (5) If orientation_abs is north-to-south, the bauplan has to be mirrored and flipped.
        elif self.orientation_abs == "south":
            bauplan_transformed = np.flip(self.bauplan.arr.swapaxes(0, 2), 0)
        # (6) If orientation_abs is south-to-north, the bauplan has to be mirrored and flipped.
        else:  # self.orientation_abs == "north"
            bauplan_transformed = np.flip(self.bauplan.arr.swapaxes(0, 2), 2)

        return bauplan_transformed

    def reproduce(self):
        """
        An entity firstly decides on what to reproduce, and only succeeds if the chosen block is available.
        """
        rnd_neighbor = random.choice(BLOCK_ORIENTATIONS)  # choose random cube for the offspring
        new_coord_abs = utils.move_coordinate(self.coord, rnd_neighbor)  # gives absolute coord of cube
        # Bedrock at y=0 is impermeable
        while new_coord_abs[1] < START_COORD[1] or new_coord_abs[1] > END_COORD[1]:
            rnd_neighbor = random.choice(BLOCK_ORIENTATIONS)
            new_coord_abs = utils.move_coordinate(self.coord, rnd_neighbor)
        new_coord_rel_trans = utils.move_coordinate((1, 1, 1), rnd_neighbor)  # gives relative coord of cube
        new_orientation_abs = change_cube_orientation(
            before_rel=self.bauplan_transformed[new_coord_rel_trans].orientation_relative,
            reference_abs=self.orientation_abs)

        assert self.bauplan_transformed[new_coord_rel_trans].block_type in BLOCK_TYPES

        if self.resources.request_resource(coord=self.coord,
                                           block_type=self.bauplan_transformed[new_coord_rel_trans].block_type):
            return Entity(coord=new_coord_abs,
                          block_type=self.bauplan_transformed[new_coord_rel_trans].block_type,
                          orientation_abs=new_orientation_abs,
                          bauplan=self.bauplan,
                          resources=self.resources,
                          block_buffer=self.block_buffer)

            # As notice, there is a dual representation ("physically in Minecraft" for physics simulation and here, for
            # for remember absolute orientation and the genetics (both can have errors), i.e., because
            # (1) we cannot retrieve orientation with this API and (2) blocks do not have unique IDs.
        else:
            return None

    def mutate(self):
        self.bauplan.mutate()

    def recombine(self):
        self.bauplan.recombine()


class Population:
    """
    This is the population of entities alive.
    """

    def __init__(self, prev_population, resources, block_buffer: utils.BlockBuffer):
        self.resources = resources
        self.block_buffer = block_buffer
        if isinstance(prev_population, Population):
            self.prev_population = prev_population
            self.population = self.give_current_population()
        elif isinstance(prev_population, Entity):  # root
            self.prev_population = [prev_population]
            self.population = [prev_population]

    def give_current_population(self):
        """
        Create the current population by reproduction and associating genetics from the previous population, as well as
        mutation/recombination.
        """
        # Associate each block with a parent and pass the corresponding bauplan to the offspring
        game_section = self.block_buffer.get_cube_info(START_COORD, END_COORD)  # ca. 100ms
        section_dict = give_section_dict(game_section)

        population = list()
        for coord in section_dict.keys():
            closest_entity = self.prev_population.give_closest_entity(coord)
            if self.resources.give_resource_level(coord) > 3:
                population.append(Entity(coord=coord,
                                         block_type=section_dict[coord],
                                         orientation_abs=closest_entity.orientation_abs,
                                         bauplan=closest_entity.bauplan,
                                         resources=self.resources,
                                         block_buffer=self.block_buffer))
            else:
                block_buffer.add_block(coord=coord, orientation=NORTH, block_type=AIR)

        # Apply recombination, mutation and reproduction operators.
        offspring = list()
        for entity in population:
            """
            Reproduction event
            """
            if random.random() > REPRODUCTION_RATE:
                new_entity = entity.reproduce()
                if new_entity:
                    # Mutation event
                    if random.random() > MUTATION_RATE:
                        entity.mutate()
                    # Recombination event
                    if random.random() > RECOMBINATION_RATE:
                        entity.recombine()
                    offspring.append(new_entity)
        print(f"{len(offspring)} new entities were added.")
        population += offspring
        return population

    def give_closest_entity(self, coord):
        min_dist = 1_000_000
        min_entity = None
        for entity in self.population:
            new_dist = give_manhattan_distance(entity.coord, coord)
            if new_dist < min_dist:
                min_dist = new_dist
                min_entity = entity
        return min_entity


class Resources:
    """
    A 3D-map keeps track of the exhausting resources (block types) at each cube position.
    """

    def __init__(self, start_coord: (int, int, int), end_coord: (int, int, int), richness=5):
        self.start_coord = start_coord
        self.end_coord = end_coord
        self.richness = richness
        self.x_len = end_coord[0] - start_coord[0] + 1
        self.y_len = end_coord[1] - start_coord[1] + 1
        self.z_len = end_coord[2] - start_coord[2] + 1
        self.block_types_len = len(BLOCK_TYPES)

        # Construct the actual array
        self.arr = np.repeat(richness, self.x_len * self.y_len * self.z_len * self.block_types_len).reshape(
            (self.x_len, self.y_len, self.z_len, self.block_types_len))

    def request_resource(self, coord: (int, int, int), block_type: int):
        if self.arr[coord[0] - 1, coord[1] - 1, coord[2] - 1, BLOCK_TYPES_TO_INDEX[block_type]] > 0:
            self.arr[coord[0] - 1, coord[1] - 1, coord[2] - 1, BLOCK_TYPES_TO_INDEX[block_type]] -= 1
            return True
        else:
            return False

    def give_resource_level(self, coord: (int, int, int)):
        return sum(self.arr[coord[0] - 1, coord[1] - 1, coord[2] - 1])

    def grow(self, by=1):
        self.arr += by

    def reset(self, richness=5):
        self.arr = np.repeat(richness, self.x_len * self.y_len * self.z_len * self.block_types_len).reshape(
            (self.x_len, self.y_len, self.z_len, self.block_types_len))


"""
Main procedure
"""
if __name__ == "__main__":
    """
    Preparation of the environment
    The bottom horizontal plane (x, y=0, z) contains non-permeable BEDROCK.
    Outside the game section defined by START_COORD and END_COORD are no resources.
    """
    block_buffer = utils.BlockBuffer()
    block_buffer.fill_cube(start_coord=START_COORD, end_coord=END_COORD, block_type=AIR)
    resources = Resources(start_coord=START_COORD, end_coord=END_COORD, richness=RICHNESS)

    """
    Seeding of the simulation with the first population containing a single entity.
    The first entity is placed in the middle of lowest plane (x, y=1, z) on top of the BEDROCK.
    """
    root_coord = (int((END_COORD[0] - START_COORD[0]) / 2),
                  1,
                  int((END_COORD[2] - START_COORD[2]) / 2))
    root_bauplan = Bauplan()
    root_entity = Entity(coord=root_coord,
                         block_type=REDSTONE_BLOCK,
                         orientation_abs=NORTH,
                         bauplan=root_bauplan,
                         resources=resources,
                         block_buffer=block_buffer)
    root_population = Population(prev_population=root_entity,
                                 resources=resources,
                                 block_buffer=block_buffer)  # first generation
    block_buffer.send_to_server()

    """
    Now we simulate for NUMBER_OF_GENERATIONS generations, i.e., generation 2 until generation 1+NUMBER_OF_GENERATIONS.
    """
    population = root_population
    for generation in range(NUMBER_OF_GENERATIONS):
        print(f"Generation: {generation + 1}")
        population = Population(prev_population=population,
                                resources=resources,
                                block_buffer=block_buffer)
        block_buffer.send_to_server()
