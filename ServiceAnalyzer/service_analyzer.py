from enum import Enum
from rapid_miner_service import RapidMinerService
from orange3_service import Orange3Service


class Functionality(Enum):
    outliers = 1
    linear_regression = 2
    prediction = 3
    k_means_clustering = 4


class ComparisonCriteria(Enum):
    results = 1


class EvaluationCriteria(Enum):
    execution_time = 1


class ServiceAnalyzer:
    def __init__(self):
        pass

    def process(self, configuration):
        # configuration = {'path': self.edit_data_path.text(),
        #                  'functionality': 0,
        #                  'rapidminer': self.cBx_rp_service_run.isChecked(),
        #                  'orange': self.cBx_orange_service_run.isChecked(),
        #                  'comparison': [],
        #                  'evaluation_criteria': [],
        #                  'target': ''
        #                  }
        services = dict({})
        results = dict({})
        if configuration['orange']:
            services['orange'] = Orange3Service(configuration['path'])
        if configuration['rapidminer']:
            services['rapidminer'] = RapidMinerService(configuration['path'])

        if configuration['functionality'] == Functionality.outliers:
            for service_name in services:
                results[service_name] = services[service_name].get_outliers()
        elif configuration['functionality'] == Functionality.linear_regression:
            for service_name in services:
                results[service_name] = services[service_name].get_linear_regression_weights(configuration['target'])
        elif configuration['functionality'] == Functionality.prediction:
            for service_name in services:
                results[service_name] = services[service_name].get_prediction(configuration['data_to_predict'],
                                                                              configuration['target'])
        elif configuration['functionality'] == Functionality.k_means_clustering:
            for service_name in services:
                print(service_name)
                results[service_name] = services[service_name].get_clusters()
                print(results[service_name])

        return results
