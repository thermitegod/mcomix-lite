class FileProviderBase:
    def __init__(self):
        super().__init__()

        self.files = []

    def list_files(self, mode: int):
        raise NotImplementedError
