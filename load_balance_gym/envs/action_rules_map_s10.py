import numpy

def actionMap(action):
    if action == 0:
        # S1, in 1, out 2
        return numpy.array([0, 0, 1])
    elif action == 1:
        # S1, in 1, out 3
        return numpy.array([0, 0, 2])
    elif action == 2:
        # S1, in 1, out 4
        return numpy.array([0, 0, 3])
    elif action == 3:
        # S1, in 1, out 5
        return numpy.array([0, 0, 5])
    elif action == 4:
        # S1, in 2, out 1
        return numpy.array([0, 1, 0])
    elif action == 5:
        # S1, in 3, out 1
        return numpy.array([0, 2, 0])
    elif action == 6:
        # S1, in 4, out 1
        return numpy.array([0, 3, 0])
    elif action == 7:
        # S1, in 5, out 1
        return numpy.array([0, 4, 0])

    ## S2
    elif action == 8:
        # S2, in 1, out 2
        return numpy.array([1, 0, 1])
    elif action == 9:
        # S2, in 1, out 3
        return numpy.array([1, 0, 2])
    elif action == 10:
        # S2, in 1, out 4
        return numpy.array([1, 0, 3])
    elif action == 11:
        # S2, in 1, out 5
        return numpy.array([1, 0, 4])
    elif action == 12:
        # S2, in 2, out 3
        return numpy.array([1, 1, 2])
    elif action == 13:
        # S2, in 2, out 4
        return numpy.array([1, 1, 3])
    elif action == 14:
        # S2, in 2, out 5
        return numpy.array([1, 1, 4])
    elif action == 15:
        # S2, in 5, out 2
        return numpy.array([1, 4, 1])
    elif action == 16:
        # S2, in 5, out 3
        return numpy.array([1, 4, 2])
    elif action == 17:
        # S2, in 5, out 4
        return numpy.array([1, 4, 3])
    elif action == 18:
        # S2, in 4, out 2
        return numpy.array([1, 3, 1])
    elif action == 19:
        # S2, in 4, out 1
        return numpy.array([1, 3, 0])
    elif action == 20:
        # S2, in 4, out 5
        return numpy.array([1, 3, 4])
    elif action == 21:
        # S2, in 3, out 5
        return numpy.array([1, 2, 4])
    elif action == 22:
        # S2, in 3, out 1
        return numpy.array([1, 2, 0])
    elif action == 23:
        # S2, in 3, out 2
        return numpy.array([1, 2, 1])

    ## S3
    elif action == 24:
        # S3, in 2, out 1
        return numpy.array([2, 1, 0])
    elif action == 25:
        # S3, in 3, out 1
        return numpy.array([2, 2, 0])
    elif action == 26:
        # S3, in 4, out 1
        return numpy.array([2, 3, 0])
    elif action == 27:
        # S3, in 5, out 1
        return numpy.array([2, 4, 0])
    elif action == 28:
        # S3, in 1, out 2
        return numpy.array([2, 0, 1])
    elif action == 29:
        # S3, in 1, out 3
        return numpy.array([2, 0, 2])
    elif action == 30:
        # S3, in 1, out 4
        return numpy.array([2, 0, 3])
    elif action == 31:
        # S3, in 1, out 5
        return numpy.array([2, 0, 4])

    ## S4
    elif action == 32:
        # S4, in 1, out 2
        return numpy.array([3, 0, 1])
    elif action == 33:
        # S4, in 1, out 3
        return numpy.array([3, 0, 2])
    elif action == 34:
        # S4, in 1, out 4
        return numpy.array([3, 0, 3])
    elif action == 35:
        # S4, in 3, out 1
        return numpy.array([3, 2, 0])
    elif action == 36:
        # S4, in 3, out 2
        return numpy.array([3, 2, 1])
    elif action == 37:
        # S4, in 3, out 4
        return numpy.array([3, 2, 3])
    elif action == 38:
        # S4, in 2, out 4
        return numpy.array([3, 1, 3])
    elif action == 39:
        # S4, in 2, out 1
        return numpy.array([3, 1, 0])
    elif action == 40:
        # S4, in 2, out 3
        return numpy.array([3, 1, 2])
    elif action == 41:
        # S4, in 4, out 1
        return numpy.array([3, 3, 0])
    elif action == 42:
        # S4, in 4, out 2
        return numpy.array([3, 3, 1])
    elif action == 43:
        # S4, in 4, out 3
        return numpy.array([3, 3, 2])


    ## S5
    elif action == 44:
        # S5, in 1, out 2
        return numpy.array([4, 0, 1])
    elif action == 45:
        # S5, in 1, out 3
        return numpy.array([4, 0, 2])
    elif action == 46:
        # S5, in 2, out 1
        return numpy.array([4, 1, 0])
    elif action == 47:
        # S5, in 2, out 3
        return numpy.array([4, 1, 3])
    elif action == 48:
        # S5, in 3, out 2
        return numpy.array([4, 2, 1])
    elif action == 49:
        # S5, in 3, out 1
        return numpy.array([4, 2, 0])

    ## S6
    elif action == 50:
        # S6, in 1, out 2
        return numpy.array([5, 0, 1])
    elif action == 51:
        # S6, in 1, out 3
        return numpy.array([5, 0, 2])
    elif action == 52:
        # S6, in 2, out 3
        return numpy.array([5, 1, 2])
    elif action == 53:
        # S6, in 3, out 2
        return numpy.array([5, 2, 1])
    elif action == 54:
        # S6, in 3, out 1
        return numpy.array([5, 2, 0])

    ## S7
    elif action == 55:
        # S7, in 1, out 2
        return numpy.array([6, 0, 1])
    elif action == 56:
        # S7, in 1, out 2
        return numpy.array([6, 1, 0])

    ## S8
    elif action == 57:
        # S8, in 1, out 2
        return numpy.array([7, 0, 1])
    elif action == 58:
        # S8, in 1, out 2
        return numpy.array([7, 1, 0])


    ## S9
    elif action == 59:
        # S9, in 1, out 2
        return numpy.array([8, 0, 1])
    elif action == 60:
        # S9, in 1, out 3
        return numpy.array([8, 0, 2])
    elif action == 61:
        # S9, in 2, out 3
        return numpy.array([8, 1, 2])
    elif action == 62:
        # S9, in 2, out 1
        return numpy.array([8, 1, 0])
    elif action == 63:
        # S9, in 3, out 2
        return numpy.array([8, 2, 1])
    elif action == 64:
        # S9, in 3, out 1
        return numpy.array([8, 2, 0])

    ## S10
    elif action == 65:
        # S10, in 1, out 2
        return numpy.array([9, 0, 1])
    elif action == 66:
        # S10, in 2, out 1
        return numpy.array([9, 1, 0])
