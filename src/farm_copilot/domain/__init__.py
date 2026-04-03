"""Domain layer barrel exports."""

from .entities import (
    CanonicalProduct,
    Farm,
    Invoice,
    InvoiceLineItem,
    InvoiceWithLineItems,
    ProductAlias,
    Supplier,
    UploadedDocument,
)
from .enums import (
    BenchmarkSourceKind,
    CorrectionKind,
    InvoiceStatus,
    LineClassification,
    SourceType,
    StockMovementDirection,
)
from .money import (
    deviation_percent,
    exceeds,
    is_negative,
    is_zero_or_negative,
    median,
    money_abs_diff,
    money_add,
    money_mul,
    money_sub,
    money_within_tolerance,
    to_decimal,
)
from .primitives import UUID, DecimalValue, IsoDateString, IsoTimestampString

__all__ = [
    # Entities
    "Farm",
    "Supplier",
    "UploadedDocument",
    "Invoice",
    "InvoiceLineItem",
    "CanonicalProduct",
    "ProductAlias",
    "InvoiceWithLineItems",
    # Enums
    "SourceType",
    "InvoiceStatus",
    "LineClassification",
    "BenchmarkSourceKind",
    "StockMovementDirection",
    "CorrectionKind",
    # Primitives
    "UUID",
    "DecimalValue",
    "IsoDateString",
    "IsoTimestampString",
    # Money
    "to_decimal",
    "money_add",
    "money_sub",
    "money_mul",
    "money_abs_diff",
    "money_within_tolerance",
    "is_negative",
    "is_zero_or_negative",
    "exceeds",
    "median",
    "deviation_percent",
]
