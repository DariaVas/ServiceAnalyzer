import sys
from PyQt5.QtWidgets import QApplication
from user_interface import ServiceAnalyzerApp
from rapid_miner_service import RapidMinerService
from orange3_service import Orange3Service
'''
1. Outliers
2. Linear regression weights
3. Prediction 
4. K-means clustering
'''


# Let's assume that our work directory is /home/dasha/ServiceAnalyzer

def show_rm_results():
    data_path = '/home/dasha/Documents/Diploma/Wine/winequality-white-cut.csv'
    rm_home = '/home/dasha/Downloads/rapidminer-studio'
    data_prediction_path = '/home/dasha/Documents/Diploma/Wine/winequality-white_100_experimental.csv'
    r = RapidMinerService(rm_home, data_path)
    print('Outliers.. ')
    print(r.get_outliers())
    input('Print "Enter" to continue..')

    print('Linear regression weights.. ')
    print(r.get_linear_regression_weights())
    input('Print "Enter" to continue..')

    print('Prediction')
    print(r.get_prediction(data_prediction_path))
    input('Print "Enter" to continue..')

    print('K-means clustering')
    print(r.get_clusters())
    input('Print "Enter" to continue..')


def show_orange_results():
    data_path = '/home/dasha/Documents/Diploma/Wine/winequality-white-cut.csv'
    data_prediction_path = '/home/dasha/Documents/Diploma/Wine/winequality-white_100_experimental.csv'

    ors = Orange3Service(data_path)
    print('Outliers.. ')
    print(ors.get_outliers())
    input('Print "Enter" to continue..')

    print('Linear regression weights.. ')
    print(ors.get_linear_regression_weights())
    input('Print "Enter" to continue..')

    print('K-means clustering')
    print(ors.get_clusters())
    input('Print "Enter" to continue..')

    print('Prediction')
    print(ors.get_prediction(data_prediction_path))
    input('Print "Enter" to continue..')


def run():
    data_path = '/home/dasha/Documents/DiplomaFolder/Wine/winequality-white_100_experimental.csv'
    rm_home = '/home/dasha/Downloads/rapidminer-studio'
    data_prediction_path = '/home/dasha/Documents/DiplomaFolder/Wine/winequality-white_100_experimental.csv'
    r = RapidMinerService(data_path)
    ors = Orange3Service(data_path)
    # print('Outliers.. ')
    # time_or, res1 = ors.measure_time_execution(ors.get_outliers)
    # time_r, res2 = r.measure_time_execution(r.get_outliers)
    # print('Orange time: ', time_or, 'Rapid Miner time ', time_r)
    # print(res1)
    # print(res2)
    # print(type(res1))
    # print(type(res2))


    print('Linear regression weights.. ')
    time_or, res1 = ors.measure_time_execution(ors.get_linear_regression_weights, target_name='quality')
    time_r, res2 = r.measure_time_execution(r.get_linear_regression_weights, target_name='quality')
    print('Orange time: ', time_or, 'Rapid Miner time ', time_r)
    print(res1)
    print(res2)
    print(type(res1))
    print(type(res2))

    # print('K-means clustering')
    # time_or, res1 = ors.measure_time_execution(ors.get_clusters)
    # time_r, res2 = r.measure_time_execution(r.get_clusters)
    # print('Orange time: ', time_or, 'Rapid Miner time ', time_r)
    # print(res1)
    # print(res2)
    # print(type(res1))
    # print(type(res2))

    # print('Prediction')
    # time_or, res1 = ors.measure_time_execution(ors.get_prediction, data_to_predict_path=data_prediction_path, target_name='quality')
    # time_r, res2 = r.measure_time_execution(r.get_prediction, data_to_predict_path=data_prediction_path, target_name='quality')
    # print('Orange time: ', time_or, 'Rapid Miner time ', time_r)
    # #time_r, _ = r.measure_time_execution(r.run_empty_process)
    # print('Orange time: ', time_or, 'Rapid Miner time ', time_r)
    # print(res1)
    # print(res2)
    # print(type(res1))
    # print(type(res2))


def main():
    app = QApplication(sys.argv)
    window = ServiceAnalyzerApp()
    window.show()
    app.exec_()
    #run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
