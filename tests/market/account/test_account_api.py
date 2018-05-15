from tests.market.base_api_test import *


class TestAccountApi(BaseApiTest):

    def test_login_and_confirm(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        self.assertIsNotNone(token,"token should not be empty")
