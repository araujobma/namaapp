import subprocess
import signal
import pytest
import os
import pathlib
import requests
import time
import filecmp
import datetime


@pytest.fixture(scope="module")
def app_folder():
    parent_path = pathlib.Path(__file__).parent.resolve()
    grand_parent_path = pathlib.Path(parent_path).parent.resolve()
    return os.path.join(grand_parent_path, 'app')


@pytest.fixture(scope="module")
def start_server(app_folder):
    os.chdir(app_folder)
    p = subprocess.Popen(["flask", "run"])
    # waits the server is ready
    time.sleep(3)
    print(p.pid)
    yield p
    os.kill(p.pid, signal.SIGKILL)


@pytest.fixture()
def test_file_path():
    parent_path = pathlib.Path(__file__).parent.resolve()
    return os.path.join(parent_path, 'dados.txt')


@pytest.fixture()
def test_file_name(test_file_path):
    return os.path.basename(test_file_path)


@pytest.fixture()
def upload_folder():
    return os.environ.get("UPLOAD_FOLDER")


def test_get_home(start_server, upload_folder):
    resp: requests.Response
    resp = requests.get("http://127.0.0.1:5000/")
    assert resp.status_code == 200
    assert "Hello World!" in resp.text


def test_post_home_success(test_file_path, test_file_name, upload_folder, start_server):
    resp: requests.Response
    files = {'file': open(test_file_path, 'rb')}
    resp = requests.post("http://127.0.0.1:5000/", files=files)
    uploaded_file_path = os.path.join(upload_folder, test_file_name)
    assert resp.status_code == 200
    assert test_file_name in os.listdir(upload_folder)
    assert filecmp.cmp(test_file_path, uploaded_file_path, shallow=False)
    fname = pathlib.Path(uploaded_file_path)
    mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime)
    assert (datetime.datetime.now() - mtime).seconds <= 10

