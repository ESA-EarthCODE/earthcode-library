# earthcode

Python tools for creating, validating, and searching EarthCODE Open Science Catalog metadata.

```bash
pip install earthcode
```

## Development

To run:

1. `git clone https://github.com/ESA-EarthCODE/earthcode-library.git`
2. Install pixi - https://pixi.sh/dev/installation/
3. `cd earthcode-library`
4. `pixi install`
5. `pixi run jupyter lab`

We have examples for:
- `./examples/example_create_osc_entries.ipynb` - shows how to create OSC entries
- `./examples/contribute_via_pr_osc.ipynb` - shows how to add newly created entries to the OSC, using a GitHub pull request
- `./examples/contribute_via_osc_editor.ipynb` - shows how to add entries to the OSC, using a combination of this library and the OSC Editor (a GUI tool)
- `./examples/earthcode_publishing_guide.ipynb` - is a simplified introduction to the OSC and the necessary steps to publish data
