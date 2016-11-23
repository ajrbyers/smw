# RUA
Rua - the Simple Monograph Workflow

# Context
Rua is an Open Source application designed to assist with the Monograph publishing life cycle. Stages include:

- optional proposal
- submission
- internal review
- peer review
- copy editing
- production
- publication

Rua is completely free to use under the GNU GENERAL PUBLIC LICENSE v2 (see LICENSE). [Ubiquity Press](http://ubiquitypress.com/site/contact/) also offers a paid for hosted service for Rua.

# Technology
RUA is written in Python using the Django Web Application framework and follows a MTV (that is, “model”, “template”, and “view.”) style. The template system is simple, easy to modify and uses Twitter Bootstrap 3.

# Development

If you want to hack on Rua, getting it set up is easy. You'll need a unix machine (you can set it up on Windows if you're super hard core). We recommend you use [VirtualEnvironment](https://virtualenv.pypa.io/en/latest/) with [VirtualEnvWrapper](https://virtualenvwrapper.readthedocs.org/en/latest/). Once these are installed, clone the repo with:

	$ git clone https://github.com/ubiquitypress/rua.git

Ensure VirtualEnvWrapper is installed:

	$ pip install virtualenvwrapper

Make a virtual environment:

	$ mkvirtualenv rua

And install the requirements (requirements.txt is found in the root folder of the repo):

	$ pip install -r requirements.txt

This will install a small number of requirements including Django.

Symlink the settings module you require. In development, this will be:

	$ ln -s dev_settings.py src/core/settings.py

These settings assume a `root` user with the password `root` and a database called `rua`. To create this database:

	$ mysql -u root -p -e "CREATE DATABASE rua;"

Sync and migrate the SQLite DB (from the src folder):

	$ python src/manage.py syncdb
	$ python src/manage.py migrate

We have a few required database settings so you need to import some data:

	$ python manage.py loaddata core/fixtures/settinggroup.json
	$ python manage.py loaddata core/fixtures/settings.json
	$ python manage.py loaddata core/fixtures/cc-licenses.json
	$ python manage.py loaddata core/fixtures/role.json

In the future this will all be hanlded by an install command.

To start hacking run (from the src folder):

	$ python manage.py runserver

You'll now be able to access the server from http://localhost:8000

# Credit
Originally started by a team of volunteer developers, this project is now supported by [Ubiquity Press](http://ubiquitypress.com/).

Core developers:

- Andy Byers
- Mauro Sanchez
- Ioannis Cleary
- Paige MacKay

# Milestones
We're currently working on the Alpha, which is the backend release, this will be followed by the initial front end release then others.
