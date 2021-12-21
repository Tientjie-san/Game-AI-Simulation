import math


def calc_distance(pos1, pos2):
    """returns distance between two 2D points"""
    dx = (pos1[0] - pos2[0]) ** 2
    dy = (pos1[1] - pos2[1]) ** 2
    distance = math.sqrt(dx + dy)
    return int(distance)
