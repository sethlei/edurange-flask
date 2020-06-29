# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import logging
import os

import pytest

from flask.testing import FlaskClient

from webtest import TestApp

from autoapp import Aid, Iid, create_all_group, create_admin
from edurange_refactored.app import create_app
from edurange_refactored.database import db as _db
from edurange_refactored.user.models import User, StudentGroups

from .factories import UserFactory, GroupFactory


@pytest.fixture
def app():
    """Create application for the tests."""
    _app = create_app("tests.settings")
    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()


    _app.jinja_env.globals.update(Aid=Aid)
    _app.jinja_env.globals.update(Iid=Iid)



    yield _app



    ctx.pop()


@pytest.fixture
def testapp(app):
    """Create Webtest app."""
    return TestApp(app)


@pytest.fixture
def db(app):
    """Create database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

        admin = User.query.limit(1).all()
        print(admin)
        print(admin)
        print(admin)
        if not admin:
            create_admin()

        group = StudentGroups.query.limit(1).all()
        admin = User.query.filter_by(username=os.environ['USERNAME']).first()
        a_id = admin.get_id()
        if not group:
            create_all_group()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """Create user for the tests."""
    user = UserFactory(password="myprecious")
    db.session.commit()
    return user

@pytest.fixture
def admin(db, testapp):
    """Create admin user for the tests."""
    admin = UserFactory(username="admin", password="myprecious")
    admin.is_admin = True
    db.session.commit()

    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form in navbar
    form = res.forms["loginForm"]
    form["username"] = admin.username
    form["password"] = "myprecious"
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200
    return admin

@pytest.fixture
def group(db):
    """Create group for the tests."""
    group = GroupFactory()
    db.session.commit()
    return group

