

class PlanGraph:
  pass

class DependencyGraph:
  pass

def ConstructDependencyGraph(R):
  pass

def AddRoot(G, x):
  pass

def CodePlan(R, Delta_seeds, Theta, L):
  """
  Inputs: 
  - R: the source code of a repository
  - Delta_seeds: a set of seed edit specifications
  - Theta: an oracle
  - L: an LLM
  """

  """
  Plan graph G. Each node is a tuple <B, I, Status>.
    - B: Block of code (sequence of code locations) in R
    - I: Edit instruction (diff)
    - Status: Either PENDING or COMPLETED
  """
  G: PlanGraph = None

  """
  Dependency graph D. represents the syntactic and semantic dependency relations
  between code blocks in the repository R
  """
  D: DependencyGraph = ConstructDependencyGraph(R)
  
  while len(Delta_seeds) != 0:
    IntializePlanGraph(G, Delta_seeds)
    AdaptivePlanAndExecute(R, D, G)
    Delta_seeds = Theta(R)

def InitializePlanGraph(G, Delta_seeds):
  for (B, I) in Delta_seeds:
    AddRoot(G, (B, I, "PENDING"))

def AdaptivePlanAndExecute(R, D, G):
  while HasNodesWith(G, "PENDING"):
    (B, I, Pending) = GetNextPending(G)
  
    # First step: extract fragment of code
    """
    We found the surrounding context is most helpful when a block belongs to a
    class. For such blocks, we sketch the enclosing class. That is, in addition
    to the code of block B, we also keep declarations of the enclosing class
    and its members
    """
    Fragment = ExtractCodeFragment(B, R, I)

    # Second step: gather context of the edit
    """
    The context of the edit (line 38-41) consists of (a) spatial context, which
    contains related code such as methods called from the block B, and (b)
    temporal context, which contains the previous edits that caused the need to
    edit the block B. The temporal context is formed by edits along the paths
    from the root nodes of the plan graph to B
    """
    Context = GatherContext(B, R, D)

    # Third step: use the LLM to get edited code fragment
    Prompt = MakePrompt(Fragment, I, Context)
    NewFragment = InvokeLLM(L, Prompt)

    # Fourth step: merge the updated code fragment into R
    R = Merge(NewFragment, B, R)
    Labels = ClassifyChanges(Fragment, NewFragment)
    D_prime = UpdateDependencyGraph(D, Labels, Fragment, NewFragment, B)

    # Fifth step: adaptively plan and propagate the effect of the edit on
    # dependant code
    BlockRelationPairs = GetAffectedBlocks(Labels, B, D, D_prime)
    MarkCompleted(B, G)
    for (B_prime, rel) in BlockRelationPairs:
      N = GetNode(B)
      M = SelectOrAddNode(B_prime, None, Pending)
      AddEdge(G, M, N, rel)
      
    D = D_prime

def GatherContext(B, R, D):
  SC = GetSpatialContext(B, R)
  TC = GetTemporalContext(G, B)
  return (SC, TC)