#########
clireader
#########

A simple program for paging through text files from the command line.


What does it do?
================
It allows you to page through text files in a terminal.


Why Did I Make This?
====================
Great question. Mainly it's to allow me to add help screens to a
blackjack program I'm writing. A certain amount of curiosity about
how Unix `man` pages get written was also involved. There were
probably better ways to address both of those, but this is what I
chose to do.


To Run
======
To open a document with clireader, download the repository and use `pip`
to install the package. The run the following::

    clireader path/to/file

Where `path/to/file` is the file path to the document you want to open.

The commands at the bottom of the terminal window allow you to navigate
the document and otherwise interact with `clireader`:

*   `Back` Go back one page.
*   `Flow` Reflow the document (see Wrapping Modes below).
*   `Jump` Go to a specific page.
*   `Next` Go forward one page.
*   `eXit` Quit out of `clireader`

Invoke the command by typing the letter capitalized in the command.


Wrapping Modes
--------------
Documents can be opened in a few different "wrapping modes." This mainly
affects how lines longer than the terminal are handled, but they can have
other formatting effects. While the default is to try and rewrap the
entire document for the width of the current terminal, other options can
be set when invoking `clireader` from the command line:

*   `-l` Only rewrap the long lines.
*   `-m` Use "manlike" formatting.
*   `-n` Truncate long lines rather than rewrapping them.

The wrapping mode can also be changed while `clireader` is running using
the "Flow" command.


Manlike Formatting
------------------
"Manlike formatting" interprets commands similar to the `troff` macros
used to format Unix `man` pages to allow additional formatting when
reflowing a document. Use the `clireader -M` to learn more.


To-Do
=====
The following are nice to have features for future releases:

*   Manage the flowing of text with curses better.
*   Allow removal of the side frames and padding.
*   Implement the load command.


Testing
=======
To run the unit tests, pull the repository and run the following from
the root of the repository::

    python3 -m unittest discover tests

To run a more comprehensive suite of tests, run the following from the
root of the repository::

    precommit.py


How do I contribute?
====================
At this time, this is code is really just me exploring and learning.
I've made it available in case it helps anyone else, but I'm not really
intending to turn this into anything other than a personal project.

That said, if other people do find it useful and start using it, I'll
reconsider. If you do use it and see something you want changed or
added, go ahead and open an issue. If anyone ever does that, I'll
figure out how to handle it.
