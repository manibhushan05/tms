def stringToInteger(num):
    temp = ''
    for i in num:
        if i == '.':
            break
        elif i.isdigit():
            temp = temp + i
    return int(temp)


def loading_city(transaction):
    city = transaction.loading_unloading_location.filter(type='loading').values_list('city__name', flat=True)
    try:
        return city[0]
    except IndexError:
        return ''


def unloading_city(transaction):
    city = transaction.loading_unloading_location.filter(type='unloading').values_list('city__name', flat=True)
    try:
        return city[0]
    except IndexError:
        return ''


def allocated_vehicle_type(allocated_vehicle_obj):
    if allocated_vehicle_obj.vehicle_number:
        if allocated_vehicle_obj.vehicle_number.vehicle_type:
            return allocated_vehicle_obj.vehicle_number.vehicle_type.vehicle_type + ', ' + allocated_vehicle_obj.vehicle_number.vehicle_type.capacity
    else:
        return ''


def allocated_driver_name(allocated_vehicle_obj):
    if allocated_vehicle_obj.vehicle_number:
        if allocated_vehicle_obj.vehicle_number.driver:
            return allocated_vehicle_obj.vehicle_number.driver.name
    else:
        return ''


def allocated_driver_phone(allocated_vehicle_obj):
    if allocated_vehicle_obj.vehicle_number:
        if allocated_vehicle_obj.vehicle_number.driver:
            return allocated_vehicle_obj.vehicle_number.driver.phone
    else:
        return ''


def allocated_driver_dl(allocated_vehicle_obj):
    if allocated_vehicle_obj.vehicle_number:
        if allocated_vehicle_obj.vehicle_number.driver:
            return allocated_vehicle_obj.vehicle_number.driver.driving_licence_number
    else:
        return ''


