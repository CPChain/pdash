dumpdata:
python manage.py dumpdata --format=json account > fixtures/init_account.json
python manage.py dumpdata --format=json product > fixtures/init_product.json
python manage.py dumpdata --format=json main > fixtures/init_main.json
python manage.py dumpdata --format=json comment > fixtures/init_comment.json
python manage.py dumpdata --format=json user_data > fixtures/init_user_data.json
python manage.py dumpdata --format=json transaction > fixtures/init_transaction.json


load data:
python manage.py loaddata --format=json fixtures/*.json