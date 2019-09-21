from api.decorators import api_post, authenticated_user
from fms.forms import MobileAppVersionsForm
from fms.models import MobileAppVersions
from api.helper import json_response
from django.db import IntegrityError


@api_post
@authenticated_user
def app_version_add(request):
    form = MobileAppVersionsForm(request.data)
    if not form.is_valid():
        return {'status': 'failure', 'msg': 'Pls enter all * fields'}
    app_platform = request.data.get('app_platform')
    app_name = request.data.get('app_name')
    app_version = request.data.get('app_version')
    comment = request.data.get('comment')

    objects = {'app_platform': app_platform, 'app_name': app_name,
               'app_version': app_version, 'comment': comment}
    try:
        MobileAppVersions.objects.create(**objects)
    except IntegrityError:
        return json_response({'status': 'failure', 'msg': 'MobileAppVersions could not be created'})

    return json_response({'status': 'success', 'msg': 'MobileAppVersions successfully submitted'})


def get_all_app_versions(request):
    appversions = MobileAppVersions.objects.all().exclude(deleted=True)
    if not appversions:
        return json_response({'status': 'failure', 'msg': 'No app versions found', 'data': {}})
    return json_response({'status': 'success', 'msg': 'app version data', 'data': get_appversion_data(appversions)})


def get_appversion_data(appversions):
    app_data = []
    for ver in appversions:
        app_data.append({
            'id': ver.id,
            'app_platform': ver.app_platform,
            'app_name': ver.app_name,
            'app_version': ver.app_version,
            'version_comment': ver.comment
        })
    data = {
        'app_versions': app_data
    }
    return data

@api_post
def app_version_check(request):
    print("Request for app version check")
    form = MobileAppVersionsForm(request.data)
    if not form.is_valid():
        return {'status': 'failure', 'msg': 'Pls enter all * fields'}
    app_platform = request.data.get('app_platform')
    app_name = request.data.get('app_name')
    app_version = request.data.get('app_version')

    mobile_app_version = MobileAppVersions.objects.filter(app_name=app_name, app_platform=app_platform).\
        exclude(deleted=True).order_by('-created_on').first()

    if not mobile_app_version:
        return json_response({'status': 'failure', 'msg': 'Mobile app {} version not found'.format(app_name)})

    if mobile_app_version.app_version == app_version:
        force_upgrade = False
        recommend_upgrade = False
    else:
        if mobile_app_version.upgrade_type == 'force':
            force_upgrade = True
            recommend_upgrade = False
        else:
            recommend_upgrade = True
            force_upgrade = False

    print("Returning : Request for app version check")
    return json_response({'status': 'success', 'msg': 'App version data', 'data': {
        'forceUpgrade': force_upgrade,
        'recommendUpgrade': recommend_upgrade,
        'latest_version': mobile_app_version.app_version
    }})
