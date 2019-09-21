# encoding: utf-8
import mimetypes
import re
from django.urls import reverse

def order_name(name):
    """order_name -- Limit a text to 20 chars length, if necessary strips the
    middle of the text and substitute it for an ellipsis.

    name -- text to be limited.

    """
    name = re.sub(r'^.*/', '', name)
    if len(name) <= 30:
        return name
    return name[:10] + "..." + name[-7:]


def serialize(instance):
    """serialize -- Serialize a Picture instance into a dict.

    instance -- Picture instance
    file_attr -- attribute name that contains the FileField or ImageField

    """
    return {
        'url': instance.url(),
        'name': order_name(instance.filename()),
        'type': mimetypes.guess_type(instance.filename())[0] or 'image/png',
        'thumbnailUrl': instance.url(),
        'size': 0,
        'deleteUrl': reverse('upload-delete', args=[instance.pk]),
        'deleteType': 'POST',
        'data': instance.to_json(),
    }


