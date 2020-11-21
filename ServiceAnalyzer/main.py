import sys
from PyQt5.QtWidgets import QApplication
from user_interface import ServiceAnalyzerApp


'''
1. Outliers
2. Linear regression weights
3. Prediction 
4. K-means clustering
'''


def main():
    app = QApplication(sys.argv)
    window = ServiceAnalyzerApp()
    window.show()
    app.exec_()
    # from orange3_service import Orange3Service
    # o = Orange3Service("/home/dasha/Documents/DiplomaFolder/Wine/winequality-white_100_experimental.csv")
    # t = o.remove_outliers()
    # save_data_table_to_file(t, '/home/dasha/orange.csv')
    # o.set_data_path('/home/dasha/orange.csv')
    # print(o.get_clusters(4))
    # from rapid_miner_service import  RapidMinerService, save_data_frame_to_file
    # r = RapidMinerService("/home/dasha/Documents/DiplomaFolder/Wine/winequality-white_100_experimental.csv")
    # t1 = r.remove_outliers()
    # save_data_frame_to_file(t1, '/home/dasha/rp.csv')

    #
    # def aucroc(y_pred_test, y_pred_outliers):
    #     return roc_auc_score(np.append(np.ones((len(y_pred_test))), -np.ones((len(y_pred_outliers)))),
    #                          np.append(y_pred_test, y_pred_outliers))
  #  print(t1)

    return 0


if __name__ == '__main__':
    sys.exit(main())
