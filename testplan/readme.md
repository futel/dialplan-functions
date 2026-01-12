## how to run the testplan

- setup what is necessary for the tests to be run, see [setup](setup.md) document
- run tests listed on the google sheet
- tests are found in [tests.md](tests.md)
- so for every extension and context listed in the sheet, run the tests listed in [tests.md](tests.md)
- run tests on stage
- update the record of tests on the google sheet
  - for passed tests, mark date
  - for failed tests, mark fail, comment, optionally [open issue](https://github.com/futel/dialplan-functions/issues)
    and add link

## where to find the testplan

- source is the testplan directory of the dialplan-functions repository (where this readme lives)
  - https://github.com/futel/dialplan-functions/tree/main/testplan
- record of tests is the google sheet
  - https://docs.google.com/spreadsheets/d/1WYEMQqlvuJeSEwOWJAA_KTBnpaOOddj_leQfczQgE0w/edit#gid=670551017

what should be tested, this should be what is filled out in the testplan sheet
- for every extension listed, run extension tests in tests.md
- for every incoming extension listed, run the incoming call tests
- general context tests, run once
- for every context listed, run the context tests
- for every context listed, run the specific context tests

## notes

- do not dial 911! Emergency service is connected on stage! Dial 933 for all dialtone 911 tests.
- prioritize tests which haven't been run in a while or which are important
- bad documentation is a bug, file an issue if you don't understand something
- some tests are confusing or can't be run, don't stress, ask, leave notes, or file an issue if this isn't documented
