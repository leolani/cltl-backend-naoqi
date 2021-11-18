class TextOutput:
    def consume(self, text, language=None):
        raise NotImplementedError()

    def consume_stream(self, texts, language=None):
        for text in texts:
            self.consume(text)


class TextSource:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        return iter(self.text)

    @property
    def text(self):
        raise NotImplementedError()

    @property
    def language(self):
        return None
