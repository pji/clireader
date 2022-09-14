######################
clireader Requirements
######################

The purpose of this document is to detail the requirements for the
`clireader` package. This is an initial take to help with planning.
There may be additional requirements of non-required features added in
the future that are not recorded here.


Purpose
=======
The purposes of `clireader` are:

*   Read a multipage text in a terminal session.
*   Experiment with CLI app design with the `blessed` package.


Functional Requirements
=======================
The following are the functional requirements for `clireader`:

*   Load text from a file.
*   Display text in the terminal.
*   Wrap the text to the dimensions of the terminal.
*   Page through text that overflows the terminal dimensions.
*   Exit cleanly.
*   Display text with rich formatting, such as:
    *   Colored text,
    *   Bold,
    *   Underline,
    *   Italics.
*   Provide UI hints for available commands.
*   Be called as a standalone application.
*   Be imported into other Python code.


Technical Requirements
======================
The following are the technical requirements for `clireader`:

*   Be written in Python.
*   Rich formatting must use a standard text formating syntax.


Design Discussion
=================

Terminal Controller Structure
-----------------------------
This is starting from the design I made for the terminal interface
for my blackjack game. In that design:

*   The game engine sends events to a game UI object.
*   The game UI translates that even into UI actions.
*   The game UI then sends those actions to a Terminal Controller object.
*   The Terminal Controller then updates the terminal and waits for input.

This design is starting with the Terminal Controller object. Do I need
a separate object that is equivalent to the game UI to drive the
terminal controller? Probably. It'll be very small. But I think it's
good to keep loading of files and such separate. That said, it doesn't
have to be an object. Maybe a bunch of functions makes more sense?

The tricky thing is, currently, paging is all done in the terminal
controller, and that's 90% of the work of the application. If that's
handed there, then I'm not sure it makes sense to have a UI object
just reads files. So, maybe the paging should be split out to a
separate object? Something like:

*   Pager object to manage the text.
*   A Controller to handle the commands.
*   A Viewer to manage the terminal.


Pager API
---------
The API for the `Pager` manages the text being displayed in the terminal.
It has the following public attributes:

:text: The raw text being managed.
:title: A title for the text being managed.
:paged: The text divided into pages.
:pages: The total number of pages of the text.
:height: The height in lines of the pages.
:width: The width in characters of the pages.

It has the following public methods:

:flow(height, width): Reflow the text for the new dimensions.
:load(file): Read and store text from a file.
:get_page(page): Return the text for the given page number.


Viewer API
----------
The API for the `Viewer` manages the terminal displaying the text.
It has the following public attributes:

:term: The blessed.Terminal object representing the terminal.

It has the following public methods:

:clear(): Clear the page in the terminal.
:draw_commands(cmds): Draw the available commands to the terminal.
:draw_frame(frame_type): Draw the app frame to the terminal.
:draw_status(title, page_num): Draw the status line to the terminal.
:draw_page(text): Draw the given page to the terminal.
:get_key(): Wait for a keystroke from the user.
:get_text(): Get a text string from the user.


Loop:
-----
The loop understands both the `Pager` and the `Viewer` and translates
user commands into API calls to them. It also defines what actions are
available to the user. It has the following attributes:

:pager: The `Pager` object for the currently displayed text.
:viewer: The `Viewer` object for the terminal.
:current_page: The page being displayed.

It has the following functions available:

:back_page(): View the previous page of the text.
:next_page(): View the next page of the text.
:init_screen(): Draw the initial screen.
:home(): View the first page of the text.
:end(): View the last page of the text.
:load_page(file): Load the given file for viewing.

While described like an API here, the loop is function. This is because
there really isn't any need for anything to interact with the loop once
it's running. No output needs to go back to calling applications. It
just runs until the user is done reading and exits.

It may be worth asking why a loop is needed at all. The reason is
`blessed.Terminal.fullscreen()`. To take over the terminal, you need
to run in fullscreen mode. The easiest way to do that is with the
`fullscreen` context manager. And to use the context manager, you
have to run everything in a loop. Or, at least, that's the easiest
way to do it that I've found.


When to Rewrap Text
-------------------
Text files don't come with any certain indicators of when text should
reflow for the size of the viewing area. This makes it difficult to know
when newline characters indicate a hard-wrapped paragraph or visual
formatting that shouldn't be reflowed. Any detection for this is likely
to be complex and prone to errors.

`clireader` should probably have a couple of modes for how it makes the
decision to rewrap text. Some modes could include:

*   No rewrapping. Long lines are just truncated.
*   Only lines longer than the width of the viewer are wrapped.
*   Reflow everything.
*   Detect reflowable paragraphs and reflow them.

Users should be able to switch between the modes when using the program
to find the mode that works best for the document. That mode should be
an attribute of the `Pager` object.


Rich Formatting and Word Wrapping
---------------------------------
Does `wordwrap` already handle this? It does not.
