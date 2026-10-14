import asyncio

from mcp_server import server

GENERATION_TOOLS = ("generate_cv_from_job", "generate_custom_cv", "improve_cv_short", "improve_cv_long")


def _schemas():
    tools = asyncio.run(server.mcp.list_tools())
    return {tool.name: tool.inputSchema for tool in tools}


def _allowed_values(property_schema):
    for option in property_schema.get("anyOf", [property_schema]):
        if "enum" in option:
            return set(option["enum"])
    return set()


def test_generation_tools_expose_photo_position_choices():
    schemas = _schemas()

    for name in GENERATION_TOOLS:
        prop = schemas[name]["properties"].get("photo_position")
        assert prop is not None, name
        assert _allowed_values(prop) == {"left", "right", "none"}, name
