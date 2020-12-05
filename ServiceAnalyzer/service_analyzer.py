import os
import glob
from enum import Enum
import config
from rapid_miner_service import RapidMinerService
from orange3_service import Orange3Service
from utils import read_cvs_file, generate_test_cvs_file, convert_string_list_to_int
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

    '''
    :output [(rows, time), ]
    '''

    def _find_time_dependence(self, service, func, **kwargs):
        data_path = service.get_data_path()
        num_experiments = self.config['num_experiments']
        headers, content, num_of_initial_rows = read_cvs_file(data_path)
        generated_path_template = '%s.{}.csv' % str(self.service_settings['Service']['dir_for_generated_files'] +
                                                    os.path.sep +
                                                    os.path.splitext(os.path.basename(data_path))[0])
        rows_increment = num_of_initial_rows - 1

        result = []
        for i in range(num_experiments):
            rows = i * rows_increment + num_of_initial_rows - 1
            file_path = generated_path_template.format(rows)
            if not os.path.exists(file_path):
                generate_test_cvs_file(file_path, content, headers, rows)

            service.set_data_path(file_path)
            _, time = service.measure_time_execution(func, **kwargs)
            result.append((rows, time))
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

    def _make_preprocess(self, service):
        data_table = None
        if self.config['remove_outliers']:
            data_table = service.remove_outliers()
        if self.config['normalization']:
            data_table = service.normalize(data_table)
        if data_table is None:
            return
        generated_path_template = '%s_pre_processed_{}.csv' % str(
            self.service_settings['Service']['dir_for_generated_files'] +
            os.path.sep +
            os.path.splitext(os.path.basename(self.config['path']))[0])
        generated_path = generated_path_template.format(__class__.__name__)
        service.save_data_to_file(data_table, generated_path)
        service.set_data_path(generated_path)

    def _get_service_results(self, service):
        self._make_preprocess(service)
        functionality = self.config['functionality']
        if functionality == Functionality.outliers:
            results = self._run_service_functionality(service, service.get_outliers)
            if self.config['file_with_outliers']:
                _, outliers_score, _ = read_cvs_file(self.config['file_with_outliers'])
                outliers_score = convert_string_list_to_int(outliers_score)
                results['auc_roc_score'] = service.get_roc_auc_score(outliers_score, results['result'])
        elif functionality == Functionality.linear_regression:
            results = self._run_service_functionality(service, service.get_linear_regression_weights,
                                                      target_name=self.config['target'])
        elif functionality == Functionality.prediction:
            results = self._run_service_functionality(service,
                                                      service.get_prediction,
                                                      data_to_predict_path=self.config['data_to_predict'],
                                                      target_name=self.config['target'])
        elif functionality == Functionality.k_means_clustering:
            results = self._run_service_functionality(service, service.get_clusters,
                                                      num_clusters=self.config['clusters'])
        else:
            raise RuntimeError('Unknown functionality')
        return results

    def _get_service_comparison_results(self, results):
        service_comparator = ServiceComparator(self.config['path'])
        functionality = self.config['functionality']
        compare_results = ''
        if functionality == Functionality.outliers:
            compare_results = service_comparator.compare_outliers(r_outliers=results['rapidminer']['result'],
                                                                  o_outliers=results['orange']['result'])
        elif functionality == Functionality.linear_regression:
            compare_results = service_comparator.compare_linear_regression_coefs(
                r_coefs=results['rapidminer']['result'][1],
                o_coefs=results['orange']['result'][1])
        elif functionality == Functionality.prediction:
            compare_results = service_comparator.compare_predictions(r_predicts=results['rapidminer']['result'],
                                                                     o_predicts=results['orange']['result'])
        elif functionality == Functionality.k_means_clustering:
            compare_results = service_comparator.compare_clusters(r_clusters=results['rapidminer']['result'],
                                                                  o_clusters=results['orange']['result'])
        else:
            raise RuntimeError('Unknown functionality')
        return compare_results

    def _compare_services(self, results):
        if not self.config['comparison']:
            return results
        for comparison_criteria in self.config['comparison']:
            if comparison_criteria == ComparisonCriteria.results:
                results['service_comparison'] = self._get_service_comparison_results(results)
        return results

    def process(self, configuration):

        files = glob.glob('{}/*'.format(self.service_settings['Service']['dir_for_generated_files']))
        for f in files:
            os.remove(f)
        # configuration = {'path': self.edit_data_path.text(),
        #                  'functionality': 0,
        #                  'rapidminer': self.cBx_rp_service_run.isChecked(),
        #                  'orange': self.cBx_orange_service_run.isChecked(),
        #                  'comparison': [],
        #                  'evaluation_criteria': [],
        #                  'target': ''
        #                  'data_to_predict': '',
        #                  'num_experiments': '',
        #                  'clusters': '',
        #                  'normalization': False,
        #                  'remove_outliers': False,
        #                  'file_with_outliers':''
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
