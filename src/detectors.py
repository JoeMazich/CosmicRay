import geopy as gp
import codecs
from dataclasses import dataclass
from typing import Tuple
from taTools import *

import time

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

        with codecs.open('tasd_gpscoors.txt', 'rb',  'utf-8') as file: 
            for line in file.readlines():

                det, lat, long, alt = line.split()
                gps = gp.point.Point(lat, long, 0)
                x, y, z = gps2cart(gps)
                self._detectors[det] = Detector(det, (x, y))


    def __getitem__(self, id: str) -> Detector:
        return self._detectors[id]
    
    def getCart(self, id:str) -> Tuple[float, float]:
        return self._detectors[id].detector_cart_position

if __name__ == '__main__':
    start = time.perf_counter()
    Det = Detectors()
    stop = time.perf_counter()
    print(stop - start)

    start = time.perf_counter()
    cart = Det.getCart('0619')
    stop = time.perf_counter()
    print(stop - start)