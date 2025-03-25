    # def __init_string__(
    #         self, 
    #         value: str,
    #         base: Optional[int] = None, # (#TODO: none for default behaviour, number for strict) base is used for understanding str inputs, ignored if zero_b_o_x_leading_implicit_based or scientific notation
    #         digits: str = _DEFAULT_DIGITS, # TODO: List or Tuple as well, also weird multi char should be handled here if wanna be handled
    #         is_scientific_notation_str = False, 
    #         zero_b_o_x_leading_implicit_based = False, # if true, if str has a format of 0b 0x 0o it would be converted to the respective base
    #         scientific_notation_char = "eE", # used for scientific notation conversion 
    #         case_sensitive = False, # if true, the digits and scientific notation char are case sensitive
    #         representation_base = None # None for default (using 10 for int, float, decimal, using `base` or b_o_x for str, using `"fraction"` for Fraction), int for base, "fraction" for fraction, this is used for showing output and cross operation propegation
    # ):

    # def num_to_num():

    # def _append_any_base_str_particles_to_unified_str(self):
    #     return self.i_str + ("." if (self.fp_rep_str or self.fp_str) else "") + self.fp_str + ("[" + self.fp_rep_str + "]" if self.fp_rep_str else "")

        # frac: fractional value
        # case_sensitive = case_sensitive
        # digits: string of digits used for representation and conversion of string
        # representation_base: int or "fraction"
        # representation_value

# keep these for same base merging, @ and []

# operation stuff
# [] @ 
# digits, base and other stuff how to keep and propegate cross operations

# @Base() @Digits() @SciNot() @CaseSensitive
# .to(base="")
# [10] to base 10