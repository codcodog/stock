import numpy as np


def average(data):
    '''求取平均数'''
    if len(data) == 0:
        return 0

    data.sort()
    if len(data) > 2:
        filter_data = data[1:-1]
    else:
        filter_data = data
    return np.mean(filter_data)


def median(data):
    '''求取中数'''
    if len(data) == 0:
        return 0
    return np.median(data)
