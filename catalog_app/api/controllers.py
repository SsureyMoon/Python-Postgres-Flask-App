#!/usr/bin/env python

"""controllers.py
This module handles requests and responses of
        retrieving and storing data of category and item.
Attributes:
    basic: Flask blueprint instance which bind / url

Functions:
    showMain()
    showItemList(category_id)
    showItemDetail(category_id, item_id)
    addItem()
    editItem(category_id, item_id)
    deleteItem(item_id)
    getAllContent()
    getJsonItemList(category_id)
    getJsonItemDetail(category_id, item_id)

created on 13/June/2014
"""
import json

from flask import render_template, Blueprint, request,\
    redirect, url_for, flash, jsonify, make_response

from catalog_app import session
from catalog_app.api.models import User, Category, Item
from util import validate_token


basic = Blueprint('basic', __name__)


@basic.route('/')
def showMain():
    """Render the main page contain all categories and most recent items
        GET /
    """
    # Check if user is authenticated
    token = request.cookies.get('token')
    expire_time = request.cookies.get('expire_time')
    user_data = None
    if token:
        user_data = validate_token(token, expire_time)

    # SQL model method which retrieve all categories.
    categories = Category.get_all(session, order_by=Category.name,
                                  ascending=True)
    # SQL model method which retrieve most recent 10 items.
    items = Item.get_recent(session, limit=10)
    # Show user a different view which contains 'add item' link
    #     if user_data is not None, which means an authenticated user.
    return render_template('main.html', categories=categories,
                           items=items, user=user_data)


@basic.route('/category/<int:category_id>/')
def showItemList(category_id):
    """Render the page contain all categories
           and all items in a selected category
        GET /category/category id/
        Example:
            GET /category/1/ shows a list of items in category 1
    """
    # Check if user is authenticated
    token = request.cookies.get('token')
    expire_time = request.cookies.get('expire_time')
    user_data = None
    if token:
        user_data = validate_token(token, expire_time)

    # SQL model method which retrieve all categories.
    categories = Category.get_all(session, order_by=Category.created,
                                  ascending=True)

    # SQL model method which retrieve a category row by its' id.
    category = Category.get_by_id(session, category_id)
    if category:
        # SQL model method which retrieve all items in their category's id.
        items = Category.item_set(session, category.id)
    else:
        items = []
    # Show user a different view which contains 'add item' link
    #     if user_data is not None, which means an authenticated user.
    return render_template('show_item_list.html', categories=categories,
                           category=category, items=items, user=user_data)


@basic.route('/category/<int:category_id>/item/<int:item_id>')
def showItemDetail(category_id, item_id):
    """Render the detail page of a selected item
        GET /category/category id/item/item id
        Example:
            GET /category/1/item/2 shows the detail of the item 2
                in the category 1
    """
    token = request.cookies.get('token')
    expire_time = request.cookies.get('expire_time')
    user_data = None
    if token:
        user_data = validate_token(token, expire_time)
    category = Category.get_by_id(session, category_id)
    item = Item.get_by_id(session, item_id)
    # Show user a different view which contains 'edit' and 'delete' link
    #     if user_data is not None, which means an authenticated user.
    return render_template('show_item_detail.html',
                           category=category, item=item, user=user_data)


@basic.route('/items/', methods=['GET', 'POST'])
def addItem():
    """
        GET /items:
            Render a create item form page
        POST /items:
            Create a new item and store it in database.
            Fields:
                title (required)
                description
                category (required)
            Created date are default saved as timestamp
    """
    token = request.cookies.get('token')
    expire_time = request.cookies.get('expire_time')
    # Only authenticated user can add a new item
    if not token:
        flash("Please login.")
        return redirect(url_for('auth.login'))

    if request.method == "GET":
        user_data = validate_token(token, expire_time)
        categories = Category.get_all(session)
        return render_template('add_item.html',
                               categories=categories, user=user_data)

    if request.method == "POST":
        # When user send POST request,
        #     we get a token again from HTTP header, not from cookie
        token = request.headers.get('Authorization')
        # Only authenticated user can add a new item
        user_data = validate_token(token, expire_time)
        if not user_data:
            response = make_response(
                json.dumps({
                    "message": "Please login",
                    "redirect": url_for('auth.login')
                }), 401
            )
            response.headers['Content-Type'] = 'application/json'
            return response

        # Get title, description, and category_id from the form.
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category')

        # In the form in HTML title field is required.
        # No title means the user use another way to send POST request
        if not title:
            response = make_response(
                json.dumps({
                    "message": "Please use the proper way",
                    "redirect": url_for('basic.addItem')
                }), 401
            )
            response.headers['Content-Type'] = 'application/json'
            return response

        # Create a new item row with the fields user has inputted
        item = Item(title=title, description=description,
                    category_id=category_id, user_id=user_data.get("id"))
        session.add(item)
        session.commit()
        # Redirect to the detail page, so user can check their input.
        response = make_response(
            json.dumps({
                "message": "The item was successfully created.",
                "redirect": url_for('basic.showItemDetail',
                                    category_id=category_id, item_id=item.id)
                }), 200
            )
        response.headers['Content-Type'] = 'application/json'
        return response


@basic.route('/category/<int:category_id>/item/<int:item_id>/edit',
             methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """
        GET /category/category id/item/item id/edit:
            Render an edit item form page
        POST /category/category id/item/item id/edit:
            Update the selected item's attributes
            Fields:
                title (required)
                description
                category (required)
    """
    token = request.cookies.get('token')
    expire_time = request.cookies.get('expire_time')
    # Only authorized user can see an edit item page
    if not token:
        flash("You are not authorized.")
        return redirect(url_for('basic.showMain'))

    if request.method == "GET":

        # Only authorized user can see an edit item page
        user_data = validate_token(token, expire_time)
        if not user_data:
            flash("You are not authorized.")
            return redirect(url_for('basic.showMain'))

        # Only authorized user can see an edit item page
        # Authorized user id must be the same as
        #     the user's id who created the item before.
        if not User.is_authorized(session, user_data.get("id"), item_id):
            flash("You are not authorized.")
            return redirect(url_for('basic.showMain'))

        categories = Category.get_all(session)
        item = Item.get_by_id(session, item_id)
        return render_template('edit_item.html',
                               categories=categories, item=item)

    if request.method == "POST":
        # When user send POST request,
        #     we get a token again from HTTP header, not from cookie
        token = request.headers.get('Authorization')
        # Only authorized user can edit this item
        user_data = validate_token(token, expire_time)
        if not user_data:
            response = make_response(
                json.dumps({
                    "message": "You are not authorized",
                    "redirect": url_for('basic.showItemDetail',
                                        category_id=category_id,
                                        item_id=item_id)
                }), 401
            )
            response.headers['Content-Type'] = 'application/json'
            return response

        item = Item.get_by_id(session, item_id)
        title = request.form.get('title')
        description = request.form.get('description')
        new_category_id = request.form.get('category')

        # In the form in HTML title field is required.
        # No title means the user use another way to send POST request
        if not title:
            response = make_response(
                json.dumps({
                    "message": "Please use the proper way",
                    "redirect": url_for('basic.showItemDetail',
                                        category_id=category_id,
                                        item_id=item_id)
                }), 401
            )
            response.headers['Content-Type'] = 'application/json'
            return response

        # Only authorized user can edit item
        # Authorized user id must be the same as
        #     the user's id who created the item before.
        user = User.get_by_id(session, user_data.get("id"))
        if not User.is_authorized(session, user.id, item_id):
            response = make_response(
                json.dumps({
                    "message": "You are not authorized",
                    "redirect": url_for('basic.showItemDetail',
                                        category_id=item.category_id,
                                        item_id=item_id)
                }), 401
            )
            response.headers['Content-Type'] = 'application/json'
            return response

        item.title = title
        item.description = description
        item.category_id = new_category_id
        session.add(item)
        session.commit()

        response = make_response(
            json.dumps({
                "message": "The item was successfully edited.",
                "redirect": url_for('basic.showItemDetail',
                                    category_id=category_id,
                                    item_id=item.id)
            }), 200
        )
        response.headers['Content-Type'] = 'application/json'
        return response


@basic.route('/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id):
    """
        GET /item/item id/delete:
            Render an delete item form page
        POST /item/item id/delete:
            Delete the selected item from database
    """
    token = request.cookies.get('token')
    expire_time = request.cookies.get('expire_time')
    # Only authorized user can see an edit item page
    if not token:
        flash("You are not authorized.")
        return redirect(url_for('basic.showMain'))

    if request.method == "GET":
        # Only authorized user can see a delete item page
        user_data = validate_token(token, expire_time)
        if not user_data:
            flash("You are not authorized.")
            return redirect(url_for('basic.showMain'))

        item = Item.get_by_id(session, item_id)
        return render_template('delete_item.html', item=item, user=user_data)

    if request.method == "POST":
        # When user send POST request,
        #     we get a token again from HTTP header, not from cookie
        token = request.headers.get('Authorization')
        # Get item to delete
        item = Item.get_by_id(session, item_id)
        # Only authorized user can delete this item
        user_data = validate_token(token, expire_time)
        if not user_data:
            response = make_response(
                json.dumps({
                    "message": "You are not authorized",
                    "redirect": url_for('basic.showItemDetail',
                                        category_id=item.category_id,
                                        item_id=item_id)
                }), 401
            )
            response.headers['Content-Type'] = 'application/json'
            return response

        # Only authorized user can delete an item
        # Authorized user id must be the same as
        #     the user's id who created the item before.
        user = User.get_by_id(session, user_data.get("id"))
        if not User.is_authorized(session, user.id, item_id):
            response = make_response(
                json.dumps({
                    "message": "You are not authorized",
                    "redirect": url_for('basic.showItemDetail',
                                        category_id=item.category_id,
                                        item_id=item_id)
                }), 401
            )
            response.headers['Content-Type'] = 'application/json'
            return response

        session.delete(item)
        session.commit()

        response = make_response(
            json.dumps({
                "message": "The item was successfully deleted.",
                "redirect": url_for('basic.showMain')
            }), 200
        )
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON end-point
@basic.route('/catalog.json')
def getAllContent():
    categories = Category.get_all(session, order_by=Category.name,
                                  ascending=True)
    categories_list = [c.serialize for c in categories]
    for c in categories_list:
        c["items"] = [i.serialize for i in Category.item_set(session, c["id"])]
    result = {
        "status": "success",
        "type": "collection",
        "collection_type": "categories",
        "categories": categories_list
        }
    return jsonify(result)


@basic.route('/category/<int:category_id>/item.json')
def getJsonItemList(category_id):
    category = Category.get_by_id(session, category_id)
    if category:
        items = Category.item_set(session, category.id)
    else:
        items = []

    result = {
        "status": "success",
        "type": "collection",
        "collection_type": "items",
        "category": category.serialize,
        "items": [i.serialize for i in items]
        }
    return jsonify(result)


@basic.route('/category/<int:category_id>/item/<int:item_id>/detail.json')
def getJsonItemDetail(category_id, item_id):
    category = Category.get_by_id(session, category_id)
    item = Item.get_by_id(session, item_id)
    result = {
        "status": "success",
        "type": "attributes",
        "attributes_type": "item",
        "category": category.serialize,
        "item": item.serialize
    }
    return jsonify(result)
