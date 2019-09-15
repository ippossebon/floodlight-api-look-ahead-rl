# -*- coding: utf-8 -*-

import csv
import pandas as pd
import numpy as np

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold

class FlowSizePredictor(object):
    def __init__(self):
        self.evaluation_set = []
        self.training_set = []

    def trainModel(self):
        dataset_path = './datasets/unicauca1000.csv'

        raw_dataset = pd.read_csv(
            dataset_path,
            na_values = "?",
            comment='\t',
            sep=",",
            skipinitialspace=True
        )
        dataset = raw_dataset.copy()

        # remove colunas com valores irrelevantes: parâmetro 1 é para colunas, 0 é para linhas
        # dataset = dataset.drop('Flow.ID', 1)
        # dataset = dataset.drop('Source.IP', 1)
        # dataset = dataset.drop('Source.Port', 1) # infos qualitativas
        # dataset = dataset.drop('Destination.IP', 1) # infos qualitativas
        # dataset = dataset.drop('Destination.Port', 1) # infos qualitativas
        # dataset = dataset.drop('Protocol', 1) # infos qualitativas
        # dataset = dataset.drop('Timestamp', 1) # infos qualitativas
        # dataset = dataset.drop('Label', 1) # infos qualitativas
        # dataset = dataset.drop('L7Protocol', 1) # infos qualitativas
        # dataset = dataset.drop('ProtocolName', 1) # infos qualitativas
        #
        # dataset = dataset.drop('Flow.Duration', 1) # não vamos ter essa feature
        #
        # # drop rows that contain unknown values
        # dataset = dataset.dropna()

        dataset = dataset[['Flow.Duration', 'Total.Fwd.Packets', 'Total.Length.of.Fwd.Packets']]

        # Split dataset into a training set and a test set
        train_dataset = dataset.sample(frac=0.8,random_state=0)
        test_dataset = dataset.drop(train_dataset.index)
        features = list(dataset.columns.values)

        train_dataset_features = train_dataset.loc[:, features].values.tolist()
        train_dataset_correct_value = train_dataset.loc[:,'Total.Length.of.Fwd.Packets'].tolist()

        test_dataset_features = test_dataset.loc[:, features].values.tolist()
        test_dataset_correct_value = test_dataset.loc[:,'Total.Length.of.Fwd.Packets'].tolist()

        self.model = LinearRegression().fit(train_dataset_features, train_dataset_correct_value)
        score = self.model.score(train_dataset_features, train_dataset_correct_value)
        predictions = self.model.predict(test_dataset_features)

        print('Training dataset size = {0}'.format(len(train_dataset_correct_value)))
        print('Test dataset size = {0}'.format(len(test_dataset_correct_value)))
        print('score', score)

        for i in range(len(predictions)):
            print('Valor real: {0} - Predição: {1}'.format(test_dataset_correct_value[i], predictions[i]))

        print('mean_absolute_error = ', mean_absolute_error(test_dataset_correct_value, predictions))
        print('mean_squared_error = ', mean_squared_error(test_dataset_correct_value, predictions))
        print('r2_score = ', r2_score(test_dataset_correct_value, predictions))


    def predictFlowSize(self, data):
        prediction = self.model.predict(data)

        return prediction


# if __name__ == '__main__':
#     predictor = FlowSizePredictor()
#     predictor.trainModel()
