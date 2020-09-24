import numpy

def actionMap(action):
    if action == 0:
        return numpy.array([0, 0, 1])
    elif action == 1:
        return numpy.array([0, 0, 2])
    elif action == 2:
        return numpy.array([1, 0, 1])
    elif action == 3:
        return numpy.array([1, 0, 2])
    elif action == 4:
        return numpy.array([1, 0, 3])
    elif action == 5:
        return numpy.array([1, 1, 2])
    elif action == 6:
        return numpy.array([1, 1, 3])
    elif action == 7:
        return numpy.array([2, 1, 0])
    elif action == 8:
        return numpy.array([2, 2, 0])
    elif action == 9:
        return numpy.array([2, 3, 0])
    elif action == 10:
        return numpy.array([3, 0, 2])
    elif action == 11:
        return numpy.array([3, 0, 1])
    elif action == 12:
        return numpy.array([3, 1, 2])
    elif action == 13:
        return numpy.array([4, 0, 1])
