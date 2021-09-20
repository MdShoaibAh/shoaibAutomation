import requests


class APIRequest:
    def get(self, url):
        response = requests.get(url)
        return response

    def post(self, url, payload, headers):
        response = requests.post(url, json=payload, headers=headers)
        return response

