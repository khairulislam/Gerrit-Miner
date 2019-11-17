from Field import *
from Status import *
from Gerrit import *
import requests
import json, os
import time
from concurrent.futures import as_completed, ProcessPoolExecutor, ThreadPoolExecutor


class Miner:
    start_index = 0
    # some sites like android have upper limit to end index too
    end_index = -1
    # some site like eclipse sets  highest batch download limit to 100
    # other sites may allow upto 500
    batch_size = 100

    # must be like this format: 2016-01-01 00:00:00.000000000
    after = ''
    before = ''

    has_more_changes = True

    def __init__(self, gerrit: Gerrit, fields: [Field], status: Status, replace: bool = False):
        if type(gerrit) != Gerrit:
            print("Error: please pass a Gerrit type arg. Exiting ..")
            exit(-1)
        self.gerrit = gerrit
        self.fields = fields
        self.status = status
        self.replace = replace

        self.root = f"{gerrit}"
        if not os.path.isdir(self.root):
            os.mkdir(self.root)

    def create_url(self, start_index):
        url = f"{self.gerrit.value}/changes/?"
        # add query
        url += f"q=status:{self.status}"

        if self.after != '':
            url += f"+after:\"{self.after}\""
        if self.before != '':
            url += f"+before:\"{self.before}\""

        # optional fields
        for field in self.fields:
            if type(field) is Field:
                url += f"&o={field}"
            else:
                print(f"Error: unknown field {field}")

        # The S or start query parameter can be supplied to skip a number of changes from the list
        if start_index < 0:
            print("Error: start index can't be negative. Resetting to 0.")
            start_index = 0
        url += f"&S={start_index}"

        # used to limit the returned results.
        if self.batch_size <= 0:
            print("Error: change count can't be 0. Resetting to 100.")
            self.batch_size = 100

        if self.end_index != -1:
            url += f"&n={min(self.batch_size, self.end_index-start_index)}"
        else:
            url += f"&n={self.batch_size}"

        # an exceptional case
        url = url.replace("NO_LIMIT", "NO-LIMIT")

        return url

    def create_filename(self, current_index):
        return f"{self.gerrit}_{self.status}_{current_index}_{current_index + self.batch_size}.json"

    def download(self, url: str, timeout: int, filename: str):
        data = requests.get(url, timeout=timeout).text[4:]
        if len(data) == 0:
            print(f"Error: {url} response is empty")
            self.has_more_changes = False
            return False

        if "\"_more_changes\": true" not in data:
            print("No more changes left")
            self.has_more_changes = False

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
            current_index = self.start_index
            while self.has_more_changes and (self.end_index == -1 or current_index < self.end_index):
                url = self.create_url(current_index)
                filename = self.create_filename(current_index)

                if not self.replace and os.path.exists(f"{self.root}/{filename}"):
                    print(f"{filename} already exists")
                    current_index += self.batch_size
                    continue

                future = executor.submit(self.download, url, timeout, filename)
                future_to_url[future] = url

                current_index += self.batch_size

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
