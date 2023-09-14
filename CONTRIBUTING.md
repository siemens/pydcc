# Contributing

We welcome contributions in several forms, e.g.

- Sponsoring
- Documenting
- Testing
- Coding
- etc.

Please read [14 Ways to Contribute to Open Source without Being a Programming Genius or a Rock Star](https://smartbear.com/blog/test-and-monitor/14-ways-to-contribute-to-open-source-without-being/ ).

Please check [Issues](https://gitlab.com/gemimeg/pydcc/-/issues) and look for unassigned ones or create a new one.

## General Workflow

We use the [Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow) and review all changes we merge to master.

We appreciate any contributions, so please use the [Forking Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow).

For fast feedback, before submitting your contribution execute the unit test and ensure it was passed successfully. However, the test will be executed in the GitLab pipeline after committing to any branch, including the master.
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

In the case of new API features, it is mandatory to
* Add a new entry to the doc/mydcc.md in the section API
* Add a unit test to tests/unit_test.py
* Implement a new API function.
* Make sure to pass all the tests, including the new API test.


