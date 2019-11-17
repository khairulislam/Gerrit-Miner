from Miner import *

if __name__ == "__main__":
    fields = [Field.all_revisions, Field.all_files, Field.messages, Field.detailed_labels]
    miner = Miner(gerrit=Gerrit.eclipse, fields=fields, status=Status.closed, replace=False)

    miner.batch_size = 100
    step = 2000
    for index in range(0, 4000, step):
        miner.start_index = index
        miner.end_index = miner.start_index + step
        miner.after = "2009-01-01 00:00:00.000000000"
        miner.before = "2009-12-31 23:59:59.000000000"

        result = miner.mine(n_jobs=5, timeout=120)
        for url, did_succeed in result:
            if did_succeed is False:
                print(f"{url} failed in the previous run. Mining again")
                index -= step
                break
        if not miner.has_more_changes:
            print("Stopping mining")
            break
        # print(result)
