from __future__ import division
from .base import Stim, CollectionStimMixin
from .audio import AudioStim
from .image import ImageStim
from moviepy.video.io.VideoFileClip import VideoFileClip
import pandas as pd


class VideoFrameStim(ImageStim):

    ''' A single frame of video. '''

    def __init__(self, video, frame_num, duration=None, filename=None, data=None):
        self.video = video
        self.frame_num = frame_num
        spf = 1. / video.fps
        duration = spf if duration is None else duration
        onset = frame_num * spf
        super(VideoFrameStim, self).__init__(filename, onset, duration, data)
        if data is None:
            self.data = self.video.get_frame(index=frame_num).data
        if video.filename:
            self.name = video.name + '->'
        self.name += 'frame[%s]' % frame_num


class VideoStim(Stim, CollectionStimMixin):

    ''' A video. '''

    def __init__(self, filename, onset=None):

        self.filename = filename
        self._load_clip()
        self.fps = self.clip.fps
        self.width = self.clip.w
        self.height = self.clip.h
        self.n_frames = int(self.fps * self.clip.duration)
        duration = self.clip.duration

        super(VideoStim, self).__init__(filename, onset, duration)

    def _load_clip(self):
        self.clip = VideoFileClip(self.filename)

    def __iter__(self):
        """ Frame iteration. """
        for i, f in enumerate(self.clip.iter_frames()):
            yield VideoFrameStim(self, i, data=f)

    def __getstate__(self):
        d = self.__dict__.copy()
        d['clip'] = None
        return d

    def __setstate__(self, d):
        self.__dict__ = d
        self._load_clip()

    @property
    def frames(self):
        return [f for f in self.clip.iter_frames()]

    def get_frame(self, index=None, onset=None):
        if index is not None:
            onset = float(index) / self.fps
        else:
            index = int(onset * self.fps)
        return VideoFrameStim(self, index, data=self.clip.get_frame(onset))


class DerivedVideoStim(VideoStim):
    """
    VideoStim containing keyframes (for API calls). Each keyframe is associated
    with a duration reflecting the length of its "scene."
    """
    def __init__(self, filename, elements, frame_index=None):
        super(DerivedVideoStim, self).__init__(filename)
        self.elements = elements
        self.frame_index = frame_index
        self.name += '_derived'
        
    def __iter__(self):
        for elem in self.elements:
            yield elem