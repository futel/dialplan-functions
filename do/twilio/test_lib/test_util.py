class MockDict(dict):
    def __getitem__(self, k):
        return k
