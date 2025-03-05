# Bike 2 Work

## Setup

### Install deps

```bash
pip install -r requirements.txt
```

Write secrets

```bash
echo "MAPS_API_KEY=$MAPS_API_KEY" > .env
```

### Run

```bash
python main.py --direction work
```