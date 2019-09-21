from api.schema import status_msg_extra_schema, dict_schema, list_schema, str_schema, num_schema, null_str_schema, \
    null_num_schema, enum_schema, null_dict_schema


def fms_edit_profile_schema():
    return status_msg_extra_schema(
        user=fms_user_schema()
    )


def fms_user_schema():
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


def fms_app_data_schema():
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
            city_scores=list_schema(schema=dict_schema()),
            address_scores=list_schema(schema=dict_schema()),
            user=dict_schema(),
            accounts_data=list_schema(schema=account_schema())
        )
    )


def fms_edit_vehicle_status_schema():
    return status_msg_extra_schema(
        vehicle_status=vehicle_status_schema()
    )


def fms_edit_owner_schema():
    return status_msg_extra_schema(
        data=owner_schema(null=False)
    )


def fms_edit_vehicle_schema():
    return status_msg_extra_schema(
        data=vehicle_schema(null=False)
    )


def fms_edit_driver_schema():
    return status_msg_extra_schema(
        data=driver_schema(null=False)
    )


def fms_send_quote_schema():
    return status_msg_extra_schema(
        data=dict_schema(
            id=num_schema(),
            transaction_id=num_schema(),
            vehicle_request_id=num_schema(),
            user_id=num_schema(),
            quantity=num_schema(gt=0, multiple_of=1),
            amount=num_schema(gt=0),
            comments=null_str_schema()
        )
    )


def fms_edit_account_schema():
    return status_msg_extra_schema(
        data=account_schema(null=False)
    )


def fms_login_status_schema():
    return status_msg_extra_schema(
        state=enum_schema(['logged_in', 'inactive', 'logged_out'], type='string')
    )


def fms_available_loads_schema():
    return status_msg_extra_schema(
        data=list_schema(
            schema=dict_schema(
                vehicle_request_id=num_schema(),
                vehicle_category_id=num_schema(),
                vehicle_category=str_schema(),
                vehicle_quantity=num_schema(gt=0, multiple_of=1),
                transaction_id=num_schema(),
                transaction_number=str_schema(),
                shipment_datetime=str_schema(),
                from_city=str_schema(),
                from_state=str_schema(),
                to_city=str_schema(),
                to_state=str_schema(),
                quote=null_dict_schema(
                    id=num_schema(),
                    transaction_id=num_schema(),
                    vehicle_request_id=num_schema(),
                    user_id=num_schema(),
                    quantity=num_schema(gt=0, multiple_of=1),
                    amount=num_schema(),
                    comments=null_str_schema()
                )
            )
        )
    )


def vehicle_status_schema():
    return enum_schema(['loading', 'unloading', 'loaded', 'unloaded'], type='string')


def fms_track_vehicles_schema():
    return status_msg_extra_schema(
        data=list_schema(
            schema=dict_schema(
                vehicle_id=num_schema(),
                vehicle_number=str_schema(),
                vehicle_status=vehicle_status_schema(),
                driver=null_dict_schema(
                    id=num_schema(),
                    name=str_schema(),
                    phone=str_schema()
                ),
                location=null_dict_schema(
                    name=str_schema(),
                    district=str_schema(),
                    state=str_schema(),
                    country=str_schema(),
                    latitude=num_schema(gt=-90.0, lt=90.0),
                    longitude=num_schema(gt=-180.0, lt=180.0),
                    time=str_schema()
                ),
                path=list_schema(
                    schema=list_schema(schema=num_schema(), min_items=3, max_items=3)
                ),
                bearing=num_schema(),
            )
        )
    )


def fms_list_vehicles_schema():
    return status_msg_extra_schema(
        data=list_schema(
            schema=dict_schema(
                id=num_schema(),
                vehicle_number=str_schema(),
                vehicle_type=null_num_schema(),
                vehicle_model=null_str_schema(),
            )
        ),
        owners_data=list_schema(
            schema=dict_schema(
                id=num_schema(),
                name=null_str_schema(),
                phone=null_str_schema(),
            )
        ),
        drivers_data=list_schema(
            schema=dict_schema(
                id=num_schema(),
                name=str_schema(),
                phone=str_schema(),
                driving_licence_number=null_str_schema()
            )
        ),
        accounts_data=list_schema(
            schema=account_schema()
        )
    )


def fms_list_drivers_schema():
    return status_msg_extra_schema(
        data=list_schema(
            schema=dict_schema(
                id=num_schema(),
                name=str_schema(),
                phone=str_schema(),
                driving_licence_number=null_str_schema()
            )
        ),
    )


def fms_vehicle_detail_schema():
    return status_msg_extra_schema(
        data=vehicle_schema(null=False)
    )


def fms_driver_detail_schema():
    return status_msg_extra_schema(
        data=driver_schema(null=False)
    )


def vehicle_schema(null=True):
    func = null_dict_schema if null else dict_schema
    return func(
        required_schema_properties=['id', 'vehicle_number', 'rc_doc', 'puc_doc', 'permit_doc', 'fitness_doc',
                                    'insurance_doc', 'vehicle_type',  'registration_year'],
        id=num_schema(),
        vehicle_number=str_schema(),
        owner=owner_schema(),
        driver=driver_schema(),
        driver_app_user=null_dict_schema(),
        vehicle_type=null_num_schema(),
        registration_year=null_str_schema(),
        rc_doc=doc_schema(),
        puc_doc=doc_schema(),
        fitness_doc=doc_schema(),
        permit_doc=doc_schema(),
        insurance_doc=doc_schema(),
        owner_pan_doc=doc_schema(),
        owner_dec_doc=doc_schema(),
        driver_dl_doc=doc_schema(),
        account=account_schema()
    )


def owner_schema(null=True):
    func = null_dict_schema if null else dict_schema
    return func(
        required_schema_properties=['id', 'user_id', 'username', 'user_fullname', 'name', 'phone', 'declaration'],
        id=num_schema(),
        user_id=null_num_schema(),
        username=null_str_schema(),
        user_fullname=null_str_schema(),
        name=null_str_schema(),
        phone=null_str_schema(),
        declaration=null_str_schema(),
        declaration_validity=null_str_schema(),
        declaration_doc=null_dict_schema(),
        account_details=account_schema(),
        address=null_dict_schema(),
        vehicles_detail=null_dict_schema(),
        taxation_details=null_dict_schema(
            id=num_schema(),
            pan=str_schema()
        )
    )


def driver_schema(null=True):
    func = null_dict_schema if null else dict_schema
    return func(
        required_schema_properties=['id', 'name', 'phone', 'driving_licence_number', 'account', 'dl_doc'],
        id=num_schema(),
        name=str_schema(),
        phone=str_schema(),
        driving_licence_number=null_str_schema(),
        account=account_schema(),
        pan_doc=doc_schema(),
        dl_doc=doc_schema(),
    )


def account_schema(null=True):
    func = null_dict_schema if null else dict_schema
    return func(
        required_schema_properties=['id', 'bank', 'account_holder_name', 'account_number', 'account_type', 'ifsc'],
        id=num_schema(),
        bank=null_str_schema(),
        account_holder_name=str_schema(),
        account_number=str_schema(),
        account_type=str_schema(),
        account_type_verbose=str_schema(),
        ifsc=str_schema()
    )


def doc_schema():
    return null_dict_schema(
        required_schema_properties=['url', 'thumb_url', 'doc_id', 'validity'],
        url=null_str_schema(),
        thumb_url=null_str_schema(),
        doc_id=null_str_schema(),
        validity=null_str_schema(),
        manufacture_year=null_str_schema(),
        insurer_name=null_str_schema(),
        permit_type=null_str_schema(),
        issue_location=null_str_schema(),
    )
