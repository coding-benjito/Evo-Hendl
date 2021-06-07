# Evo-Hendl

> Submission to the [Minecraft Open-Endedness Challenge](https://evocraft.life/) ([GECCO 2021](https://gecco-2021.sigevo.org))

This project was done as a **spare-time project**, as I found it very interesting to think about evolution in a synthetic fashion instead of the more common analytical/statistical view point of analysis of the process. Unfortunately, I have only a very limited time available. One can see this as my first exploration of this so-called *a-life* field. I have to say, this process let many interesting thoughts and problems of this synthetic viewpoint arise, sort of reminiscent of this typical "was-there-first-the-hen-or-the-egg" sort of headache.

Here, I am providing my submission for the [Minecraft Open-Endedness Challenge](https://evocraft.life/) which is the first open-ended evolution challenge posed in the *The Genetic and Evolutionary Computation Conference* 2021 (GECCO 2021) conference competition track.

The submission deadline is ~~June 1st~~ June 7th, 2021. The winners are announced during GECCO 2021 (The Genetic and Evolutionary Computation Conference) on July 10th, 2021.

## Short algorithm description

This algorithm is based on using a single block as the unit of evolution/selection, and it includes mutational, recombinational (conversion) and reproduction. The genetics are embedded in a so called *bauplan* (a wanted neighborhood), but can be rather easily exchanged with other modes, e.g., neural nets for more environmental feedback, etc.

The algorithm includes competition, firstly because living cubes are removed given resources below a threshold in the occupied cube (energy homoeostasis), and secondly they cannot recreate offspring of a particular type if this given type is not available locally.

## What makes this algorithm special?

Differently, to what I have seen to be commonly done, I do not build single relicts which are sort of the unit of evolution, but every single block is a unit of selection and interacts with others in the neighborhood, i.e., there is also competition for resources implemented.

The code is functional.

Following work could be tracking a tree of inheritance for bauplans, etc. and playing with parameters (more air, etc. to see movements of 'artifacts').

**Also remember, that in this repo are two videos of this running algorithm** They are both part of a single evolutionary replicate (at beginning: part 1 and then part 2). You only need basic libraries, including numpy and the API provided by Evocraft-py.

**Thanks to the organizers and API-providers, etc. See the citation at the bottom**

## Getting started

### Set-up

For the necessary environment please check the [EvoCraft API](https://github.com/real-itu/Evocraft-py).
As also described there, you require (including UNIX-commands):
1. *Java 8* (aka 1.8): `sudo apt-get install openjdk-8-jre`
2. [EvoCraft API](https://github.com/real-itu/Evocraft-py): `git clone https://github.com/real-itu/Evocraft-py`
3. [grpc](https://grpc.io/): `pip install grpcio`

Rendering (*Java Edition* in UNIX):
Launch the *Minecraft Launcher*. Click *Installations*. Click *New installation*. Impute a name of your choice, **select version 1.12.2** and hit *Create*. After that, launch this version *1.12.2*, hit *Multiplayer*, *Direct Connect*, enter *localhost* as a *Server Address*, hit *Join Server*. You are now in the game as a *mob* and could freely move wiht `W`, `A`, `S`, `D`, `SPACE`, but caveat, as you interact with environment. Just hit `ESC` to pause the game, transition to the terminal (where your Minecraft server is running) to place some command (see below) and then hit *Back to Game* to see what is happening.
Commands:
1. Teleport yourself (the *mob*) via `/tp @p x y z` to position (x, y, z), e.g., try `/tp @p 1 1 1`. You will be in a corner (around you is `DIRT` and `GRASS` showing you the end of the accessible environment.
2. Introduce daylight `time set day`.
3. Remove day-night cycle `gamerule doDaylightCycle false`.
4. Go in creative mode `defaultgamemode creative`.
5. `/weather clear 1000000` for 1e6 ticks it is clear (max)

On top of that, my submission requires:
- numpy

### Start-up

1. From *Evocraft-py*, start the Minecraft server with `java -jar spongevanilla-1.12.2-7.3.0.jar`. The first time you try to start the server a text file `eula.txt` with be generated, you need to modifying its last line to `eula=true` to accept the Minecraft EULA. From that onwards, running `java -jar spongevanilla-1.12.2-7.3.0.jar` will start the server. Upon start-up of the server lines with `[... INFO]: Listening on 5001` should appear which means that the Minecraft server is ready for communication on port `5001`.
2. Run your *EvoCraft API* script which now manipulates the environment in the Minecraft server.
3. Rendering Minecraft necessitates buying the [Minecraft](https://www.minecraft.net/en-us) game.

## Purpose

The purpose of this competition is to create an algorithm which creates novel and increasingly complex *Minecraft builds* (artefacts) in an *open-ended evolution* fashion in a *Minecraft* environment using the *EvoCraft API* [Grbic et al. (2020)](https://arxiv.org/abs/2012.04751) which allows programmatic manipulation of blocks in a running *Minecraft server*. Accordingly, the *Minecraft world* is the used alife world, e.g., just like Tierra, Avida, Polyworld, Geb, Division Blocks and Evosphere, that can be assessed with Mark Bedau's *activity statistics* as a measure of *open-endedness*.

The simulation runs in *Minecraft* which is a voxel-based environment.

## KPIs

I am judging my submission by the following key performance indicators (KPIs) wich are several emergent properties:
- divergence
- diversity
- complexity
- ecological interactions
- life-like properties: autopoiesis (self-replication) and resilience/adaptation
- elegance and algorithmic minimalism: minimal 'interference'

## Code

We start with

```
>>> import grpc
>>> import minecraft_pb2_grpc
>>> from minecraft_pb2 import *
>>> channel = grpc.insecure_channel('localhost:5001')
>>> client = minecraft_pb2_grpc.MinecraftServiceStub(channel)
```

I only use three different methods provided by the [EvoCraft API](https://github.com/real-itu/Evocraft-py) that act on a client which interacts at a maximal tick rate of 20Hz with the Minecraft server:

### Filling a cube of voxels with blocks of a single block type

> `fillCube(FillCubeRequest) returns None;`

I use this method to empty a *game space*.

```
client.fillCube(FillCubeRequest(
  cube=Cube(
    min=Point(x=x_min, y=y_min, z=z_min),
    max=Point(x=x_max, y=y_max, z=z_max)),
  type=AIR))
```

> Every Minecraft voxel is identified by an integer 3-tuple (x, y, z). Here, we fill every voxel with x_min<=x<=x_max, y_min<=y<=y_max and z_min<=z<=z_max with a block of block type `AIR`.

### Spawning blocks of varying block types

> `spawnBlocks(Blocks) returns None;`

```
client.spawnBlocks(Blocks=[
 Block(position=Point(x=1, y=5, z=1), type=PISTON, NORTH),
 Block(position=Point(x=2, y=5, z=1), type=PISTON, NORTH)])
```

```
client.spawnBlocks(Blocks(blocks=[Block(position=Point(x=1, y=5, z=1), type=PISTON, orientation=NORTH)]))
```

> Every Minecraft block has a type and orientation. The chosen block is placed to occupy the voxel (x, y, z).

### Reading blocks

> `readCube(Cube) returns Blocks;`

```
blocks = client.readCube(Cube(
         min=Point(x=0, y=0, z=0),
         max=Point(x=10, y=10, z=10)
))
```

## Environment

The environment is voxel-based, i.e., composed out of discrete 1 x 1 x 1 cubes which span this discrete 3D world (limited to `Overworld`).

The environment's acessible three dimensional volume extends vertically (gravitation) from the *Void* (y=0) up to the *build limit* (y=256). In the horizontal plane (x, z) the environment extends infinitely.

At the start start-up, the plane (x, y=0, z) (*Floor*, y=0) is occupied by blocks of block type `BEDROCK` which is *indestructible* and prevents gravitation from pulling entities into the *Void*. `BEDROCK` does not alter its position, i.e., it cannot be pushed/pulled by piston types. I will keep this natural fixed *earth crust* in the simulations as a flat earth surface which linearly attracts (gravitation, constant across x, y, z).

We ignore the section (x, y<0, z), the so called *Void* (filled with `AIR`), as entities cannot permeate the *Floor*. Therefore, we will never enter it. Also I will introduce an artifical ceiling at (x, y=201, z) that cannot be permeated.

Accordingly, I limit the game field to (x, 1 <= y <= 200, y). I could put something like bedrock but translucent.

A column section
```
blocks = client.readCube(Cube(
         min=Point(x=0, y=0, z=0),
         max=Point(x=0, y=200, z=0)
))
print(blocks)
```

will reveal that for x>0 there is some (`DIRT`, `GRASS`) and potentially others in a 'natural landscape' ordering,  for all (x, z). We do not want those randomly seeded obstacles that we have no control over.

Therefore, I firstly draw another limitation:
I limit the game environment only to (1 <= x <= 10_000, 1 <= y <= 200, 1 <= z <= 10_000).
I.e., you can imagine inert, fixed and indestructible `BEDROCK` planes at x=0, x=10_001, y=0, y=201, z=0 and z=10_001.

A quick check reveals (importanty big `readCube` requests will actually kill the server):
```
import time
t_0 = time.time()
blocks = client.readCube(Cube(
         min=Point(x=1, y=1, z=1),
         max=Point(x=1, y=1, z=10_000)
))
t_1 = time.time()
print(t_1-t_0)
```

A `readCube` request on
1. 1x1x10_000=10_000 cubes takes on the order of 0.01s.
2. 10x1x10_000=**100_000** cubes takes on the order of 0.1s.
Beyond such request sizes, it gets fishy and the server gets overloaded.

#### Cleaning up the game field

We want to fill our (1 <= x <= 10_000, 1 <= y <= 200, 1 <= z <= 10_000) game field with *nothing*, which means placing `AIR` blocks in *Minecraft* terms:

```
import time
t_0 = time.time()
client.fillCube(FillCubeRequest(
  cube=Cube(
    min=Point(x=1, y=1, z=1),
    max=Point(x=100, y=200, z=100)),
  type=AIR))
t_1 = time.time()
print(t_1-t_0)
print('hi')
```

which has to be done iteratively, else the server is overloaded.
Therefore, we loop over the 10_000 segments of size 100x200x100, which each iteratively takes on the order of 0.1s, i.e., 1_000s which practically equates to 10-20min.

This ensures that there is only `AIR` around, and e.g., `GRASS`, `DIRT` is out of the way.

### Block types

Any cube the environment can only be of any of the following types:

I limit myself to 1 x 1 x 1 blocks of the following block types, this is what I call the `MINIMAL_BLOCK_TYPES`:
- `AIR`: such block is a placeholder for `nothing` and is totally permeable
- `SAND` (gravity): the only block that feels *gravitation* and will fall downwards (y) given no *support*, others will remain at a constant position (x, y, z) given no *support*
- `STONE`: just a building block with no extra attributes
- `SLIME`: this block *sticks* to von-Neumann-neighboring blocks and moves them along if shafted
- `REDSTONE_BLOCK`: is an always active *power source*, the reader shall consult sources on the topic *redstones* to understand this intricate phenomenon
- `PISTON` (oriented): A mechanical block which shafts outwards a piston given *power*, and shafts back inwards given *no power*. Therefore this block has orientation (where the shaft is located). Importantly, the `PISTON` block does not get moved upon shafting, but shafed blocks do, except they are located on the border `BEDROCK`. Activated `PISTON` cannot be moved, but deactivated can.
- `STICKY_PISTON` (oriented): Analogous, to `PISTON` but with the specification that the shaft is sticky, such that upon inward-shafting the attached object is pulled backwards in again, while the `PISTON` only pushed the object but does not retract it again. Activated `STICKY_PISTON` cannot be moved, but deactivated can.

The set `MINIMAL_BLOCK_TYPES` by now already has **7** `BLOCK_TYPE` components.
Naturally, a cube has 6 *von Neumann neighbors* and 26 *Moore neighbors*.
Using *minimalism*, I postulate that a cube
**developmentally-senses** only its *von Neumann neighborhood* of 6 cubes.

A single cube may accordingly find itself in any of 7^6 which is a big number, namely 117_649 **developmental settings**.
For each *developmental setting*, precluded that at least one neighbor is `AIR`, the central cube, if **living** asks itself
*Where and which block do I put next?*

Firstly, we need to preclude, that the cube has available the necessary cube: The energy is just keeping it alive.

1. Where?
2. Which?

Both question are answered at the same time,
namely, we need an automaton, which given the input space of 117_649 **developmental settings** outputs an offspring at any location which is of a given type and carries the same genetic information, importantly it must therefore output the position (which is empty) and the type.

Other interesting `BLOCK_TYPES` for a future expansion are `OBSERVER`, `DAYLIGHT_DETECTOR`, `REDSTONE_TORCH`, `TRIP_WIRE` and `REDSTONE_WIRE`.

## Approach

### Seeding

1. *Big Bang*: (a) The simulation environment is restricted by impermeable planes to a section of 10_000x200x10_000 cubes (b) that are filled with blocks of type `AIR`. (c) The plane (x, y=1, z) is densely filled with randomly selected **dead blocks** uniformly across all types in the `MINIMAL_BLOCK_TYPES`. This is done by fixing the random number generator seed to `EVOLUTIONARY_RUN` and then sampling a random matrix with integer elements between 1 and 7.
2. The evolutionary process is seeded with a single **living block** which has a randomly selected type out of `MINIMAL_BLOCK_TYPES` at central position (x=5_000, y=2, z=5_000). The identity is stored in the collection `LIVING_BLOCKS`, an *evolutionary run* is terminated once `LIVING_BLOCKS` is empty. The initial *bauplan* is chosen randomly. We can also drop many at once.

All blocks except `PISTON` and `STICKY_PISTON` are always oriented towards `NORTH`.

Any living block `bl` is of the `class livingBlock` which has the following attributes, namely
1. `bl.position` contains the current position (x, y, z)
2. `bl.bauplan` contains the bauplan (hereditary information) as a map across the von Neumann neighborhood (after northing according to orientation as): `down`, `north`, `east`, `south`, `west` and `up`, containing integers out of 1 to 7 corresponding to the block

`GENOMIC_ENVIRONMENT` contains 

#### Now comes of course the big question: Inheritance

Which genome does the newly added block have? The newly added block immediately inherits the bauplan from the parent applying only the **mutational operator** which alters the bauplan such that at 0 (`p1`) or 1 positions (`1-p1`) a modification occurs to another randomly chosen block which with probability 1/7 is the same. Accordingly we define a mutation probability per tick as `mu=(1-p1)6/7`, i.e., `p1=1-7/6*mu` (clearly, `mu` is bounded above by 6/7).

Given all *living blocks* at this moment there will be a `genetic environment` constructed, this genetic environment is just a list of all living blocks, but in particular, it associates every point (x, y, z) with a `bauplan` or `None`.
This serves in order to define the idea of inheritance.

Problematic is the following, `lb1` with `lb1.position` at tick `0` places `lb2` write on `top` with position `lb1.position+(1,0,0)` at tick `1` if it can. At the same time `lb1` may be moved around in a non-trivial fashion.

#### And how does competition arise?

## API examples

(x, y, z) are non-negative.

```
blocks = client.readCube(Cube(
         min=Point(x=0, y=0, z=0),
         max=Point(x=10, y=0, z=0)
))
print(blocks)
```

**Returns** (`<class 'minecraft_pb2.Blocks'>`)
```blocks {
  position {
  }
  type: BEDROCK
}
blocks {
  position {
    y: 1
  }
  type: DIRT
}
```

## Resources

D. Grbic, R. B. Palm, E. Najarro, C. Glanois, S. Risi. EvoCraft: A New Challenge for Open-Endedness. arXiv 2020 Dec. eprint 2012.04751. url https://arxiv.org/abs/2012.04751v1

[EvoCraft API](https://github.com/real-itu/Evocraft-py)

[Introduction to Open-Endedness](https://www.oreilly.com/radar/open-endedness-the-last-grand-challenge-youve-never-heard-of)

## Contact

Benjamin Wölfl
