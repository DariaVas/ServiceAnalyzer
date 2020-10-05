from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QInputDialog, QMessageBox
import csv
import mainwindow
import config
import traceback
from threading import Thread
from service_analyzer import ServiceAnalyzer, Functionality, ComparisonCriteria, EvaluationCriteria

DEFAULT_SOURCE_PATH = config.get_config()['Service']['default_sources_path']
INVISIBLE_STYLE = "QLabel {color : rgba(0, 170, 0, 0); }"
VISIBLE_STYLE = "QLabel {color : rgb(0, 170, 0); }"


class ServiceStatus:
    unknown = 'unknown'
    in_progress = 'in progress'
    completed = 'completed'


class ServiceAnalyzerApp(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.service_analyzer = ServiceAnalyzer()
        self.btn_browse_path.clicked.connect(self.onBrowseDataPathClicked)
        self.btn_process_data.clicked.connect(self.onProcessBtnClicked)
        self.table_data = QTableWidget()
        self.prediction_table = QTableWidget()
        self.rp_result_table = QTableWidget()
        self.orange_result_table = QTableWidget()
        self.scrollArea_data.setWidget(self.table_data)
        self.scrollArea_data_to_predict.setWidget(self.prediction_table)
        self.scrollArea_orange_results.setWidget(self.orange_result_table)
        self.scrollArea_rp_results.setWidget(self.rp_result_table)
        self.cBx_find_time_dependency.stateChanged.connect(self.onCBxFindTimeDependency_stateChanged)

    def onCBxFindTimeDependency_stateChanged(self, i):
        state = self.cBx_find_time_dependency.isChecked()
        self.label_data_increments.setEnabled(state)
        self.lineEdit_data_increments.setEnabled(state)
        self.label_num_experiments.setEnabled(state)
        self.lineEdit_num_experiments.setEnabled(state)

    def onBrowseDataPathClicked(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', filter='*.csv', directory=DEFAULT_SOURCE_PATH)[0]
        if fname:
            self.edit_data_path.setText(fname)
        self.load_cvs_file_to_table(self.edit_data_path.text(), self.table_data)

    def load_cvs_file_to_table(self, fname, table):
        self.clean_table(table)
        with open(fname, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            line = 0
            for row in reader:
                j = 0
                if line != 0:
                    table.insertRow(table.rowCount())
                table.setColumnCount(len(row))
                for value in row:
                    item = QTableWidgetItem(value)
                    if line == 0:
                        table.setHorizontalHeaderItem(j, item)
                    else:
                        table.setItem(table.rowCount() - 1, j, item)
                    j += 1
                line += 1

    def clean_table(self, table):
        self.table_data.clear()
        while table.rowCount() > 0:
            table.removeRow(0)

    def show_error_msg(self, details):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Error")
        msgBox.setText("Cannot process data")
        msgBox.setDetailedText(details)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def show_service_result_table(self, results, service_result_table):
        self.clean_table(service_result_table)
        if not results:
            return
        for r in results:
            service_result_table.insertRow(service_result_table.rowCount())
            if not isinstance(r, list):
                service_result_table.setColumnCount(1)
                item = QTableWidgetItem(str(r))
                service_result_table.setItem(service_result_table.rowCount() - 1, 0, item)
                continue
            service_result_table.setColumnCount(len(r))
            j = 0
            for sub_item in r:
                item = QTableWidgetItem(str(sub_item))
                service_result_table.setItem(service_result_table.rowCount() - 1, j, item)
                j += 1

    def show_service_results(self, config, service_results, label):
        if not config.get("evaluation_criteria"):
            return
        results = ""
        for c in service_results["criteria"]:
            v = service_results["criteria"][c]
            readable_c = " ".join(c.split("_"))
            results = results + "{}: {}\n".format(readable_c, v)
        label.setText(results)

    def process(self):
        configuration = {'path': self.edit_data_path.text(),
                         'functionality': 0,
                         'rapidminer': self.cBx_rp_service_run.isChecked(),
                         'orange': self.cBx_orange_service_run.isChecked(),
                         'comparison': [],
                         'evaluation_criteria': [],
                         'target': '',
                         'data_to_predict': ''
                         }
        try:
            self.clean_table(self.prediction_table)
            index = self.list_functionality.currentIndex() + 1
            if index in (Functionality.prediction.value, Functionality.linear_regression.value):
                target, _ = QInputDialog.getText(self, 'Need target column', 'Enter target column name:')
                if not target:
                    self.show_error_msg("Functions to predict value or calculate linear regression requires label name")
                    return
                configuration['target'] = target
            if index == Functionality.prediction.value:
                fname = \
                    QFileDialog.getOpenFileName(self, 'Path to data for prediction', filter='*.csv',
                                                directory=DEFAULT_SOURCE_PATH)[0]
                if not fname:
                    self.show_error_msg('Need path to preditction')
                self.load_cvs_file_to_table(fname, self.prediction_table)
                configuration['data_to_predict'] = fname

            configuration['functionality'] = Functionality(index)
            if self.cBx_compare_results:
                configuration['comparison'].append(ComparisonCriteria.results)
            if self.cBx_find_execution_time:
                configuration['evaluation_criteria'].append(EvaluationCriteria.execution_time)

            if configuration['orange']:
                self.label_orange_status.setText(ServiceStatus.in_progress)
            if configuration['rapidminer']:
                self.label_rp_status.setText(ServiceStatus.in_progress)

            results = self.service_analyzer.process(configuration)

            if configuration['orange']:
                self.label_orange_status.setText(ServiceStatus.completed)
                self.show_service_results(configuration, results.get('orange'), self.label_orange_criteria_results)
                self.show_service_result_table(results.get('orange')['result'], self.orange_result_table)

            if configuration['rapidminer']:
                self.label_rp_status.setText(ServiceStatus.completed)
                self.show_service_results(configuration, results.get('rapidminer'), self.label_rp_results)
                self.show_service_result_table(results.get('rapidminer')['result'], self.rp_result_table)
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            self.show_error_msg(str(ex))
        finally:
            self.setEnabled(True)
            self.label_status.setText("Finished")

    def onProcessBtnClicked(self):
        # gather config
        # run process
        # show results
        th = Thread(target=self.process)
        self.label_status.setStyleSheet(VISIBLE_STYLE)
        self.setEnabled(False)
        th.start()
