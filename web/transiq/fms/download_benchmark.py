import zipfile
from io import BytesIO

import requests
import time

from fms.doc import s3_url

from multiprocessing import Pool


"""
Benchmark for async download,

result = compare(times=20, processes=8)

result shows that downloading async is up to 5 times faster, but it also has to be more fault tolerant


result = {
  'async': {'average': 1.0615207195281982,
  'average_download': 1.0628360152244567,
  'error': 0,
  'results': [(0.5692601203918457, 0.5680360794067383, 3),
   (0.41873693466186523, 0.41751599311828613, 0),
   (0.7808980941772461, 0.7796981334686279, 1),
   (0.41937899589538574, 0.4181509017944336, 0),
   (0.3948028087615967, 0.3935220241546631, 0),
   (0.723128080368042, 0.7218501567840576, 1),
   (0.4541621208190918, 0.4528369903564453, 0),
   (0.4141390323638916, 0.41295790672302246, 0),
   (0.6156971454620361, 0.6144640445709229, 2),
   (0.470905065536499, 0.4686601161956787, 0),
   (5.409278869628906, 5.407970905303955, 0),
   (0.8919570446014404, 0.8906300067901611, 6),
   (0.7923140525817871, 0.7909939289093018, 1),
   (0.6640529632568359, 0.6626091003417969, 1),
   (0.7180159091949463, 0.7167630195617676, 5),
   (5.369326114654541, 5.368098974227905, 2),
   (0.3970630168914795, 0.3957540988922119, 0),
   (0.819390058517456, 0.8181710243225098, 4),
   (0.4796760082244873, 0.47841310501098633, 0),
   (0.45453786849975586, 0.45331788063049316, 0)],
  'success': 20,
  'timeouts': 26,
  'total': 21.230414390563965,
  'total_download': 21.256720304489136},
 'sync': {'average': 4.577543342113495,
  'average_download': 4.5799590110778805,
  'error': 0,
  'results': [(3.0104808807373047, 3.0083088874816895, 0),
   (8.653135061264038, 8.650620937347412, 2),
   (3.460524082183838, 3.458127975463867, 2),
   (12.719703912734985, 12.717881917953491, 0),
   (2.790576934814453, 2.788295030593872, 0),
   (3.1375458240509033, 3.1350820064544678, 1),
   (8.127126932144165, 8.124743938446045, 1),
   (3.216603994369507, 3.2138969898223877, 1),
   (8.340095043182373, 8.337708950042725, 1),
   (3.0222511291503906, 3.019767999649048, 1),
   (2.892751932144165, 2.8903539180755615, 0),
   (2.9099061489105225, 2.9031760692596436, 0),
   (2.840101957321167, 2.8377511501312256, 0),
   (8.025404214859009, 8.023483991622925, 0),
   (2.7491061687469482, 2.7465641498565674, 0),
   (3.0193281173706055, 3.0185999870300293, 1),
   (4.005234003067017, 4.002815008163452, 3),
   (3.2486300468444824, 3.2480151653289795, 1),
   (2.8174920082092285, 2.8149828910827637, 0),
   (2.6131818294525146, 2.610689878463745, 0)],
  'success': 20,
  'timeouts': 14,
  'total': 91.5508668422699,
  'total_download': 91.59918022155762}
}

"""


def compare(times=10, **kwargs):
    sync_rep = test_func(test_sync, times=times, **kwargs)
    async_rep = test_func(test_async, times=times, **kwargs)

    return {
        'sync': sync_rep,
        'async': async_rep
    }


def test_func(func, times=10, **kwargs):
    results = []
    total = [0.0, 0.0, 0]
    errors = 0

    for i in range(times):
        try:
            res = func(**kwargs)
            results.append(res)
            total[0] += res[0]
            total[1] += res[1]
            total[2] += res[2]
        except AssertionError:
            errors += 1

    count = len(results)
    total_dl, total_total, total_timeouts = total
    report = {
        'results': results,
        'success': count,
        'error': errors,
        'total_download': total_dl,
        'total': total_total,
        'timeouts': total_timeouts
    }
    if not count:
        return report

    report['average_download'] = total_dl / count
    report['average'] = total_total / count

    return report


def download(d):
    fname, url = d
    max_retries = 5
    timeouts = 0
    for i in range(max_retries):
        if i != 0:
            pass
        try:
            response = requests.get(url, timeout=0.2)
            return d, response.content, timeouts
        except Exception:
            pass
            timeouts += 1
    return d, None, timeouts


def test_sync(**kwargs):
    s3_keys = ['test1.png', 'test2.png', 'test3.png', 'test4.png', 'test5.png', 'test6.png', 'test7.png', 'test8.png']
    s3_data = [(k, s3_url(k)) for k in s3_keys]
    bytes_io = BytesIO()
    zip_file = zipfile.ZipFile(bytes_io, 'w')

    total_timeouts = 0
    results = []
    start = time.time()
    for d in s3_data:
        _, content, timeouts = download(d)
        if not content:
            raise AssertionError('no content')
        results.append((d, content))
        total_timeouts += timeouts
    dl_duration = time.time() - start

    for (f, u), r in results:
        zip_file.writestr(f, r)

    zip_file.close()
    res = bytes_io.getvalue()
    duration = time.time() - start
    return duration, dl_duration, total_timeouts


def test_async(processes=4, **kwargs):
    s3_keys = ['test1.png', 'test2.png', 'test3.png', 'test4.png', 'test5.png', 'test6.png', 'test7.png', 'test8.png']
    s3_data = [(k, s3_url(k)) for k in s3_keys]
    bytes_io = BytesIO()
    zip_file = zipfile.ZipFile(bytes_io, 'w')
    pool = Pool(processes=processes)

    total_timeouts = 0
    start = time.time()
    results = pool.map(download, s3_data)
    for d, r, t in results:
        if not r:
            raise AssertionError('no content')
        total_timeouts += t
    dl_duration = time.time() - start

    for (f, u), r, t in results:
        zip_file.writestr(f, r)

    zip_file.close()
    res = bytes_io.getvalue()
    duration = time.time() - start
    return duration, dl_duration, total_timeouts
