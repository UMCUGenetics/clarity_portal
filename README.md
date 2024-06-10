# Clarity Portal

## Install
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Development server
```bash
flask --app portal run --debug
```

## Production server
```bash
gunicorn -w 4 portal:app
```
