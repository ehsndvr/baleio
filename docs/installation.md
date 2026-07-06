# Installation

baleio requires **Python 3.9+**.

## From PyPI

```bash
pip install baleio
```

## From source

```bash
git clone https://github.com/ehsndvr/baleio
cd baleio
pip install -e .
```

## Dependencies

baleio pulls in a small, well-established stack:

| Package | Purpose |
|---|---|
| [`aiohttp`](https://docs.aiohttp.org/) | async HTTP client/server |
| [`pydantic`](https://docs.pydantic.dev/) v2 | typed API models & validation |
| [`magic-filter`](https://github.com/aiogram/magic-filter) | the magic `F` filter |
| `certifi` | up-to-date CA bundle for TLS |

## Development install

To work on baleio itself (tests, docs):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Getting a bot token

Talk to [@botfather](https://ble.ir/botfather) in Bale to create a bot and receive a
token that looks like `123456789:XXXXXXXXXXXXXXXXXXXXXXXXXXX`. Pass it to `Bot(token)`.
