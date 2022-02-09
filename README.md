# Gerrit-Miner

 Mines gerrit changes with detailed info. This miner follows the rest api documentation in
 [rest-api](https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html) to mine changes.

## Features

Can be used to mine:

* Code changes with revisions, messages, labels and many other fields in details
* Apply queries to filter our changes by a range of date and status
(open, closed etc)
* Developer profiles (registration date and other personal details)
* Respective work of each developer
* Comments or discussions

## Speciality

* This miner creates concurrent threads to make several web requests at a time. This makes mining several
 times faster than normal.The user is free to use concurrent process also,
 by commenting out the related code.
* The complete list of optional fields provided by gerrit is available here.

## Requirements

* enum
* concurrent.futures
* json
* os
* requests
* time

## Install

 ```diff
 git clone https://github.com/khairulislam/Gerrit-Miner
 cd Gerrit-Miner
 pip install -r requirements.txt
```

## Getting started

 Run the main.py file to start mining.

 ```bash
python main.py
```

 Modify miner arguments accordingly. To add more gerrit sites please modify Gerrit.py file.

## Citation

The miner was created as part of the paper titled [Early Prediction for Merged vs Abandoned CodeChanges in Modern Code Reviews](https://github.com/khairulislam/Predict-Code-Changes). Paper link : [IST](https://www.sciencedirect.com/science/article/abs/pii/S0950584921002032), [arxiv](https://arxiv.org/pdf/1912.03437.pdf).

```bash
@article{ISLAM2022106756,
title = {Early prediction for merged vs abandoned code changes in modern code reviews},
journal = {Information and Software Technology},
volume = {142},
pages = {106756},
year = {2022},
issn = {0950-5849},
doi = {https://doi.org/10.1016/j.infsof.2021.106756},
url = {https://www.sciencedirect.com/science/article/pii/S0950584921002032},
author = {Khairul Islam and Toufique Ahmed and Rifat Shahriyar and Anindya Iqbal and Gias Uddin}
}
```

## Feedback

Please open an issue to request a feature or submit a bug report. Or even if
you just want to provide some feedback, I'd love to hear. I'm available at khairulislamtanim@gmail.com.

## Contributing

1. Fork it.
2. Create your feature branch (`git checkout -b my-new-feature`).
3. Commit your changes (`git commit -am 'Added some feature'`).
4. Push to the branch (`git push origin my-new-feature`).
5. Create a new Pull Request.
