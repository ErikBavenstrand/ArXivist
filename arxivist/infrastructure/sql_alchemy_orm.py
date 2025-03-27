import datetime

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


paper_category = Table(
    "paper_category",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("paper.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("category.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("paper_id", "category_id", name="uq_paper_category"),
)
"""`SQLAlchemy` association table for the many-to-many relationship between papers and categories."""


class CategoryORM(Base):
    """`SQLAlchemy` ORM model representing an ArXiv category in the database."""

    __tablename__ = "category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    archive: Mapped[str] = mapped_column(String, nullable=False)
    subcategory: Mapped[str | None] = mapped_column(String, nullable=True)
    archive_name: Mapped[str | None] = mapped_column(String, nullable=True)
    category_name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    papers: Mapped[list["PaperORM"]] = relationship(
        "PaperORM",
        secondary=paper_category,
        back_populates="categories",
    )

    __table_args__ = (UniqueConstraint("archive", "subcategory", name="uq_category_archive_subcategory"),)


class PaperORM(Base):
    """`SQLAlchemy` ORM model representing an ArXiv paper in the database."""

    __tablename__ = "paper"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    arxiv_id: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(String)
    abstract: Mapped[str] = mapped_column(String)
    published_at: Mapped[datetime.date] = mapped_column(Date)

    categories: Mapped[list["CategoryORM"]] = relationship(
        "CategoryORM",
        secondary=paper_category,
        back_populates="papers",
    )
