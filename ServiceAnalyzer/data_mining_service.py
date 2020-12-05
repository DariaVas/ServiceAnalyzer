from abc import ABC, abstractmethod
from sklearn.metrics import roc_auc_score

'''
1. Outliers
2. Linear regression weights
3. Prediction 
4. K-means clustering
'''


class DataMiningService(ABC):
    '''
     :return [1,0 ..]
    '''

    @abstractmethod
    def get_outliers(self):
        pass

    '''
     :return [5,6 ..]
    '''

    @abstractmethod
    def get_prediction(self, data_to_predict_path, target_name):
        pass

    '''
    :return [[column1,w1],[column2,w2]]
    '''

    @abstractmethod
    def get_linear_regression_weights(self, target_name):
        pass

    '''
     :return [cluster_1, ..]
    '''

    @abstractmethod
    def get_clusters(self, num_clusters):
        pass

    @abstractmethod
    def measure_time_execution(self, func, **kwargs):
        pass

    def set_data_path(self, data_path):
        pass

    '''
    actual_results= [1,0..]
    scores = [0,1..] | [0.1, 0.7 ...] 
    '''

    @staticmethod
    def get_roc_auc_score(actual_results, scores):
        n_classes = set(actual_results)
        return round(roc_auc_score(actual_results, scores), 3)


