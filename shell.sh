#!/bin/bash

source virtualenvwrapper.sh
workon /venv/
source /home/goTandem/.virtualenvs/venv/bin/postactivate
workon /venv/
cd /home/goTandem/mysite
python manage.py send_staff_reminders