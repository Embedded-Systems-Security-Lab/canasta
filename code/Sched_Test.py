import random
import math

class resp:
    
    j=0
    
    def __init__(self,p, priority, period, TX,num_frame,tbit,DLC):
        self.p = p
        self.priority = priority
        self.period = period
        self.TX = TX
        self.num_frame = num_frame
        self.tbit = tbit
        self.DLC = DLC

    @staticmethod

    def test_parameter(n,bus_speed = 125):
    #print(2)
        tbit = 1/ bus_speed
        sum=0
        s=0
        t,p=[],[]
        period_set = [5,10,100,1000]
        p_random_num = [random.choice(period_set) for i in range(n)]
        P_ = sorted(p_random_num)
        DLC = [random.randint(1, 8) for i in range(n)]
        T_time = [(55 + (10 * d)) * tbit for d in range(len(DLC))]
        u_each_task = [T_time[i]/P_[i] for i in range(len(T_time))]
        #print(u_each_task)
        for u in range(len(u_each_task)):
            sum = sum + u_each_task[u]
        
        su = round(sum,1)
        
        return su, T_time, DLC, P_, tbit


    def get_Blocking_m(self):
        
        lp=[]
        Blocking_m =0
        #incase of lower priority messages in transmission
        for m in range(len(self.priority)):
            if max(self.priority) == self.priority[self.p]:
                Blocking_m=0
            elif self.priority[m] > self.priority[self.p]:
                lp.append(self.TX[m])
                Blocking_m= max(lp) 
        return Blocking_m

    def new_get_Blocking_m(self,pmac_TX,cmac,cmax):
        Blocking_m=0
        real_blocking =0
        lp=[]
        
        #incase of lower priority
        # messages in transmission
        for m in range(len(self.priority)):
            if max(self.priority) == self.priority[self.p]:
                Blocking_m=0
            elif self.priority[m] > self.priority[self.p]:
                lp.append(max(pmac_TX[m],cmac[m])) #alpha-1 =0
                Blocking_m =max(lp)
        return Blocking_m 

    def get_Blocking_mac(self,pmac_TX,cmac,cmax):
        Blocking_m=0
        lp=[]
        #incase of lower priority messages in transmission
        for m in range(len(self.priority)):
            if max(self.priority) == self.priority[self.p]:
                Blocking_m=0
            elif self.priority[m] > self.priority[self.p]:
                lp.append(max(cmac[m],cmax[m]))
                Blocking_m= max(lp)
                #print(Blocking_m) 
                
                
        return Blocking_m    

    def get_length_m_nomac(self,t,new_t=None):
    #the recursion base case
        if t == new_t: return new_t
                    
        sum_val = 0.0
        length_m_nomac=0
        for i in range(len(self.period)):
            if self.priority[i] <= self.priority[self.p]:
                
                #follows the use case for deriving the length of the priority-level m busy period 
                val=(t + self.j)/self.period[i]  
                
                a= math.ceil(val)
                l  =a * self.TX[i]
                sum_val+= l
        #length_m = B + sum_val
                
        length_m_nomac = self.B + sum_val
            
    #calls itself recursively to reach the base case and then terminates      
        return resp.get_length_m_nomac(self,length_m_nomac, t)

    def get_qd_m_nomac(self,q,w, prev_w=None):
    
    
        if w ==prev_w: return  prev_w
        #initialise blocking messages to be zero
        
        v=0                
        sum_val = 0
        qd = 0
        
        #follows the use case to derive the worst case queuing delay
        #priority_sort=sorted(priority)
        #print(priority_sort)
        for i in range(len(self.period)):
            
            if max(self.priority)== self.p:
                qd = self.B + q * self.TX[i]
                #print(qd)
                
            v=v+1       
                
            if self.priority[i]<self.priority[self.p]:
                
                val = (w + self.j + self.tbit)/ self.period[v-1]
                #print(math.ceil(val))
                sum_val += math.ceil(val) * self.TX[v-1]
                #print("--",sum_val)
                
            
            qd = self.B + q * self.TX[self.p] + sum_val
            
                
        
        return resp.get_qd_m_nomac(q,qd,w) 

    def get_Response_time_nomac(self,Q):
        w=0
        
        response_time,Rt1, RT2=0,0,0
        #to derive the number of instances of the message 
        for q in range(int(Q)):
            init_w = self.B + q * self.TX[self.p]
            
            if q == 0:
                
                prev_inst = resp.get_qd_m_nomac(q,init_w)            
                Rt1= round((prev_inst  + self.TX[self.p]),6)
                    
            elif q > 0:
                w= resp.get_qd_m_nomac(0,self.B) + self.TX[self.p]
                
                new_inst = resp.get_qd_m_nomac(q,w)
                
                RT2 = round(new_inst - q * self.period[self.p] +self.TX[self.p])
                #if Response_Time>Deadline[p]:
                    #break;

                #print("{Message}_{instance} = {resp}ms".format(Message=priority[p],instance=q,resp=round((Response_Time),6))) 
                
            if Rt1 >RT2:
                response_time = Rt1
            else:
                response_time =RT2
        return response_time
#mac

    def get_qd_m_mac(self, cmax,q, w, new_TX, prev_w=None):
    
    
        if w ==prev_w: return  prev_w
        #initialise blocking messages to be zero
        index=0                
        sum_val = 0
        qd = 0
        
        #follows the use case to derive the worst case queuing delay
        for i in range(len(self.period)):
            
            if max(self.priority)== self.p:
                qd = self.B + q * new_TX[i]
                
            index=index+1       
                
            if self.priority[i]< self.priority[self.p]:
                
                val = (w+self.j+self.tbit)/self.period[index-1]
                sum_val += math.ceil(val) * new_TX[index-1] 
                
            qd = self.B + ((q % self.num_frame[self.p]) *cmax[self.p]) + (math.floor(q/self.num_frame[self.p])* new_TX[self.p]) +sum_val
       


        try:
            r =resp.get_qd_m_mac(q,qd,new_TX,w) 
        except Exception:
            r = 0
        return r

    def get_length_m_mac(self,t,new_TX, new_t=None):
        #the recursion base case
    
        if t == new_t: return new_t
        r=0          
        sum_val = 0.0
        length_m=0
        for i in range(len(self.period)):
            
            if self.priority[i] <= self.priority[self.p]:
                
                #follows the use case for deriving the length of the priority-level m busy period 
                val=(t + self.j)/self.period[i]  
                
                a= math.ceil(val)
                l  =a * new_TX[i]
                sum_val+= l 
                #print(sum_val)
            length_m = self.B + sum_val
            
        try:
            r =resp.get_length_m_mac( length_m,new_TX,t)
            
        except Exception:
            r =0
        #calls itself recursively to reach the base case and then terminates      
        return r

    def get_Response_time_mac(self,Q,cmac,cmax,new_TX):
        w=0
        response_time,Rt1, RT2=0,0,0
        #to derive the number of instances of the message 
        for q in range(int(Q)):
            init_w = self.B + q * new_TX[self.p]
            if q == 0:
                prev_inst = resp.get_qd_m_mac(q,new_TX,init_w) 
                    
                Rt1= round((prev_inst - (math.floor(q/self.num_frame[self.p]) *self.period[self.p]) + (math.floor(((q % self.num_frame[self.p])+1))/self.num_frame[self.p]) *cmac[self.p] +((1- math.floor((q %self.num_frame[self.p])+1)/self.num_frame[self.p])*cmax[self.p])),6)
                
                    
            elif q > 0:
                new_q =q-1
                w= resp.get_qd_m_mac(new_q,new_TX,self.B) + new_TX[self.p]
                
                new_inst = resp.get_qd_m_mac(q,new_TX,w)
                
                RT2 = round((new_inst - (math.floor(q/self.num_frame[self.p]) *self.period[self.p]) + (math.floor(((q % self.num_frame[self.p])+1))/self.num_frame[self.p]) *cmac[self.p] +((1- math.floor((q %self.num_frame[self.p])+1)/self.num_frame[self.p])*cmax[self.p])),6)
                
            if Rt1 >RT2:
                response_time = Rt1
            else:
                response_time =RT2
        return response_time

    #periodic
    def get_length_m_periodic(self,rho,pmac_TX,t,new_t=None):
        #the recursion base case
        
        if t == new_t: return new_t
                
        sum_val = 0.0
        length_m=0
        for i in range(len(self.period)):
            if self.priority[i] <= self.priority[self.p]:
                
                #follows the use case for deriving the length of the priority-level m busy period 
                inf_m =(t + self.j) / self.period[i] * self.TX[i]  
                add_frame = ((t + self.j) / rho[i]) * pmac_TX[i]
                
                total_inf = math.ceil(inf_m) + math.ceil(add_frame)
                
                val  = total_inf 
                sum_val += val
                #print(sum_val)
        
        length_m = self.B + sum_val
        #print(length_m)        
        #calls itself recursively to reach the base case and then terminates      
        try:
            r = resp.get_length_m_periodic(rho,pmac_TX, length_m, t)
            
        except Exception:
            r =0
        
        return r

    def get_qd_m_periodic(self,pmac_TX,rho,q,w, prev_w = None):
        #print(q)
        
        if w ==prev_w: return  prev_w
        #initialise blocking messages to be zero
        
        v=0                
        sum_val = 0
        qd = 0
        
        #follows the use case to derive the worst case queuing delay
        for i in range(len(self.period)):
            
            if max(self.priority)== self.p:
                qd = self.B + q * self.TX[self.p]
                
            v=v+1       
            s= self.B + (q * self.TX[self.p])  
            if self.priority[i] < self.priority[self.p]:
                
                inf = ((w + self.j + self.tbit) / self.period[v-1]) *self.TX[v-1]
                add_inf = (((w + self.j + self.tbit) / rho[v-1])) *pmac_TX[v-1] 
                #print(math.ceil(val))
                total_inst = math.ceil(inf) + math.ceil(add_inf) 
                sum_val += total_inst 
                
            qd = s + sum_val   
            #print(qd,priority[p])
        return resp.get_qd_m_periodic(pmac_TX,rho,q,qd,w) 
            

    def get_Response_time_periodic(self,rho,pmac_TX,Q):
        w=0
        Response_Time, Rt1,RT2 =0,0,0
        r=[]
        #to derive the number of instances of the message 
        for q in range(int(Q)):
            init_w = self.B + q * self.TX[self.p]
            
            
            if q == 0:
                prev_inst = resp.get_qd_m_periodic(pmac_TX,rho,q,init_w)
                #print(prev_inst)
                

                Rt1 = round((prev_inst - ((q-math.ceil(q/(rho[self.p]/self.period[self.p])))*self.period[self.p])+self.TX[self.p]),6)
                #if the response time more than the dealine, this will terminat
            elif q > 0:
            
                new_q =q-1
                w= resp.get_qd_m_periodic(pmac_TX,rho,q,self.B) + self.TX[self.p]
                #print("thus",w)
                
                new_inst = resp.get_qd_m_periodic(pmac_TX,rho,q,w)
                
                RT2 = round((new_inst - ((q-math.ceil(q/(rho[self.p]/self.period[self.p])))*self.period[self.p])+self.TX[self.p]),6)
                #print(RT2)
                
                r.append(RT2)

            #print(r)    #print("{Message}_{instance} = {resp}ms".format(Message=priority[p],instance=q,resp=round((Response_Time),6))) 
            if Rt1 >RT2:
                    Response_Time = Rt1
            else:
                Response_Time =RT2    
        return Response_Time    
    '''
    def try_method(bus_speed):
    
        result =[]
        ch=[]
        ext_alpha = math.ceil(4/8) #mac and fv profile 1
        tbit =1/bus_speed
        result1 =[]
        result3=[]
        n_tx = 0
        new_TX = []
        attr_m = respr()
        TX,DLC,period, n= resp.parameters(bus_speed)

        num_frame = [math.ceil((float(d + 4) /8 )) for d in DLC]
        

        ext_alpha = math.ceil(4/8) #mac and fv profile 1
        modul = [4 %8 for i in range(len(DLC))]
        
        #print(cmax)
        modul_mac = [(DLC[i] +4 )%8 for i in range(len(DLC))]
        cmac_mac =[ (55 + 10 *modul_mac[i])*tbit for i in range(len(DLC))]
        cmax = [ (55 + (10 *8))*tbit for i in range(len(DLC))] 
        cmac =[ (55 + 10 *modul[i])*tbit for i in range(len(DLC))]   
        pmac_TX = [(ext_alpha -1)*cmax[i]  + cmac[i] for i in range(len(DLC))]

        for i in range(len(DLC)):
            n_tx = (num_frame[i]-1)*cmax[i] +cmac_mac[i]
            new_TX.append(n_tx)
        

        priority = [i+1 for i in range(n)]
        #print(priority)
        rho= [period[i]*2 for i in range(len(period))]
        #rho= [period[i]  for i in range(len(period))]
        
            

        for p in range(len(priority)):
            #for response_time_with _no mac
                
            B = get_Blocking_m(p,priority,TX)
        
                #print("nothing")
            length_m_nomac = get_length_m_nomac(p,priority, period,TX,B,TX[p])
            Q = math.ceil(length_m_nomac / period[p])   
                    
            result.append(get_Response_time_nomac(p,Q,B, TX,priority,period,tbit))
                
            #for resp with mac
            mac_B = get_Blocking_mac(p,priority,new_TX,cmac,cmax)

            mac_t = new_TX[p]
            length_m = get_length_m_mac(p, priority,  period,new_TX, num_frame, mac_B, mac_t)
            #print(length_m)
            Q2 = math.ceil(length_m / period[p]) * num_frame[p]
            result1.append(get_Response_time_mac(p,Q2,mac_B, new_TX,priority,period,num_frame,tbit))
            
            #periodic mac resp
            
            pmac_b = new_get_Blocking_m(p,priority,pmac_TX,cmac,cmax)
            pmac_t = ext_alpha* pmac_TX[p] + TX[p]
            
            length_m_p = get_length_m_periodic(p,priority,period,rho,TX,pmac_TX,pmac_b,pmac_t)
            
            Q3 = math.ceil(length_m_p /period[p]) + (math.ceil(length_m_p/rho[p]) )
            
            result3.append(get_Response_time_periodic(p,priority,period,tbit,Q3,pmac_b,rho,TX,pmac_TX))
            
            ch.append(length_m)
        return result, result1,result3,period
    '''

