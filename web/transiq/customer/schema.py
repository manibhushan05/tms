from api.schema import status_msg_extra_schema, dict_schema, list_schema, str_schema, num_schema, null_str_schema, \
    enum_schema, null_dict_schema


def customer_app_data_schema():
    return status_msg_extra_schema(
        data=dict_schema(
            cities=list_schema(
                schema=dict_schema(
                    id=num_schema(),
                    name=str_schema(),
                    state=str_schema()
                )
            ),
            vehicles=list_schema(
                schema=dict_schema(
                    id=num_schema(),
                    vehicle_type=null_str_schema(),
                    capacity=null_str_schema()
                )
            ),
            vendors=list_schema(
                schema=dict_schema(
                    id=num_schema(),
                    name=null_str_schema(),
                    phone=null_str_schema(),
                )
            ),
            city_scores=list_schema(
                schema=list_schema(min_items=2, max_items=2)
            ),
            address_scores=list_schema(
                schema=list_schema(min_items=3, max_items=3)
            ),
            user=sme_user_schema(),
        )
    )


def customer_login_status_schema():
    return status_msg_extra_schema(
        state=enum_schema(['logged_in', 'inactive', 'logged_out'], type='string')
    )


def customer_add_vendor_schema():
    return status_msg_extra_schema(
        vendors=list_schema(
            schema=dict_schema(
                id=num_schema(),
                name=str_schema(),
                phone=str_schema()
            )
        )
    )


def customer_delete_vendor_schema():
    return customer_add_vendor_schema()


def customer_edit_profile_schema():
    return status_msg_extra_schema(
        user=sme_user_schema()
    )


def customer_new_booking_schema():
    return status_msg_extra_schema(
        booking_id=num_schema(gt=0, multiple_of=1),
        vendors=list_schema(
            schema=dict_schema(
                id=num_schema(),
                name=null_str_schema(),
                phone=null_str_schema(),
            )
        ),
        city_scores=list_schema(
            schema=list_schema(min_items=2, max_items=2)
        ),
        address_scores=list_schema(
            schema=list_schema(min_items=3, max_items=3)
        )
    )


def sme_user_schema():
    return dict_schema(
        full_name=null_str_schema(),
        contact_name=null_str_schema(),
        address=address_schema(),
        username=str_schema(),
        phone=null_str_schema(),
        email=null_str_schema(),
        designation=null_str_schema(),
        id=num_schema()
    )


def address_schema(null=True):
    schema_func = null_dict_schema if null else dict_schema
    return schema_func(
        required_schema_properties=[],
        id=num_schema(),
        line1=null_str_schema(),
        line2=null_str_schema(),
        line3=null_str_schema(),
        landmark=null_str_schema(),
        pin=null_str_schema(),
        city=null_dict_schema(
            id=num_schema(),
            name=str_schema(),
            state=str_schema()
        )
    )
