"""
Overview section models — Product information and Manufacturer.
Maps to ontology Data_ontology rows: Overview section.
"""

from typing import Optional

from pydantic import BaseModel, Field

from .common import ExtractedField


class ProductInfo(BaseModel):
    """General product information — required and optional fields."""
    product_name: ExtractedField[str] = Field(default_factory=ExtractedField)
    product_image: ExtractedField[str] = Field(default_factory=ExtractedField)
    product_description: ExtractedField[str] = Field(default_factory=ExtractedField)
    uid: ExtractedField[str] = Field(default_factory=ExtractedField)
    item_type: ExtractedField[str] = Field(default_factory=ExtractedField)
    product_family: ExtractedField[str] = Field(default_factory=ExtractedField)
    product_family_code: ExtractedField[str] = Field(default_factory=ExtractedField)
    intended_use: ExtractedField[str] = Field(default_factory=ExtractedField)
    # Optional fields
    serial_number: ExtractedField[str] = Field(default_factory=ExtractedField)
    batch_number: ExtractedField[str] = Field(default_factory=ExtractedField)
    gtin: ExtractedField[str] = Field(default_factory=ExtractedField)
    functional_unit: ExtractedField[str] = Field(default_factory=ExtractedField)
    standard_dimension: ExtractedField[str] = Field(default_factory=ExtractedField)
    weight: ExtractedField[str] = Field(default_factory=ExtractedField)
    production_period: ExtractedField[str] = Field(default_factory=ExtractedField)


class Manufacturer(BaseModel):
    """Manufacturer / company information."""
    company_name: ExtractedField[str] = Field(default_factory=ExtractedField)
    company_description: ExtractedField[str] = Field(default_factory=ExtractedField)
    address: ExtractedField[str] = Field(default_factory=ExtractedField)
    website: ExtractedField[str] = Field(default_factory=ExtractedField)
    manufacturing_site: ExtractedField[str] = Field(default_factory=ExtractedField)
    email: ExtractedField[str] = Field(default_factory=ExtractedField)
    phone: ExtractedField[str] = Field(default_factory=ExtractedField)
    sale_type: ExtractedField[str] = Field(default_factory=ExtractedField)


class OverviewSection(BaseModel):
    """Complete Overview section of the DPP."""
    product_info: ProductInfo = Field(default_factory=ProductInfo)
    manufacturer: Manufacturer = Field(default_factory=Manufacturer)
