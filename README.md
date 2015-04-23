# Sly

A Python library for 3D construction from 2D parts. 

Sly is still undergoing heavy development, and some functions may be incomplete
or broken. More documentation is forthcoming.

## Installation

### Dependencies

Sly has several external dependencies:

* [Blender](http://www.blender.org/) of course. Must be version 2.71 or later.
* [GEOS](http://trac.osgeo.org/geos/) - Can be installed via Yum/Apt/Homebrew/etc. 
  Seems the only Windows binary is through [OSGeo4W](http://trac.osgeo.org/osgeo4w/).
* Various Python Modules (See next step)


### Installing Sly and Python dependencies in Blender (Easy way)

Since some of the Python dependencies rely on C modules, Sly can't have a
platform-independent release with all the deps rolled in. I've created a zipfile
for OS X, but for other platforms you'll need to use the hard way below.

1. Download the sly-osx-addon.zip file from the releases page
2. Open the Blender preferences and go to the *Add-ons* tab
3. Click *Install from File...* at the bottom and select the
   zipfile.
4. You're done! Sly is immediately available in Blender's Python
   environment; no restart required.


### Installing Sly and Python dependencies in Blender (Hard way)

This method requires a local Python3 installation and some familiarity dealing with
Python packages. Commands should work in any Unixy environment; YMMV.

1. Clone or download this repository and cd into the directory
2. Create a virtualenv so you can more easily find the modules you install:

   ```virtualenv --python=/path/to/python3 ./sly-venv```
3. Switch into the virtualenv:

   ```source ./sly-venv/bin/activate```
4. Install the dependencies:

   ```pip install -r requirements.txt```
5. Figure out where to put the modules so that Blender can find them.

   For Windows:

        C:\Documents and Settings\{username}\AppData\Roaming\Blender Foundation\Blender\{version}\scripts\addons\

   For Unix/Linux/etc:

        $HOME/.config/blender/{version}/scripts/addons/

    For OS X:

        /Users/{user}/Library/Application Support/Blender/{version}/scripts/addons/

6. Copy the following files and directories from `sly-venv/lib/python3.4/site-packages`
   to the path in the above step: `Cython/`, `cython.py`, `pyparsing.py`, `pyximport/`,
   `shapely/`, `svgwrite/`, `triangle/`.
7. Copy the sly/ directory (the one which contains `__init__.py`, not the whole repo) to 
   the same path.

## Usage

See examples/chair.blend
