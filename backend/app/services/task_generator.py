import random
import math
from typing import Any
from dataclasses import dataclass, field
from fractions import Fraction


@dataclass
class GeneratedTask:
    content: dict
    solution: dict
    answer: str
    difficulty: float
    format: str


class ParamGen:
    @staticmethod
    def int_range(lo: int, hi: int) -> int:
        return random.randint(lo, hi)

    @staticmethod
    def int_range_not_zero(lo: int, hi: int) -> int:
        v = 0
        while v == 0:
            v = random.randint(lo, hi)
        return v

    @staticmethod
    def choice(opts: list) -> Any:
        return random.choice(opts)

    @staticmethod
    def float_range(lo: float, hi: float, decimals: int = 1) -> float:
        return round(random.uniform(lo, hi), decimals)


def frac_str(num: int, den: int) -> str:
    if den < 0:
        num, den = -num, -den
    if den == 1:
        return str(num)
    return f"{num}/{den}"


def sqrt_str(n: int) -> str:
    if n == 1:
        return "1"
    root = int(math.isqrt(n))
    if root * root == n:
        return str(root)
    for factor in [4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144]:
        if n % factor == 0:
            f = int(math.isqrt(factor))
            rem = n // factor
            return f"{f}√{rem}"
    return f"√{n}"


def simplify_fraction(num: int, den: int) -> str:
    if den == 0:
        return "∞"
    g = math.gcd(abs(num), abs(den))
    num //= g
    den //= g
    if den == 1:
        return str(num)
    return f"{num}/{den}"


class TaskGenerator:
    def __init__(self, templates: list):
        self._templates = {t["id"]: t for t in templates}
        self._by_topic: dict[str, list] = {}
        for t in templates:
            self._by_topic.setdefault(t["topic_code"], []).append(t)

    def generate(self, template_id: str, difficulty_variation: float = 0.0) -> GeneratedTask:
        tmpl = self._templates[template_id]
        raw_params = tmpl["generate_params"]()
        params = self._enrich_params(raw_params)
        answer = tmpl["compute_answer"](params)
        params["answer"] = str(answer)
        content = self._render(tmpl["content_template"], params)
        solution = self._render_solution(tmpl["solution_template"], params)
        difficulty = min(1.0, max(0.1, tmpl["difficulty_base"] + difficulty_variation))
        return GeneratedTask(
            content=content,
            solution=solution,
            answer=str(answer),
            difficulty=difficulty,
            format=tmpl.get("format", "numeric"),
        )

    def _enrich_params(self, params: dict) -> dict:
        enriched = dict(params)
        for key, val in params.items():
            if key.startswith("sign_") and isinstance(val, str):
                continue
            if isinstance(val, int) or isinstance(val, float):
                if val < 0 and not key.startswith("sign_"):
                    sign_key = f"sign_{key}"
                    abs_key = f"{key}_abs"
                    if sign_key not in enriched:
                        enriched[sign_key] = "-"
                    if abs_key not in enriched:
                        enriched[abs_key] = str(abs(val))
        for key in list(params.keys()):
            if isinstance(params[key], (int, float)):
                for suffix, func in [("_minus", lambda a, b: a - b), ("_plus", lambda a, b: a + b), ("_times", lambda a, b: a * b)]:
                    if key.endswith(suffix + "_b") or key.endswith(suffix + "_c") or key.endswith(suffix + "_d"):
                        continue
        for key in list(enriched.keys()):
            if key.endswith("_abs") and key[:-4] not in enriched:
                orig = params.get(key[:-4])
                if orig is not None:
                    enriched[key] = str(abs(orig))
            else:
                val = enriched.get(key)
                if isinstance(val, str) and val.startswith("-"):
                    enriched[key] = val[1:]
                    sign_key = f"sign_{key}"
                    if sign_key not in enriched:
                        enriched[sign_key] = "-"

        for key, val in list(enriched.items()):
            if isinstance(val, int):
                sgn = "-" if val < 0 else "+"
                enriched[f"sign_{key}"] = sgn
                enriched[f"{key}_abs"] = str(abs(val))

        for key in list(params.keys()):
            val = params[key]
            if isinstance(val, int):
                enriched[f"sign_{key}"] = "-" if val < 0 else "+"
                enriched[f"{key}_abs"] = str(abs(val))

        miss_val = 1 - (enriched.get("pct", 0) / 100)
        if abs(miss_val) < 1:
            enriched["miss"] = round(miss_val, 2)

        enriched["total"] = enriched.get("n", 0) + enriched.get("m", 0)
        enriched["not_k"] = enriched.get("n", 0) - enriched.get("k", 0)
        enriched["product"] = enriched.get("a", 1) * enriched.get("b", 1)
        enriched["quotient"] = enriched.get("a", 1) / (enriched.get("b", 1) or 1)
        enriched["n1"] = enriched.get("n", 0) - 1
        enriched["n2"] = enriched.get("n", 0) - 2
        enriched["n_minus_1"] = enriched.get("n", 0) - 1
        enriched["n_k"] = enriched.get("n", 0) - enriched.get("k", 0)
        enriched["2a"] = 2 * enriched.get("a", 1)
        enriched["vsum"] = enriched.get("v1", 0) + enriched.get("v2", 0)
        enriched["total_rate"] = round(1 / enriched.get("a", 1) + 1 / enriched.get("b", 1), 4) if enriched.get("a") and enriched.get("b") else 0
        enriched["sqrt_n"] = round(math.sqrt(enriched.get("n", 2)), 2)
        enriched["sqrt_m"] = round(math.sqrt(enriched.get("m", 2)), 2)
        enriched["per_kg"] = round(enriched.get("m", 0) / enriched.get("n", 1), 2)
        enriched["discount"] = enriched.get("price", 0) * enriched.get("pct", 0) // 100
        enriched["fav"] = enriched.get("n", 0)
        enriched["ab"] = enriched.get("a", 0) * enriched.get("b", 0)
        enriched["c_minus_b"] = enriched.get("c", 0) - enriched.get("b", 0)
        enriched["2a"] = 2 * enriched.get("a", 1)
        summ = sum(enriched.get("nums", [0])) if isinstance(enriched.get("nums"), list) else 0
        enriched["sum_"] = summ
        enriched["max_"] = max(enriched.get("nums", [0])) if isinstance(enriched.get("nums"), list) else 0
        enriched["min_"] = min(enriched.get("nums", [0])) if isinstance(enriched.get("nums"), list) else 0
        enriched["good"] = round(1 - enriched.get("pct", 0) / 100, 2)
        enriched["comb"] = math.comb(enriched.get("n", 2), enriched.get("k", 2)) if enriched.get("n", 0) >= enriched.get("k", 0) else 0
        enriched["arg"] = enriched.get("base", 1) ** enriched.get("exp", 1)

        if "a" in params and "b" in params and "c" in params:
            enriched["D_val"] = params["b"] ** 2 - 4 * params["a"] * params["c"]

        if "x1" in params and "x2" in params:
            enriched["p"] = -(params["x1"] + params["x2"])
            enriched["q"] = params["x1"] * params["x2"]

        return enriched

    def generate_variations(self, template_id: str, count: int = 5) -> list[GeneratedTask]:
        tasks = []
        for _ in range(count):
            variation = random.uniform(-0.1, 0.15)
            tasks.append(self.generate(template_id, variation))
        return tasks

    def generate_for_topic(self, topic_code: str, count: int = 5) -> list[GeneratedTask]:
        templates = self._by_topic.get(topic_code, [])
        if not templates:
            return []
        tasks = []
        for _ in range(count):
            tmpl = random.choice(templates)
            tasks.append(self.generate(tmpl["id"]))
        return tasks

    def get_template_ids(self) -> list[str]:
        return list(self._templates.keys())

    def get_template_ids_by_topic(self, topic_code: str) -> list[str]:
        return [t["id"] for t in self._by_topic.get(topic_code, [])]

    def _render(self, content_template: dict, params: dict) -> dict:
        result = {}
        for key, template in content_template.items():
            if isinstance(template, str):
                result[key] = self._smart_format(template, params)
            elif isinstance(template, list):
                result[key] = [self._smart_format(item, params) if isinstance(item, str) else item for item in template]
            else:
                result[key] = template
        return result

    def _smart_format(self, template: str, params: dict) -> str:
        result = template
        for key, val in params.items():
            placeholder = "{" + key + "}"
            if placeholder not in result:
                continue
            str_val = str(val)
            try:
                num = float(str_val)
                is_zero = abs(num) < 0.001
            except (ValueError, TypeError):
                is_zero = False

            if is_zero and not key.startswith("sign_"):
                result = result.replace(placeholder, "")
                continue
            result = result.replace(placeholder, str_val)

        import re
        result = re.sub(r'\s+', ' ', result).strip()

        result = result.replace('\x0c', '\\f')

        return result

    def _render_solution(self, solution_template: dict, params: dict) -> dict:
        result = {}
        if "steps" in solution_template:
            result["steps"] = [
                step.format(**params) if isinstance(step, str) else step
                for step in solution_template["steps"]
            ]
        if "answer_hint" in solution_template:
            hint = solution_template["answer_hint"]
            if isinstance(hint, str):
                result["answer_hint"] = hint.format(**params)
            else:
                result["answer_hint"] = hint
        return result
