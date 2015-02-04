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

import pypi_debian.core


def test_wsgi(monkeypatch):
    wsgi_app = pretend.stub()
    configuration = pretend.stub(
        make_wsgi_app=pretend.call_recorder(lambda: wsgi_app),
    )
    configure = pretend.call_recorder(lambda: configuration)
    monkeypatch.setattr(pypi_debian.core, "configure", configure)

    from pypi_debian.wsgi import application

    assert application is wsgi_app
    assert configure.calls == [pretend.call()]
    assert configuration.make_wsgi_app.calls == [pretend.call()]
