import requests

url = "http://localhost:8080/api/2/things/org.vehicle:car1"
response = requests.get(url, auth=("ditto", "ditto"), timeout=5)
print(response.json())
