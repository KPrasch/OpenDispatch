from hendrix.deploy.base import HendrixDeploy
import sys, os



os.environ['DJANGO_SETTINGS_MODULE'] = 'main.settings'
sys.path.insert(0, '/home/k/git/Dispatch.py/main/')

import pdb; pdb.set_trace()

#Run Hendrix
options = {'settings':'main.settings'}
deployer = HendrixDeploy(options=options)
deployer.run()