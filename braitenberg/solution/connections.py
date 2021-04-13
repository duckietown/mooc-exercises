from typing import Tuple

import numpy as np


# First try: FEAR
def get_motor_left_matrix(shape: Tuple[int, int]) -> np.ndarray:
    res = np.zeros(shape=shape, dtype="float32")
    # MH: creates a mask with 1s in left side of image and 0s in right side
    mid_width = int(np.floor(shape[1]/2))
    thrd_height = int(np.floor(shape[0]/2)) #note this is half!

    res[thrd_height:, :mid_width] = 1
    return res


def get_motor_right_matrix(shape: Tuple[int, int]) -> np.ndarray:
    res = np.zeros(shape=shape, dtype="float32")  # write your function instead of this one
    # MH: creates a mask with 0s in left side of image and 1s in right side
    mid_width = int(np.floor(shape[1]/2))
    thrd_height = int(np.floor(shape[0]/2)) #note this is half!dts challen

    res[thrd_height:, mid_width:] = 1
    return res

"""
#Second try: EXPLORER (requires negative GAIN)

def get_motor_left_matrix(shape: Tuple[int, int]) -> np.ndarray:
    res = np.zeros(shape=shape, dtype="float32")
    # MH: creates a mask with 1s in the 2/3 lower 1/2 right side corner of the image and 0s elsewhere
    mid_width = int(np.floor(shape[1]/2))
    thrd_height = int(np.floor(shape[0]/3))

    res[thrd_height:, mid_width:] = 1
    return res


def get_motor_right_matrix(shape: Tuple[int, int]) -> np.ndarray:
    res = np.zeros(shape=shape, dtype="float32")  # write your function instead of this one
    # MH: creates a mask with 1s in the 2/3 lower 1/2 left side corner of the image and 0s elsewhere
    mid_width = int(np.floor(shape[1]/2))
    thrd_height = int(np.floor(shape[0]/3))

    res[thrd_height:, :mid_width] = 1
    return res
"""
