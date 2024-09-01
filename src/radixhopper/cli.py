import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from radixhopper import BaseConverter, ConversionInput, ConversionError

console = Console()

@click.command()
@click.option('--num', prompt='Enter number to convert', help='Number to convert')
@click.option('--base-from', type=int, prompt='Enter base to convert from', help='Base to convert from')
@click.option('--base-to', type=int, prompt='Enter base to convert to', help='Base to convert to')
def convert(num, base_from, base_to):
    try:
        input_data = ConversionInput(num=num, base_from=base_from, base_to=base_to)
        result = BaseConverter.base_convert(input_data)
        
        if '[' in result and ']' in result:
            parts = result.split('[')
            non_repeating = parts[0]
            repeating = parts[1].strip(']')
            formatted_result = Text()
            formatted_result.append(non_repeating)
            formatted_result.append(repeating, style="overline")
        else:
            formatted_result = result

        panel = Panel(formatted_result, title="Conversion Result", expand=False)
        console.print(panel)
    except ConversionError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    except Exception as e:
        console.print("[bold red]An unexpected error occurred. Please check your input and try again.[/bold red]")

if __name__ == '__main__':
    convert()