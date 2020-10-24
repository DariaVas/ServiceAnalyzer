import copy
import math

'''
1. Outliers
2. Linear regression weights
3. Prediction 
4. K-means clustering
'''


class ServiceComparator:
    def __init__(self):
        pass

    def compare_outliers(self, r_outliers, o_outliers):
        assert len(r_outliers) == len(o_outliers)
        size = len(r_outliers)
        results = {'orange': o_outliers,
                   'rapidminer': copy.copy(r_outliers)}

        # Normalize Rapid Miner results [0,1]
        for i in range(size):
            r = results['rapidminer'][i]
            if r > 1:
                results['rapidminer'][i] = 1
            else:
                results['rapidminer'][i] = int(round(r))
        matches = []
        sum_matches = 0
        # find matches
        for i in range(size):
            if results['rapidminer'][i] == results['orange'][i]:
                matches.append(1)
                sum_matches += 1
            else:
                matches.append(0)

        results['matches'] = matches
        results['percent_of_matches'] = round(sum_matches * 100 / len(r_outliers), 3)
        return results

    def compare_linear_regression_coefs(self, r_coefs, o_coefs):
        assert len(r_coefs) == len(o_coefs)
        size = len(r_coefs)
        results = {'orange': [],
                   'rapidminer': [],
                   'titles': [],
                   'diffs': []}

        print(results)
        # find matches
        for i in range(size):
            print(o_coefs[i], '', r_coefs[i])
            results['titles'].append(o_coefs[i][0])
            results['diffs'].append(o_coefs[i][1] - r_coefs[i][1])
            results['orange'].append(o_coefs[i][1])
            results['rapidminer'].append(r_coefs[i][1])

        return results

    def compare_predictions(self, r_predicts, o_predicts):
        assert len(r_predicts) == len(o_predicts)
        size = len(r_predicts)
        results = {'orange': [],
                   'rapidminer': [],
                   'matches': [],
                   'percent_of_matches': 0}
        # Round up Orange results
        for i in range(size):
            o = math.ceil(o_predicts[i] - 0.5)
            results['orange'].append(o)
            results['rapidminer'].append(r_predicts[i])
        matches = []
        sum_matches = 0
        # find matches
        for i in range(size):
            if results['rapidminer'][i] == results['orange'][i]:
                matches.append(1)
                sum_matches += 1
            else:
                matches.append(0)
        results['matches'] = matches
        results['percent_of_matches'] = round(sum_matches * 100 / size, 3)
        return results

    def compare_clusters(self, r_clusters, o_clusters):
        def _convert_rp_cluster_name(name):
            name = name.replace('cluster_', '')
            return int(name)

        assert len(r_clusters) == len(o_clusters)
        size = len(r_clusters)
        results = {'orange': copy.copy(o_clusters),
                   'rapidminer': copy.copy(r_clusters),
                   'distribution': {
                       'orange': [],
                       'rapidminer': [],
                   }
                   }
        r_clusters = results['rapidminer']
        o_clusters = results['orange']
        o_dict = {}
        r_dict = {}
        for i in range(size):
            r_clusters[i] = _convert_rp_cluster_name(r_clusters[i])
            rp_cluster = r_clusters[i]
            if rp_cluster not in r_dict:
                r_dict[rp_cluster] = 1
            else:
                r_dict[rp_cluster] += 1

            if o_clusters[i] not in o_dict:
                o_dict[o_clusters[i]] = 1
            else:
                o_dict[o_clusters[i]] += 1
        # convert dict to list
        o_list = [None for _ in range(len(o_dict))]
        r_list = [None for _ in range(len(r_dict))]
        for i in range(len(o_dict)):
            o_list[i] = o_dict[i]
            r_list[i] = r_dict[i]
        results['distribution']['orange'] = o_list
        results['distribution']['rapidminer'] = r_list
        results['clusters_intersection'] = self._find_clusters_crossing(o_clusters, r_clusters)
        return results

    def _find_clusters_crossing(self, or_clusters, rp_clusters):
        # return {1: [0,3,5,6,7]}
        def _fill_dict(c_dict, clusters_list, index):
            cluster = clusters_list[index]
            if not c_dict.get(cluster):
                c_dict[cluster] = {index}
            else:
                c_dict[cluster].add(index)

        def _percent_of_intersestion(list1, list2):
            # percent of intersection of list1 with list2
            list_len = len(list1)
            intersection_len = len(list1 & list2)
            return round(intersection_len * 100 / list_len, 3)

        r_dict = {}
        o_dict = {}
        for i in range(len(or_clusters)):
            _fill_dict(r_dict, rp_clusters, i)
            _fill_dict(o_dict, or_clusters, i)

        assert len(r_dict) == len(o_dict)
        results = {
            'orange': {},
            'rapidminer': {},
        }
        # Get crossing of clusters
        for r_cluster in r_dict:
            r_set = r_dict[r_cluster]
            results['rapidminer'][r_cluster] = dict()
            for o_cluster in o_dict:
                o_set = o_dict[o_cluster]
                if not results['orange'].get(o_cluster):
                    results['orange'][o_cluster] = dict()
                o_intersection = results['orange'][o_cluster]
                r_intersection = results['rapidminer'][r_cluster]
                p1 = _percent_of_intersestion(o_set, r_set)
                p2 = _percent_of_intersestion(r_set, o_set)
                if p1 != 0:
                    o_intersection[r_cluster] = p1
                if p2 != 0:
                    r_intersection[o_cluster] = p2

        print('Interesting)))')
        print('Orange')
        for key in results['orange']:
            print(key, ' : ', results['orange'][key])
        print('Rapid Miner')
        for key in results['rapidminer']:
            print(key, ' : ', results['rapidminer'][key])
        print(results)
        return results
