import os
import uuid
from collections import ChainMap
from datetime import datetime
from typing import Dict
import pytest
from pytest import StashKey, CollectReport
from pytest_django.fixtures import _disable_migrations
from playwright.sync_api import BrowserType, sync_playwright
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
phase_report_key = StashKey[Dict[str, CollectReport]]()


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    rep = yield
    # store test results for each phase of a call, which can
    # be "setup", "call", "teardown"
    item.stash.setdefault(phase_report_key, {})[rep.when] = rep
    return rep


@pytest.fixture(scope="function")
def page(request):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=True,
        slow_mo=500,
        args=[
            "--no-sandbox",
            "--headless=new",
        ],
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.39 Safari/537.36",
        record_video_dir=settings.MEDIA_ROOT.joinpath("test_video").as_posix(),
        record_video_size={"width": 640, "height": 480},
    )
    context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', { get: () => false, });"
    )
    context.set_default_navigation_timeout(10 * 1000)
    context.set_default_timeout(10 * 1000)
    page = context.new_page()
    page.set_default_timeout(10 * 1000)
    yield page
    video_fp = page.video.path()
    new_video_fp = f"{os.path.split(video_fp)[0]}/{request.node.nodeid.replace('::', '__')}__{datetime.today().strftime('%Y-%m-%d %H-%M-%S')}.webm"
    page.close()
    context.close()
    browser.close()
    playwright.stop()
    report = request.node.stash[phase_report_key]
    if os.path.isfile(video_fp):
        if report["setup"].failed:
            print("setting up a test failed or skipped", request.node.nodeid)
        elif ("call" not in report) or report["call"].failed:
            print("executing test failed or skipped", request.node.nodeid)
            if not os.path.isdir(os.path.split(new_video_fp)[0]):
                os.path.split(new_video_fp)[0]
            if not os.path.isfile(new_video_fp):
                os.rename(video_fp, new_video_fp)
        else:
            os.unlink(video_fp)


class BaseTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=True,
            slow_mo=500,
            args=[
                "--no-sandbox",
                "--headless=new",
            ],
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.39 Safari/537.36",
            record_video_dir=settings.MEDIA_ROOT.joinpath("test_video").as_posix(),
            record_video_size={"width": 640, "height": 480},
        )
        self.context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => false, });"
        )
        self.context.set_default_navigation_timeout(10 * 1000)
        self.context.set_default_timeout(10 * 1000)
        self.page = self.context.new_page()
        self.page.set_default_timeout(10 * 1000)

    def tearDown(self):
        video_fp = self.page.video.path()
        self.page.close()
        self.context.close()
        new_video_fp = f"{os.path.split(video_fp)[0]}/{self.id().replace('.', '__')}__{datetime.today().strftime('%Y-%m-%d %H-%M-%S')}.webm"
        if not os.path.isfile(new_video_fp):
            print(os.rename(video_fp, new_video_fp))


@pytest.fixture
def test_password():
    return "admin@123#"


@pytest.fixture
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs["password"] = test_password
        if "name" not in kwargs:
            kwargs["name"] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
    def make_auto_login(user=None):
        client.login(password=test_password, email=user.email)
        return client, user

    return make_auto_login


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def api_client_with_credentials(db, create_user, api_client):
    user = create_user()
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.fixture(scope="function")
def django_db_setup(
    request,
    django_test_environment: None,
    django_db_blocker,
    django_db_use_migrations: bool,
    django_db_keepdb: bool,
    django_db_createdb: bool,
    django_db_modify_db_settings: None,
) -> None:
    """Top level fixture to ensure test databases are available"""
    from django.test.utils import setup_databases, teardown_databases

    setup_databases_args = {}

    if not django_db_use_migrations:
        _disable_migrations()

    if django_db_keepdb and not django_db_createdb:
        setup_databases_args["keepdb"] = True
