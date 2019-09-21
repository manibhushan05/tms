from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User, Group
from django.db.models import Q
from rest_framework import permissions
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from api import s3util
from api.helper import json_error_response, json_401_wrong_credentials
from api.models import S3Upload
from api.utils import parse_iso
from authentication.models import Profile
from broker.models import Broker
from driver.models import OTP
from fileupload.models import OwnerFile
from fileupload.views import get_new_serial
from fms.views import validate_url, get_user_data, save_broker_address
from owner.models import Owner
from restapi.helper_api import task_send_otp_sms, generate_otp, task_send_otp_email, success_response, error_response
from restapi.serializers.authentication import ChangePasswordSerializer, ForgotPasswordSerializer, VerifyOTPSerializer, \
    ResetPasswordSerializer, ProfileSerializer, GroupSerializer
from restapi.serializers.authentication import UserSerializer
from restapi.serializers.broker import BrokerSerializer
from restapi.serializers.owner import OwnerSerializer
from restapi.service.fms import parse_profile_data
from restapi.utils import get_or_none

# class UserListView(generics.ListAPIView):
# #     queryset = User.objects.order_by('-id')
#     serializer_class = UserSerializer
#     pagination_class = StandardResultsSetPagination
#     filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
#     filter_class = UserFilter
#     #search_fields = ('username', 'email')
from supplier.models import Supplier
from utils.models import TaxationID, City


class CreatorPermission(permissions.BasePermission):
    """
        Customer permission class which allows user creation without authentications
        and other operation needs to be authenticated
    """

    def has_permission(self, request, view):

        if view.action == 'create' or view.action == None:
            return True
        else:

            if request.user.is_authenticated:
                return True
            else:
                return False


class ProfileViewSet(viewsets.ViewSet):
    """
        A simple ViewSet for listing, updating or deleting user
    """

    def create(self, request):
        profile_serializer = ProfileSerializer(data=request.data)
        if profile_serializer.is_valid():
            profile_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "User's Profile Created",
                "data": profile_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "User's Profile not Created",
            "data": profile_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        user = get_or_none(User, id=pk)

        if not isinstance(user, User):
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if not Profile.objects.filter(user=user).exists():
            return Response({"error": "User's Profile does not exist. Please create it first"},
                            status=status.HTTP_400_BAD_REQUEST)

        profile_serializer = ProfileSerializer(user.profile, data=request.data)

        if profile_serializer.is_valid():
            profile_serializer.save()
            # Here somehow profile_serializer data was all null though it was updating correctly. So we retrieve the
            # user again to display updated data. This is a patch, need to fix this
            user = get_or_none(User, id=pk)
            profile_serializer = ProfileSerializer(user.profile)
            return Response(profile_serializer.data, status=status.HTTP_201_CREATED)
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        user = get_or_none(User, id=pk)

        if not isinstance(user, User):
            return Response({"status": "User Doesn't exists"}, status=status.HTTP_404_NOT_FOUND)
        if not Profile.objects.filter(user=user).exists():
            return Response({"error": "User's Profile does not exist. Please create it first"},
                            status=status.HTTP_400_BAD_REQUEST)
        request.data["user"] = pk
        profile_serializer = ProfileSerializer(instance=user.profile, data=request.data, partial=True)
        if profile_serializer.is_valid():
            profile_serializer.save()
            # Here somehow profile_serializer data was all null though it was updating correctly. So we retrieve the
            # user again to display updated data. This is a patch, need to fix this
            user = get_or_none(User, id=pk)
            profile_serializer = ProfileSerializer(user.profile)
            return Response(profile_serializer.data, status=status.HTTP_201_CREATED)
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def fms_partial_update(self, request, pk=None):
        data = request.data
        parsed_data = parse_profile_data(data=data)
        supplier = get_or_none(Broker, name=request.user)
        profile = get_or_none(Profile, user=request.user)
        if (not isinstance(supplier, Supplier)) and not isinstance(profile, Profile):
            return error_response(msg="Something went wrong, pls try later", status=status.HTTP_404_NOT_FOUND, data={})
        if parsed_data['profile_data'] and isinstance(profile, Profile):
            profile_serializer = ProfileSerializer(instance=profile, data=parsed_data['profile_data'], partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                return error_response(status=status.HTTP_400_BAD_REQUEST, data=profile_serializer.errors, msg='Error')
        if parsed_data['broker_data'] and isinstance(supplier, Broker):
            broker_serializer = BrokerSerializer(instance=supplier, data=parsed_data['broker_data'], partial=True)
            if broker_serializer.is_valid():
                broker_serializer.save()
            else:
                return error_response(status=status.HTTP_400_BAD_REQUEST, data=broker_serializer.errors, msg='Error')

        doc_key = 'pan_doc'
        if doc_key in data and supplier and data[doc_key].get('url'):
            if not OwnerFile.objects.filter(
                    Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                        s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                            data[doc_key].get('thumb_url')) else None)).exists():
                if S3Upload.objects.filter(uuid=data[doc_key].get('uuid', None)).exists():
                    s3_upload = S3Upload.objects.filter(uuid=data[doc_key].get('uuid', None)).last()
                else:
                    s3_upload = s3util.get_or_create_s3_upload(
                        bucket=data[doc_key].get('bucketName', None),
                        folder=data[doc_key].get('folderName', None),
                        filename=data[doc_key].get('fileName', None),
                        verified=False,
                        is_valid=False,
                        uuid=data[doc_key].get('uuid', None),
                    )
                OwnerFile.objects.create(
                    uploaded_by=request.user,
                    supplier=supplier,
                    document_category='PAN',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(OwnerFile, supplier=supplier),
                    s3_upload=s3_upload
                )

        doc_key = 'dec_doc'
        if doc_key in data and supplier and data[doc_key].get('url'):
            if not OwnerFile.objects.filter(
                    Q(s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None) | Q(
                        s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                            data[doc_key].get('thumb_url')) else None)).exists():
                if S3Upload.objects.filter(uuid=data[doc_key].get('uuid', None)).exists():
                    s3_upload = S3Upload.objects.filter(uuid=data[doc_key].get('uuid', None)).last()
                else:
                    s3_upload = s3util.get_or_create_s3_upload(
                        bucket=data[doc_key].get('bucketName', None),
                        folder=data[doc_key].get('folderName', None),
                        filename=data[doc_key].get('fileName', None),
                        verified=False,
                        is_valid=False,
                        uuid=data[doc_key].get('uuid', None),
                    )
                OwnerFile.objects.create(
                    uploaded_by=request.user,
                    supplier=supplier,
                    document_category='DEC',
                    s3_url=data[doc_key].get('url') if validate_url(data[doc_key].get('url')) else None,
                    s3_thumb_url=data[doc_key].get('thumb_url') if validate_url(
                        data[doc_key].get('thumb_url')) else None,
                    serial=get_new_serial(OwnerFile, supplier=supplier),
                    s3_upload=s3_upload,
                )
        return success_response(msg='profile edited', data={}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        user = get_or_none(User, id=pk)
        if not isinstance(user, User):
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if Profile.objects.filter(user=user).exists():
            profile_serializer = ProfileSerializer(user.profile).data
            return Response(profile_serializer, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"error": "User's Profile does not exist. Please create it first"},
                            status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ProfileViewSet):
    """
    A simple ViewSet for listing or retrieving users.

    """
    permission_classes = (CreatorPermission,)

    def create(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "User Created",
                "data": user_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "User not Created",
            "data": user_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):

        user = get_or_none(User, id=pk)

        if not isinstance(user, User):
            return Response({"status": "User Doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        user_serializer = UserSerializer(instance=user, data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "Success",
                "msg": "User Created",
                "data": user_serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "User not Created",
            "data": user_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        user = get_or_none(User, id=pk)

        if not isinstance(user, User):
            return Response({"status": "User Doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        user_serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            response = {
                "status_code": status.HTTP_202_ACCEPTED,
                "status": "Success",
                "msg": "User Updated",
                "data": user_serializer.data
            }
            return Response(data=response, status=status.HTTP_202_ACCEPTED)
        response = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "status": "Error",
            "msg": "User not Created",
            "data": user_serializer.errors
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user = get_or_none(User, id=pk)
        if not isinstance(user, User):
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        user_serializers = UserSerializer(user).data
        if Profile.objects.filter(user=user).exists():
            profile_serializer = ProfileSerializer(user.profile).data
        else:
            profile_serializer = {}
        user_serializers["profile"] = profile_serializer
        return Response(user_serializers, status=status.HTTP_200_OK)
    #
    # def retrieve_token_auth_user(self, request):
    #     token = request.data.get('token')
    #     token_obj = get_or_none(Token, key=token)
    #     if isinstance(token_obj, Token) and isinstance(token_obj.user, User):
    #         user_serializer = UserSerializer(token_obj.user)
    #         return success_response(status=status.HTTP_200_OK, msg='User exists', data=user_serializer.data,
    #                                 token=token_obj.key)
    #     return error_response(status=status.HTTP_400_BAD_REQUEST, msg='User doesnot exits', data={})

    # def soft_destroy(self, request, pk=None):
    #     user = get_or_none(User, id=pk)
    #     if not isinstance(user, User):
    #         return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
    #     user_serializers = UserSerializer(user)
    #     user.is_active = False
    #     if Profile.objects.filter(user=user).exists():
    #         user.profile.deleted = True
    #         user.profile.deleted_on = datetime.now()
    #     return Response(user_serializers.data, status=status.HTTP_202_ACCEPTED)
    #
    # def destroy(self, request, pk=None):
    #     user = get_or_none(User, id=pk)
    #     if not isinstance(user, User):
    #         return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
    #     user_serializers = UserSerializer(user)
    #     User.objects.filter(id=user.id).delete()
    #     return Response(user_serializers.data, status=status.HTTP_200_OK)


class UserLogin(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user_serializer = UserSerializer(user)
            token, created = Token.objects.get_or_create(user=user)
            response = Response({
                'status': 'success',
                'msg': 'Login Successful',
                'token': token.key,
                'data': user_serializer.data,
                'status_code': status.HTTP_200_OK
            }, status=status.HTTP_200_OK)
            return response
        response = Response({
            'status': 'failure',
            'msg': 'Login Unsuccessful',
            'data': serializer.errors,
            'status_code': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST)
        return response


class UserTokenLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        token_obj = get_or_none(Token, key=token)
        if isinstance(token_obj, Token) and isinstance(token_obj.user, User):
            user_serializer = UserSerializer(token_obj.user)
            return Response({
                'status': 'success',
                'msg': 'Login Successful',
                'token': token_obj.key,
                'data': user_serializer.data,
                'status_code': status.HTTP_200_OK
            }, status=status.HTTP_200_OK)
        return error_response(status=status.HTTP_400_BAD_REQUEST, msg='User doesnot exits', data={})


class UserLogout(APIView):
    queryset = User.objects.all()

    def delete(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response({'status': 'success', 'msg': 'Logout Successfull'}, status=status.HTTP_200_OK)


class GroupViewSet(viewsets.ViewSet):

    def list(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserRegister(viewsets.ViewSet):
    """
    A simple ViewSet for creating users.

    """
    permission_classes = [
        permissions.AllowAny
    ]

    def create_user(self, request):
        user_serializer = UserSerializer(data=request.data)
        if not request.data.get('profile', None):
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "Profile field is mandatory",
                "data": {}
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        if not user_serializer.is_valid():
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "User Register not Created",
                "data": user_serializer.errors
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        user_serializer.save()
        if type(request.data['profile']) is not dict:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "Profile field is not dictionary",
                "data": user_serializer.errors
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        request.data['profile']['user'] = user_serializer.data['id']
        profile_serializer = ProfileSerializer(data=request.data['profile'])
        if not profile_serializer.is_valid():
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "User Register not Created",
                "data": profile_serializer.errors
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        profile_serializer.save()
        # Add entry in respective tables as per user category
        response = {
            "status_code": status.HTTP_201_CREATED,
            "status": "success",
            "msg": "User Register Created",
            "data": user_serializer.data
        }
        return Response(data=response, status=status.HTTP_201_CREATED)


class UserForgotPassword(viewsets.ViewSet):
    """
        An endpoint for send otp for forgot password.
    """
    permission_classes = [
        permissions.AllowAny
    ]

    def send_otp(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(username=serializer.data.get("username"))
            except User.DoesNotExist:
                return Response({'status': 'failure', 'msg': 'User Does not exist', 'data': {},
                                 'status_code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            phone = user.profile.phone
            otp_sent_to = []
            if not phone:
                return Response({'status': 'failure', 'msg': 'Phone not found', 'data': {},
                                 'status_code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            otp_sent_to.append(phone)
            email = user.profile.email
            otp = generate_otp(phone)
            task_send_otp_sms(phone, otp)
            if email:
                otp_sent_to.append(email)
                task_send_otp_email([email], otp)
            return Response({'status': 'success', 'msg': 'OTP Sent to {}'.format(otp_sent_to), 'data': {},
                             'status_code': status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({'status': 'failure', 'msg': 'OTP Sending failed', 'data': serializer.errors,
                         'status_code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    def verify_otp(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(username=serializer.data.get("username"))
            except User.DoesNotExist:
                return Response({
                    'status': 'failure',
                    'msg': 'User Does Not Exist',
                    'data': {},
                    'status_code': status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST)
            phone = user.profile.phone
            otp = serializer.data.get("otp")
            if not phone:
                return Response({
                    'status': 'failure',
                    'msg': 'Phone not found',
                    'data': {},
                    'status_code': status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST)
            if not otp:
                return Response({
                    'status': 'failure',
                    'msg': 'OTP not received',
                    'data': {},
                    'status_code': status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST)
            verified, msg = OTP.verify(phone, otp)
            if not verified:
                return Response({
                    'status': 'failure',
                    'msg': 'Invalid OTP',
                    'data': {},
                    'status_code': status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'status': 'success',
                'token': token.key,
                'msg': 'OTP Verified',
                'data': {},
                'status_code': status.HTTP_200_OK},
                status=status.HTTP_200_OK)

        return Response({
            'status': 'failure',
            'msg': serializer.errors,
            'data': {},
            'status_code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    def get_phone_username(self, request):
        username = request.GET.get('username', None)
        return_response = {"status": "failure", "msg": "Username is required field", "data": {},
                           "status_code": status.HTTP_400_BAD_REQUEST}
        if username is None or username == '':
            return Response(return_response, status=status.HTTP_400_BAD_REQUEST)
        profile_phone = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return_response['msg'] = 'User Does Not Exist'
                return Response(return_response, status=status.HTTP_400_BAD_REQUEST)
            profile_phone = user.profile.phone
            if not profile_phone:
                return_response['msg'] = 'Phone not found'
                return Response(return_response, status=status.HTTP_400_BAD_REQUEST)
        return_response['msg'] = 'Phone found'
        return_response['status'] = 'success'
        return_response['status_code'] = status.HTTP_200_OK
        return_response['data'] = {'username': username, 'phone_no': profile_phone}
        return Response(return_response, status=status.HTTP_200_OK)


class UserResetPassword(APIView):
    """
        An endpoint for resetting password.
    """

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            password = serializer.data.get("password")
            username = serializer.data.get("username")
            if not self.object.username == username:
                return Response({"status": "failure", "msg": "Wrong username.", "data": {},
                                 "status_code": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(password)
            self.object.save()
            return Response({"status": "success", "msg": "Password is reset", "data": {},
                             "status_code": status.HTTP_204_NO_CONTENT}, status=status.HTTP_204_NO_CONTENT)

        return Response({"status": "failure", "msg": serializer.errors, "data": {},
                         "status_code": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdatePassword(APIView):
    """
       An endpoint for changing password.
    """

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return error_response(data={"old_password": ["Wrong password."]},
                                      status=status.HTTP_400_BAD_REQUEST, msg="Old password is not valid")
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return success_response(msg='Password updated', status=status.HTTP_200_OK, data={})
        return error_response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST,
                              msg='Something went wrong, Plz try later')


class AWSCredentials(viewsets.ViewSet):

    def get_aws_credentials(self, request):
        return_response = {}
        return_response['msg'] = 'AWS Credentials found'
        return_response['status'] = 'success'
        return_response['status_code'] = status.HTTP_200_OK
        return_response['data'] = {'AWS_ACCESS_KEY': 'AKIAJXFC3JRVYNIHX2UA',
                                   'AWS_ACCESS_SECRET_KEY': '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'}
        print('AWS Credentials retrieved')
        return Response(return_response, status=status.HTTP_200_OK)
