from django.db import models


class CityManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class AahoOfficeManager(models.Manager):
    def get_by_natural_key(self, branch_name,branch_head):
        return self.get(branch_name=branch_name,branch_head=branch_head)
