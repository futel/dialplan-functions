how to run the testplan
- setup what is necessary for the tests to be run, see setup document
- run tests listed in testplan document
- tests are found in tests document
- run tests on stage
- update the record of tests
  - for passed tests, mark date and name
  - for failed tests, mark fail, name, comment, optionally open issue and add link

where to find the testplan
- source is the testplan directory of the dialplan-functions repository https://github.com/futel/dialplan-functions/tree/main/testplan
- record of tests is the google sheet https://docs.google.com/spreadsheets/d/1WYEMQqlvuJeSEwOWJAA_KTBnpaOOddj_leQfczQgE0w/edit#gid=670551017

notes
- do not dial 911! Emergency service is connected on stage! Dial 933 for all dialtone 911 tests.
- prioritize tests which haven't been run in a while or which are important
- bad documentation is a bug, file an issue if you don't understand something
- some tests are confusing or can't be run, don't stress, ask, leave notes, or file an issue if this isn't documented
