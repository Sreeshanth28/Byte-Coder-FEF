import json
import os
import random
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from datetime import datetime, timedelta

# Paths to JSON files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMPLOYEES_FILE = os.path.join(BASE_DIR, 'data', 'employee.json')
BNPL_CUSTOMER_FILE = os.path.join(BASE_DIR, 'data', 'bnplcustomer.json')
CARD_FILE = os.path.join(BASE_DIR, 'data', 'cards.json')
CREDIT_HISTORY_FILE = os.path.join(BASE_DIR,'data','credit_history.json')
SALARY_INFO_FILE = os.path.join(BASE_DIR,'data','salaryinfo.json')
SWEET_SHOP_FILE = os.path.join(BASE_DIR,'data','sweetshop.json')
TRANSACTION_FILE = os.path.join(BASE_DIR,'data','transaction.json')
NATWEST_FILE = os.path.join(BASE_DIR,'data','natwest.json')
ETSY_FILE = os.path.join(BASE_DIR,'data','etsy.json')
TRANSACTION_INFO_FILE=os.path.join(BASE_DIR,'data','transaction_info.json')

# All methods Info
# generate_random_card -> Generated random card for the customer just signed up
# Categorize -> Categorizes the customer based on PAN card and the credit history
# get_Employee_Details -> Gets the employee details from sweet shop
########### make_payment -> Makes payment ############
# make_salary_cuttings -> performs the salary cuttings from the customer's account
# update_salary_cuts -> performs the updation of salary cuttings
# modify_AutoPay -> customer can toggle autopay
# add_autoPay_Account
########### make_autopay_payments -> performs autopay payments from the installments of the customer
# customer_self_payment -> handles the payments done by customer himself


# Utility functions to read and write JSON files
def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    
def write_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
 
@csrf_exempt       
def set_Date(request):
    if request.method=='PUT':
        response={}
        body=json.loads(request.body)
        date=body["date"]
        newDate=datetime.strptime(date, "%b %d %Y").date()
        newDate=datetime.strftime(newDate, "%b %d %Y")
        
        #Updating the auto pay salary cuts
        url = request.build_absolute_uri('/updatesalarycuts/')
        resp = requests.get(url, params={'newDate': newDate})
        
        #make autopay payments of customers
        url = request.build_absolute_uri('/makeautopaypayment/')
        resp = requests.get(url, params={'newDate': newDate})
        
        #Identifying late payments
        url = request.build_absolute_uri('/identifylatepayments/')
        respon = requests.get(url, params={'newDate': newDate})
        
        return JsonResponse(response)

# Method to generate Random BNPL CARD
def generate_random_card():
    card_number = " ".join(["".join([str(random.randint(0, 9)) for _ in range(4)]) for _ in range(4)])
    cvv = "".join([str(random.randint(0, 9)) for _ in range(3)])
    expiry_date = f"{random.randint(1, 12):02d}/{random.randint(24, 29):02d}"
    return {
        "cardNumber": card_number,
        "CVV": cvv,
        "expiryDate": expiry_date
    }
    
# Function to find the category of the customer
def categorize(creditHistory,salary):
    latePayments=0
    customerCreditAccounts=creditHistory["CreditHistory"]["CreditAccounts"]
    for creditAccount in customerCreditAccounts:
        for key,value in creditAccount.items():
            if f"{key}"=="OnTimePayments" and f"{value}"=="false" :
                latePayments+=1
    if(latePayments>1):
        return "Neglect"
    elif(latePayments==1):
        return "Considerable"
    elif(salary>="30000"):
        return "Good"
    return "Best"
    

    
    
    
    
# Create your views here.

def home(request):
    # print(request)
    if request.method=="GET":
        return HttpResponse("Hey! You sent GET request for first url")
    elif request.method=="POST":
        # print("Request body is getting printed")
        # print(request.body)
        return HttpResponse("OK")

# Function to handle Login
def login(request):
    if request.method=='GET':
        response={}
        #Getting all bnpl customers
        email=request.GET.get('email')
        loginPassword=request.GET.get('loginPassword')
        allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
        for eachCustomer in allBnplCustomers:
            if eachCustomer["email"]==email:
                if eachCustomer["loginPassword"]==loginPassword:
                    response["succcess"]="yes"
                    response["bnplId"]=eachCustomer["bnplId"]
                    response["email"]=eachCustomer["email"]
                    response["empId"]=eachCustomer["empID"]
                    response["orgId"]=eachCustomer["orgId"]
                    return JsonResponse(response)
                else:
                    response["success"]="no"
                    response["message"]="Password mismatch. Please try again"
                    return JsonResponse(response)
        response["success"]="no"
        response["message"]="Email doesn't exist. Please signup"
        return JsonResponse(response)
    
# Function to create initial user record with email,password,empId,orgid
@csrf_exempt
def create_new_user(request):
    if request.method=='POST':
        response={"response":{}}
        body=body=json.loads(request.body)
        email=body["email"]
        loginPassword=body["loginPassword"]
        empId=body["empId"]
        orgId=body["orgId"]
        
        #Getting all the customer details
        allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
        for eachCustomer in allBnplCustomers:
            if eachCustomer["email"]==email:
                response["response"]="User already exists"
                return JsonResponse(response)
            
        newCustomer={
        "bnplId": "",
        "email":"",
        "loginPassword": "",
        "empID": "",
        "orgId": "",
        "name": "",
        "accountNumber": "",
        "salary": "",
        "isInNoticePeriod": "",
        "address": "",
        "bnplLimit": "",
        "PAN": "",
        "bnplCard": {},
        "paymentPin": "",
        "autoPay": "",
        "autoPayAccount": {}
        }
        newCustomer["email"]=email
        newCustomer["loginPassword"]=loginPassword
        if empId != "" and orgId != "":
            #Fetching the employee details from sweet shop
            url = request.build_absolute_uri('/empdetails/')
            employeeDetailsFromSweetShop = requests.get(url, params={'empID': empId,'orgId':orgId})
            employeeDetailsFromSweetShop=employeeDetailsFromSweetShop.json()
            if employeeDetailsFromSweetShop != {}:
                newCustomer["empID"]=empId
                newCustomer["orgId"]=orgId
                newCustomer["name"]=employeeDetailsFromSweetShop["name"]
                newCustomer["accountNumber"]=employeeDetailsFromSweetShop["accountNumber"]
                newCustomer["salary"]=employeeDetailsFromSweetShop["salary"]
                newCustomer["isInNoticePeriod"]=employeeDetailsFromSweetShop["isInNoticePeriod"]
        response["response"]=newCustomer
        response["success"]="yes"
        #saving all the details
        allBnplCustomers.append(newCustomer)
        write_json(BNPL_CUSTOMER_FILE,allBnplCustomers)
            
        return JsonResponse(response)

#Function to get employee details
def get_Employee_Details(request):
    if request.method=='GET':
        empId = request.GET.get('empID')
        orgId = request.GET.get('orgId')
        allEmployeeDetails=read_json(EMPLOYEES_FILE)
        currentEmployee={}
        for emp in allEmployeeDetails:
            if emp["empID"]==empId and emp["Org"]==orgId:
                currentEmployee=emp
                break

        return JsonResponse(currentEmployee)
    
# Method to send salaries
@csrf_exempt
def sending_salaries(request):
    if request.method=='POST':
        #Getting info from request body
        requestbody=json.loads(request.body)
        sweetShopId=requestbody["sweetShopId"]
        beneficiary=requestbody["beneficiary"]

        #Getting all sweet shop details
        sweetShopInfo=read_json(SWEET_SHOP_FILE)
        currentSweetShopAccountInfo=sweetShopInfo[sweetShopId]
        currentSweetShopAccountNumber=currentSweetShopAccountInfo["accountNumber"]
        currentSweetShopAccountBalance=float(currentSweetShopAccountInfo["accountBalance"])
        
        #Getting all employee account details
        employeeAccounts=read_json(SALARY_INFO_FILE)
        
        #Crediting salaries into beneficiary accounts
        totalSalaryCredited=0
        for each in beneficiary:
            currentEmployeeAccountNumber=each["accountNumber"]
            currentEmployeeSalary=float(each["salary"])
            employeeAccounts[currentEmployeeAccountNumber]=str(float(employeeAccounts[currentEmployeeAccountNumber])+currentEmployeeSalary) 
            totalSalaryCredited+=float(currentEmployeeSalary)
        currentSweetShopAccountBalance=str(currentSweetShopAccountBalance-totalSalaryCredited)
        
        #moving the upcoming into previous
        sweetShopInfo[sweetShopId]["previous"].append(sweetShopInfo[sweetShopId]["upcoming"][0])
        sweetShopInfo[sweetShopId]["upcoming"]=[]
        print(sweetShopInfo[sweetShopId]["upcoming"])
        #Updating json files
        # latestSweetShopInfo={
        #     "accountNumber":currentSweetShopAccountNumber,
        #     "accountBalance":currentSweetShopAccountBalance
        # }
        # sweetShopInfo[sweetShopId]=latestSweetShopInfo
        
        write_json(SALARY_INFO_FILE,employeeAccounts)
        write_json(SWEET_SHOP_FILE,sweetShopInfo)
        
        #Now request is sent to make_salary_cut for cutting the amount after crediting the salaries
        # url = request.build_absolute_uri('/makesalarycuttings/')
        # requests.post(url,data=requestbody)
        return HttpResponse("Salaries Credited")

# method to get BNPL amount limit
#uses Categorize method for categorizing the customer
def get_Bnpl_Limit(request):
    if request.method=="GET":
                    
        currentCustomerPancard=request.GET.get('PAN')
        currentCustomerSalary=request.GET.get('salary')
        # print(type(currentCustomerPancard))
        # print(type(currentCustomerSalary))

        currentCustomerCreditHistory={}
        allCreditHistory=read_json(CREDIT_HISTORY_FILE)
        currentCustomerCreditHistory=allCreditHistory[currentCustomerPancard]    
        
        # Categorizing the customer and deciding the salary
        limit=0
        category=categorize(currentCustomerCreditHistory,currentCustomerSalary)
        
        if category=="Best":
            limit=str(int(float(currentCustomerSalary)*0.5))
        elif category=="Good":
            limit=str(int(float(currentCustomerSalary)*0.4))
        elif category=="Considerable":
            limit=str(int(float(currentCustomerSalary)*0.2))
        response={"limit":limit}
        return JsonResponse(response)
    
# Method to add new customer
# This method is called while user is signing up
@csrf_exempt
def add_new_customer(request):
    if request.method=='POST':
        body=json.loads(request.body)
        email=body["email"]
        loginPassword=body["loginPassword"]
        empId=body["empID"]
        orgId=body["orgId"]
        name=body["name"]
        accountNumber=body["accountNumber"]
        salary=body["salary"]
        isInNoticePeriod=body["isInNoticePeriod"]
        address=body["address"]
        PAN=body["PAN"]
        paymentPin=body["paymentPin"]
        bnplId="".join([str(random.randint(0, 9)) for _ in range(8)])
        # print(bnplId)
        #Checking if employee already registered
        #Getting all bnplcustomers
        allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
        # for eachCustomer in allBnplCustomers:
        #     if eachCustomer["empID"]==empId:
        #         return HttpResponse("Employee already registered")
        # Fetching employee details from sweetshop using empID
        # url = request.build_absolute_uri('/empdetails/')
        # response = requests.get(url, params={'empID': empId})
        # currentEmployee=response.json()
        # currentEmployeePanCard=currentEmployee["PAN"]
        # currentEmployeeSalary=currentEmployee["salary"]
        
        #Getting employee bnpllimit
        url=request.build_absolute_uri('/bnpllimit/')
        response=requests.get(url,params={'PAN':PAN,'salary':salary})
        response=response.json()
        currentEmployeeBnplLimit=response["limit"]
        # print(currentEmployeeBnplLimit)
        #Generatingn new card for customer
        newCardDetails=generate_random_card()
        # print(newCardDetails)
        newCustomer={
                "bnplId": bnplId,
                "email":email,
                "LoginPassword":loginPassword,
                "empID": empId,
                "orgId":orgId,
                "name": name,
                "accountNumber": accountNumber,
                "salary":salary,
                "isInNoticePeriod":isInNoticePeriod,
                "address":address,
                "bnplLimit":currentEmployeeBnplLimit,
                "PAN":PAN,
                "bnplCard":newCardDetails,
                "paymentPin":paymentPin,
                "autoPay": "0",
                "autoPayAccount":{}
            }
        print(newCustomer)
        # print(allBnplCustomers)
        for eachCustomer in allBnplCustomers:
            if eachCustomer["email"]==email:
                eachCustomer["bnplId"]=newCustomer["bnplId"]
                eachCustomer["email"]=newCustomer["email"]
                eachCustomer["LoginPassword"]=newCustomer["LoginPassword"]
                eachCustomer["empID"]=newCustomer["empID"]
                eachCustomer["orgId"]=newCustomer["orgId"]
                eachCustomer["name"]=newCustomer["name"]
                eachCustomer["accountNumber"]=newCustomer["accountNumber"]
                eachCustomer["salary"]=newCustomer["salary"]
                eachCustomer["isInNoticePeriod"]=newCustomer["isInNoticePeriod"]
                eachCustomer["address"]=newCustomer["address"]
                eachCustomer["bnplLimit"]=newCustomer["bnplLimit"]
                eachCustomer["PAN"]=newCustomer["PAN"]
                eachCustomer["bnplCard"]=newCustomer["bnplCard"]
                eachCustomer["paymentPin"]=newCustomer["paymentPin"]
                eachCustomer["autoPay"]=newCustomer["autoPay"]
                eachCustomer["autoPayAccount"]=newCustomer["autoPayAccount"]
                break
    
        #Creating an entry in transaction history
        transactionHistory=read_json(TRANSACTION_INFO_FILE)
        emptyTransactionHistory={
            "history":[],
            "pastTransaction":[]
        }
        transactionHistory[bnplId]=emptyTransactionHistory
        
        #Saving all the files
        write_json(BNPL_CUSTOMER_FILE, allBnplCustomers)
        write_json(TRANSACTION_INFO_FILE,transactionHistory)
        return HttpResponse("New Customer Added")
    
    
#*********************************************************************************************************************
#Function to make payment
@csrf_exempt
def make_payment(request):
    if request.method=='POST':
        #Fetching details from request body
        body=json.loads(request.body)
        cardNumber=body["cardNumber"]
        expiryDate=body["exp"]
        cvv=body["cvv"]
        amount=float(body["amount"])
        duration=int(body["duration"])
        salaryCut=int(body["salaryCut"])
        paymentPin=body["paymentPin"]
        description=body["description"]
        #Validating the card details and the bnpl limit
        currentCustomer={}
        allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
        for eachCustomer in allBnplCustomers:
            if cardNumber==eachCustomer["bnplCard"]["cardNumber"]:
                currentCustomer=eachCustomer
                break
        if currentCustomer=={}:
            return HttpResponse("Card does not exist")
        if currentCustomer["bnplCard"]["expiryDate"]!=expiryDate:
            return HttpResponse("Expiry date mismatch")
        if currentCustomer["bnplCard"]["CVV"]!=cvv:
            return HttpResponse("CVV mismatch")
        if float(currentCustomer["bnplLimit"])<amount:
            return HttpResponse("Amount limit exhausted")
        if currentCustomer["paymentPin"]!=paymentPin:
            return HttpResponse("PIN mismatch. Please check your pin")
        
        #All details are valid. Transaction details are saved into transaction.json
        
        #Creating transaction ID
        transactionId=cvv = "".join([str(random.randint(0, 9)) for _ in range(14)])
        
        #Calculating date of transaction
        transactionDate=datetime.today()
        transactionTime=datetime.now()
        tempDate=transactionDate
        dummyDate=transactionDate
        #Calculating charges for e-commerce
        chargesForEtsy=0
        if amount>5000.00 and amount<10000.00:
            chargesForEtsy=amount*0.05
        elif amount>=10000.00:
            chargesForEtsy=amount*0.07
     
        currentCustomerSalary=float(currentCustomer["salary"])
        currentCustomerSalaryCut=amount*(salaryCut/100)
        amountAfterSalaryCut=amount-currentCustomerSalaryCut   
        #charges applied

        #Computing all the installments from the date of payment
        installments=[]
        
        i=0
        while i<duration:
            dueDate=tempDate+timedelta(30)
            date=dueDate.date().strftime("%b %d %Y")
            amountToPay=amountAfterSalaryCut/duration
            #Id for an installment
            dueId=cvv = "".join([str(random.randint(0, 9)) for _ in range(6)])
            due={
                "installmentId":dueId,
                "dueDate":date,
                "amountToPay":str(amountToPay)
            }
            installments.append(due)
            tempDate=dueDate
            i+=1
        
        #computing the autopay salary cuts from his monthly salary
        salaryCuttings=[]
        i=0
        while i<duration:
            salaryCutDate=dummyDate+timedelta(30)
            salaryCutDateString=salaryCutDate.date().strftime("%b %d %Y")
            amountToCutFromSalary=currentCustomerSalaryCut/duration
            #Id for an installment
            cutId=cvv = "".join([str(random.randint(0, 9)) for _ in range(6)])
            eachSalaryCut={
                "installmentId":cutId,
                "dueDate":salaryCutDateString,
                "amountToPay":str(amountToCutFromSalary)
            }
            salaryCuttings.append(eachSalaryCut)
            dummyDate=salaryCutDate
            i+=1
        #Creating new transaction
        newTransaction={
            "transactionId":transactionId,
            "transactionDate":transactionDate.date().strftime("%b %d %Y"),
            "description":description,
            "amount":str(amount),
            "amountLeft":str(amount),
            "salaryCut":str(salaryCut), 
            "personalPayLeft": str(amountAfterSalaryCut),
            "salaryPayCutLeft": str(currentCustomerSalaryCut),
            "bnplId":currentCustomer["bnplId"],
            "cardNumber":cardNumber,
            "installments":installments,
            "salaryCuttings":salaryCuttings
        }
        # Adding new transaction to database
        currentTransactions=read_json(TRANSACTION_FILE)
        currentTransactions.append(newTransaction)
        write_json(TRANSACTION_FILE,currentTransactions)
        
        #Updating the bnplLimit of the customer
        currentCustomer["bnplLimit"]=str(float(currentCustomer["bnplLimit"])-amount)
        for eachCustomer in allBnplCustomers:
            if eachCustomer["bnplId"]==currentCustomer["bnplId"]:
                eachCustomer=currentCustomer
                break
        write_json(BNPL_CUSTOMER_FILE,allBnplCustomers)
        
        #Decreasing the natwest account balance by amount paid to e-commerce platform on behalf of customer
        natwest=read_json(NATWEST_FILE)
        natwest["totalAmount"]=str(float(natwest["totalAmount"])-amount)
        write_json(NATWEST_FILE,natwest)
        
        #Adding the amount in e-commerce platform account
        etsy=read_json(ETSY_FILE)
        etsy["totalAmount"]=str(float(etsy["totalAmount"])+amount)
        write_json(ETSY_FILE,etsy)
        
        #Deducting the charges from e-commerce platform account
        etsy=read_json(ETSY_FILE)
        etsy["totalAmount"]=str(float(etsy["totalAmount"])-chargesForEtsy)
        write_json(ETSY_FILE,etsy)
        
        
        
        return HttpResponse("Payment successful")

#Function to do salary cuttings from customers
@csrf_exempt
def make_salary_cuttings(request):
    if request.method=='POST':
        
        body=json.loads(request.body)
        currentBeneficiaryOrgid=body["sweetShopId"]
        beneficiary=body["beneficiary"]
        print(beneficiary)
        #Getting all bnplcustomer details
        allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
        
        #Getting all transaction details
        allTransactions=read_json(TRANSACTION_FILE)
        
        #Getting all account details of customers
        allAccountDetails=read_json(SALARY_INFO_FILE)
        
        #Getting natwest account details
        natwest=read_json(NATWEST_FILE)
        
        #Getting transaction info details
        allTransactionInfo=read_json(TRANSACTION_INFO_FILE)
        
        for eachBeneficiary in beneficiary:
            currentBeneficiaryEmpId=eachBeneficiary["empId"]
            currentBeneficiaryAccountNumner=eachBeneficiary["accountNumber"]
            
            #Getting the bnplId from orgId and empId
            currentBeneficiaryBnplId=""
            for eachCustomer in allBnplCustomers:
                if eachCustomer["orgId"]==currentBeneficiaryOrgid and eachCustomer["empID"]==currentBeneficiaryEmpId:
                    currentBeneficiaryBnplId=eachCustomer["bnplId"]
                    break
            
            #Finding all the transactions of the current customer of the bnplId and deductiong the money from the account
            for eachTransaction in allTransactions:
                if eachTransaction["bnplId"]==currentBeneficiaryBnplId:
                    currentTransaction=eachTransaction
                    print(currentTransaction)
                    amountToCut=float(currentTransaction["salaryCuttings"][0]["amountToPay"])
                    #Deductiong the amount from customer's account
                    allAccountDetails[currentBeneficiaryAccountNumner]=str(float(allAccountDetails[currentBeneficiaryAccountNumner])-amountToCut)
                    #Adding the amount to natwest
                    natwest["totalAmount"]=str(float(natwest["totalAmount"])+amountToCut)
                    #Adding the transaction to the salary cuts in the history of customer
                    currentSalaryCut=currentTransaction["salaryCuttings"][0]
                    currentSalaryCut["message"]="Salary cut success"
                    currentSalaryCut["description"]=eachTransaction["description"]
                    salaryCutDate=datetime.today().date().strftime("%b %d %Y")
                    currentSalaryCut["dateOfCut"]=salaryCutDate
                    allTransactionInfo[currentBeneficiaryBnplId]["history"].append(currentSalaryCut)
                    #Deleting the record from the salarycuttings of the customer in his transaction
                    currentTransaction["salaryCuttings"].pop(0)
                    #Updating the remaining cutting amount from salary
                    currentTransaction["salaryPayCutLeft"]=str(float(currentTransaction["salaryPayCutLeft"])-amountToCut)
            
            #Now saving the transaction information and accout details of the customer
            write_json(TRANSACTION_FILE,allTransactions)
            write_json(SALARY_INFO_FILE,allAccountDetails)
            write_json(NATWEST_FILE,natwest)
            write_json(TRANSACTION_INFO_FILE,allTransactionInfo)       
    return HttpResponse("Salary cuts done")

#Function to refactor the salary cuttings
def update_salary_cuts(request):
    if request.method=='GET':
        print("Inside update_salary_cuts")
        #Getting today's date
        todayDate = request.GET.get("newDate")
        todayDate = datetime.strptime(todayDate, "%b %d %Y").date()
        #Getting all transactions
        allTransactions=read_json(TRANSACTION_FILE)
        
        #Getting all transaction history
        allTransactionInfo=read_json(TRANSACTION_INFO_FILE)
        
        #Removing the record of late salary cut and splitting the amount equally to the other splits
        for eachTransaction in allTransactions:
            salaryCuttings=eachTransaction["salaryCuttings"]
            currentTransactionBnplId=eachTransaction["bnplId"]
            if len(salaryCuttings):
                dateOfFirstCut=datetime.strptime(salaryCuttings[0]["dueDate"], "%b %d %Y").date()
                if todayDate>dateOfFirstCut:
                    amountToSplit=float(salaryCuttings[0]["amountToPay"])
                    #Adding to late payments
                    missedSalaryCut=salaryCuttings[0]
                    missedSalaryCut["message"]="Salary cut miss"
                    missedSalaryCut["description"]=eachTransaction["description"]
                    missedSalaryCut["amountAdded"]=str(amountToSplit)
                    
                    n=len(salaryCuttings)
                    salaryCuttings.pop(0)
                    amountToAdd=float(amountToSplit/n)
                    for each in salaryCuttings:
                        each["amountToPay"]=str(float(each["amountToPay"])+amountToAdd)
                    missedSalaryCut["splitCount"]=n
                    allTransactionInfo[currentTransactionBnplId]["history"].append(missedSalaryCut)

                    
        # saving all the files          
        write_json(TRANSACTION_FILE,allTransactions)
        write_json(TRANSACTION_INFO_FILE,allTransactionInfo)           
        return HttpResponse("Updated")
    
    
# Function to verify autoPay
def modify_AutoPay(request):
    if request.method=='GET':
        currentCustomerBnplId=request.GET.get("bnplId")
        currentCustomerAutoPay=request.GET.get("autoPay")
        #Getting all customer details
        allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
        currentCustomerAutoPayAccountDetails={}
        for eachCustomer in allBnplCustomers:
            if eachCustomer["bnplId"]==currentCustomerBnplId:
                eachCustomer["autoPay"]=currentCustomerAutoPay
                currentCustomerAutoPayAccountDetails=eachCustomer["autoPayAccount"]
                break
        #saving the customer details
        write_json(BNPL_CUSTOMER_FILE,allBnplCustomers)
        response={}
        response["autoPayAccount"]=currentCustomerAutoPayAccountDetails
        return JsonResponse(response)

@csrf_exempt    
# Function to add autoPay account
def add_autoPay_Account(request):
    if request.method=='PUT':
        body=json.loads(request.body)
        currentCustomerBnplId=body["bnplId"]
        accountDetails=body["accountDetails"]
        
        #Getting all customer details and adding the autopay account to the bnpl id
        allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
        for eachCustomer in allBnplCustomers:
            if eachCustomer["bnplId"]==currentCustomerBnplId:
               eachCustomer["autoPayAccount"]=accountDetails
               break
        
        #Saving the updated customer info
        write_json(BNPL_CUSTOMER_FILE,allBnplCustomers)
        return HttpResponse("Account details added")
    
# Function for doing autopay for customer payments
def make_autoPay_payments(request):
    print("Inside make_autopay_payments")
    todayDate = request.GET.get("newDate")
    todayDate = datetime.strptime(todayDate, "%b %d %Y").date()
    
    #Fetching all the transactions
    allTransactions=read_json(TRANSACTION_FILE)
    
    #Fetching all the customer details
    allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
    
    #Fetching all account details
    allAccountDetails=read_json(SALARY_INFO_FILE)
    
    #Fetching the natwest account details
    natwest=read_json(NATWEST_FILE)
    
    #Fetching all transaction info details
    allTransactionInfo=read_json(TRANSACTION_INFO_FILE)
    # currentDueDate=datetime.strptime(eachInstallment["dueDate"], "%b %d %Y").date()
    for eachTransaction in allTransactions:
        bnplId=eachTransaction["bnplId"]
        
        for eachCustomer in allBnplCustomers:
            if eachCustomer["bnplId"]==bnplId:
                currentCustomerAutoPay=eachCustomer["autoPay"]
                customerAutoPayAccountNumber=eachCustomer["autoPayAccount"]["accountNumber"] 
                customerAutpPayAccountBalance=allAccountDetails[customerAutoPayAccountNumber]
                break
        
        for eachInstallment in eachTransaction["installments"]:
           currentDueDate=datetime.strptime(eachInstallment["dueDate"], "%b %d %Y").date()
           if currentCustomerAutoPay=="1":
                if currentDueDate==todayDate:
                    if customerAutpPayAccountBalance < eachInstallment["amountToPay"]:
                        #Updating personal pay left in the transaction
                        eachTransaction["personalPayLeft"]=str(float(eachTransaction["personalPayLeft"])+float(eachInstallment["amountToPay"])*0.1)
                        #Adding interest
                        eachInstallment["amountToPay"]=str(float(eachInstallment["amountToPay"])*1.1)
                        #Extending due date
                        eachInstallment["dueDate"]=datetime.strptime(eachInstallment["dueDate"], "%b %d %Y").date()+timedelta(30)
                        eachInstallment["dueDate"]=eachInstallment["dueDate"].strftime("%b %d %Y")
                        #Adding this installment into late installments also
                        lateInstallment=eachInstallment
                        lateInstallment["message"]="Insufficient Balance"
                        lateInstallment["description"]=eachTransaction["description"]
                        allTransactionInfo[bnplId]["history"].append(lateInstallment)
                    else:
                        #Adding the installment into personal in transaction history
                        successfulInstallment=eachInstallment
                        successfulInstallment["message"]="Success"
                        successfulInstallment["date"]=todayDate.strftime("%b %d %Y")
                        successfulInstallment["description"]=eachTransaction["description"]
                        allTransactionInfo[bnplId]["history"].append(successfulInstallment)
                        
                        #Decreasing the autopay account balance of the customer
                        allAccountDetails[customerAutoPayAccountNumber]=str(float(allAccountDetails[customerAutoPayAccountNumber])-float(eachInstallment["amountToPay"]))
                        
                        #Updating personal pay left in the transaction
                        eachTransaction["personalPayLeft"]=str(float(eachTransaction["personalPayLeft"])-float(eachInstallment["amountToPay"]))
                        
                        #Increasing natwest account balance
                        natwest=read_json(NATWEST_FILE)
                        natwest["totalAmount"]=str(float(natwest["totalAmount"])+float(eachInstallment["amountToPay"]))
                        
                        #Deleting the record from the installments
                        eachTransaction["installments"].remove(eachInstallment)
                   
    #Saving all the files
    write_json(TRANSACTION_FILE,allTransactions)
    write_json(BNPL_CUSTOMER_FILE,allBnplCustomers)
    write_json(SALARY_INFO_FILE,allAccountDetails)
    write_json(NATWEST_FILE,natwest)           
    write_json(TRANSACTION_INFO_FILE,allTransactionInfo)
    return HttpResponse("AutoPay Payments Done")

#Function for handling payment done by customer himself
@csrf_exempt
def customer_self_payment(request):
    if request.method=='POST':
        body=json.loads(request.body)
        bnplId=body["bnplId"]
        installmentIds=body["installmentIds"]
        accountNumber=body["accountNumber"]
        
        #Getting all transaction details
        allTransactions=read_json(TRANSACTION_FILE)
        
        #Getting all account details
        allAccountDetails=read_json(SALARY_INFO_FILE)
        
        #Getting natwest details
        natwest=read_json(NATWEST_FILE)
        
        #Getting transaction history details
        allTransactionInfo=read_json(TRANSACTION_INFO_FILE)
        
        # print(allAccountDetails[accountNumber])
        
        for eachInstallmentId in installmentIds:
            for eachTransaction in allTransactions:
                if eachTransaction["bnplId"]==bnplId:
                    for eachInstallment in eachTransaction["installments"]:
                        if eachInstallment["installmentId"]==eachInstallmentId:
                            currentInstallment=eachInstallment
        #                   #Adding the installment in personal in customer history
                            currentInstallment["message"]="Success"
                            currentInstallment["description"]=eachTransaction["description"]
                            currentInstallment["paymentDate"]=datetime.today().date().strftime("%b %d %Y")
                            allTransactionInfo[bnplId]["history"].append(currentInstallment)
                            # #Deleting the record from the late payments if present
                            # for each in allTransactionInfo["history"]:
                            #     if each["installmentId"]==installmentId:
                            #         allTransactionInfo["late"].erase(each)
                            #         break
                            amountToPay=float(eachInstallment["amountToPay"])
                            # if amountToPay < float(allAccountDetails[accountNumber]):
                            #     return HttpResponse("Insufficient Balance")
                            #Deleting the record from the installments
                            eachTransaction["installments"].remove(eachInstallment)
                            
                            #Deducting the amount to pay from the account provided by the customer
                            allAccountDetails[accountNumber]=str(float(allAccountDetails[accountNumber])-amountToPay)
                            #Adding the amount to natwest
                            natwest["totalAmount"]=str(float(natwest["totalAmount"])+amountToPay)
        
        # for eachTransaction in allTransactionDetails:
        #     if str(eachTransaction["bnplId"])==bnplId:
        #         installments=eachTransaction["installments"]
        #         currentInstallment={}
        #         for eachInstallment in installments:
        #             if eachInstallment["installmentId"]==installmentId:
        #                 currentInstallment=eachInstallment
        #                 #Adding the installment in personal in customer history
        #                 currentInstallment["message"]="success"
        #                 currentInstallment["paymentDate"]=datetime.today().date().strftime("%b %d %Y")
        #                 allTransactionInfo[bnplId]["history"].append(currentInstallment)
        #                 # #Deleting the record from the late payments if present
        #                 # for each in allTransactionInfo["history"]:
        #                 #     if each["installmentId"]==installmentId:
        #                 #         allTransactionInfo["late"].erase(each)
        #                 #         break
        #                 amountToPay=float(eachInstallment["amountToPay"])
        #                 if amountToPay < float(allAccountDetails[accountNumber]):
        #                     return HttpResponse("Insufficient Balance")
        #                 #Deleting the record from the installments
        #                 eachTransaction["installments"].remove(eachInstallment)
                        
        #                 #Deducting the amount to pay from the account provided by the customer
        #                 allAccountDetails[accountNumber]=str(float(allAccountDetails[accountNumber])-amountToPay)
        #                 #Adding the amount to natwest
        #                 natwest["totalAmount"]=str(float(natwest["totalAmount"])+amountToPay)
        
        #Saving all the files
        write_json(TRANSACTION_FILE,allTransactions)
        write_json(SALARY_INFO_FILE,allAccountDetails)
        write_json(NATWEST_FILE,natwest)
        write_json(TRANSACTION_INFO_FILE,allTransactionInfo)
        return HttpResponse("OK")
    
# Function to indentify late installments of the customer 
def identify_late_payments(request):
    if request.method=='GET':
        print("inside identify_late_payments")
        todayDate = request.GET.get("newDate")
        todayDate = datetime.strptime(todayDate, "%b %d %Y").date()
        
        # Getting all transaction details
        allTransactions=read_json(TRANSACTION_FILE)
        
        #Getting all history details
        allTransactionInfo=read_json(TRANSACTION_INFO_FILE)
        
        for eachTransaction in allTransactions:
            currentBnplId=eachTransaction["bnplId"]
            for eachInstallment in eachTransaction["installments"]:
                currentDueDate=datetime.strptime(eachInstallment["dueDate"], "%b %d %Y").date()
                if currentDueDate<todayDate:
                    #Add interest and extend due date
                    eachInstallment["dueDate"]=datetime.strptime(eachInstallment["dueDate"], "%b %d %Y").date()+timedelta(30)
                    eachInstallment["dueDate"]=eachInstallment["dueDate"].strftime("%b %d %Y")
                    interest=str(float(eachInstallment["amountToPay"])*0.1)
                    eachInstallment["amountToPay"]=str(float(eachInstallment["amountToPay"])*1.1)
                    #Adding this to late payments of the customer
                    newLatePayment=eachInstallment
                    newLatePayment["message"]="Interest"
                    newLatePayment["description"]=eachTransaction["description"]
                    newLatePayment["interest"]=str(interest)
                    allTransactionInfo[currentBnplId]["history"].append(newLatePayment)
        
        #Saving all the details
        write_json(TRANSACTION_FILE,allTransactions)
        write_json(TRANSACTION_INFO_FILE,allTransactionInfo)
                    
        return HttpResponse("Identified late payments")
    
    
# Function to send the transaction details of the customer
def get_Transaction_Details(request):
    if request.method=='GET':
        currentbnplId=request.GET.get("bnplId")
        response={"allTransactions":[]}
        allTransactionsOfCustomer=[]
        #Getting all transaction details
        allTransactions=read_json(TRANSACTION_FILE)
        
        for eachTransaction in allTransactions:
            if eachTransaction["bnplId"]==currentbnplId:
                allTransactionsOfCustomer.append(eachTransaction)
                 
        response["allTransactions"]=allTransactionsOfCustomer
        return JsonResponse(response)
    
# Function to send all the transaction status of the customer
def get_Transaction_Info(request):
    if request.method=='GET':
        currentBnplid=request.GET.get("bnplId")
        response={}
        
        #Getting al the transaction info details
        allCustomerHistory=read_json(TRANSACTION_INFO_FILE)
        response["success"]="yes"
        response["transactionHistory"]=allCustomerHistory[currentBnplid]
        
        return JsonResponse(response)    

#Function to send bnpl customer details
def get_customer_details(request):
    if request.method=='GET':
        email=request.GET.get("email")
        response={}
        #Getting all the customer details
        allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
        for eachCustomer in allBnplCustomers:
            if eachCustomer["email"]==email:
                response["success"]="yes"
                response["customerInfo"]=eachCustomer
                return JsonResponse(response)
        return JsonResponse(response)
    
# Function to get the latest payment dues
def get_latest_dues(request):
    if request.method=='GET':
        response={"latestDues":[]}
        bnplId=request.GET.get("bnplId")
        allInstallmentsOfCustomer=[]
        
        #Getting all transaction details
        allTransactions=read_json(TRANSACTION_FILE)
        
        #Collecting all installments of a customer
        for eachTransaction in allTransactions:
            if eachTransaction["bnplId"]==bnplId:
                transactionDescription=eachTransaction["description"]
                currentCustomerInstallments=eachTransaction["installments"]
                for eachInstallment in currentCustomerInstallments:
                    currentInstallment=eachInstallment
                    currentInstallment["description"]=transactionDescription
                    allInstallmentsOfCustomer.append(currentInstallment)
        
        
        allInstallmentsOfCustomer=sort_list_by_date(allInstallmentsOfCustomer)
        latestDues=[]
        date=allInstallmentsOfCustomer[0]["dueDate"]
        for eachInstallment in allInstallmentsOfCustomer:
            if eachInstallment["dueDate"]==date:
                latestDues.append(eachInstallment)
        response["latestDues"]=latestDues
        return JsonResponse(response)

def sort_list_by_date(listt):
    
    def get_due_date(obj):
        return datetime.strptime(obj["dueDate"], "%b %d %Y") 
    sorted_list = sorted(listt, key=get_due_date)
    
    return sorted_list


#Function to get all customer details
def get_all_customer_details(request):
    if request.method=='GET':
        response={}
        
        # Getting all customer details
        allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
        
        response["allCustomers"]=allBnplCustomers
        return JsonResponse(response)
    

def get_Customer_details_by_bnplId(request):
    if request.method=='GET':
        bnplId=request.GET.get("bnplId")
        response={}
        #Getting all customer details
        allBnplCustomers=read_json(BNPL_CUSTOMER_FILE)
        for eachCustomer in allBnplCustomers:
            if eachCustomer["bnplId"]==bnplId:
                response["customerInfo"]=eachCustomer
                break
        return JsonResponse(response)
    
#get all employees of a organisation
def get_employess_by_orgId(request):
    if request.method=='GET':
        orgId=request.GET.get("orgId")
        employess=[]
        response={}
        #Getting all employee details
        allEmployees=read_json(EMPLOYEES_FILE)
        
        for eachEmployee in allEmployees:
            if eachEmployee["Org"]==orgId:
                employess.append(eachEmployee)
        response["allEmployees"]=employess
        return JsonResponse(response)
    
def get_organisation_details(request):
    if request.method=='GET':
        orgId=request.GET.get("orgId")
        response={}
        allOrgs=read_json(SWEET_SHOP_FILE)
        response["name"]=allOrgs[orgId]["name"]
        response["accountNumber"]=allOrgs[orgId]["accountNumber"]
        response["accountBalance"]=allOrgs[orgId]["accountBalance"]
        return JsonResponse(response)

@csrf_exempt
def add_to_upcoming(request):
    if request.method=='POST':
        body=json.loads(request.body)
        orgId=body["OrgID"]
        date=body["Date"]
        description=body["Description"] 
        beneficiary=body["beneficiary"]
        amount=body["amount"]
        tranId=body["tranID"]
        
        #Getting all organisation details
        newEntity={}
        newEntity["orgId"]=orgId
        newEntity["Date"]=date
        newEntity["Description"]=description
        newEntity["beneficiary"]=beneficiary
        newEntity["amount"]=amount
        newEntity["tranId"]=tranId
        allOrgs=read_json(SWEET_SHOP_FILE)
        allOrgs[orgId]["upcoming"].append(newEntity)
        #Saving al the details
        write_json(SWEET_SHOP_FILE,allOrgs)
        return HttpResponse("OK")
    
#Get all the organisation information
def get_all_orgs_info(request):
    if request.method=='GET':
        response={"OK":"OK"}
        allOrgsInfo=read_json(SWEET_SHOP_FILE)
        response=allOrgsInfo
        return JsonResponse(response)