# Introduction

This repository provides Python tools for creating, validating, and searching EarthCODE [Open Science Catalog metadata](https://opensciencedata.esa.int/).


## Installation
```bash
pip install earthcode
```

## Publishing to the Open Science catalog

In the `guide/` folder you can find instructions how to publish your results to the Open Science Catalog.
Start with the `guide/0.Prerequisites - local.ipynb` notebook if you are running the examples locally.
Alternatively, start with `guide/0.Prerequisites - local.ipynb` if you are using the EarthCODE workspace.


## Examples
In the examples folder you can find notebooks that show:
- How to use the library to semantically search the Open Science Catalog - `examples/earthcode_data_discovery.ipynb`
- (Experimental) How to combine the library and the OSC editor - `examples/contribute_via_osc_editor.ipynb`
- How to validate a local copy of the catalog and open a PR - `examples/contribute_via_pr_osc.ipynb`


# For Developers:

1. `git clone https://github.com/ESA-EarthCODE/earthcode-library.git`
2. Install pixi - https://pixi.sh/dev/installation/
3. `cd earthcode-library`
4. `pixi install`
5. `pixi run jupyter lab`

You can run tests through `pixi run pytest`. If running on Windows use ` pixi run pytest --basetemp=C:\t` to avoid long path errors, since some of the project names are >260 chars.


# To create a new release and publish it

edit pyproject.toml to 1.1.4 and run

pixi lock
git add pyproject.toml pixi.toml pixi.lock
git commit -m "Release v1.1.4"
git push origin main
git tag -a v1.1.4 -m "Release v1.1.4"
git push origin v1.1.4
