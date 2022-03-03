import os
import csv
import operator
import math


class Response_time:

    def __init__(self,priority, period,TX, num_frame,DLC, pmac_TX,cmac,cmax,tbit):
        self.priority = priority
        self.period = period
        self.TX = TX
        self.num_frame = num_frame
        self.DLC = DLC
        self.pmac_TX = pmac_TX
        self.cmac =cmac
        self.cmax =cmax
        self.tbit =tbit
        
        
    @staticmethod   
    def read_file():
        priority,period,TX,DLC = [],[],[],[]
        bus_speed = 125
        tbit = 1 / float(bus_speed)
        len_message_frame=[]

        CURRENT_DIR = os.path.dirname(__file__)
        file_path = os.path.join(CURRENT_DIR,'satest.csv')
        with open(file_path,'r') as dataset:
            reader = csv.reader(dataset)
            next(reader)
            for row in reader:
                TX.append(round(float((55 + (10 * (int(row[1])))) * tbit),6))
                period.append(int(row[5]))
                priority.append(row[0])
                DLC.append(int(row[1]))
                len_message_frame.append(math.ceil((3 +1)/8)) #profile 1
                
        ext_alpha = math.ceil(4/8) #mac and fv profile 1
        modul = [4 %8 for i in range(len(DLC))]
        cmax = [ (55 + (10 *8))*tbit for i in range(len(DLC))] #Cap(C_Dmax)
        cmac =[ (55 + 10 *modul[i])*tbit for i in range(len(DLC))]   #Cap(C_(A+F))

        pmac_TX = [(ext_alpha -1)*cmax[i]  + cmac[i] for i in range(len(DLC))] #calculate the periodic_mac transmission time
        return priority, period,TX, len_message_frame,DLC, pmac_TX,cmac,cmax,tbit

    #calculate length of the busy period
    def get_length_m_periodic(self,p,rho,B,t,j=0, new_t=None):
        #the recursion base case
        if t == new_t: return new_t
           
        sum_val = 0.0
        length_m=0
        for i in range(len(self.period)):
            if self.priority[i] <= self.priority[p]:
                
                #follows the use case for deriving the length of the priority-level m busy period 
                inf_m =(t + j) / self.period[i] * self.TX[i]  
                add_frame = ((t + j) / rho[i]) * self.pmac_TX[i]
                
                total_inf = math.ceil(inf_m) + math.ceil(add_frame)
                
                val  = total_inf 
                sum_val += val
    
        length_m = B + sum_val 
        #calls itself recursively to reach the base case and then terminates      
        try:
            len_r = self.get_length_m_periodic(p,rho,B,length_m,j, t)
            
        except Exception:
            len_r =0
        
        return len_r

    def new_get_Blocking_m(self,p):
        Blocking_m=0
        lp=[]
        #incase of lower priority messages in transmission
        for m in range(len(self.priority)):
            if max(self.priority) == self.priority[p]:
                Blocking_m=0
            elif self.priority[m] > self.priority[p]:
                lp.append(max(self.pmac_TX[m],self.cmac[m])) #alpha-1 =0 always for profile 1
                Blocking_m =max(lp)
        return Blocking_m     
    #calculates queuing delay
    def get_qd_m_periodic(self,p,rho,B,q,w, prev_w = None, j=0):
    
        if w ==prev_w: return  prev_w
        #initialise blocking messages to be zero
        
        v=0                
        sum_val = 0
        qd = 0
        
        #follows the use case to derive the worst case queuing delay
        for i in range(len(self.period)):
            
            if max(self.priority)==p:
                qd = B + q * self.TX[p]
                
            v=v+1 #nextIndex_holder
            sum= B + (q * self.TX[p])  
            if self.priority[i] < self.priority[p]:
                
                inf = ((w + j + self.tbit) / self.period[v-1]) * self.TX[v-1]
                add_inf = (((w + j + self.tbit) / rho[v-1])) * self.pmac_TX[v-1] #alpha is constant 1 in this case

                total_inst = math.ceil(inf) + math.ceil(add_inf) 
                sum_val += total_inst 
                
            qd = sum + sum_val   
    
        return self.get_qd_m_periodic(p,rho,B,q,qd,w,j) 
            

    def get_Response_time_periodic(self,p,Q,B,rho):
        w=0
        Response_Time, f_resp,l_resp =0,0,0
        r=[]
        #to derive the number of instances of the message 
        for q in range(int(Q)):
            init_w = B + q * self.TX[p]
            if q == 0:
                prev_inst = self.get_qd_m_periodic(p,rho,B,q,init_w)
                f_resp = round((prev_inst - ((q-math.ceil(q/(rho[p]/self.period[p])))*self.period[p])+ max(self.pmac_TX[p],self.TX[p])),6)
                
            elif q > 0:
                new_q =q-1
                w= self.get_qd_m_periodic(p,rho,B,q,B) + self.TX[p]
                new_inst = self.get_qd_m_periodic(p,rho,B,q,w)
                
                l_resp= round((new_inst - ((q-math.ceil(q/(rho[p]/self.period[p])))*self.period[p])+ max(self.TX[p],self.pmac_TX[p])),6)
            if f_resp >l_resp:
                    Response_Time = f_resp
            else:
                Response_Time = l_resp  
        return Response_Time    
    
    def sort_file_to_csv(self,res):
        file_path2 = ""
        with open(file_path2, "w",newline="") as output:
            writer = csv.writer(output)
            for  row in range(len(self.period)):
                writer.writerow([self.priority[row],self.period[row],self.DLC[row],self.TX[row],res[row]])        
        data =csv.reader(open(file_path2), delimiter =',')      
        sort_file = sorted(data, key=operator.itemgetter(0), reverse = False)
        with open(file_path2, "w", newline="") as sort:
            writer =csv.writer(sort)
            writer.writerow(["ID","PERIOD","DLC","TRANSMISSION TIME","RESPONSE TIME"])
            
            writer.writerows(sort_file)    

    def get_rho(self,multiplier):
        rho_message= [self.period[i]*1000 for i in range(len(self.period))] 
        return rho_message

def main():
    val1,val2,val3,val4,val5,val6,val7,val8,val9= Response_time.read_file()
    pmac_resp = Response_time(val1,val2,val3,val4,val5,val6,val7,val8,val9)
    res = []
    rho = pmac_resp.get_rho(1000)

    for p in range(len(pmac_resp.priority)):
        B = pmac_resp.new_get_Blocking_m(p)
        t = pmac_resp.pmac_TX[p]+ pmac_resp.TX[p]
        length_m = pmac_resp.get_length_m_periodic(p,rho,B,t)
        
        Q = math.ceil(length_m /pmac_resp.period[p]) + (math.ceil(length_m /rho[p]) )
    
        res.append(pmac_resp.get_Response_time_periodic(p,Q,B,rho))
    print(res)
             
if __name__ == '__main__':
        main()        
       
     
       
    
    
    
    
    


    
   
        