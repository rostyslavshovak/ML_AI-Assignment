import re

def split_problems(text):
    pattern = r"(Problem\s+\d+.*?)(?=Problem\s+\d+|$)"
    problems = []
    for block in re.findall(pattern, text, flags=re.DOTALL):
        match = re.search(r"Problem\s+(\d+)", block)
        number = match.group(1) if match else "Unknown"
        content = re.sub(r"Problem\s+\d+", "", block, count=1).strip()
        content = re.sub(r"^\(\d+(\+\d+)*\s*points\)\s*", "", content)
        problems.append((number, content))
    return problems

def split_subquestions(text):
    parts = re.split(r"(\([a-z]\))", text)
    results, buffer = [], ""
    for part in parts:
        part = part.strip()
        if re.fullmatch(r"\([a-z]\)", part):
            if buffer:
                results.append(buffer.strip())
            buffer = part
        else:
            buffer += " " + part
    if buffer:
        results.append(buffer.strip())
    return results

def split_text_into_parts(text):
    parts = []
    for seg in re.split(r"(https?://[^\s]+)", text):
        seg = seg.strip()
        if seg:
            parts.append({"type": "text", "body": seg})
    return parts

def json_structure(raw_text):
    problems = split_problems(raw_text)
    output = []
    for num, content in problems:
        subs = split_subquestions(content)
        if len(subs) > 1:
            main_parts = split_text_into_parts(subs[0])
            children = []
            for sub in subs[1:]:
                m = re.match(r"\(([a-z])\)\s*(.*)", sub, flags=re.DOTALL)
                if m:
                    label, subtext = m.groups()
                    parts = [{"type": "text", "body": f"({label})"}] + split_text_into_parts(subtext)
                else:
                    parts = split_text_into_parts(sub)
                children.append({"parts": parts})
            body = {"parts": main_parts, "children": children}
        else:
            body = {"parts": split_text_into_parts(content), "children": []}
        output.append({"number": num, "body": body})
    return output

def process_snippet(snippet):
    snippet = re.sub(r"f\s*\(", "f(", snippet)
    snippet = re.sub(r"\)\s*\[dx\]", ")[dx]", snippet)
    snippet = re.sub(r"([a-zA-Z])\s+T\b", r"\1^T", snippet)

    snippet = snippet.replace("->", r"\to").replace("→", r"\to")
    snippet = snippet.replace("θ", r"\theta").replace("sin(", r"\sin(").replace("cos(", r"\cos(")
    snippet = snippet.replace("￿", "")
    snippet = snippet.replace("∈", r"\in")
    snippet = snippet.replace("Rn×n", r"\mathbb{R}^{n\times n}").replace("Rn", r"\mathbb{R}^n")
    snippet = snippet.replace("xxT", r"x x^T")
    snippet = snippet.replace("xTx", r"x^T x")
    snippet = re.sub(r"\(cid:\d+\)", "", snippet)
    snippet = re.sub(r'([a-zA-Z])2\b', r'\1^2', snippet)

    if not snippet.lstrip().startswith("f("):
        snippet = snippet.replace("f(", r"f'(")

    if "rotate(" in snippet:
        snippet = snippet.replace("rotate(", r"\text{rotate}(")
    if "hyperbolic_rotate(" in snippet:
        snippet = snippet.replace("hyperbolic_rotate(", r"\text{hyperbolic\_rotate}(")
    if "nonlin_shear(" in snippet:
        snippet = snippet.replace("nonlin_shear(", r"\text{nonlin\_shear}(")
    if "warp(" in snippet:
        snippet = snippet.replace("warp(", r"\text{warp}(")

    math_triggers = ["\\in", "\\to", "\\mathbb{R}", "x^T", "f(", "f'("]
    is_math = any(trigger in snippet for trigger in math_triggers)
    return snippet, is_math

def postprocess_snippets(data):
    for question in data:
        for part in question["body"]["parts"]:
            txt, is_math = process_snippet(part["body"])
            part["body"] = txt
            if is_math:
                part["type"] = "LaTeX"
        for child in question["body"]["children"]:
            for part in child["parts"]:
                txt, is_math = process_snippet(part["body"])
                part["body"] = txt
                if is_math:
                    part["type"] = "LaTeX"