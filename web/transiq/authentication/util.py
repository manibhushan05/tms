from django.contrib.auth.models import User, Group


def update_groups():
    g = Group.objects.get(name='emp_group1')
    for user in g.user_set.all():
        user.groups.add(Group.objects.get(name='sales'))
