import re
import pytest
from src.processor import (
    split_problems,
    split_subquestions,
    split_text_into_parts,
    json_structure,
    process_snippet,
    postprocess_snippets
)

def test_split_problems():
    text = (
        "Problem 1 (3 points) What is the value of x? "
        "Problem 2 (4 points) Solve the equation."
    )
    problems = split_problems(text)
    assert len(problems) == 2
    # Check problem numbers and that content was cleaned from the header.
    assert problems[0][0] == "1"
    assert "What is the value of x?" in problems[0][1]
    assert problems[1][0] == "2"
    assert "Solve the equation." in problems[1][1]


def test_split_problems_no_match():
    text = "There is no problem keyword here."
    problems = split_problems(text)
    assert problems == []


def test_split_subquestions():
    text = "Main question text (a) First subquestion text (b) Second subquestion text"
    subs = split_subquestions(text)
    # The function should split the text into 3 parts:
    # 1. The main part before any subquestion marker.
    # 2. The first subquestion starting with (a).
    # 3. The second subquestion starting with (b).
    assert len(subs) == 3
    assert subs[0].startswith("Main question text")
    assert subs[1].startswith("(a)")
    assert subs[2].startswith("(b)")


def test_split_subquestions_no_subquestions():
    text = "This is a question without subquestions."
    subs = split_subquestions(text)
    assert len(subs) == 1


def test_split_text_into_parts():
    text = "Here is a link: https://example.com in a sentence."
    parts = split_text_into_parts(text)
    # The parts list should include the URL as its own segment.
    url_parts = [part for part in parts if part["body"] == "https://example.com"]
    assert len(url_parts) == 1
    # Check that every part has a "type" of "text"
    for part in parts:
        assert part["type"] == "text"


# --- Tests for JSON structure creation ---

def test_json_structure():
    raw_text = "Problem 1 (3 points) Main content (a) Subcontent A (b) Subcontent B"
    structure = json_structure(raw_text)
    assert isinstance(structure, list)
    assert len(structure) == 1
    problem = structure[0]
    assert problem["number"] == "1"
    body = problem["body"]
    # Check that the main parts and children are present.
    assert "parts" in body
    assert "children" in body
    assert isinstance(body["parts"], list)
    assert isinstance(body["children"], list)
    # There should be at least two children corresponding to subquestions.
    assert len(body["children"]) == 2


# --- Tests for snippet processing functions ---

def test_process_snippet_math():
    # A snippet that should trigger math replacements.
    snippet = "f( x ) -> sin(θ) and also check x T."
    processed, is_math = process_snippet(snippet)
    # Verify some expected replacements:
    # - "->" replaced by "\to"
    # - "sin(" replaced by "\sin("
    # - "θ" replaced by "\theta"
    assert r"\to" in processed
    assert r"\sin(" in processed
    assert r"\theta" in processed
    # Since math triggers are present, is_math should be True.
    assert is_math is True


def test_process_snippet_non_math():
    snippet = "This is a plain text snippet."
    processed, is_math = process_snippet(snippet)
    # No math triggers are expected.
    assert processed == snippet or "f'(" in processed  # if any f( was replaced
    assert is_math is False


def test_process_snippet_replace_f():
    # This snippet does not start with "f(" so all occurrences of "f(" should be replaced with "f'(".
    snippet = "Calculate f(x) = x^2 and then f(x+1)."
    processed, _ = process_snippet(snippet)
    # Since the snippet does not start with "f(", we expect every "f(" to become "f'(".
    assert "f'(" in processed
    assert "f(" not in processed


def test_postprocess_snippets():
    # Create a dummy data structure as produced by json_structure
    data = [{
        "number": "1",
        "body": {
            "parts": [{"type": "text", "body": "f( x ) -> cos(θ)"}],
            "children": [{"parts": [{"type": "text", "body": "rotate(45)"}]}]
        }
    }]
    postprocess_snippets(data)

    main_part = data[0]["body"]["parts"][0]
    child_part = data[0]["body"]["children"][0]["parts"][0]
    # The replacements in process_snippet should flag math content so that type is updated to "LaTeX".
    assert main_part["type"] == "LaTeX"
    assert child_part["type"] == "LaTeX"