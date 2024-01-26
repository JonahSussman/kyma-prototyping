# BE WARNED, UNHINGED NOTES BELOW

Take the code
Make the change
- use textdocument/symbol to find the new location of the shit
- does tree-sitter allow partial java code?
Find all the code that "touches" it
update if necessary

eclipse jdtls has refactoring


use the tree to determine if there has been any changes within the function?

Are there any errors in *this* file?

"this is the Nth draft."

These commands are available
- https://github.com/eclipse-jdtls/eclipse.jdt.ls/blob/master/org.eclipse.jdt.ls.core/src/org/eclipse/jdt/ls/core/internal/JDTDelegateCommandHandler.java#L127
- Vscode has these commands: https://github.com/redhat-developer/vscode-java/blob/174e8a8f0c26fbf2b6b08e3f7dc01cb37be86de3/src/commands.ts#L239

Show call/type hierarchy?
- look above for where it's called. Look here for how it's impl'd: https://github.com/eclipse-jdtls/eclipse.jdt.ls/blob/65ec9231d0986e18acc9a8bc52d86d6d151d9dab/org.eclipse.jdt.ls.core/src/org/eclipse/jdt/ls/core/internal/commands/TypeHierarchyCommand.java
- How the vscode ext calls it: https://github.com/redhat-developer/vscode-java/blob/master/src/typeHierarchy/util.ts#L84
- Vscode's types for the typeHierarchy call: https://github.com/redhat-developer/vscode-java/blob/master/src/typeHierarchy/protocol.ts#L7



blocks of code vs the locations that make it up


# Relations and how to accomplish it

## syntactic relations
- ParentOf
- ChildOf
- Constructs
- ConstructedBy

between a block 𝑐 and the block 𝑝 that encloses 𝑐 syntactically; a special
case being a constructor and its enclosing class related by Construct and
ConstructedBy

Can be accomplished via tree queries?

## import relations 
Imports
ImportedBy

- either of these
  - hover and use the text there
  - go to definition, get package from that file.
- compare with import statements at the top of the file in the tree

## inheritance relations
BaseClassOf
DerivedClassOf

java.navigate.openTypeHierarchy

## method override relations
Overrides
OverridenBy

vscode has "go to super impl", though it might not be obvious, have to check
each method if it has a super. could be slow

## method invocation relations 
Calls
CalledBy

"Find all references", note it may include the location itself

## object instantiation relations 
Instantiates
InstantiatedBy

"go to definition", check if it's a constructor
or the other direction? Constructor and then find all references.
constructor_declaration exists in tree-sitter!

## field use relations 
Uses
UsedBy


# The before and after

<!-- Ok so how should be determine the changes. We have a straight up diff, but there's no ast there. 

Ok how about diff -> find beginning and end diff bytes -> find in tree the smallest node that encapsulates all the bytes? no.... -->

ok there's only a couple of different edits that we really want to support. Modify, add, and delete.

<!-- ## Import statements

check the import statements between the two using tree-sitter

## -->

take out all whitespace and comments (nodes?).
catalog all:
- import statements
- fields in the class
- class declarations
- methods and constructors (and their signatures)

from there, we can see if the trees are the same or different between the two, or do a diff (cache the nodes *and names*)

Another wrinkle is that the lsp server can only act on one version of the stuff at a time...


How to handle changes of names??? Handling the change of a function body is easy. Changing a method signature is easy. Changing the type of a field is easy. What about changing a class name?

Shit if they change the class name and we get all references beforehand, then we might get places that have already been changed. Will have to check if they exist in the new graph?


Well it doesn't have to be perfect, screw it.








Tree beforehand, tree afterward

an affected block is not merely a position in code, but rather a node in a tree.
The tree-sitter node contains the location information.

## Ticketing

First time, node -> get a ticket. Store the relation node <-> ticket