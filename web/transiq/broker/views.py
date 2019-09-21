import json

from django.db.models import Q
from django.http import HttpResponse

from api.utils import to_int
from broker.models import Broker


def broker_data(request):
    rows = to_int(request.GET.get('page'))
    brokers = Broker.objects.all()

    search_value = request.GET.get('search')
    if search_value:
        brokers = Broker.objects.filter(
            Q(name__profile__name__icontains=search_value) | Q(name__profile__phone__icontains=search_value))
    data = []
    for broker in brokers[:rows]:
        data.append({
            'id': broker.id,
            'text': '{}, {}'.format(broker.get_name(), broker.get_phone())
        })
    data = {
        'results': data
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
