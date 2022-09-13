#########
clireader
#########

A simple program for paging through text files from the command line.


To-Do
=====
The following items are still to-do before the initial release of the
package:

*   x Remove next command when at the last page of the document.
*   x Implement the jump command.
    *   x Create ability to input multiple characters.
    *   x Create ability to prompt for input.
    *   x Create ability to show the prompt for input.
    *   x Create ability to echo input to screen.
    *   x Have the jump command prompt for input.
    *   x Have the jump command jump to the page.
*   x Allow invocation with arguments.
*   x Allow calling of main components from __init__.
*   x Require files exist before opening them.

The following are nice to have features for future releases:

*   Manage the flowing of text with curses better.
*   Don't rewrap lines that are shorter than the terminal width.
*   Implement the load command.
