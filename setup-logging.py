import os
from private.dispatch_settings import GLOBAL_LOGGING_DIRECTORY

if not os.path.exists(GLOBAL_LOGGING_DIRECTORY):
    os.makedirs(GLOBAL_LOGGING_DIRECTORY)
else:
    print 'Logging directory already exists, you\'re ready to go!'
