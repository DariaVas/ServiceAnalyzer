import os
from enum import Enum
import config
from rapid_miner_service import RapidMinerService
from orange3_service import Orange3Service
from utils import read_cvs_file, generate_test_cvs_file
from service_comparator import ServiceComparator

class Functionality(Enum):
    outliers = 1
    linear_regression = 2
    prediction = 3
    k_means_clustering = 4


class ComparisonCriteria(Enum):
    results = 1


class EvaluationCriteria(Enum):
    execution_time = 1
    time_dependence_from_data = 2


def simple_wrapper(func, **kwargs):
    def wrapper():
        return func(**kwargs)

    return wrapper


class ServiceAnalyzer:
    def __init__(self):
        self.service_settings = config.get_config()
        self.config = {}
        self.service_comparator = ServiceComparator()

    '''
    :output [(rows, time), ]
    '''

    def _find_time_dependence(self, service, func, **kwargs):
        data_path = self.config['path']
        rows_increment = self.config['rows_increment_index']
        num_experiments = self.config['num_experiments']
        headers, content, num_of_initial_rows = read_cvs_file(data_path)

        generated_path_template = '%s.{}.csv' % str(self.service_settings['Service']['dir_for_generated_files'] +
                                                    os.path.sep +
                                                    os.path.splitext(os.path.basename(data_path))[0])
        result = []
        for i in range(num_experiments):
            rows = i * rows_increment + num_of_initial_rows - 1
            file_path = generated_path_template.format(rows)
            if not os.path.exists(file_path):
                generate_test_cvs_file(file_path, content, headers, rows)
                print(file_path)

            service.set_data_path(file_path)
            _, time = service.measure_time_execution(func, **kwargs)
            result.append((rows, time))
        # print(result)
        return result

    def _run_service_functionality(self, service, service_func, **kwargs):
        results = {}
        for c in self.config['evaluation_criteria']:
            if c == EvaluationCriteria.execution_time:
                results["result"], results["execution_time"] = service.measure_time_execution(service_func, **kwargs)
            if c == EvaluationCriteria.time_dependence_from_data:
                results["time_dependence"] = self._find_time_dependence(service, service_func, **kwargs)
                service.set_data_path(self.config['path'])
        if not results.get('result'):
            results["result"] = service_func(**kwargs)

        return results

    def _get_service_results(self, service):
        functionality = self.config['functionality']
        if functionality == Functionality.outliers:
            results = self._run_service_functionality(service, service.get_outliers)
        elif functionality == Functionality.linear_regression:
            results = self._run_service_functionality(service, service.get_linear_regression_weights,
                                                      target_name=self.config['target'])
        elif functionality == Functionality.prediction:
            results = self._run_service_functionality(service,
                                                      service.get_prediction,
                                                      data_to_predict_path=self.config['data_to_predict'],
                                                      target_name=self.config['target'])
        elif functionality == Functionality.k_means_clustering:
            results = self._run_service_functionality(service, service.get_clusters)
        else:
            raise RuntimeError('Unknown functionality')
        return results

    def _compare_services(self, results):
        if not self.config['comparison']:
            return results
        # for comparison_criteria in self.config['comparison']:
        #     if comparison_criteria == ComparisonCriteria.results:
        #         results = self.service_comparator.c

    def process(self, configuration):
        # configuration = {'path': self.edit_data_path.text(),
        #                  'functionality': 0,
        #                  'rapidminer': self.cBx_rp_service_run.isChecked(),
        #                  'orange': self.cBx_orange_service_run.isChecked(),
        #                  'comparison': [],
        #                  'evaluation_criteria': [],
        #                  'target': ''
        #                  'data_to_predict': '',
        #                  'rows_increment_index': '',
        #                  'num_experiments': '',
        #                  }
        self.config = configuration
        results = dict({})
        if configuration['orange']:
            orange = Orange3Service(configuration['path'])
            results['orange'] = self._get_service_results(orange)
        if configuration['rapidminer']:
            rp_miner = RapidMinerService(configuration['path'])
            results['rapidminer'] = self._get_service_results(rp_miner)

        results = self._compare_services(results)

        return results
