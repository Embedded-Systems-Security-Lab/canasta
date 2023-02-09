import math  
import random 
from libs.can_nomac_module import can_result  
def xl_TX(payload, tbit, dtbit):
    # assuming base format
    Trans_time= 37 * tbit + ((129 + (8 * payload)+math.floor((9+ (8*payload))/10)) * dtbit)

    return Trans_time

def generate_data():
    dtbit = 1/10000
    tbit = 500
    priority = [i for i in range(1,16)]
    DLC = [random.randint(8,2048) for i in range(15)]
    period_set = [10,50,100,1000]
    period = sorted([random.choice(period_set) for i in range(15)])
    print(period)
    TX = [xl_TX(i, tbit, dtbit) for i in DLC] 
    
    nomac_result = can_result(priority, period, TX, DLC, tbit)
    
    return nomac_result
         