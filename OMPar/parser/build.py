# Copyright (c) Microsoft Corporation. 
# Licensed under the MIT license.

from tree_sitter import Language, Parser

Language.build_library(
  # Store the library in the `build` directory
  'my-languages.so',

  # Include one or more languages
  [
    'vendor/tree-sitter-c-sharp'#,
    # 'vendor/tree-sitter-c',    # for C language support
    # 'vendor/tree-sitter-cpp'   # for C++ language support (if needed)
  ]
)

