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

# Installation

If you want to hack on Rua, getting it set up is easy. You'll need a unix machine (you can set it up on Windows if you're super hard core). We recommend you use [VirtualEnvironment](https://virtualenv.pypa.io/en/latest/). 

Rua uses a MySQL database called 'rua' accessed by a 'root' user by default. Create it with:

	$ mysql -u root -p -e "CREATE DATABASE rua;"

Once created, clone the repo with:

	$ git clone https://github.com/ubiquitypress/rua.git

And install with:

    $ ./install.sh

This will install a small number of requirements including Django.

# Development

To start hacking run (from the src folder):

	$ python manage.py runserver

You'll now be able to access the server from http://localhost:8000

# Testing

Run the unit tests with:

    $ ./test.sh

# Credit
Originally started by a team of volunteer developers, this project is now supported by [Ubiquity Press](http://ubiquitypress.com/).

Core developers:

- Andy Byers
- Mauro Sanchez
- Ioannis Cleary
- Paige MacKay

# Milestones
We're currently working on the Alpha, which is the backend release, this will be followed by the initial front end release then others.
