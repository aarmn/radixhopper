"""
This module provides the RadixNumber class, which allows for flexible base conversion and representation of numbers.
It supports operations on numbers in arbitrary bases, scientific notation, and repeating decimals.
"""

import re
import sys
import math
from fractions import Fraction
from typing import Optional, Union
from decimal import Decimal
from typeguard import typechecked
from .error import BaseRangeError

TOLERANCE = sys.float_info.epsilon * 2

class RadixNumber:
    """
    A class to represent numbers in arbitrary bases with flexible conversion and representation options.

    Constants:
        _DEFAULT_DIGITS (str): Default set of digits for base representation.
        SPECIAL_CHARS (str): Special characters allowed in number representations.

    Internals:
        frac (Fraction): Fractional value of the number.
        case_sensitive (bool): Whether the digit set is case-sensitive.
        digits (str): String of digits used for representation and conversion.
        representation_base (Union[int, str]): Base for output representation (as int) or "fraction" (as str) for Fraction.

    Cached Internals:
        getter: representation_value (str): Cached string representation of the number in the current base.
            - _representation_cache_hash (int): Hash of the current state for cache validation.
            - _representation_cache_value (str): Cached value of the string representation.
            used for performance optimization.
    """
    _DEFAULT_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    SPECIAL_CHARS = "+-._[] "

    @staticmethod
    @typechecked
    def scientific_str_to_decimal_str(
        sci_str: str,
        scientific_notation_char: str = "eE",
        case_sensitive: bool = False,
        digits: str = "0123456789",
        base: int = 10,
    ) -> str:
        """
        Convert a scientific notation string to a fully written o t decimal string.
        Works with string operations only, without converting the mantissa to float (should convert exponent to int tho).

        Args:
            sci_str (str): Scientific notation string (e.g., '1.23e+5', '4.56E-3').
            scientific_notation_char (str, optional): Characters used for scientific notation. Defaults to "eE".
            case_sensitive (bool, optional): Whether to treat the input as case-sensitive. Defaults to False.
            digits (str, optional): String of digits used for representation. Defaults to "0123456789".
            base (int, optional): Base of the number system. Defaults to 10.

        Returns:
            str: Fully written-out decimal string or original string if invalid format.

        Raises:
            ValueError: If scientific notation characters overlap with digits or if the input format is invalid.
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

    def to(self, *, base: Optional[int] = None, digits: Optional[str] = None) -> "RadixNumber":
        """
        Convert the number to a specified base and/or digit set.

        Args:
            base (Optional[int], optional): Target base for conversion. Defaults to None.
            digits (Optional[str], optional): Target digit set for conversion. Defaults to None.

        Returns:
            RadixNumber: The updated RadixNumber instance.
        """
        self.representation_base = base if base is not None else self.representation_base
        self.digits = digits if digits is not None else self.digits
        self.representation_value
        return self

    @staticmethod
    @typechecked
    def _check_representation_base(
        base: int, digits: str, representation_base: Optional[Union[int, str]], case_sensitive: bool
    ) -> Union[int, str]:
        """
        Validate and normalize the representation base.

        Args:
            base (int): Base of the number system.
            digits (str): String of digits used for representation.
            representation_base (Optional[Union[int, str]]): Desired representation base.
            case_sensitive (bool): Whether the digit set is case-sensitive.

        Returns:
            Union[int, str]: Validated representation base.

        Raises:
            ValueError: If the representation base is invalid.
        """
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

    def _check_and_normalize_digits(
        self, *, digits: str, case_sensitive: bool, base: int
    ) -> str:
        """
        Validate and normalize the digit set.

        Args:
            digits (str): String of digits used for representation.
            case_sensitive (bool): Whether the digit set is case-sensitive.
            base (int): Base of the number system.

        Returns:
            str: Normalized digit set.

        Raises:
            ValueError: If the digit set is invalid.
        """
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
    ) -> str:
        """
        Validate and normalize the scientific notation characters.

        Args:
            scientific_notation_char (str): Characters used for scientific notation.
            digits (str): String of digits used for representation.
            case_sensitive (bool): Whether the digit set is case-sensitive.
            base (int): Base of the number system.

        Returns:
            str: Normalized scientific notation characters.

        Raises:
            ValueError: If the scientific notation characters overlap with digits.
        """
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
    @typechecked
    def normalized_str_to_str_particles_and_check(value_string: str) -> tuple[int, str, str, str]:
        """
        Normalize a string representation of a number and extract its components.

        Args:
            value_string (str): String representation of the number.

        Returns:
            tuple[str, str, str]: Tuple containing integer part, fractional part, and repeating fractional part.

        Raises:
            ValueError: If the input format is invalid.
        """
        sign, i_str, fp_str, fp_rep_str = 1, "", "", ""

        if value_string.startswith("-"):
            sign = -1
            value_string = value_string[1:]
        elif value_string.startswith("+"):
            value_string = value_string[1:]

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

        return sign, i_str, fp_str, fp_rep_str

    @property
    def representation_value(self) -> str:
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
        zero_b_o_x_leading_implicit_based: bool = False,
        scientific_notation_char: str = "eE",
        case_sensitive: bool = False,
        representation_base: Optional[Union[int, str]] = None,
        gentle_to_over_base: bool = False,
    ) -> None:
        """
        Initialize a RadixNumber instance with flexible base conversion options.

        Args:
            value (Union[str, int, float, Decimal, Fraction, RadixNumber]): The number to be converted.
            base (int, optional): Base for interpreting string inputs. Defaults to 10.
            digits (str, optional): String of digits used for representation. Defaults to _DEFAULT_DIGITS.
            is_scientific_notation_str (bool, optional): Whether the input is in scientific notation. Defaults to False.
            direct_conversion_of_float_decimal_to_frac (bool, optional): Directly convert float/Decimal to Fraction. Defaults to False.
            zero_b_o_x_leading_implicit_based (bool, optional): Detect base prefixes (0b, 0x, 0o) in input strings. Defaults to False.
            scientific_notation_char (str, optional): Characters for scientific notation. Defaults to "eE".
            case_sensitive (bool, optional): Whether the digit set is case-sensitive. Defaults to False.
            representation_base (Optional[Union[int, str]], optional): Base for output representation. Defaults to None.
            gentle_to_over_base (bool, optional): Allow digits outside the base range without raising an error.
                                Useful for research or experimental purposes. Defaults to False.

        Raises:
            TypeError: If the input value is of an unsupported type.
            ValueError: If the input format or digit set is invalid.
        """
        if not isinstance(value, (str, int, float, Decimal, Fraction, RadixNumber)):
            raise TypeError(
                "value should be str, int, float, Decimal, Fraction or RadixNumber"
            )

        if isinstance(value, RadixNumber):
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
            if direct_conversion_of_float_decimal_to_frac: # why not always this? for int, float and Decimal?
                self.frac = Fraction(value)
                # break out of this if statement
            else:
                if (not isinstance(value, int)) and (not isinstance(value, str)):
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

                # Validate that the value only contain digits which are in the part
                # of the base (look if there is a digit in str which is not in the
                # base-th first elements of digits string)
                # Find digits that are over the base limit
                over_base_digits = [d for d in value if d in digits and digits.index(d) >= base]

                if over_base_digits and not gentle_to_over_base:
                    if is_scientific_notation_str:
                        # Normalize scientific_notation_char for comparison if needed
                        sci_chars = scientific_notation_char
                        if not case_sensitive:
                            sci_chars = sci_chars.upper()

                        # Check if all over-base digits are scientific notation characters
                        if not all(char in sci_chars for char in over_base_digits):
                            raise ValueError(
                                "value contains digits outside the base range that are not scientific notation characters"
                            )
                    else:
                        raise ValueError(
                            "value contains digits outside the base range"
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

                sign, i_str, fp_str, fp_rep_str = (
                    self.normalized_str_to_str_particles_and_check(value)
                )
                self.frac = self._any_base_str_particles_to_frac(
                    i_str, fp_str, fp_rep_str, base, digits
                )
                self.frac = sign * self.frac

        if isinstance(value, Fraction):
            self.frac = value

        # caches value for representation in the target base
        _ = self.representation_value

    def __repr__(self) -> str:
        """
        Return a string representation of the RadixNumber instance.

        Returns:
            str: String representation of the instance.
        """
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

        sign, int_part, frac_part, frac_rep_part = (
            self.normalized_str_to_str_particles_and_check(self.representation_value)
        )
        # Build the latex string parts
        parts = []
        if sign == -1:
            parts.append("-")
        parts.append(int_part)

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

    def __str__(self) -> str:
        """
        Return the string representation of the number in the current representation base.

        Returns:
            str: String representation of the number.
        """
        if self.representation_base != "fraction":
            return self._my_frac_to_any_base_str(self.digits, self.representation_base)
        else:
            return str(self.frac)

    def _my_frac_to_any_base_str(self, digits, base):
        return self._frac_to_any_base_str(self.frac, base, digits)

    @staticmethod
    @typechecked
    def _frac_to_any_base_str(
        frac: Union[Fraction, int], to_base: int, digits: str
    ) -> str:
        """
        Convert a Fraction to a string representation in the specified base.

        Args:
            frac (Fraction): The fraction to convert.
            to_base (int): Target base for conversion.
            digits (str): String of digits used for the target base.

        Returns:
            str: String representation of the number in the target base,
                including decimal point and fractional part if present

        Example:
            >>> RadixNumber._frac_to_any_base(Fraction(25, 4), 16, "0123456789ABCDEF")
            '6.4'
        """
        # print(f"Converting {frac} to base {to_base} with digits {digits}")
        i_int, f_frac = RadixNumber._frac_extract_int_and_frac(frac)
        # print(f"Integer part: {i_int}, Fractional part: {f_frac}")
        sign_i, int_out = RadixNumber._partial_frac_to_any_base_str(
            i_int, to_base, True, digits
        )
        # print(f"Integer part in base {to_base}: {int_out}")
        sign_f, fraction_part_out = RadixNumber._partial_frac_to_any_base_str(
            f_frac, to_base, False, digits
        )
        # print(f"Fractional part in base {to_base}: {fraction_part_out}")
        if int_out == "":
            int_out = "0"
        if sign_f == -1 or sign_i == -1:
            int_out = "-" + int_out
        return (int_out) + (("." + fraction_part_out) if fraction_part_out else "")

    @staticmethod
    @typechecked
    def _frac_extract_int_and_frac(fraction: Fraction) -> tuple[int, Fraction]:
        """
        Split a fraction into integer and fractional parts.

        Args:
            fraction (Fraction): The fraction to split.

        Returns:
            tuple[int, Fraction]: Integer part and fractional part as a Fraction.
        Example:
            >>> RadixNumber._frac_extract_int_and_frac(Fraction(7, 3))
            (2, Fraction(1, 3))
        """
        i = math.trunc(fraction)  # Get the integer part
        frac = fraction - i  # Get the fractional part
        # i, frac = divmod(fraction.numerator, fraction.denominator) used to be used, but couldn't handle negative fractions correctly
        return i, frac

    @staticmethod
    @typechecked
    def _partial_frac_to_any_base_str(
        frac: Union[Fraction, int], to_base: int, intpart: bool, digits: str
    ) -> tuple[int, str]:
        """
        Converts a Fraction to a string representation in any base, detecting repeating decimals.
        This function handles pure logic of the int and fractional part, with intpart flag to set
        which one will be processed at moment.

        Args:
            frac (Fraction): The fraction to convert.
            to_base (int): Target base for conversion.
            intpart (bool): True if converting integer part, False for fractional part.
            digits (str): String of digits used for the target base.

        Returns:
            str: String representation of the number in the target base.
        """
        sign = 1 if frac >= 0 else -1
        frac = abs(frac)
        buffer_rep, out_x = "", ""
        while frac > 0:
            if not intpart:
                if math.gcd(frac.denominator, to_base) == 1:
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
        return sign, out_x[::-1] if intpart else out_x

    @staticmethod
    @typechecked
    def _any_base_str_particles_to_frac(
        i: str, fp: str, fp_rep: str, from_base: int, digits: str
    ) -> Fraction:
        """
        Convert a number from any base to a Fraction, handling integer, fractional, and repeating parts.

        Args:
            i (str): Integer part of the number.
            fp (str): Fractional part of the number (non-repeating).
            fp_rep (str): Repeating part of the fractional portion.
            from_base (int): Base of the input number.
            digits (str): String of digits used in the input number.

        Returns:
            Fraction: Exact representation of the input number as a Fraction.
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
        """
        Compare the RadixNumber with a float value within a tolerance.

        Args:
            other (float): The float value to compare.
            epsilon (float, optional): Tolerance for comparison. Defaults to TOLERANCE.

        Returns:
            bool: True if the values are within the tolerance, False otherwise.
        """
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
        return self.bioperand_operatin_handle_strategy(other, lambda x, y: Fraction(x // y,1))
    def __rfloordiv__(self, other):
        return self.bioperand_operatin_handle_strategy(other, lambda x, y: Fraction(y // x,1))

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

    def __trunc__(self):
        i_int, _ = RadixNumber._frac_extract_int_and_frac(self.frac)
        self.frac = Fraction(i_int, 1)
        return self
    def __round__(self):
        i_int, f_frac = RadixNumber._frac_extract_int_and_frac(self.frac)
        self.frac = Fraction(i_int + round(f_frac), 1)
        return self
    def __floor__(self):
        self.frac = Fraction(math.floor(self.frac), 1) #self.frac.numerator // self.frac.denominator
        return self
    def __ceil__(self):
        self.frac = Fraction(math.ceil(self.frac), 1)
        return self
    def __bool__(self):
        return bool(self.frac)

    def __matmul__(self, digits: str):
        return self.to(digits=digits)
    def __rmatmul__(self, smth):
        return NotImplemented
    def __getitem__(self, base: Union[int, str]):
        return self.to(base=base)

    # def __hash__(self):
    # def __format__(self):

    # gotta change up the int?

    # def __divmod__(self, other): ...
    # def __rdivmod__(self, other): ...
    # def __mod__(self, other): ...
    # def __rmod__(self, other): ...
    # def __pow__(self, other):
    #     return self.bioperand_operatin_handle_strategy(other, lambda x, y: x ** y) # untested
    # def __rpow__(self, other): ...

    def __rshift__(self, n: int) -> "RadixNumber":
        if n < 0:
            return self.__lshift__(-n)
        return self // (self.representation_base ** n)

    def __lshift__(self, n: int) -> "RadixNumber":
        if n < 0:
            return self.__rshift__(-n)
        return self * (self.representation_base ** n)

    def __rrshift__(self, n: int) -> "RadixNumber":
        if int(self) != self.frac:
            raise ValueError("Cannot shift by a non-integer value")
        n >> int(self)

    def __rlshift__(self, n: int) -> "RadixNumber":
        if int(self) != self.frac:
            raise ValueError("Cannot shift by a non-integer value")
        n << int(self)
