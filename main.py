from Miner import *

if __name__ == "__main__":
    fields = [Field.all_revisions, Field.all_files, Field.messages, Field.detailed_labels]
    miner = Miner(gerrit=Gerrit.android, fields=fields, status=Status.closed, start_index=0, end_index=10,
                  batch_size=5, replace=True)

    result = miner.mine(n_jobs=2)
    print(result)
