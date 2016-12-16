import time
from PyQt4.QtCore import *

# w main app nalezy podac self.connect(self.rk.diag, QCore.SIGNAL("virt_balisa_int"), self.rk.diag.virtualBalisaAlertInterrupt)
# inicjalizujac PKMWindow.
# w PKMMap nalezy dodac self.diag = techDiag.TrainsDelays(self.czujniki, sensorRadius) inicjalizujac Map
# oraz w tick wstawic diag.tick(self.czujniki, self.trains)


class TrainsDelays(QObject):

    def __init__(self, sensors, sensorRadius):
        QObject.__init__(self)
        self.realBalisaCheckedCountdown = [0] * len(sensors)
        self.alarmSensCountdown = [0] * len(sensors)
        self.alarmedOnTrain = [0] * len(sensors)
        self.stanCzujnikow = []
        for sensor in sensors:
            self.stanCzujnikow.append(sensor.Aktywny)
        self.R = sensorRadius

    def tick(self, czujniki, trains):
        REAL_BALISA_CNT_MAX = 20
        # ALARM_CNT_MAX = 20
        #
        # i_cz = 0
        # for czujnik in czujniki:
        #     if czujnik.Aktywny != self.stanCzujnikow[i_cz]:
        #         self.stanCzujnikow[i_cz] = czujnik.czyA
        #         self.realBalisaCheckedCountdown[i_cz] = REAL_BALISA_CNT_MAX
        #     elif self.realBalisaCheckedCountdown[i_cz]>0:
        #         self.realBalisaCheckedCountdown[i_cz] -= 1
        #     elif self.alarmSensCountdown[i_cz] > 0:
        #         self.alarmSensCountdown[i_cz] -= 1
        #         if self.alarmSensCountdown[i_cz] == 0:
        #             print "ALARM!",czujnik.nr, self.alarmedOnTrain[i_cz]
        #             el = (czujnik.nr, self.alarmedOnTrain[i_cz])
        #             self.emit(SIGNAL("virt_balisa_int"), el)
        #     else:
        #         i_t = 0
        #         for train in trains:
        #             if (train[0].x/10 - czujnik.x)**2 + (train[0].y/10 - czujnik.y)**2 <= self.R**2:
        #                 self.alarmSensCountdown[i_cz] = ALARM_CNT_MAX
        #                 self.alarmedOnTrain[i_cz] = i_t
        #                 break
        #             i_t += 1
        #     i_cz += 1

    def virtualBalisaAlertInterrupt(self, list):
        cz_nr, train_nr = list
        # print "Mozliwe wykolejenie pociagu", train_nr, "przed balisa nr", cz_nr