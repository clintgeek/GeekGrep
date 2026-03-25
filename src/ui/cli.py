"""Command-line interface for geekGrep."""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path

from src.pipeline import ingest, query, get_store_info

app = typer.Typer(help="geekGrep - Intelligent document query system")
console = Console()


@app.command()
def ingest_docs(
    directory: str = typer.Argument(..., help="Directory containing documents to ingest"),
    persist_dir: str = typer.Option(
        "./data/chroma_db",
        "--persist-dir",
        "-p",
        help="Directory where vector store will be saved"
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        "-r",
        help="Clear existing vector store before ingesting"
    ),
) -> None:
    """Ingest documents from a directory into the vector store."""
    
    # Validate directory exists
    if not Path(directory).exists():
        console.print(f"[red]Error: Directory not found: {directory}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Ingesting documents from: {directory}[/cyan]")
    
    result = ingest(directory, persist_dir, reset=reset)
    
    if result["status"] == "success":
        console.print(
            Panel(
                f"[green]✓ Successfully ingested {result['documents_loaded']} documents[/green]\n"
                f"[cyan]Created {result['chunks_created']} chunks[/cyan]",
                title="Ingestion Complete",
                border_style="green"
            )
        )
    else:
        console.print(
            Panel(
                f"[red]✗ Ingestion failed[/red]\n{result['message']}",
                title="Error",
                border_style="red"
            )
        )
        raise typer.Exit(1)


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask"),
    persist_dir: str = typer.Option(
        "./data/chroma_db",
        "--persist-dir",
        "-p",
        help="Directory where vector store is saved"
    ),
    top_k: int = typer.Option(
        4,
        "--top-k",
        "-k",
        help="Number of documents to retrieve"
    ),
    backend: str = typer.Option(
        None,
        "--backend",
        "-b",
        help="LLM backend (openai or ollama)"
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="LLM model to use"
    ),
) -> None:
    """Ask a question about your documents."""
    
    # Override environment variables if provided
    import os
    if backend:
        os.environ["GEEKGREP_LLM_BACKEND"] = backend
    if model:
        os.environ["GEEKGREP_MODEL"] = model
    
    console.print(f"[cyan]Question: {question}[/cyan]\n")
    
    result = query(question, persist_dir, k=top_k)
    
    if result["status"] == "success":
        console.print(
            Panel(
                result["answer"],
                title="Answer",
                border_style="green"
            )
        )
        
        if result["sources"]:
            console.print("\n[cyan]Sources:[/cyan]")
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("File", style="green")
            table.add_column("Chunk", style="yellow")
            table.add_column("Type", style="blue")
            
            for source in result["sources"]:
                table.add_row(
                    source["filename"],
                    str(source["chunk_index"]),
                    source["file_type"]
                )
            
            console.print(table)
    else:
        console.print(
            Panel(
                f"[red]✗ Query failed[/red]\n{result['answer']}",
                title="Error",
                border_style="red"
            )
        )
        raise typer.Exit(1)


@app.command()
def info(
    persist_dir: str = typer.Option(
        "./data/chroma_db",
        "--persist-dir",
        "-p",
        help="Directory where vector store is saved"
    ),
) -> None:
    """Show information about the vector store."""
    
    result = get_store_info(persist_dir)
    
    if result["status"] == "success":
        console.print(
            Panel(
                f"[cyan]Vector Store Location:[/cyan] {result['persist_directory']}\n"
                f"[cyan]Documents Stored:[/cyan] {result['document_count']}",
                title="Store Information",
                border_style="cyan"
            )
        )
    else:
        console.print(
            Panel(
                f"[red]✗ Error[/red]\n{result['message']}",
                title="Error",
                border_style="red"
            )
        )
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
