from rapid_miner_service import RapidMinerService
from orange3_service import Orange3Service

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
        results = {}
        # Normalize Rapid Miner results [0,1]
        for i in range(r_outliers):
            r = r_outliers[i]
            if r > 1:
                r_outliers[i] = 1
            else:
                r_outliers[i] = int(round(r))
        results['orange'] = o_outliers
        results['rapidminer'] = r_outliers
        matches = []
        sum_matches = 0
        # find matches
        for i in range(r_outliers):
            if r_outliers[i] == o_outliers[i]:
                matches.append(1)
                sum_matches += 1
            else:
                matches.append(0)

        results['matches'] = matches
        results['percent_of_matches'] = round(sum_matches * 100 / len(r_outliers), 3)
        return results
