from arxivist.application.ports.arxiv_extractor import AbstractArXivCategoryExtractor
from arxivist.application.ports.persistence.unit_of_work import AbstractUnitOfWork
from arxivist.domain import model
from arxivist.infrastructure.arxiv_extractor import AbstractArXivPaperExtractor


def fetch_and_store_categories(
    arxiv_category_extractor: AbstractArXivCategoryExtractor,
    uow: AbstractUnitOfWork,
) -> list[model.Category]:
    """Fetches categories from the ArXiv extractor and stores them in the repository.

    Args:
        arxiv_category_extractor: The category extractor to fetch categories from.
        uow: The unit of work to manage repository transactions.

    Raises:
        CategoryFetchError: If fetching categories fails.
        CategoryParseError: If parsing categories fails.

    Returns:
        A list of all `Category` domain objects fetched from the extractor.
    """
    category_dtos = arxiv_category_extractor.fetch_categories()
    categories = [
        model.Category(
            archive=category.archive,
            subcategory=category.subcategory,
            archive_name=category.archive_name,
            category_name=category.category_name,
            description=category.description,
        )
        for category in category_dtos
    ]

    with uow:
        for category in categories:
            uow.papers.upsert_category(category)
        uow.commit()

    return categories


def fetch_and_store_latest_papers(
    categories: list[str],
    arxiv_paper_extractor: AbstractArXivPaperExtractor,
    uow: AbstractUnitOfWork,
) -> list[model.Paper]:
    """Fetches the latest papers from the ArXiv extractor and stores them in the repository.

    It also enriches the categories of the papers with the ones stored in the repository, if they exist.
    Otherwise, it creates new categories and stores them in the repository.

    Args:
        categories: A list of category strings to filter the papers by, (e.g., ["cs.AI", "math.ST"]).
        arxiv_paper_extractor: The paper extractor to fetch papers from.
        uow: The unit of work to manage repository transactions.

    Raises:
        PaperMissingFieldError: If a required field is missing in the paper.

    Returns:
        A list of `Paper` domain objects representing the papers fetched from the extractor.
    """
    paper_dtos = arxiv_paper_extractor.fetch_latest_papers([
        model.Category.from_string(category) for category in categories
    ])

    with uow:
        enriched_category_mapping = {
            category_str: uow.papers.get_category(*model.Category.split_string(category_str))
            or model.Category.from_string(category_str)
            for paper_dto in paper_dtos
            for category_str in paper_dto.categories
        }

        papers = [
            model.Paper(
                arxiv_id=paper_dto.arxiv_id,
                title=paper_dto.title,
                abstract=paper_dto.abstract,
                published_at=paper_dto.published_at,
                categories=[enriched_category_mapping[category_str] for category_str in paper_dto.categories],
            )
            for paper_dto in paper_dtos
        ]

        for paper in papers:
            uow.papers.upsert_paper(paper)
        uow.commit()

    return papers
