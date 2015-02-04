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

import collections

import requests

from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPMovedPermanently, HTTPNotFound
from pyramid.view import view_config

from .mapper import PyPIDebianMapper


@view_config(route_name="project.index", renderer="project.html")
def project_index(request, project):
    # Fetch the data from PyPI
    resp = requests.get("https://pypi.python.org/pypi/{}/json".format(project))
    resp.raise_for_status()
    data = resp.json()

    # Sort the data from PyPI
    releases = collections.OrderedDict()
    for version, files in sorted(data["releases"].items()):
        releases[version] = sorted(files, key=lambda x: x["filename"])

    return {"project": data["info"], "releases": releases}


@view_config(route_name="project.file")
def project_file(request, project, filename):
    # Get the data from PyPI
    resp = requests.get("https://pypi.python.org/pypi/{}/json".format(project))
    resp.raise_for_status()
    data = resp.json()

    # Find out the URL on PyPI that points to this filename
    for version, files in data["releases"].items():
        for file_ in files:
            if file_["filename"] == filename:
                return HTTPMovedPermanently(file_["url"])

    raise HTTPNotFound(
        "Could not find filename '{}' for project '{}'".format(
            project,
            filename,
        )
    )


def configure(settings=None):
    if settings is None:
        settings = {}

    config = Configurator(settings=settings)

    # Setup our custom view mapper, this will provide one thing:
    #   * Pass matched items from views in as keyword arguments to the
    #     function.
    config.set_view_mapper(PyPIDebianMapper)

    # We'll want to use Jinja2 as our template system.
    config.include("pyramid_jinja2")

    # We also want to use Jinja2 for .html templates as well, because we just
    # assume that all templates will be using Jinja.
    config.add_jinja2_renderer(".html")

    # We'll store all of our templates in one location, warehouse/templates
    # so we'll go ahead and add that to the Jinja2 search path.
    config.add_jinja2_search_path("pypi_debian:templates", name=".html")

    # Add our routes to the configuration.
    config.add_route("project.index", "/{project}/")
    config.add_route("project.file", "/{project}/{filename}")

    # Scan everything for configuration
    config.scan()

    return config
