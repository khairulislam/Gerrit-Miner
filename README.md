# Gerrit-Miner
 Mines gerrit changes with detailed info. This miner follows the rest api documentation in
 [rest-api](https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html) to mine changes.

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
 $ git clone https://github.com/khairulislam/Gerrit-Miner
 $ cd Gerrit-Miner
 $ pip install -r requirements.txt
```
 ## Getting started
 Run the main.py file to start mining. 
 ```
$ python main.py
```
 Modify miner arguments accordingly. To add more gerrit sites please modify Gerrit.py file.
 
## Feedback
Please open an issue to request a feature or submit a bug report. Or even if
you just want to provide some feedback, I'd love to hear. I'm available at khairulislamtanim@gmail.com.

## Contributing
1.  Fork it.
2.  Create your feature branch (`git checkout -b my-new-feature`).
3.  Commit your changes (`git commit -am 'Added some feature'`).
4.  Push to the branch (`git push origin my-new-feature`).
5.  Create a new Pull Request.