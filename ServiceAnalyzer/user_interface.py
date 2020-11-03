import pyqtgraph as pg
from math import fabs
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, \
    QSizePolicy, QTextEdit, QInputDialog
import csv

import numpy as np

import mainwindow
import config
import traceback
from service_analyzer import ServiceAnalyzer, Functionality, ComparisonCriteria, EvaluationCriteria

DEFAULT_SOURCE_PATH = config.get_config()['Service']['default_sources_path']
INVISIBLE_STYLE = "QLabel {color : rgba(0, 170, 0, 0); }"
GREEN_STYLE = "QLabel {color : rgb(0, 170, 0); }"
BLACK_STYLE = "QLabel {color : rgb(0, 0, 0); }"


class ServiceStatus:
    unknown = 'unknown'
    in_progress = 'in progress'
    completed = 'completed'


class ServiceAnalyzerApp(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.graph_windows = {'Orange3': GraphWindow(), 'Rapid Miner': GraphWindow()}
        self.barchar_window = {'Orange3': BarChart(), 'Rapid Miner': BarChart()}
        self.setupUi(self)
        self.service_analyzer = ServiceAnalyzer()
        self.btn_browse_path.clicked.connect(self.onBrowseDataPathClicked)
        self.btn_browse_predi_path.clicked.connect(self.onBrowsePredictionDataPathClicked)
        self.btn_process_data.clicked.connect(self.onProcessBtnClicked)
        self.list_functionality.currentIndexChanged.connect(self.onFunctionalityChanged)
        self.table_data = QTableWidget()
        self.prediction_table = QTableWidget()
        self.rp_result_table = QTableWidget()
        self.orange_result_table = QTableWidget()
        self.service_compare_table = QTableWidget()
        self.scrollArea_data.setWidget(self.table_data)
        self.scrollArea_data_to_predict.setWidget(self.prediction_table)
        self.scrollArea_orange_results.setWidget(self.orange_result_table)
        self.scrollArea_rp_results.setWidget(self.rp_result_table)
        self.cBx_find_time_dependency.stateChanged.connect(self.onCBxFindTimeDependency_stateChanged)
        self.k_means_results = QTextEdit()

    def swap_comparison_results_widget(self, show_table=True):
        if show_table:
            self.scrollArea_comparison_results.setWidget(self.service_compare_table)
            self.k_means_results = QTextEdit()
        else:
            self.scrollArea_comparison_results.setWidget(self.k_means_results)
            self.service_compare_table = QTableWidget()


    def onBrowsePredictionDataPathClicked(self):
        fname, _ = \
            QFileDialog.getOpenFileName(self, 'Path to data for prediction', filter='*.csv',
                                        directory=DEFAULT_SOURCE_PATH)
        self.edit_prediction_data_path.setText(fname)
        self.load_cvs_file_to_table(fname, self.prediction_table)

    def onFunctionalityChanged(self, index):
        enable_prediction_path = False
        enable_target_variable = False
        index = index + 1
        if index == Functionality.prediction.value:
            enable_prediction_path = True
        if index in (Functionality.prediction.value, Functionality.linear_regression.value):
            enable_target_variable = True

        self.edit_prediction_data_path.setEnabled(enable_prediction_path)
        self.btn_browse_predi_path.setEnabled(enable_prediction_path)
        self.lineEdit_target_name.setEnabled(enable_target_variable)

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
                if not row:
                    continue
                j = 0
                if line != 0:
                    table.insertRow(table.rowCount())
                table.setColumnCount(len(row))
                for value in row:
                    item = QTableWidgetItem(value)
                    if line == 0:
                        table.setHorizontalHeaderItem(j, item)
                    else:
                        print('insert {} ( {}, {})'.format(value, table.rowCount() - 1, j))
                        table.setItem(table.rowCount() - 1, j, item)
                    j += 1
                line += 1

    def clean_table(self, table):
        table.clear()
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

    def _show_chart(self, data, service_name):
        self.graph_windows[service_name].setWindowTitle(
            "{} execution time dependence from amount of data".format(service_name))
        self.graph_windows[service_name].setGeometry(self.geometry())
        self.graph_windows[service_name].update_plot(data)
        self.graph_windows[service_name].show()

    def show_service_results(self, _config, service_results, label, service_name):
        if not _config.get("evaluation_criteria"):
            return
        results = ''
        for c in service_results:
            if c == 'execution_time':
                results = results + "{}: {}\n".format("execution time", service_results['execution_time'])
            if c == 'time_dependence':
                self._show_chart(service_results['time_dependence'], service_name)
        if not results:
            results = 'unknown'
        label.setText(results)

    def _show_outliers_comparison_results(self, results):
        notes = '* Rapid Miner results were normalized to [0;1] range\n' \
                'Services results matches in {} %'.format(results['percent_of_matches'])
        self.label_notes.setStyleSheet(BLACK_STYLE)
        self.label_notes.setText(notes)
        self.swap_comparison_results_widget()
        self.clean_table(self.service_compare_table)
        self._show_matches_table(results)

    def _show_linear_regression_coefs(self, results):
        self.swap_comparison_results_widget()
        self.clean_table(self.service_compare_table)
        columns = 4
        self.service_compare_table.setColumnCount(columns)
        headers = ['titles', 'Orange3', 'Rapid Miner', 'Diff (Orange result - Rapid Miner result)']
        self.service_compare_table.setHorizontalHeaderLabels(headers)
        self.service_compare_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.service_compare_table.horizontalHeader().setStretchLastSection(True)
        total_tolerance = 0
        for i in range(len(results['orange'])):
            self.service_compare_table.insertRow(self.service_compare_table.rowCount())
            total_tolerance += fabs(fabs(results['orange'][i]) - fabs(results['rapidminer'][i]))
            row = [results['titles'][i], results['orange'][i], results['rapidminer'][i], results['diffs'][i]]
            self.service_compare_table.setColumnCount(columns)
            for j in range(columns):
                item = QTableWidgetItem(str(row[j]))
                self.service_compare_table.setItem(self.service_compare_table.rowCount() - 1, j, item)
        self.label_comparison_results.setText('Total tolerance %s ' % total_tolerance)

    def _show_matches_table(self, results):
        columns = 3
        self.service_compare_table.setColumnCount(columns)
        headers = ['Orange3', 'Rapid Miner', 'Matches']

        self.service_compare_table.setHorizontalHeaderLabels(headers)
        self.service_compare_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.service_compare_table.horizontalHeader().setStretchLastSection(True)

        for i in range(len(results['orange'])):
            self.service_compare_table.insertRow(self.service_compare_table.rowCount())
            row = [results['orange'][i], results['rapidminer'][i], results['matches'][i]]
            self.service_compare_table.setColumnCount(columns)
            for j in range(columns):
                item = QTableWidgetItem(str(row[j]))
                self.service_compare_table.setItem(self.service_compare_table.rowCount() - 1, j, item)

    def _show_prediction_comparison_results(self, results):
        notes = '* Orange results were rounded up\n' \
                'Services results matches in {} %'.format(results['percent_of_matches'])
        self.label_notes.setStyleSheet(BLACK_STYLE)
        self.label_notes.setText(notes)
        self.swap_comparison_results_widget()
        self.clean_table(self.service_compare_table)
        self._show_matches_table(results)

    def _prepare_clusters_results(self, results):
        headers_objects = {
            'orange': ('Orange3', 'Rapid Miner'),
            'rapidminer': ('Rapid Miner', 'Orange3')
        }
        print('THIIS')
        print(results)
        result_string = ''
        for service in results:
            result_string += '{} matches: \n'.format(headers_objects[service][0])
            for cluster in results[service]:
                print(cluster)
                result_string += '  {} cluster to {} clusters: \n'.format(cluster, headers_objects[service][1])
                print(service, '  ', cluster)
                print(results[service])
                for match_cluster in results[service][cluster]:
                    result_string += '      {} - {}% \n'.format(match_cluster, results[service][cluster][match_cluster])
        return result_string

    def _show_k_means_clustering_results(self, results):
        text = self._prepare_clusters_results(results['clusters_intersection'])
        self.swap_comparison_results_widget(show_table=False)
        self.k_means_results.setText(text)

        # print(text)
        # self.label_notes.setStyleSheet(BLACK_STYLE)
        # self.label_notes.setText(text)

        self.barchar_window['Orange3'].update_bar(results['distribution']['orange'])
        self.barchar_window['Rapid Miner'].update_bar(results['distribution']['rapidminer'])
        for service_name in ('Orange3', 'Rapid Miner'):
            self.barchar_window[service_name].setWindowTitle(
                "{} clusters distribution".format(service_name))
            self.barchar_window[service_name].setGeometry(self.geometry())
            self.barchar_window[service_name].show()

    def show_service_comparison_results(self, functionality, results):
        self.label_comparison_status.setText('success')
        self.label_comparison_results.setText('')
        if functionality == Functionality.outliers:
            self._show_outliers_comparison_results(results['service_comparison'])
        elif functionality == Functionality.linear_regression:
            self._show_linear_regression_coefs(results['service_comparison'])
        elif functionality == Functionality.prediction:
            self._show_prediction_comparison_results(results['service_comparison'])
        elif functionality == Functionality.k_means_clustering:
            self._show_k_means_clustering_results(results['service_comparison'])
        else:
            print('Unknown functionality in comparison results ')

    def process(self):
        configuration = {'path': self.edit_data_path.text(),
                         'functionality': 0,
                         'rapidminer': self.cBx_rp_service_run.isChecked(),
                         'orange': self.cBx_orange_service_run.isChecked(),
                         'comparison': [],
                         'evaluation_criteria': [],
                         'target': '',
                         'data_to_predict': '',
                         'rows_increment_index': '',
                         'num_experiments': '',
                         'clusters': ''
                         }
        try:
            self.clean_table(self.prediction_table)
            index = self.list_functionality.currentIndex() + 1
            if index in (Functionality.prediction.value, Functionality.linear_regression.value):
                target = self.lineEdit_target_name.text()
                if not target:
                    self.show_error_msg("Functions to predict value or calculate linear regression requires label name")
                    return
                configuration['target'] = target
            if index == Functionality.prediction.value:
                fname = self.edit_prediction_data_path.text()
                if not fname:
                    self.show_error_msg('Need path to prediction')
                self.load_cvs_file_to_table(fname, self.prediction_table)
                configuration['data_to_predict'] = fname
            if index == Functionality.k_means_clustering.value:
                    # get k for experiment
                    num, ok = QInputDialog.getInt(self, "Number of cluster", "enter k: ")
                    if ok or num:
                        configuration['clusters'] = num
                    else:
                        raise RuntimeError('You should specify the number of cluster for k-means clustering!')

            configuration['functionality'] = Functionality(index)
            if self.cBx_compare_results.isChecked():
                configuration['comparison'].append(ComparisonCriteria.results)
            if self.cBx_find_execution_time.isChecked():
                configuration['evaluation_criteria'].append(EvaluationCriteria.execution_time)
            if self.cBx_find_time_dependency.isChecked():
                configuration['evaluation_criteria'].append(EvaluationCriteria.time_dependence_from_data)
                if not self.lineEdit_num_experiments.text() or not self.lineEdit_data_increments.text():
                    raise RuntimeError('Amount of incremented rows and number of experiments must be set!')
                configuration['rows_increment_index'] = int(self.lineEdit_data_increments.text())
                configuration['num_experiments'] = int(self.lineEdit_num_experiments.text())

            if configuration['orange']:
                self.label_orange_status.setText(ServiceStatus.in_progress)
            if configuration['rapidminer']:
                self.label_rp_status.setText(ServiceStatus.in_progress)

            results = self.service_analyzer.process(configuration)

            if configuration['orange']:
                self.label_orange_status.setText(ServiceStatus.completed)
                self.show_service_results(configuration, results.get('orange'), self.label_orange_criteria_results,
                                          'Orange3')
                self.show_service_result_table(results.get('orange')['result'], self.orange_result_table)

            if configuration['rapidminer']:
                self.label_rp_status.setText(ServiceStatus.completed)
                self.show_service_results(configuration, results.get('rapidminer'), self.label_rp_results,
                                          'Rapid Miner')
                self.show_service_result_table(results.get('rapidminer')['result'], self.rp_result_table)

            if configuration['comparison']:
                self.show_service_comparison_results(configuration['functionality'], results)
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
        self.label_status.setText("Processing")
        self.label_status.setStyleSheet(GREEN_STYLE)
        self.label_notes.setStyleSheet(INVISIBLE_STYLE)
        self.label_comparison_status.setText('unknown')
        self.label_rp_results.setText('')
        self.clean_table(self.service_compare_table)
        self.setEnabled(False)
        self.repaint()
        self.process()


class GraphWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(GraphWindow, self).__init__(*args, **kwargs)
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.plotItem.getAxis('left').setLabel('time (ms)')
        self.graphWidget.plotItem.getAxis('bottom').setLabel('number of processed rows')

    def update_plot(self, data):
        # plot data: x - num rows y - time values
        time = []
        rows = []
        for r, t in data:
            time.append(t)
            rows.append(r)
        self.graphWidget.plot(rows, time, clear=None, meta='time dependence from amount of data')


class BarChart(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(BarChart, self).__init__(*args, **kwargs)
        self.graphWidget = pg.plot()
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground((255, 255, 255))

    def update_bar(self, data):
        print(data)
        x = np.arange(len(data))
        bg = pg.BarGraphItem(x=x, height=data, width=0.6, brush=(133, 175, 198))
        self.graphWidget.addItem(bg)
