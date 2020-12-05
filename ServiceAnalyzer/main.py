import sys
from PyQt5.QtWidgets import QApplication

from service_analyzer import EvaluationCriteria, Functionality, ComparisonCriteria
from user_interface import ServiceAnalyzerApp

'''
1. Outliers
2. Linear regression weights
3. Prediction 
4. K-means clustering
'''


def exp1(service_analyzer, path, num_clusters):
    # normalize only
    configuration = {'path': path,
                     'functionality': Functionality.k_means_clustering,
                     'rapidminer': True,
                     'orange': True,
                     'comparison': [ComparisonCriteria.results],
                     'evaluation_criteria': [],
                     'target': '',
                     'data_to_predict': '',
                     'num_experiments': '',
                     'clusters': num_clusters,
                     'normalization': True,
                     'remove_outliers': False,
                     'file_with_outliers': ''
                     }
    results = service_analyzer.process(configuration)

    return results

#
# def exp2(service_analyzer, path, num_clusters):
#     # normalize and remove
#     configuration = {'path': path,
#                      'functionality': Functionality.k_means_clustering,
#                      'rapidminer': True,
#                      'orange': True,
#                      'comparison': [ComparisonCriteria.results],
#                      'evaluation_criteria': [],
#                      'target': '',
#                      'data_to_predict': '',
#                      'num_experiments': '',
#                      'clusters': num_clusters,
#                      'normalization': True,
#                      'remove_outliers': True,
#                      'file_with_outliers': ''
#                      }
#     results = service_analyzer.process(configuration)
#
#     return results
#
#
# def exp3(service_analyzer, path, num_clusters):
#     # remove
#     configuration = {'path': path,
#                      'functionality': Functionality.k_means_clustering,
#                      'rapidminer': True,
#                      'orange': True,
#                      'comparison': [ComparisonCriteria.results],
#                      'evaluation_criteria': [],
#                      'target': '',
#                      'data_to_predict': '',
#                      'num_experiments': '',
#                      'clusters': num_clusters,
#                      'normalization': False,
#                      'remove_outliers': True,
#                      'file_with_outliers': ''
#                      }
#     results = service_analyzer.process(configuration)
#
#     return results


def exp4(service_analyzer, path, num_clusters):
    # nothing
    configuration = {'path': path,
                     'functionality': Functionality.k_means_clustering,
                     'rapidminer': True,
                     'orange': True,
                     'comparison': [ComparisonCriteria.results],
                     'evaluation_criteria': [],
                     'target': '',
                     'data_to_predict': '',
                     'num_experiments': '',
                     'clusters': num_clusters,
                     'normalization': False,
                     'remove_outliers': False,
                     'file_with_outliers': ''
                     }
    results = service_analyzer.process(configuration)

    return results


def get_time(service_analyzer, path, num_clusters):
    configuration = {'path': path,
                     'functionality': Functionality.k_means_clustering,
                     'rapidminer': True,
                     'orange': True,
                     'comparison': [],
                     'evaluation_criteria': [EvaluationCriteria.time_dependence_from_data],
                     'target': '',
                     'data_to_predict': '',
                     'num_experiments': 15,
                     'clusters': num_clusters,
                     'normalization': False,
                     'remove_outliers': False,
                     'file_with_outliers': ''
                     }
    results = service_analyzer.process(configuration)

    return results


def do_experiment():
    from service_analyzer import ServiceAnalyzer
    service_analyzer = ServiceAnalyzer()
    import os
    simple_data_paths = [
        #"/home/dasha/Documents/DiplomaFolder/Experiments/clusters/1/iris.data_new.csv",
        #"/home/dasha/Documents/DiplomaFolder/Experiments/clusters/2/winequality-red.csv",
        "/home/dasha/Documents/DiplomaFolder/Experiments/clusters/3/wine.csv"
    ]
    big_data_paths = [
        #"/home/dasha/Documents/DiplomaFolder/Experiments/clusters/1/iris_big.csv",
        #"/home/dasha/Documents/DiplomaFolder/Experiments/clusters/2/winequality-red_big.csv",
        "/home/dasha/Documents/DiplomaFolder/Experiments/clusters/3/wine_big.csv"

    ]
    cluster_nums = [
       # 3,
      #  6,
        3]
    # simple_data_paths = ["/home/dasha/Documents/DiplomaFolder/Experiments/LG_PRED/4/machine_new.data.csv"]
    # big_data_paths = ["/home/dasha/Documents/DiplomaFolder/Experiments/LG_PRED/1/Fish_trainee_big.csv"]
    # target = ['y']

    for i in range(len(simple_data_paths)):
        res1 = exp1(service_analyzer, simple_data_paths[i], cluster_nums[i])
        # res2 = exp2(service_analyzer, simple_data_paths[i], cluster_nums[i])
        # res3 = exp3(service_analyzer, simple_data_paths[i], cluster_nums[i])
        res4 = exp4(service_analyzer, simple_data_paths[i], cluster_nums[i])
        t = get_time(service_analyzer, simple_data_paths[i], cluster_nums[i])
        with open('/home/dasha/results/simple_data__new_time{}.txt'.format(os.path.basename(simple_data_paths[i])),
                  'w') as f:
            #f.write('\nEXPERIMENT 1\n')
            #f.write(str(res1))
            # f.write('\nEXPERIMENT 2\n')
            # f.write(str(res2))
            # f.write('\nEXPERIMENT 3\n')
            # f.write(str(res3))
           # f.write('\nEXPERIMENT 4\n')
           # f.write(str(res4))
            f.write('\nTIME 4\n')
            f.write(str(t))

    # for i in range(len(big_data_paths)):
    #     res1 = exp1(service_analyzer, big_data_paths[i], cluster_nums[i])
    #     # res2 = exp2(service_analyzer, big_data_paths[i], cluster_nums[i])
    #     # res3 = exp3(service_analyzer, big_data_paths[i], cluster_nums[i])
    #     res4 = exp4(service_analyzer, big_data_paths[i], cluster_nums[i])
    #     with open('/home/dasha/results/big_data_{}.txt'.format(os.path.basename(simple_data_paths[i])), 'w') as f:
    #         f.write('\nEXPERIMENT 1\n')
    #         f.write(str(res1))
    #         # f.write('\nEXPERIMENT 2\n')
    #         # f.write(str(res2))
    #         # f.write('\nEXPERIMENT 3\n')
    #         # f.write(str(res3))
    #         f.write('\nEXPERIMENT 4\n')
    #         f.write(str(res4))


def main():
    #do_experiment()
    app = QApplication(sys.argv)
    window = ServiceAnalyzerApp()
    window.show()
    app.exec_()
    return 0


if __name__ == '__main__':
    sys.exit(main())
