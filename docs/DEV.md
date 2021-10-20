Local development
============

We run `pre-commit` to preserve the quality of the code. To set up `pre-commit` run:

```
python3.8 -m venv .venv
. .venv/bin/activate
pip install pre-commit==2.15.0
pre-commit install
pre-commit install --hook-type commit-msg
```
