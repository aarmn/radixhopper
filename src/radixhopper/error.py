from enum import Enum

class RadixError(Exception):
    """Base exception for all RadixNumber errors"""
    pass

class BaseRangeError(RadixError):
    """Error for base out of allowed range"""
    pass

class DigitError(RadixError):
    """Error for invalid digit for given base"""
    pass

class ParseError(RadixError):
    """Error for invalid number format"""
    pass

class BaseRange(Enum):
    MIN = 2
    MAX = 36
