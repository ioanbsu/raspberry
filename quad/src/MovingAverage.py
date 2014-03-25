__author__ = 'ivanbahdanau'
import time
from random import randint


class MovingAverage:
    dataArray = []
    movingAverageSize = 0


    def __init__(self, movingAverageSize=10):
        self.dataArray = [] * movingAverageSize
        self.movingAverageSize = movingAverageSize

    def add(self, value):
        if self.movingAverageSize == len(self.dataArray):
            self.dataArray.pop(0)
        self.dataArray.append(value)


    def getAverageValue(self):
        totalValue = 0
        counter = 0
        for value in self.dataArray:
            counter += 1
            totalValue += value
        return totalValue / counter


test = MovingAverage(20)
millis = int(round(time.time() * 1000))

for i in range(0, 500):
    rand = randint(1, 50)
    test.add(rand)