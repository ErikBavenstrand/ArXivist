import datetime

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    String,
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


class PaperORM(Base):
    """`SQLAlchemy` ORM model representing a paper in the database."""

    __tablename__ = "paper"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    arxiv_id: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(String)
    abstract: Mapped[str] = mapped_column(String)
    published_at: Mapped[datetime.date] = mapped_column(Date)

    categories: Mapped[set["CategoryORM"]] = relationship(
        "CategoryORM",
        back_populates="paper",
        collection_class=set,
        cascade="all, delete-orphan",
    )


class CategoryORM(Base):
    """`SQLAlchemy` ORM model representing a category in the database."""

    __tablename__ = "category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("paper.id", ondelete="CASCADE"), nullable=False
    )
    major: Mapped[str] = mapped_column(String, nullable=False)
    minor: Mapped[str] = mapped_column(String, nullable=True)

    paper: Mapped["PaperORM"] = relationship("PaperORM", back_populates="categories")

    __table_args__ = (
        UniqueConstraint(
            "paper_id", "major", "minor", name="uq_category_paper_id_major_minor"
        ),
    )
