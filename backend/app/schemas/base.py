from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Base schema for all request and response models.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )
