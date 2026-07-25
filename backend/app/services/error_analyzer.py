from dataclasses import dataclass, field
from typing import Optional
import re
from openai import AsyncOpenAI
from app.core.config import get_settings

settings = get_settings()

ERROR_PATTERNS = [
    {
        "id": "discriminant_half",
        "name": "Забыл разделить на 2a",
        "message": "Вы применили формулу дискриминанта, но забыли разделить на 2a. Корни квадратного уравнения: x = (-b ± √D) / (2a).",
        "topics": ["quadratic_equations"],
        "detect": lambda s, c: _sign_match(s, c) and _off_by_factor(s, c, 2),
        "micro_task": "Решите: $2x^2 - 8x + 6 = 0$. Проверьте, что вы разделили на 2a.",
    },
    {
        "id": "sign_error",
        "name": "Ошибка в знаке",
        "message": "Ошибка в знаке при переносе слагаемого через знак равенства. При переносе меняйте знак на противоположный.",
        "topics": ["linear_equations", "quadratic_equations", "inequalities"],
        "detect": lambda s, c: _sign_mismatch(s, c),
        "micro_task": "Решите: $3x + 7 = -2x + 2$. Внимательно следите за знаками при переносе.",
    },
    {
        "id": "log_property",
        "name": "Свойство логарифма",
        "message": "Проверьте свойства логарифмов: $\\log_a(xy) = \\log_a x + \\log_a y$, $\\log_a(x^n) = n\\log_a x$.",
        "topics": ["logarithms"],
        "detect": lambda s, c: any(op in s for op in ["+", "-"]) and _is_numeric(c) and _is_expression(s),
        "micro_task": "Вычислите: $\\log_2 8 + \\log_2 4$. Используйте свойство суммы логарифмов.",
    },
    {
        "id": "trig_value",
        "name": "Табличное значение тригонометрии",
        "message": "Ошибка в табличном значении. Запомните: $\\sin 30° = 1/2$, $\\sin 45° = \\sqrt{2}/2$, $\\sin 60° = \\sqrt{3}/2$.",
        "topics": ["trigonometry"],
        "detect": lambda s, c: _trig_mismatch(s, c),
        "micro_task": "Вычислите $\\sin 30° + \\cos 60°$ без калькулятора.",
    },
    {
        "id": "power_rule",
        "name": "Свойство степеней",
        "message": "Проверьте свойства: $a^m \\cdot a^n = a^{m+n}$, $(a^m)^n = a^{m \\cdot n}$, $a^m / a^n = a^{m-n}$.",
        "topics": ["exponents"],
        "detect": lambda s, c: _power_mismatch(s, c),
        "micro_task": "Вычислите $2^3 \\cdot 2^4$ двумя способами для проверки.",
    },
    {
        "id": "fraction_error",
        "name": "Ошибка в дробях",
        "message": "При решении уравнения с дробями не забудьте учесть ОДЗ (знаменатель ≠ 0) и правильно выполнить умножение.",
        "topics": ["rational_equations", "linear_equations"],
        "detect": lambda s, c: "/" in s and _is_numeric(s) and _sign_mismatch(s, c),
        "micro_task": "Решите: $(x-1)/(x+2) = 2/3$. Проверьте ОДЗ.",
    },
    {
        "id": "derivative_power",
        "name": "Производная степенной функции",
        "message": "Производная $x^n$ равна $n \\cdot x^{n-1}$. Проверьте показатель степени.",
        "topics": ["derivatives"],
        "detect": lambda s, c: _derivative_mismatch(s, c),
        "micro_task": "Найдите производную $f(x) = x^3$ и проверьте по формуле.",
    },
    {
        "id": "combinatorics_formula",
        "name": "Формула комбинаторики",
        "message": "Число сочетаний: $C_n^k = n! / (k! \\cdot (n-k)!)$. Число размещений: $A_n^k = n! / (n-k)!$.",
        "topics": ["combinatorics"],
        "detect": lambda s, c: _combo_mismatch(s, c),
        "micro_task": "Сколькими способами можно выбрать 2 человек из 5? Проверьте по формуле.",
    },
]


def _is_numeric(s: str) -> bool:
    s = s.strip().replace("-", "").replace(".", "").replace(",", "").replace("/", "")
    return s.isdigit() or all(c in "0123456789. " for c in s)


def _is_expression(s: str) -> bool:
    return any(op in s for op in ["+", "-", "*", "/", "log", "sin", "cos", "^", "√"])


def _sign_match(s: str, c: str) -> bool:
    return s.replace("-", "") == c.replace("-", "") or s.replace("-", "") == c


def _sign_mismatch(s: str, c: str) -> bool:
    sa = s.strip().replace(" ", "")
    ca = c.strip().replace(" ", "")
    if not sa or not ca:
        return False
    try:
        sn = float(sa)
        cn = float(ca)
        return sn == -cn
    except ValueError:
        s_clean = re.sub(r"\s+", "", s)
        c_clean = re.sub(r"\s+", "", c)
        if s_clean.startswith("-") and not c_clean.startswith("-"):
            return s_clean[1:] == c_clean
        if c_clean.startswith("-") and not s_clean.startswith("-"):
            return s_clean == c_clean[1:]
    return False


def _off_by_factor(s: str, c: str, factor: int) -> bool:
    try:
        sn = float(s.strip())
        cn = float(c.strip())
        return abs(sn * factor - cn) < 0.001 or abs(sn - cn * factor) < 0.001
    except ValueError:
        return False


def _trig_mismatch(s: str, c: str) -> bool:
    trig_values = {
        "0": 0, "0.5": 0.5, "1/2": 0.5, "0.707": 0.707, "0.866": 0.866, "1": 1,
        "√2/2": 0.7071, "√3/2": 0.866, "1/√3": 0.577, "√3": 1.732,
    }
    sv = trig_values.get(s.strip().lower())
    cv = trig_values.get(c.strip().lower())
    if sv is not None and cv is not None and sv != cv:
        return True
    try:
        return abs(float(s) - float(c)) > 0.01
    except ValueError:
        return False


def _power_mismatch(s: str, c: str) -> bool:
    try:
        return abs(float(s.strip()) - float(c.strip())) > 0.1
    except ValueError:
        return False


def _derivative_mismatch(s: str, c: str) -> bool:
    return _power_mismatch(s, c)


def _combo_mismatch(s: str, c: str) -> bool:
    try:
        return abs(float(s.strip()) - float(c.strip())) > 0.1
    except ValueError:
        return False


@dataclass
class ErrorAnalysis:
    error_type: str
    explanation: str
    ai_explanation: Optional[str] = None
    micro_task: Optional[str] = None
    ai_confidence: float = 0.0
    needs_moderation: bool = False


class ErrorAnalyzer:
    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        if settings.openai_api_key:
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )

    def analyze_by_pattern(self, student_answer: str, correct_answer: str, topic_id: int) -> Optional[ErrorAnalysis]:
        topic_codes = {
            1: "linear_equations", 2: "quadratic_equations", 3: "rational_equations",
            4: "systems_equations", 5: "inequalities", 6: "exponents",
            7: "logarithms", 8: "trigonometry", 9: "derivatives",
            10: "integrals", 11: "probability", 12: "geometry_planimetry",
            13: "geometry_stereometry", 14: "word_problems", 15: "graphs",
            16: "financial_math", 17: "optimization", 18: "parameters",
            19: "number_theory", 20: "sequences", 21: "vectors",
            22: "combinatorics", 23: "statistics",
        }
        topic = topic_codes.get(topic_id, "unknown")

        student = student_answer.strip()
        correct = correct_answer.strip()
        if student == correct:
            return None

        for pattern in ERROR_PATTERNS:
            if topic in pattern["topics"]:
                try:
                    if pattern["detect"](student, correct):
                        return ErrorAnalysis(
                            error_type=pattern["id"],
                            explanation=pattern["message"],
                            micro_task=pattern.get("micro_task"),
                        )
                except Exception:
                    pass

        return ErrorAnalysis(
            error_type="unknown",
            explanation="Ответ не совпадает с правильным. Проверьте решение по шагам и попробуйте снова.",
        )

    async def generate_ai_explanation(
        self,
        topic_name: str,
        task_content: str,
        student_answer: str,
        correct_answer: str,
        error_type: str,
    ) -> tuple[str, float]:
        if self.client and settings.openai_api_key:
            return await self._openai_explain(topic_name, task_content, student_answer, correct_answer, error_type)
        return self._local_explain(topic_name, task_content, student_answer, correct_answer, error_type), 0.85

    def _local_explain(
        self,
        topic_name: str,
        task_content: str,
        student_answer: str,
        correct_answer: str,
        error_type: str,
    ) -> str:
        parts = [f"**Тема:** {topic_name}\n"]

        parts.append(f"Ваш ответ: **{student_answer}**. Правильный ответ: **{correct_answer}**.\n")

        if error_type and error_type != "unknown":
            for p in ERROR_PATTERNS:
                if p["id"] == error_type:
                    parts.append(f"**{p['name']}:** {p['message']}\n")
                    break

        parts.append("**Как решать правильно:**")
        parts.append(f"1. Внимательно прочитайте условие: _{task_content[:150]}_")
        parts.append(f"2. Выполните вычисления по шагам")
        parts.append(f"3. Проверьте ответ: {correct_answer}")
        parts.append(f"4. Сравните с вашим ответом ({student_answer}) и найдите расхождение")

        try:
            s = float(student_answer.strip().replace(",", "."))
            c = float(correct_answer.strip().replace(",", "."))
            diff = abs(s - c)
            if diff < 0.01:
                parts.append(f"\nРазница минимальна ({diff:.4f}) — возможно, ошибка в округлении.")
            elif s == -c:
                parts.append(f"\nВаш ответ отличается только знаком. Проверьте знаки при переносе.")
            elif abs(s * 2 - c) < 0.01:
                parts.append(f"\nВаш ответ ровно в 2 раза меньше/больше. Проверьте деление/умножение.")
        except ValueError:
            pass

        return "\n".join(parts)

    async def _openai_explain(self, topic_name, task_content, student_answer, correct_answer, error_type):
        prompt = f"""Ты — репетитор по математике ЕГЭ. Разбери ошибку ученика.

Тема: {topic_name}
Задача: {task_content}
Ответ ученика: {student_answer}
Правильный ответ: {correct_answer}
Тип ошибки: {error_type}

Напиши краткий разбор (3-5 предложений):
1. В чём ошибка (одно предложение)
2. Как правильно решать (1-2 предложения с формулами LaTeX в $...$)
3. Совет на будущее"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7,
            )
            text = response.choices[0].message.content
            confidence = self._validate_response(text)
            return text, confidence
        except Exception:
            return self._local_explain(topic_name, task_content, student_answer, correct_answer, error_type), 0.0

    def _validate_response(self, text: str | None) -> float:
        if not text:
            return 0.0
        confidence = 1.0
        forbidden = ["не могу", "не знаю", "как ИИ", "я не умею", "извините", "к сожалению"]
        for phrase in forbidden:
            if phrase in text.lower():
                confidence -= 0.15
        if len(text) < 30:
            confidence -= 0.3
        if len(text) > 1500:
            confidence -= 0.1
        return max(0.0, confidence)

    async def full_analysis(
        self,
        topic_id: int,
        topic_name: str,
        task_content: str,
        student_answer: str,
        correct_answer: str,
    ) -> ErrorAnalysis:
        pattern_result = self.analyze_by_pattern(student_answer, correct_answer, topic_id)

        if pattern_result:
            ai_text, confidence = await self.generate_ai_explanation(
                topic_name, task_content, student_answer, correct_answer, pattern_result.error_type
            )
            pattern_result.ai_explanation = ai_text
            pattern_result.ai_confidence = confidence
            pattern_result.needs_moderation = confidence < 0.7
            return pattern_result

        ai_text, confidence = await self.generate_ai_explanation(
            topic_name, task_content, student_answer, correct_answer, "unknown"
        )
        return ErrorAnalysis(
            error_type="unknown",
            explanation="Ответ не совпадает с правильным.",
            ai_explanation=ai_text,
            ai_confidence=confidence,
            needs_moderation=confidence < 0.7,
        )
