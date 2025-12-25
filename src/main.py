import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
import os
import sys

# Add the project root to sys.path to allow imports if we expand structure
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

console = Console()

@click.command()
@click.option('--destination', '-d', help='The destination of the trip')
@click.option('--dates', '-t', help='The dates of the trip')
def main(destination, dates):
    """
    AI-Driven Year End Trip Advisor
    """
    console.print(Panel("[bold blue]Year End Trip Advisor[/bold blue]", subtitle="Planning Helper"))

    if not destination:
        destination = Prompt.ask("[green]Where are you planning to go?[/green]", default="Undecided")
        
    if not dates:
        dates = Prompt.ask("[green]When are you planning to go?[/green]", default="Dec 2025")

    console.print(f"\n[bold]Current Plan Context:[/bold]")
    console.print(f"Destination: [cyan]{destination}[/cyan]")
    console.print(f"Dates: [cyan]{dates}[/cyan]")
    
    # Simple integration of the new search module
    from src.search import TripSearch
    
    if destination.lower() == "undecided" or destination.lower() == "search":
        searcher = TripSearch(origin="ATL")
        console.print("\n[bold yellow]Searching for options...[/bold yellow]")
        
        console.print("\n[bold]🚗 Driving Ideas:[/bold]")
        drive_opts = searcher.search_drive_options()
        for opt in drive_opts:
            console.print(f"- [green]{opt['dest']}[/green] ({opt['drive_time']}): {opt['notes']}")

        console.print("\n[bold]✈️ Flight Ideas (Mock Data):[/bold]")
        flight_opts = searcher.search_flights(dates, dates) # simplifying dates for now
        for opt in flight_opts:
            console.print(f"- [cyan]{opt['dest']}[/cyan] ~ {opt['price']}: {opt['notes']}")

    console.print("\n[dim]Advisor logic not yet implemented...[/dim]")

if __name__ == '__main__':
    main()
