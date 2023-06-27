"""Test pass module."""
from jaclang.jac.passes.decl_def_match_pass import DeclDefMatchPass
from jaclang.jac.transpiler import jac_file_to_pass
from jaclang.utils.test import TestCase


class BluePygenPassTests(TestCase):
    """Test pass module."""

    def setUp(self) -> None:
        """Set up test."""
        return super().setUp()

    def test_pygen_jac_cli(self) -> None:
        """Basic test for pass."""
        state = jac_file_to_pass(
            "../../../../cli/jac_cli.jac", self.fixture_abs_path(""), DeclDefMatchPass
        )
        print(state.sym_tab)
        self.assertFalse(state.errors_had)
