import codecs
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import geopy as gp

from TA.taTools import gps2cart, tasdxyz


@dataclass
class Detector():
    detector_num: str
    detector_cart_position: Tuple[float, float]

class Detectors():
    def __init__(self) -> None:
        self._detectors = {}
        
        self.tasdx = []
        self.tasdy = []
        
        tasdxyz([],self.tasdx,self.tasdy,[])

        with codecs.open(Path(__file__).resolve().parent / 'TA/tasd_gpscoors.txt', 'rb', 'utf-8') as file: 
            for line in file.readlines():

                det, lat, long, alt = line.split()
                gps = gp.point.Point(lat, long, 0)
                x, y, z = gps2cart(gps)
                self._detectors[det] = Detector(det, (x, y))


    def __getitem__(self, id: str) -> Detector:
        return self._detectors[id]

    def getCart(self, id:str) -> Tuple[float, float]:
        return self._detectors[id].detector_cart_position

    def getAllDets(self) -> List[str]:
        return [detector for detector in self._detectors]


def NearDets(det_num, size, centered) -> Dict:
    det_num = int(det_num)
    dict = {}

    if centered:
        l = math.floor((size/2) - .5)
        for _ in range(l):
            det_num -= 99

    for n in range(size):
        temp_det_num = det_num
        for m in range(size):
            dict[(n, m)] = str(temp_det_num).rjust(4, "0")
            temp_det_num += 100
        det_num -= 1
    return dict

if __name__ == '__main__':
    start = time.perf_counter()
    Det = Detectors()
    stop = time.perf_counter()
    print(stop - start)

    start = time.perf_counter()
    cart = Det.getCart('0619')
    stop = time.perf_counter()
    print(stop - start)
