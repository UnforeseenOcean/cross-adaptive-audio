import statistics
import pprint
import settings
import math


class Standardizer(object):
    def __init__(self, sound_files):
        self.sound_files = sound_files
        self.feature_statistics = {}

    def calculate_feature_statistics(self):
        analyses = [sf.get_analysis() for sf in self.sound_files]

        for key in analyses[0]['series']:
            self.feature_statistics[key] = {'min': None, 'max': None, 'mean': None, 'standard_deviation': None}

        for feature in self.feature_statistics:
            if settings.VERBOSE:
                print 'Analyzing {} feature statistics'.format(feature)
            series = []
            for analysis in analyses:
                series += analysis['series'][feature]

            if len(series) == 0:
                continue

            self.feature_statistics[feature]['min'] = min(series)
            self.feature_statistics[feature]['max'] = max(series)
            self.feature_statistics[feature]['mean'] = statistics.mean(series)
            self.feature_statistics[feature]['standard_deviation'] = statistics.pstdev(series)

        if settings.VERBOSE:
            pprint.pprint(self.feature_statistics)

    def add_standardized_series(self):
        print 'Calculating and writing standardized series...'

        for sf in self.sound_files:
            analysis = sf.get_analysis()
            if 'series_standardized' not in analysis:
                analysis['series_standardized'] = {}
                for feature in self.feature_statistics:
                    analysis['series_standardized'][feature] = [
                        self.get_standardized_value(feature, value)
                        for value in analysis['series'][feature]
                        ]
                sf.write_analysis_data_cache()

    def get_standardized_value(self, feature, value):
        """
        :param feature:
        :param value:
        :return: A value that makes the series have zero mean and unit variance. Good for machine learning.
        """
        return (value - self.feature_statistics[feature]['mean']) / \
               self.feature_statistics[feature]['standard_deviation']

    @staticmethod
    def get_normalized_value(standardized_value):
        """
        :param standardized_value:
        :return: A value between 0 and 1. Good for visualization.
        """
        return 0.5 + math.tanh(standardized_value) / 2
