# Client for memoQ server Web Service API

This is a group of packages for Python to interact with [memoQ server Web Service API](https://www.memoq.com/en/the-memoq-apis/memoq-server-web-service-api). It's using Suds SOAP client, I recommend downloading [Satiani's version](https://github.com/satiani/suds) as it fixes problem with recursion.

It's quite heavily customized to my own needs in terms of settings (project creation, statistics), so you may want to check some of the methods before running them. **All exceptions returned by the server are ignored.**

You may use them all as single package or as standalone ones. Start with adjusting *config.json*, especially "api_base_url". If you want your projects to be created as user other than built-in Administrator change "creator_guid" as well.

Every method in each package is unit tested. However, I'm aware that not all possible cases are covered. Before running tests on your side you'll need to change few things in *testFiles/testConfig.json* to align it with your environment. Especially items starting with *valid*.

**I've created this for my experiments and never used it on production environment. You're free to use it however you wish, but I take no responsibility for any possible damage caused by it.**
