import json
import random


class Sample:
    """`self.__dict__` stores the object’s attributes as a dictionary.
    """
    def __init__(self, sample, author=None):
        self.sample = sample
        self.author = author

    def json(self):
        return self.__dict__


class SampleFile:
    """
    samples = ["xyz"]
    with SampleFile(SAMPLE_PATH) as sample_writer:
        sample_writer.truncate()
        samples_objects = [Sample(text, None) for text in samples]
        for sample in samples_objects:
            sample_writer.append(sample)
    """
    FLUSH_LIMIT = 5

    def __init__(self, file):
        self.file = open(file, "r+")

        try:
            self.samples = json.load(self.file)
        except json.decoder.JSONDecodeError:
            self.samples = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def truncate(self):
        self.samples.clear()

    def read(self, size=-1):
        return self.samples if size < 0 else self.samples[:size]

    def write(self, sample: Sample):
        self.samples.clear()
        self.append(sample)

    def append(self, sample: Sample):
        self.samples.append(sample.json())
        if len(self.samples) % SampleFile.FLUSH_LIMIT == 0:
            self.flush()

    def close(self):
        """Flush and close the IO object.
        This method has no effect if the file is already closed.
        """
        if not self.file.closed:
            self.flush()
            self.file.close()

    def flush(self):
        self.file.seek(0)
        self.file.truncate()
        json.dump(self.samples, self.file)


def get_random_sample(sample_path):
    with SampleFile(sample_path) as f:
        sample = random.choice(f.read())
        return sample
