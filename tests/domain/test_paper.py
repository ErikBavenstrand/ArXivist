from datetime import date

from arxivist.domain import Category, Paper


class TestPaper:
    def test_init(self) -> None:
        arxiv_id = "2101.00001v1"
        title = "Sample Paper"
        abstract = "This is a sample abstract."
        published_at = date(2025, 1, 1)
        categories = {Category("cs", "CV")}
        paper = Paper(
            arxiv_id=arxiv_id,
            title=title,
            abstract=abstract,
            published_at=published_at,
            categories=categories,
        )
        assert paper.arxiv_id == arxiv_id
        assert paper.title == title
        assert paper.abstract == abstract
        assert paper.published_at == published_at
        assert paper.categories == categories

    def test_multi_category(self) -> None:
        arxiv_id = "2101.00001v1"
        title = "Sample Paper"
        abstract = "This is a sample abstract."
        published_at = date(2025, 1, 1)
        categories = {Category("cs", "CV"), Category("cs", "CL")}
        paper = Paper(
            arxiv_id=arxiv_id,
            title=title,
            abstract=abstract,
            published_at=published_at,
            categories=categories,
        )
        assert paper.arxiv_id == arxiv_id
        assert paper.title == title
        assert paper.abstract == abstract
        assert paper.published_at == published_at
        assert paper.categories == categories

    def test_no_categories(self) -> None:
        arxiv_id = "2101.00001v1"
        title = "Sample Paper"
        abstract = "This is a sample abstract."
        published_at = date(2025, 1, 1)
        paper = Paper(
            arxiv_id=arxiv_id,
            title=title,
            abstract=abstract,
            published_at=published_at,
        )
        assert paper.arxiv_id == arxiv_id
        assert paper.title == title
        assert paper.abstract == abstract
        assert paper.published_at == published_at
        assert paper.categories == set()

    def test_url_properties(self) -> None:
        arxiv_id = "2101.00001v1"
        paper = Paper(
            arxiv_id=arxiv_id,
            title="Sample Paper",
            abstract="This is a sample abstract.",
            published_at=date(2025, 1, 1),
        )

        assert paper.summary_url == f"https://arxiv.org/abs/{arxiv_id}"
        assert paper.pdf_url == f"https://arxiv.org/pdf/{arxiv_id}"
        assert paper.html_url == f"https://arxiv.org/html/{arxiv_id}"


class TestCategory:
    def test_init(self) -> None:
        category = Category("cs", "CV")
        assert category.major == "cs"
        assert category.minor == "CV"

    def test_init_no_minor(self) -> None:
        category = Category("cs")
        assert category.major == "cs"
        assert category.minor is None

    def test_str_init(self) -> None:
        category = Category.from_string("cs.CV")
        assert category.major == "cs"
        assert category.minor == "CV"

    def test_str_init_no_minor(self) -> None:
        category = Category.from_string("cs")
        assert category.major == "cs"
        assert category.minor is None

    def test_category_equality(self) -> None:
        category1 = Category("cs", "CV")
        category2 = Category("cs", "CV")
        assert category1 == category2

    def test_category_hash_equality(self) -> None:
        category1 = Category("cs", "CV")
        category2 = Category("cs", "CV")
        assert hash(category1) == hash(category2)

    def test_category_repr(self) -> None:
        category = Category("cs", "CV")
        assert repr(category) == "Category(major='cs', minor='CV')"

    def test_category_str(self) -> None:
        category = Category("cs", "CV")
        assert str(category) == "cs.CV"
