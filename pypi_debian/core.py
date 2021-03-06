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


PYPI_JSON_URL = "https://pypi.python.org/pypi/{}/json"


@view_config(route_name="project.index", renderer="project.html")
def project_index(request, project):
    # Fetch the data from PyPI
    try:
        resp = requests.get(PYPI_JSON_URL.format(project))
        resp.raise_for_status()
    except requests.HTTPError as exc:
        if exc.response.status_code == 404:
            raise HTTPNotFound("Could not find project '{}'".format(project))
        raise
    data = resp.json()

    # Sort the data from PyPI
    releases = collections.OrderedDict()
    for version, files in sorted(data["releases"].items()):
        releases[version] = sorted(files, key=lambda x: x["filename"])

    return {"project": data["info"], "releases": releases}


@view_config(route_name="project.file")
def project_file(request, project, filename):
    # Get the data from PyPI
    try:
        resp = requests.get(PYPI_JSON_URL.format(project))
        resp.raise_for_status()
    except requests.HTTPError as exc:
        if exc.response.status_code == 404:
            raise HTTPNotFound("Could not find project '{}'".format(project))
    data = resp.json()

    # Determine if we're looking for a signature file and if we are correct
    # the filename to the non signature filename.
    if filename.endswith(".asc"):
        sig = True
        filename = filename[:-4]
    else:
        sig = False

    # Find out the URL on PyPI that points to this filename.
    for version, files in data["releases"].items():
        for file_ in files:
            if file_["filename"] == filename:
                # If we're looking for a signature, and this file has a
                # signature then we'll redirect to this URL.
                if sig and file_["has_sig"]:
                    return HTTPMovedPermanently(file_["url"] + ".asc")
                # If we're looking for a signature, and this file does not have
                # a signature then continue on looking for more files.
                elif sig:
                    continue
                # If we're not looking for a signature then redirect to this
                # URL.
                else:
                    return HTTPMovedPermanently(file_["url"])

    # If we've gotten to this point, then we were unable to find a filename
    # that matches the given filename for this project.
    raise HTTPNotFound(
        "Could not find filename '{}' for project '{}'".format(
            filename, project,
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
