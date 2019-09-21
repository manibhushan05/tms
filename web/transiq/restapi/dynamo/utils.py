

class DynamoTable:
    def __init__(self, table):
        self.table = table

    def create(self):
        if not self.table.exists():
            self.table.create_table(wait=True)
        else:
            return -1

    def delete(self):
        if self.table.exists():
            self.table.delete_table()

    def describe_table(self):
        return self.table.describe_table()

    def put_item(self, hash_key, attributes=None):
        if attributes:
            item = self.table(hash_key, **attributes)
        else:
            item = self.table(hash_key)
        item.save()
        return item

    def get_item(self, hash_key):
        try:
            item = self.table.get(hash_key)
        except self.table.DoesNotExist:
            item = None
        return item

    def update_item(self, hash_key, attributes):
        if attributes:
            item = self.table.get(hash_key)
            for key in attributes.keys():
                item.update(
                    actions=[
                        getattr(self.table, str(key)).set(attributes[key])
                    ]
                )
        else:
            item = None
        return item

    def scan(self):
        return self.table.scan()
