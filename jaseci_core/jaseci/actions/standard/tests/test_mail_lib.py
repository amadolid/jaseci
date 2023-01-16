from jaseci.utils.test_core import CoreTest


class MailLibTest(CoreTest):
    """Unit tests for Jac Walker APIs"""

    fixture_src = __file__

    def setUp(self):
        super().setUp(True)

    def test_send_mail(self):
        self.call(
            self.mast,
            ["sentinel_register", {"code": self.load_jac("mail_test.jac")}],
        )
        ret = self.call(self.mast, ["walker_run", {"name": "send_mail"}])
        self.assertTrue(ret["success"])
        self.assertTrue(self.mast._h.mail.connect.called)
        self.assertEqual(
            self.mast._h.mail.app.method_calls[0].args,
            (None, ["jaseci.dev@gmail.com"], "Test Subject", ("Test", "<h1>Test</h1>")),
        )
