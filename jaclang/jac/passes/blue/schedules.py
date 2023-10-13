"""Pass schedules."""
from .ast_build_pass import AstBuildPass  # noqa: I100
from .sub_node_tab_pass import SubNodeTabPass
from .import_pass import ImportPass  # noqa: I100
from .sym_tab_build_pass import SymTabBuildPass  # noqa: I100
from .decl_def_match_pass import DeclDefMatchPass  # noqa: I100
from .semantic_check_pass import SemanticCheckPass  # noqa: I100
from .blue_pygen_pass import BluePygenPass  # noqa: I100
from .pyout_pass import PyOutPass  # noqa: I100
from .dot_exporter_pass import DotGraphPass  # noqa: I100
from .ast_printer_pass import ASTPrinterPass  # noqa: I100
from .sym_tab_printer_pass import SymbolTablePrinterPass  # noqa: I100
from .sym_tab_dot_exporter_pass import SymtabDotGraphPass   # noqa: I100


py_code_gen = [
    AstBuildPass,
    SubNodeTabPass,
    ImportPass,
    SymTabBuildPass,
    DeclDefMatchPass,
    SemanticCheckPass,
    BluePygenPass,
]

py_transpiler = [
    *py_code_gen,
    PyOutPass,
]

ast_dot_gen = [
    AstBuildPass,
    DotGraphPass,
]

full_ast_dot_gen = [
    AstBuildPass,
    SubNodeTabPass,
    ImportPass,
    SymTabBuildPass,
    DeclDefMatchPass,
    DotGraphPass,
]

ast_print = [
    AstBuildPass,
    ASTPrinterPass
]

full_ast_print = [
    AstBuildPass,
    SubNodeTabPass,
    ImportPass,
    SymTabBuildPass,
    DeclDefMatchPass,
    ASTPrinterPass
]

sym_tab_print = [
    AstBuildPass,
    SubNodeTabPass,
    ImportPass,
    SymTabBuildPass,
    DeclDefMatchPass,
    SymbolTablePrinterPass
]

sym_tab_dot_gen = [
    AstBuildPass,
    SubNodeTabPass,
    ImportPass,
    SymTabBuildPass,
    DeclDefMatchPass,
    SymtabDotGraphPass
]
