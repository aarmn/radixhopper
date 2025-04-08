import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from radixhopper import RadixNumber

# ------- Setup -------
console = Console()
app = typer.Typer(
    help="A CLI tool to convert numbers between different bases (radices)."
) # Create a Typer application instance

# ------- Core -------
@app.command()
def convert_and_show(
    num: str = typer.Argument(
        ..., # Ellipsis (...) means the argument is required
        help="Number to convert (treated strictly as a string). Use quotes if needed for shell interpretation, e.g., '1.0e5' or '123.45'."
    ),
    base_from: int = typer.Argument(
        ...,
        min=2,  # Add basic validation via Typer
        max=36,
        help="Source base (integer between 2 and 36)."
    ),
    base_to: int = typer.Argument(
        ...,
        min=2,
        max=36,
        help="Target base (integer between 2 and 36)."
    )
):
    """
    Converts a number represented as a STRING between different bases.

    Typer ensures 'num' is passed as a string, and bases are integers.
    """
    try:
        radix_num = RadixNumber(num, base_from)
        result = radix_num.to(base=base_to).representation_value
        # console.print(f"Raw result: {result}", style="dim") # Optional: raw result debug

        # --- Rich Formatting ---
        int_, frac, frac_rep = RadixNumber.normalized_str_to_str_particles_and_check(result)
        formatted_result = Text()
        formatted_result.append(int_, style="bold green") # Added some color
        if frac or frac_rep:
            formatted_result.append(".")
        formatted_result.append(frac, style="bold green") # Added some color
        # Using a distinct style for repeating part
        formatted_result.append(frac_rep, style="bold cyan overline")

        console.print(Panel(formatted_result, title="[bold green]Conversion Result[/]", expand=False, border_style="green"))

    except ValueError as ve:
        # Catch potential errors from RadixNumber (e.g., invalid digit for base)
        console.print(f"[bold red]Input Error:[/bold red] {str(ve)}")
        raise typer.Exit(code=1) # Exit with a non-zero code to indicate failure
    except Exception as e:
        # Catch any other unexpected errors
        console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}")
        # Keep traceback for debugging if needed, but hide locals for cleaner output
        console.print_exception(show_locals=False)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app() # Run the Typer application
