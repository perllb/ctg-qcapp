#!/usr/bin/env python3.8

import sys
import site

site.addsitedir('/home/srv/flask/qcapp/project/auth/lib/python3.8/site-packages')

sys.path.insert(0, '/home/srv/flask/qcapp')

from qcapp import app as application
