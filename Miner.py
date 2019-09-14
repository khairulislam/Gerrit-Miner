from Field import *
from Status import *
from Gerrit import *
import requests
import json, os
import time
from concurrent.futures import as_completed, ProcessPoolExecutor, ThreadPoolExecutor


class Miner:
    def __init__(self, gerrit: Gerrit, fields: [Field], status: Status, start_index: int, end_index: int,
                 batch_size: int = 100, replace: bool = False):
        if type(gerrit) != Gerrit:
            print("Error: please pass a Gerrit type arg. Exiting ..")
            exit(-1)
        self.gerrit = gerrit
        self.fields = fields
        self.status = status
        self.start_index = start_index
        self.end_index = end_index
        self.batch_size = batch_size
        self.replace = replace

        self.root = f"{gerrit}"
        if not os.path.isdir(self.root):
            os.mkdir(self.root)

    def create_url(self, current_index):
        url = f"{self.gerrit.value}/changes/?"
        # add query
        url += f"q=status:{self.status}&"

        # The S or start query parameter can be supplied to skip a number of changes from the list
        if current_index < 0:
            print("Error: start index can't be negative. Resetting to 0.")
            start_index = 0
        url += f"S={current_index}&"

        # used to limit the returned results.
        if self.batch_size <= 0:
            print("Error: change count can't be 0. Resetting to 100.")
            count = 100
        url += f"n={self.batch_size}&"

        # optional fields
        for field in self.fields:
            if type(field) is Field:
                url += f"o={field}&"
            else:
                print(f"Error: unknown field {field}")
        # an exceptional case
        url = url.replace("NO_LIMIT", "NO-LIMIT")

        if url[-1] == '&':
            url = url[:-1]
        return url

    def create_filename(self, current_index):
        return f"{self.gerrit}_{self.status}_{current_index}_{current_index + self.batch_size}.json"

    def download(self, url: str, timeout: int, filename: str):
        data = requests.get(url, timeout=timeout).text[4:]
        if len(data) == 0:
            print(f"Error: {url} response is empty")
            return False

        data = Miner.parse(data)
        if data is None:
            print(f"Error: {url} response could not be parsed")
            return False
        else:
            path = f"{self.root}/{filename}"
            self.dump(path=path, data=data)
            return True

    def mine(self, n_jobs: int = 1, timeout: int = 30):
        urls = []
        for index in range(self.start_index, self.end_index, self.batch_size):
            url = self.create_url(index)
            urls.append(url)

        # with ProcessPoolExecutor(max_workers=n_jobs) as executor:
        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            start = time.time()

            future_to_url = {}
            for index in range(self.start_index, self.end_index, self.batch_size):
                url = self.create_url(index)
                filename = self.create_filename(index)
                if not self.replace and os.path.exists(f"{self.root}/{filename}"):
                    continue

                future = executor.submit(self.download, url, timeout, filename)
                future_to_url[future] = url

            results = []
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    did_succeed = future.result()
                except Exception as exc:
                    print(f"{url} generated an exception: {exc}")
                else:
                    results.append((url, did_succeed))
            end = time.time()
            print("Time Taken: {:.6f}s".format(end - start))
            return results

    @staticmethod
    def parse(data: str):
        json_data = None
        try:
            json_data = json.loads(data)
        except ValueError:
            print(ValueError)
        return json_data

    def dump(self, path: str, data: json):
        if data is None:
            print("Error: data is None")
            return False
        if not os.path.exists(path) or self.replace:
            try:
                f = open(path, "w")
                json.dump(data, f, indent=4)
                f.close()
            except OSError as e:
                print(f"Data could not be dumped to {path}.")
                print(e)
                return False
        return True
