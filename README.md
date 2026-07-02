# Introduction
The EarthCODE Library is a Python package developed to support the creation, validation, and search of Open Science Catalog metadata within the EarthCODE publishing workflow. It provides a shared implementation layer for catalog-related operations, reducing the need for project teams and platforms to maintain separate, ad hoc approaches for generating and checking metadata. This repository includes the core package, a command-line interface, usage examples, publication guides, and a test suite, 
This repository provides Python tools for creating, validating, and searching EarthCODE [Open Science Catalog metadata](https://opensciencedata.esa.int/).

Documentation on usage and guides is maintained at: https://esa-earthcode.github.io/earthcode-library/README.html 

## 1. Installation
```bash
pip install earthcode
```
### Requirements
The *minimum* required Python version if you would like to install the library locally is 3.12


## 2. Quick start
```bash
# 1. Import the library
import earthcode

# 2. Search through the catalog
from earthcode.search import search

# 3. Search through semantix text
# Here we take as an example the search done by semantix text and search the catalog via the collection.id which is known
search(collection_ids="seasfire-cube")[0]

# 4. Filter the products in the catalog
search("global chlorophyll dataset", variable=chlorophyll.id, type="products", mission="sentinel-3")
```

## 3. How to contribute to Open Science Catalogue? 
With `earthcode` library creating new entries in the catalogue is semi-automatic. Please find step by step instructions in the `docs/` folder.
Start by going through the `docs/contributing_to_the_osc` document.

## 4. Search through Open Science Catalogue
In the `examples/` folder you can find notebooks that show:
- How to use the library to semantically search the Open Science Catalog - `examples/earthcode_data_discovery.ipynb`

# Looking for support? 
We are ready to assist you in case you have any questions/found a bug or mistake, please use GitHub Issues to open a ticket!  
Alternatively contact the team via e-mail: earthcode@esa.int 

If you would like to request a specific feature, or any question to the community of Earthcode and library developers, please use the [EarthCODE discourse Technical Support channel](https://discourse-earthcode.eox.at/c/technical-support/8) 

## Development 

If you want to contribute a feature to the library you are welcome to contribute via pull request.
First, fork this repository; then make your suggested change and open a PR against this repo. Make sure to add tests for any new functionality.

### Local  install
1. `git clone https://github.com/ESA-EarthCODE/earthcode-library.git`
2. Install pixi - https://pixi.sh/dev/installation/
3. `cd earthcode-library`
4. `pixi install`
5. `pixi run jupyter lab`

You can run tests through `pixi run pytest`. If running on Windows use ` pixi run pytest --basetemp=C:\t` to avoid long path errors, since some of the project names are >260 chars.

## To publish a realease
Edit pyproject.toml to 1.1.4 and run

- `pixi lock`
- `git add pyproject.toml pixi.toml pixi.lock`
- `git commit -m "Release v1.1.4"`
- `git push origin main`
- `git tag -a v1.1.4 -m "Release v1.1.4"`
- `git push origin v1.1.4`
