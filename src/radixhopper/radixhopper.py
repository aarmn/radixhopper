import re
import sys
from fractions import Fraction
from math import gcd
from typing import Optional, Union
from decimal import Decimal
from typeguard import typechecked
from error import BaseRangeError

TOLERANCE = sys.float_info.epsilon * 2

# ‌TODO: [NEXT VERS] handle none singular digit with list, maximal munch, and ambiguity check (should use a wrapper around the actual thing, instead of directly working with strings as digits)
# TODO: [NEXT VERS] unary base easter egg

# TODO: keep these for same base merging, @ and []
# TODO: Improve errors (more helpful, like in check, what went wrong, what overlaps, ...)
# TODO: add unit test (octal, hex, 0x, and sci notation, zero, ...)
# TODO: nix?
# TODO: github actions?
# TODO: improve pydocs
# TODO: improve comments
# TODO: operations
# TODO: chars should be limited to base bug for 0b17
# IDEA: call objects handle for some actions maybe

class RadixNumber:
    _DEFAULT_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    SPECIAL_CHARS = "+-._[] "

    # internals
    # frac:                          fractional value
    # case_sensitive:                case_sensitive
    # digits:                        string of digits used for representation and conversion of string
    # representation_base:           int or "fraction"
    # getter | representation_value: a getter with buffer, of the string representation of the number in the base, for performance sake
    # _representation_cache_hash:
    # _representation_cache_value:

    @staticmethod
    @typechecked
    def scientific_str_to_decimal_str(
        sci_str: str,
        scientific_notation_char: str = "eE",
        case_sensitive: bool = False,
        digits: str = "0123456789",
        base: int = 10,
    ):
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
        if any(
            (char in digits) and (digits.index(char) <= base)
            for char in scientific_notation_char
        ):
            raise ValueError(
                "Scientific notation char should not overlap with digits, specifically when the overlapping chars are in the range of used digits of the base"
            )

        sci_str = sci_str.strip()

        if not sci_str:
            raise ValueError("Empty input string")

        if sci_str.startswith("_"):
            raise ValueError("Invalid scientific notation format")

        sci_str = sci_str.replace("_", "")

        if not case_sensitive:
            sci_str = sci_str.lower()
            scientific_notation_char = scientific_notation_char.lower()

        # Check if it's already in decimal form (no 'e' or 'E', although, scientific notatatoin char is overridable)
        if set(scientific_notation_char).isdisjoint(sci_str):
            return sci_str

        spliter = lambda x: re.split( # NOQA
            f'[{"".join(re.escape(d) for d in set(scientific_notation_char))}]+',
            sci_str,
        ) 

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
            if x.startswith("+"):
                return x[1:], False
            if x.startswith("-"):
                return x[1:], True
            return x, False

        # Validate exponent as a number, as we need its value later on for shifts
        exponent, negative_exponent = sign_extractor(exponent)

        exponent = int(
            RadixNumber(
                exponent, base=base, digits=digits, is_scientific_notation_str=False
            )
            .to(base=10)
            .representation_value
        )  # int(RadixNumber.base_convert(ConversionInput(num=exponent, base_from=base, base_to=10, digits=digits))[:-1])
        exponent = -exponent if negative_exponent else exponent

        mantissa, negative_mantissa = sign_extractor(mantissa)

        # Check for multiple decimal points
        if mantissa.count(".") > 1:
            raise ValueError("Invalid mantissa format")

        # Handle decimal point in mantissa
        if "." in mantissa:
            dot_pos = mantissa.find(".")
            digit_only = mantissa.replace(".", "")
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
            result = "0." + "0" * (-new_pos) + digit_only
        elif new_pos >= len(digit_only):
            result = digit_only + "0" * (new_pos - len(digit_only))
        else:
            result = digit_only[:new_pos] + "." + digit_only[new_pos:]

        # Add negative sign if needed
        if negative_mantissa:
            result = "-" + result

        # Clean up trailing zeros and decimal point
        if "." in result:
            result = result.rstrip("0").rstrip(".")

        return result

    def to(self, *, base=None, digits=None):  # base, digits
        self.representation_base = base if base is not None else self.representation_base
        self.digits = digits if digits is not None else self.digits
        self.representation_value
        return self

    @staticmethod
    def _check_representation_base(
        base: int, digits: str, representation_base: Optional[int], case_sensitive: bool
    ):
        if representation_base is None:
            return base
        elif isinstance(representation_base, int):
            if len(digits) < representation_base:
                raise ValueError(
                    "Representation base should be less than or equal to the number of digits"
                )
            return representation_base
        elif representation_base == "fraction":
            return representation_base
        else:
            raise ValueError("representation_base should be int or 'fraction'")

    # def _check_base(self, base: int):

    def _check_and_normalize_digits(
        self, *, digits: str, case_sensitive: bool, base: int
    ):
        if not case_sensitive:
            digits = digits.upper()

        if len(set(digits)) != len(digits):
            raise ValueError("Digits should be unique")

        if not set(digits).isdisjoint(self.SPECIAL_CHARS):
            raise ValueError(
                "Digits should not overlap with special characters of ., _, [, or ]"
            )

        if len(digits) < base:
            raise ValueError("Digits should be at least as long as the base")

        return digits

    # def _check_value(self, value: str, base: int):
        # value should only contain digits and special characters, and check if the digits are in the base range

        # if base < 2:
        #     raise BaseRangeError("Base should be greater than 1")
        # if base > len(self.digits):
        #     raise BaseRangeError(
        #         f"Base {base} is larger than the number of digits {len(self.digits)}"
        #     )
        # return base

    def _check_and_normalize_scientific_notation_char(
        self,
        *,
        scientific_notation_char: str,
        digits: str,
        case_sensitive: bool,
        base: int,
    ):
        # normal digit?
        # 1. Convert scientific notation chars to uppercase if case insensitive
        if not case_sensitive:
            scientific_notation_char = scientific_notation_char.upper()

        # 2. Ensure that scientific notation chars are unique (no repeating characters)
        scientific_notation_char = str("".join(set(scientific_notation_char)))

        # 3. Check that scientific notation chars do not overlap with digits in the active range
        if any(
            ((char in digits) or (char in scientific_notation_char))
            and (digits.index(char) <= base)
            for char in scientific_notation_char
        ):
            raise ValueError(
                "Scientific notation char should not overlap with digits, specifically when the overlapping chars are in the range of used digits of the base"
            )

        return scientific_notation_char

    @staticmethod
    def normalized_str_to_str_particles_and_check(value_string):
        i_str, fp_str, fp_rep_str = "", "", ""

        if "." in value_string:
            i_str, fp_str = value_string.split(".")
            if ("[" in fp_str) or ("]" in fp_str):
                if fp_str.count("[") != 1 or fp_str.count("]") != 1:
                    raise ValueError("Invalid input format for repeating decimal")
                if fp_str.index("[") > fp_str.index("]"):
                    raise ValueError("Invalid input format for repeating decimal")
                try:
                    fp_rep_str = fp_str[fp_str.index("[") + 1 : fp_str.index("]")]
                    fp_str = fp_str[: fp_str.index("[")]
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
        current_hash = hash(
            (self.frac, self.digits, self.case_sensitive, self.representation_base)
        )
        if (
            hasattr(self, "_representation_cache_hash")
            and self._representation_cache_hash == current_hash
        ):
            return self._representation_cache_value

        if self.representation_base == "fraction":
            value = str(self.frac)
        else:
            value = self._my_frac_to_any_base_str(
                self.digits, self.representation_base
            )  # TODO: check is this the right shit

        self._representation_cache_hash = current_hash
        self._representation_cache_value = value
        return value

    @typechecked
    def __init__(
        self,
        value: Union[str, int, float, Decimal, Fraction, "RadixNumber"],
        base: int = 10,  # (#TODO: none for default behaviour, number for strict) base is used for understanding str inputs, ignored if zero_b_o_x_leading_implicit_based or scientific notation
        digits: str = _DEFAULT_DIGITS,  # TODO: List or Tuple as well, also weird multi char should be handled here if wanna be handled
        is_scientific_notation_str: bool = False,
        direct_conversion_of_float_decimal_to_frac: bool = False,
        zero_b_o_x_leading_implicit_based: bool = False,  # if true, if str has a format of 0b 0x 0o it would be converted to the respective base
        scientific_notation_char: str = "eE",  # used for scientific notation conversion
        case_sensitive: bool = False,  # if true, the digits and scientific notation char are case sensitive
        representation_base: Optional[
            int
        ] = None,  # None for default (using 10 for int, float, decimal, using `base` or b_o_x for str, using `"fraction"` for Fraction), int for base, "fraction" for fraction, this is used for showing output and cross operation propegation
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
            raise TypeError(
                "value should be str, int, float, Decimal, Fraction or RadixNumber"
            )

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

        if base < 2:
            raise BaseRangeError("base should be greater than 1")

        self.case_sensitive = case_sensitive
        digits = self._check_and_normalize_digits(
            digits=digits, case_sensitive=case_sensitive, base=base
        )
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
                    scientific_notation_char = (
                        self._check_and_normalize_scientific_notation_char(
                            scientific_notation_char=scientific_notation_char,
                            digits=digits,
                            case_sensitive=case_sensitive,
                            base=base,
                        )
                    )

                # Validate that the value only contains allowed characters
                if not set(value).issubset(
                    digits
                    + self.SPECIAL_CHARS
                    + (scientific_notation_char if is_scientific_notation_str else "")
                ):  # gotta get chars and sci note
                    raise ValueError(
                        "value should only contain digits and special characters"
                    )

                if zero_b_o_x_leading_implicit_based:
                    if value.startswith("0x" if case_sensitive else "0X"):
                        value = value[2:]
                        base = 16
                    elif value.startswith("0b" if case_sensitive else "0B"):
                        value = value[2:]
                        base = 2
                    elif value.startswith("0o" if case_sensitive else "0O"):
                        value = value[2:]
                        base = 8

                    # as base extended, digits might not be sufficent
                    self._check_and_normalize_digits(
                        digits=digits, case_sensitive=case_sensitive, base=base
                    )

                self.representation_base = self._check_representation_base(
                    base, digits, representation_base, case_sensitive
                )  # TODO probably incomplete

                if is_scientific_notation_str:
                    # no [] is supported in scientific notation mantissa, and clearly not in its exponent (can use itself for exponent analysis and check?)
                    value = self.scientific_str_to_decimal_str(
                        value,
                        scientific_notation_char=scientific_notation_char,
                        case_sensitive=case_sensitive,
                        digits=digits,
                        base=base,
                    )

                i_str, fp_str, fp_rep_str = (
                    self.normalized_str_to_str_particles_and_check(value)
                )
                self.frac = self._any_base_str_particles_to_frac(
                    i_str, fp_str, fp_rep_str, base, digits
                )

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

    def _repr_latex_(self):
        """
        LaTeX representation for Jupyter notebooks.
        Returns a LaTeX string for mathematical display with proper formatting:
        - Integer part
        - Optional decimal point and non-repeating fractional part
        - Optional repeating part with overline
        - Base subscript
        """

        if self.representation_base == "fraction":
            return rf"$$\frac{{{self.frac.numerator}}}{{{self.frac.denominator}}}$$"

        int_part, frac_part, frac_rep_part = (
            self.normalized_str_to_str_particles_and_check(self.representation_value)
        )
        # Build the latex string parts
        parts = [int_part]

        # Add decimal point and fraction part if either fraction or repeating part exists
        if frac_part or frac_rep_part:
            parts.append(".")
            parts.append(frac_part)

        # Add repeating part with overline if it exists
        if frac_rep_part:
            parts.append(f"\\overline{{{frac_rep_part}}}")
        
        # Combine parts and add base subscript
        return f"$${''.join(parts)}_{{{self.representation_base}}}$$"
    
    def _repr_mimebundle_(self, include=None, exclude=None):
        return {
            # "text/html": self._repr_html_(),
            "text/latex": self._repr_latex_(),
            "text/plain": self.__repr__(),
        }

    def __str__(self):
        if self.representation_base != "fraction":
            return self._my_frac_to_any_base_str(self.digits, self.representation_base)
        else:
            return str(self.frac)

    def _my_frac_to_any_base_str(self, digits, base):
        return self._frac_to_any_base_str(self.frac, base, digits)

    @staticmethod
    def _frac_to_any_base_str(
        frac: Fraction, to_base: int, digits: str
    ):  # scientific notation
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
        int_out = RadixNumber._partial_frac_to_any_base_str(
            i_int, to_base, True, digits
        )
        fraction_part_out = RadixNumber._partial_frac_to_any_base_str(
            f_frac, to_base, False, digits
        )
        return (int_out if int_out else "0") + (("." + fraction_part_out) if fraction_part_out else "")

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
    def _partial_frac_to_any_base_str(
        frac: Fraction, to_base: int, intpart: bool, digits: str
    ) -> str:
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
            frac, digit = (
                divmod(frac, to_base)
                if intpart
                else RadixNumber._frac_extract_int_and_frac(frac * to_base)[::-1]
            )
            out_x += digits[digit]
        return out_x[::-1] if intpart else out_x

    @staticmethod
    def _any_base_str_particles_to_frac(
        i: str, fp: str, fp_rep: str, from_base: int, digits: str
    ) -> Fraction:
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
        fraction += (
            (
                Fraction(
                    RadixNumber._any_base_str_particles_to_frac(
                        fp, "", "", from_base, digits
                    ),
                    from_base ** (len(fp)),
                )
            )
            if fp
            else 0
        )
        fraction += (
            (
                Fraction(
                    RadixNumber._any_base_str_particles_to_frac(
                        fp_rep, "", "", from_base, digits
                    ),
                    ((from_base ** len(fp_rep)) - 1) * (from_base ** len(fp)),
                )
            )
            if fp_rep
            else 0
        )
        return fraction

    def compare_float(self, other: float, epsilon: float = TOLERANCE) -> bool:
        return abs(float(self.frac) - other) < TOLERANCE

    def __eq__(self, other):  # int, RadixNumber, float, decimal
        if isinstance(other, RadixNumber):
            return self.frac == other.frac
        return self.frac == other

    def __gt__(self, other):  # int, RadixNumber, float, decimal
        if isinstance(other, RadixNumber):
            return self.frac > other.frac
        return self.frac > other

    def __ge__(self, other):  # int, RadixNumber, float, decimal
        if isinstance(other, RadixNumber):
            return self.frac >= other.frac
        return self.frac >= other

    def __lt__(self, other):  # int, RadixNumber, float, decimal
        if isinstance(other, RadixNumber):
            return self.frac < other.frac
        return self.frac < other

    def __le__(self, other):  # int, RadixNumber, float, decimal
        if isinstance(other, RadixNumber):
            return self.frac <= other.frac
        return self.frac <= other

    def bioperand_operatin_handle_strategy(self, other, operation, default_base="fraction"):
        if isinstance(other, RadixNumber):
            if self.representation_base == other.representation_base and self.digits == other.digits:
                new_frac = operation(self.frac, other.frac)
                self.frac = new_frac
                return self
            else:
                # if not same base and digits, convert to fraction and do the operation
                new_frac = operation(self.frac, other.frac)
                return RadixNumber(
                    new_frac,
                    representation_base="fraction",
                    digits=self._DEFAULT_DIGITS if self.digits != other.digits else self.digits,
                )
        if isinstance(other, str):
            other = RadixNumber(
                other,
                base=self.representation_base,
                digits=self.digits,
                representation_base=self.representation_base,
                case_sensitive=self.case_sensitive,
            )
            self.frac = operation(self.frac, other.frac)
            return self
        try:
            self.frac = operation(self.frac, Fraction(other))
            return self
        except (ValueError, TypeError):
            # Handle the case where other is not a valid number
            raise ValueError(f"Invalid operation with {other}, of type, {type(other)}")            

    def __add__(self, other):
        return self.bioperand_operatin_handle_strategy(other, lambda x, y: x + y)
    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.bioperand_operatin_handle_strategy(other, lambda x, y: x - y)
    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        return self.bioperand_operatin_handle_strategy(other, lambda x, y: x * y)
    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self.bioperand_operatin_handle_strategy(other, lambda x, y: x / y)
    def __rtruediv__(self, other):
        return (~self) * other
    
    def __floordiv__(self, other):
        return self.bioperand_operatin_handle_strategy(other, lambda x, y: x // y)
    def __rfloordiv__(self, other): 
        return self.bioperand_operatin_handle_strategy(other, lambda x, y: y // x)

    def __divmod__(self, other): ...
    def __rdivmod__(self, other): ...
    def __mod__(self, other): ...
    def __rmod__(self, other): ...
    def __pow__(self, other): ...
    def __rpow__(self, other): ...

    def __neg__(self):
        self.frac = -self.frac
        return self

    def __pos__(self):
        return self

    def __abs__(self):
        self.frac = abs(self.frac)
        return self

    def __invert__(self):
        self.frac = Fraction(self.frac.denominator, self.frac.numerator)
        return self

    # Conversion dunder methods
    def decimal(self):
        return Decimal(self.frac.numerator) / Decimal(self.frac.denominator)
    def __float__(self):
        return float(self.frac)
    def __int__(self):
        return int(self.frac)

    # Not sure Dunders 

    # and, rand
    # xor, rxor
    # or, ror

    # not sure how this will be useful, with []
    # and to() function already available
    def __matmul__(self, base: int):
        return NotImplemented
    def __rmatmul__(self, base: int):
        return NotImplemented

    # def __trunc__(self):
    # def __round__(self):
    # def __floor__(self):
    # def __ceil__(self):
    # def __index__(self):
    # def __hash__(self):
    # def __bool__(self):
    # def __format__(self):
    # def __next__(self):
    # def __contains__(self):
    # def __reversed__(self):

    # not sure how to implement this
    # should it be shift in base or base 2?
    # how to handle sub 1 values?
    # denom * base for r and nom * base for l?
    # then what about info loss of real shift?
    # more useful overload?
    def __rshift__(self, n: int) -> "RadixNumber":
        return NotImplemented

    def __lshift__(self, n: int) -> "RadixNumber":
        return NotImplemented

    def __rrshift__(self, n: int) -> "RadixNumber":
        return NotImplemented

    def __rlshift__(self, n: int) -> "RadixNumber":
        return NotImplemented

RadixNumber("1K", base=16, digits="0123456789ABCDEF", representation_base=10, case_sensitive=False).representation_value