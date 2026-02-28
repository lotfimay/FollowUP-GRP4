
if __name__ == '__main__':
    import requests, yaml, json
    r = requests.get('http://localhost:8000/openapi.json')
    with open('openapi.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(r.json(), f, allow_unicode=True, sort_keys=False)