# import csv
# import pandas as pd
# import numpy as np
#
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
#
# from sklearn.linear_model import LinearRegression
# from sklearn.model_selection import KFold
#
class FlowSizePredictor(object):
    def __init__(self):
        self.evaluation_set_features = []

        self.training_set_features = []
        self.training_set_correct_values = []

#
#
#     def setTrainingData(self):
#         training_dataset = {} # dicionario cuja chave é o ID do fluxo
#         dataset_files = [
#             '../snapshots/training/snapshot-2019-09-15 15:34:56 - total 83 giga.405508.csv',
#             '../snapshots/training/snapshot-2019-09-15 16:55:10 - total 767 giga.680717.csv',
#             '../snapshots/training/snapshot-2019-09-15 18:46:34 - total 808 giga.934714.csv'
#         ]
#
#         for flow_dataset_file_name in dataset_files:
#             # Cada arquivo corresponde a um fluxo bidirecional diferente
#             with open(flow_dataset_file_name) as csvfile:
#                 lines = csv.reader(csvfile, delimiter=',')
#
#                 for instance in lines:
#                     flow_id = instance[1]
#                     # Cada item do dicionário é o ID do fluxo com a lista de features associadas
#                     training_dataset[flow_id] = instance
#
#                     instance_correct_value = instance[3]
#                     features = list(instance)
#                     features.remove(instance[3]) # remove flow["byte_count"], que é o atributo alvo
#
#                     self.training_set_features.append(features)
#                     self.training_set_correct_values.append(instance_correct_value)
#
#
#
#     def trainModel(self):
#         self.model = LinearRegression().fit(self.training_set_features, self.training_set_correct_values)
#         score = self.model.score(self.training_set_features, self.training_set_correct_values)
#
#         print('Training dataset size = {0}'.format(len(train_dataset_correct_value)))
#         print('score', score)
#
#         for i in range(len(predictions)):
#             print('Valor real: {0} - Predição: {1}'.format(test_dataset_correct_value[i], predictions[i]))
#
#         print('mean_absolute_error = ', mean_absolute_error(test_dataset_correct_value, predictions))
#         print('mean_squared_error = ', mean_squared_error(test_dataset_correct_value, predictions))
#         print('r2_score = ', r2_score(test_dataset_correct_value, predictions))
#
#
#
#     def predictFlowSize(self, data):
#         prediction = self.model.predict(data)
#
#         return prediction
#
#
# if __name__ == '__main__':
#     predictor = FlowSizePredictor()
#     predictor.trainModel()
