import math
from libs.can_nomac_rt import CAN_NOMAC_RT

def can_result(priority, period, TX, DLC, tbit):
    resp =  CAN_NOMAC_RT(priority, period, TX, DLC, tbit)
    result =[]
    for p in range(len(priority)):
        
        B= resp.get_Blocking_m(p)
        length_m=resp.get_length_m(p,TX,B,TX[p])
        Q=math.ceil(length_m /period[p])
        result.append(resp.get_Response_time(p,Q,B))
