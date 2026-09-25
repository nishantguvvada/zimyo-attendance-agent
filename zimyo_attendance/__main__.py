"""Main entry point for Zimyo Attendance Logger."""
import sys
import argparse
from datetime import datetime

from zimyo_attendance.agent.graph import run_attendance_agent
from zimyo_attendance.config.settings import get_settings
from zimyo_attendance.storage.json_file import create_storage
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def print_banner():
    """Print application banner."""
    console.print(Panel.fit(
        "[bold cyan]Zimyo Attendance Logger[/bold cyan]\n"
        "Automated clock in/out with LangGraph agent",
        border_style="cyan"
    ))


def print_result(result: dict):
    """Print agent result with formatting."""
    if result["success"]:
        console.print(f"[green]✅ {result['result']}[/green]")
    else:
        console.print(f"[red]❌ {result['result']}[/red]")
        if result.get("error"):
            console.print(f"[red]Error: {result['error']}[/red]")


def show_history(limit: int = 10):
    """Show attendance history."""
    storage = create_storage(get_settings().storage_path)
    records = storage.get_records(limit=limit)
    
    if not records:
        console.print("[yellow]No attendance records found.[/yellow]")
        return
    
    table = Table(title="Attendance History")
    table.add_column("Date", style="cyan")
    table.add_column("Action", style="magenta")
    table.add_column("UAE Time", style="green")
    table.add_column("Status Before", style="yellow")
    table.add_column("Result", style="white")
    table.add_column("Success", justify="center")
    
    for record in records:
        success_icon = "✅" if record.get("success") else "❌"
        table.add_row(
            record.get("date", ""),
            record.get("action", ""),
            record.get("uae_time", "").split(" ")[1] if " " in record.get("uae_time", "") else "",
            record.get("status_before", ""),
            record.get("result", "")[:50] + ("..." if len(record.get("result", "")) > 50 else ""),
            success_icon
        )
    
    console.print(table)


def show_status():
    """Show current status from Zimyo."""
    from zimyo_attendance.tools.zimyo_client import create_zimyo_client
    
    client = create_zimyo_client()
    attendance = client.get_attendance_status()
    client.close()
    
    if attendance:
        console.print(Panel(
            f"[bold]Date:[/bold] {attendance.date} ({attendance.date_format})\n"
            f"[bold]Shift:[/bold] {attendance.shift_name} ({attendance.shift_code})\n"
            f"[bold]Shift Hours:[/bold] {attendance.day_start_time} - {attendance.day_end_time}\n"
            f"[bold]Punch In:[/bold] {attendance.punch_in_time or 'Not punched'}\n"
            f"[bold]Punch Out:[/bold] {attendance.punch_out_time or 'Not punched'}\n"
            f"[bold]Status:[/bold] {attendance.in_out_status}\n"
            f"[bold]Current Time:[/bold] {attendance.current_time}\n"
            f"[bold]Timezone:[/bold] {attendance.timezone}",
            title="Current Attendance Status",
            border_style="blue"
        ))
    else:
        console.print("[red]Failed to fetch attendance status[/red]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Zimyo Attendance Logger")
    parser.add_argument(
        "action",
        nargs="?",
        choices=["auto", "clock_in", "clock_out", "status", "history"],
        default="auto",
        help="Action to perform (default: auto)"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=10,
        help="Number of history records to show"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Zimyo Attendance Logger 0.1.0"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.action == "history":
        show_history(args.limit)
    elif args.action == "status":
        show_status()
    else:
        console.print(f"[bold]Action:[/bold] {args.action}")
        console.print(f"[bold]Time:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        console.print()
        
        result = run_attendance_agent(args.action)
        print_result(result)


if __name__ == "__main__":
    main()