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

from pypi_debian.mapper import PyPIDebianMapper


def test_mapped_function():
    @pretend.call_recorder
    def fake_view(request, foo):
        pass

    request = pretend.stub(matchdict={"foo": "bar"})

    PyPIDebianMapper()(fake_view)(pretend.stub(), request)

    assert fake_view.calls == [pretend.call(request, foo="bar")]
