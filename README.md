# Skeleton
Sentence skeleton extraction from the Lore knowledge base to improve TRIPS parser.

First of all, install all the requirements

    pip install -r requirements.txt

After that, run django migration

    python manage.py migrate

To load sentences into the database,

    python manage.py loadsentences -i data/input/money_sentence


