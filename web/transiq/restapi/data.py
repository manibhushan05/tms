from django.contrib.auth.models import User
from django.db.models import Q

from employee.models import Employee
from fileupload.models import PODFile
from fms.models import MobileAppVersions
from restapi.helper_api import check_booking_status, create_new_booking_status, update_booking_status
from restapi.models import UserCategory, EmployeeRoles, TaskDashboardFunctionalities, EmployeeRolesMapping, \
    EmployeeRolesFunctionalityMapping, BookingStatuses, BookingStatusChain, BookingStatusesMapping
import pandas as pd
from datetime import datetime, timedelta

from restapi.utils import get_or_none
from team.models import ManualBooking, Invoice


def update_user_category():
    if not UserCategory.objects.filter(category='customer'):
        UserCategory.objects.create(category='customer')
    if not UserCategory.objects.filter(category='employee'):
        UserCategory.objects.create(category='employee')
    if not UserCategory.objects.filter(category='supplier'):
        UserCategory.objects.create(category='supplier')
    if not UserCategory.objects.filter(category='broker'):
        UserCategory.objects.filter(category='broker')


def update_employee_roles():
    if not EmployeeRoles.objects.filter(role='office_data_entry'):
        EmployeeRoles.objects.create(role='office_data_entry')
    if not EmployeeRoles.objects.filter(role='ops_executive'):
        EmployeeRoles.objects.create(role='ops_executive')
    if not EmployeeRoles.objects.filter(role='accounts_payable'):
        EmployeeRoles.objects.create(role='accounts_payable')
    if not EmployeeRoles.objects.filter(role='accounts_receivable'):
        EmployeeRoles.objects.create(role='accounts_receivable')
    if not EmployeeRoles.objects.filter(role='sales'):
        EmployeeRoles.objects.create(role='sales')
    if not EmployeeRoles.objects.filter(role='traffic'):
        EmployeeRoles.objects.create(role='traffic')
    if not EmployeeRoles.objects.filter(role='city_head'):
        EmployeeRoles.objects.create(role='city_head')
    if not EmployeeRoles.objects.filter(role='management'):
        EmployeeRoles.objects.create(role='management')
    if not EmployeeRoles.objects.filter(role='tech'):
        EmployeeRoles.objects.create(role='tech')


def update_td_functionalities():
    if not TaskDashboardFunctionalities.objects.filter(functionality='new_inquiry'):
        TaskDashboardFunctionalities.objects.create(functionality='new_inquiry')
    if not TaskDashboardFunctionalities.objects.filter(functionality='customer_inquiries'):
        TaskDashboardFunctionalities.objects.create(functionality='customer_inquiries')
    if not TaskDashboardFunctionalities.objects.filter(functionality='open_inquiries'):
        TaskDashboardFunctionalities.objects.create(functionality='open_inquiries')
    if not TaskDashboardFunctionalities.objects.filter(functionality='my_inquiries'):
        TaskDashboardFunctionalities.objects.create(functionality='my_inquiries')
    if not TaskDashboardFunctionalities.objects.filter(functionality='pending_payments'):
        TaskDashboardFunctionalities.objects.create(functionality='pending_payments')
    if not TaskDashboardFunctionalities.objects.filter(functionality='pending_lr'):
        TaskDashboardFunctionalities.objects.create(functionality='pending_lr')
    if not TaskDashboardFunctionalities.objects.filter(functionality='in_transit'):
        TaskDashboardFunctionalities.objects.create(functionality='in_transit')
    if not TaskDashboardFunctionalities.objects.filter(functionality='invoice_confirmation'):
        TaskDashboardFunctionalities.objects.create(functionality='invoice_confirmation')
    if not TaskDashboardFunctionalities.objects.filter(functionality='delivered'):
        TaskDashboardFunctionalities.objects.create(functionality='delivered')
    if not TaskDashboardFunctionalities.objects.filter(functionality='confirm_booking'):
        TaskDashboardFunctionalities.objects.create(functionality='confirm_booking')
    if not TaskDashboardFunctionalities.objects.filter(functionality='lr_generation'):
        TaskDashboardFunctionalities.objects.create(functionality='lr_generation')
    if not TaskDashboardFunctionalities.objects.filter(functionality='pay_advance'):
        TaskDashboardFunctionalities.objects.create(functionality='pay_advance')
    if not TaskDashboardFunctionalities.objects.filter(functionality='pay_balance'):
        TaskDashboardFunctionalities.objects.create(functionality='pay_balance')
    if not TaskDashboardFunctionalities.objects.filter(functionality='send_invoice'):
        TaskDashboardFunctionalities.objects.create(functionality='send_invoice')
    if not TaskDashboardFunctionalities.objects.filter(functionality='verify_pod'):
        TaskDashboardFunctionalities.objects.create(functionality='verify_pod')
    if not TaskDashboardFunctionalities.objects.filter(functionality='raise_invoice'):
        TaskDashboardFunctionalities.objects.create(functionality='raise_invoice')
    if not TaskDashboardFunctionalities.objects.filter(functionality='confirm_invoice'):
        TaskDashboardFunctionalities.objects.create(functionality='confirm_invoice')
    if not TaskDashboardFunctionalities.objects.filter(functionality='inward_entry'):
        TaskDashboardFunctionalities.objects.create(functionality='inward_entry')
    if not TaskDashboardFunctionalities.objects.filter(functionality='process_payments'):
        TaskDashboardFunctionalities.objects.create(functionality='process_payments')
    if not TaskDashboardFunctionalities.objects.filter(functionality='reconcile'):
        TaskDashboardFunctionalities.objects.create(functionality='reconcile')


def update_employee_roles_mapping():
    # EmployeeRolesMapping.objects.all().delete()
    df = pd.read_excel('/Users/aaho/Downloads/Employee Role Mapping.xlsx')
    df = df.fillna('')
    for i, row in df.iterrows():
        if row['Emp ID']:
            employee = Employee.objects.get(id=row['Emp ID'])
            if row['Role 1']:
                emp_role = EmployeeRoles.objects.get(role=row['Role 1'])
                if not EmployeeRolesMapping.objects.filter(employee=employee, employee_role=emp_role,
                                                           employee_status='active'):
                    EmployeeRolesMapping.objects.create(employee=employee, employee_role=emp_role,
                                                        employee_status='active')
            if row['Role 2']:
                emp_role = EmployeeRoles.objects.get(role=row['Role 2'])
                if not EmployeeRolesMapping.objects.filter(employee=employee, employee_role=emp_role,
                                                           employee_status='active'):
                    EmployeeRolesMapping.objects.create(employee=employee, employee_role=emp_role,
                                                        employee_status='active')
            if row['Role 3']:
                emp_role = EmployeeRoles.objects.get(role=row['Role 3'])
                if not EmployeeRolesMapping.objects.filter(employee=employee, employee_role=emp_role,
                                                           employee_status='active'):
                    EmployeeRolesMapping.objects.create(employee=employee, employee_role=emp_role,
                                                        employee_status='active')


def update_employee_roles_functionalities_mapping():
    # EmployeeRolesFunctionalityMapping.objects.all().delete()
    emp_role_sales = EmployeeRoles.objects.get(role='sales')
    emp_role_traffic = EmployeeRoles.objects.get(role='traffic')
    emp_role_ops = EmployeeRoles.objects.get(role='ops_executive')
    emp_role_city_head = EmployeeRoles.objects.get(role='city_head')
    emp_role_management = EmployeeRoles.objects.get(role='management')
    emp_role_tech = EmployeeRoles.objects.get(role='tech')
    emp_role_ode = EmployeeRoles.objects.get(role='office_data_entry')
    emp_role_accounts_payable = EmployeeRoles.objects.get(role='accounts_payable')
    emp_role_accounts_receivable = EmployeeRoles.objects.get(role='accounts_receivable')

    td_new_inquiry = TaskDashboardFunctionalities.objects.get(functionality='new_inquiry')
    td_customer_inquiries = TaskDashboardFunctionalities.objects.get(functionality='customer_inquiries')
    td_open_inquiries = TaskDashboardFunctionalities.objects.get(functionality='open_inquiries')
    td_my_inquiries = TaskDashboardFunctionalities.objects.get(functionality='my_inquiries')
    td_pending_payments = TaskDashboardFunctionalities.objects.get(functionality='pending_payments')
    td_pending_lr = TaskDashboardFunctionalities.objects.get(functionality='pending_lr')
    td_in_transit = TaskDashboardFunctionalities.objects.get(functionality='in_transit')
    td_invoice_confirmation = TaskDashboardFunctionalities.objects.get(functionality='invoice_confirmation')
    td_delivered = TaskDashboardFunctionalities.objects.get(functionality='delivered')
    td_confirm_booking = TaskDashboardFunctionalities.objects.get(functionality='confirm_booking')
    td_lr_generation = TaskDashboardFunctionalities.objects.get(functionality='lr_generation')
    td_pay_advance = TaskDashboardFunctionalities.objects.get(functionality='pay_advance')
    td_pay_balance = TaskDashboardFunctionalities.objects.get(functionality='pay_balance')
    td_send_invoice = TaskDashboardFunctionalities.objects.get(functionality='send_invoice')
    td_verify_pod = TaskDashboardFunctionalities.objects.get(functionality='verify_pod')
    td_raise_invoice = TaskDashboardFunctionalities.objects.get(functionality='raise_invoice')
    td_confirm_invoice = TaskDashboardFunctionalities.objects.get(functionality='confirm_invoice')
    td_inward_entry = TaskDashboardFunctionalities.objects.get(functionality='inward_entry')
    td_process_payments = TaskDashboardFunctionalities.objects.get(functionality='process_payments')
    td_reconcile = TaskDashboardFunctionalities.objects.get(functionality='reconcile')

    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_sales,
                                                            td_functionality=td_new_inquiry,
                                                            caption='New Inquiry'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_sales, td_functionality=td_new_inquiry,
                                                         caption='New Inquiry')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_sales,
                                                            td_functionality=td_customer_inquiries,
                                                            caption='Customer Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_sales,
                                                         td_functionality=td_customer_inquiries,
                                                         caption='Customer Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_sales,
                                                            td_functionality=td_my_inquiries,
                                                            caption='My Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_sales,
                                                         td_functionality=td_my_inquiries,
                                                         caption='My Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_sales,
                                                            td_functionality=td_pending_payments,
                                                            caption='Pending Payment'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_sales,
                                                         td_functionality=td_pending_payments,
                                                         caption='Pending Payment')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_sales,
                                                            td_functionality=td_pending_lr,
                                                            caption='Pending LR'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_sales,
                                                         td_functionality=td_pending_lr,
                                                         caption='Pending LR')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_sales,
                                                            td_functionality=td_in_transit,
                                                            caption='In Transit'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_sales,
                                                         td_functionality=td_in_transit,
                                                         caption='In Transit')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_sales,
                                                            td_functionality=td_invoice_confirmation,
                                                            caption='Invoice Confirmation'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_sales,
                                                         td_functionality=td_invoice_confirmation,
                                                         caption='Invoice Confirmation')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_sales,
                                                            td_functionality=td_delivered,
                                                            caption='Delivered'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_sales,
                                                         td_functionality=td_delivered,
                                                         caption='Delivered')

    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_traffic,
                                                            td_functionality=td_open_inquiries,
                                                            caption='Open Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_traffic,
                                                         td_functionality=td_open_inquiries,
                                                         caption='Open Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_traffic,
                                                            td_functionality=td_in_transit,
                                                            caption='In Transit'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_traffic,
                                                         td_functionality=td_in_transit,
                                                         caption='In Transit')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_traffic,
                                                            td_functionality=td_pending_lr,
                                                            caption='Pending LR'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_traffic,
                                                         td_functionality=td_pending_lr,
                                                         caption='Pending LR')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_traffic,
                                                            td_functionality=td_delivered,
                                                            caption='Delivered'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_traffic,
                                                         td_functionality=td_delivered,
                                                         caption='Delivered')

    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_ops,
                                                            td_functionality=td_delivered,
                                                            caption='Delivered'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_ops,
                                                         td_functionality=td_delivered,
                                                         caption='Delivered')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_ops,
                                                            td_functionality=td_in_transit,
                                                            caption='In Transit'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_ops,
                                                         td_functionality=td_in_transit,
                                                         caption='In Transit')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_ops, td_functionality=td_pending_lr,
                                                            caption='Pending LR'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_ops, td_functionality=td_pending_lr,
                                                         caption='Pending LR')

    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_city_head,
                                                            td_functionality=td_new_inquiry,
                                                            caption='New Inquiry'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_city_head,
                                                         td_functionality=td_new_inquiry,
                                                         caption='New Inquiry')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_city_head,
                                                            td_functionality=td_customer_inquiries,
                                                            caption='Customer Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_city_head,
                                                         td_functionality=td_customer_inquiries,
                                                         caption='Customer Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_city_head,
                                                            td_functionality=td_my_inquiries,
                                                            caption='My Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_city_head,
                                                         td_functionality=td_my_inquiries,
                                                         caption='My Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_city_head,
                                                            td_functionality=td_pending_payments,
                                                            caption='Pending Payment'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_city_head,
                                                         td_functionality=td_pending_payments,
                                                         caption='Pending Payment')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_city_head,
                                                            td_functionality=td_pending_lr,
                                                            caption='Pending LR'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_city_head,
                                                         td_functionality=td_pending_lr,
                                                         caption='Pending LR')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_city_head,
                                                            td_functionality=td_in_transit,
                                                            caption='In Transit'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_city_head,
                                                         td_functionality=td_in_transit,
                                                         caption='In Transit')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_city_head,
                                                            td_functionality=td_invoice_confirmation,
                                                            caption='Invoice Confirmation'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_city_head,
                                                         td_functionality=td_invoice_confirmation,
                                                         caption='Invoice Confirmation')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_city_head,
                                                            td_functionality=td_delivered,
                                                            caption='Delivered'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_city_head,
                                                         td_functionality=td_delivered,
                                                         caption='Delivered')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_city_head,
                                                            td_functionality=td_open_inquiries,
                                                            caption='Open Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_city_head,
                                                         td_functionality=td_open_inquiries,
                                                         caption='Open Inquiries')

    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_new_inquiry,
                                                            caption='New Inquiry'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_new_inquiry,
                                                         caption='New Inquiry')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_customer_inquiries,
                                                            caption='Customer Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_customer_inquiries,
                                                         caption='Customer Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_my_inquiries,
                                                            caption='My Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_my_inquiries,
                                                         caption='My Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_pending_payments,
                                                            caption='Pending Payment'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_pending_payments,
                                                         caption='Pending Payment')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_pending_lr,
                                                            caption='Pending LR'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_pending_lr,
                                                         caption='Pending LR')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_in_transit,
                                                            caption='In Transit'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_in_transit,
                                                         caption='In Transit')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_invoice_confirmation,
                                                            caption='Invoice Confirmation'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_invoice_confirmation,
                                                         caption='Invoice Confirmation')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_delivered,
                                                            caption='Delivered'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_delivered,
                                                         caption='Delivered')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_open_inquiries,
                                                            caption='Open Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_open_inquiries,
                                                         caption='Open Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_confirm_booking,
                                                            caption='New Booking'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_confirm_booking,
                                                         caption='New Booking')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_lr_generation,
                                                            caption='Generate LR'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_lr_generation,
                                                         caption='Generate LR')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_pay_advance,
                                                            caption='Pay Advance'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_pay_advance,
                                                         caption='Pay Advance')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_pay_balance,
                                                            caption='Pay Balance'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_pay_balance,
                                                         caption='Pay Balance')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_send_invoice,
                                                            caption='Send Invoice'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_send_invoice,
                                                         caption='Send Invoice')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_verify_pod,
                                                            caption='Verify PoD'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_verify_pod,
                                                         caption='Verify PoD')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_raise_invoice,
                                                            caption='Raise Invoice'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_raise_invoice,
                                                         caption='Raise Invoice')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_confirm_invoice,
                                                            caption='Confirm Invoice'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_confirm_invoice,
                                                         caption='Confirm Invoice')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_inward_entry,
                                                            caption='Inward Entry'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_inward_entry,
                                                         caption='Inward Entry')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_process_payments,
                                                            caption='Process Payment'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_process_payments,
                                                         caption='Process Payment')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_management,
                                                            td_functionality=td_reconcile,
                                                            caption='Reconcile'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_management,
                                                         td_functionality=td_reconcile,
                                                         caption='Reconcile')

    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_new_inquiry,
                                                            caption='New Inquiry'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_new_inquiry,
                                                         caption='New Inquiry')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_customer_inquiries,
                                                            caption='Customer Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_customer_inquiries,
                                                         caption='Customer Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_my_inquiries,
                                                            caption='My Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_my_inquiries,
                                                         caption='My Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_pending_payments,
                                                            caption='Pending Payment'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_pending_payments,
                                                         caption='Pending Payment')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_pending_lr,
                                                            caption='Pending LR'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_pending_lr,
                                                         caption='Pending LR')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_in_transit,
                                                            caption='In Transit'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_in_transit,
                                                         caption='In Transit')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_invoice_confirmation,
                                                            caption='Invoice Confirmation'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_invoice_confirmation,
                                                         caption='Invoice Confirmation')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_delivered,
                                                            caption='Delivered'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_delivered,
                                                         caption='Delivered')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_open_inquiries,
                                                            caption='Open Inquiries'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_open_inquiries,
                                                         caption='Open Inquiries')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_confirm_booking,
                                                            caption='New Booking'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_confirm_booking,
                                                         caption='New Booking')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_lr_generation,
                                                            caption='Generate LR'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_lr_generation,
                                                         caption='Generate LR')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_pay_advance,
                                                            caption='Pay Advance'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_pay_advance,
                                                         caption='Pay Advance')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_pay_balance,
                                                            caption='Pay Balance'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_pay_balance,
                                                         caption='Pay Balance')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_send_invoice,
                                                            caption='Send Invoice'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_send_invoice,
                                                         caption='Send Invoice')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_verify_pod,
                                                            caption='Verify PoD'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_verify_pod,
                                                         caption='Verify PoD')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_raise_invoice,
                                                            caption='Raise Invoice'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_raise_invoice,
                                                         caption='Raise Invoice')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_confirm_invoice,
                                                            caption='Confirm Invoice'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_confirm_invoice,
                                                         caption='Confirm Invoice')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_inward_entry,
                                                            caption='Inward Entry'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_inward_entry,
                                                         caption='Inward Entry')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_process_payments,
                                                            caption='Process Payment'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_process_payments,
                                                         caption='Process Payment')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_tech,
                                                            td_functionality=td_reconcile,
                                                            caption='Reconcile'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_tech,
                                                         td_functionality=td_reconcile,
                                                         caption='Reconcile')

    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_ode,
                                                            td_functionality=td_confirm_booking,
                                                            caption='New Booking'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_ode,
                                                         td_functionality=td_confirm_booking,
                                                         caption='New Booking')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_ode,
                                                            td_functionality=td_lr_generation,
                                                            caption='Generate LR'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_ode,
                                                         td_functionality=td_lr_generation,
                                                         caption='Generate LR')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_ode,
                                                            td_functionality=td_pay_advance,
                                                            caption='Pay Advance'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_ode,
                                                         td_functionality=td_pay_advance,
                                                         caption='Pay Advance')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_ode,
                                                            td_functionality=td_pay_balance,
                                                            caption='Pay Balance'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_ode,
                                                         td_functionality=td_pay_balance,
                                                         caption='Pay Balance')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_ode,
                                                            td_functionality=td_send_invoice,
                                                            caption='Send Invoice'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_ode,
                                                         td_functionality=td_send_invoice,
                                                         caption='Send Invoice')

    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_accounts_receivable,
                                                            td_functionality=td_verify_pod,
                                                            caption='Verify PoD'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_accounts_receivable,
                                                         td_functionality=td_verify_pod,
                                                         caption='Verify PoD')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_accounts_receivable,
                                                            td_functionality=td_raise_invoice,
                                                            caption='Raise Invoice'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_accounts_receivable,
                                                         td_functionality=td_raise_invoice,
                                                         caption='Raise Invoice')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_accounts_receivable,
                                                            td_functionality=td_send_invoice,
                                                            caption='Send Invoice'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_accounts_receivable,
                                                         td_functionality=td_send_invoice,
                                                         caption='Send Invoice')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_accounts_receivable,
                                                            td_functionality=td_confirm_invoice,
                                                            caption='Confirm Invoice'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_accounts_receivable,
                                                         td_functionality=td_confirm_invoice,
                                                         caption='Confirm Invoice')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_accounts_receivable,
                                                            td_functionality=td_inward_entry,
                                                            caption='Inward Entry'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_accounts_receivable,
                                                         td_functionality=td_inward_entry,
                                                         caption='Inward Entry')

    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_accounts_payable,
                                                            td_functionality=td_process_payments,
                                                            caption='Process Payment'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_accounts_payable,
                                                         td_functionality=td_process_payments,
                                                         caption='Process Payment')
    if not EmployeeRolesFunctionalityMapping.objects.filter(employee_role=emp_role_accounts_payable,
                                                            td_functionality=td_reconcile,
                                                            caption='Reconcile'):
        EmployeeRolesFunctionalityMapping.objects.create(employee_role=emp_role_accounts_payable,
                                                         td_functionality=td_reconcile,
                                                         caption='Reconcile')


def update_booking_statuses():
    # BookingStatuses.objects.all().delete()
    if not BookingStatuses.objects.filter(status='confirmed'):
        BookingStatuses.objects.create(status='confirmed', time_limit=1440)
    else:
        BookingStatuses.objects.filter(status='confirmed').update(status='confirmed', time_limit=1440)
    if not BookingStatuses.objects.filter(status='loaded'):
        BookingStatuses.objects.create(status='loaded', time_limit=1440)
    else:
        BookingStatuses.objects.filter(status='loaded').update(status='loaded', time_limit=1440)
    if not BookingStatuses.objects.filter(status='lr_generated'):
        BookingStatuses.objects.create(status='lr_generated', time_limit=1440)
    else:
        BookingStatuses.objects.filter(status='lr_generated').update(status='lr_generated', time_limit=1440)
    if not BookingStatuses.objects.filter(status='advance_paid'):
        BookingStatuses.objects.create(status='advance_paid', time_limit=1440)
    else:
        BookingStatuses.objects.filter(status='advance_paid').update(status='advance_paid', time_limit=1440)
    if not BookingStatuses.objects.filter(status='unloaded'):
        BookingStatuses.objects.create(status='unloaded', time_limit=14400)
    else:
        BookingStatuses.objects.filter(status='unloaded').update(status='unloaded', time_limit=14400)
    if not BookingStatuses.objects.filter(status='pod_uploaded'):
        BookingStatuses.objects.create(status='pod_uploaded', time_limit=1440)
    else:
        BookingStatuses.objects.filter(status='pod_uploaded').update(status='pod_uploaded', time_limit=1440)
    if not BookingStatuses.objects.filter(status='pod_verified'):
        BookingStatuses.objects.create(status='pod_verified', time_limit=1440)
    else:
        BookingStatuses.objects.filter(status='pod_verified').update(status='pod_verified', time_limit=1440)
    if not BookingStatuses.objects.filter(status='invoice_raised'):
        BookingStatuses.objects.create(status='invoice_raised', time_limit=1440)
    else:
        BookingStatuses.objects.filter(status='invoice_raised').update(status='invoice_raised', time_limit=1440)
    if not BookingStatuses.objects.filter(status='invoice_confirmed'):
        BookingStatuses.objects.create(status='invoice_confirmed', time_limit=0)
    else:
        BookingStatuses.objects.filter(status='invoice_confirmed').update(status='invoice_confirmed', time_limit=0)
    if not BookingStatuses.objects.filter(status='balance_paid'):
        BookingStatuses.objects.create(status='balance_paid', time_limit=0)
    else:
        BookingStatuses.objects.filter(status='balance_paid').update(status='balance_paid', time_limit=0)
    if not BookingStatuses.objects.filter(status='party_invoice_sent'):
        BookingStatuses.objects.create(status='party_invoice_sent', time_limit=4320)
    else:
        BookingStatuses.objects.filter(status='party_invoice_sent').update(status='party_invoice_sent', time_limit=4320)
    if not BookingStatuses.objects.filter(status='inward_followup_completed'):
        BookingStatuses.objects.create(status='inward_followup_completed', time_limit=2880)
    else:
        BookingStatuses.objects.filter(status='inward_followup_completed').update(status='inward_followup_completed',
                                                                                  time_limit=2880)
    if BookingStatuses.objects.filter(status='inward_followup'):
        BookingStatuses.objects.filter(status='inward_followup', time_limit=0).delete()
    if not BookingStatuses.objects.filter(status='complete'):
        BookingStatuses.objects.create(status='complete', time_limit=0)
    else:
        BookingStatuses.objects.filter(status='complete').update(status='complete', time_limit=0)


def update_booking_status_chain():
    # BookingStatusChain.objects.all().delete()
    bs_confirmed = BookingStatuses.objects.get(status='confirmed')
    bs_loaded = BookingStatuses.objects.get(status='loaded')
    bs_lr_generated = BookingStatuses.objects.get(status='lr_generated')
    bs_advance_paid = BookingStatuses.objects.get(status='advance_paid')
    bs_unloaded = BookingStatuses.objects.get(status='unloaded')
    bs_pod_uploaded = BookingStatuses.objects.get(status='pod_uploaded')
    bs_pod_verified = BookingStatuses.objects.get(status='pod_verified')
    bs_invoice_raised = BookingStatuses.objects.get(status='invoice_raised')
    bs_invoice_confirmed = BookingStatuses.objects.get(status='invoice_confirmed')
    bs_balance_paid = BookingStatuses.objects.get(status='balance_paid')
    bs_party_invoice_sent = BookingStatuses.objects.get(status='party_invoice_sent')
    bs_inward_followup = BookingStatuses.objects.get(status='inward_followup_completed')
    bs_complete = BookingStatuses.objects.get(status='complete')

    if not BookingStatusChain.objects.filter(booking_status=bs_confirmed):
        BookingStatusChain.objects.create(booking_status=bs_confirmed, level='primary',
                                          primary_preceded_booking_status=bs_confirmed,
                                          primary_succeeded_booking_status=bs_loaded,
                                          secondary_preceded_booking_status=bs_confirmed,
                                          secondary_succeeded_booking_status=bs_loaded)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_confirmed).update(booking_status=bs_confirmed,
                                                                              level='primary',
                                                                              primary_preceded_booking_status=bs_confirmed,
                                                                              primary_succeeded_booking_status=bs_loaded,
                                                                              secondary_preceded_booking_status=bs_confirmed,
                                                                              secondary_succeeded_booking_status=bs_loaded)
    if not BookingStatusChain.objects.filter(booking_status=bs_loaded):
        BookingStatusChain.objects.create(booking_status=bs_loaded, level='primary',
                                          primary_preceded_booking_status=bs_confirmed,
                                          primary_succeeded_booking_status=bs_lr_generated,
                                          secondary_preceded_booking_status=bs_confirmed,
                                          secondary_succeeded_booking_status=bs_lr_generated)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_loaded).update(booking_status=bs_loaded, level='primary',
                                                                           primary_preceded_booking_status=bs_confirmed,
                                                                           primary_succeeded_booking_status=bs_lr_generated,
                                                                           secondary_preceded_booking_status=bs_confirmed,
                                                                           secondary_succeeded_booking_status=bs_lr_generated)
    if not BookingStatusChain.objects.filter(booking_status=bs_lr_generated):
        BookingStatusChain.objects.create(booking_status=bs_lr_generated, level='primary',
                                          primary_preceded_booking_status=bs_loaded,
                                          primary_succeeded_booking_status=bs_unloaded,
                                          secondary_preceded_booking_status=bs_loaded,
                                          secondary_succeeded_booking_status=bs_advance_paid)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_lr_generated).update(booking_status=bs_lr_generated,
                                                                                 level='primary',
                                                                                 primary_preceded_booking_status=bs_loaded,
                                                                                 primary_succeeded_booking_status=bs_unloaded,
                                                                                 secondary_preceded_booking_status=bs_loaded,
                                                                                 secondary_succeeded_booking_status=bs_advance_paid)
    if not BookingStatusChain.objects.filter(booking_status=bs_advance_paid):
        BookingStatusChain.objects.create(booking_status=bs_advance_paid, level='secondary',
                                          primary_preceded_booking_status=bs_lr_generated,
                                          primary_succeeded_booking_status=bs_unloaded,
                                          secondary_preceded_booking_status=bs_lr_generated,
                                          secondary_succeeded_booking_status=bs_unloaded)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_advance_paid).update(booking_status=bs_advance_paid,
                                                                                 level='secondary',
                                                                                 primary_preceded_booking_status=bs_lr_generated,
                                                                                 primary_succeeded_booking_status=bs_unloaded,
                                                                                 secondary_preceded_booking_status=bs_lr_generated,
                                                                                 secondary_succeeded_booking_status=bs_unloaded)
    if not BookingStatusChain.objects.filter(booking_status=bs_unloaded):
        BookingStatusChain.objects.create(booking_status=bs_unloaded, level='primary',
                                          primary_preceded_booking_status=bs_lr_generated,
                                          primary_succeeded_booking_status=bs_invoice_raised,
                                          secondary_preceded_booking_status=bs_advance_paid,
                                          secondary_succeeded_booking_status=bs_pod_uploaded)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_unloaded).update(booking_status=bs_unloaded,
                                                                             level='primary',
                                                                             primary_preceded_booking_status=bs_lr_generated,
                                                                             primary_succeeded_booking_status=bs_invoice_raised,
                                                                             secondary_preceded_booking_status=bs_advance_paid,
                                                                             secondary_succeeded_booking_status=bs_pod_uploaded)

    if not BookingStatusChain.objects.filter(booking_status=bs_pod_uploaded):
        BookingStatusChain.objects.create(booking_status=bs_pod_uploaded, level='secondary',
                                          primary_preceded_booking_status=bs_unloaded,
                                          primary_succeeded_booking_status=bs_invoice_raised,
                                          secondary_preceded_booking_status=bs_unloaded,
                                          secondary_succeeded_booking_status=bs_pod_verified)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_pod_uploaded).update(booking_status=bs_pod_uploaded,
                                                                                 level='secondary',
                                                                                 primary_preceded_booking_status=bs_unloaded,
                                                                                 primary_succeeded_booking_status=bs_invoice_raised,
                                                                                 secondary_preceded_booking_status=bs_unloaded,
                                                                                 secondary_succeeded_booking_status=bs_pod_verified)
    if not BookingStatusChain.objects.filter(booking_status=bs_pod_verified):
        BookingStatusChain.objects.create(booking_status=bs_pod_verified, level='secondary',
                                          primary_preceded_booking_status=bs_unloaded,
                                          primary_succeeded_booking_status=bs_invoice_raised,
                                          secondary_preceded_booking_status=bs_pod_uploaded,
                                          secondary_succeeded_booking_status=bs_invoice_raised)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_pod_verified).update(booking_status=bs_pod_verified,
                                                                                 level='secondary',
                                                                                 primary_preceded_booking_status=bs_unloaded,
                                                                                 primary_succeeded_booking_status=bs_invoice_raised,
                                                                                 secondary_preceded_booking_status=bs_pod_uploaded,
                                                                                 secondary_succeeded_booking_status=bs_invoice_raised)
    if not BookingStatusChain.objects.filter(booking_status=bs_invoice_raised):
        BookingStatusChain.objects.create(booking_status=bs_invoice_raised, level='primary',
                                          primary_preceded_booking_status=bs_unloaded,
                                          primary_succeeded_booking_status=bs_party_invoice_sent,
                                          secondary_preceded_booking_status=bs_pod_verified,
                                          secondary_succeeded_booking_status=bs_party_invoice_sent)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_invoice_raised).update(booking_status=bs_invoice_raised,
                                                                                   level='primary',
                                                                                   primary_preceded_booking_status=bs_unloaded,
                                                                                   primary_succeeded_booking_status=bs_party_invoice_sent,
                                                                                   secondary_preceded_booking_status=bs_pod_verified,
                                                                                   secondary_succeeded_booking_status=bs_party_invoice_sent)
    if not BookingStatusChain.objects.filter(booking_status=bs_party_invoice_sent):
        BookingStatusChain.objects.create(booking_status=bs_party_invoice_sent, level='primary',
                                          primary_preceded_booking_status=bs_invoice_raised,
                                          primary_succeeded_booking_status=bs_invoice_confirmed,
                                          secondary_preceded_booking_status=bs_invoice_raised,
                                          secondary_succeeded_booking_status=bs_invoice_confirmed)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_party_invoice_sent).update(
            booking_status=bs_party_invoice_sent, level='primary',
            primary_preceded_booking_status=bs_invoice_raised,
            primary_succeeded_booking_status=bs_invoice_confirmed,
            secondary_preceded_booking_status=bs_invoice_raised,
            secondary_succeeded_booking_status=bs_invoice_confirmed)
    if not BookingStatusChain.objects.filter(booking_status=bs_balance_paid):
        BookingStatusChain.objects.create(booking_status=bs_balance_paid, level='secondary',
                                          primary_preceded_booking_status=bs_pod_uploaded,
                                          primary_succeeded_booking_status=bs_invoice_raised,
                                          secondary_preceded_booking_status=bs_pod_verified,
                                          secondary_succeeded_booking_status=bs_invoice_raised)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_balance_paid).update(booking_status=bs_balance_paid,
                                                                                 level='secondary',
                                                                                 primary_preceded_booking_status=bs_pod_uploaded,
                                                                                 primary_succeeded_booking_status=bs_invoice_raised,
                                                                                 secondary_preceded_booking_status=bs_pod_verified,
                                                                                 secondary_succeeded_booking_status=bs_invoice_raised)
    if not BookingStatusChain.objects.filter(booking_status=bs_invoice_confirmed):
        BookingStatusChain.objects.create(booking_status=bs_invoice_confirmed, level='primary',
                                          primary_preceded_booking_status=bs_party_invoice_sent,
                                          primary_succeeded_booking_status=bs_complete,
                                          secondary_preceded_booking_status=bs_party_invoice_sent,
                                          secondary_succeeded_booking_status=bs_inward_followup)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_invoice_confirmed).update(
            booking_status=bs_invoice_confirmed, level='primary',
            primary_preceded_booking_status=bs_party_invoice_sent,
            primary_succeeded_booking_status=bs_complete,
            secondary_preceded_booking_status=bs_party_invoice_sent,
            secondary_succeeded_booking_status=bs_inward_followup)
    if not BookingStatusChain.objects.filter(booking_status=bs_inward_followup):
        BookingStatusChain.objects.create(booking_status=bs_inward_followup, level='secondary',
                                          primary_preceded_booking_status=bs_invoice_confirmed,
                                          primary_succeeded_booking_status=bs_complete,
                                          secondary_preceded_booking_status=bs_invoice_confirmed,
                                          secondary_succeeded_booking_status=bs_complete)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_inward_followup).update(booking_status=bs_inward_followup,
                                                                                    level='secondary',
                                                                                    primary_preceded_booking_status=bs_invoice_confirmed,
                                                                                    primary_succeeded_booking_status=bs_complete,
                                                                                    secondary_preceded_booking_status=bs_invoice_confirmed,
                                                                                    secondary_succeeded_booking_status=bs_complete)
    if not BookingStatusChain.objects.filter(booking_status=bs_complete):
        BookingStatusChain.objects.create(booking_status=bs_complete, level='primary',
                                          primary_preceded_booking_status=bs_invoice_confirmed,
                                          primary_succeeded_booking_status=bs_complete,
                                          secondary_preceded_booking_status=bs_inward_followup,
                                          secondary_succeeded_booking_status=bs_complete)
    else:
        BookingStatusChain.objects.filter(booking_status=bs_complete).update(booking_status=bs_complete,
                                                                             level='primary',
                                                                             primary_preceded_booking_status=bs_invoice_confirmed,
                                                                             primary_succeeded_booking_status=bs_complete,
                                                                             secondary_preceded_booking_status=bs_inward_followup,
                                                                             secondary_succeeded_booking_status=bs_complete)


def prepare_user_data():
    update_user_category()
    update_employee_roles()
    update_td_functionalities()
    update_employee_roles_mapping()
    update_employee_roles_functionalities_mapping()
    update_booking_statuses()
    update_booking_status_chain()


def update_mobile_app_version():
    MobileAppVersions.objects.create(app_platform='android', app_name='AE', app_version='1.6')
    MobileAppVersions.objects.create(app_platform='android', app_name='AO', app_version='1.8')


def remove_old_in_transit_data():
    lr_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='lr_generated').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    unloaded_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='unloaded').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    in_transit_bookings = [x for x in lr_bookings if x not in unloaded_bookings]
    pods_verified = PODFile.objects.filter(booking__id__in=in_transit_bookings, verified=True, is_valid=True)
    user = User.objects.filter(username__iexact='raviaaho')[0]
    for pod_v in pods_verified:
        booking_unloaded = check_booking_status(pod_v.booking, 'unloaded')
        if not booking_unloaded:
            create_new_booking_status(pod_v.booking, 'unloaded', user)
        booking_pod_uploaded = check_booking_status(pod_v.booking, 'pod_uploaded')
        if not booking_pod_uploaded:
            create_new_booking_status(pod_v.booking, 'pod_uploaded', user)
        else:
            update_booking_status(pod_v.booking, 'pod_uploaded', 'in_progress', user)
        booking_pod_verified = check_booking_status(pod_v.booking, 'pod_verified')
        if not booking_pod_verified:
            create_new_booking_status(pod_v.booking, 'pod_verified', user)
        else:
            update_booking_status(pod_v.booking, 'pod_verified', 'in_progress', user)

    # pods_unverified = PODFile.objects.filter(booking__id__in=in_transit_bookings, verified=False, is_valid=False)
    # pods_rejected = PODFile.objects.filter(booking__id__in=in_transit_bookings, verified=True, is_valid=False)


def pod_upload_data_sync_in_bsm():
    user = User.objects.filter(username__iexact='raviaaho')[0]
    for booking in ManualBooking.objects.filter(
            Q(pod_status__iexact='unverified')).exclude(
        Q(booking_status='cancelled') | Q(deleted=True)).order_by('id'):
        booking_unloaded = check_booking_status(booking, 'unloaded')
        booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
        if booking_unloaded and not booking_pod_uploaded:
            booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
            if not booking_pod_uploaded:
                create_new_booking_status(booking, 'pod_uploaded', user)
            else:
                update_booking_status(booking, 'pod_uploaded', 'in_progress', user)


def pod_rejected_data_sync_in_bsm():
    user = User.objects.filter(username__iexact='raviaaho')[0]
    for booking in ManualBooking.objects.filter(
            Q(pod_status__iexact='rejected')).exclude(
        Q(booking_status='cancelled') | Q(deleted=True)).order_by('id'):
        booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
        booking_pod_verified = check_booking_status(booking, 'pod_verified')
        if not booking_pod_verified:
            booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
            if not booking_pod_uploaded:
                create_new_booking_status(booking, 'pod_uploaded', user)
            else:
                update_booking_status(booking, 'pod_uploaded', 'reverted', user)


def pod_verified_data_sync_in_bsm():
    user = User.objects.filter(username__iexact='raviaaho')[0]
    for booking in ManualBooking.objects.filter(
            Q(pod_status__iexact='completed') & Q(
                shipment_date__gte=(datetime.now() - timedelta(days=100)).date())).exclude(
        Q(booking_status='cancelled') | Q(deleted=True)).order_by('id'):
        booking_unloaded = check_booking_status(booking, 'unloaded')
        booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
        booking_pod_verified = check_booking_status(booking, 'pod_verified')
        if not booking_pod_verified and (booking_unloaded or booking_pod_uploaded):
            booking_pod_uploaded = check_booking_status(booking, 'unloaded')
            if not booking_pod_uploaded:
                create_new_booking_status(booking, 'unloaded', user)
            else:
                update_booking_status(booking, 'pod_uploaded', 'in_progress', user)
            booking_pod_uploaded = check_booking_status(booking, 'pod_uploaded')
            if not booking_pod_uploaded:
                create_new_booking_status(booking, 'pod_uploaded', user)
            else:
                update_booking_status(booking, 'pod_uploaded', 'in_progress', user)
            booking_pod_uploaded = check_booking_status(booking, 'pod_verified')
            if not booking_pod_uploaded:
                create_new_booking_status(booking, 'pod_verified', user)
            else:
                update_booking_status(booking, 'pod_verified', 'in_progress', user)


def sync_invoice_status():
    user = User.objects.filter(username__iexact='raviaaho')[0]
    for invoice in Invoice.objects.filter(payment_received=False):
        for booking in invoice.bookings.all():
            booking.invoice_status='invoice_confirmed'
            booking.save()
            booking_balance_paid = check_booking_status(booking, 'invoice_raised')
            if not booking_balance_paid:
                create_new_booking_status(booking, 'invoice_raised', user)
            else:
                update_booking_status(booking, 'invoice_raised', 'in_progress', user)

            booking_balance_paid = check_booking_status(booking, 'party_invoice_sent')
            if not booking_balance_paid:
                create_new_booking_status(booking, 'party_invoice_sent', user)
            else:
                update_booking_status(booking, 'party_invoice_sent', 'in_progress', user)
            booking_balance_paid = check_booking_status(booking, 'invoice_confirmed')
            if not booking_balance_paid:
                create_new_booking_status(booking, 'invoice_confirmed', user)
            else:
                update_booking_status(booking, 'invoice_confirmed', 'in_progress', user)


def pay_balance_data_sync_up():
    user = User.objects.filter(username__iexact='raviaaho')[0]
    pod_verified_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='pod_verified').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    balance_paid_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__in=['balance_paid', 'complete']).exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    balance_not_paid_bookings = [x for x in pod_verified_bookings if x not in balance_paid_bookings]
    for id in balance_not_paid_bookings:
        booking = get_or_none(ManualBooking, id=id)
        if booking and (booking.outward_payment_status == 'complete' or booking.outward_payment_status == 'excess'):
            booking_balance_paid = check_booking_status(booking, 'balance_paid')
            if not booking_balance_paid:
                create_new_booking_status(booking, 'balance_paid', user)
            else:
                update_booking_status(booking, 'balance_paid', 'in_progress', user)


def raise_invoice_data_sync_up():
    user = User.objects.filter(username__iexact='raviaaho')[0]
    pod_verified_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='pod_verified').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    invoice_raised_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='invoice_raised').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    invoice_not_raised_bookings = [x for x in pod_verified_bookings if x not in invoice_raised_bookings]
    for id in invoice_not_raised_bookings:
        booking = get_or_none(ManualBooking, id=id)
        if booking and booking.invoice_status == 'invoice_raised':
            booking_invoice_raised = check_booking_status(booking, 'invoice_raised')
            if not booking_invoice_raised:
                create_new_booking_status(booking, 'invoice_raised', user)
            else:
                update_booking_status(booking, 'invoice_raised', 'in_progress', user)
            booking_party_invoice_sent = check_booking_status(booking, 'party_invoice_sent')
            if not booking_party_invoice_sent:
                create_new_booking_status(booking, 'party_invoice_sent', user)
            else:
                update_booking_status(booking, 'party_invoice_sent', 'in_progress', user)
            booking_invoice_confirmed = check_booking_status(booking, 'invoice_confirmed')
            if not booking_invoice_confirmed:
                create_new_booking_status(booking, 'invoice_confirmed', user)
            else:
                update_booking_status(booking, 'invoice_confirmed', 'in_progress', user)
        if booking and booking.invoice_status == 'invoice_sent':
            booking_invoice_raised = check_booking_status(booking, 'invoice_raised')
            if not booking_invoice_raised:
                create_new_booking_status(booking, 'invoice_raised', user)
            else:
                update_booking_status(booking, 'invoice_raised', 'in_progress', user)
            booking_party_invoice_sent = check_booking_status(booking, 'party_invoice_sent')
            if not booking_party_invoice_sent:
                create_new_booking_status(booking, 'party_invoice_sent', user)
            else:
                update_booking_status(booking, 'party_invoice_sent', 'in_progress', user)
            booking_invoice_confirmed = check_booking_status(booking, 'invoice_confirmed')
            if not booking_invoice_confirmed:
                create_new_booking_status(booking, 'invoice_confirmed', user)
            else:
                update_booking_status(booking, 'invoice_confirmed', 'in_progress', user)
        if booking and booking.invoice_status == 'invoice_confirmed':
            booking_invoice_raised = check_booking_status(booking, 'invoice_raised')
            if not booking_invoice_raised:
                create_new_booking_status(booking, 'invoice_raised', user)
            else:
                update_booking_status(booking, 'invoice_raised', 'in_progress', user)
            booking_party_invoice_sent = check_booking_status(booking, 'party_invoice_sent')
            if not booking_party_invoice_sent:
                create_new_booking_status(booking, 'party_invoice_sent', user)
            else:
                update_booking_status(booking, 'party_invoice_sent', 'in_progress', user)
            booking_invoice_confirmed = check_booking_status(booking, 'invoice_confirmed')
            if not booking_invoice_confirmed:
                create_new_booking_status(booking, 'invoice_confirmed', user)
            else:
                update_booking_status(booking, 'invoice_confirmed', 'in_progress', user)


def sent_invoice_data_sync_up():
    user = User.objects.filter(username__iexact='raviaaho')[0]
    invoice_raised_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='invoice_raised').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    invoice_not_sent_bookings = [x for x in invoice_raised_bookings if x not in party_invoice_sent_bookings]
    for id in invoice_not_sent_bookings:
        booking = get_or_none(ManualBooking, id=id)
        if booking and (booking.invoice_status == 'invoice_raised' or booking.invoice_status == 'invoice_sent'
                        or booking.invoice_status == 'invoice_confirmed'):
            booking_invoice_raised = check_booking_status(booking, 'invoice_raised')
            if not booking_invoice_raised:
                create_new_booking_status(booking, 'invoice_raised', user)
            booking_party_invoice_sent = check_booking_status(booking, 'party_invoice_sent')
            if not booking_party_invoice_sent:
                create_new_booking_status(booking, 'party_invoice_sent', user)
            else:
                update_booking_status(booking, 'party_invoice_sent', 'in_progress', user)
            booking_invoice_confirmed = check_booking_status(booking, 'invoice_confirmed')
            if not booking_invoice_confirmed:
                create_new_booking_status(booking, 'invoice_confirmed', user)
            else:
                update_booking_status(booking, 'invoice_confirmed', 'in_progress', user)


def confirm_invoice_data_sync_up():
    user = User.objects.filter(username__iexact='raviaaho')[0]
    party_invoice_sent_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='party_invoice_sent').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='invoice_confirmed').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    invoice_not_confirmed_bookings = [x for x in party_invoice_sent_bookings if x not in invoice_confirmed_bookings]
    for id in invoice_not_confirmed_bookings:
        booking = get_or_none(ManualBooking, id=id)
        if booking and (booking.invoice_status == 'invoice_raised' or booking.invoice_status == 'invoice_sent'
                        or booking.invoice_status == 'invoice_confirmed'):
            booking_invoice_raised = check_booking_status(booking, 'invoice_raised')
            if not booking_invoice_raised:
                create_new_booking_status(booking, 'invoice_raised', user)
            booking_party_invoice_sent = check_booking_status(booking, 'party_invoice_sent')
            if not booking_party_invoice_sent:
                create_new_booking_status(booking, 'party_invoice_sent', user)
            booking_invoice_confirmed = check_booking_status(booking, 'invoice_confirmed')
            if not booking_invoice_confirmed:
                create_new_booking_status(booking, 'invoice_confirmed', user)
            else:
                update_booking_status(booking, 'invoice_confirmed', 'in_progress', user)


def inward_followup_completed_sync_up():
    user = User.objects.filter(username__iexact='raviaaho')[0]
    invoice_confirmed_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='invoice_confirmed').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    complete_bookings = BookingStatusesMapping.objects.filter(
        booking_status_chain__booking_status__status__iexact='inward_followup_completed').exclude(deleted=True). \
        values_list('manual_booking_id', flat=True)
    pending_payments_bookings = [x for x in invoice_confirmed_bookings if x not in complete_bookings]
    for id in pending_payments_bookings:
        booking = get_or_none(ManualBooking, id=id)
        if booking and (booking.inward_payment_status == 'full_received' or booking.inward_payment_status == 'excess'):
            booking_inward_followup_completed = check_booking_status(booking, 'inward_followup_completed')
            if not booking_inward_followup_completed:
                create_new_booking_status(booking, 'inward_followup_completed', user)
            else:
                update_booking_status(booking, 'inward_followup_completed', 'in_progress', user)


def save_all_manual_bookings():
    for booking in ManualBooking.objects.filter(id__gte=9231).exclude(booking_status='cancelled'):
        # try:
        booking.save()
        # except:
        #     print(booking)