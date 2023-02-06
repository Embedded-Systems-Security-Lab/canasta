import math
from libs.can_nomac_rt import CAN_NOMAC_RT

def can_result(priority, period, TX, DLC, tbit):
    resp =  CAN_NOMAC_RT(priority, period, TX, DLC, tbit)
    result =[]
    for p in range(len(priority)):
        
        B= resp.get_Blocking_m(p)
        #print(B)
        
        length_m=resp.get_length_m(p,TX,B,TX[p])
        #print(length_m)
        Q=math.ceil(length_m /period[p])
        #print(Q)
        
        result.append(resp.get_Response_time(p,Q,B))
        #get_Response_time(p,Q,B)
