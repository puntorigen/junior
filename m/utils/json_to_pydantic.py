from pydantic import BaseModel, Field, create_model
from typing import List, Dict, Type, Any
import json

# type: ignore

def parse_field_type(type_str: str) -> Type:
    """
    Parse a string representing a Python type into an actual type.
    Handles cases where no specific type is provided, defaulting to str.
    """
    if ':' in type_str:
        type_name = type_str.split(':')[1]
        if type_name.startswith("List"):
            inner_type = type_name.split("[")[1].rstrip("]")
            return List[eval(inner_type)]
        return eval(type_name)
    return str  # Default to str if no type is specified

def generate_pydantic_model(data: Dict[str, str]) -> type(BaseModel): # type: ignore
    """
    Generate a Pydantic model class dynamically based on the input dictionary (JSON).
    Keys without type hints default to str.
    """
    fields = {}
    for key, description in data.items():
        # Check if field name contains a type hint
        if ':' in key:
            field_name, field_type_str = key.split(':')
            field_type = parse_field_type(field_type_str)
        else:
            field_name = key
            field_type = str  # Default type

        # Create the field with the type and description
        fields[field_name] = (field_type, Field(..., description=description))

    # Create the model class
    return create_model('GeneratedModel', **fields)
