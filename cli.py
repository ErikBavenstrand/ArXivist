import datetime

import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from arxivist import config
from arxivist.domain.model import Category, Paper
from arxivist.infrastructure.arxiv_rss_fetcher import ArXivRSSPaperExtractor
from arxivist.infrastructure.feedparser_rss_fetcher import FeedparserRSSClient
from arxivist.infrastructure.sql_alchemy_orm import Base
from arxivist.infrastructure.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork

engine = create_engine(config.DATABASE_URL)
Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)

uow = SqlAlchemyUnitOfWork(session_factory)
rss_client = ArXivRSSPaperExtractor(FeedparserRSSClient())


@click.group()
def cli() -> None:
    """ArXivist CLI."""


@cli.command()
def get_papers() -> None:
    """Test the CLI."""
    papers = rss_client.fetch_recent_papers({Category("cs", "CL")})
    with uow:
        for paper in papers:
            uow.papers.add(paper)
        uow.commit()


@cli.command()
def list_papers() -> None:
    """List papers."""
    with uow:
        papers = uow.papers.list(limit=10)
        for paper in papers:
            click.echo(
                f"arxiv_id={paper.arxiv_id!r} title={paper.title!r} categories={paper.categories or {}}",
            )
            click.echo(f"{paper.summary_url=}, {paper.pdf_url=}, {paper.html_url=}")
            click.echo()


@cli.command()
@click.option("--arxiv_id", "-i", required=True, help="The ArXiv ID of the paper.")
@click.option("--title", "-t", required=True, help="The title of the paper.")
@click.option("--abstract", "-a", help="The abstract of the paper.")
@click.option("--published_at", "-p", help="The date the paper was published.")
@click.option("--categories", "-c", multiple=True, help="The categories the paper belongs to.")
def add_paper(
    arxiv_id: str,
    title: str,
    abstract: str | None,
    published_at: str | None,
    categories: set[str] | None,
) -> None:
    """Add a paper."""
    abstract = abstract or ""
    published_at = published_at or str(datetime.datetime.now(tz=datetime.UTC).date())
    categories = categories or set()
    with uow:
        paper = Paper(
            arxiv_id=arxiv_id,
            title=title,
            abstract=abstract,
            published_at=datetime.date.fromisoformat(published_at),
            categories={Category(*category.split(".")[:2]) for category in categories},
        )
        uow.papers.add(paper)
        uow.commit()


if __name__ == "__main__":
    cli()
