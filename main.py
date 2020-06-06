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
    # 1. Download change details
    miner = Miner(gerrit=Gerrit.libreoffice, replace=False)

    parameters = Parameters(status=Status.closed, start_index=0, end_index=-1,
                            after='2012-01-01 00:00:00.000000000',
                            before='2013-01-01 00:00:00.000000000',
                            fields=[Field.all_revisions, Field.all_files, Field.messages, Field.detailed_labels],
                            n_jobs=4, batch_size=100)

    index = 0
    max_retry = 3
    while miner.has_more_changes and max_retry > 0:
        miner.start_index = index
        result = miner.change_details_mine(parameters=parameters)
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

