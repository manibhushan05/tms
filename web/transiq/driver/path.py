from datetime import timedelta

import time
from django.utils import timezone

from driver import vw
from driver.models import GPSLogNew


def get_paths(driver_app_user_ids, hours):
    after = timezone.now() - timedelta(hours=hours)
    gps_data = GPSLogNew.objects.filter(
        driver_id__in=driver_app_user_ids, datetime__gt=after
    ).order_by('datetime')
    grouped_data = {}
    for data in gps_data:
        if data.driver_id in grouped_data:
            grouped_data[data.driver_id].append((float(data.latitude), float(data.longitude), timestamp(data.datetime)))
        else:
            grouped_data[data.driver_id] = [(float(data.latitude), float(data.longitude), timestamp(data.datetime))]

    return grouped_data


def simplify(grouped_data, factor):
    res = {}
    for driver_id, path_data in grouped_data.items():
        sim = vw.Simplifier(path_data)
        threshold = factor * sim.th
        simple_path = sim.simplify(threshold=threshold)
        res[driver_id] = simple_path.tolist()
    return res


def timestamp(dt):
    return time.mktime(dt.timetuple())


def get_simple_paths(driver_ids, hours, factor):
    grouped_data = get_paths(driver_ids, hours)
    return simplify(grouped_data, factor)


# tests

def test(d=6, h=48, f=1.0):
    grouped_data = get_paths([d], h)
    res = simplify(grouped_data, f)
    data = grouped_data[d]
    sim_data = res[d]
    plot(data, sim_data)


def test2(f=0.1):
    data = [
        (4, 4), (6, 6), (12, 5), (20, 11), (27, 11), (34, 15), (40, 22),
        (42, 30), (48, 34), (50, 40), (57, 42), (64, 50), (72, 49),
        (74, 52), (77, 52), (83, 47), (86, 38), (91, 33), (95, 27),
        (100, 20), (92, 19), (74, 17), (67, 13), (60, 14), (53, 21),
        (42, 30), (34, 41), (32, 47), (40, 55), (52, 57), (59, 62),
        (65, 64), (70, 65), (77, 62), (89, 60), (94, 52), (107, 51),
        (129, 45), (133, 39), (136, 39), (134, 58), (125, 70), (123, 91),
        (118, 101), (117, 110), (107, 97), (105, 82), (97, 66), (87, 86),
        (82, 107), (76, 122), (72, 129), (68, 140), (61, 133), (59, 136),
        (53, 128), (38, 126), (33, 118), (20, 114), (23, 104), (30, 97),
        (33, 90), (36, 88), (45, 95), (48, 96), (53, 95), (63, 103),
        (85, 116), (93, 120), (89, 111), (82, 107), (79, 100), (75, 98),
        (73, 95), (67, 94), (57, 87), (43, 83), (32, 80), (29, 77),
        (20, 74), (20, 65), (15, 50), (18, 43), (16, 36)
    ]
    data = [(float(a), float(b)) for a, b in data]
    sim = vw.Simplifier(data)
    # if sim.total_length != 0:
    threshold = f * sim.th
    # else:
    #    threshold = 1e-300
    sim_data = sim.simplify(threshold=threshold)
    plot(data, sim_data)


def plot(data, sim_data):
    import matplotlib.pyplot as plt
    d_x = [x[0] for x in data]
    d_y = [x[1] for x in data]
    sd_x = [x[0] for x in sim_data]
    sd_y = [x[1] for x in sim_data]
    plt.plot(d_x, d_y, 'b', sd_x, sd_y, 'r')
    plt.show()
