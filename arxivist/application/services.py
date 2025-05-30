from tqdm.auto import tqdm

from arxivist.application.ports.arxiv_extractor import AbstractArXivCategoryExtractor, PaperDTO
from arxivist.application.ports.persistence.unit_of_work import AbstractUnitOfWork
from arxivist.domain import model
from arxivist.infrastructure.arxiv_extractor import AbstractArXivPaperExtractor


class NoCategoriesError(Exception):
    """Exception raised when no categories are found in the repository."""

    def __init__(self) -> None:
        """Initializes the `NoCategoriesError` exception."""
        super().__init__("No categories found in the repository.")


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
            identifier=model.CategoryIdentifier(archive=category.archive, subcategory=category.subcategory),
            archive_name=category.archive_name,
            category_name=category.category_name,
            description=category.description,
        )
        for category in category_dtos
    ]

    with uow:
        uow.papers.upsert_categories(categories)
        uow.commit()

    return categories


def _resolve_categories(categories: list[str] | None, uow: AbstractUnitOfWork) -> list[model.CategoryIdentifier]:
    """Resolves the categories to be used for fetching papers.

    If `categories` is None, it fetches all archives (top-level categories) from the repository.

    Args:
        categories: A list of category strings to filter the papers by, (e.g., ["cs.AI", "math.ST"]).
        uow: The unit of work to manage repository transactions.

    Raises:
        NoCategoriesError: If `categories` is None and no categories are found in the repository.

    Returns:
        A list of `CategoryIdentifier` domain objects representing the categories to be used for fetching papers.
    """
    if categories is not None:
        return [model.CategoryIdentifier.from_string(category) for category in categories]

    category_identifiers = [category.identifier for category in uow.papers.list_categories(limit=None)]
    if not category_identifiers:
        raise NoCategoriesError

    return category_identifiers


def _should_split_categories(
    result: list[PaperDTO],
    category_identifiers: list[model.CategoryIdentifier],
    arxiv_paper_extractor: AbstractArXivPaperExtractor,
) -> bool:
    """Checks if the categories should be split based on the result and category identifiers.

    Args:
        result: A list of `PaperDTO` objects representing the papers fetched from the extractor.
        category_identifiers: A list of `CategoryIdentifier` domain objects representing the categories to be
            used for fetching papers.
        arxiv_paper_extractor: The paper extractor to fetch papers from.

    Returns:
        True if the categories should be split, False otherwise.
    """
    return len(result) == arxiv_paper_extractor.limit and (
        len(category_identifiers) >= 2
        or (len(category_identifiers) == 1 and category_identifiers[0].subcategory is None)
    )


def _split_categories(
    category_identifiers: list[model.CategoryIdentifier],
    uow: AbstractUnitOfWork,
) -> list[list[model.CategoryIdentifier]]:
    """Splits the list of category identifiers into two halves or a list of subcategories.

    Args:
        category_identifiers: A list of `CategoryIdentifier` domain objects representing the categories to be
            used for fetching papers.
        uow: The unit of work to manage repository transactions.

    Returns:
        A list of lists of `CategoryIdentifier` domain objects representing the split categories.
    """
    if len(category_identifiers) >= 2:
        mid = len(category_identifiers) // 2
        return [category_identifiers[:mid], category_identifiers[mid:]]

    subcategories = uow.papers.get_subcategories(category_identifiers[0].archive)
    return [[subcategory.identifier for subcategory in subcategories]] if subcategories else []


def _fetch_papers_with_progress(
    category_identifiers: list[model.CategoryIdentifier],
    arxiv_paper_extractor: AbstractArXivPaperExtractor,
    uow: AbstractUnitOfWork,
) -> set[PaperDTO]:
    """Fetches papers from the ArXiv extractor with a progress bar.

    Args:
        category_identifiers: A list of `CategoryIdentifier` domain objects representing the categories to be
            used for fetching papers.
        arxiv_paper_extractor: The paper extractor to fetch papers from.
        uow: The unit of work to manage repository transactions.

    Returns:
        A set of `PaperDTO` objects representing the papers fetched from the extractor.
    """
    category_identifiers_queue = [category_identifiers]
    pbar = tqdm(total=len(category_identifiers_queue), desc="Fetching latest papers from ArXiv")
    paper_dtos: set[PaperDTO] = set()

    while category_identifiers_queue:
        category_identifiers = category_identifiers_queue.pop(0)
        result = arxiv_paper_extractor.fetch_latest_papers(category_identifiers)

        if _should_split_categories(result, category_identifiers, arxiv_paper_extractor):
            new_category_identifiers = _split_categories(category_identifiers, uow)
            category_identifiers_queue.extend(new_category_identifiers)
            pbar.total += len(new_category_identifiers)
            pbar.refresh()

        paper_dtos.update(result)
        pbar.update(1)

    pbar.close()
    return paper_dtos


def fetch_and_store_latest_papers(
    categories: list[str] | None,
    arxiv_paper_extractor: AbstractArXivPaperExtractor,
    uow: AbstractUnitOfWork,
) -> list[model.Paper]:
    """Fetches the latest papers from the ArXiv extractor and stores them in the repository.

    It also enriches the categories of the papers with the ones stored in the repository, if they exist.
    Otherwise, it creates new categories and stores them in the repository.

    Args:
        categories: A list of category strings to filter the papers by, (e.g., ["cs.AI", "math.ST"]).
            If None, fetches papers from all categories.
        arxiv_paper_extractor: The paper extractor to fetch papers from.
        uow: The unit of work to manage repository transactions.

    Raises:
        PaperMissingFieldError: If a required field is missing in the paper.
        NoCategoriesError: If `categories` is None and no categories are found in the repository.

    Returns:
        A list of `Paper` domain objects representing the papers fetched from the extractor.
    """
    with uow:
        category_identifiers = _resolve_categories(categories, uow)
        paper_dtos = _fetch_papers_with_progress(category_identifiers, arxiv_paper_extractor, uow)

        enriched_category_mapping = {
            category_str: uow.papers.get_category(model.CategoryIdentifier.from_string(category_str))
            or model.Category(identifier=model.CategoryIdentifier.from_string(category_str))
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
        uow.papers.upsert_papers(papers)
        uow.commit()

    return papers
