# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pretend
import pytest
import requests

from pyramid.httpexceptions import HTTPNotFound

import pypi_debian.core
from pypi_debian.core import project_index, project_file, configure
from pypi_debian.mapper import PyPIDebianMapper


class TestProjectIndex:

    def test_project_found(self, monkeypatch):
        resp = pretend.stub(
            raise_for_status=lambda: None,
            json=lambda: {
                "info": {"name": "FooBar"},
                "releases": {
                    "1.0": [{
                        "url": "https://example.com/FooBar-1.0.tar.gz",
                        "filename": "FooBar-1.0.tar.gz",
                        "has_sig": True,
                    }]
                }
            }
        )
        get = pretend.call_recorder(lambda url: resp)
        monkeypatch.setattr(requests, "get", get)

        result = project_index(pretend.stub(), project="FooBar")

        assert get.calls == [
            pretend.call("https://pypi.python.org/pypi/FooBar/json"),
        ]
        assert result == {
            "project": {"name": "FooBar"},
            "releases": {
                "1.0": [
                    {
                        "url": "https://example.com/FooBar-1.0.tar.gz",
                        "filename": "FooBar-1.0.tar.gz",
                        "has_sig": True,
                    },
                ],
            },
        }

    def test_project_not_found(self, monkeypatch):
        def raise_for_status():
            exc = requests.HTTPError()
            exc.response = pretend.stub(status_code=404)
            raise exc

        resp = pretend.stub(raise_for_status=raise_for_status)
        get = pretend.call_recorder(lambda url: resp)

        monkeypatch.setattr(requests, "get", get)

        with pytest.raises(HTTPNotFound):
            project_index(pretend.stub(), project="FooBar")

        assert get.calls == [
            pretend.call("https://pypi.python.org/pypi/FooBar/json"),
        ]

    def test_project_other_error(self, monkeypatch):
        def raise_for_status():
            exc = requests.HTTPError()
            exc.response = pretend.stub(status_code=503)
            raise exc

        resp = pretend.stub(raise_for_status=raise_for_status)
        get = pretend.call_recorder(lambda url: resp)

        monkeypatch.setattr(requests, "get", get)

        with pytest.raises(requests.HTTPError):
            project_index(pretend.stub(), project="FooBar")

        assert get.calls == [
            pretend.call("https://pypi.python.org/pypi/FooBar/json"),
        ]


class TestProjectFile:

    def test_found(self, monkeypatch):
        resp = pretend.stub(
            raise_for_status=lambda: None,
            json=lambda: {
                "releases": {
                    "1.0": [{
                        "url": "https://example.com/FooBar-1.0.tar.gz",
                        "filename": "FooBar-1.0.tar.gz",
                        "has_sig": True,
                    }]
                }
            }
        )
        get = pretend.call_recorder(lambda url: resp)
        monkeypatch.setattr(requests, "get", get)

        response = project_file(
            pretend.stub(), project="FooBar", filename="FooBar-1.0.tar.gz",
        )

        assert get.calls == [
            pretend.call("https://pypi.python.org/pypi/FooBar/json"),
        ]
        assert response.status_code == 301
        assert response.headers["Location"] == \
            "https://example.com/FooBar-1.0.tar.gz"

    def test_found_sig(self, monkeypatch):
        resp = pretend.stub(
            raise_for_status=lambda: None,
            json=lambda: {
                "releases": {
                    "1.0": [{
                        "url": "https://example.com/FooBar-1.0.tar.gz",
                        "filename": "FooBar-1.0.tar.gz",
                        "has_sig": True,
                    }]
                }
            }
        )
        get = pretend.call_recorder(lambda url: resp)
        monkeypatch.setattr(requests, "get", get)

        response = project_file(
            pretend.stub(), project="FooBar", filename="FooBar-1.0.tar.gz.asc",
        )

        assert get.calls == [
            pretend.call("https://pypi.python.org/pypi/FooBar/json"),
        ]
        assert response.status_code == 301
        assert response.headers["Location"] == \
            "https://example.com/FooBar-1.0.tar.gz.asc"

    def test_project_not_found(self, monkeypatch):
        def raise_for_status():
            exc = requests.HTTPError()
            exc.response = pretend.stub(status_code=404)
            raise exc

        resp = pretend.stub(raise_for_status=raise_for_status)
        get = pretend.call_recorder(lambda url: resp)

        monkeypatch.setattr(requests, "get", get)

        with pytest.raises(HTTPNotFound):
            project_file(
                pretend.stub(), project="FooBar", filename="FooBar-1.0.tar.gz",
            )

        assert get.calls == [
            pretend.call("https://pypi.python.org/pypi/FooBar/json"),
        ]

    def test_file_not_found(self, monkeypatch):
        resp = pretend.stub(
            raise_for_status=lambda: None,
            json=lambda: {
                "releases": {
                    "1.0": [{
                        "url": "https://example.com/FooBar-1.0.tar.gz",
                        "filename": "FooBar-1.0.tar.gz",
                        "has_sig": True,
                    }]
                }
            }
        )
        get = pretend.call_recorder(lambda url: resp)
        monkeypatch.setattr(requests, "get", get)

        with pytest.raises(HTTPNotFound):
            project_file(
                pretend.stub(), project="FooBar", filename="FooBar-1.1.tar.gz",
            )

        assert get.calls == [
            pretend.call("https://pypi.python.org/pypi/FooBar/json"),
        ]

    def test_sig_not_found(self, monkeypatch):
        resp = pretend.stub(
            raise_for_status=lambda: None,
            json=lambda: {
                "releases": {
                    "1.0": [{
                        "url": "https://example.com/FooBar-1.0.tar.gz",
                        "filename": "FooBar-1.0.tar.gz",
                        "has_sig": False,
                    }]
                }
            }
        )
        get = pretend.call_recorder(lambda url: resp)
        monkeypatch.setattr(requests, "get", get)

        with pytest.raises(HTTPNotFound):
            project_file(
                pretend.stub(),
                project="FooBar",
                filename="FooBar-1.0.tar.gz.asc",
            )

        assert get.calls == [
            pretend.call("https://pypi.python.org/pypi/FooBar/json"),
        ]


@pytest.mark.parametrize("settings", [None, {"foo": "bar"}])
def test_configure(monkeypatch, settings):
    configurator_obj = pretend.stub(
        set_view_mapper=pretend.call_recorder(lambda x: None),
        include=pretend.call_recorder(lambda x: None),
        add_jinja2_renderer=pretend.call_recorder(lambda x: None),
        add_jinja2_search_path=pretend.call_recorder(lambda x, name: None),
        add_route=pretend.call_recorder(lambda x, y: None),
        scan=pretend.call_recorder(lambda: None),
    )
    configurator = pretend.call_recorder(lambda settings: configurator_obj)
    monkeypatch.setattr(pypi_debian.core, "Configurator", configurator)

    assert configure(settings=settings) is configurator_obj

    assert configurator.calls == [
        pretend.call(settings=settings if settings is not None else {}),
    ]
    assert configurator_obj.set_view_mapper.calls == [
        pretend.call(PyPIDebianMapper),
    ]
    assert configurator_obj.include.calls == [pretend.call("pyramid_jinja2")]
    assert configurator_obj.add_jinja2_renderer.calls == [
        pretend.call(".html"),
    ]
    assert configurator_obj.add_jinja2_search_path.calls == [
        pretend.call("pypi_debian:templates", name=".html"),
    ]
    assert configurator_obj.add_route.calls == [
        pretend.call("project.index", "/{project}/"),
        pretend.call("project.file", "/{project}/{filename}"),
    ]
    assert configurator_obj.scan.calls == [pretend.call()]
