from Miner import *


def change_mine(miner: Miner, status=Status.closed, start=0, end=100, batch=100):
    fields = [Field.all_revisions, Field.all_files, Field.messages, Field.detailed_labels]

    miner.fields = fields
    miner.status = status
    miner.batch_size = batch
    step = 2000
    for index in range(start, end, step):
        miner.start_index = index
        miner.end_index = miner.start_index + step
        miner.after = "2009-01-01 00:00:00.000000000"
        miner.before = "2009-12-31 23:59:59.000000000"

        result = miner.change_mine(n_jobs=5, timeout=120)
        for url, did_succeed in result:
            if did_succeed is False:
                print(f"{url} failed in the previous run. Mining again")
                index -= step
                break
        if not miner.has_more_changes:
            print("Stopping mining")
            break


if __name__ == "__main__":
    miner = Miner(gerrit=Gerrit.eclipse, replace=False)

    # miner.set_data_root('change')
    # fields = [Field.all_revisions, Field.all_files, Field.messages, Field.detailed_labels]
    # change_mine(miner, fields, Status.closed, start=0, end=2000)

    # miner.set_data_root('profile')
    # miner.profile_mine(973)

    # miner.set_data_root('comment')
    # miner.comment_mine(1235)

