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

import functools

from pyramid.config.views import DefaultViewMapper


class PyPIDebianMapper(DefaultViewMapper):

    def __call__(self, view):
        # Wrap our view with our wrapper which will pull items out of the
        # matchdict and pass it into the given view.
        view = self._wrap_with_matchdict(view)

        return super().__call__(view)

    def _wrap_with_matchdict(self, view):
        @functools.wraps(view)
        def wrapper(context, request):
            kwargs = request.matchdict.copy()
            return view(request, **kwargs)

        return wrapper
