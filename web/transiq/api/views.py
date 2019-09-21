import os

from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_str

from api.blackbuck import DATA_DIR
from api.decorators import authenticated_user, no_test


@no_test
@authenticated_user
def blackbuck_list(request):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    files.sort(reverse=True)
    return render(request, 'list.html', {'files': files})


@no_test
@authenticated_user
def blackbuck_file(request, filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return Http404

    data = open(filepath).read()
    response = HttpResponse(data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filename)
    response['Content-Length'] = os.path.getsize(filepath)

    return response
