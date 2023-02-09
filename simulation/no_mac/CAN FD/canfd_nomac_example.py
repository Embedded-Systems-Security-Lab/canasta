import os
import csv
import math

from libs.can_nomac_module import can_result
from libs.can_fd_padding import can_fd_data

#import utils.can_fd_padding
def read_file():
    priority,period,TX,size = [],[],[],[]
    bus_speed = 250
    fd_bus_speed =4000
    tx=0
    tbit = 1 / float(bus_speed)
    len_message_frame=[]
    dtbit = 1/fd_bus_speed

    
    CURRENT_DIR = os.path.dirname(__file__)
    file_path = os.path.join(CURRENT_DIR,'cfdtest.csv')
    with open(file_path,'r') as dataset:
        reader = csv.reader(dataset)
        next(reader)
        for row in reader:
            period.append(int(row[1]))
            priority.append(int(row[0]))
            size.append(int(row[2]))
    
    DLC = [can_fd_data(i) for i in size]
    for i in range(len(DLC)):
        if DLC[i] <= 16:
            
            tx = 33 * tbit + ((35 + (10 * DLC[i])) * dtbit)
        if DLC[i] > 16:
            tx= 33 * tbit + ((40 + 10 * DLC[i]) * dtbit)  
        
        TX.append(tx)
        
    nomac_result = can_result(priority, period, TX, DLC, tbit)
    
    return nomac_result
         