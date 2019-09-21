import pandas as pd
from django.contrib.auth.models import User

from employee.models import Employee, TaskEmail


def employee_details():
    data = []
    for employee in Employee.objects.order_by('date_of_joining'):
        data.append([
            employee.id,
            employee.emp_name(),
            employee.emp_phone(),
            employee.employee_id,
            employee.get_status_display(),
            employee.date_of_joining
        ])
    df = pd.DataFrame(data=data, columns=['ID', 'Name', 'Phone', 'Emp ID', 'Status', 'date_of_joining'])
    df.to_excel('Employee details.xlsx', index=False)


def employee_is_staff():
    for emp in Employee.objects.filter(status='active'):
        user = User.objects.get(username=emp.username.username)
        user.is_staff = True
        user.save()


def reset_employee():
    emp = Employee.objects.get(id=66)
    for task in TaskEmail.objects.all():
        task.employee.clear()
        task.employee.add(emp)

def reset_all_password():
    for user in User.objects.all():
        print(user)
        user.set_password('aaho1234')
        user.save()
