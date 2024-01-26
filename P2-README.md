# KAI Phase 2

## Dependencies

Clone the following repos:

```sh
# tree-sitter java support
git clone https://github.com/tree-sitter/tree-sitter-java

# multipylsp from here: https://github.com/microsoft/monitors4codegen?tab=readme-ov-file#4-multilspy
# NOTE: Had a lot of errors installing, only worked with python 3.10?

# gumtree for intelligent tree diffing. Go to https://github.com/GumTreeDiff/gumtree/wiki/Getting-Started for build instructions
git clone https://github.com/GumTreeDiff/gumtree



# NOTE: Might be unnecessary, as the latest builds of gumtree have tree-sitter support built in
git clone --recurse-submodules -j8 https://github.com/GumTreeDiff/tree-sitter-parser
```

## Directory layout

-  `playground/`: Misc testing stuff. Only look if you want to peek at the unhinged madness that is the inner machinations of my mind.
- `p2-notes.md`: Notes doc that I used to keep track of stuff. Again, you might go insane if you look at this. Less so than the playground, but still...
- `java-test-projects/`: A folder with a test project in it for testing
- `organized/`: The organized stuff that I've worked on
  - `tester_notebook.ipynb` old, probably doesn't work
  - `tester_script.py` A useful tester script testing stuff
  - `multilspy_monkey_patch.py` Monkey patch a bunch of stuff into the lsp library
  - `dijkstra.py` My pride and joy algorithm that's ungodly slow and should probably remove
  - `core_logic.py` The core logic