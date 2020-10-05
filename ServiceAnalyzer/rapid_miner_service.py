import os
import os.path
import rapidminer
import pandas
import config
from data_mining_service import DataMiningService

PROCESSES = {
    'outliers': '//Local Repository/detect_outliers',
    'prediction': '//Local Repository/prediction',
    'linear_regression': '//Local Repository/linear_regression',
    'k_means_clusters': '//Local Repository/k_means_clustering_with_normalization'
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
        df = pandas.read_csv(data_path)
        self._data_path = TEST_DIR_PATH + os.path.basename(data_path)
        self._connector.write_resource(df, self._data_path)

    def get_outliers(self):
        df = self._connector.read_resource(self._data_path)
        outliers = self._connector.run_process(PROCESSES['outliers'], inputs=[df])
        print(outliers)
        return {"result": outliers['outlier'].to_numpy().tolist()}

    def get_prediction(self, data_to_predict_path, target_name):
        df_to_predict = pandas.read_csv(data_to_predict_path)
        df = self._connector.read_resource(self._data_path)
        prediction = self._connector.run_process(PROCESSES['prediction'], inputs=[df, df_to_predict],
                                                 macros={'target': target_name})
        return {"result": prediction['prediction(%s)' % target_name].values.tolist()}

    def get_linear_regression_weights(self, target_name):
        df = self._connector.read_resource(self._data_path)
        weights = self._connector.run_process(PROCESSES['linear_regression'], inputs=[df],
                                              macros={'target': target_name})
        return {"result": weights.values.tolist()}

    def get_clusters(self):
        df = self._connector.read_resource(self._data_path)
        clusters = self._connector.run_process(PROCESSES['k_means_clusters'], inputs=[df])
        return {"result": clusters['cluster'].values.tolist()}

    def _get_logged_time(self):
        if not os.path.exists(TIME_EXECUTION_PATH):
            raise RuntimeError('Cannot get execution time, because %s is absent', TIME_EXECUTION_PATH)
        with open(TIME_EXECUTION_PATH) as f:
            for l in f.readlines():
                print(l)
                if l.startswith('#'):
                    continue
                nums = [float(n.strip()) for n in l.split('\t')]
                return sum(nums)

    def measure_time_execution(self, func, **kwargs):
        def measure():
            print('Rapid miner service. Running function ', func.__name__)
            import time
            ms_koef = 1000
            ts = time.time()
            res = func(**kwargs)
            te = time.time()
            diff1 = (te - ts) * ms_koef
            diff = self._get_logged_time()
            print('Rapid miner service. {} execution time: {}, manual time {}'.format(func.__name__, diff, diff1))
            if not res.get("criteria"):
                res["criteria"] = {}
            res["criteria"]["execution_time"] = diff
            return res
        return measure

    def run_empty_process(self):
        self._connector.run_process('//Local Repository/empty_process')
