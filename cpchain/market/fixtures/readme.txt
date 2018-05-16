dumpdata:
python manage.py dumpdata --format=json account product main comment user_data > fixtures/init_data.json


load data:
python manage.py loaddata --format=json fixtures/init_data.json