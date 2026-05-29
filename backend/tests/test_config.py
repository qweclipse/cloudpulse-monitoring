from app.config import parse_cors_origins


def test_parse_cors_origins_accepts_json_list() -> None:
    assert parse_cors_origins(
        '["https://frontend.example.com","http://localhost:5173"]'
    ) == ["https://frontend.example.com", "http://localhost:5173"]


def test_parse_cors_origins_accepts_single_origin() -> None:
    assert parse_cors_origins("https://frontend.example.com") == [
        "https://frontend.example.com"
    ]


def test_parse_cors_origins_accepts_comma_separated_origins() -> None:
    assert parse_cors_origins(
        "https://frontend.example.com, http://localhost:5173"
    ) == ["https://frontend.example.com", "http://localhost:5173"]


def test_parse_cors_origins_accepts_unquoted_bracket_list() -> None:
    assert parse_cors_origins("[https://frontend.example.com]") == [
        "https://frontend.example.com"
    ]
