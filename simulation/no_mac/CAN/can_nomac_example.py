import os
import csv
import math
from libs.can_nomac_module import can_result


def generate_data():
    priority = []
    period=[]
    TX=[]
    DLC = []
    bus_speed = 125000
    tbit = 1 / float(bus_speed)

    CURRENT_DIR = os.path.dirname(__file__)
    file_path = os.path.join(CURRENT_DIR,'satest.csv')
    with open(file_path,'r') as dataset:
        reader = csv.reader(dataset)
        next(reader)
        for row in reader:
            
            TX.append(round(float((55 + (10 * (int(row[1])))) * tbit),6))
            period.append(int(row[5]))
            priority.append((row[0]))
            DLC.append(int(row[1]))
    nomac_result = can_result(priority, period, TX, DLC, tbit)
    
    return nomac_result