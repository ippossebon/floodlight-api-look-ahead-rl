import numpy

def actionMap(action):
    ## H1 -> H2
    if action == 0:
        return numpy.array([0, 0, 1])
    elif action == 1:
        # S1, in 1, out 3
        return numpy.array([0, 0, 2])
    elif action == 2:
        # S2, in 1, out 2
        return numpy.array([1, 0, 1])
    elif action == 3:
        # S2, in 1, out 3
        return numpy.array([1, 0, 2])
    elif action == 4:
        # S2, in 1, out 4
        return numpy.array([1, 0, 3])
    elif action == 5:
        # S2, in 2, out 3
        return numpy.array([1, 1, 2])
    elif action == 6:
        # S2, in 2, out 4
        return numpy.array([1, 1, 3])
    elif action == 7:
        # S3, in 2, out 1
        return numpy.array([2, 1, 0])
    elif action == 8:
        # S3, in 3, out 1
        return numpy.array([2, 2, 0])
    elif action == 9:
        # S3, in 4, out 1
        return numpy.array([2, 3, 0])
    elif action == 10:
        # S4, in 1, out 3
        return numpy.array([3, 0, 2])
    elif action == 11:
        # S4, in 1, out 2
        return numpy.array([3, 0, 1])
    elif action == 12:
        # S4, in 2, out 3
        return numpy.array([3, 1, 2])
    elif action == 13:
        # S5, in 1, out 2
        return numpy.array([4, 0, 1])

    ## H2 -> H1
    elif action == 14:
        # S3, in 1, out 2
        return numpy.array([2, 0, 1])
    elif action == 15:
        # S3, in 1, out 3
        return numpy.array([2, 0, 2])
    elif action == 16:
        # S3, in 1, out 4
        return numpy.array([2, 0, 3])
    elif action == 17:
        # S2, in 4, out 1
        return numpy.array([1, 3, 0])
    elif action == 18:
        # S2, in 4, out 2
        return numpy.array([1, 3, 1])
    elif action == 19:
        # S2, in 3, out 1
        return numpy.array([1, 2, 0])
    elif action == 20:
        # S2, in 3, out 2
        return numpy.array([1, 2, 1])
    elif action == 21:
        # S2, in 2, out 1
        return numpy.array([1, 1, 0])
    elif action == 22:
        # S4, in 3, out 1
        return numpy.array([3, 2, 0])
    elif action == 23:
        # S4, in 3, out 2
        return numpy.array([3, 2, 1])
    elif action == 24:
        # S4, in 2, out 1
        return numpy.array([3, 1, 0])
    elif action == 25:
        # S5, in 2, out 1
        return numpy.array([4, 1, 0])
    elif action == 26:
        # S1, in 2, out 1
        return numpy.array([0, 1, 0])
    elif action == 27:
        # S1, in 3, out 1
        return numpy.array([0, 2, 0])

    ## S10 topology
    elif action == 28:
        # S1
        return numpy.array([0, -1, -1])
    elif action == 29:
        # S2
        return numpy.array([1, -1, -1])
    elif action == 30:
        # S3
        return numpy.array([2, -1, -1])
    elif action == 31:
        # S4
        return numpy.array([3, -1, -1])
    elif action == 32:
        # S5
        return numpy.array([4, -1, -1])
    elif action == 33:
        # S1
        return numpy.array([0, -1, -1])
    elif action == 34:
        # S2
        return numpy.array([1, -1, -1])
    elif action == 35:
        # S3
        return numpy.array([2, -1, -1])
    elif action == 36:
        # S4
        return numpy.array([3, -1, -1])
    elif action == 37:
        # S5
        return numpy.array([4, -1, -1])
    elif action == 38:
        # S1
        return numpy.array([0, -1, -1])
    elif action == 39:
        # S2
        return numpy.array([1, -1, -1])
    elif action == 40:
        # S3
        return numpy.array([2, -1, -1])
    elif action == 41:
        # S4
        return numpy.array([3, -1, -1])
    elif action == 42:
        # S5
        return numpy.array([4, -1, -1])
    elif action == 43:
        # S1
        return numpy.array([0, -1, -1])
    elif action == 44:
        # S2
        return numpy.array([1, -1, -1])
    elif action == 45:
        # S3
        return numpy.array([2, -1, -1])
    elif action == 46:
        # S4
        return numpy.array([3, -1, -1])
    elif action == 47:
        # S5
        return numpy.array([4, -1, -1])
    elif action == 48:
        # S3
        return numpy.array([2, -1, -1])
    elif action == 49:
        # S4
        return numpy.array([3, -1, -1])
