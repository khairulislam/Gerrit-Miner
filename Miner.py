from Field import *
from Status import *
from Gerrit import *
import requests
import json, os
import time
from concurrent.futures import as_completed, ProcessPoolExecutor, ThreadPoolExecutor


class Miner:
    status: Status = Status.open
    fields: [Field] = []

    # some site like eclipse sets  highest batch download limit to 100
    # other sites may allow upto 500
    batch_size: int = 100

    has_more_changes: bool = True

    def __init__(self, gerrit: Gerrit, root: str = None, replace: bool = False):
        if type(gerrit) != Gerrit:
            print("Error: please pass a Gerrit type arg. Exiting ..")
            exit(-1)
        self.gerrit = gerrit
        self.replace = replace

        if root is None:
            self.root = f"{gerrit}"
        else:
            self.root = root
        if not os.path.isdir(self.root):
            os.mkdir(self.root)

    def create_change_url(self, start_index, after, before, end_index):
        url = f"{self.gerrit.value}/changes"
        # add query
        # Clients are allowed to specify more than one query by setting the q parameter multiple times.
        # In that case the result is an array of arrays, one per query in the same order the queries were given in.
        # however here we have written code for one query only
        url += "/?q="
        if self.status != '':
            url += f"status:{self.status}"

        if after != '':
            url += f"+after:\"{after}\""
        if before != '':
            url += f"+before:\"{before}\""

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

        if end_index != -1:
            url += f"&n={min(self.batch_size, end_index - start_index)}"
        else:
            url += f"&n={self.batch_size}"

        # an exceptional case
        url = url.replace("NO_LIMIT", "NO-LIMIT").replace('=+', '=')

        return url

    def create_change_filename(self, current_index):
        return f"{self.gerrit}_{self.status}_{current_index}_{current_index + self.batch_size}.json"

    @staticmethod
    def parse(data: str):
        json_data = None
        try:
            json_data = json.loads(data)
        except ValueError:
            print(f"Failed to load json. Invalid data {data}")
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
        elif len(data) == 0:
            print(f" {url} returned empty")
            self.has_more_changes = False
            return False
        else:
            print("Dumping response of {0}".format(url))
            self.dump(path=filename, data=data)
            return True

    def change_mine(self,
                    sub_directory: str = "change",
                    start_index: int = 0,
                    end_index: int = -1,
                    after: str = '2019-01-01 00:00:00.000000000',
                    before: str = '2020-01-01 00:00:00.000000000',
                    n_jobs: int = None,
                    timeout: int = 60
                    ):
        current_dir = os.path.join(self.root, sub_directory)
        if not os.path.isdir(current_dir):
            os.mkdir(current_dir)

        future_to_url = {}
        current_index = start_index
        while self.has_more_changes and (end_index == -1 or current_index < end_index):
            with ThreadPoolExecutor(max_workers=n_jobs) as executor:
                jobs = n_jobs
                while self.has_more_changes and (end_index == -1 or current_index < end_index) and jobs >= 0:
                    url = self.create_change_url(current_index, after, before, end_index)
                    filename = self.create_change_filename(current_index)

                    path = os.path.join(current_dir, filename)
                    if not self.replace and os.path.exists(path):
                        print(f"{filename} already exists")
                        current_index += self.batch_size
                        continue

                    future = executor.submit(self.download, url, timeout, path)
                    future_to_url[future] = url
                    current_index += self.batch_size
                    jobs -= 1

                print("Shutting down executor without waiting")
                executor.shutdown(wait=False)
                print("Canceling running futures")
                for future in future_to_url:
                    future.cancel()

        results = []
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                did_succeed = future.result()
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")
            else:
                results.append((url, did_succeed))
        return results

    def profile_mine(self, account_id, sub_directory: str = "profile", timeout: int = 60):
        current_dir = os.path.join(self.root, sub_directory)
        if not os.path.isdir(current_dir):
            os.mkdir(current_dir)

        join_file_path = os.path.join(current_dir, f"profile_{account_id}.json")
        details_file_path = os.path.join(current_dir, f"profile_details_{account_id}.json")

        # download join date 
        if self.replace or not os.path.exists(join_file_path):
            url = f"{self.gerrit.value}/accounts/{account_id}/detail"
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.download, url, timeout, join_file_path)

        # download all changes associated with this account
        if self.replace or not os.path.exists(details_file_path):
            url = f"{self.gerrit.value}/changes/?q=is:closed+owner:{account_id}"

            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.download, url, timeout, details_file_path)

    def comment_mine(self, change_number, sub_directory: str = "comment", timeout: int = 60):
        current_directory = os.path.join(self.root, sub_directory)
        if not os.path.exists(current_directory):
            os.mkdir(current_directory)

        file_path = os.path.join(current_directory, f"comment_{change_number}.json")

        if self.replace or not os.path.exists(file_path):
            url = f"{self.gerrit.value}/changes/{change_number}/comments"
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.download, url, timeout, file_path)
