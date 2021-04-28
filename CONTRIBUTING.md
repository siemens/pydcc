# Contributing

In general, please feel free to contact the maintainers of the software via E-Mail. 
## Contributing Code  

Please read [14 Ways to Contribute to Open Source without Being a Programming Genius or a Rock Star](https://smartbear.com/blog/test-and-monitor/14-ways-to-contribute-to-open-source-without-being/ ).

Please check [Issues](https://gitlab.com/gemimeg/pydcc/-/issues) and look for unassigned ones or create a new one.

## General Workflow

We use the [Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) and review all changes we merge to master.

We appreciate any contributions, so please use the [Forking Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow).

For fast feedback, before submiting your contribution execute the unit test and make sure it was passed successfully. However, the test will be executed in the GitLab pipeline after commiting to any branch including master.
```bash
cd tests
pytest --cov=dcc unit_test.py
```

After passing the test send a [merge request](https://gitlab.com/gemimeg/pydcc/-/merge_requests) via Gitlab.

## Dependencies for developers

Additional dependencies for developers 
```bash
pytest
pytest-cov
setuptools
```

## Additional Workflow when changing the API

In case of new API features it is mendatory to
* Add a new entry to the doc/mydcc.md in the section API
* Add an unit test to tests/unit_test.py
* Implement a new API function.
* Make sure passing the all test including the new API test.


