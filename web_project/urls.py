"""
URL configuration for web_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from first import views
urlpatterns = [
    path("first/", views.home,name="home"),
    path("login/",views.login,name="login"),
    path("createnewuser/",views.create_new_user,name="create_new_user"),
    path("sendingsalaries/",views.sending_salaries,name="sendingsalaries"),
    path("bnpllimit/",views.get_Bnpl_Limit,name="getBnplLimit"),
    path("empdetails/",views.get_Employee_Details,name="getEmployeeDetailsByEmpID"),
    path("addnewcustomer/",views.add_new_customer,name="add_new_customer"),
    path("makepayment/",views.make_payment,name="make_payment"),
    path("makesalarycuttings/",views.make_salary_cuttings,name="make_salary_cuttings"),
    path("updatesalarycuts/",views.update_salary_cuts,name="update_salary_cuts"),
    path("modifyautopay/",views.modify_AutoPay,name="modify_AutoPay"),
    path("addautopayaccount/",views.add_autoPay_Account,name="add_autoPay_Account"),
    path("makeautopaypayment/",views.make_autoPay_payments,name="make_autoPay_payments"),
    path("customerselfpayment/",views.customer_self_payment,name="customer_self_payment"),
    path("identifylatepayments/",views.identify_late_payments,name="identify_late_payments"),
    path("gettransactiondetails/",views.get_Transaction_Details,name="get_Transaction_Details"),
    path("getcustomerhistory/",views.get_Transaction_Info,name="get_Transaction_Info"),
    path("setdate/",views.set_Date,name="set_Date"),
    path("getcustomerdetails/",views.get_customer_details,name="get_customer_details"),
    path("getlatestdues/",views.get_latest_dues,name="get_latest_dues"),
    path("getallcustomerdetails/",views.get_all_customer_details,name="get_all_customer_details"),
    path("getcustomerdetailsbybnplid/",views.get_Customer_details_by_bnplId,name="get_Customer_details_by_bnplId"),
    path("getemployeedetailsbyorgid/",views.get_employess_by_orgId,name="get_employess_by_orgId"),
    path("getorganisationdetails/",views.get_organisation_details,name="get_organisation_details"),
    path("addtoupcoming/",views.add_to_upcoming,name="add_to_upcoming"),
    path("getallorgdetails/",views.get_all_orgs_info,name="get_all_orgs_info"),
    path("admin/", admin.site.urls),
]
