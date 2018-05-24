dumpdata:
python3 manage.py dumpdata --format=json account > fixtures/init_account.json
python3 manage.py dumpdata --format=json product > fixtures/init_product.json
python3 manage.py dumpdata --format=json main > fixtures/init_main.json
python3 manage.py dumpdata --format=json comment > fixtures/init_comment.json
python3 manage.py dumpdata --format=json user_data > fixtures/init_user_data.json
python3 manage.py dumpdata --format=json transaction > fixtures/init_transaction.json


load data:
python3 manage.py loaddata --format=json fixtures/*.json