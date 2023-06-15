"""Parser for Jac."""
from jaclang.jac.errors import JacParseErrorMixIn
from jaclang.jac.lexer import JacLexer
from jaclang.utils.sly.yacc import Parser, YaccProduction

_ = None  # For flake8 linting


class JacParser(JacParseErrorMixIn, Parser):
    """Parser for Jac."""

    tokens = JacLexer.tokens
    debugfile = "parser.out"

    # All mighty start rule
    # ---------------------
    @_("doc_tag element_list")
    def start(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Start rule."""
        return p

    @_(
        "empty",
        "DOC_STRING",
    )
    def doc_tag(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Doc tag rule."""
        return p

    # Jac program structured as a list of elements
    # --------------------------------------------
    @_(
        "element",
        "element_list element",
    )
    def element_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Element list rule."""
        return p

    # Element types
    # -------------
    @_(
        "global_var",
        "test",
        "mod_code",
        "import_stmt",
        "include_stmt",
        "architype",
        "ability",
        "sub_ability_spec",
    )
    def element(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Element rule."""
        return p

    @_("access_tag KW_GLOBAL global_var_clause SEMI")
    def global_var(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Global variable rule."""
        return p

    @_(
        "KW_PRIV",
        "KW_PUB",
        "KW_PROT",
    )
    def access(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Permission tag rule."""
        return p

    @_(
        "access COLON",
        "empty",
    )
    def access_tag(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Permission tag rule."""
        return p

    @_(
        "NAME EQ expression",
        "global_var_clause COMMA NAME EQ expression",
    )
    def global_var_clause(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Global variable tail rule."""
        return p

    @_("KW_TEST NAME multistring code_block")
    def test(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Test rule."""
        return p

    @_("KW_WITH KW_ENTRY code_block")
    def mod_code(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Module-level free code rule."""
        return p

    # Import Statements
    # -----------------
    @_(
        "KW_IMPORT sub_name import_path SEMI",
        "KW_IMPORT sub_name import_path KW_AS NAME SEMI",
        "KW_IMPORT sub_name KW_FROM import_path COMMA name_as_list SEMI",
    )
    def import_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Import rule."""
        return p

    @_("KW_INCLUDE sub_name import_path SEMI")
    def include_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Import rule."""
        return p

    @_(
        "import_path_prefix",
        "import_path_prefix import_path_tail",
    )
    def import_path(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Import path rule."""
        return p

    @_(
        "NAME",
        "DOT NAME",
        "DOT DOT NAME",
    )
    def import_path_prefix(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Import path prefix rule."""
        return p

    @_(
        "DOT NAME",
        "import_path_tail DOT NAME",
    )
    def import_path_tail(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Import path tail rule."""
        return p

    @_(
        "NAME",
        "NAME KW_AS NAME",
        "name_as_list COMMA NAME",
        "name_as_list COMMA NAME KW_AS NAME",
    )
    def name_as_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Name as list rule."""
        return p

    # Architype elements
    # ------------------
    @_(
        "architype_full_spec",
        "architype_decl",
        "architype_def",
    )
    def architype(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Architype rule."""
        return p

    @_(
        "access_tag KW_NODE NAME inherited_archs member_block",
        "access_tag KW_EDGE NAME inherited_archs member_block",
        "access_tag KW_OBJECT NAME inherited_archs member_block",
        "access_tag KW_WALKER NAME inherited_archs member_block",
    )
    def architype_full_spec(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Architype rule."""
        return p

    @_(
        "access_tag KW_NODE NAME inherited_archs SEMI",
        "access_tag KW_EDGE NAME inherited_archs SEMI",
        "access_tag KW_OBJECT NAME inherited_archs SEMI",
        "access_tag KW_WALKER NAME inherited_archs SEMI",
    )
    def architype_decl(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Architype declaration rule."""
        return p

    @_(
        "strict_arch_ref member_block",
        "NAME strict_arch_ref member_block",
    )
    def architype_def(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Architype definition rule."""
        return p

    @_(
        "empty",
        "inherited_archs sub_name",
    )
    def inherited_archs(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Sub name list rule."""
        return p

    @_("COLON NAME")
    def sub_name(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Sub name rule."""
        return p

    # Ability elements
    # ----------------
    @_(
        "ability_full_spec",
        "ability_decl",
        "ability_def",
    )
    def ability(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Ability rule."""
        return p

    @_(
        "access_tag KW_CAN NAME code_block",
        "access_tag KW_CAN NAME return_type_tag code_block",
        "access_tag KW_CAN NAME func_decl code_block",
    )
    def ability_full_spec(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Ability rule."""
        return p

    @_(
        "access_tag KW_CAN NAME SEMI",
        "access_tag KW_CAN NAME return_type_tag SEMI",
        "access_tag KW_CAN NAME func_decl SEMI",
    )
    def ability_decl(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Ability declaration rule."""
        return p

    @_(
        "ability_ref code_block",
        "NAME ability_ref code_block",
    )
    def ability_def(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Architype definition rule."""
        return p

    @_(
        "strict_arch_ref ability_ref code_block",
        "strict_arch_ref ability_ref func_decl code_block",
        "NAME strict_arch_ref ability_ref code_block",
        "NAME strict_arch_ref ability_ref func_decl code_block",
    )
    def sub_ability_spec(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Ability rule."""
        return p

    # Attribute blocks
    # ----------------
    @_(
        "LBRACE RBRACE",
        "LBRACE doc_tag member_stmt_list RBRACE",
    )
    def member_block(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Attribute block rule."""
        return p

    @_(
        "member_stmt",
        "member_stmt_list member_stmt",
    )
    def member_stmt_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Attribute statement list rule."""
        return p

    @_(
        "has_stmt",
        "can_stmt",
    )
    def member_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Attribute statement rule."""
        return p

    # Has statements
    # --------------
    @_("access_tag KW_HAS has_assign_clause SEMI")
    def has_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Has statement rule."""
        return p

    @_(
        "typed_has",
        "has_assign_clause COMMA typed_has",
    )
    def has_assign_clause(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Has assign list rule."""
        return p

    @_(
        "has_tag NAME type_tag",
        "has_tag NAME type_tag EQ expression",
    )
    def typed_has(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Parameter variable rule rule."""
        return p

    @_(
        "has_tag KW_HIDDEN",
        "has_tag KW_ANCHOR",
        "empty",
    )
    def has_tag(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Has tag rule."""
        return p

    @_("COLON type_name")
    def type_tag(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Type hint rule."""
        return p

    @_("RETURN_HINT type_name")
    def return_type_tag(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Type hint rule."""
        return p

    @_(
        "builtin_type",
        "NULL",
        "NAME",
        "TYP_LIST LSQUARE type_name RSQUARE",
        "TYP_DICT LSQUARE type_name COMMA type_name RSQUARE",
    )
    def type_name(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Type hint rule."""
        return p

    @_(
        "TYP_STRING",
        "TYP_BYTES",
        "TYP_INT",
        "TYP_FLOAT",
        "TYP_LIST",
        "TYP_TUPLE",
        "TYP_SET",
        "TYP_DICT",
        "TYP_BOOL",
        "TYP_ANY",
        "TYP_TYPE",
    )
    def builtin_type(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Any type rule."""
        return p

    # Can statements
    # --------------
    @_(
        "access_tag can_ds_ability",
        "access_tag can_func_ability",
    )
    def can_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Can statement rule."""
        return p

    @_(
        "KW_CAN NAME event_clause code_block",
        "KW_CAN NAME event_clause SEMI",
    )
    def can_ds_ability(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Can statement rule."""
        return p

    @_(
        "KW_CAN NAME func_decl code_block",
        "KW_CAN NAME func_decl SEMI",
    )
    def can_func_ability(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Can statement rule."""
        return p

    @_(
        "empty",
        "KW_WITH KW_ENTRY",
        "KW_WITH KW_EXIT",
        "KW_WITH STAR_MUL KW_ENTRY",
        "KW_WITH STAR_MUL KW_EXIT",
        "KW_WITH name_list KW_ENTRY",
        "KW_WITH name_list KW_EXIT",
    )
    def event_clause(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Event clause rule."""
        return p

    @_(
        "NAME",
        "name_list COMMA NAME",
    )
    def name_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Name list rule."""
        return p

    @_(
        "LPAREN RPAREN return_type_tag",
        "LPAREN func_decl_param_list RPAREN return_type_tag",
    )
    def func_decl(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Func declaration parameter rule."""
        return p

    @_(
        "param_var",
        "func_decl_param_list COMMA param_var",
    )
    def func_decl_param_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Func declaration parameters list rule."""
        return p

    @_(
        "NAME type_tag",
        "NAME type_tag EQ expression",
    )
    def param_var(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Parameter variable rule rule."""
        return p

    @_(
        "LBRACE RBRACE",
        "LBRACE doc_tag statement_list RBRACE",
    )
    def code_block(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Code block rule."""
        return p

    # Codeblock statements
    # --------------------
    @_(
        "statement_list statement",
        "statement",
    )
    def statement_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Statement list rule."""
        return p

    @_(
        "assignment SEMI",
        "expression SEMI",
        "if_stmt",
        "try_stmt",
        "for_stmt",
        "while_stmt",
        "raise_stmt SEMI",
        "assert_stmt SEMI",
        "ctrl_stmt SEMI",
        "delete_stmt SEMI",
        "report_stmt SEMI",
        "return_stmt SEMI",
        "yield_stmt SEMI",
        "walker_stmt",
    )
    def statement(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Statement rule."""
        return p

    @_(
        "KW_IF expression code_block",
        "KW_IF expression code_block else_stmt",
        "KW_IF expression code_block elif_list",
        "KW_IF expression code_block elif_list else_stmt",
    )
    def if_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """If statement rule."""
        return p

    @_(
        "KW_ELIF expression code_block",
        "elif_list KW_ELIF expression code_block",
    )
    def elif_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Else if statement list rule."""
        return p

    @_("KW_ELSE code_block")
    def else_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Else statement rule."""
        return p

    @_(
        "KW_TRY code_block",
        "KW_TRY code_block except_list",
        "KW_TRY code_block finally_stmt",
        "KW_TRY code_block except_list finally_stmt",
    )
    def try_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Try statement rule."""
        return p

    @_(
        "except_def",
        "except_list except_def",
    )
    def except_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Except statement list rule."""
        return p

    @_(
        "KW_EXCEPT expression code_block",
        "KW_EXCEPT expression KW_AS NAME code_block",
    )
    def except_def(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Except definition rule."""
        return p

    @_(
        "KW_FINALLY code_block",
    )
    def finally_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Except finally statement rule."""
        return p

    @_(
        "KW_FOR assignment KW_TO expression KW_BY expression code_block",
        "KW_FOR NAME KW_IN expression code_block",
        "KW_FOR NAME COMMA NAME KW_IN expression code_block",
    )
    def for_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """For statement rule."""
        return p

    @_("KW_WHILE expression code_block")
    def while_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """While statement rule."""
        return p

    @_(
        "KW_RAISE",
        "KW_RAISE expression",
    )
    def raise_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Raise statement rule."""
        return p

    @_(
        "KW_ASSERT expression",
        "KW_ASSERT expression COMMA expression",
    )
    def assert_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Assert statement rule."""
        return p

    @_(
        "KW_CONTINUE",
        "KW_BREAK",
        "KW_SKIP",
    )
    def ctrl_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Control statement rule."""
        return p

    @_("KW_DELETE expression")
    def delete_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Delete statement rule."""
        return p

    @_(
        "KW_REPORT expression",
    )
    def report_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Report statement rule."""
        return p

    @_(
        "KW_RETURN",
        "KW_RETURN expression",
    )
    def return_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Report statement rule."""
        return p

    @_(
        "KW_YIELD",
        "KW_YIELD expression",
    )
    def yield_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Yield statement rule."""
        return p

    @_(
        "ignore_stmt SEMI",
        "visit_stmt",
        "revisit_stmt",
        "disengage_stmt SEMI",
        "sync_stmt SEMI",
    )
    def walker_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Walker statement rule."""
        return p

    @_("KW_IGNORE expression")
    def ignore_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Ignore statement rule."""
        return p

    @_(
        "KW_VISIT expression SEMI",
        "KW_VISIT sub_name expression SEMI",
        "KW_VISIT expression else_stmt",
        "KW_VISIT sub_name expression else_stmt",
    )
    def visit_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Visit statement rule."""
        return p

    @_(
        "KW_REVISIT SEMI",
        "KW_REVISIT expression SEMI",
        "KW_REVISIT else_stmt",
        "KW_REVISIT expression else_stmt",
    )
    def revisit_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Visit statement rule."""
        return p

    @_("KW_DISENGAGE")
    def disengage_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Disengage statement rule."""
        return p

    @_("KW_SYNC expression")
    def sync_stmt(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Sync statement rule."""
        return p

    # Expression rules (precedence built into grammar)
    # ------------------------------------------------
    @_(
        "atom EQ expression",
        "KW_HAS NAME EQ expression",  # static variables
    )
    def assignment(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Rule for assignment statement."""
        return p

    @_(
        "walrus_assign",
        "walrus_assign KW_IF expression KW_ELSE expression",
    )
    def expression(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Expression rule."""
        return p

    @_(
        "pipe",
        "pipe walrus_op walrus_assign",
    )
    def walrus_assign(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Walrus assignment rule."""
        return p

    @_(
        "elvis_check",
        "elvis_check PIPE_FWD pipe",  # casting achieved here
        "elvis_check PIPE_FWD filter_ctx",  # for comprehension on list, dict, etc.
        "elvis_check PIPE_FWD spawn_ctx",  # for rapid assignments to collections
        "spawn_ctx PIPE_FWD pipe",  # for function calls
    )
    def pipe(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Expression rule."""
        return p

    @_(
        "logical",
        "logical ELVIS_OP elvis_check",
    )
    def elvis_check(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Expression rule."""
        return p

    @_(
        "compare",
        "compare KW_AND logical",
        "compare KW_OR logical",
    )
    def logical(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Logical rule."""
        return p

    @_(
        "arithmetic",
        "NOT compare",
        "arithmetic cmp_op compare",
    )
    def compare(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Compare rule."""
        return p

    @_(
        "term",
        "term PLUS arithmetic",
        "term MINUS arithmetic",
    )
    def arithmetic(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Arithmetic rule."""
        return p

    @_(
        "factor",
        "factor STAR_MUL term",
        "factor DIV term",
        "factor MOD term",
    )
    def term(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Term rule."""
        return p

    @_(
        "PLUS factor",
        "MINUS factor",
        "power",
    )
    def factor(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Factor rule."""
        return p

    @_(
        "connect",
        "connect POW power",
    )
    def power(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Power rule."""
        return p

    @_(
        "spawn_object disconnect_op connect",
        "spawn_object connect_op connect",
        "spawn_object",
    )
    def connect(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Connect rule."""
        return p

    @_(
        "spawn_op atom",
        "unpack",
    )
    def spawn_object(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Spawn object rule."""
        return p

    @_(
        "STAR_MUL STAR_MUL atom",
        "STAR_MUL atom",
        "ref",
    )
    def unpack(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Unpack rule."""
        return p

    @_(
        "KW_REF atom",
        "atom",
    )
    def ref(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Unpack rule."""
        return p

    @_(
        "WALRUS_EQ",
        "ADD_EQ",
        "SUB_EQ",
        "MUL_EQ",
        "DIV_EQ",
        "MOD_EQ",
    )
    def walrus_op(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Production Assignment rule."""
        return p

    @_(
        "EE",
        "LT",
        "GT",
        "LTE",
        "GTE",
        "NE",
        "KW_IN",
        "KW_NIN",
    )
    def cmp_op(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Compare operator rule."""
        return p

    @_(
        "KW_SPAWN",
        "SPAWN_OP",
    )
    def spawn_op(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Spawn operator rule."""
        return p

    # Atom rules
    # --------------------
    @_(
        "atom_literal",
        "atom_collection",
        "LPAREN expression RPAREN",
        "global_ref",
        "atomic_chain",
        "arch_ref",
        "edge_op_ref",
        "KW_HERE",
        "KW_VISITOR",
    )
    def atom(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Atom rule."""
        return p

    @_(
        "INT",
        "FLOAT",
        "multistring",
        "BOOL",
        "NULL",
        "NAME",
        "builtin_type",
    )
    def atom_literal(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Atom rule."""
        return p

    @_(
        "list_val",
        "dict_val",
        # sets and tuples are supported through the pipe forward semantic
        "comprehension",
    )
    def atom_collection(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Atom rule."""
        return p

    @_(
        "STRING",
        "FSTRING",
        "STRING multistring",
        "FSTRING multistring",
    )
    def multistring(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Multistring rule."""
        return p

    @_(
        "LSQUARE RSQUARE",
        "LSQUARE expr_list RSQUARE",
    )
    def list_val(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """List value rule."""
        return p

    @_(
        "expression",
        "expr_list COMMA expression",
    )
    def expr_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Expression list rule."""
        return p

    @_(
        "LBRACE RBRACE",
        "LBRACE kv_pairs RBRACE",
    )
    def dict_val(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Production for dictionary value rule."""
        return p

    @_(
        "LSQUARE expression KW_FOR NAME KW_IN walrus_assign RSQUARE",
        "LBRACE expression COLON expression KW_FOR NAME KW_IN walrus_assign RBRACE",
        "LSQUARE expression KW_FOR NAME KW_IN walrus_assign KW_IF expression RSQUARE",
        "LBRACE expression COLON expression KW_FOR NAME KW_IN walrus_assign KW_IF expression RBRACE",
    )
    def comprehension(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Comprehension rule."""
        return p

    @_(
        "expression COLON expression",
        "kv_pairs COMMA expression COLON expression",
    )
    def kv_pairs(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Key/value pairs rule."""
        return p

    @_(
        "atomic_chain_safe",
        "atomic_chain_unsafe",
        "atomic_call",
    )
    def atomic_chain(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Atom trailer rule."""
        return p

    @_(
        "atom DOT NAME",
        "atom index_slice",
        "atom arch_ref",
    )
    def atomic_chain_unsafe(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Atom trailer rule."""
        return p

    @_(
        "atom NULL_OK DOT NAME",
        "atom NULL_OK index_slice",
        "atom NULL_OK arch_ref",
    )
    def atomic_chain_safe(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Atom trailer rule."""
        return p

    @_(
        "atom func_call_tail",
        "atom ds_call",
    )
    def atomic_call(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Ability call rule."""
        return p

    @_("DBL_COLON NAME")  # ::name for abilitie
    def ds_call(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Ability operator rule."""
        return p

    @_(
        "LPAREN RPAREN",
        "LPAREN param_list RPAREN",
    )
    def func_call_tail(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Rule for function calls."""
        return p

    @_(
        "expr_list",
        "assignment_list",
        "expr_list COMMA assignment_list",
    )
    def param_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Parameter list rule."""
        return p

    @_(
        "assignment",
        "assignment_list COMMA assignment",
    )
    def assignment_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Keyword expression list rule."""
        return p

    @_(
        "LSQUARE expression RSQUARE",
        "LSQUARE expression COLON expression RSQUARE",
    )
    def index_slice(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Index/slice rule."""
        return p

    @_("GLOBAL_OP NAME")
    def global_ref(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Global reference rule."""
        return p

    # Architype reference rules
    # -------------------------
    @_(
        "node_ref",
        "edge_ref",
        "walker_ref",
        "object_ref",
        "ability_ref",
    )
    def arch_ref(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Architype reference rule."""
        return p

    @_(
        "node_ref",
        "edge_ref",
        "walker_ref",
        "object_ref",
    )
    def strict_arch_ref(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Strict Architype reference rule."""
        return p

    @_("NODE_OP NAME")
    def node_ref(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Node reference rule."""
        return p

    @_("EDGE_OP NAME")
    def edge_ref(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Edge reference rule."""
        return p

    @_("WALKER_OP NAME")
    def walker_ref(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Walker reference rule."""
        return p

    @_("OBJECT_OP NAME")
    def object_ref(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Object type reference rule."""
        return p

    @_("ABILITY_OP NAME")
    def ability_ref(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Ability reference rule."""
        return p

    # Node / Edge reference and connection rules
    # ------------------------------------------
    @_(
        "edge_to",
        "edge_from",
        "edge_any",
    )
    def edge_op_ref(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Edge reference rule."""
        return p

    @_(
        "ARROW_R",
        "ARROW_R_p1 expression ARROW_R_p2",
    )
    def edge_to(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Edge to rule."""
        return p

    @_(
        "ARROW_L",
        "ARROW_L_p1 expression ARROW_L_p2",
    )
    def edge_from(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Edge from rule."""
        return p

    @_(
        "ARROW_BI",
        "ARROW_L_p1 expression ARROW_R_p2",
    )
    def edge_any(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Edge any rule."""
        return p

    @_(
        "connect_to",
        "connect_from",
        "connect_any",
    )
    def connect_op(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Connect operator rule."""
        return p

    @_("NOT edge_op_ref")
    def disconnect_op(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Connect operator not rule."""
        return p

    @_(
        "CARROW_R",
        "CARROW_R_p1 expression CARROW_R_p2",
    )
    def connect_to(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Connect to rule."""
        return p

    @_(
        "CARROW_L",
        "CARROW_L_p1 expression CARROW_L_p2",
    )
    def connect_from(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Connect from rule."""
        return p

    @_(
        "CARROW_BI",
        "CARROW_L_p1 expression CARROW_R_p2",
    )
    def connect_any(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Connect any rule."""
        return p

    @_(
        "LPAREN EQ filter_compare_list RPAREN",
    )
    def filter_ctx(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Filter context rule."""
        return p

    @_("LBRACE param_list RBRACE")
    def spawn_ctx(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Spawn context rule."""
        return p

    @_(
        "NAME cmp_op expression",
        "filter_compare_list COMMA NAME cmp_op expression",
    )
    def filter_compare_list(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Filter comparison list rule."""
        return p

    @_("")
    def empty(self: "JacParser", p: YaccProduction) -> YaccProduction:
        """Empty rule."""
        return p
