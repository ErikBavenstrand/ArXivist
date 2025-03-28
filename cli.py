import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from arxivist import config
from arxivist.application.ports.arxiv_extractor import CategoryFetchError, CategoryParseError, PaperMissingFieldError
from arxivist.application.services import fetch_and_store_categories, fetch_and_store_latest_papers
from arxivist.infrastructure.arxiv_extractor import ArXivCategoryExtractor, ArXivRSSPaperExtractor
from arxivist.infrastructure.persistence.orm import Base
from arxivist.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork

engine = create_engine(config.DATABASE_URL)
Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)

uow = SqlAlchemyUnitOfWork(session_factory)
arxiv_paper_extractor = ArXivRSSPaperExtractor()
arxiv_category_extractor = ArXivCategoryExtractor()


@click.group()
def cli() -> None:
    """ArXivist CLI."""


@cli.command()
def fetch_categories() -> None:
    """Fetch and store categories from ArXiv."""
    try:
        categories = fetch_and_store_categories(arxiv_category_extractor, uow)
    except CategoryFetchError as e:
        click.echo(f"Error fetching categories: {e}")
        return
    except CategoryParseError as e:
        click.echo(f"Error parsing categories: {e}")
        return

    click.echo(f"Fetched and stored {len(categories)} categories from ArXiv.")


@cli.command()
@click.option(
    "--categories",
    "-c",
    multiple=True,
    required=False,
    help="The categories to fetch papers from. (e.g. 'cs', 'cs.AI', ...)",
)
@click.option(
    "--all-categories",
    "-a",
    is_flag=True,
    help="Fetch papers from all available categories.",
)
def fetch_latest_papers(categories: list[str], all_categories: bool) -> None:
    """Fetch and store the latest papers from ArXiv."""
    if all_categories:
        categories = [
            "astro-ph",
            "cond-mat",
            "cs",
            "econ",
            "eess",
            "gr-qc",
            "hep-ex",
            "hep-lat",
            "hep-ph",
            "hep-th",
            "math",
            "math-ph",
            "nlin",
            "nucl-ex",
            "nucl-th",
            "physics",
            "q-bio",
            "q-fin",
            "quant-ph",
            "stat",
        ]
        click.echo(f"Fetching papers from all {len(categories)} categories.")
    elif not categories:
        click.echo("Error: You must specify either --categories or --all.", err=True)
        return
    else:
        click.echo(f"Fetching papers from {len(categories)} categories: {categories!r}")
    try:
        papers = fetch_and_store_latest_papers(
            categories=categories,
            arxiv_paper_extractor=arxiv_paper_extractor,
            uow=uow,
        )
    except PaperMissingFieldError as e:
        click.echo(f"Error fetching papers: {e}")
        return

    click.echo(f"Fetched {len(papers)} papers from ArXiv.")


if __name__ == "__main__":
    cli()
