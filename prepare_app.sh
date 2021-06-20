#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata initial_data
echo "
from django.contrib.auth.models import User
from image_app.models import AccountTierClass, AccountTier
superuser = User.objects.create_superuser(username='admin', password='secret1')
tier = AccountTierClass.objects.get(name='Enterprise')
AccountTier.add_user_to_account_tier(tier, superuser)
user = User.objects.create_user(username='user', password='secret2')
tier = AccountTierClass.objects.get(name='Basic')
AccountTier.add_user_to_account_tier(tier, user)
" | python manage.py shell
python manage.py runserver 0.0.0.0:8000
