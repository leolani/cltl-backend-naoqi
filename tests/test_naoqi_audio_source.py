import time
import unittest
from Queue import Queue
from threading import Thread, Event

import numpy as np

from cltl.naoqi.audio_source import NAOqiAudioSource, reframe


class DummySession:
    def service(self, name):
        return DummyService()

    def registerService(self, name, cls):
        pass


class DummyService:
    def setClientPreferences(self, cls, rate, index, _):
        pass

    def subscribe(self, naem):
        pass


class NAOqiAudioSourceTest(unittest.TestCase):
    def test_reframe_equal_size_chunks(self):
        decades = np.split(np.array(list(range(100))), 10)
        self.assertTrue(all(frame.shape == (10,) for frame in decades))

        queue = Queue()
        [queue.put(interval) for interval in decades]

        frame_stream = reframe(queue, 10, 1)
        frames = [next(frame_stream)  for _ in range(10)]

        self.assertEqual(10, len(frames))
        self.assertTrue(all(frame.shape == (10,) for frame in frames))
        self.assertEqual(list(range(100)), [el for frame in frames for el in frame])

        frame_stream.close()

    def test_reframe_larger_chunks(self):
        decades = np.split(np.array(list(range(100))), 10)
        self.assertTrue(all(frame.shape == (10,) for frame in decades))

        queue = Queue()
        [queue.put(interval) for interval in decades]

        frame_stream = reframe(queue, 3, 1)
        frames = [next(frame_stream)  for _ in range(33)]

        self.assertEqual(33, len(frames))
        self.assertTrue(all(frame.shape == (3,) for frame in frames))
        self.assertEqual(list(range(99)), [el for frame in frames for el in frame])

        frame_stream.close()

    def test_reframe_smaller_chunks(self):
        decades = np.split(np.array(list(range(100))), 10)
        self.assertTrue(all(frame.shape == (10,) for frame in decades))

        queue = Queue()
        [queue.put(interval) for interval in decades]

        frame_stream = reframe(queue, 33, 1)
        frames = [next(frame_stream)  for _ in range(3)]

        self.assertEqual(3, len(frames))
        self.assertTrue(all(frame.shape == (33,) for frame in frames))
        self.assertEqual(list(range(99)), [el for frame in frames for el in frame])

        frame_stream.close()

    def test_source(self):
        source = NAOqiAudioSource(DummySession(), 1, 1, 10, 1)
        source.start()

        done = Event()

        def feed_mic():
            while not done.is_set():
                source.processRemote(1, 1, 1, np.ones((50,), dtype=np.int16).tobytes())
                time.sleep(0.01)

        feed_thread = Thread(target = feed_mic)
        feed_thread.start()

        with source as mic:
            audio = [next(mic) for i in range(10)]
            self.assertTrue(all(frame.shape == (10,) for frame in audio))

        done.set()
        feed_thread.join()


if __name__ == '__main__':
    unittest.main()