from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import fire
from radixhopper import RadixNumber

console = Console()

def convert(num: str, base_from: int, base_to: int) -> str:
    """Convert a number between different bases
    
    Args:
        num: Number to convert as string
        base_from: Source base (2-36)
        base_to: Target base (2-36)
        
    Returns:
        Converted number as string
    """
    try:
        result = RadixNumber(num, base_from).to(base=base_to).representation_value

        if '[' in result and ']' in result:
            parts = result.split('[')
            non_repeating = parts[0]
            repeating = parts[1].strip(']')
            formatted_result = Text()
            formatted_result.append(non_repeating)
            formatted_result.append(repeating, style="overline")
        else:
            formatted_result = result

        console.print(Panel(formatted_result, title="Conversion Result", expand=False))
return result
except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        console.print_exception(show_locals=True)
        return str(e)

def main():
    fire.Fire(convert)
    
if __name__ == '__main__':
    main()