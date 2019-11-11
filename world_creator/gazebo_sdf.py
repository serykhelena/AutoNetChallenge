#!/usr/bin/env python3
from lxml import etree
import copy, numpy
from enum import Enum
from json_converter import *
from data_structures import *
from objects import *

class SignOrientation(Enum):
    RIGHT_TOP = 0
    RIGHT_BOT = 1
    LEFT_TOP = 2
    LEFT_BOT = 3

# Constants
WALL_WIDTH = float(0.01)
WALL_HEGHT = float(0.5)
WALL_SPAWN_Z = float(0.25)

# Files pathes
# For correct use, you should run export GAZEBO_RESOURCE_PATH=path/to/media
SIGN_PATH = "media/stop_sign.sdf"
BOX_PATH = "box.world"
EMPTY_WORLD_PATH = "empty_world.world"

# Signs materials
class SignsImages(Enum):
    STOP = "SignsImages/Stop"
    ONLY_FORWARD = "SignsImages/OnlyForward"
    ONLY_RIGHT = "SignsImages/OnlyRight"
    ONLY_LEFT = "SignsImages/OnlyLeft"
    FORWARD_OR_RIGHT = "SignsImages/ForwardOrRight"
    FORWARD_OR_LEFT = "SignsImages/ForwardOrLeft"


class SdfCreator:
    def __init__(self, start, finish, cellsAmount, cellsSize, mapSize):
        """ 
        @brief Constructor that create empty world with defined config
        """
        self.__setConfig(start, finish, cellsAmount, cellsSize, mapSize)
        self.__create_empty_world()


    def showTree(self):
        """ 
        @brief Print on console xml tree of current world 
        """
        print(etree.tostring(self.SDF_ROOT, pretty_print=True))


    def writeWorldToFile(self, fileName):
        """ 
        @brief Write current world to file
        """
        f = open(fileName, 'wb')
        f.write(etree.tostring(self.SDF_ROOT, pretty_print=True))


    def addWall(self, wall):
        """ 
        @brief Spawn wall (only vertical or horizontal)
        @param wall - object from json
        @note wall must be horizontal or vertical (too lazy to work with
        rotation angles)
        """
        print("wall with pos:", wall)
        center_x = numpy.mean([wall.point1.x, wall.point2.x]) 
        center_y = numpy.mean([wall.point1.y, wall.point2.y])
        center_point = Point3D(center_x, center_y, WALL_SPAWN_Z)

        # vertical
        if wall.point1.x == wall.point2.x:
            wall_length = abs(wall.point1.y - wall.point2.y)
            wall_size = Point3D(WALL_WIDTH, wall_length, WALL_HEGHT)
        # horizontal
        elif wall.point1.y == wall.point2.y:
            wall_length = abs(wall.point1.x - wall.point2.x)
            wall_size = Point3D(wall_length, WALL_WIDTH, WALL_HEGHT)
        else:
            return
        self.__spawnBox(center_point, wall_size)


    def addBox(self, box):
        """ 
        @brief Spawn box with cell size in middle of cell
        @param box - object from json
        """
        boxSize = Point3D(self.CELLS_SIZE.x, self.CELLS_SIZE.y, WALL_HEGHT)
        pose_x = box.point.x * boxSize.x + boxSize.x / 2
        pose_y = box.point.y * boxSize.y + boxSize.y / 2
        self.__spawnBox(Point3D(pose_x, pose_y, WALL_HEGHT), boxSize)


    def addSign(self, sign):
        """ 
        @param sign - object from json
        @note we can figure out orientation from position
        """
        if sign.type == SignsTypes.STOP.value:
            signImage = SignsImages.STOP
        elif sign.type == SignsTypes.ONLY_FORWARD.value:
            signImage = SignsImages.ONLY_FORWARD
        elif sign.type == SignsTypes.ONLY_LEFT.value:
            signImage = SignsImages.ONLY_LEFT
        elif sign.type == SignsTypes.ONLY_RIGHT.value:
            signImage = SignsImages.ONLY_RIGHT
        elif sign.type == SignsTypes.FORWARD_OR_LEFT.value:
            signImage = SignsImages.FORWARD_OR_LEFT
        elif sign.type == SignsTypes.FORWARD_OR_RIGHT.value:
            signImage = SignsImages.FORWARD_OR_RIGHT
        else:
            print("Error: sign type is ", sign.type)
            return
        self.__spawnSign(sign.point, signImage)


    def __spawnBox(self, box_position, box_size):
        """ 
        @brief Spawn box with defined size in defined position
        @note You can spawn it in 2 variants:
        1. box: on center of cell in template [odd; odd], 
            for example [3; 1], [3; 3], [3; 5]
        2. wall: on center of cell in template [even; odd] or [odd; even], 
            for example [1; 0], [2; 1], [4; 3]
        @param box_position - position in high level abstraction, in other 
            words, start offset is not taken into account.
        """
        self.box_counter += 1
        box_root = etree.parse(BOX_PATH).getroot()
        box_position.x = self.START.x - box_position.x
        box_position.y = - self.START.y + box_position.y
        self.__setBoxParams(box_root, box_position, box_size)
        self.SDF_ROOT.find("world").insert(0, copy.deepcopy(box_root) )


    def __spawnSign(self, position, signImage):
        """ 
        @brief Spawn box in defined position
        @param position - Point2D - position on map (high level abstraction),
            in other words, start offset is not taken into account.
        @param signImage - object of SignsImages class
        @note You can spawn it in 4 variants (see SignOrientation)
        """
        if (position.x % self.CELLS_SIZE.x <= self.CELLS_SIZE.x/2) and \
           (position.y % self.CELLS_SIZE.y <= self.CELLS_SIZE.y/2):
            orientation = SignOrientation.LEFT_BOT
        elif (position.x % self.CELLS_SIZE.x >= self.CELLS_SIZE.x/2) and \
             (position.y % self.CELLS_SIZE.y <= self.CELLS_SIZE.y/2):
            orientation = SignOrientation.RIGHT_BOT
        elif (position.x % self.CELLS_SIZE.x <= self.CELLS_SIZE.x/2) and \
             (position.y % self.CELLS_SIZE.y >= self.CELLS_SIZE.y/2):
            orientation = SignOrientation.LEFT_TOP
        elif (position.x % self.CELLS_SIZE.x >= self.CELLS_SIZE.x/2) and \
             (position.y % self.CELLS_SIZE.y >= self.CELLS_SIZE.y/2):
            orientation = SignOrientation.RIGHT_TOP
        print("sign with pos:", position, orientation, signImage)
        self.sign_counter += 1
        sign_root = etree.parse(SIGN_PATH).getroot()
        position.x = self.START.x - position.x
        position.y = - self.START.y + position.y
        self.__setSignParams(sign_root, position, orientation, signImage)
        self.SDF_ROOT.find("world").insert(0, copy.deepcopy(sign_root) )


    def __setSignParams(self, sign_root, position, orientation, signImage):
        """ 
        @brief Set sign desired parameters
        """
        # Calculate sign position
        if orientation is SignOrientation.LEFT_BOT:
            roll = 1.57
            yaw = 1.57
            imagePos = Point2D(position.x - 0.025, position.y - 0.00)
        elif orientation is SignOrientation.RIGHT_BOT:
            roll = 0
            yaw = 1.57
            imagePos = Point2D(position.x + 0.00, position.y + 0.025)
        elif orientation is SignOrientation.LEFT_TOP:
            roll = 0
            yaw = -1.57
            imagePos = Point2D(position.x + 0.00, position.y - 0.025)
        elif orientation is SignOrientation.RIGHT_TOP:
            roll = 1.57
            yaw = -1.57
            imagePos = Point2D(position.x + 0.025, position.y - 0.00)

        # Set sign position
        signName = "unit_stop_sign_" + str(self.sign_counter)
        columnPos = "{0} {1} 0.35 0.00 0.0 0.0".format(position.x, position.y)
        signPos =   "{0} {1} 0.95 1.57 {2} {3}".format(position.x, position.y, yaw, roll)
        fondPos =   "{0} {1} 0.95 1.57 {2} {3}".format(imagePos.x, imagePos.y, yaw, roll)
        imagePos =  "{0} {1} 0.95 1.57 {2} {3}".format(imagePos.x, imagePos.y, yaw, roll)
        sign_root.set("name", signName)
        sign_root[0][1].text = columnPos
        sign_root[1][1].text = signPos
        sign_root[2][1].text = fondPos
        sign_root[3][1].text = imagePos

        # Set sign image
        sign_root[2].find("visual").find("material").find("script").find("name").text = "Gazebo/White"
        sign_root[3].find("visual").find("material").find("script").find("name").text = signImage.value


    def __setBoxParams(self, box_root, box_position, box_size):
        """ 
        @brief Set box desired parameters
        @note To avoid collision problem when objects spawn on borders of each
            other, the collision length will reduce on WALL width size
        """
        box_name = "unit_box_" + str(self.box_counter)
        box_position_text = box_position.getString()
        box_visual_size_text = box_size.getString()

        collision_size = box_size
        if collision_size.x > WALL_WIDTH:
            collision_size.x = collision_size.x - WALL_WIDTH
        if collision_size.y > WALL_WIDTH:
            collision_size.y -= WALL_WIDTH
        box_collision_size_text = collision_size.getString()

        box_root.set("name", box_name)
        box_root.find("pose").text = box_position_text
        link = box_root.find("link")
        link.find("collision").find("geometry").find("box").find("size").text = box_collision_size_text
        link.find("visual").find("geometry").find("box").find("size").text = box_visual_size_text

    @staticmethod
    def __controlRange(value, minimum, maximum, default):
        if value >= minimum and value <= maximum:
            return value
        else:
            return default


    def __setConfig(self, start, finish, cellsAmount, cellsSize, mapSize):
        """ 
        @brief Set config from inputs
        """
        MIN_MAP_SIZE = 4
        MAX_MAP_SIZE = 40
        MIN_CELL_SIZE = 0.1
        MAX_CELL_SIZE = 10

        DEFAULT_MAP_SIZE = 18
        DEFAULT_POSE = 17
        DEFAULT_CELL_SIZE = 2

        # Control cells size range
        x = SdfCreator.__controlRange(cellsSize.x, MIN_CELL_SIZE, MAX_CELL_SIZE,
                                      DEFAULT_CELL_SIZE)
        y = SdfCreator.__controlRange(cellsSize.y, MIN_CELL_SIZE, MAX_CELL_SIZE,
                                      DEFAULT_CELL_SIZE)
        self.CELLS_SIZE = Size2D(x, y)

        # Control map size range
        x = SdfCreator.__controlRange(mapSize.x, MIN_MAP_SIZE, MAX_MAP_SIZE,
                                      DEFAULT_MAP_SIZE)
        y = SdfCreator.__controlRange(mapSize.y, MIN_MAP_SIZE, MAX_MAP_SIZE, 
                                      DEFAULT_MAP_SIZE)
        self.MAP_SIZE = Size2D(x, y)

        # Control start range
        x = SdfCreator.__controlRange(start.x, 0,self.MAP_SIZE.x,DEFAULT_POSE)
        y = SdfCreator.__controlRange(start.y, 0,self.MAP_SIZE.y,DEFAULT_POSE)
        self.START = Size2D(x, y)

        print("World settings are:") 
        print("- start:", self.START)
        print("- finish: [ don't support now]")
        print("- cells amount: [ don't support now]")
        print("- cells size:", self.CELLS_SIZE)
        print("- map size:", self.MAP_SIZE)


    def __create_empty_world(self):
        """ 
        @brief Create sdf tree for empty world from file
        """
        self.SDF_ROOT = etree.parse(EMPTY_WORLD_PATH).getroot()

    # Variables:
    box_counter = 0
    sign_counter = 0

