import datetime
from Orange import clustering, data, classification
from Orange.data import Domain, ContinuousVariable
from Orange.regression.linear import LinearRegressionLearner
from Orange.evaluation import R2, MAE, MSE, RMSE, CrossValidation
from Orange.preprocess import Normalize
from data_mining_service import DataMiningService
from sklearn.preprocessing import StandardScaler


class Orange3Service(DataMiningService):
    def __init__(self, data_path):
        self._data_path = data_path

    def get_outliers(self):
        data_table = data.Table(self._data_path)
        lof = classification.LocalOutlierFactorLearner(metric="chebyshev")
        res = lof(data_table)(data_table)
        return list(res.get_column_view('Outlier')[0])

    def normalize(self, data_table=None):
        if not data_table:
            data_table = data.Table(self._data_path)
        normalizer = Normalize(zero_based=True, norm_type=Normalize.NormalizeBySD, transform_class=False,
                               center=True, normalize_datetime=False)
        normalized_data = normalizer(data_table)
        return normalized_data

    def remove_outliers(self, data_table=None):
        outliers = self.get_outliers()
        if not data_table:
            data_table = data.Table(self._data_path)
        new_indices = []
        for i in range(len(outliers)):
            if outliers[i] == 1:  # not outlier
                new_indices.append(i)
            else:
                print(i)
        print('finish')

        new_table = data_table.from_table(data_table.domain, data_table, new_indices)
        return new_table

    def _specify_target_variable(self, table, target_name):
        new_attributes = []
        class_vars = []
        for a in table.domain.attributes:
            if a.name != target_name:
                new_attributes.append(a)
            else:
                class_vars.append(ContinuousVariable(a.name))
        for c in table.domain.class_vars:
            if c.name != target_name:
                new_attributes.append(c)
            else:
                class_vars.append(ContinuousVariable(a.name))

        domain = Domain(new_attributes,
                        class_vars,
                        table.domain.metas)

        return table.transform(domain)

    def get_prediction(self, data_to_predict_path, target_name):

        data_table = data.Table(self._data_path)
        data_table = self._specify_target_variable(data_table, target_name)
        print(data_table.domain)
        mean_ = LinearRegressionLearner()
        model = mean_(data_table)
        data_to_predict_table = data.Table(data_to_predict_path)
        data_to_predict_table = self._specify_target_variable(data_to_predict_table, target_name)
        res = model.predict_storage(data_to_predict_table)

        return res.tolist()

    def get_linear_regression_weights(self, target_name):
        data_table = data.Table(self._data_path)
        data_table = self._specify_target_variable(data_table, target_name)
        print(data_table.domain)
        mean_ = LinearRegressionLearner()
        model = mean_(data_table)
        columns = [d.name for d in data_table.domain.variables]
        columns.remove(target_name)
        result = []
        for i in range(len(columns)):
            result.append([columns[i], model.coefficients[i]])
        res = CrossValidation(data_table, [mean_, ])
        criterias = {'root_mean_squared_error': RMSE(res), 'absolute_error': MAE(res), 'squared_error': MSE(res),
                     'squared_correlation': R2(res)}
        for c in criterias:
            criterias[c] = round(criterias[c][0], 3)
        return criterias, result
        # columns = [d.name for d in data_table.domain.variables]
        # columns.remove(target_name)
        # new_table = data.Table.from_table(domain=d, source=data_table)
        # mean_ = LinearRegressionLearner()
        # model = mean_(new_table)

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

    @classmethod
    def save_data_to_file(cls, data_table, file_path):
        assert isinstance(data_table, data.Table)
        data_table.save(file_path)

    def get_data_path(self):
        return self._data_path
