from api.schema import status_msg_extra_schema, bool_schema, null_str_schema, null_dict_schema, str_schema, dict_schema


def pod_details_schema():
    return status_msg_extra_schema(
        can_upload_pod=bool_schema(),
        no_pod_reason=null_str_schema(),
        pod_details=null_dict_schema()
    )


def driver_register_schema():
    return status_msg_extra_schema(
        auth_token=str_schema()
    )


def update_pod_schema():
    return status_msg_extra_schema(
        pod_details=dict_schema()
    )

