# Sending a repo to backend to be processed:
```python
import requests
repo_url            = "https://github.com/Adarsh9616/Electricity_Billing_System/"
url_to_process_repo = f"https://bjxdbdicckttmzhrhnpl342k2q0pcthx.lambda-url.us-east-1.on.aws/?repo_url={repo_url}"
response            = requests.get(url_to_process_repo)
```

