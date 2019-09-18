OpenTimelineIO
=======
[![OpenTimelineIO](docs/_static/OpenTimelineIO@3xDark.png)](http://opentimeline.io)
==============

[![Supported VFX Platform Versions](https://img.shields.io/badge/vfx%20platform-2016--2020-lightgrey.svg)](http://www.vfxplatform.com/)
![Supported Versions](https://img.shields.io/badge/python-2.7%2C%203.6%2C%203.7-blue.svg)
[![Build Status](https://travis-ci.com/PixarAnimationStudios/OpenTimelineIO.svg?branch=master)](https://travis-ci.com/PixarAnimationStudios/OpenTimelineIO)
[![codecov](https://codecov.io/gh/PixarAnimationStudios/OpenTimelineIO/branch/master/graph/badge.svg)](https://codecov.io/gh/PixarAnimationStudios/OpenTimelineIO)
[![docs](https://readthedocs.org/projects/opentimelineio/badge/?version=latest)](https://opentimelineio.readthedocs.io/en/latest/index.html)

Main web site: http://opentimeline.io/

Documentation: https://opentimelineio.readthedocs.io/

GitHub: https://github.com/PixarAnimationStudios/OpenTimelineIO

Discussion group: https://lists.aswf.io/g/otio-discussion

Slack channel: https://academysoftwarefdn.slack.com/messages/CMQ9J4BQC
To join, create an account here first: https://slack.aswf.io/

PUBLIC BETA NOTICE
------------------

OpenTimelineIO is currently in Public Beta. That means that it may be missing
some essential features and there are large changes planned. During this phase
we actively encourage you to provide feedback, requests, comments, and/or
contributions.

Overview
--------

OpenTimelineIO is an interchange format and API for editorial cut information.
OTIO is not a container format for media, rather it contains information about
the order and length of cuts and references to external media.

OTIO includes both a file format and an API for manipulating that format. It
also includes a plugin architecture for writing adapters to convert
from/to existing editorial timeline formats. It also implements a dependency-
less library for dealing strictly with time, `opentime`.

You can provide adapters for your video editing tool or pipeline as needed.
Each adapter allows for import/export between that proprietary tool and the
OpenTimelineIO format.

Documentation
--------------
Documentation, including quick start, architecture, use cases, API docs, and much more, is available on [ReadTheDocs](https://opentimelineio.readthedocs.io/)

Adapters
--------

OpenTimelineIO supports, or plans to support, conversion adapters for many
existing file formats, such as Final Cut Pro XML, AAF, CMX 3600 EDL, etc.

See: https://opentimelineio.readthedocs.io/en/latest/tutorials/adapters.html

Other Plugins
-------------

OTIO also supports several other kinds of plugins, for more information see:

* [Media Linkers](https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-media-linker.html) - Generate media references to local media according to your local conventions.
* [HookScripts](https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-hookscript.html) - Scripts that can run at various points during OTIO execution (_ie_ before the media linker)
* [SchemaDefs](https://opentimelineio.readthedocs.io/en/latest/tutorials/write-a-schemadef.html) - Define OTIO schemas.

Installing / Quick-Start
----------

The python-wrapped version of OpenTimelineIO is publicly available via pypy.  You can install OpenTimelineIO via:

`pip install opentimelineio`

For more details, including how to run the included viewer program, see: https://opentimelineio.readthedocs.io/en/latest/tutorials/quickstart.html

C++ Installation Instructions
-----------------------------

0.  Get the source and deal with submodules:
    + `git clone git@github.com:PixarAnimationStudios/OpenTimelineIO.git`
    + `cd OpenTimelineIO`
    + `git submodule init`
    + `git submodule update`

1. If you want to only build for C++ development (i.e. produce the OTIO C++ libraries and header files), then use cmake:
    + `mkdir build`
    + `cd build`
    + `cmake ..`
    (configure PYTHON_EXECUTABLE, PYTHON_LIBRARY, and CMAKE_INSTALL_PREFIX)
    + `make install`
    
2. If you wish to build only for use with Python, run one of the following two commands:
   + `pip install .`
   + `python setup.py install`
   
3. However, if you want to build for Python but you also want to install the OTIO C++ headers and libraries, then run one of the following two commands
   + `pip install . --install-option=“--cxx-install-root=/home/someone/cxx-otio-root"`
   + `python setup.py install --cxx-install-root=/home/someone/cxx-otio-root`
   
   To compile a C++ file, add the following -I flags:
   + `c++ -c source.cpp -I/home/someone/cxx-otio-root/include -I/home/someone/cxx-otio-root/include/opentimelineio/deps`
   
   To link, add the following -L/-l flags:
   + `c++ ... -L/home/someone/cxx-otio-root/lib -lopentimelineio`
   
   (If you are using only opentime, not opentimelineio, use -lopentime.  Also, you could leave out the second -I flag.)

Example Usage
-------

```
import opentimelineio as otio

timeline = otio.adapters.read_from_file("foo.aaf")
for clip in timeline.each_clip():
  print clip.name, clip.duration()
```

There are more code examples here: https://github.com/PixarAnimationStudios/OpenTimelineIO/tree/master/examples

Also, looking through the unit tests is a great way to see what OTIO can do:
https://github.com/PixarAnimationStudios/OpenTimelineIO/tree/master/tests

OTIO includes a viewer program as well (see the quickstart section for instructions on installing it):

![OTIO View Screenshot](docs/_static/otioview.png)

Developing
-------

If you want to contribute to the project, please see: https://opentimelineio.readthedocs.io/en/latest/tutorials/contributing.html

You can get the latest development version via:

`git clone git@github.com:PixarAnimationStudios/OpenTimelineIO.git OpenTimelineIO`

You can install development dependencies with `pip install .[dev]`

You can also install the PySide2 dependency with `pip install .[view]`

Currently the code base is written against python 2.7, python 3.6 and 3.7, in keeping 
with the pep8 style.  We ask that before you submit a pull request, you:

- run `make test` -- to ensure that none of the unit tests were broken
- run `make lint` -- to conform to pep8
- run `make coverage` -- to detect code which isn't covered

PEP8: https://www.python.org/dev/peps/pep-0008/

Contact
-------

For more information, please visit http://opentimeline.io/
or https://github.com/PixarAnimationStudios/OpenTimelineIO
or join our discussion forum: https://lists.aswf.io/g/otio-discussion

