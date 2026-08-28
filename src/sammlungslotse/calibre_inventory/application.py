"""Application service for one explicit inventory provider."""

from __future__ import annotations

from .model import CalibreInventoryReport
from .ports import CalibreInventoryPort


class CalibreInventoryService:
    def project(self, provider: CalibreInventoryPort) -> CalibreInventoryReport:
        return provider.project()
