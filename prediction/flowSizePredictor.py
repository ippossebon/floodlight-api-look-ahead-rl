import csv

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold

class FlowSizePredictor(object):
    def __init__(self):
        self.evaluation_set = []
        self.training_set = []

    def trainModel(self):
        # Split dataset into a training set and a test set
        train_dataset = self.training_set.sample(frac=0.8,random_state=0)
        test_dataset = self.training_set.drop(train_dataset.index)
        features = list(self.training_set.columns.values)

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
