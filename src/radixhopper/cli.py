import fire
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from radixhopper import BaseConverter, ConversionInput, ConversionError

console = Console()

def convert(num, base_from, base_to):
    try:
        input_data = ConversionInput(num=str(num), base_from=base_from, base_to=base_to)
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
        console.print(f"[bold red]An unexpected error occurred. Please check your input and try again. Details:[/bold red]\n{str(e)}")

def main():
    fire.Fire(convert)

if __name__ == '__main__':
    main()