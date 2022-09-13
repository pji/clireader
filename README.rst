#########
clireader
#########

A simple program for paging through text files from the command line.


To Run
======
To open a document with clireader, use `pip` to install the package
and run the following::

    clireader path/to/file

Where `path/to/file` is the file path to the document you want to open.


To-Do
=====
The main features for the initial release have been completed.

The following are nice to have features for future releases:

*   Manage the flowing of text with curses better.
*   Don't rewrap lines that are shorter than the terminal width.
*   Implement the load command.


Testing
=======
To run the unit tests, pull the repository and run the following from
the root of the repository::

    python3 -m unittest discover tests

To run a more comprehensive suite of tests, run the following from the
root of the repository::

    precommit.py


How do contribute?
==================
At this time, this is code is really just me exploring and learning.
I've made it available in case it helps anyone else, but I'm not really
intending to turn this into anything other than a personal project.

That said, if other people do find it useful and start using it, I'll
reconsider. If you do use it and see something you want changed or
added, go ahead and open an issue. If anyone ever does that, I'll
figure out how to handle it.
