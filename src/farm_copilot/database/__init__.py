"""Database package — models, session factory, and query helpers."""

from .benchmark_observations import (
    insert_benchmark_observation,
    insert_benchmark_observations_batch,
    list_benchmark_observations,
    list_benchmark_observations_by_provenance,
)
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
from .line_corrections import (
    insert_line_correction,
    list_line_corrections_by_line_item_id,
)
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
from .normalization_lookup import list_exact_normalization_candidates
from .product_aliases import (
    list_precedence_ordered_visible_aliases,
    list_product_aliases_by_alias_text,
    list_product_aliases_by_canonical_product_id,
    list_visible_product_aliases_by_alias_text,
)
from .session import async_session, get_db, get_engine
from .stock_movements import (
    insert_stock_movement_idempotent,
    list_stock_movements_by_invoice_id,
)

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
    # Query helpers — product aliases
    "list_product_aliases_by_canonical_product_id",
    "list_product_aliases_by_alias_text",
    "list_visible_product_aliases_by_alias_text",
    "list_precedence_ordered_visible_aliases",
    # Query helpers — normalization lookup
    "list_exact_normalization_candidates",
    # Query helpers — benchmark observations
    "insert_benchmark_observation",
    "insert_benchmark_observations_batch",
    "list_benchmark_observations",
    "list_benchmark_observations_by_provenance",
    # Query helpers — stock movements
    "insert_stock_movement_idempotent",
    "list_stock_movements_by_invoice_id",
    # Query helpers — line corrections
    "insert_line_correction",
    "list_line_corrections_by_line_item_id",
]

