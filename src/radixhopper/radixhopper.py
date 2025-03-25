import re
from enum import Enum
from fractions import Fraction
from math import gcd
from typing import Optional, Tuple, Union
from decimal import Decimal
from copy import deepcopy
from tooling import deprecated # better import?

from error import *

from typeguard import typechecked
from pydantic import BaseModel, Field, validator # get rid of this as well, very useless in grand scheme of things

#‌ TODO: handle none singular digit with list, maximal munch, and ambiguity check (should use a wrapper around the actual thing, instead of directly working with strings as digits)

# TODO: handle zero
# TODO: lets add decimal tho?
# check _ in number and ignore

# Handle empty input
# check for scientific notation char overlap base don case sensitivity
# always always always, ignore _ and use . as decimal point
# cant use x and b in the bases with implicit load

@deprecated("Use RadixNumber class instead")
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
            if not all(d in digits[:base_from] for d in v if d not in ".[]-"):
                raise DigitError(f"Invalid digit(s) for base {base_from}")
        return v #.upper()

# TODO: keep these for same base merging, @ and [] 
# TODO: same base operation keep in base (if same digit and base)

class RadixNumber:
    _DEFAULT_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    SPECIAL_CHARS = "._[] "

    # internals
    # frac:                          fractional value
    # case_sensitive:                case_sensitive
    # digits:                        string of digits used for representation and conversion of string
    # representation_base:           int or "fraction"
    # getter | representation_value: a getter with buffer, of the string representation of the number in the base, for performance sake
    # _representation_cache_hash:    
    # _representation_cache_value:   

    # str - sci notation : (like normal str, it can have any base, defaults to 10)
    # str - box : (if in form, use its base)
    # str - defaults to 10, 
    # fraction : "fraction"
    # float : 10 with scientific notation flag
    # decimal : 10 with scientific notation flag
    # int : 10
    # Radixhopper : inherit from other Radixhopper

    @staticmethod
    def scientific_str_to_decimal_str(sci_str: str, scientific_notation_char: str = "eE", case_sensitive: bool = False, digits:str="0123456789", base:int=10): 
        """
        Convert a scientific notation string to a fully written out decimal string.
        Works with string operations only, without converting the mantissa to float (should convert exponent to int tho).
        
        Args:
            sci_str (str): Scientific notation string (e.g., '1.23e+5', '4.56E-3')
            scientific_notation_char (str, optional): Characters used for scientific notation. Defaults to "eE".
            case_sensitive (bool, optional): Whether to treat the input number and scientific notation chars in different radices or digit set as case-sensitive. Defaults to True.
            

        Returns:
            str: Fully written out decimal string or original string if invalid format
        """
        if any((char in digits) and (digits.index(char) <= base) for char in scientific_notation_char):
            raise ValueError("Scientific notation char should not overlap with digits, specifically when the overlapping chars are in the range of used digits of the base")

        sci_str = sci_str.strip()

        if not sci_str:
            raise ValueError("Empty input string")
        
        if sci_str.startswith('_'):
            raise ValueError("Invalid scientific notation format")
        
        sci_str = sci_str.replace('_', '')

        if not case_sensitive:
            sci_str = sci_str.lower()
            scientific_notation_char = scientific_notation_char.lower()
        
        # Check if it's already in decimal form (no 'e' or 'E', although, scientific notatatoin char is overridable)
        if set(scientific_notation_char).isdisjoint(sci_str) :
            return sci_str

        spliter = lambda x: re.split(f'[{"".join(re.escape(d) for d in set(scientific_notation_char))}]+', sci_str) # NOQA
        
        # Split into mantissa and exponent
        parts = spliter(sci_str)
        if len(parts) != 2:
            raise ValueError("Invalid scientific notation format")
        
        mantissa = parts[0].strip()
        exponent = parts[1].strip()
        
        # Check if mantissa or exponent is empty
        if not mantissa or not exponent:
            raise ValueError("Invalid scientific notation format")

        def sign_extractor(x):
            if x.startswith('+'):
                return x[1:], False
            if x.startswith('-'):
                return x[1:], True
            return x, False

        # Validate exponent as a number, as we need its value later on for shifts
        exponent, negative_exponent = sign_extractor(exponent)
        exponent = int(RadixNumber.base_convert(ConversionInput(num=exponent, base_from=base, base_to=10, digits=digits))[:-1]) # needs refactor after delete of base_convert
        exponent = -exponent if negative_exponent else exponent
        
        mantissa, negative_mantissa = sign_extractor(mantissa)
        
        # Check for multiple decimal points
        if mantissa.count('.') > 1:
            raise ValueError("Invalid mantissa format")
        
        # Handle decimal point in mantissa
        if '.' in mantissa:
            dot_pos = mantissa.find('.')
            digit_only = mantissa.replace('.', '')
        else:
            dot_pos = len(mantissa)
            digit_only = mantissa
        
        # Handle empty digits
        if not digit_only:
            raise ValueError("Invalid mantissa format")
        
        # Calculate new decimal point position
        new_pos = dot_pos + exponent
        
        # Generate result based on decimal point position
        if new_pos <= 0:
            result = '0.' + '0' * (-new_pos) + digit_only
        elif new_pos >= len(digit_only):
            result = digit_only + '0' * (new_pos - len(digit_only))
        else:
            result = digit_only[:new_pos] + '.' + digit_only[new_pos:]
        
        # Add negative sign if needed
        if negative_mantissa:
            result = '-' + result
        
        # Clean up trailing zeros and decimal point
        if '.' in result:
            result = result.rstrip('0').rstrip('.')
        
        return result

    def to(self, *, base=None, digits=None): # base, digits
        self.representation_base = base if base else self.representation_base
        self.digits = digits if digits else self.digits
        self.representation_value
        return self

    # latex repr, using atomizer of output or frac
    # [2] for getting base
    # Improve errors
    # add unit test
    # improve pydocs
    # improve comments
    # operations

    @staticmethod
    def _check_representation_base(base: int, digits: str, representation_base: Optional[int], case_sensitive: bool):
        if (representation_base is None):
            return base
        elif isinstance(representation_base, int):
            if len(digits) < representation_base:
                raise ValueError("Representation base should be less than or equal to the number of digits")
            return representation_base
        elif representation_base == "fraction":
            return representation_base
        else:
            raise ValueError("representation_base should be int or 'fraction'")

    # def _check_base(self, base: int):

    def _check_and_normalize_digits(self, *, digits: str, case_sensitive: bool, base: int):
        if not case_sensitive:
            digits = digits.upper()
        
        if len(set(digits)) != len(digits):
            raise ValueError("Digits should be unique") 

        if not set(digits).isdisjoint(self.SPECIAL_CHARS):
            raise ValueError("Digits should not overlap with special characters of ., _, [, or ]")
    
        if len(digits) < base:
            raise ValueError("Digits should be at least as long as the base")
    
        return digits

    def _check_and_normalize_scientific_notation_char(self, *, scientific_notation_char: str, digits: str, case_sensitive: bool, base: int):
        # normal digit?
        # 1. Convert scientific notation chars to uppercase if case insensitive
        if not case_sensitive:
            scientific_notation_char = scientific_notation_char.upper()
        
        # 2. Ensure that scientific notation chars are unique (no repeating characters)
        scientific_notation_char = str("".join(set(scientific_notation_char)))

        # 3. Check that scientific notation chars do not overlap with digits in the active range
        if any(((char in digits) or (char in scientific_notation_char)) and (digits.index(char) <= base) for char in scientific_notation_char):
            raise ValueError("Scientific notation char should not overlap with digits, specifically when the overlapping chars are in the range of used digits of the base")
        
        return scientific_notation_char


    def _check_value_type(self, value: str, digits: str, base: Optional[int], case_sensitive: bool, ):
        # 1. Check if the value is of a valid type
        # if not isinstance(value, (str, int, float, Decimal, Fraction, RadixNumber)):
        #     raise TypeError("value should be str, int, float, Decimal, Fraction or RadixNumber")

        # # 2. If the value is already a RadixNumber, return its attributes
        # if isinstance(value, RadixNumber):
        #     return value, None, None
        
        # 4. Handle Fraction
        if isinstance(value, Fraction):
            self.representation_base = "fraction" # handle out
            return None, value, None  # Return None for full and the Fraction object

        # 3. Handle specific types and normalize the value
        # if isinstance(value, (float, Decimal)):
        #     self.is_scientific_notation_str = True # this is not a stroed value, gotta return # Mark as scientific notation if float or Decimal

        # reaching here, its either int, float, decimal, which will become str, or, its an str from the start
        # maybe a faster way to handle int, float, decimal is direct conversion to fraction, but not for now


        

        return None, None, value
    
    @staticmethod
    def normalized_str_to_str_particles_and_check(value_string):
        i_str, fp_str, fp_rep_str = "", "", ""

        if "." in value_string:
            i_str, fp_str = value_string.split(".")
            if ("[" in fp_str) or ("]" in fp_str):
                if fp_rep_str.count("[") != 1 or fp_rep_str.count("]") != 1:
                    raise ValueError("Invalid input format for repeating decimal")
                if fp_rep_str.index("[") > fp_rep_str.index("]"):
                    raise ValueError("Invalid input format for repeating decimal")
                try:
                    fp_rep_str = fp_str[fp_str.index("[") + 1:fp_str.index("]")]
                    fp_str = fp_str[:fp_str.index("[")]
                except ValueError:
                    raise ValueError("Invalid input format for repeating decimal")
        else:
            i_str = value_string
        
        return i_str, fp_str, fp_rep_str

    @property
    def representation_value(self):
        """
        Get the string representation of self.frac in the current representation_base.
        Uses a cached value if the hash (computed from self.frac, self.digits, self.case_sensitive, and self.representation_base)
        has not changed; otherwise, recalculates the representation using the internal conversion function.
        """
        current_hash = hash((self.frac, self.digits, self.case_sensitive, self.representation_base))
        if hasattr(self, '_representation_cache_hash') and self._representation_cache_hash == current_hash:
            return self._representation_cache_value

        if self.representation_base == "fraction":
            value = str(self.frac)
        else:
            value = self._my_frac_to_any_base_str(self.digits, self.representation_base) #TODO: check is this the right shit
        
        self._representation_cache_hash = current_hash
        self._representation_cache_value = value
        return value

    @typechecked
    def __init__(self, 
                 value: Union[str, int, float, Decimal, Fraction ,'RadixNumber'],
                 base: int = 10, # (#TODO: none for default behaviour, number for strict) base is used for understanding str inputs, ignored if zero_b_o_x_leading_implicit_based or scientific notation
                 digits: str = _DEFAULT_DIGITS, # TODO: List or Tuple as well, also weird multi char should be handled here if wanna be handled
                 is_scientific_notation_str = False, 
                 direct_conversion_of_float_decimal_to_frac = False,
                 zero_b_o_x_leading_implicit_based = False, # if true, if str has a format of 0b 0x 0o it would be converted to the respective base
                 scientific_notation_char = "eE", # used for scientific notation conversion 
                 case_sensitive = False, # if true, the digits and scientific notation char are case sensitive
                 representation_base = None # None for default (using 10 for int, float, decimal, using `base` or b_o_x for str, using `"fraction"` for Fraction), int for base, "fraction" for fraction, this is used for showing output and cross operation propegation
                 ):
        """
        Initialize a RadixNumber from various input types with flexible base conversion options.

        This constructor accepts a value that can be a string, integer, float, Decimal, Fraction, or another
        RadixNumber. It converts the input into an internal Fraction representation, handling different numeric
        formats such as standard, scientific, and many more. The provided base, digit set, and notation
        options customize both parsing and output. The key feature is the ability to handle repeating decimals in
        inputs and outputs, and first class support for numbers in any base with custom digits and arbitrary
        precision.
        The constructor also allows for automatic detection of base prefixes (0b, 0x, 0o) in string inputs, and
        provides options for case sensitivity and scientific notation handling.

        Parameters:
            value (Union[str, int, float, Decimal, Fraction, RadixNumber]):
                The number to be converted. If a RadixNumber is provided, it is returned as is.
                Floats are treated as scientific notation strings.
            base (int, optional):
                The base used to interpret string inputs. This parameter is ignored if the input includes an
                implicit base prefix (e.g. 0b, 0x, 0o) or when scientific notation is detected. Defaults to 10.
            digits (str, optional):
                String containing the characters representing the digits. Must not overlap with special characters
                (e.g. '.', '_', '[', ']'). Defaults to the module’s _DEFAULT_DIGITS.
            is_scientific_notation_str (bool, optional):
                Indicates whether to treat the input string as a scientific notation string, triggering a conversion
                to its full decimal representation. Defaults to False.
            zero_b_o_x_leading_implicit_based (bool, optional):
                If True, automatically detects prefixes (0b, 0x, 0o) in the input string and adjusts the base accordingly.
                Defaults to False.
            scientific_notation_char (str, optional):
                Characters used to denote scientific notation. Must not overlap with digits in their active range.
                Defaults to "eE".
            case_sensitive (bool, optional):
                Determines if the digit set and scientific notation characters are treated as case sensitive.
                If False, they are normalized to uppercase. Defaults to False.
            representation_base (int or str, optional):
                Specifies the base for output and operation propagation. Use an integer for a fixed base or
                "fraction" to preserve the Fraction representation. Defaults to None, inferring the base from the input.

        Raises:
            ValueError:
                If the provided digit set contains any reserved special characters or if the input value contains
                characters not found within the allowed digit set.

        Notes:
            - When the provided value is already a RadixNumber, it is directly assigned.
            - Scientific notation strings are fully expanded using a dedicated conversion mechanism without
            relying on floating-point arithmetic.
        """

        if not isinstance(value, (str, int, float, Decimal, Fraction, RadixNumber)):
            raise TypeError("value should be str, int, float, Decimal, Fraction or RadixNumber")

        if isinstance(value, RadixNumber):
            # frac:                          fractional value
            # case_sensitive:                case_sensitive
            # digits:                        string of digits used for representation and conversion of string
            # representation_base:           int or "fraction"
            self.frac = value.frac
            self.case_sensitive = value.case_sensitive
            self.digits = value.digits
            self.representation_base = value.representation_base
            # wont pass on cache, just to not cause unintended issues
            return 

        if base < 2 :
            raise BaseRangeError("base should be greater than 1")

        self.case_sensitive = case_sensitive
        digits = self._check_and_normalize_digits(digits=digits, case_sensitive=case_sensitive, base=base)
        self.digits = digits
        # normalize_scientific notation based on case 
        # dont check for sci and digit collision as it might never happen
        # do ALL value unrelated checks here 

        if isinstance(value, (float, Decimal, int, str)):
            if direct_conversion_of_float_decimal_to_frac:
                self.frac = Fraction(value)
                # break out of this if statement
            else:
                if not isinstance(value, int):
                    is_scientific_notation_str = True
                    
                value = str(value)
        
                # strip the value of leading and trailing spaces
                value = value.strip()

                # Normalize case if case sensitivity is disabled
                if not case_sensitive:
                    value = value.upper()

                if is_scientific_notation_str:
                    scientific_notation_char = self._check_and_normalize_scientific_notation_char(
                        scientific_notation_char=scientific_notation_char, digits=digits, case_sensitive=case_sensitive, base=base
                    )

                # Validate that the value only contains allowed characters
                if not set(value).issubset(digits + self.SPECIAL_CHARS + (scientific_notation_char if is_scientific_notation_str else "")): # gotta get chars and sci note
                    raise ValueError("value should only contain digits and special characters")

                if zero_b_o_x_leading_implicit_based:
                    if value.startswith("0x"):
                        value = value[2:]
                        base = 16
                    elif value.startswith("0b"):
                        value = value[2:]
                        base = 2
                    elif value.startswith("0o"):
                        value = value[2:]
                        base = 8
                    
                    # as base extended, digits might not be sufficent
                    self._check_and_normalize_digits(digits=digits, case_sensitive=case_sensitive, base=base)
                
                self.representation_base = self._check_representation_base(base, digits, representation_base, case_sensitive) # TODO probably incomplete
            
                if is_scientific_notation_str:
                    # no [] is supported in scientific notation mantissa, and clearly not in its exponent (can use itself for exponent analysis and check?)
                    value = self.scientific_str_to_decimal_str(value, scientific_notation_char=scientific_notation_char, case_sensitive=case_sensitive, digits=digits, base=base)
            
                i_str, fp_str, fp_rep_str = self.normalized_str_to_str_particles_and_check(value)
                self.frac = self._any_base_str_particles_to_frac(i_str, fp_str, fp_rep_str, base, digits)

        if isinstance(value, Fraction):
            self.frac = value

        # caches value for representation in the target base
        _ = self.representation_value
      
    def __repr__(self):
        numeric = "RadixNumber("
        if self.representation_base != "fraction":
           numeric += f"number={self.representation_value}, representation_base={self.representation_base}, digits={self.digits}, case_sensitive={self.case_sensitive}, "
        numeric += f"fraction=({str(self.frac)}))"
        return numeric
        # return f"number={self._append_any_base_str_particles_to_unified_str()}, representation_base={self.representation_base}, digits={self.digits if self.digits != self._DEFAULT_DIGITS else '(DEFAULT)'}, case_sensitive={self.case_sensitive})"
        # 
        # return f"RadixNumber(engine={str(self.engine)}, fraction={str(self.frac)})"
         
    def __str__(self):
        if self.representation_base != "fraction":
            return self._my_frac_to_any_base_str(self.digits, self.representation_base)
        else:
            return str(self.frac)

    def _my_frac_to_any_base_str(self, digits, base):
        return self._frac_to_any_base_str(self.frac, base, digits)

    @staticmethod
    def _frac_to_any_base_str(frac: Fraction, to_base: int, digits: str): # scientific notation
        """
        Converts a Fraction to a string representation in the specified base using given digit set.

        Args:
            frac (Fraction): The fraction to convert
            base_to (int): The target base for conversion (2-36)
            digits_to (str): String containing the digits to use for the target base

        Returns:
            str: String representation of the number in the target base, 
                including decimal point and fractional part if present

        Example:
            >>> RadixNumber._frac_to_any_base(Fraction(25, 4), 16, "0123456789ABCDEF")
            '6.4'
        """
        i_int, f_frac = RadixNumber._frac_extract_int_and_frac(frac)
        int_out = RadixNumber._partial_frac_to_any_base_str(i_int, to_base, True, digits)
        fraction_part_out = RadixNumber._partial_frac_to_any_base_str(f_frac, to_base, False, digits)
        return ( int_out + ("." + fraction_part_out) if fraction_part_out else "" )

    @staticmethod
    def _frac_extract_int_and_frac(fraction: Fraction) -> tuple[int, Fraction]:
        """
        Splits a fraction into integer and fractional parts.

        Args:
            fraction (Fraction): The fraction to split

        Returns:
            tuple[int, Fraction]: A tuple containing:
                - Integer part of the fraction
                - Remaining fractional part as a Fraction

        Example:
            >>> RadixNumber._frac_extract_int_and_frac(Fraction(7, 3))
            (2, Fraction(1, 3))
        """
        i, frac = divmod(fraction.numerator, fraction.denominator)
        return i, Fraction(frac, fraction.denominator)

    @staticmethod
    def _partial_frac_to_any_base_str(frac: Fraction, to_base: int, intpart: bool, digits: str) -> str:
        """
        Converts a Fraction to a string representation in any base, detecting repeating decimals.
        This function handles pure logic of the int and fractional part, with intpart flag to set
        which one will be processed at moment. 

        Args:
            x (Fraction): The fraction to convert
            to_base (int): Target base for conversion (2-36)
            intpart (bool): True if converting integer part, False for fractional part
            digits (str): String containing digits to use for the target base

        Returns:
            str: String representation of the number in target base.
                For fractional parts, repeating sequences are enclosed in square brackets.

        Example:
            >>> RadixNumber._frac_to_any_base_partial(Fraction(1, 3), 10, False, "0123456789")
            '[3]'  # represents 0.333...
            >>> RadixNumber._frac_to_any_base_partial(Fraction(25, 4), 16, True, "0123456789ABCDEF")
            '6'    # integer part of 6.4 in base 16
        """
        buffer_rep, out_x = "", ""
        while frac > 0:
            if not intpart:
                if gcd(frac.denominator, to_base) == 1:
                    if buffer_rep == "":
                        buffer_rep = frac
                        out_x += "["
                    elif buffer_rep == frac:
                        out_x += "]"
                        break
            frac, digit = divmod(frac, to_base) if intpart else RadixNumber._frac_extract_int_and_frac(frac * to_base)[::-1]
            out_x += digits[digit]
        return out_x[::-1] if intpart else out_x
    
    @staticmethod
    def _any_base_str_particles_to_frac(i: str, fp: str, fp_rep: str, from_base: int, digits: str) -> Fraction:
        """
        Converts a number from any base to a Fraction, handling integer, fractional and repeating parts.

        Args:
            i (str): Integer part of the number
            fp (str): Fractional part of the number (non-repeating)
            fp_rep (str): Repeating part of the fractional portion
            from_base (int): Base of the input number (2-36)
            digits (str): String containing the digits used in the input number

        Returns:
            Fraction: Exact representation of the input number as a Fraction

        Example:
            >>> RadixNumber._any_base_particles_to_frac("6", "4", "", 16, "0123456789ABCDEF")
            Fraction(25, 4)
            >>> RadixNumber._any_base_particles_to_frac("0", "3", "3", 10, "0123456789")
            Fraction(1, 3)  # converts 0.333... to 1/3
        """
        fraction = Fraction()

        for index, digit in enumerate(i):
            fraction += digits.index(digit) * (from_base ** (len(i) - index - 1))
        fraction += (Fraction(RadixNumber._any_base_str_particles_to_frac(fp, "", "", from_base, digits), from_base ** (len(fp)))) if fp else 0
        fraction += (Fraction(RadixNumber._any_base_str_particles_to_frac(fp_rep, "", "", from_base, digits), ((from_base ** len(fp_rep)) - 1) * (from_base ** len(fp)))) if fp_rep else 0
        return fraction

    # def num_to_frac():

    def __float__(self):
        # return float(RadixNumber.base_convert(ConversionInput(num=self._string_particle_to_string(), base_from=self.base, base_to=10, digits=self.digits)))   
        return float(self.frac)
            
    def __int__(self):
        # return int(RadixNumber.base_convert(ConversionInput(num=self._string_particle_to_string(), base_from=self.base, base_to=10, digits=self.digits)))
        return int(self.frac)
    
    # def compare_with_epsilon(self, other, epsilon=1e-10):
    #     return abs(float(self) - float(other)) < epsilon
    
    def __eq__(self, other): # int, RadixNumber, float, decimal
        if isinstance(other, RadixNumber):
            return self.frac == other.frac
        return self.frac == other

    def __gt__(self, other): # int, RadixNumber, float, decimal
        if isinstance(other, RadixNumber):
            return self.frac > other.frac
        return self.frac > other
    
    def __ge__(self, other): # int, RadixNumber, float, decimal
        if isinstance(other, RadixNumber):
            return self.frac >= other.frac
        return self.frac >= other

    def __lt__(self, other): # int, RadixNumber, float, decimal
        if isinstance(other, RadixNumber):
            return self.frac < other.frac
        return self.frac < other
    
    def __le__(self, other): # int, RadixNumber, float, decimal
        if isinstance(other, RadixNumber):
            return self.frac <= other.frac
        return self.frac <= other

    #bool
    #int
    #float
    #complex
    #index

    #call

    # matmul for base conversion

    def add():
        ...
        # normal fractional

    # def __add__(self, other):
    #     # str, Fraction ,'RadixNumber'
    #     if isinstance(other, RadixNumber):
    #         if self.representation_base == other.representation_base and self.digits == other.digits:
    #             return self._frac_to_any_base_str(
    #                 frac=
    #                 self.frac+other.frac, self.representation_base, self.digits)
    #     elif isinstance(other, (int, float, Decimal)):
    #         self.__add__(RadixNumber(other))

        
    def __radd__(self, other):
        ...

    def sub():
        ...
        # normal fractional

    def __sub__(self, other):
        ...
    def __rsub__(self, other):
        ...

    def mul(self, other): # R or L?
        ...
        # normal fractional 
    
    def __mul__(self, other):
        ...
    def __rmul__(self, other):
        ...

    def div():
        ...
        # normal fractional

    def __truediv__(self, other):
        ...
    def __rtruediv__(self, other):
        ...
    def __floordiv__(self, other):
        ...
    def __rfloordiv__(self, other):
        ...
    
    def divmod():
        ...
        # normal fractional 
    
    def __divmod__(self, other):
        ...
    def __rdivmod__(self, other):
        ...

    def pow():
        ...
    
    def __pow__(self, other):
        ...
    def __rpow__(self, other):
        ...
    
    def __neg__(self):
        self.frac = - self.frac
        return self
    def __pos__(self):
        return self
    def __abs__(self):
        self.frac = abs(self.frac)
        return self
    # def __invert__(self):
    #     ...

    def shift():
        ...

    def __rshift__(self, n: int):
        ...
    def __lshift__(self, n: int):
        ...
    def __rrshift__(self, n: int):
        ...
    def __rlshift__(self, n: int):
        ...

    # and, rand
    # xor, rxor
    # or, ror

    # better error
    # better doc string
    # test
    
    def to_base(self, base: int):
        ...
    
    def to_decimal(self):
        ...

    def matmul():
        ...
    
    def __matmul__(self, base: int):
        ...
    def __rmatmul__(self, base: int):
        ...


    # # convert to decimal
    # def to_decimal(self):
    


    @deprecated("Use new_function() instead")
    @staticmethod
    def base_convert(input_data: ConversionInput) -> str:
        i_str, fp_str, fp_rep_str = "", "", ""
        num = input_data.num
        if "." in num:
            i_str, fp_str = num.split(".")
            if ("[" in fp_str) or ("]" in fp_str):
                try:
                    fp_rep_str = fp_str[fp_str.index("[") + 1:fp_str.index("]")]
                    fp_str = fp_str[:fp_str.index("[")]
                except:
                    raise ValueError("Invalid input format for repeating decimal")
        else:
            i_str = num

        i_int, f_frac = RadixNumber._frac_extract_int_and_frac(RadixNumber._any_base_str_particles_to_frac(i_str, fp_str, fp_rep_str, input_data.base_from, input_data.digits))
        return (RadixNumber._partial_frac_to_any_base_str(i_int, input_data.base_to, True, input_data.digits) + 
                "." + RadixNumber._partial_frac_to_any_base_str(f_frac, input_data.base_to, False, input_data.digits))
    

class TheRadixNumber:
    """
    A number that knows its base and can be converted between different bases.
    
    This class represents a number in any base from 2 to 36, handling both 
    integer and fractional parts, including repeating decimals.
    """
    
    DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def __init__(self, value: Union[str, int, float, Fraction], base: int = 10, digits: Optional[str] = None):
        """
        Initialize a RadixNumber with a value and base.
        
        Args:
            value: The number value as string, int, float or Fraction
            base: The base of the number (2-36)
        
        Raises:
            BaseRangeError: If base is outside the allowed range
            DigitError: If any digit in the value is invalid for the given base
            ParseError: If the value string format is invalid
        """
        self._validate_base(base)
        self.base = base
        self.digits = digits or self.DIGITS
        self._fraction = self._parse_to_fraction(value)
    
    @classmethod
    def _validate_base(cls, base: int) -> None:
        if not BaseRange.MIN.value <= base <= BaseRange.MAX.value:
            raise BaseRangeError(f"Base must be between {BaseRange.MIN.value} and {BaseRange.MAX.value}")
    
    @classmethod
    def _validate_digits(cls, value: str, base: int) -> None:
        valid_digits = cls.DIGITS[:base]
        if not all(d in valid_digits for d in value if d not in ".[]-"):
            raise DigitError(f"Invalid digit(s) for base {base}")
    
    def _parse_to_fraction(self, value: Union[str, int, float, Fraction]) -> Fraction:
        """Convert the input value to a Fraction for internal representation"""
        if isinstance(value, Fraction):
            return value
        
        if isinstance(value, (int, float)):
            return Fraction(value)
        
        # String processing
        # value = value.upper() 
        self._validate_digits(value, self.base)
        
        int_part = ""
        frac_part = ""
        rep_part = ""
        
        # Parse the string into components
        if "." in value:
            int_part, frac_str = value.split(".")
            if "[" in frac_str and "]" in frac_str:
                match = re.search(r'\[(.*?)\]', frac_str)
                if not match:
                    raise ParseError("Invalid repeating decimal format")
                rep_part = match.group(1)
                frac_part = frac_str[:frac_str.index("[")]
            else:
                frac_part = frac_str
        else:
            int_part = value
        
        # Handle empty parts
        int_part = int_part or "0"
        
        # Convert to Fraction
        fraction = Fraction()
        
        # Integer part
        for index, digit in enumerate(int_part):
            if digit in "+-":  # Handle sign
                continue
            digit_value = self.DIGITS.index(digit)
            fraction += digit_value * (self.base ** (len(int_part) - index - 1))
        
        # Apply sign
        if int_part.startswith('-'):
            fraction = -fraction
            
        # Fractional part
        if frac_part:
            for index, digit in enumerate(frac_part):
                digit_value = self.DIGITS.index(digit)
                fraction += Fraction(digit_value, self.base ** (index + 1))
        
        # Repeating part
        if rep_part:
            repeating_value = Fraction(0)
            for index, digit in enumerate(rep_part):
                digit_value = self.DIGITS.index(digit)
                repeating_value += Fraction(digit_value, self.base ** (index + 1))
                
            # Formula for repeating decimal: x = n / (10^k * (10^p - 1))
            # where n is the repeating part, k is the position where repetition starts,
            # and p is the length of the repeating part
            denominator = (self.base ** len(rep_part)) - 1
            rep_fraction = Fraction(repeating_value.numerator, 
                                   repeating_value.denominator * denominator)
            
            # Adjust for the position after the decimal point
            rep_fraction = Fraction(rep_fraction.numerator,
                                   rep_fraction.denominator * (self.base ** len(frac_part)))
            
            fraction += rep_fraction
            
        return fraction
    
    def _int_and_frac_parts(self) -> Tuple[int, Fraction]:
        """Split the number into integer and fractional parts"""
        int_part = int(self._fraction)
        frac_part = self._fraction - int_part
        return int_part, frac_part
    
    def to_base(self, base: int) -> 'RadixNumber':
        """
        Convert the number to a different base
        
        Args:
            base: The target base (2-36)
            
        Returns:
            A new RadixNumber in the specified base
        """
        self._validate_base(base)
        # The internal representation as a Fraction doesn't change
        # We just create a new RadixNumber with the same fraction but different base
        new_number = RadixNumber(0, base)
        new_number._fraction = self._fraction
        return new_number
    
    def _convert_int_part(self, int_value: int, base: int) -> str:
        """Convert integer part to the target base"""
        if int_value == 0:
            return "0"
            
        result = ""
        is_negative = int_value < 0
        int_value = abs(int_value)
        
        while int_value > 0:
            digit = int_value % base
            result = self.DIGITS[digit] + result
            int_value //= base
            
        return "-" + result if is_negative else result
    
    def _convert_frac_part(self, frac_value: Fraction, base: int) -> str:
        """Convert fractional part to the target base, handling repeating decimals"""
        if frac_value == 0:
            return ""
            
        result = ""
        remainders = {}
        position = 0
        
        while frac_value > 0:
            # Check if we've seen this remainder before (indicates repeating decimal)
            if frac_value in remainders:
                start_pos = remainders[frac_value]
                non_repeating = result[:start_pos]
                repeating = result[start_pos:]
                return non_repeating + "[" + repeating + "]"
                
            # Record the current remainder and position
            remainders[frac_value] = position
            
            # Get the next digit
            frac_value *= base
            digit, frac_value = divmod(frac_value, 1)
            result += self.DIGITS[int(digit)]
            position += 1
            
            # Limit to prevent infinite loops for non-terminating non-repeating decimals
            # (which shouldn't exist in rational numbers, but protecting against potential bugs)
            if position > 100:
                return result + "..."
                
        return result
    
    def __str__(self) -> str:
        """
        Convert the number to its string representation in its base
        
        Returns:
            String representation of the number in its base
        """
        int_part, frac_part = self._int_and_frac_parts()
        
        int_str = self._convert_int_part(int_part, self.base)
        frac_str = self._convert_frac_part(frac_part, self.base)
        
        if frac_str:
            return f"{int_str}.{frac_str}"
        else:
            return int_str
    
    def __repr__(self) -> str:
        """
        Returns a string representation showing the number and its base
        
        Returns:
            String in format "RadixNumber('value', base)"
        """
        return f"RadixNumber('{self}', {self.base})"
    
    def __float__(self) -> float:
        """
        Convert to float in base 10
        
        Returns:
            Float value of the number
        """
        return float(self._fraction)
    
    def __int__(self) -> int:
        """
        Convert to int in base 10, discarding fractional part
        
        Returns:
            Integer value of the number (truncated)
        """
        return int(self._fraction)
    
    @property
    def fraction(self) -> Fraction:
        """
        Get the exact value as a Fraction
        
        Returns:
            The number as a Fraction
        """
        return self._fraction
    
    def __eq__(self, other) -> bool:
        if isinstance(other, RadixNumber):
            return self._fraction == other._fraction
        return self._fraction == other
    
    def __add__(self, other) -> 'RadixNumber':
        if isinstance(other, RadixNumber):
            result = RadixNumber(self._fraction + other._fraction, self.base)
            return result
        return RadixNumber(self._fraction + other, self.base)
    
    def __sub__(self, other) -> 'RadixNumber':
        if isinstance(other, RadixNumber):
            result = RadixNumber(self._fraction - other._fraction, self.base)
            return result
        return RadixNumber(self._fraction - other, self.base)
    
    def __mul__(self, other) -> 'RadixNumber':
        if isinstance(other, RadixNumber):
            result = RadixNumber(self._fraction * other._fraction, self.base)
            return result
        return RadixNumber(self._fraction * other, self.base)
    
    def __truediv__(self, other) -> 'RadixNumber':
        if isinstance(other, RadixNumber):
            result = RadixNumber(self._fraction / other._fraction, self.base)
            return result
        return RadixNumber(self._fraction / other, self.base)

    def __pow__(self, other) -> 'RadixNumber':
        if isinstance(other, RadixNumber):
            result = RadixNumber(self._fraction ** other._fraction, self.base)
            return result
        return RadixNumber(self._fraction ** other, self.base)
    
    def __neg__(self) -> 'RadixNumber':
        return RadixNumber(-self._fraction, self.base)
    
    def __abs__(self) -> 'RadixNumber':
        return RadixNumber(abs(self._fraction), self.base)
    
    def __rshift__(self, n: int) -> 'RadixNumber':
        """
        Right shift operator - shifts decimal point right by n positions
        Equivalent to multiplying by base^(-n)
        
        Args:
            n: Number of positions to shift right
            
        Returns:
            A new RadixNumber shifted right by n positions
        """
        if not isinstance(n, int):
            raise TypeError("Right shift amount must be an integer")
        
        shift_factor = Fraction(1, self.base ** n)
        return RadixNumber(self._fraction * shift_factor, self.base)
    
    def __lshift__(self, n: int) -> 'RadixNumber':
        """
        Left shift operator - shifts decimal point left by n positions
        Equivalent to multiplying by base^n
        
        Args:
            n: Number of positions to shift left
            
        Returns:
            A new RadixNumber shifted left by n positions
        """
        if not isinstance(n, int):
            raise TypeError("Left shift amount must be an integer")
        
        shift_factor = self.base ** n
        return RadixNumber(self._fraction * shift_factor, self.base)

