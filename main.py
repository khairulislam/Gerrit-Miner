from Miner import *
import pandas as pd


def load_profiles(miner: Miner, sub_directory: str = "profile"):
    current_directory = os.path.join(miner.root, sub_directory)
    if not os.path.exists(current_directory):
        os.mkdir(current_directory)

    # create the profiles list before calling this batch profile loading
    df = pd.read_csv(os.path.join(current_directory, "profiles.csv"))
    ids = df['account_id'].values
    for account_id in ids:
        miner.profile_mine(account_id=account_id, timeout=120)


if __name__ == "__main__":
    miner = Miner(gerrit=Gerrit.libreoffice, replace=False)

    fields = [Field.all_revisions, Field.all_files, Field.messages, Field.detailed_labels]
    miner.fields = fields
    miner.status = Status.closed
    miner.end_index = -1
    miner.batch_size = 500  # or 100

    index = 0
    max_retry = 3
    while miner.has_more_changes and max_retry > 0:
        miner.start_index = index
        result = miner.change_mine(n_jobs=4, timeout=600, after='2012-01-01 00:00:00.000000000',
                                   before='2013-01-01 00:00:00.000000000')
        for url, did_succeed in result:
            if did_succeed is False:
                print(f"{url} failed .")
                max_retry -= 1
                break

        if max_retry <= 0:
            print("Max retry count has ended")

    # load_profiles(miner)
    # miner.profile_mine(973)
    # miner.comment_mine(1235)

