from unittest import mock, TestCase

from chalicelib import ivrs

c_dict = {
    "name": "outgoing_portland",
    "pre_callable": "friction",
    "intro_statements": ["para-espanol", "oprima-estrella"],
    "menu_entries": [
        ["to-make-a-call", "outgoing-dialtone-wrapper"],
        ["for-voicemail", "voicemail_outgoing"],
        ["for-the-directory", "directory_portland"],
        ["for-utilities", "utilities_portland"],
        ["for-the-fewtel-community", "community_outgoing"],
        ["for-community-services", "community_services_oregon"],
    ["for-the-telecommunications-network", "network"],
        None,
        [None, "call_911_9"]],
    "other_menu_entries": [
        ["for-the-operator", 0, "operator"]],
    "statement_dir": "outgoing"}

request = mock.Mock(
    headers={'host': 'host'},
    post_fields={})


class TestIvrs(TestCase):

    def test_pre_callable_missing(self):
        self.assertEqual(
            ivrs.pre_callable('response', {}, 'dummy'),
            'response')

    def test_pre_callable_friction(self):
        self.assertEqual(
            ivrs.pre_callable(
                'response',
                {"name": "dummy", "pre_callable": "friction"},
                'dummy'),
            'response')

    def test_context_dict(self):
        self.assertIsInstance(
            ivrs.context_dict(
                {'outgoing_portland':{}},
                'outgoing_portland'),
            dict)

    # def test_destination_context_dict_not_local(self):
    #     """Selecting a context not in the ivrs returns None."""
    #     self.assertIs(
    #         ivrs.destination_context_dict(
    #             'outgoing_portland', '1', 'parent'),
    #         None)

    # def test_destination_context_dict_lang(self):
    #     self.assertIs(
    #         ivrs.destination_context_dict(
    #             'outgoing_portland', '*', 'parent'),
    #         ivrs.LANG_DESTINATION)

    # def test_destination_context_dict_lang(self):
    #     self.assertIs(
    #         ivrs.destination_context_dict(
    #             'outgoing_portland', '#', 'parent'),
    #         ivrs.PARENT_DESTINATION)

    # def test_destination_context_dict_invalid(self):
    #     self.assertEqual(
    #         ivrs.destination_context_dict(
    #             'outgoing_portland', '8', 'parent')['name'],
    #         'outgoing_portland')

    def test_destination_context_name(self):
        self.assertEqual(
            ivrs.destination_context_name('0', c_dict),
            'operator')
        self.assertEqual(
            ivrs.destination_context_name('1', c_dict),
            'outgoing-dialtone-wrapper')
        self.assertEqual(
            ivrs.destination_context_name('4', c_dict),
            'utilities_portland')
        self.assertEqual(
            ivrs.destination_context_name('8', c_dict),
            'outgoing_portland')
        self.assertEqual(
            ivrs.destination_context_name('9', c_dict),
            'call_911_9')
        self.assertEqual(
            ivrs.destination_context_name('#', c_dict),
            ivrs.PARENT_DESTINATION)

    def test_add_intro_stanza(self):
        response = mock.Mock()
        self.assertEqual(
            ivrs.add_intro_stanza(
                response,
                {'name':'name'},
                'lang',
                'parent_c_name',
                1,
                request,
                {}),
            response)

    def test_add_menu_stanza(self):
        response = mock.Mock()
        self.assertEqual(
            ivrs.add_menu_stanza(
                response,
                {'name':'name'},
                'lang',
                'parent_c_name',
                1,
                request,
                {}),
            response)

    def test_sound_url(self):
        self.assertEqual(
            ivrs.sound_url(
                'hello',
                'en',
                'directory',
                'request',
                {'ASSET_HOST':'ASSET_HOST'}),
            'https://ASSET_HOST/en/directory/hello.ulaw')


    def test_ivr_context(self):
        response = mock.Mock()
        self.assertTrue(
            ivrs.ivr_context(
                c_dict,
                'en',
                'c_name',
                ivrs.INTRO_STANZA,
                1,
                request,
                {'ASSET_HOST':'ASSET_HOST'}))


if __name__ == '__main__':
    unittest.main()
