import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from collections import deque

class APIClient:
    def __init__(self, base_url, delay=1, max_failures=5):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.request_count = {"v1": 0, "v2": 0, "v3": 0}
        self.result_count = {"v1": 0, "v2": 0, "v3": 0}
        self.failure_count = 0
        self.max_failures = max_failures  # Stop script if too many failures
        retry_strategy = Retry(
            total=3,  # Reduce retries to prevent long wait times
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.last_request_time = 0

    def make_request(self, version, path, params):
        self.request_count[version] += 1
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

        print(f"Making request: {version} | Query: {params['query']} | Page: {params['page']}")
        
        try:
            response = self.session.get(f"{self.base_url}{path}", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.result_count[version] += len(data.get("results", []))
            self.failure_count = 0  # Reset failure count on success
            return data
        except requests.exceptions.RequestException as e:
            self.failure_count += 1
            print(f"Request failed: {e}")
            if self.failure_count >= self.max_failures:
                print(f"Too many failures ({self.max_failures}), stopping script.")
                exit(1)  # Stop execution if server keeps failing
            return None

def fetch_results(client, version, path):
    print(f"Fetching results for {version}...")
    processed_prefixes = set()
    queue = deque()
    names = set()

    for c in 'abcdefghijklmnopqrstuvwxyz':
        queue.append(c)
        processed_prefixes.add(c)

    while queue:
        prefix = queue.popleft()
        print(f"Processing prefix: {prefix}")
        page = 1
        while True:
            params = {'query': prefix, 'page': page}
            data = client.make_request(version, path, params)
            if not data:
                print(f"No data returned for prefix {prefix}, moving to next.")
                break
            results = data.get('results', [])
            if not results:
                break
            for name in results:
                normalized_name = name.strip().lower()
                if normalized_name not in names:
                    names.add(normalized_name)
                    if len(normalized_name) > len(prefix):
                        next_char = normalized_name[len(prefix)]
                        next_prefix = prefix + next_char
                        if next_prefix not in processed_prefixes:
                            processed_prefixes.add(next_prefix)
                            queue.append(next_prefix)
            if not data.get('has_next_page', False):
                break
            page += 1

    return names

def check_server(base_url):
    """ Check if server is reachable before running full script. """
    try:
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()
        print("Server is reachable. Proceeding with data collection.")
        return True
    except requests.exceptions.RequestException:
        print("Server is down or not responding. Exiting.")
        return False

def main():
    base_url = "http://35.200.185.69:8000"
    
    if not check_server(base_url):
        return  # Stop execution if server is down

    client = APIClient(base_url, delay=1)
    
    versions = {"v1": "/v1/autocomplete", "v2": "/v2/autocomplete", "v3": "/v3/autocomplete"}
    for version, path in versions.items():
        print(f"Starting data collection for {version}...")
        names = fetch_results(client, version, path)
        with open(f'names_{version}.txt', 'w') as f:
            for name in sorted(names):
                f.write(f"{name}\n")
        print(f"Completed data collection for {version}.")

    print(f"No. of searches made for v1: {client.request_count['v1']}")
    print(f"No. of searches made for v2: {client.request_count['v2']}")
    print(f"No. of searches made for v3: {client.request_count['v3']}")
    print(f"No. of results in v1: {client.result_count['v1']}")
    print(f"No. of results in v2: {client.result_count['v2']}")
    print(f"No. of results in v3: {client.result_count['v3']}")

if __name__ == "__main__":
    print("Starting script...")
    main()
