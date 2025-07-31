#!/usr/bin/env python3
"""
RadixHopper CLI - Base conversion tool with rich formatting.
"""

import sys
from typing import Any, Dict

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from radixhopper import RadixNumber

# TODO:
# * Hide from and to, default to 0x,... and base 10, so one of the bases can always be implicit (from or to)
# * Never asssume smth is flag, unless fully match the flag, has " to force number be a number (check for " not be in digits)
# * Digits passing by param optional (using flag)
# * Type check and beautify but dont use a 3rd party if it doesnt match the purpose of the project
# * In help ensure user knows about the syntax of numbers and stuff

# ------- Setup -------
console = Console()

def create_help_table() -> Table:
    """Create a beautiful help table using rich."""
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan")
    table.add_column("Description", style="green")

    # Required arguments
    table.add_row(
        "--value",
        "The number to convert (required if not using positional arguments)"
    )
    table.add_row(
        "--from",
        "Source base (2-36). If not specified, inferred from number prefix (0b=2, 0o=8, 0x=16) or default to 10"
    )
    table.add_row(
        "--to",
        "Target base (2-36). If not specified, defaults to 10"
    )

    # Optional arguments
    table.add_row(
        "--digits",
        f"By defaults, digits are {RadixNumber._DEFAULT_DIGITS} by order of value, but user can set custom digit set. By default, digits are case-insensitive, but if custom digits contain both upper and lower case alphabets, digits would be assumed to be case-sensitive."
    )
    table.add_row(
        "--scientific",
        "Treat the input value as scientific notation (e.g., 1.23e4)"
    )
    table.add_row(
        "--help",
        "Show this help message"
    )

    # Additional Clarifications
    table.add_section() # Add a separator line for clarity
    table.add_row(
        "Positional Arg Order:",
        "\\[value] \\[from_base] \\[to_base]. Flags override positional arguments, and if e.g.: value is provided by a flag, first positional would be assumed to be by the order of positional, in this case, 'from base'."
    )
    table.add_row(
        "Base Inference:",
        "0b (binary), 0o (octal), Prefixes 0x (hex) automatically set the source base if --from is not used."
    )

    return table

def infer_base_implicit_from_prefix(value: str) -> tuple[bool, int | None]:
    """
    Check if the value has an implicit base prefix (0x, 0b, 0o).
    Returns a tuple of (has_prefix, base) where base is:
    - 2 for 0b/0B
    - 8 for 0o/0O
    - 16 for 0x/0X
    - None if no valid prefix
    """
    import re
    match = re.match(r"[-+]?0([xboXBO])(.*)", value)
    if not match:
        return False, None

    prefix = match.group(1).lower()
    if prefix == "b":
        return True, 2
    elif prefix == "o":
        return True, 8
    elif prefix == "x":
        return True, 16
    return False, None

def show_help_and_exit():
    """Show help and exit with error code."""
    console.print(Panel(create_help_table(), title="[bold blue]RadixHopper Help[/]", border_style="blue"))
    sys.exit(1)

class RadixHopperError(Exception):
    """Base exception for RadixHopper CLI errors."""
    pass

def parse_args() -> Dict[str, Any]:
    """
    Parse command line arguments with strict flag handling.
    Returns a dictionary of parsed arguments.
    """
    implicit_single = False
    order = ["value", "base", "_base_to"]
    result = {
        "value": None,
        "base": None,
        "_base_to": None,
        "digits": None,
        "is_scientific_notation_str": False,
    }
    seen_flags = set()  # Track which flags we've seen
    args = sys.argv[1:]

    if not args:
        raise RadixHopperError("No arguments provided")

    if "--help" in args:
        console.print(Panel(create_help_table(), title="[bold blue]RadixHopper Help[/]", border_style="blue"))
        sys.exit(0)

    if "--scientific" in args:
        result["is_scientific_notation_str"] = True
        args.remove("--scientific")

    # First pass: collect all flags to check for duplicates
    for arg in args:
        if arg.startswith("--"):
            if arg in seen_flags:
                raise RadixHopperError(f"Flag {arg} provided multiple times")
            seen_flags.add(arg)

    # Process named arguments first (higher priority)
    i = 0
    while i < len(args):
        arg = args[i]
        # Handle named arguments
        if arg.startswith("--"):
            if arg == "--value":
                if i + 1 >= len(args):
                    raise RadixHopperError("Missing value for --value")
                result["value"] = args[i + 1]
                i += 1
            elif arg == "--from":
                if i + 1 >= len(args):
                    raise RadixHopperError("Missing value for --from")
                try:
                    result["base"] = int(args[i + 1])
                except ValueError:
                    raise RadixHopperError("Base must be an integer")
                i += 1
            elif arg == "--to":
                if i + 1 >= len(args):
                    raise RadixHopperError("Missing value for --to")
                try:
                    result["_base_to"] = int(args[i + 1])
                except ValueError:
                    raise RadixHopperError("Base must be an integer")
                i += 1
            elif arg == "--digits":
                if i + 1 >= len(args):
                    raise RadixHopperError("Missing value for --digits")
                result["digits"] = args[i + 1]
                if set(result["digits"].upper()) != set(result["digits"]):
                    result["case_sensitive"] = True

                print(args[i], args[i+1])
                i += 1
            else:
                raise RadixHopperError(f"Unknown flag: {arg}")
        i += 1

    # Then process positional arguments (lower priority)
    i = 0
    while i < len(args):
        arg = args[i]
        if not arg.startswith("--"):
            # Handle positional arguments
            if result["value"] is None:
                result["value"] = arg
            elif result["base"] is None:
                if result["_base_to"] is None and result["base"] is None:
                    implicit_single = True
                try:
                    result["base"] = int(arg)
                except ValueError:
                    raise RadixHopperError("Base must be an integer")
            elif result["_base_to"] is None:
                implicit_single = False
                try:
                    result["_base_to"] = int(arg)
                except ValueError:
                    raise RadixHopperError("Base must be an integer")
            else:
                raise RadixHopperError(f"Unexpected argument: {arg}")
        else:
            i += 1
        i += 1


    # Validate required arguments
    if result["value"] is None:
        raise RadixHopperError("Missing required argument: value")

    inferable_from_base, inferred_base = infer_base_implicit_from_prefix(result["value"])

    if result["base"] and inferred_base:
        raise RadixHopperError("Cannot specify both explicit base and use implicit base prefix")

    if not inferable_from_base:
        if implicit_single:
            raise RadixHopperError("Ambiguous input: two values provided but unclear if second value is source base or target base. Please use --from or --to to specify, or, provide both.")

    # Handle base inference
    if result["base"] is None:
        # If no --from specified, infer from prefix
        if inferable_from_base:
            result["zero_b_o_x_leading_implicit_based"] = True
            result["is_scientific_notation_str"] = False
            result["base"] = 10
        else:
            if implicit_single:
                raise RadixHopperError("Ambigous input: two value is entered but its unclear the 2nd one is base from or base to")


    # If no --to specified, default to 10

    if result["_base_to"] is None and result["base"] is None:
        raise RadixHopperError("No base provided")

    if result["_base_to"] is None:
        result["_base_to"] = 10

    if result["base"] is None:
        result["base"] = 10

    # Validate base ranges
    if not (2 <= result["base"] <= 36):
        raise RadixHopperError(f"Source base must be between 2 and 36, got {result['base']}")
    if not (2 <= result["_base_to"] <= 36):
        raise RadixHopperError(f"Target base must be between 2 and 36, got {result['_base_to']}")

    if result["digits"] is None:
        result["digits"] = RadixNumber._DEFAULT_DIGITS

    return result

def app():
    """
    Main conversion function with rich formatting and error handling.
    """
    try:
        # Parse arguments
        args = parse_args()
        to = args["_base_to"]
        del args["_base_to"]

        # Create RadixNumber with appropriate settings
        radix_num = RadixNumber(
            **args
        )

        # Convert to target base
        result = radix_num.to(base=to).representation_value

        # --- Rich Formatting ---
        sign, int_, frac, frac_rep = RadixNumber.normalized_str_to_str_particles_and_check(result)
        formatted_result = Text()
        formatted_result.append("-") if (sign == -1) else None
        formatted_result.append(int_, style="bold green")
        if frac or frac_rep:
            formatted_result.append(".")
        formatted_result.append(frac, style="bold green")
        formatted_result.append(frac_rep, style="bold cyan overline")

        # Create a panel with conversion details
        details = Table.grid(padding=1)
        details.add_row("Input:", args["value"])
        details.add_row("From Base:", str(args["base"]))
        details.add_row("To Base:", str(to))
        if args["digits"] is not None:
            details.add_row("Custom Digits:", args["digits"])

        console.print(Panel(
            details,
            title="[bold blue]Conversion Details[/]",
            border_style="blue"
        ))

        console.print(Panel(
            formatted_result,
            title="[bold green]Result[/]",
            border_style="green"
        ))

    except RadixHopperError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        # console.print_exception(show_locals=False) # TODO test
        show_help_and_exit()
    except ValueError as ve:
        console.print(f"[bold red]Error:[/bold red] {str(ve)}")
        # console.print_exception(show_locals=False) # TODO test
        show_help_and_exit()
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}")
        console.print_exception(show_locals=False)
        show_help_and_exit()

if __name__ == "__main__":
    app()
