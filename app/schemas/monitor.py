from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
    BeforeValidator
)
from typing import Annotated, Any
from typing_extensions import Self

class MonitorCreate(BaseModel):
    name: str | None = Field(default = None, max_length=64)
    url: HttpUrl
    check_interval_seconds : int = Field(default = 60, ge=5, le=3600)
    timeout_seconds : int = Field(default = 5, ge=1)
    expected_status_code : int = Field(default = 200, ge = 200, le = 599)
    is_enabled : bool = True

    @field_validator('name', mode='before')
    @classmethod
    def ensure_name(cls, value : Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            return value
        return value

    @model_validator(mode = 'after')
    def validate_timeout_before_interval(self)-> Self:
        if self.timeout_seconds >= self.check_interval_seconds:
            raise ValueError('timeout_seconds must be less than check_interval_seconds.')
        return self

