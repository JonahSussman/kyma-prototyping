import os
import threading
import json
import subprocess
from typing import Optional, Callable
from enum import Enum
import asyncio
from dataclasses import dataclass

from monitors4codegen.multilspy import LanguageServer
from monitors4codegen.multilspy.multilspy_types import Range, Position
from tree_sitter import Language, Tree, Node

def is_within_range(range: Range, pos: Position):
  if range["start"]["line"] < pos["line"] < range["end"]["line"]:
    return True
  elif pos["line"] == range["start"]["line"] and pos["line"] == range["end"]["line"]:
    return range["start"]["character"] <= pos["character"] <= range["end"]["character"]
  elif pos["line"] == range["start"]["line"]:
    return pos["character"] >= range["start"]["character"]
  elif pos["line"] == range["end"]["line"]:
    return pos["character"] <= range["end"]["character"]
  else:
    return False
  
# TODO: How should be handle cross-referencing between the two trees?
def gumtree_diff(old_file: str, new_file: str):
  GUMTREE_LOC = '/home/jonah/Projects/kyma-prototyping/gumtree-3.1.0-SNAPSHOT/bin/gumtree'
  TREE_SITTER_PARSER_LOC = '/home/jonah/Projects/kyma-prototyping/tree-sitter-parser'

  env = os.environ.copy()
  env['PATH'] = TREE_SITTER_PARSER_LOC + ':' + os.environ.get('PATH')
  result = subprocess.run(
    [GUMTREE_LOC, 'textdiff', old_file, new_file, '-g', 'java-treesitter', '-f', 'JSON'], 
    stdout=subprocess.PIPE, 
    env=env
  )
  return json.loads(result.stdout)

ChangeCause = Enum('ChangeCause', [
  'INITIAL', # Initial change
  'PARENT_OF', 'CHILD_OF', 'CONSTRUCTS', 'CONSTRUCTED_BY' # Syntactic
  'IMPORTS', 'IMPORTED_BY', # Import
  'BASE_CLASS_OF', 'DERIVED_CLASS_OF', # Inheritance
  'OVERRIDES', 'OVERRIDDEN_BY', # Method override
  'CALLS', 'CALLED_BY', # Method invocation
  'INSTANTIATES', 'INSTANTIATED_BY', # Object instantiation 
  'USES', 'USED_BY', # Field use
])

NodeTicket = int

class Ticketer:
  """
  Using nodes for locations solves a lot of problems that come with storing
  byte/row-col information. You can make direct edits to trees and still have
  the references be a-ok. The problem comes that sometimes we may need to change
  a node or replace a tree associated with a file with an entire new one.
  Because they are different objects, the Changes now have references to trees
  that don't exist anymore.

  Idea of the Ticketer class is that the CodePlan class (or somewhere else)
  should have a central source of truth for mapping URIs to trees. We map nodes
  to ints, and when we update or invalidate a node, we use this class. An extra
  buffer layer of indirection.
  """

  def __init__(self):
    # Associate nodes with a specific number
    self.ticket_counter: int = 0 # Highest unused ticket number
    self.node_to_ticket: dict[int, NodeTicket]  = {} # id -> NodeTicket
    self.ticket_to_node: dict[NodeTicket, Node] = {} # NodeTicket -> Node

  def get_ticket(self, node: Node):
    if id(node) in self.node_to_ticket:
      return self.node_to_ticket[id(node)]
    
    self.node_to_ticket[id(node)] = self.ticket_counter
    self.ticket_counter += 1

    return self.ticket_counter - 1
  
  def get_node(self, ticket: NodeTicket) -> Optional[Node]:
    if ticket in self.ticket_to_node:
      return self.ticket_to_node[ticket]
    
    return None
    
  def change_node_assoc_with_ticket(self, ticket: NodeTicket, node: Node):
    self.node_to_ticket[id(node)] = ticket
    self.ticket_to_node[ticket] = node


@dataclass
class Change:
  """
  The 'seed'. Has all 3 types of context embedded within it. Fingers crossed we
  try and keep this immutable
  """

  # --- Temporal Context ---
  uri: str # The file URI

  # TODO: Store a tree-sitter node or NodeTicket instead of a Range. This will
  # allow us to keep references to locations in files more "steady" when a file
  # is modified.
  range: Range # The edit range

  # NOTE: Not sure if this trio is really necessary. Lots of data duplication
  # for sure. Storing the trees especially gets confusing when the question of
  # "which tree is the most up to date" gets thrown around. See the Ticketer
  # class for a potential solution.
  file_before_change: str
  tree_before_change: Tree
  edit_before_change: str

  node_ticket: NodeTicket

  file_after_change: Optional[str]
  tree_after_change: Optional[Tree]
  edit_after_change: Optional[str]

  # Linked list structure, could also just have a list
  # perhaps less like a tree and more like a graph?

  # head: "Change"
  prev: Optional["Change"]

  # --- Causal Context ---
  change_cause: ChangeCause

  # --- Spatial Context ---
  spatial_context: str

  def cascaded_change(
    self,
    new_uri: str,
    new_range: Range,
    new_change_cause: ChangeCause,
    new_spatial_context: str
  ) -> "Change":
    return Change(
      uri=new_uri,
      range=new_range,

      file_before_change=self.file_after_change,
      tree_before_change=self.tree_after_change,
      edit_before_change=self.edit_after_change,

      file_after_change=None,
      tree_after_change=None,
      edit_after_change=None,

      node_ticket=None,

      # head=self.head,
      prev=self,

      change_cause=new_change_cause,
      spatial_context=new_spatial_context,
    )


class LLMResult:
  """
  Magical result from the LLM. Haven't even looked at the AI stuff yet.
  """

  pass

class CodePlan:
  # TODO: Store trees in here? Then we really do need to just store the edits
  # and not the full file...

  def __init__(
    self,
    language: Language,
    project_path: str,
    lsp: LanguageServer,
  ):
    self.language: Language = language
    self.project_path: str = project_path

    # TODO: This LanguageServer causes async-await hell everywhere. There's got
    # to be a better way
    self.lsp: LanguageServer = lsp

    self.ticketer = Ticketer()

    # Changes yet to be looked at, but still committed in the filesystem. We
    # need to store the nodes, then when a change is made, intelligently make
    # it. Priority of types of changes? 
    self.changes_to_cascade: list[Change] = []

  def queue_change_cascade(self, change: Change):
    self.changes_to_cascade.append(change)

  async def run(self):
    while len(self.changes_to_cascade) > 0:
      # Restart each time to avoid waiting for build message. Unclear how to
      # find that out.
      async with self.lsp.start_server():
        change = self.changes_to_cascade.pop(0)

        # FIXME: Figure out how to handle things when affected blocks are in the
        # same file, or even in the same file as the original change. Iterator
        # perhaps? Or do we even need to worry about this?
        affected_blocks = await self.get_affected_blocks(change)

        print("affected_blocks:")
        for b in affected_blocks:
          print(f"-{b.uri=}\n-{b.range=}\n")

        return

        # NOTE: May want to have something like this?
        # uri_to_changes: dict[str, list[Change]] = {}

        results: list[Change] = []

        for block in affected_blocks:
          prompt = self.construct_prompt(block)
          llm_result = self.generate_llm_result(prompt)
          result = self.combine_result(llm_result, block)

          results.append(result)

        # Perhaps have a "failed merges" thing? Need to loop it back in with the
        # LLM
        for result in results:
          self.merge_changes(result)
          self.changes_to_cascade.append(result)

        # oracle stuff
        if len(self.changes_to_cascade) == 0:
          self.run_oracle()


  # FIXME: This whole function can be done a whole lot cleaner with gumtree at
  # our disposal.
  async def get_affected_blocks(self, spawning_change: Change) -> list[Change]:
    async def do_thing(
      query: str, 
      hash: Callable[[Node, str], str],
      is_modified: Callable[[Node, Node], bool],
    ) -> list[Change]:
      q = self.language.query(query)
      old_c = q.captures(spawning_change.tree_before_change.root_node)
      new_c = q.captures(spawning_change.tree_after_change.root_node)

      fbc: str = spawning_change.file_before_change
      fac: str = spawning_change.file_after_change
      old_dict: dict[str, Node] = {hash(c[0], fbc): c[0] for c in old_c}
      new_dict: dict[str, Node] = {hash(c[0], fac): c[0] for c in new_c}

      keys_removed = set(old_dict.keys()) - set(new_dict.keys())
      keys_added   = set(new_dict.keys()) - set(old_dict.keys())
      keys_common  = set(old_dict.keys()).intersection(set(new_dict.keys()))

      added:    list[Node] = [new_dict[k] for k in keys_added]
      deleted:  list[Node] = [old_dict[k] for k in keys_removed]
      modified: list[tuple[Node, Node]] = [
        (old_dict[k], new_dict[k]) 
        for k in keys_common 
        if is_modified(old_dict[k], new_dict[k])
      ]

      return added, deleted, modified


    async def from_imports() -> list[Node]:
      h = lambda n, f: f[n.children[1].start_byte:n.children[1].end_byte]
      m = lambda x, y: False

      added, deleted, modified = await do_thing(
        "(import_declaration) @import_declaration", h, m
      )

      output: list[Node] = []

      for imp in deleted:
        row, col = imp.children[1].end_point

        refs = await (self.lsp.request_references(
          spawning_change.uri[len(f"file://{self.project_path}"):],
          row,
          col
        ))

        # NOTE: There's something here about for all cases of each type
        # "expanding out" to a node of a specific type and deleting duplicates.
        # For example, say we want to find all references to Bicycle, and in
        # this method `refs` has these two locations:

        #   Bicycle b = new Bicycle();
        #   ^~~~~~~         ^~~~~~~

        # To save on LLM calls, we can combine the two intelligently by finding
        # the method node that they both belong to and filter based on that.

        # TODO: How should we handle overlapping ranges?

        for ref in refs:
          if ref['uri'] != spawning_change.uri:
            continue
          if is_within_range(Range(**ref['range']), Position(line=row, character=col)):
            continue

          output.append(spawning_change.cascaded_change(
            spawning_change.uri,
            ref['range'],
            ChangeCause.IMPORTED_BY,
            "",
          ))

      return output

    async def from_fields() -> list[Node]:
      # name = node.child_by_field_name('declarator').child_by_field_name('name')
      # return file_contents[name.start_byte:name.end_byte]
      return []
    async def from_class_declarations() -> list[Node]:
      return []
    async def from_methods() -> list[Node]:
      return []
    async def from_constructors() -> list[Node]:
      return []


    return await from_imports() \
      + await from_fields() \
      + await from_class_declarations() \
      + await from_methods() \
      + await from_constructors()