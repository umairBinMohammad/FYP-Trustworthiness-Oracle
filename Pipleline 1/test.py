from tree_sitter import Language, Parser

# Compile the language library (only once needed)
Language.build_library(
    'build/my-languages.so',  # Output path
    ['tree-sitter-python']     # Paths to language repos
)

# Load the compiled library
PY_LANGUAGE = Language('build/my-languages.so', 'python')

# Use the parser
parser = Parser()
parser.set_language(PY_LANGUAGE)

source_code = b'''
def add(a, b):
    return a + b
'''

tree = parser.parse(source_code)
root_node = tree.root_node
print(root_node.sexp())  # See the full AST in s-expression format
