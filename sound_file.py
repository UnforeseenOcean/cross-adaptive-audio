from __future__ import absolute_import
import hashlib
import wave
import contextlib
import json
import os
import settings
import analyze
import six


class SoundFile(object):
    def __init__(self, filename, is_input=True):
        self.is_input = is_input
        self.filename = filename
        if self.is_input:
            self.file_path = os.path.join(settings.INPUT_DIRECTORY, self.filename)
        else:
            self.file_path = os.path.join(settings.OUTPUT_DIRECTORY, self.filename)
        
        self.md5 = None
        self.get_md5()
        self.duration = None
        self.analysis = {
            'ksmps': settings.CSOUND_KSMPS,
            'series': {}
        }

    def get_md5(self):
        if self.md5 is None:
            my_hash = hashlib.md5()
            with open(self.file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    my_hash.update(chunk)
            self.md5 = my_hash.hexdigest()
        return self.md5

    def compute_duration(self):
        with contextlib.closing(wave.open(self.file_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

    def get_duration(self):
        if self.duration is None:
            self.duration = self.compute_duration()
        return self.duration

    def get_analysis(self, ensure_standardized_series=False):
        if self.analysis is None:
            raise Exception(str(self) + ' lacks analysis')
        if ensure_standardized_series and 'series_standardized' not in self.analysis:
            raise Exception('Standardized analysis needs to be calculated on beforehand!')
        return self.analysis

    def get_num_frames(self):
        arbitrary_series = six.next(six.itervalues(self.analysis['series']))
        return len(arbitrary_series)

    def get_standardized_neural_input_vector(self, k):
        """
        Get a neural input vector for a given frame k.
        Assumes that self.analysis['series_standardized'] is defined and k is within bounds.
        May raise an exception otherwise
        :param k:
        :return: list
        """
        feature_vector = []
        for feature in settings.NEURAL_INPUT_CHANNELS:
            feature_vector.append(self.analysis['series_standardized'][feature][k])
        return feature_vector

    def get_serialized_representation(self):
        feature_data = self.get_analysis(ensure_standardized_series=True)
        feature_data['order'] = analyze.Analyzer.FEATURES_LIST
        return {
            'feature_data': feature_data,
            'filename': self.filename,
            'is_input': self.is_input
        }

    def delete(self):
        try:
            os.remove(self.file_path)
        except OSError:
            pass
