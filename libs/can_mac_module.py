import math
from libs.can_mac_rt import CAN_MAC_RT

def rand_result(priority, period,TX, full_frame,partial_frame, DLC,cmax,cmac,data_size,bus_speed):
    
    result=[]  

    resp = CAN_MAC_RT(priority, period,TX, full_frame,partial_frame, DLC,cmax,cmac,data_size,bus_speed)

    for p in range(len(resp.priority)):
        
        B = resp.get_Blocking_m(p)
        t = resp.TX[p]
        length_m = resp.get_length_busy_period(p, B, t)
    
        Q = math.ceil(length_m /resp.period[p])*(resp.full_frame[p]+resp.partial_frame[p])
       
        result.append(resp.get_Response_time(p,Q,B))
        
    return result
    #sort_file_to_csv(priority,period,DLC,TX,result)   
