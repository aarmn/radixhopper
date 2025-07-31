from typing import Any

try:
    from rich.console import Console
    from rich.traceback import install
    install(show_locals=True)
    console = Console()
except Exception:
    pass

class RadixError(Exception):
    """Base exception class for RadixNumber errors with rich formatting support"""
    def __init__(self, message: str, context: dict[str, Any] | None = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)

    def __rich__(self):
        """Rich console protocol support for better error presentation"""
        from rich.panel import Panel
        from rich.table import Table

        error_panel = Panel(
            self.message,
            title=f"[red]{self.__class__.__name__}[/red]",
            border_style="red"
        )

        if self.context:
            context_table = Table(show_header=False)
            context_table.add_column("Key", style="bold cyan")
            context_table.add_column("Value")

            for key, value in self.context.items():
                context_table.add_row(str(key), str(value))

            return f"{error_panel}\n\n{context_table}"

        return error_panel

class BaseRangeError(RadixError):
    """Raised when the base is outside the valid range."""
    def __init__(self, message: str, base: int | None = None):
        super().__init__(
            message,
            {"base": base} if base is not None else None
        )

class DigitError(RadixError):
    """Raised when an invalid digit is used for the given base."""
    def __init__(self, message: str, digit: str | None = None, base: int | None = None):
        super().__init__(
            message,
            {
                "digit": digit,
                "base": base
            } if digit and base else None
        )

class ParseError(RadixError):
    """Raised when the string representation cannot be parsed."""
    def __init__(self, message: str, value: str | None = None):
        super().__init__(
            message,
            {"value": value} if value is not None else None
        )
