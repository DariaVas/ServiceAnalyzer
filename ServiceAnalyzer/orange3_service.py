import datetime
import numpy

from Orange import clustering, data, classification, preprocess, base
from Orange.base import Model
from Orange.data import Domain, domain
from Orange.regression.linear import LinearRegressionLearner
from Orange.evaluation.testing import Results, TestOnTestData
from data_mining_service import DataMiningService


class Orange3Service(DataMiningService):
    def __init__(self, data_path):
        self._data_path = data_path

    def get_outliers(self):
        data_table = data.Table(self._data_path)
        lof = classification.LocalOutlierFactorLearner()
        res = lof(data_table)(data_table)
        return list(res.get_column_view('Outlier')[0])

    def get_prediction(self, data_to_predict_path, target_name):
        data_domain = data.Domain(attributes=[
            data.ContinuousVariable('fixed acidity'),
            data.ContinuousVariable('volatile acidity'),
            data.ContinuousVariable('citric acid'),
            data.ContinuousVariable('residual sugar'),
            data.ContinuousVariable('chlorides'),
            data.ContinuousVariable('free sulfur dioxide'),
            data.ContinuousVariable('total sulfur dioxide'),
            data.ContinuousVariable('density'),
            data.ContinuousVariable('pH'),
            data.ContinuousVariable('sulphates'),
            data.ContinuousVariable('alcohol')],
            class_vars=data.ContinuousVariable(target_name))
        data_table = data.Table.from_table(domain=data_domain, source=data.Table(self._data_path))
        data_to_predict_table = data.Table.from_table(domain=data_domain, source=data.Table(data_to_predict_path))
        mean_ = LinearRegressionLearner()
        model = mean_(data_table)
        ####
        results = Results()
        results.data = data_to_predict_table
        results.domain = data_to_predict_table.domain
        results.row_indices = numpy.arange(len(data_to_predict_table))
        results.folds = (Ellipsis,)
        results.actual = data_to_predict_table.Y
        domain = data_to_predict_table.domain
        classless_data = data_to_predict_table.transform(
            Domain(domain.attributes, None, domain.metas))
        pred = model(classless_data, Model.Value)
        prob = numpy.zeros((len(pred), 0))
        results.unmapped_probabilities = prob
        results.unmapped_predicted = pred
        results.probabilities = results.predicted = None
        print(results.predicted)
        backmappers, n_values = model.get_backmappers(data_to_predict_table)
        prob = model.backmap_probs(prob, n_values, backmappers)
        pred = model.backmap_value(pred, prob, n_values, backmappers)
        results.predicted = pred.reshape((1, len(data_to_predict_table)))
        results.probabilities = prob.reshape((1,) + prob.shape)
        return results.predicted[0].tolist()

    def get_linear_regression_weights(self, target_name):
        data_table = data.Table(self._data_path)
        d = data.Domain(attributes=[
            data.ContinuousVariable('fixed acidity'),
            data.ContinuousVariable('volatile acidity'),
            data.ContinuousVariable('citric acid'),
            data.ContinuousVariable('residual sugar'),
            data.ContinuousVariable('chlorides'),
            data.ContinuousVariable('free sulfur dioxide'),
            data.ContinuousVariable('total sulfur dioxide'),
            data.ContinuousVariable('density'),
            data.ContinuousVariable('pH'),
            data.ContinuousVariable('sulphates'),
            data.ContinuousVariable('alcohol')],
            class_vars=data.ContinuousVariable(target_name))
        columns = [d.name for d in data_table.domain.variables]
        columns.remove(target_name)
        new_table = data.Table.from_table(domain=d, source=data_table)
        mean_ = LinearRegressionLearner()
        model = mean_(new_table)
        result = []
        for i in range(len(columns)):
            result.append([columns[i], model.coefficients[i]])
        return result

    def get_clusters(self, num_clusters):
        data_table = data.Table(self._data_path)
        km = clustering.KMeans(n_clusters=num_clusters)
        return km(data_table).tolist()

    def measure_time_execution(self, func, **kwargs):
        ms_koef = 1000
        print('Orange service.Running function ', func.__name__)
        ts = datetime.datetime.now().timestamp() * ms_koef
        res = func(**kwargs)
        te = datetime.datetime.now().timestamp() * ms_koef
        diff = te - ts
        print('Orange service.{} execution time: {}'.format(func.__name__, diff))
        return res, diff

    def set_data_path(self, data_path):
        self._data_path = data_path
