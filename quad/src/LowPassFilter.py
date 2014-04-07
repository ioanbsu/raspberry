__author__ = 'ivanbahdanau'

import csv
import sys


class LowPassFilter:
    lastFilteredValue = 0.

    def __init__(self, smooting=100):
        self.smoothing = smooting

    def filter(self, value):
        self.lastFilteredValue += (value - self.lastFilteredValue) / self.smoothing
        return self.lastFilteredValue


if len(sys.argv) >= 2 and sys.argv[1] == 'test':
    filter = LowPassFilter(1000)
    with open('/Users/ivanbahdanau/IdeaProjects/git/raspberry/quad/src/sampleData.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            for value in row:
                print filter.filter(float(value))

