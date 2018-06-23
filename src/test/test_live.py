import json
import os
import subprocess
from time import sleep
from urllib2 import urlopen, HTTPError

from pytest import fixture

from orbLib import OaF


@fixture
def running_port():
    port = '8901'
    env = dict(os.environ)
    env['PYTHONPATH'] += ':src'
    proc = subprocess.Popen(['python', './src/test/TestService.py', port],
                            env=env)
    sleep(3)  # Sleep to allow startup
    yield port
    proc.terminate()


def test_start(running_port):
    root_page = urlopen('http://localhost:%s/oaf' % running_port)
    assert root_page.code == 200
    page_text = root_page.read()
    assert 'status: none' in page_text
    assert 'system: ' in page_text
    assert 'message: ' in page_text
    assert 'color: (1, 1, 1)' in page_text
    assert 'blink: 0' in page_text


def test_system(running_port):
    basic_system = urlopen(
        'http://localhost:%s/oaf/BasicSystem' % running_port)
    assert basic_system.code == 200
    page_text = basic_system.read()
    assert 'bgcolor="#ffffff"' in page_text

    basic_system = urlopen(
        'http://localhost:%s/oaf/BasicSystem' % running_port,
        data='status=working&message=Running test')
    assert basic_system.code == 200
    page_text = basic_system.read()
    assert 'bgcolor="#0000ff"' in page_text
    assert '<tr><td>working</td><td>Running test</td>' in page_text

    root_page = urlopen('http://localhost:%s/oaf' % running_port)
    assert root_page.code == 200
    page_text = root_page.read()
    assert 'status: working' in page_text
    assert 'system: Basic System' in page_text
    assert 'message: Running test' in page_text
    assert 'color: (0, 0, 1)' in page_text
    assert 'blink: 5' in page_text


def test_notifier(running_port):
    try:
        basic_notifier = urlopen(
            'http://localhost:%s/oaf/BasicNotifier' % running_port)
    except HTTPError as err:
        assert err.code == 415
        page_text = err.read()
        assert 'No Representation' in page_text
    else:
        assert False, 'Expected 415 Error'

    json_notifier = urlopen(
        'http://localhost:%s/oaf/JsonNotifier' % running_port)
    assert json_notifier.code == 200
    notifier_state = json.loads(json_notifier.read())
    assert notifier_state == {"color": [1, 1, 1],
                              "status": 'none',
                              "message": "Basic System: Basic System",
                              "level": OaF.NONE,
                              "blink": 0}

    basic_system = urlopen(
        'http://localhost:%s/oaf/BasicSystem' % running_port,
        data='status=working&message=Running test')
    assert basic_system.code == 200
    page_text = basic_system.read()
    assert 'bgcolor="#0000ff"' in page_text
    assert '<tr><td>working</td><td>Running test</td>' in page_text

    try:
        basic_notifier = urlopen(
            'http://localhost:%s/oaf/BasicNotifier' % running_port)
    except HTTPError as err:
        assert err.code == 415
        page_text = err.read()
        assert 'No Representation' in page_text
    else:
        assert False, 'Expected 415 Error'

    json_notifier = urlopen(
        'http://localhost:%s/oaf/JsonNotifier' % running_port)
    assert json_notifier.code == 200
    notifier_state = json.loads(json_notifier.read())
    assert notifier_state == {"color": [0, 0, 1],
                              "status": 'working',
                              "message": 'Basic System: Running test',
                              "level": OaF.INFO,
                              "blink": 5}
