from .flowSizePredictor import FlowSizePredictor

if __name__ == '__main__':
    predictor = FlowSizePredictor()

    predictor.trainModel()
