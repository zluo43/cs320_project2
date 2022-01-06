# project: p2
# submitter: zluo43
#partner: none
#hours: 72




from io import TextIOWrapper
from zipfile import ZipFile
import json
import csv

#ZippedCSVReader Class
class ZippedCSVReader():
    def __init__(self,path):
        self.path = path
        self.paths = []
        self.l=[]
      
        with ZipFile(path) as zf:
            for info in zf.infolist():
                self.paths.append(info.filename)
    
    def __str__(self):
        return '{}'.format(self.paths)
    

        
    def load_json(self,file):
            with ZipFile(self.path,'r') as zf:
                with zf.open(file,'r') as f:
                    j_read = json.loads(f.read()) 
            return j_read

    def rows(self,file = None):
        #l=[]
        if file is None:  
        #find all csv files 
            self.l=[]
            for file in self.paths:
                        with ZipFile(self.path) as zf:
                            if file.endswith('.csv'):        
                                with zf.open(file,'r') as f:
                                    tio = csv.DictReader(TextIOWrapper(f))
                                    for row in tio:
                                        self.l.append(row)
            #return self.l
            return json.loads(json.dumps(self.l))
        
        else:
            self.l=[]
            with ZipFile(self.path) as zf:
                        if file.endswith('.csv'):        
                            with zf.open(file,'r') as f:
                                tio = csv.DictReader(TextIOWrapper(f))
                                for row in tio:
                                    self.l.append(row)
            #return self.l
            return json.loads(json.dumps(self.l))     #get rid of ordered dict
     
        

#Loan Class
class Loan:
    def __init__(self, amount, purpose, race, income, decision):
        self.d={}
        self.d['amount']=self.amount=amount
        self.d['purpose']=self.purpose=purpose
        self.d['race']=self.race=race
        self.d['income']=self.income=income
        self.d['decision']=self.decision=decision

    def __repr__(self):\
        #return 'Loan [{},{},{},{},{}]'.format(self.amount,\'self.purpose\',\'self.race\',\'self.income\',\'self.decision\')
        #not sure why wouldn't work 
        return f'Loan({self.amount}, \'{self.purpose}\', \'{self.race}\', {self.income}, \'{self.decision}\')'   #escape spcial character
     
    
          
    def __getitem__(self, lookup):
        val=self.d.get(lookup)
        if lookup in self.d.values():
            return 1
        elif lookup in self.d:
            return val
        else:
            return 0
            


            
#Get bank names
reader = ZippedCSVReader('loans.zip')


def get_bank_names(reader):
    l=[]
    for i in reader.rows():
        l.append(i.get('agency_abbr'))
    return sorted(set(l)) # using set() to remove duplicated from list  (internet)
 
names = get_bank_names(reader) # should be sorted alphabetically
names



class Bank:
    def __init__(self,name=None,reader=None):
        self.name=name
        self.row=reader.rows()      #reader=zippedreader(sv)
    
    

       
        
        
        
    
    
    def loans(self):
        emp_l=[]
        if self.name is not None:
            for i in self.row:
                #print (i)
                #break
                if self.name==i.get('agency_abbr'):
                    am=int(i.get('loan_amount_000s') if str(i.get('loan_amount_000s')).strip() !='' else 0)
                    pur=i.get('loan_purpose_name')
                    ra=i.get('applicant_race_name_1')
                    inc=int(i.get('applicant_income_000s') if str(i.get('applicant_income_000s')).strip() != '' else 0)
                    deci= 'approve' if i.get('actiona_taken')=='1' else 'deny'     
                    info=Loan(am,pur,ra,inc,deci)
                    emp_l.append(info)
                        
            return emp_l
        
        else:
            for i in self.row:
                am=int(i.get('loan_amount_000s') if str(i.get('loan_amount_000s')).strip() !='' else 0)
                pur=i.get('loan_purpose_name')
                ra=i.get('applicant_race_name_1')
                inc=int(i.get('applicant_income_000s') if str(i.get('applicant_income_000s')).strip() != '' else 0)
                deci= 'approve' if i.get('actiona_taken')=='1' else 'deny'     
                info=Loan(am,pur,ra,inc,deci)
                emp_l.append(info)
            return emp_l

        
#SimplePredictor

class SimplePredictor:
    def __init__(self):
        self.approve_count = 0
        self.deny_count = 0
        
    def predict(self, loan):
        if isinstance(loan,Loan):
            p= loan["purpose"]
            if p== 'Refinancing':
                self.approve_count += 1
                return True
            else: 
                self.deny_count += 1
                return False
       
        
    def get_approved(self):
        return self.approve_count

    def get_denied(self):
        return self.deny_count

    
    
#DTree Class

class DTree(SimplePredictor):
    def __init__(self, nodes):
         # TODO: call parent constructor
        super().__init__() #call the correct next parent class function in the Method Resolution Order (MRO)
        # a dict with keys: field, threshold, left, right
        # left and right, if set, refer to similar dicts
        self.root = nodes

    def dump(self, node=None, indent=0):
        if node == None:
            node = self.root
        if node["field"] == "class":
            line = "class=" + str(node["threshold"])
        else:
            line = node["field"] + " <= " + str(node["threshold"])
        print("  " * indent + line)
        if node["left"] != None:
            self.dump(node["left"], indent + 1)
        if node["right"] != None:
            self.dump(node["right"], indent + 1)
            
    def node_count(self,nodes = None):
        if nodes != None:
            if nodes["left"] == None:
                return 1
            elif nodes["right"] == None:
                return 1
            else:
                return self.node_count(nodes["left"]) + self.node_count(nodes["right"]) + 1
        else:
            return self.node_count(self.root)
    
    def predict(self,loan,tree = None):
        
        if tree == None:
            tree = self.root
            
        if tree['field'] == 'class':
            if tree['threshold'] == 1:
                self.approve_count += 1
                return True

            else:
                self.deny_count += 1
                return False
        
        if loan[tree['field']] <= tree['threshold']:
            return self.predict(loan,tree['left'])
        else:
            return self.predict(loan,tree['right'])         
        
#Bias Testing



def bias_test(bank, predictor, race_override):
    same=0
    diff=0
    for i in bank.loans():    # use bank to iterate over loans with loans
        prediction=predictor.predict(i)
#         amount=i.amount
        
#         purpose = i.purpose
       
#         income = i.income, 
#         decision = i.decision
#         race = race_override 

# modify the loan, changing the race of applicant to race_override
        
#         loan_mod= Loan(amount,purpose,race,income,decision)


#????why above won't work??? I have to put them in the same parenthesis which looks too crowded??
       
        loan_mod=Loan(amount=i.amount,purpose=i.purpose,race=race_override,income=loan.income,decision=loan.decision)
        
        prediction1=predictor.predict(loan_mod)
        
        if prediction!=prediction1:
            diff+=1
            
        else:
            same+=1
    
    return    (diff/(diff+same))*100
            
        
    # at the end, return the percentage of cases where the predictor gave a different result after the race was changed
                                                 

    