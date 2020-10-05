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
        self.config = {}

    def wrap_service_function(self, service, func, **kwargs):
        if not self.config.get('evaluation_criteria'):
            return func(**kwargs)
        criteria = self.config['evaluation_criteria']
        # If we will have more that 1 criteria, maybe we should think about decorators?
        for c in criteria:
            if c == EvaluationCriteria.execution_time:
                return service.measure_time_execution(func, **kwargs)

    def process(self, configuration):
        # configuration = {'path': self.edit_data_path.text(),
        #                  'functionality': 0,
        #                  'rapidminer': self.cBx_rp_service_run.isChecked(),
        #                  'orange': self.cBx_orange_service_run.isChecked(),
        #                  'comparison': [],
        #                  'evaluation_criteria': [],
        #                  'target': ''
        #                  }
        self.config = configuration
        services = dict({})
        results = dict({})
        if configuration['orange']:
            services['orange'] = Orange3Service(configuration['path'])
        if configuration['rapidminer']:
            services['rapidminer'] = RapidMinerService(configuration['path'])

        if configuration['functionality'] == Functionality.outliers:
            for service_name in services:
                results[service_name] = self.wrap_service_function(services[service_name],
                                                                   services[service_name].get_outliers)()
        elif configuration['functionality'] == Functionality.linear_regression:
            for service_name in services:
                results[service_name] = self.wrap_service_function(services[service_name],
                                                                   services[service_name].get_linear_regression_weights,
                                                                   target_name=configuration['target'])()
        elif configuration['functionality'] == Functionality.prediction:
            for service_name in services:
                results[service_name] = self.wrap_service_function(services[service_name],
                                                                   services[service_name].get_prediction,
                                                                   data_to_predict_path=configuration['data_to_predict'],
                                                                   target_name=configuration['target'])()
        elif configuration['functionality'] == Functionality.k_means_clustering:
            for service_name in services:
                results[service_name] = self.wrap_service_function(services[service_name],
                                                                   services[service_name].get_clusters)()

        return results
