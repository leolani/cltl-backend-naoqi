class AudioSource:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        return iter(self.audio)

    @property
    def audio(self):
        raise NotImplementedError()

    @property
    def rate(self):
        raise NotImplementedError()

    @property
    def channels(self):
        raise NotImplementedError()

    @property
    def frame_size(self):
        raise NotImplementedError()

    @property
    def depth(self):
        raise NotImplementedError()