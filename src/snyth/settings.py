# Copyright 2021 Luke Zulauf
# All rights reserved.
from functools import lru_cache

class Settings:
    
    def __init__(self, sample_rate=88_200):
        """
        sample_rate = waveform samples per second
        """
        self.sample_rate = sample_rate
        
    @staticmethod
    @lru_cache()
    def instance():
        return Settings()
    
    def __repr__(self):
        return f'{self.__class__.__name__}(sample_rate={self.sample_rate})'
