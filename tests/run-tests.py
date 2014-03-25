from subprocess import call

errs = 0
errs += call(['python', 'tests/talk-talk-test.py'])
print "Errors: ", errs
errs += call(['python', 'tests/test-hunky.py'])
print "Errors: ", errs
exit(errs)
