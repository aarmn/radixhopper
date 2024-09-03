from typing import Optional
from fractions import Fraction
from math import gcd
from pydantic import BaseModel, Field, validator
from enum import Enum

class ConversionError(Exception):
    pass

class InputError(ConversionError):
    pass

class BaseRangeError(ConversionError):
    pass

class DigitError(ConversionError):
    pass

class BaseRange(Enum):
    MIN = 2
    MAX = 36

class ConversionInput(BaseModel):
    num: str = Field(..., description="Number to convert")
    base_from: int = Field(..., ge=BaseRange.MIN.value, le=BaseRange.MAX.value, description="Base to convert from")
    base_to: int = Field(..., ge=BaseRange.MIN.value, le=BaseRange.MAX.value, description="Base to convert to")
    digits: str = Field(default="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", description="Digit set")

    @validator('num')
    def validate_num(cls, v, values):
        if 'base_from' in values and 'digits' in values:
            base_from = values['base_from']
            digits = values['digits']
            if not all(d in digits[:base_from] for d in v.upper() if d not in ".[]-"):
                raise DigitError(f"Invalid digit(s) for base {base_from}")
        return v.upper()

class BaseConverter:
    @staticmethod
    def _int_out(fraction: Fraction) -> tuple[int, Fraction]:
        i, frac = divmod(fraction.numerator, fraction.denominator)
        return i, Fraction(frac, fraction.denominator)

    @staticmethod
    def _any_to_frac(i: str, fp: str, fp_rep: str, from_base: int, digits: str) -> Fraction:
        fraction = Fraction()

        for index, digit in enumerate(i):
            fraction += digits.index(digit) * (from_base ** (len(i) - index - 1))
        fraction += (Fraction(BaseConverter._any_to_frac(fp, "", "", from_base, digits), from_base ** (len(fp)))) if fp else 0
        fraction += (Fraction(BaseConverter._any_to_frac(fp_rep, "", "", from_base, digits), ((from_base ** len(fp_rep)) - 1) * (from_base ** len(fp)))) if fp_rep else 0
        return fraction

    @staticmethod
    def _frac_to_any(x: Fraction, to_base: int, intpart: bool, digits: str) -> str:
        buffer_rep, out_x = "", ""
        while x > 0:
            if not intpart:
                if gcd(x.denominator, to_base) == 1:
                    if buffer_rep == "":
                        buffer_rep = x
                        out_x += "["
                    elif buffer_rep == x:
                        out_x += "]"
                        break
            x, digit = divmod(x, to_base) if intpart else BaseConverter._int_out(x * to_base)[::-1]
            out_x += digits[digit]
        return out_x[::-1] if intpart else out_x

    @staticmethod
    def base_convert(input_data: ConversionInput) -> str:
        int_str, fp_str, fp_rep_str = "", "", ""
        num = input_data.num
        if "." in num:
            i_str, fp_str = num.split(".")
            if ("[" in fp_str) or ("]" in fp_str):
                try:
                    fp_rep_str = fp_str[fp_str.index("[") + 1:fp_str.index("]")]
                    fp_str = fp_str[:fp_str.index("[")]
                except:
                    raise InputError("Invalid input format for repeating decimal")
        else:
            i_str = num

        i_int, f_frac = BaseConverter._int_out(BaseConverter._any_to_frac(i_str, fp_str, fp_rep_str, input_data.base_from, input_data.digits))
        return (BaseConverter._frac_to_any(i_int, input_data.base_to, True, input_data.digits) + 
                "." + BaseConverter._frac_to_any(f_frac, input_data.base_to, False, input_data.digits))
    

# handle zero