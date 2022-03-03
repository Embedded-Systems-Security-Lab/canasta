import os
import csv
import operator
import math


class Response_time:
    def __init__(self,priority, period,TX, num_frame, DLC,cmax,cmac):
        self.priority = priority
        self.period = period
        self.TX = TX
        self.num_frame = num_frame
        self.DLC = DLC
        self.cmax =cmax
        self.cmac =cmac
        
        
    @staticmethod   
    def read_file(file_name):
        priority = []
        period=[]
        DLC,TX, nTX,num_frame=[],[],[],[]
        bus_speed = 100
        tbit = 1 / float(bus_speed)
        
        with open(file_name,'r') as dataset:
            reader = csv.reader(dataset)
            next(reader)
            for row in reader:
                #nTX.append(round(float((55 + (10 * (int(row[1])))) * tbit),6)) ##transmission time without mac
                period.append(int(row[2]))
                priority.append(int((row[0]),16))
                DLC.append(int(row[1]))
                num_frame.append(math.ceil((float(row[1]) + 3 +1)/8)) #using the first mac profile
                
        modul = [(DLC[i] + 4) % 8 for i in range(len(DLC))] # mac &fv =4
        #print(cmax)
        cmax = [ (55 + (10 * 8)) * tbit for i in range(len(DLC)) ] #C_Dmax
        cmac =[ (55 + 10 * modul[i]) * tbit for i in range(len(DLC)) ]  #C_(D+A+F)_mod Dmax

        #appends the result to the transmission time of each messages 

        for i in range(len(DLC)):
            n_tx = (num_frame[i]-1) * cmax[i] +cmac[i]
            TX.append(n_tx)

        return priority, period,TX, num_frame, DLC,cmax,cmac,tbit

    #calculates length of the busy period    
    def get_length_m(self,p, B, t, j=0, new_t=None):
        #the recursion base case
        if t == new_t: return new_t
            
        sum_val = 0.0
        length_m=0
        for r in range(len(self.priority)):
       
            if self.priority[r] <= self.priority[p]:
                
                #follows the use case for deriving the length of the priority-level m busy period 
                val=(t + j)/self.period[r] 
                a= math.ceil(val)
                l  =a * self.TX[r] 
                sum_val+= l
                #print(sum_val)
        length_m = B + sum_val
                
        #calls itself recursively to reach the base case and then terminates      
        return self.get_length_m(p,B, length_m,j, t)

    def get_Blocking_m(self,p):
        Blocking_m=0
        lp=[]
        #incase of lower priority messages in transmission
        for m in range(len(self.priority)):
            if max(self.priority) == self.priority[p]:
                Blocking_m=0
            elif self.priority[m] > self.priority[p]:
                lp.append(max(self.cmac[m],(self.num_frame[m]-1)* self.cmax[m]))
                Blocking_m= max(lp)

        return Blocking_m

    def get_qd_m(self,p, tbit, B, q, w, prev_w=None, j=0):
        
        
        if w ==prev_w: return  prev_w
        #initialise blocking messages to be zero
        
        v=0                
        sum_val = 0
        qd = 0
        
        #follows the use case to derive the worst case queuing delay
        
        for r in range(len(self.period)):
            
            if max(self.priority)==p:
                qd = B + q * self.TX[r]
                
            v=v+1       
                
            if self.priority[r]< self.priority[p]:
                
                val = (w+j+tbit) / self.period[v-1]
                #print(math.ceil(val))
                sum_val += math.ceil(val) * self.TX[v-1] 
                
            qd = B + ((q % self.num_frame[p]) *self.cmax[p]) + (math.floor(q/self.num_frame[p])* self.TX[p]) +sum_val
        
        return self.get_qd_m(p,tbit,B,q,qd,w,j) 
            

    def get_Response_time(self,p,Q,B,tbit):
        w=0
        Response_Time =0
        r=[]
        #to derive the number of instances of the message 
        
        
        for q in range(int(Q)):
            init_w = B + math.floor(q/self.num_frame[p]) * self.TX[p]
            
            if q == 0:
                prev_inst = self.get_qd_m(p,tbit,B,q,init_w)
                #print(prev_inst)
                
                
                Response_Time = round((prev_inst - (math.floor(q/self.num_frame[p]) *self.period[p]) + (math.floor(((q %self.num_frame[p])+1))/self.num_frame[p]) *self.cmac[p] +((1- math.floor((q %self.num_frame[p])+1)/self.num_frame[p])*self.cmax[p])),6)
                    
            elif q > 0:
                newq=q-1
                w= self.get_qd_m(p,tbit,B,newq,B) + self.TX[p]
                
                
                
                new_inst =self.get_qd_m(p,tbit,B,q,w)
                #print("t",new_inst)
                
                
                #print(cmac[p])
            
                Response_Time = round((new_inst - (math.floor(q/self.num_frame[p]) *self.period[p]) + (math.floor(((q %self.num_frame[p])+1))/self.num_frame[p]) *self.cmac[p] +((1- math.floor((q %self.num_frame[p])+1)/self.num_frame[p])*self.cmax[p])),6)
            
             
        return Response_Time
    #the code works whether the file is sorted according to the priortiy or not,this method sorts it to a csv file 
    def sort_file_to_csv(self,res):
        CURRENT_DIR = os.path.dirname(__file__)
        file_path2 = os.path.join(CURRENT_DIR,'file_test_result.csv')
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
        
        
def main():
    
    result=[]
    CURRENT_DIR = os.path.dirname(__file__)
    file_path = os.path.join(CURRENT_DIR,'File_test.csv')

    val1,val2,val3,val4,val5,val6,val7,tbit= Response_time.read_file(file_path)
   
    resp = Response_time(val1,val2,val3,val4,val5,val6,val7)
   
    for p in range(len(resp.priority)):
        
        B = resp.get_Blocking_m(p)
        t = resp.num_frame[p] * resp.TX[p]
        length_m = resp.get_length_m(p, B, t)
        
    
        Q = math.ceil(length_m /resp.period[p]) + (math.ceil(length_m /resp.period[p]) * resp.num_frame[p])
        
        result.append(resp.get_Response_time(p,Q,B,tbit))
        
    #print(result)
    #sort_file_to_csv(priority,period,DLC,TX,result)   
           
if __name__ == '__main__':
        main()        
       
     
       
    
    
    
    
    


    
   
        