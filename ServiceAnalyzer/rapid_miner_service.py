import os
import os.path
import rapidminer
import pandas
from pandas import DataFrame

import config
from data_mining_service import DataMiningService
from sklearn.preprocessing import StandardScaler

PROCESSES = {
    'outliers': '//Local Repository/detect_outliers',
    'prediction': '//Local Repository/prediction',
    'linear_regression': '//Local Repository/linear_regression',
    'k_means_clusters': '//Local Repository/k_means_clustering',
    'normalization': '//Local Repository/normalize'

}

TEST_DIR_PATH = '//Local Repository/test_data/'
PROGRAM_PATH = os.path.join(os.path.expanduser("~"), 'ServiceAnalyzer')
TIME_EXECUTION_PATH = os.path.join(PROGRAM_PATH, 'execution_time.log')


# We can read logs from file

# All function returns Pandas DataFrame
class RapidMinerService(DataMiningService):
    def __init__(self, data_path):
        rm_home = config.get_config()['RapidMiner']['home']
        self._connector = rapidminer.Studio(rm_home)
        # load dataframe from csv
        self._data_path = data_path

    def remove_outliers(self, data_frame=None):
        outliers = self.get_outliers()
        if data_frame is None:
            data_frame = pandas.read_csv(self._data_path)
        new_indices = []
        for i in range(len(outliers)):
            if outliers[i] >= 1:  # not outlier
                new_indices.append(i)
            else:
                print(i)
        data_frame = data_frame.filter(items=new_indices, axis=0)
        return data_frame

    def normalize(self, data_frame=None):
        if data_frame is None:
            data_frame = pandas.read_csv(self._data_path)
        # z- centered
        normalized_data = self._connector.run_process(PROCESSES['normalization'], inputs=[data_frame])
        return normalized_data

    def get_outliers(self):
        # df = self._connector.read_resource(self._data_path)
        df = pandas.read_csv(self._data_path)
        outliers = self._connector.run_process(PROCESSES['outliers'], inputs=[df])
        return outliers['outlier'].to_numpy().tolist()

    def get_prediction(self, data_to_predict_path, target_name):
        df_to_predict = pandas.read_csv(data_to_predict_path)
        df = pandas.read_csv(self._data_path)
        prediction = self._connector.run_process(PROCESSES['prediction'], inputs=[df, df_to_predict],
                                                 macros={'target': target_name})
        return prediction['prediction(%s)' % target_name].values.tolist()

    def get_linear_regression_weights(self, target_name):
        df = pandas.read_csv(self._data_path)
        data = self._connector.run_process(PROCESSES['linear_regression'], inputs=[df],
                                           macros={'target': target_name})
        criterias = {}
        for i in range(len(data[1])):
            criterias[data[1]['Criterion'][i]] = round(data[1]['Value'][i], 3)

        return criterias, data[0].values.tolist()

    def get_clusters(self, num_clusters):
        df = pandas.read_csv(self._data_path)
        clusters = self._connector.run_process(PROCESSES['k_means_clusters'], inputs=[df],
                                               macros={'num_clusters': num_clusters})
        return clusters['cluster'].values.tolist()

    def _get_logged_time(self):
        if not os.path.exists(TIME_EXECUTION_PATH):
            raise RuntimeError('Cannot get execution time, because %s is absent', TIME_EXECUTION_PATH)
        with open(TIME_EXECUTION_PATH) as f:
            for l in f.readlines():
                print(l)
                if l.startswith('#'):
                    continue
                nums = [float(n.strip()) if 'null' not in n else 0 for n in l.split('\t')]
                return sum(nums)

    def measure_time_execution(self, func, **kwargs):
        print('Rapid miner service. Running function ', func.__name__)
        import time
        ms_koef = 1000
        ts = time.time()
        res = func(**kwargs)
        te = time.time()
        diff1 = (te - ts) * ms_koef
        diff = self._get_logged_time()
        print('Rapid miner service. {} execution time: {}, manual time {}'.format(func.__name__, diff, diff1))
        return res, diff

    def run_empty_process(self):
        self._connector.run_process('//Local Repository/empty_process')

    def set_data_path(self, data_path):
        self._data_path = data_path

    @classmethod
    def save_data_to_file(cls, data_table, file_path):
        assert isinstance(data_table, DataFrame)
        csv_format = data_table.to_csv(index=False)
        with open(file_path, 'w') as f:
            f.write(csv_format)

    def get_data_path(self):
        return self._data_path
