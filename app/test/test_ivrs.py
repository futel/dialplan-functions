from unittest import mock, TestCase

from chalicelib import ivrs


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

    def test_menu(self):
        response = mock.Mock()
        self.assertEqual(
            ivrs.menu(
                response,
                {'name':'name'},
                'lang',
                'parent_c_name',
                'env',
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


if __name__ == '__main__':
    unittest.main()
