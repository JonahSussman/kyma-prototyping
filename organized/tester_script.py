from core_logic import *
from tree_sitter import *

import monitors4codegen.multilspy.multilspy_types as multilspy_types
from monitors4codegen.multilspy.multilspy_config import MultilspyConfig
from monitors4codegen.multilspy.multilspy_logger import MultilspyLogger

TS_OUTPUT_PATH = "build/language-java.so"
TS_REPO_PATHS = ["../tree-sitter-java/"]
TS_NAME = "java"

Language.build_library(TS_OUTPUT_PATH, TS_REPO_PATHS)
TS_JAVA_LANGUAGE = Language(TS_OUTPUT_PATH, TS_NAME)

PROJECT_PATH  = "/home/jonah/Projects/kyma-prototyping/java-test-projects/complex-numbers/"

LSP_CONFIG = MultilspyConfig.from_dict({"code_language": "java"})
LSP_LOGGER = MultilspyLogger()

LSP = LanguageServer.create(
  LSP_CONFIG, LSP_LOGGER, 
  PROJECT_PATH
)

parser = Parser()
parser.set_language(TS_JAVA_LANGUAGE)

path  = '/home/jonah/Projects/kyma-prototyping/java-test-projects/complex-numbers/src/main/java/net/jsussman/complexnumber/ComplexNumber.java'
path2 = '/home/jonah/Projects/kyma-prototyping/java-test-projects/complex-numbers/src/main/java/net/jsussman/complexnumber/ComplexNumber2.java'
uri = f"file://{path}"

file_before_change: str
with open(path, 'r') as f:
  file_before_change = f.read()
tree_before_change = parser.parse(bytes(file_before_change, 'utf-8'))

file_after_change: str
with open(path2, 'r') as f:
  file_after_change = f.read()
tree_after_change = parser.parse(bytes(file_after_change, 'utf-8'))

change = Change(
  uri=uri,
  range=multilspy_types.Range(
    start=multilspy_types.Position(
      line=tree_before_change.root_node.start_point[0],
      character=tree_before_change.root_node.start_point[1],
    ),
    end=multilspy_types.Position(
      line=tree_before_change.root_node.end_point[0],
      character=tree_before_change.root_node.end_point[1],
    ),
  ),
  file_before_change=file_before_change,
  tree_before_change=tree_before_change,
  edit_before_change="",
  file_after_change=file_after_change,
  tree_after_change=tree_after_change,
  edit_after_change="",
  node_ticket=None,
  prev=None,
  change_cause=ChangeCause.INITIAL,
  spatial_context=""
)

cp = CodePlan(TS_JAVA_LANGUAGE, PROJECT_PATH, LSP)
cp.queue_change_cascade(change)
asyncio.run(cp.run())