"""Database package — models, session factory, and query helpers."""

from .canonical_products import get_canonical_product_by_id, list_canonical_products
from .invoice_duplicate_candidates import list_invoice_duplicate_candidates
from .invoice_extraction import (
    get_invoice_for_extraction_by_id,
    update_invoice_extraction,
)
from .invoice_intake import (
    get_invoice_shell_by_id,
    get_uploaded_document_by_id,
    insert_invoice_shell,
    insert_uploaded_document,
)
from .invoice_line_classification import update_invoice_line_item_classification
from .invoice_line_items import (
    get_invoice_line_item_by_id,
    get_invoice_line_items_by_invoice_id,
    replace_invoice_extracted_line_items,
)
from .invoice_line_normalization import update_invoice_line_item_normalization
from .invoice_status import update_invoice_status
from .models import (
    Base,
    BenchmarkObservation,
    BenchmarkSourceKind,
    CanonicalProduct,
    CorrectionKind,
    Farm,
    Invoice,
    InvoiceLineItem,
    InvoiceStatus,
    LineClassification,
    LineCorrection,
    ProductAlias,
    SourceType,
    StockMovement,
    StockMovementDirection,
    Supplier,
    UploadedDocument,
)
from .session import async_session, get_db, get_engine

__all__ = [
    # Base
    "Base",
    # Enums
    "SourceType",
    "InvoiceStatus",
    "LineClassification",
    "BenchmarkSourceKind",
    "StockMovementDirection",
    "CorrectionKind",
    # Models
    "Farm",
    "Supplier",
    "UploadedDocument",
    "Invoice",
    "CanonicalProduct",
    "InvoiceLineItem",
    "ProductAlias",
    "BenchmarkObservation",
    "StockMovement",
    "LineCorrection",
    # Session
    "get_db",
    "get_engine",
    "async_session",
    # Query helpers — invoice intake
    "insert_uploaded_document",
    "insert_invoice_shell",
    "get_invoice_shell_by_id",
    "get_uploaded_document_by_id",
    # Query helpers — invoice extraction
    "get_invoice_for_extraction_by_id",
    "update_invoice_extraction",
    # Query helpers — invoice line items
    "replace_invoice_extracted_line_items",
    "get_invoice_line_items_by_invoice_id",
    "get_invoice_line_item_by_id",
    # Query helpers — invoice status
    "update_invoice_status",
    # Query helpers — invoice line classification
    "update_invoice_line_item_classification",
    # Query helpers — invoice line normalization
    "update_invoice_line_item_normalization",
    # Query helpers — invoice duplicate candidates
    "list_invoice_duplicate_candidates",
    # Query helpers — canonical products
    "get_canonical_product_by_id",
    "list_canonical_products",
]

