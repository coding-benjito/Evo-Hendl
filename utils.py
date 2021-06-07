#!/usr/bin/env python3

import grpc
import minecraft_pb2_grpc as mcraft_grpc
from minecraft_pb2 import *
import typing

BLOCK_TYPES = [AIR, SAND, STONE, SLIME, REDSTONE_BLOCK, PISTON, STICKY_PISTON]
BLOCK_ORIENTATIONS = [NORTH, WEST, SOUTH, EAST, UP, DOWN]  # absolute orientations

def move_coordinate(coord: (int, int, int), side_id: int, delta=1):
    """
    Returns new coordinate after a move in a given direction.
    """
    switcher = [
        lambda c: (c[0], c[1], c[2] - delta),  # go north
        lambda c: (c[0] - delta, c[1], c[2]),  # go west
        lambda c: (c[0], c[1], c[2] + delta),  # go south
        lambda c: (c[0] + delta, c[1], c[2]),  # go east
        lambda c: (c[0], c[1] + delta, c[2]),  # go up
        lambda c: (c[0], c[1] - delta, c[2]),  # go down
    ]
    return switcher[side_id](coord)


class BlockBuffer:
    """
    Blocks are buffered here and then sent to the Minecraft server.
    """
    def __init__(self):
        self._blocks = list()
        self._channel = grpc.insecure_channel('localhost:5001')
        self._client = mcraft_grpc.MinecraftServiceStub(self._channel)

    def add_block(self, coord: (int, int, int), orientation: int, block_type: int):
        assert block_type in BLOCK_TYPES, f"Unknown block type: {block_type}"
        assert orientation in BLOCK_ORIENTATIONS, f"Unknown orientation: {orientation}"

        self._blocks.append(Block(
            position=Point(x=coord[0], y=coord[1], z=coord[2]),
            type=block_type,
            orientation=orientation))

    def send_to_server(self):
        response = self._client.spawnBlocks(Blocks(blocks=self._blocks))
        self._blocks = []
        return response

    def fill_cube(self, start_coord: (int, int, int), end_coord: (int, int, int), block_type: BlockType):
        assert block_type in BLOCK_TYPES, "Unknown block type"

        min_x, max_x = (start_coord[0], end_coord[0]) if start_coord[0] < end_coord[0] else (end_coord[0],
                                                                                             start_coord[0])
        min_y, max_y = (start_coord[1], end_coord[1]) if start_coord[1] < end_coord[1] else (end_coord[1],
                                                                                             start_coord[1])
        min_z, max_z = (start_coord[2], end_coord[2]) if start_coord[2] < end_coord[2] else (end_coord[2],
                                                                                             start_coord[2])
        self._client.fillCube(FillCubeRequest(
            cube=Cube(min=Point(x=min_x, y=min_y, z=min_z),
                      max=Point(x=max_x, y=max_y, z=max_z)),
            type=block_type
        ))

    def get_cube_info(self, start_coord: (int, int, int), end_coord: (int, int, int)):
        min_x, max_x = (start_coord[0], end_coord[0]) if start_coord[0] < end_coord[0] else (end_coord[0],
                                                                                             start_coord[0])
        min_y, max_y = (start_coord[1], end_coord[1]) if start_coord[1] < end_coord[1] else (end_coord[1],
                                                                                             start_coord[1])
        min_z, max_z = (start_coord[2], end_coord[2]) if start_coord[2] < end_coord[2] else (end_coord[2],
                                                                                             start_coord[2])
        response = self._client.readCube(Cube(min=Point(x=min_x, y=min_y, z=min_z),
                                              max=Point(x=max_x, y=max_y, z=max_z)))
        return response.blocks
