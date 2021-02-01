# Contributing
## Contributing Code  

Please read [14 Ways to Contribute to Open Source without Being a Programming Genius or a Rock Star](https://smartbear.com/blog/test-and-monitor/14-ways-to-contribute-to-open-source-without-being/ ).

Please check [Issues](https://code.siemens.com/siemens/code/-/issues) and look for unassigned ones or create a new one.

## General Workflow

We use the [Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) and review all changes we merge to master.

We appreciate any contributions, so please use the [Forking Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow) and send us [Merge Requests](https://code.siemens.com/help/user/project/merge_requests/index.md)!

Before submiting your contribution execute the unit test. 
```bash
cd tests
python unit_test.py
```
## Additional Workflow when Changing the API

In case of new API features it is mendatory to
* Add a new entry to the README.md in the section API
* Add a unit test to tests/unit_test.py
* Implement your new API function.
* Make sure passing your test.


