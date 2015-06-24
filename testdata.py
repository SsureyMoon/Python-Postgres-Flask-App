#!/usr/bin/env python

"""
testdata.py
    import dummy data into database.

created on 13/June/2014

"""


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_app.api.util import encrypt_password, check_password
from catalog_app.api.models import Base, User, Category, Item

from settings import config

# Get engine and session for dummy data importing
engine = create_engine(
    config.DATABASE_URI
)
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy users(10 users)
# Example:
#     Username: user1@email.com ~ user10@email.com
#     Password: user1password ~ user10@password
for i in range(10):
    password = "user{}password".format(i + 1)
    enc, salt = encrypt_password(password)
    user = User(name="user{}".format(i + 1),
                email="user{}@email.com".format(i + 1),
                password=enc, salt=salt)
    session.add(user)
    session.commit()

# Create dummy categories and items(10 categories, 100 items)
# Example:
#     Category: category1 ~ category10
#     Item: item1_c1 ~ item10_c10
for c in range(10):
    category = Category(name="category{}".format(c + 1))
    session.add(category)
    session.commit()

    # 10 items in each category
    for i in range(10):
        item = Item(title="item{}_c{}".format(i + 1, c + 1),
                    category_id=category.id, user_id=(i % 10 + 1))
        item.description = "This is a description of category: \
        {} and item: {}. This item is created by {}"\
            .format(i + 1, c + 1, "user{}".format(i % 10 + 1))
        session.add(item)
        session.commit()

print "inserting rows done!"
