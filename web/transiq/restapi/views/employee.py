from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, permissions, filters
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response

from authentication.models import Profile
from employee.models import Department, Employee, Designation, FitnessDetail, PastEmployment, PermanentAddress, \
    Referral, EmploymentAgency, CurrentEmploymentDetails, EducationalDegree, CertificationCourse, SkillSet, Nominee, \
    LeaveRecord, Salary, TaskEmail, Task
from restapi.filter.employee import EmployeeFilter
from restapi.helper_api import error_response, success_response
from restapi.serializers.authentication import ProfileSerializer
from restapi.serializers.employee import DepartmentSerializer, EmployeeSerializer, DesignationSerializer, \
    FitnessDetailSerializer, PastEmploymentSerializer, PermanentAddressSerializer, ReferralSerializer, \
    EmploymentAgencySerializer, CurrentEmploymentDetailsSerializer, EducationalDegreeSerializer, \
    CertificationCourseSerializer, SkillSetSerializer, NomineeSerializer, LeaveRecordSerializer, \
    SalarySerializer, TaskSerializer, TaskEmailSerializer
from restapi.utils import get_or_none


class DesignationViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Designation
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        designation_serializer = DesignationSerializer(data=request.data)
        if designation_serializer.is_valid():
            designation_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Designation Created",
                "data": designation_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Designation not Created",
            "data": designation_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        designation = get_or_none(Designation, id=pk)
        if not isinstance(designation, Designation):
            return Response({"error": "Designation does not exist"}, status=status.HTTP_404_NOT_FOUND)
        designation_serializer = DesignationSerializer(designation, data=request.data)

        if designation_serializer.is_valid():
            designation_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Designation Updated",
                "data": designation_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Designation not Updated",
            "data": designation_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        designation = get_or_none(Designation, id=pk)
        if not isinstance(designation, Designation):
            return Response({"error": "Designation does not exist"}, status=status.HTTP_404_NOT_FOUND)
        designation_serializer = DesignationSerializer(
            instance=designation,
            data=request.data,
            partial=True
        )

        if designation_serializer.is_valid():
            designation_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Designation Updated",
                "data": designation_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Designation not Updated",
            "data": designation_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        designation = get_or_none(Designation, id=pk)
        if isinstance(designation, Designation):
            designation_serializer = DesignationSerializer(designation)
            return Response(designation_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Designation does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DepartmentViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Department
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        department_serializer = DepartmentSerializer(data=request.data)
        if department_serializer.is_valid():
            department_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Department Created",
                "data": department_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Department not Created",
            "data": department_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        department = get_or_none(Department, id=pk)
        if not isinstance(department, Department):
            return Response({"error": "Department does not exist"}, status=status.HTTP_404_NOT_FOUND)
        department_serializer = DepartmentSerializer(department, data=request.data)

        if department_serializer.is_valid():
            department_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Department Updated",
                "data": department_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Department not Updated",
            "data": department_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        department = get_or_none(Department, id=pk)
        if not isinstance(department, Department):
            return Response({"error": "Department does not exist"}, status=status.HTTP_404_NOT_FOUND)
        department_serializer = DepartmentSerializer(
            instance=department,
            data=request.data,
            partial=True
        )

        if department_serializer.is_valid():
            department_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Department Updated",
                "data": department_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Department not Updated",
            "data": department_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        department = get_or_none(Department, id=pk)
        if isinstance(department, Department):
            department_serializer = DepartmentSerializer(department)
            return Response(department_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Department does not exist"}, status=status.HTTP_404_NOT_FOUND)


class FitnessViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Fitness Detail
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        fitness_detail_serializer = FitnessDetailSerializer(data=request.data)
        if fitness_detail_serializer.is_valid():
            fitness_detail_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Fitness Detail Created",
                "data": fitness_detail_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Fitness Detail not Created",
            "data": fitness_detail_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        fitness_detail = get_or_none(FitnessDetail, id=pk)
        if not isinstance(fitness_detail, FitnessDetail):
            return Response({"error": "Fitness Detail does not exist"}, status=status.HTTP_404_NOT_FOUND)
        fitness_detail_serializer = FitnessDetailSerializer(fitness_detail, data=request.data)

        if fitness_detail_serializer.is_valid():
            fitness_detail_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Fitness Detail Updated",
                "data": fitness_detail_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Fitness Detail not Updated",
            "data": fitness_detail_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        fitness_detail = get_or_none(FitnessDetail, id=pk)
        if not isinstance(fitness_detail, FitnessDetail):
            return Response({"error": "Fitness Detail does not exist"}, status=status.HTTP_404_NOT_FOUND)
        fitness_detail_serializer = FitnessDetailSerializer(
            instance=fitness_detail,
            data=request.data,
            partial=True
        )

        if fitness_detail_serializer.is_valid():
            fitness_detail_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Fitness Detail Updated",
                "data": fitness_detail_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Fitness Detail not Updated",
            "data": fitness_detail_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        fitness_detail = get_or_none(FitnessDetail, id=pk)
        if isinstance(fitness_detail, FitnessDetail):
            fitness_detail_serializer = FitnessDetailSerializer(fitness_detail)
            return Response(fitness_detail_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Fitness Detail does not exist"}, status=status.HTTP_404_NOT_FOUND)


class PastEmploymentViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on PastEmployment
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        past_employment_serializer = PastEmploymentSerializer(data=request.data)
        if past_employment_serializer.is_valid():
            past_employment_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Past Employment Created",
                "data": past_employment_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Past Employment not Created",
            "data": past_employment_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        past_employment = get_or_none(PastEmployment, id=pk)
        if not isinstance(past_employment, PastEmployment):
            return Response({"error": "Past Employment does not exist"}, status=status.HTTP_404_NOT_FOUND)
        past_employment_serializer = PastEmploymentSerializer(past_employment, data=request.data)

        if past_employment_serializer.is_valid():
            past_employment_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Past Employment Updated",
                "data": past_employment_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Past Employment not Updated",
            "data": past_employment_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        past_employment = get_or_none(PastEmployment, id=pk)
        if not isinstance(past_employment, PastEmployment):
            return Response({"error": "Past Employment does not exist"}, status=status.HTTP_404_NOT_FOUND)
        past_employment_serializer = PastEmploymentSerializer(
            instance=past_employment,
            data=request.data,
            partial=True
        )

        if past_employment_serializer.is_valid():
            past_employment_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Past Employment Updated",
                "data": past_employment_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Past Employment not Updated",
            "data": past_employment_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        past_employment = get_or_none(PastEmployment, id=pk)
        if isinstance(past_employment, PastEmployment):
            past_employment_serializer = PastEmploymentSerializer(past_employment)
            return Response(past_employment_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Past Employment does not exist"}, status=status.HTTP_404_NOT_FOUND)


class PermanentAddressViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Permanent Address
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        permanent_address_serializer = PermanentAddressSerializer(data=request.data)
        if permanent_address_serializer.is_valid():
            permanent_address_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Permanent Address Created",
                "data": permanent_address_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Permanent Address not Created",
            "data": permanent_address_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        permanent_address = get_or_none(PermanentAddress, id=pk)
        if not isinstance(permanent_address, PermanentAddress):
            return Response({"error": "Permanent Address does not exist"}, status=status.HTTP_404_NOT_FOUND)
        permanent_address_serializer = PermanentAddressSerializer(permanent_address, data=request.data)

        if permanent_address_serializer.is_valid():
            permanent_address_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Permanent Address Updated",
                "data": permanent_address_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Permanent Address not Updated",
            "data": permanent_address_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        permanent_address = get_or_none(PermanentAddress, id=pk)
        if not isinstance(permanent_address, PermanentAddress):
            return Response({"error": "Permanent Address does not exist"}, status=status.HTTP_404_NOT_FOUND)
        permanent_address_serializer = PermanentAddressSerializer(
            instance=permanent_address,
            data=request.data,
            partial=True
        )

        if permanent_address_serializer.is_valid():
            permanent_address_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Permanent Address Updated",
                "data": permanent_address_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Permanent Address not Updated",
            "data": permanent_address_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        permanent_address = get_or_none(PermanentAddress, id=pk)
        if isinstance(permanent_address, PermanentAddress):
            permanent_address_serializer = PermanentAddressSerializer(permanent_address)
            return Response(permanent_address_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Permanent Address does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ReferralViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Referral
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        referral_serializer = ReferralSerializer(data=request.data)
        if referral_serializer.is_valid():
            referral_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Referral Created",
                "data": referral_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Referral not Created",
            "data": referral_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        referral = get_or_none(Referral, id=pk)
        if not isinstance(referral, Referral):
            return Response({"error": "Referral does not exist"}, status=status.HTTP_404_NOT_FOUND)
        referral_serializer = ReferralSerializer(referral, data=request.data)

        if referral_serializer.is_valid():
            referral_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Referral Updated",
                "data": referral_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Referral not Updated",
            "data": referral_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        referral = get_or_none(Referral, id=pk)
        if not isinstance(referral, Referral):
            return Response({"error": "Referral does not exist"}, status=status.HTTP_404_NOT_FOUND)
        referral_serializer = ReferralSerializer(
            instance=referral,
            data=request.data,
            partial=True
        )

        if referral_serializer.is_valid():
            referral_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Referral Updated",
                "data": referral_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Referral not Updated",
            "data": referral_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        referral = get_or_none(Referral, id=pk)
        if isinstance(referral, Referral):
            referral_serializer = ReferralSerializer(referral)
            return Response(referral_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Referral does not exist"}, status=status.HTTP_404_NOT_FOUND)


class EmploymentAgencyViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on EmploymentAgency
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        employment_agency_serializer = EmploymentAgencySerializer(data=request.data)
        if employment_agency_serializer.is_valid():
            employment_agency_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "EmploymentAgency Created",
                "data": employment_agency_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "EmploymentAgency not Created",
            "data": employment_agency_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        employment_agency = get_or_none(EmploymentAgency, id=pk)
        if not isinstance(employment_agency, EmploymentAgency):
            return Response({"error": "EmploymentAgency does not exist"}, status=status.HTTP_404_NOT_FOUND)
        employment_agency_serializer = EmploymentAgencySerializer(employment_agency, data=request.data)

        if employment_agency_serializer.is_valid():
            employment_agency_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "EmploymentAgency Updated",
                "data": employment_agency_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "EmploymentAgency not Updated",
            "data": employment_agency_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        employment_agency = get_or_none(EmploymentAgency, id=pk)
        if not isinstance(employment_agency, EmploymentAgency):
            return Response({"error": "EmploymentAgency does not exist"}, status=status.HTTP_404_NOT_FOUND)
        employment_agency_serializer = EmploymentAgencySerializer(
            instance=employment_agency,
            data=request.data,
            partial=True
        )

        if employment_agency_serializer.is_valid():
            employment_agency_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "EmploymentAgency Updated",
                "data": employment_agency_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "EmploymentAgency not Updated",
            "data": employment_agency_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        employment_agency = get_or_none(EmploymentAgency, id=pk)
        if isinstance(employment_agency, EmploymentAgency):
            employment_agency_serializer = EmploymentAgencySerializer(employment_agency)
            return Response(employment_agency_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "EmploymentAgency does not exist"}, status=status.HTTP_404_NOT_FOUND)


class EmployeeListView(generics.ListAPIView):
    queryset = Employee.objects.order_by('-id').exclude(Q(deleted=True))
    serializer_class = EmployeeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filter_class = EmployeeFilter
    search_fields = (
        'username__profile__name', 'username__profile__phone', 'username__username', 'employee_id',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = {"status": "success", "status_code": status.HTTP_200_OK, "msg": "Employee List"}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data["data"] = serializer.data
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data["data"] = serializer.data

        return Response(data)


class EmployeeViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Employee
    """
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        employee_serializer = EmployeeSerializer(data=request.data)
        if employee_serializer.is_valid():
            employee_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Employee Created",
                "data": employee_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Employee not Created",
            "data": employee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        employee = get_or_none(Employee, id=pk)
        if not isinstance(employee, Employee):
            return Response({"error": "Employee does not exist"}, status=status.HTTP_404_NOT_FOUND)
        employee_serializer = EmployeeSerializer(instance=employee, data=request.data)
        if employee_serializer.is_valid():
            employee_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Employee Updated",
                "data": employee_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Employee not Updated",
            "data": employee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        employee = get_or_none(Employee, id=pk)
        if not isinstance(employee, Employee):
            return Response({"error": "Employee does not exist"}, status=status.HTTP_404_NOT_FOUND)
        profile = get_or_none(Profile, user=request.user)
        if isinstance(profile, Profile):
            profile_data = {
                'name': request.data.get('name', profile.name),
                'alternate_phone': request.data.get('alternate_phone', profile.name),
                'phone': request.data.get('phone', profile.name),
                'email': request.data.get('email', profile.name),
            }
            profile_serializer = ProfileSerializer(data=profile_data, instance=profile, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Error", data=profile_serializer.errors)
        employee_serializer = EmployeeSerializer(
            instance=employee,
            data=request.data,
            partial=True
        )
        if employee_serializer.is_valid():
            employee_serializer.save()
            return success_response(status=status.HTTP_202_ACCEPTED, msg="Employee Updated",
                                    data=employee_serializer.data)
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg="Employee not Updated",
                              data=employee_serializer.errors)

    def retrieve(self, request, pk=None):
        employee = get_or_none(Employee, id=pk)
        if not isinstance(employee, Employee):
            return Response({"error": "Employee does not exist"}, status=status.HTTP_404_NOT_FOUND)
        employee_serializer = EmployeeSerializer(employee)
        return Response(data=employee_serializer.data, status=status.HTTP_200_OK,
                        template_name='team/employee/update-profile.html')


class CurrentEmploymentDetailsViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Current Employment Details
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        current_employment_details_serializer = CurrentEmploymentDetailsSerializer(data=request.data)
        if current_employment_details_serializer.is_valid():
            current_employment_details_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Current Employment Details Created",
                "data": current_employment_details_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Current Employment Details not Created",
            "data": current_employment_details_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        current_employment_details = get_or_none(CurrentEmploymentDetails, id=pk)
        if not isinstance(current_employment_details, CurrentEmploymentDetails):
            return Response({"error": "Current Employment Details does not exist"}, status=status.HTTP_404_NOT_FOUND)
        current_employment_details_serializer = CurrentEmploymentDetailsSerializer(current_employment_details,
                                                                                   data=request.data)

        if current_employment_details_serializer.is_valid():
            current_employment_details_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Current Employment Details Updated",
                "data": current_employment_details_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Current Employment Details not Updated",
            "data": current_employment_details_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        current_employment_details = get_or_none(CurrentEmploymentDetails, id=pk)
        if not isinstance(current_employment_details, CurrentEmploymentDetails):
            return Response({"error": "Current Employment Details does not exist"}, status=status.HTTP_404_NOT_FOUND)
        current_employment_details_serializer = CurrentEmploymentDetailsSerializer(
            instance=current_employment_details,
            data=request.data,
            partial=True
        )

        if current_employment_details_serializer.is_valid():
            current_employment_details_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Current Employment Details Updated",
                "data": current_employment_details_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Current Employment Details not Updated",
            "data": current_employment_details_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        current_employment_details = get_or_none(CurrentEmploymentDetails, id=pk)
        if isinstance(current_employment_details, CurrentEmploymentDetails):
            current_employment_details_serializer = CurrentEmploymentDetailsSerializer(current_employment_details)
            return Response(current_employment_details_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Current Employment Details does not exist"}, status=status.HTTP_404_NOT_FOUND)


class EducationalDegreeViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Educational Degree
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        educational_degree_serializer = EducationalDegreeSerializer(data=request.data)
        if educational_degree_serializer.is_valid():
            educational_degree_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Educational Degree Created",
                "data": educational_degree_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Educational Degree not Created",
            "data": educational_degree_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        educational_degree = get_or_none(EducationalDegree, id=pk)
        if not isinstance(educational_degree, EducationalDegree):
            return Response({"error": "Educational Degree does not exist"}, status=status.HTTP_404_NOT_FOUND)
        educational_degree_serializer = EducationalDegreeSerializer(educational_degree, data=request.data)

        if educational_degree_serializer.is_valid():
            educational_degree_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Educational Degree Updated",
                "data": educational_degree_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Educational Degree not Updated",
            "data": educational_degree_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        educational_degree = get_or_none(EducationalDegree, id=pk)
        if not isinstance(educational_degree, EducationalDegree):
            return Response({"error": "Educational Degree does not exist"}, status=status.HTTP_404_NOT_FOUND)
        educational_degree_serializer = EducationalDegreeSerializer(
            instance=educational_degree,
            data=request.data,
            partial=True
        )

        if educational_degree_serializer.is_valid():
            educational_degree_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Educational Degree Updated",
                "data": educational_degree_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Educational Degree not Updated",
            "data": educational_degree_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        educational_degree = get_or_none(EducationalDegree, id=pk)
        if isinstance(educational_degree, EducationalDegree):
            educational_degree_serializer = EducationalDegreeSerializer(educational_degree)
            return Response(educational_degree_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Educational Degree does not exist"}, status=status.HTTP_404_NOT_FOUND)


class CertificationCourseViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Certification Course
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        certification_course_serializer = CertificationCourseSerializer(data=request.data)
        if certification_course_serializer.is_valid():
            certification_course_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Certification Course Created",
                "data": certification_course_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Certification Course not Created",
            "data": certification_course_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        certification_course = get_or_none(CertificationCourse, id=pk)
        if not isinstance(certification_course, CertificationCourse):
            return Response({"error": "Certification Course does not exist"}, status=status.HTTP_404_NOT_FOUND)
        certification_course_serializer = CertificationCourseSerializer(certification_course, data=request.data)

        if certification_course_serializer.is_valid():
            certification_course_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Certification Course Updated",
                "data": certification_course_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Certification Course not Updated",
            "data": certification_course_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        certification_course = get_or_none(CertificationCourse, id=pk)
        if not isinstance(certification_course, CertificationCourse):
            return Response({"error": "Certification Course does not exist"}, status=status.HTTP_404_NOT_FOUND)
        certification_course_serializer = CertificationCourseSerializer(
            instance=certification_course,
            data=request.data,
            partial=True
        )

        if certification_course_serializer.is_valid():
            certification_course_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Certification Course Updated",
                "data": certification_course_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Certification Course not Updated",
            "data": certification_course_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        certification_course = get_or_none(CertificationCourse, id=pk)
        if isinstance(certification_course, CertificationCourse):
            certification_course_serializer = CertificationCourseSerializer(certification_course)
            return Response(certification_course_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Certification Course does not exist"}, status=status.HTTP_404_NOT_FOUND)


class SkillSetViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Skill Set
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        skill_set_serializer = SkillSetSerializer(data=request.data)
        if skill_set_serializer.is_valid():
            skill_set_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Skill Set Created",
                "data": skill_set_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Skill Set not Created",
            "data": skill_set_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        skill_set = get_or_none(SkillSet, id=pk)
        if not isinstance(skill_set, SkillSet):
            return Response({"error": "Skill Set does not exist"}, status=status.HTTP_404_NOT_FOUND)
        skill_set_serializer = SkillSetSerializer(skill_set, data=request.data)

        if skill_set_serializer.is_valid():
            skill_set_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Skill Set Updated",
                "data": skill_set_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Skill Set not Updated",
            "data": skill_set_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        skill_set = get_or_none(SkillSet, id=pk)
        if not isinstance(skill_set, SkillSet):
            return Response({"error": "Skill Set does not exist"}, status=status.HTTP_404_NOT_FOUND)
        skill_set_serializer = SkillSetSerializer(
            instance=skill_set,
            data=request.data,
            partial=True
        )

        if skill_set_serializer.is_valid():
            skill_set_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Skill Set Updated",
                "data": skill_set_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Skill Set not Updated",
            "data": skill_set_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        skill_set = get_or_none(SkillSet, id=pk)
        if isinstance(skill_set, SkillSet):
            skill_set_serializer = SkillSetSerializer(skill_set)
            return Response(skill_set_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Skill Set does not exist"}, status=status.HTTP_404_NOT_FOUND)


class NomineeViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Nominee
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        nominee_serializer = NomineeSerializer(data=request.data)
        if nominee_serializer.is_valid():
            nominee_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Nominee Created",
                "data": nominee_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Nominee not Created",
            "data": nominee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        nominee = get_or_none(Nominee, id=pk)
        if not isinstance(nominee, Nominee):
            return Response({"error": "Nominee does not exist"}, status=status.HTTP_404_NOT_FOUND)
        nominee_serializer = NomineeSerializer(nominee, data=request.data)

        if nominee_serializer.is_valid():
            nominee_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Nominee Updated",
                "data": nominee_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Nominee not Updated",
            "data": nominee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        nominee = get_or_none(Nominee, id=pk)
        if not isinstance(nominee, Nominee):
            return Response({"error": "Nominee does not exist"}, status=status.HTTP_404_NOT_FOUND)
        nominee_serializer = NomineeSerializer(
            instance=nominee,
            data=request.data,
            partial=True
        )

        if nominee_serializer.is_valid():
            nominee_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Nominee Updated",
                "data": nominee_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Nominee not Updated",
            "data": nominee_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        nominee = get_or_none(Nominee, id=pk)
        if isinstance(nominee, Nominee):
            nominee_serializer = NomineeSerializer(nominee)
            return Response(nominee_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Nominee does not exist"}, status=status.HTTP_404_NOT_FOUND)


class LeaveRecordViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Leave Record
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        leave_record_serializer = LeaveRecordSerializer(data=request.data)
        if leave_record_serializer.is_valid():
            leave_record_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Leave Record Created",
                "data": leave_record_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Leave Record not Created",
            "data": leave_record_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        leave_record = get_or_none(LeaveRecord, id=pk)
        if not isinstance(leave_record, LeaveRecord):
            return Response({"error": "Leave Record does not exist"}, status=status.HTTP_404_NOT_FOUND)
        leave_record_serializer = LeaveRecordSerializer(leave_record, data=request.data)

        if leave_record_serializer.is_valid():
            leave_record_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Leave Record Updated",
                "data": leave_record_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Leave Record not Updated",
            "data": leave_record_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        leave_record = get_or_none(LeaveRecord, id=pk)
        if not isinstance(leave_record, LeaveRecord):
            return Response({"error": "Leave Record does not exist"}, status=status.HTTP_404_NOT_FOUND)
        leave_record_serializer = LeaveRecordSerializer(
            instance=leave_record,
            data=request.data,
            partial=True
        )

        if leave_record_serializer.is_valid():
            leave_record_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Leave Record Updated",
                "data": leave_record_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Leave Record not Updated",
            "data": leave_record_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        leave_record = get_or_none(LeaveRecord, id=pk)
        if isinstance(leave_record, LeaveRecord):
            leave_record_serializer = LeaveRecordSerializer(leave_record)
            return Response(leave_record_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Leave Record does not exist"}, status=status.HTTP_404_NOT_FOUND)


class SalaryViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Salary
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        salary_serializer = SalarySerializer(data=request.data)
        if salary_serializer.is_valid():
            salary_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Salary Created",
                "data": salary_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Salary not Created",
            "data": salary_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        salary = get_or_none(Salary, id=pk)
        if not isinstance(salary, Salary):
            return Response({"error": "Salary does not exist"}, status=status.HTTP_404_NOT_FOUND)
        salary_serializer = SalarySerializer(salary, data=request.data)

        if salary_serializer.is_valid():
            salary_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Salary Updated",
                "data": salary_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Salary not Updated",
            "data": salary_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        salary = get_or_none(Salary, id=pk)
        if not isinstance(salary, Salary):
            return Response({"error": "Salary does not exist"}, status=status.HTTP_404_NOT_FOUND)
        salary_serializer = SalarySerializer(
            instance=salary,
            data=request.data,
            partial=True
        )

        if salary_serializer.is_valid():
            salary_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Salary Updated",
                "data": salary_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Salary not Updated",
            "data": salary_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        salary = get_or_none(Salary, id=pk)
        if isinstance(salary, Salary):
            salary_serializer = SalarySerializer(salary)
            return Response(salary_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Salary does not exist"}, status=status.HTTP_404_NOT_FOUND)


class TaskViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Task
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        task_serializer = TaskSerializer(data=request.data)
        if task_serializer.is_valid():
            task_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Task Created",
                "data": task_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Task not Created",
            "data": task_serializer.errors
        }
        return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        task = get_or_none(Task, id=pk)
        if not isinstance(task, Task):
            return Response({"error": "Task does not exist"}, status=status.HTTP_404_NOT_FOUND)
        task_serializer = TaskSerializer(task, data=request.data)

        if task_serializer.is_valid():
            task_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Task Updated",
                "data": task_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Task not Updated",
            "data": task_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        task = get_or_none(Task, id=pk)
        if not isinstance(task, Task):
            return Response({"error": "Task does not exist"}, status=status.HTTP_404_NOT_FOUND)
        task_serializer = TaskSerializer(
            instance=task,
            data=request.data,
            partial=True
        )

        if task_serializer.is_valid():
            task_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Task Updated",
                "data": task_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Task not Updated",
            "data": task_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        task = get_or_none(Task, id=pk)
        if isinstance(task, Task):
            task_serializer = TaskSerializer(task)
            return Response(task_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Task does not exist"}, status=status.HTTP_404_NOT_FOUND)


class TaskEmailViewSet(viewsets.ViewSet):
    """
        API for CRUP operation on Task Email
    """

    def create(self, request):
        request.data["created_by"] = self.request.user.username
        request.data["changed_by"] = self.request.user.username
        task_email_serializer = TaskEmailSerializer(data=request.data)
        if task_email_serializer.is_valid():
            task_email_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "Task Email Created",
                "data": task_email_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Task Email not Created",
            "data": task_email_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username

        task_email = get_or_none(TaskEmail, id=pk)
        if not isinstance(task_email, TaskEmail):
            return Response({"error": "Task Email does not exist"}, status=status.HTTP_404_NOT_FOUND)
        task_email_serializer = TaskEmailSerializer(task_email, data=request.data)

        if task_email_serializer.is_valid():
            task_email_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Task Email Updated",
                "data": task_email_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Task Email not Updated",
            "data": task_email_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        request.data["changed_by"] = self.request.user.username
        task_email = get_or_none(TaskEmail, id=pk)
        if not isinstance(task_email, TaskEmail):
            return Response({"error": "Task Email does not exist"}, status=status.HTTP_404_NOT_FOUND)
        task_email_serializer = TaskEmailSerializer(
            instance=task_email,
            data=request.data,
            partial=True
        )

        if task_email_serializer.is_valid():
            task_email_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "Task Email Updated",
                "data": task_email_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "Task Email not Updated",
            "data": task_email_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        task_email = get_or_none(TaskEmail, id=pk)
        if isinstance(task_email, TaskEmail):
            task_email_serializer = TaskEmailSerializer(task_email)
            return Response(task_email_serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Task Email does not exist"}, status=status.HTTP_404_NOT_FOUND)
