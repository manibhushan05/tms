from api.abstract import GetApiTestCase, UnAbstract


class TestIndexPageNoAuth(GetApiTestCase, UnAbstract):
    def is_json(self):
        return False

    def url(self):
        return '/'


class TestTrackShipmentGet(GetApiTestCase, UnAbstract):
    def is_json(self):
        return False

    def url(self):
        return '/track/'
