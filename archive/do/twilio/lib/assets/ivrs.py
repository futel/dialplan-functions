ivrs = {
    "outgoing_portland": {
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
        "statement_dir": "outgoing"},
    "outgoing_ypsi":  {
        "name": "outgoing_ypsi",
        "pre_callable": "friction",
        "intro_statements": ["para-espanol", "oprima-estrella"],
        "menu_entries": [
            ["to-make-a-call", "outgoing-dialtone-wrapper"],
            ["for-voicemail", "voicemail_outgoing"],
            ["for-the-directory", "directory_ypsi"],
            ["for-utilities", "utilities_generic"],
            ["for-the-fewtel-community", "community_outgoing"],
            ["for-community-services", "community_services_michigan"],
            ["for-the-telecommunications-network", "network"],
            None,
            [None, "call_911_9"]],
        "other_menu_entries": [
            ["for-the-operator", 0, "operator"]],
        "statement_dir": "outgoing"},
    "outgoing_detroit":  {
        "name": "outgoing_detroit",
        "pre_callable": "friction",
        "intro_statements": ["para-espanol", "oprima-estrella"],
        "menu_entries": [
            ["to-make-a-call", "outgoing-dialtone-wrapper"],
            ["for-voicemail", "voicemail_outgoing"],
            ["for-the-directory", "directory_detroit"],
            ["for-utilities", "utilities_generic"],
            ["for-the-fewtel-community", "community_outgoing"],
            ["for-community-services""community_services_michigan"],
            ["for-the-telecommunications-network", "network"],
            None,
            [None, "call_911_9"],
            ["for-the-operator", "operator"]],
        "other_menu_entries": [
            ["for-the-operator", 0, "operator"]],
        "statement_dir": "outgoing"},
    "outgoing_souwester": {
        "name": "outgoing_souwester",
        "pre_callable": "friction",
        "intro_statements": ["para-espanol", "oprima-estrella"],
        "menu_entries": [
            ["to-make-a-call", "outgoing-dialtone-wrapper"],
            ["for-voicemail", "voicemail_outgoing"],
            ["for-the-directory", "directory_souwester"],
            ["for-utilities", "utilities_generic"],
            ["for-the-fewtel-community", "community_outgoing"],
            ["for-the-telecommunications-network", "network"],
            None,
            None,
            [None, "call_911_9"]],
        "other_menu_entries": [
            ["for-the-operator", 0, "operator"]],
        "statement_dir": "outgoing"},
    "outgoing_safe": {
        "name": "outgoing_safe",
        "pre_callable": "friction",
        "intro_statements": ["para-espanol", "oprima-estrella"],
        "menu_entries": [
            ["to-make-a-call", "outgoing-dialtone-wrapper"],
            ["for-voicemail", "voicemail_outgoing"],
            ["for-the-directory", "directory_safe"],
            ["for-utilities", "utilities_portland"],
            ["for-the-fewtel-community", "community_outgoing"],
            ["for-the-telecommunications-network", "network"],
            None,
            None,
            None],
        "other_menu_entries": [
            ["for-the-operator", 0, "operator"]],
        "statement_dir": "outgoing"}
}
