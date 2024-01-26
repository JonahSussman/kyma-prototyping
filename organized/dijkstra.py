from queue import PriorityQueue
from dataclasses import dataclass

from tree_sitter import TreeCursor, Node, Tree

# NOTE: Ultimately, this file is most likely meaningless in the grand scheme of
# things (too slow), but I spent way too much time on it.

class GKind:
  pass

@dataclass
class GKindAdd(GKind):
  node: Node
@dataclass
class GKindDel(GKind):
  node: Node
@dataclass
class GKindMod(GKind):
  old_node: Node
  new_node: Node
# @dataclass
# class GKindNil(GKind):
#   pass

# "novel" nodes on the rhs, lhs Try to "modify" nodes Perhaps each tree should
# have a "canonical representation"? I.e. we sort the method names, and the ...
# no that's terrible. Cause the method names might be in a specific order for a
# specific reason.

def dijkstra(old_tree: Tree, new_tree: Tree):
  old_cur: TreeCursor = old_tree.walk()
  new_cur: TreeCursor = new_tree.walk()

  while old_cur.goto_last_child(): continue
  while new_cur.goto_last_child(): continue

  max_old_idx = old_cur.descendant_index()
  max_new_idx = new_cur.descendant_index()

  # print(f"{max_old_idx=} {max_new_idx=}")

  old_cur.goto_descendant(0)
  new_cur.goto_descendant(0)

  # A "node" is the pair (old_idx, new_idx)
  GNode = tuple[int, int]

  dist: dict[GNode, float] = {}
  pred: dict[GNode, GNode] = {}
  kind: dict[GNode, GKind] = {} # The kind of "move" that took us

  dist[(0, 0)] = 0
  pq = PriorityQueue()
  pq.put((0.0, (0, 0)))

  def pq_put(fm: tuple[int, int], to: tuple[int, int], inc: float, kd: GKind):
    dist[to] = dist[fm] + inc
    pred[to] = fm
    kind[to] = kd
    pq.put((dist[fm] + inc, to))

  while pq:
    pq_top: tuple[float, GNode] = pq.get()
    curr_dist, idx = pq_top
    print(pq_top)
    old_idx, new_idx = idx

    if curr_dist != dist[(old_idx, new_idx)]:
      continue

    old_cur.goto_descendant(old_idx)
    new_cur.goto_descendant(new_idx)

    if old_idx > max_old_idx and new_idx > max_new_idx:
      break
    elif old_idx > max_old_idx:
      pq_put(idx, (old_idx, new_idx + 1), 1.0, GKindAdd(new_cur.node))
      continue
    elif new_idx > max_new_idx:
      pq_put(idx, (old_idx + 1, new_idx), 1.0, GKindDel(old_cur.node))
      continue

    # TODO: Figure out modifications
    if old_cur.node.type == new_cur.node.type:
      pq_put(idx, (old_idx + 1, new_idx + 1), 0.0, None)
      continue
    else:
      pq_put(idx, (old_idx, new_idx + 1), 1.0, GKindAdd(new_cur.node))
      pq_put(idx, (old_idx + 1, new_idx), 1.0, GKindDel(old_cur.node))
      continue
  
  edits = []
  
  curr = (max_old_idx, max_new_idx)
  while curr != (0, 0):
    k = kind[curr]
    if k is not None:
      edits.append(k)

    curr = pred[curr]

  edits.reverse()

  return edits