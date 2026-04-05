from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PropertyType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    PLOT = "plot"
    COMMERCIAL = "commercial"
    SHOP = "shop"
    OFFICE = "office"


class Purpose(str, Enum):
    BUY = "buy"
    RENT = "rent"


class SearchPropertiesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    city: Optional[str] = Field(
        default=None, min_length=1, max_length=50, description="City name (e.g. Lahore, Karachi, Islamabad)"
    )
    area: Optional[str] = Field(
        default=None, min_length=1, max_length=100, description="Locality or society, fuzzy-matched (e.g. DHA Phase 6)"
    )
    bedrooms: Optional[int] = Field(
        default=None, ge=1, le=10, description="Minimum number of bedrooms"
    )
    budget_min: Optional[int] = Field(
        default=None, ge=0, description="Minimum price in PKR"
    )
    budget_max: Optional[int] = Field(
        default=None, ge=0, description="Maximum price in PKR"
    )
    property_type: Optional[PropertyType] = Field(
        default=None, description="Type of property"
    )
    purpose: Optional[Purpose] = Field(
        default=None, description="Buy or rent"
    )
    size_min: Optional[int] = Field(
        default=None, ge=1, description="Minimum size in marla"
    )
    size_max: Optional[int] = Field(
        default=None, ge=1, description="Maximum size in marla"
    )
    limit: int = Field(default=10, ge=1, le=20, description="Number of results to return")
    offset: int = Field(default=0, ge=0, description="Pagination offset")

    @model_validator(mode="after")
    def validate_ranges(self) -> "SearchPropertiesInput":
        if self.budget_min is not None and self.budget_max is not None and self.budget_max < self.budget_min:
            raise ValueError("budget_max must be >= budget_min")
        if self.size_min is not None and self.size_max is not None and self.size_max < self.size_min:
            raise ValueError("size_max must be >= size_min")
        return self


class GetPropertyDetailsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    property_id: str = Field(..., min_length=1, description="Property ID from search results")
