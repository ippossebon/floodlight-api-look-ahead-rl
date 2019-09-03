import csv

from sklearn.model_selection import KFold

class FlowSizePredictor(object):
    def __init__(self):
        self.data = []
        self.training_set = []

        self.trainModel()
