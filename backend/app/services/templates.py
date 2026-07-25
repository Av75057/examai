import random
import math
from fractions import Fraction
from app.services.task_generator import ParamGen, frac_str, sqrt_str, simplify_fraction

P = ParamGen()

TEMPLATES = []

# ═══════════════════════════════════════════
# 1. Линейные уравнения (6 шаблонов)
# ═══════════════════════════════════════════

def _gen_linear_1():
    a = P.int_range_not_zero(2, 12)
    b = P.int_range_not_zero(-20, 20)
    c = P.int_range(-50, 50)
    return {"a": a, "b": b, "c": c}

TEMPLATES.append({
    "id": "linear_001",
    "topic_code": "linear_equations",
    "content_template": {"text": "Решите уравнение: $ {a}x {sign_b} {b_abs} = {c} $"},
    "generate_params": _gen_linear_1,
    "compute_answer": lambda p: (p["c"] - p["b"]) / p["a"],
    "solution_template": {"steps": [
        "{a}x = {c} - ({b}) = {c_minus_b}",
        "x = {c_minus_b} / {a} = {answer}",
    ], "answer_hint": "Перенесите {b} в правую часть и разделите на {a}"},
    "difficulty_base": 0.15,
})


def _gen_linear_2():
    a = P.int_range_not_zero(2, 8)
    b = P.int_range_not_zero(-15, 15)
    c = P.int_range_not_zero(2, 8)
    d = P.int_range(-30, 30)
    return {"a": a, "b": b, "c": c, "d": d}

TEMPLATES.append({
    "id": "linear_002",
    "topic_code": "linear_equations",
    "content_template": {"text": "Решите уравнение: ${a}(x {sign_b} {b_abs}) = {c}x {sign_d} {d_abs}$"},
    "generate_params": _gen_linear_2,
    "compute_answer": lambda p: (p["d"] - p["a"] * p["b"]) / (p["a"] - p["c"]) if p["a"] != p["c"] else None,
    "solution_template": {"steps": [
        "Раскрываем скобки: {a}x + {ab} = {c}x + {d}",
        "{a}x - {c}x = {d} - {ab}",
        "x = {answer}",
    ]},
    "difficulty_base": 0.2,
})


def _gen_linear_3():
    a = P.int_range_not_zero(2, 6)
    b = P.int_range_not_zero(1, 5)
    return {"a": a, "b": b}

TEMPLATES.append({
    "id": "linear_003",
    "topic_code": "linear_equations",
    "content_template": {"text": "Решите уравнение: $\frac{{x}}{{{a}}} = \frac{{x}}{{{b}}} + 1$"},
    "generate_params": _gen_linear_3,
    "compute_answer": lambda p: (p["a"] * p["b"]) / (p["b"] - p["a"]),
    "solution_template": {"steps": [
        "x/{a} - x/{b} = 1",
        "x({b} - {a})/({a}·{b}) = 1",
        "x = {a}·{b}/({b} - {a}) = {answer}",
    ]},
    "difficulty_base": 0.25,
})


def _gen_linear_4():
    a = P.int_range_not_zero(3, 15)
    b = P.int_range(10, 40)
    return {"a": a, "b": b}

TEMPLATES.append({
    "id": "linear_004",
    "topic_code": "linear_equations",
    "content_template": {"text": "Длина прямоугольника на {a} см больше ширины. Периметр равен {b} см. Найдите ширину."},
    "generate_params": _gen_linear_4,
    "compute_answer": lambda p: (p["b"] / 2 - p["a"]) / 2,
    "solution_template": {"steps": [
        "Ширина = x, длина = x + {a}",
        "P = 2(x + x + {a}) = {b}",
        "4x + {2a} = {b}",
        "x = {answer}",
    ]},
    "difficulty_base": 0.2,
})


TEMPLATES.append({
    "id": "linear_005",
    "topic_code": "linear_equations",
    "content_template": {"text": "Решите уравнение: 3(2x - 1) - 2(3x + 4) = {const_k}"},
    "generate_params": lambda: {"const_k": P.int_range_not_zero(-20, 20)},
    "compute_answer": lambda p: f"x — любое число" if p["const_k"] == -11 else "решений нет",
    "solution_template": {"steps": [
        "6x - 3 - 6x - 8 = {const_k}",
        "-11 = {const_k}",
    ]},
    "difficulty_base": 0.35,
})


TEMPLATES.append({
    "id": "linear_006",
    "topic_code": "linear_equations",
    "content_template": {"text": "Решите уравнение: $\frac{{{a}x {sign_b} {b_abs}}}{{{c}}} = \frac{{{d}x {sign_e} {e_abs}}}{{{f}}}$"},
    "generate_params": lambda: {
        "a": P.int_range_not_zero(2, 6), "b": P.int_range(1, 5), "c": P.int_range_not_zero(2, 5),
        "d": P.int_range_not_zero(2, 6), "e": P.int_range(1, 5), "f": P.int_range_not_zero(2, 5),
    },
    "compute_answer": lambda p: (p["b"] * p["f"] - p["e"] * p["c"]) / (p["a"] * p["f"] - p["d"] * p["c"]),
    "solution_template": {"steps": [
        "Домножаем на {c}·{f}: (a x - b)·f = (d x + e)·c",
        "Раскрываем, решаем относительно x",
    ]},
    "difficulty_base": 0.3,
})

# ═══════════════════════════════════════════
# 2. Квадратные уравнения (8 шаблонов)
# ═══════════════════════════════════════════

def _gen_quad_1():
    a = P.int_range_not_zero(1, 5)
    b = P.int_range_not_zero(-20, 20)
    c = P.int_range(-50, 50)
    D = b * b - 4 * a * c
    while D < 0:
        b = P.int_range_not_zero(-20, 20)
        c = P.int_range(-50, 50)
        D = b * b - 4 * a * c
    return {"a": a, "b": b, "c": c, "D": D}

TEMPLATES.append({
    "id": "quad_001",
    "topic_code": "quadratic_equations",
    "content_template": {"text": "Решите уравнение: $ {a}x^2 {sign_b} {b_abs}x {sign_c} {c_abs} = 0 $"},
    "generate_params": _gen_quad_1,
    "compute_answer": lambda p: _quad_roots(p),
    "solution_template": {"steps": [
        "D = ({b})² - 4·{a}·({c}) = {D_val}",
        "x = (-({b}) ± √{D_val}) / (2·{a})",
        "Ответ: {answer}",
    ]},
    "difficulty_base": 0.3,
})

def _quad_roots(p):
    a, b, c = p["a"], p["b"], p["c"]
    D = b * b - 4 * a * c
    if D == 0:
        return str(-b / (2 * a))
    sqrt_D = int(math.isqrt(D))
    if sqrt_D * sqrt_D == D:
        x1 = Fraction(-b + sqrt_D, 2 * a)
        x2 = Fraction(-b - sqrt_D, 2 * a)
        return f"{x1}; {x2}"
    return f"(-{b} ± √{D}) / {2 * a}"

def _quad_steps(p):
    a, b, c = p["a"], p["b"], p["c"]
    D = b * b - 4 * a * c
    sign_b = "+" if b >= 0 else "-"
    sign_c = "+" if c >= 0 else "-"
    return [
        f"D = ({b})² - 4·{a}·({c}) = {D}",
        f"x = (-({b}) ± √{D}) / (2·{a}) = {_quad_roots(p)}",
    ]


def _gen_quad_vieta():
    x1 = P.int_range_not_zero(-10, 10)
    x2 = P.int_range_not_zero(-10, 10)
    return {"x1": x1, "x2": x2, "sum_": x1 + x2, "prod_": x1 * x2}

TEMPLATES.append({
    "id": "quad_002",
    "topic_code": "quadratic_equations",
    "content_template": {"text": "Решите уравнение $x^2 {sign_sum_} {sum__abs}x {sign_prod_} {prod__abs} = 0$ (теорема Виета)"},
    "generate_params": _gen_quad_vieta,
    "compute_answer": lambda p: f"{p['x1']}; {p['x2']}",
    "solution_template": {"steps": [
        "По теореме Виета: x₁ + x₂ = {sum_}, x₁·x₂ = {prod_}",
        "Подбором: {x1} + {x2} = {sum_}, {x1}·{x2} = {prod_}",
        "Ответ: {x1}; {x2}",
    ]},
    "difficulty_base": 0.25,
})


def _gen_quad_biquad():
    a = P.int_range_not_zero(1, 3)
    b = P.int_range_not_zero(-10, 10)
    c = P.int_range(-20, 20)
    D = b * b - 4 * a * c
    return {"a": a, "b": b, "c": c, "D": D}

TEMPLATES.append({
    "id": "quad_003",
    "topic_code": "quadratic_equations",
    "content_template": {"text": "Решите биквадратное уравнение: ${a}x^4 {sign_b} {b_abs}x^2 {sign_c} {c_abs} = 0$"},
    "generate_params": _gen_quad_biquad,
    "compute_answer": lambda p: _biquad_roots(p),
    "solution_template": {"steps": [
        "Замена t = x², t ≥ 0: {a}t² {sign_b} {b_abs}t {sign_c} {c_abs} = 0",
        "Решаем квадратное относительно t",
        "Возвращаемся к x = ±√t",
    ]},
    "difficulty_base": 0.4,
})

def _biquad_roots(p):
    a, b, c = p["a"], p["b"], p["c"]
    D = b * b - 4 * a * c
    if D < 0:
        return "нет решений"
    sqrt_D = int(math.isqrt(D))
    if sqrt_D * sqrt_D != D:
        return f"t = (-{b} ± √{D}) / {2*a}, затем x = ±√t"
    t1 = Fraction(-b + sqrt_D, 2 * a)
    t2 = Fraction(-b - sqrt_D, 2 * a)
    roots = []
    for t in [t1, t2]:
        if t > 0:
            from fractions import Fraction as F
            ts = float(t)
            s = int(math.isqrt(int(ts))) if ts > 0 and ts == int(ts) else None
            if s is not None and s * s == ts:
                roots.extend([s, -s])
            else:
                roots.append(f"±√{t}")
        elif t == 0:
            roots.append(0)
    return "; ".join(str(r) for r in roots) if roots else "нет решений"


def _gen_quad_fractional():
    a = P.int_range_not_zero(1, 3)
    x1 = P.int_range_not_zero(-8, 8)
    x2 = P.int_range_not_zero(-8, 8)
    return {"a": a, "x1": x1, "x2": x2}

TEMPLATES.append({
    "id": "quad_004",
    "topic_code": "quadratic_equations",
    "content_template": {"text": "Решите уравнение: $(x {sign_x1} {x1_abs})(x {sign_x2} {x2_abs}) = 0$"},
    "generate_params": _gen_quad_fractional,
    "compute_answer": lambda p: f"{p['x1']}; {p['x2']}",
    "solution_template": {"steps": [
        "Произведение равно нулю, когда один из множителей равен нулю",
        "x - {x1} = 0 → x = {x1}",
        "x - {x2} = 0 → x = {x2}",
    ]},
    "difficulty_base": 0.1,
})


TEMPLATES.append({
    "id": "quad_005",
    "topic_code": "quadratic_equations",
    "content_template": {"text": "Решите уравнение: x² - {a}x + {b} = 0. В ответе укажите больший корень."},
    "generate_params": lambda: {
        "a": P.int_range_not_zero(3, 15),
        "x1": P.int_range(1, 10),
        "x2": P.int_range(1, 10),
        "b": 0,
    },
    "compute_answer": lambda p: str(max(p["x1"], p["x2"])),
    "solution_template": {"steps": ["По теореме Виета: x₁ + x₂ = {a}, x₁·x₂ = {b}", "Подбор корней", "Бо́льший корень: {answer}"]},
    "difficulty_base": 0.3,
})


TEMPLATES.append({
    "id": "quad_006",
    "topic_code": "quadratic_equations",
    "content_template": {"text": "Решите уравнение: {k}/(x - {m}) = {n}/(x + {p})"},
    "generate_params": lambda: {
        "k": P.int_range_not_zero(2, 10), "m": P.int_range(1, 10),
        "n": P.int_range_not_zero(2, 10), "p": P.int_range(1, 10),
    },
    "compute_answer": lambda p: _compute_fractional_quad(p),
    "solution_template": {"steps": [
        "k(x + p) = n(x - m), при x ≠ m, x ≠ -p",
        "Раскрываем → линейное или квадратное уравнение",
    ]},
    "difficulty_base": 0.45,
})

def _compute_fractional_quad(p):
    k, m, n, pp = p["k"], p["m"], p["n"], p["p"]
    num = k * pp + n * m
    den = n - k
    if den == 0:
        return "нет решений" if num != 0 else "x — любое, кроме {m} и {-p}"
    return str(num / den)


TEMPLATES.append({
    "id": "quad_007",
    "topic_code": "quadratic_equations",
    "content_template": {"text": "Решите неравенство: x² {sign_b} {b_abs}x {sign_c} {c_abs} ≤ 0"},
    "generate_params": lambda: {
        "x1": P.int_range(-8, 2),
        "x2": P.int_range(0, 10),
        "b_abs": 0, "sign_b": "", "sign_c": "", "c_abs": 0,
    },
    "compute_answer": lambda p: f"[{p['x1']}; {p['x2']}]",
    "solution_template": {"steps": [
        "Корни: x₁ = {x1}, x₂ = {x2}",
        "Парабола ветвями вверх, ≤ 0 между корнями",
        "x ∈ [{x1}; {x2}]",
    ]},
    "difficulty_base": 0.35,
})


TEMPLATES.append({
    "id": "quad_008",
    "topic_code": "quadratic_equations",
    "content_template": {"text": "Разложение: $(x {sign_x1} {x1_abs})(x {sign_x2} {x2_abs}) = 0$. Найдите сумму корней $x_1 + x_2$."},
    "generate_params": lambda: {
        "x1": P.int_range(-10, 10),
        "x2": P.int_range(-10, 10),
    },
    "compute_answer": lambda p: str(p["x1"] + p["x2"]),
    "solution_template": {"steps": ["$x_1 = {x1}$, $x_2 = {x2}$", "$x_1 + x_2 = {answer}$"]},
    "difficulty_base": 0.2,
})

# ═══════════════════════════════════════════
# 3. Теория вероятностей (6 шаблонов)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "prob_001",
    "topic_code": "probability",
    "content_template": {"text": "В коробке {n} красных и {m} синих шаров. Найдите вероятность достать красный шар."},
    "generate_params": lambda: {"n": P.int_range(2, 12), "m": P.int_range(2, 12)},
    "compute_answer": lambda p: simplify_fraction(p["n"], p["n"] + p["m"]),
    "solution_template": {"steps": [
        "Всего шаров: {n} + {m} = {total}",
        "Благоприятных: {n}",
        "P = {n}/{total} = {answer}",
    ]},
    "difficulty_base": 0.15,
})


TEMPLATES.append({
    "id": "prob_002",
    "topic_code": "probability",
    "content_template": {"text": "Игральную кость бросают дважды. Найдите вероятность, что сумма выпавших очков равна {s}."},
    "generate_params": lambda: {"s": P.int_range(5, 9)},
    "compute_answer": lambda p: _prob_dice_sum(p),
    "solution_template": {"steps": [
        "Всего исходов: 6 × 6 = 36",
        "Благоприятные: перебор пар (i, j), где i + j = {s}",
        "P = {fav}/{total}",
    ]},
    "difficulty_base": 0.25,
})

def _prob_dice_sum(p):
    s = p["s"]
    count = sum(1 for i in range(1, 7) for j in range(1, 7) if i + j == s)
    return simplify_fraction(count, 36)


TEMPLATES.append({
    "id": "prob_003",
    "topic_code": "probability",
    "content_template": {"text": "В классе {n} учеников, среди них {k} отличников. Случайно выбирают одного. Найдите вероятность, что это НЕ отличник."},
    "generate_params": lambda: {"n": P.int_range(20, 35), "k": P.int_range(3, 8)},
    "compute_answer": lambda p: simplify_fraction(p["n"] - p["k"], p["n"]),
    "solution_template": {"steps": [
        "Не отличников: {n} - {k} = {not_k}",
        "P = {not_k}/{n} = {answer}",
    ]},
    "difficulty_base": 0.15,
})


TEMPLATES.append({
    "id": "prob_004",
    "topic_code": "probability",
    "content_template": {"text": "Вероятность попадания в мишень при одном выстреле равна 0.{pct}. Найдите вероятность двух промахов подряд."},
    "generate_params": lambda: {"pct": P.int_range(30, 90)},
    "compute_answer": lambda p: round((1 - p["pct"] / 100) ** 2, 4),
    "solution_template": {"steps": [
        "Вероятность промаха: 1 - 0.{pct} = {miss}",
        "Два промаха подряд: {miss}² = {answer}",
    ]},
    "difficulty_base": 0.25,
})


TEMPLATES.append({
    "id": "prob_005",
    "topic_code": "probability",
    "content_template": {"text": "Монету бросают {n} раз. Найдите вероятность, что орёл выпадет ровно {k} раз."},
    "generate_params": lambda: _gen_prob_coins(),
    "compute_answer": lambda p: _coin_prob(p),
    "solution_template": {"steps": [
        "Число исходов: 2^{n} = {total}",
        "Число благоприятных: C({n}, {k}) = {comb}",
        "P = {comb}/{total} = {answer}",
    ]},
    "difficulty_base": 0.35,
})

def _gen_prob_coins():
    n = P.choice([2, 3, 4, 5])
    k = P.int_range(0, n)
    return {"n": n, "k": k}

def _coin_prob(p):
    n, k = p["n"], p["k"]
    total = 2 ** n
    comb = math.comb(n, k)
    return simplify_fraction(comb, total)


TEMPLATES.append({
    "id": "prob_006",
    "topic_code": "probability",
    "content_template": {"text": "Вероятность того, что батарейка бракованная, равна 0,0{pct}. Найдите вероятность, что из двух случайно взятых батареек обе исправны."},
    "generate_params": lambda: {"pct": P.int_range(1, 9)},
    "compute_answer": lambda p: round((1 - p["pct"] / 100) ** 2, 4),
    "solution_template": {"steps": [
        "P(исправна) = 1 - 0,0{pct} = {good}",
        "P(обе исправны) = {good}² = {answer}",
    ]},
    "difficulty_base": 0.2,
    "format": "numeric",
})

# ═══════════════════════════════════════════
# 4. Степени и корни (5 шаблонов)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "exp_001",
    "topic_code": "exponents",
    "content_template": {"text": "Вычислите: ${base}^{{{exp1}}} \times {base}^{{{exp2}}}$"},
    "generate_params": lambda: {"base": P.int_range_not_zero(2, 5), "exp1": P.int_range(1, 4), "exp2": P.int_range(1, 4)},
    "compute_answer": lambda p: str(p["base"] ** (p["exp1"] + p["exp2"])),
    "solution_template": {"steps": [
        "a^m × a^n = a^(m+n)",
        "{base}^{exp1} × {base}^{exp2} = {base}^({exp1}+{exp2}) = {answer}",
    ]},
    "difficulty_base": 0.15,
})


TEMPLATES.append({
    "id": "exp_002",
    "topic_code": "exponents",
    "content_template": {"text": "Вычислите: $({base}^{{{exp1}}})^{{{exp2}}} / {base}^{{{exp3}}}$"},
    "generate_params": lambda: {
        "base": P.int_range_not_zero(2, 5),
        "exp1": P.int_range(1, 3), "exp2": P.int_range(2, 4),
        "exp3": P.int_range(1, 4),
    },
    "compute_answer": lambda p: str(p["base"] ** (p["exp1"] * p["exp2"] - p["exp3"])),
    "solution_template": {"steps": [
        "(a^m)^n = a^(m·n)",
        "a^(m·n) / a^k = a^(m·n - k)",
        "Ответ: {answer}",
    ]},
    "difficulty_base": 0.2,
})


TEMPLATES.append({
    "id": "exp_003",
    "topic_code": "exponents",
    "content_template": {"text": "Вычислите: $\sqrt{{{radicand}}} \times \sqrt{{{radicand}}} / {divisor}$"},
    "generate_params": lambda: _gen_radical(),
    "compute_answer": lambda p: str(p["radicand"] // p["divisor"] if p["radicand"] % p["divisor"] == 0 else round(p["radicand"] / p["divisor"], 2)),
    "solution_template": {"steps": [
        "√{radicand} × √{radicand} = {radicand}",
        "{radicand} / {divisor} = {answer}",
    ]},
    "difficulty_base": 0.15,
})

def _gen_radical():
    a = P.int_range(2, 8)
    return {"radicand": a * a, "divisor": P.choice([2, 4, a]) if a in [2, 4] else P.choice([2, 4])}


TEMPLATES.append({
    "id": "exp_004",
    "topic_code": "exponents",
    "content_template": {"text": "Вычислите: ${a}^{{{b}/{c}}}$"},
    "generate_params": lambda: {"a": P.int_range_not_zero(2, 5), "b": P.int_range(2, 4), "c": P.int_range_not_zero(2, 5)},
    "compute_answer": lambda p: _compute_fractional_pow(p),
    "solution_template": {"steps": ["a^(b/c) = (a^b)^(1/c)", "{a}^{b}/{c} = {answer}"]},
    "difficulty_base": 0.35,
})

def _compute_fractional_pow(p):
    a, b, c = p["a"], p["b"], p["c"]
    val = a ** b
    root = round(val ** (1 / c), 4)
    return str(root) if root != int(root) else str(int(root))


TEMPLATES.append({
    "id": "exp_005",
    "topic_code": "exponents",
    "content_template": {"text": "Вычислите: $\sqrt{{{n}}} + \sqrt{{{m}}}$. Ответ округлите до десятых."},
    "generate_params": lambda: {
        "n": P.choice([2, 3, 5, 6, 7, 8, 10, 12, 18, 20]),
        "m": P.choice([2, 3, 5, 6, 7, 8, 10, 12, 18, 20]),
    },
    "compute_answer": lambda p: round(math.sqrt(p["n"]) + math.sqrt(p["m"]), 1),
    "solution_template": {"steps": [
        "√{n} ≈ {sqrt_n}",
        "√{m} ≈ {sqrt_m}",
        "Сумма = {answer}",
    ]},
    "difficulty_base": 0.2,
})

# ═══════════════════════════════════════════
# 5. Логарифмы (5 шаблонов)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "log_001",
    "topic_code": "logarithms",
    "content_template": {"text": "Вычислите: $\log_{{{base}}} {arg}$"},
    "generate_params": lambda: {
        "base": P.choice([2, 3, 5, 10]),
        "exp": P.int_range(1, 5),
    },
    "compute_answer": lambda p: str(p["exp"]),
    "solution_template": {"steps": ["{base}^{exp} = {arg}", "log_{base}({arg}) = {exp}"]},
    "difficulty_base": 0.15,
})


TEMPLATES.append({
    "id": "log_002",
    "topic_code": "logarithms",
    "content_template": {"text": "Вычислите: $\log_{{{base}}} {a} + \log_{{{base}}} {b}$"},
    "generate_params": lambda: _gen_log_sum(),
    "compute_answer": lambda p: str(int(round(math.log(p["a"] * p["b"], p["base"])))),
    "solution_template": {"steps": [
        "log_b(x) + log_b(y) = log_b(x·y)",
        "log_{base}({a}·{b}) = log_{base}({product}) = {answer}",
    ]},
    "difficulty_base": 0.25,
})

def _gen_log_sum():
    base = P.choice([2, 3, 5])
    e1 = P.int_range(1, 4)
    e2 = P.int_range(1, 4)
    return {"base": base, "a": base ** e1, "b": base ** e2}


TEMPLATES.append({
    "id": "log_003",
    "topic_code": "logarithms",
    "content_template": {"text": "Вычислите: $\log_{{{base}}} ({arg}^{{{k}}})$"},
    "generate_params": lambda: {"base": P.choice([2, 3, 5]), "arg": 0, "k": P.int_range(2, 5)},
    "compute_answer": lambda p: str(p["k"]),
    "solution_template": {"steps": ["log_b(x^k) = k·log_b(x)", "k·log_{base}({arg}) = k·1 = {answer}"]},
    "difficulty_base": 0.2,
})


TEMPLATES.append({
    "id": "log_004",
    "topic_code": "logarithms",
    "content_template": {"text": "Вычислите: $\log_{{{base}}} {a} - \log_{{{base}}} {b}$"},
    "generate_params": lambda: _gen_log_sum(),
    "compute_answer": lambda p: str(int(round(math.log(p["a"] / p["b"], p["base"])))),
    "solution_template": {"steps": [
        "log_b(x) - log_b(y) = log_b(x/y)",
        "log_{base}({a}/{b}) = log_{base}({quotient}) = {answer}",
    ]},
    "difficulty_base": 0.25,
})


TEMPLATES.append({
    "id": "log_005",
    "topic_code": "logarithms",
    "content_template": {"text": "Вычислите: {base_num}^(log_{base_num}({arg_k}))"},
    "generate_params": lambda: {"base_num": P.choice([2, 3, 5, 10]), "arg_k": P.int_range(2, 10)},
    "compute_answer": lambda p: str(p["arg_k"]),
    "solution_template": {"steps": ["a^(log_a(x)) = x", "{base_num}^(log_{base_num}({arg_k})) = {arg_k}"]},
    "difficulty_base": 0.35,
})

# ═══════════════════════════════════════════
# 6. Тригонометрия (5 шаблонов)
# ═══════════════════════════════════════════

TRIG_VALUES = {0: 0, 30: 0.5, 45: 0.70710678, 60: 0.8660254, 90: 1.0}
TRIG_TABLE_SIN = {0: "0", 30: "1/2", 45: "√2/2", 60: "√3/2", 90: "1"}
TRIG_TABLE_COS = {0: "1", 30: "√3/2", 45: "√2/2", 60: "1/2", 90: "0"}
TRIG_TABLE_TG = {0: "0", 30: f"1/√3", 45: "1", 60: "√3", 90: "—"}

TEMPLATES.append({
    "id": "trig_001",
    "topic_code": "trigonometry",
    "content_template": {"text": "Вычислите $\sin({angle}°)$. Укажите точный ответ."},
    "generate_params": lambda: {"angle": P.choice([0, 30, 45, 60, 90])},
    "compute_answer": lambda p: TRIG_TABLE_SIN[p["angle"]],
    "solution_template": {"steps": ["Табличное значение sin({angle}°) = {answer}"]},
    "difficulty_base": 0.15,
})


TEMPLATES.append({
    "id": "trig_002",
    "topic_code": "trigonometry",
    "content_template": {"text": "Вычислите $\cos({angle}°)$. Укажите точный ответ."},
    "generate_params": lambda: {"angle": P.choice([0, 30, 45, 60, 90])},
    "compute_answer": lambda p: TRIG_TABLE_COS[p["angle"]],
    "solution_template": {"steps": ["Табличное значение cos({angle}°) = {answer}"]},
    "difficulty_base": 0.15,
})


TEMPLATES.append({
    "id": "trig_003",
    "topic_code": "trigonometry",
    "content_template": {"text": "Вычислите: $\sin^2({a}°) + \cos^2({a}°)$"},
    "generate_params": lambda: {"a": P.choice([30, 45, 60])},
    "compute_answer": lambda p: "1",
    "solution_template": {"steps": ["sin²x + cos²x = 1 (основное тригонометрическое тождество)"]},
    "difficulty_base": 0.15,
})


TEMPLATES.append({
    "id": "trig_004",
    "topic_code": "trigonometry",
    "content_template": {"text": "Решите уравнение: sin x = 1/{a} на промежутке [0; π/2]. Ответ в градусах."},
    "generate_params": lambda: {"a": P.choice([2])},
    "compute_answer": lambda p: "30",
    "solution_template": {"steps": [
        "sin x = 1/{a} → x = arcsin(1/{a})",
        "Табличное значение: x = 30°",
    ]},
    "difficulty_base": 0.3,
})


TEMPLATES.append({
    "id": "trig_005",
    "topic_code": "trigonometry",
    "content_template": {"text": "Вычислите $\tg({angle}°)$. Укажите точный ответ."},
    "generate_params": lambda: {"angle": P.choice([0, 30, 45, 60])},
    "compute_answer": lambda p: TRIG_TABLE_TG[p["angle"]],
    "solution_template": {"steps": ["tg = sin/cos", "tg({angle}°) = {answer}"]},
    "difficulty_base": 0.2,
})

# ═══════════════════════════════════════════
# 7. Текстовые задачи (5 шаблонов)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "word_001",
    "topic_code": "word_problems",
    "content_template": {"text": "Автомобиль проехал {d} км за {t} часов. Найдите среднюю скорость (км/ч)."},
    "generate_params": lambda: {"d": P.int_range(60, 600), "t": P.int_range(1, 8)},
    "compute_answer": lambda p: str(p["d"] / p["t"] if p["d"] % p["t"] == 0 else round(p["d"] / p["t"], 1)),
    "solution_template": {"steps": ["v = S / t = {d} / {t} = {answer} км/ч"]},
    "difficulty_base": 0.1,
})


TEMPLATES.append({
    "id": "word_002",
    "topic_code": "word_problems",
    "content_template": {"text": "Масса {n} одинаковых деталей составляет {m} кг. Найдите массу одной детали (в граммах)."},
    "generate_params": lambda: {"n": P.int_range(5, 50), "m": P.int_range(2, 20)},
    "compute_answer": lambda p: str(round(p["m"] * 1000 / p["n"], 1)),
    "solution_template": {"steps": [
        "Масса одной в кг: {m} / {n} = {per_kg} кг",
        "В граммах: {per_kg} × 1000 = {answer} г",
    ]},
    "difficulty_base": 0.1,
})


TEMPLATES.append({
    "id": "word_003",
    "topic_code": "word_problems",
    "content_template": {"text": "Расстояние между городами {d} км. Два автомобиля выехали навстречу со скоростями {v1} и {v2} км/ч. Через сколько часов они встретятся?"},
    "generate_params": lambda: {"d": P.int_range(100, 500), "v1": P.int_range(40, 90), "v2": P.int_range(40, 90)},
    "compute_answer": lambda p: _compute_meeting(p),
    "solution_template": {"steps": [
        "Скорость сближения: {v1} + {v2} = {vsum} км/ч",
        "Время = {d} / {vsum} = {answer} ч",
    ]},
    "difficulty_base": 0.2,
})

def _compute_meeting(p):
    total = p["d"] / (p["v1"] + p["v2"])
    return str(round(total, 2))


TEMPLATES.append({
    "id": "word_004",
    "topic_code": "word_problems",
    "content_template": {"text": "Цена товара {price} рублей. Скидка {pct}%. Сколько стоит товар со скидкой?"},
    "generate_params": lambda: {"price": P.int_range(500, 5000), "pct": P.choice([10, 15, 20, 25, 30, 50])},
    "compute_answer": lambda p: str(p["price"] * (100 - p["pct"]) // 100),
    "solution_template": {"steps": [
        "Скидка: {price} × {pct}% = {discount} руб",
        "Цена со скидкой: {price} - {discount} = {answer} руб",
    ]},
    "difficulty_base": 0.1,
})


TEMPLATES.append({
    "id": "word_005",
    "topic_code": "word_problems",
    "content_template": {"text": "Первая труба наполняет бак за {a} ч, вторая — за {b} ч. За сколько часов наполнится бак при совместной работе?"},
    "generate_params": lambda: {"a": P.int_range(3, 12), "b": P.int_range(4, 15)},
    "compute_answer": lambda p: str(round(p["a"] * p["b"] / (p["a"] + p["b"]), 2)),
    "solution_template": {"steps": [
        "Производительности: 1/{a} и 1/{b} бака/ч",
        "Общая: 1/{a} + 1/{b} = {total_rate} бака/ч",
        "Время = 1 / {total_rate} = {answer} ч",
    ]},
    "difficulty_base": 0.3,
})

# ═══════════════════════════════════════════
# 8. Производные (4 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "deriv_001",
    "topic_code": "derivatives",
    "content_template": {"text": "Найдите производную $f(x) = x^{{{n}}}$ в точке $x = {x0}$."},
    "generate_params": lambda: {"n": P.int_range(2, 6), "x0": P.int_range(1, 5)},
    "compute_answer": lambda p: str(p["n"] * (p["x0"] ** (p["n"] - 1))),
    "solution_template": {"steps": [
        "f'(x) = {n}·x^{n_minus_1}",
        "f'({x0}) = {n}·{x0}^{n_minus_1} = {answer}",
    ]},
    "difficulty_base": 0.2,
})


TEMPLATES.append({
    "id": "deriv_002",
    "topic_code": "derivatives",
    "content_template": {"text": "Найдите производную f(x) = {a}x^{na} + {b}x^{nb} + {c}"},
    "generate_params": lambda: {"a": P.int_range(1, 5), "na": P.int_range(1, 4), "b": P.int_range(1, 5), "nb": P.int_range(1, 3), "c": P.int_range(1, 20)},
    "compute_answer": lambda p: f"{p['a']*p['na']}x^{p['na']-1} + {p['b']*p['nb']}x^{p['nb']-1}" if p["nb"] > 1 else f"{p['a']*p['na']}x^{p['na']-1} + {p['b']*p['nb']}",
    "solution_template": {"steps": [
        "(x^n)' = n·x^(n-1), константа → 0",
        "f'(x) = {answer}",
    ]},
    "difficulty_base": 0.25,
})


TEMPLATES.append({
    "id": "deriv_003",
    "topic_code": "derivatives",
    "content_template": {"text": "Найдите $f'({x0})$ для $f(x) = {a}x^2 {sign_b} {b_abs}x {sign_c} {c_abs}$"},
    "generate_params": lambda: {"a": P.int_range(1, 4), "b": P.int_range(-10, 10), "c": P.int_range(-20, 20), "x0": P.int_range(0, 5)},
    "compute_answer": lambda p: str(2 * p["a"] * p["x0"] + p["b"]),
    "solution_template": {"steps": [
        "f'(x) = {2a}x + {b}",
        "f'({x0}) = {2a}·{x0} + {b} = {answer}",
    ]},
    "difficulty_base": 0.2,
})


TEMPLATES.append({
    "id": "deriv_004",
    "topic_code": "derivatives",
    "content_template": {"text": "Материальная точка движется по закону x(t) = {a}t² + {b}t + {c}. Найдите скорость в момент t = {t0} с."},
    "generate_params": lambda: {"a": P.int_range(1, 4), "b": P.int_range(1, 10), "c": P.int_range(0, 30), "t0": P.int_range(1, 5)},
    "compute_answer": lambda p: str(2 * p["a"] * p["t0"] + p["b"]),
    "solution_template": {"steps": [
        "v(t) = x'(t) = {2a}t + {b}",
        "v({t0}) = {answer}",
    ]},
    "difficulty_base": 0.25,
})

# ═══════════════════════════════════════════
# 9. Комбинаторика (4 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "comb_001",
    "topic_code": "combinatorics",
    "content_template": {"text": "Сколько способов выбрать {k} человек из {n}? $C_{{{n}}}^{{{k}}}$"},
    "generate_params": lambda: {"n": P.int_range(5, 15), "k": P.int_range(2, 4)},
    "compute_answer": lambda p: str(math.comb(p["n"], p["k"])),
    "solution_template": {"steps": ["C({n}, {k}) = {n}! / ({k}!·{n_k}!) = {answer}"]},
    "difficulty_base": 0.2,
})


TEMPLATES.append({
    "id": "comb_002",
    "topic_code": "combinatorics",
    "content_template": {"text": "Сколько различных трёхзначных чисел можно составить из цифр {digits} без повторений?"},
    "generate_params": lambda: _gen_digit_perm(),
    "compute_answer": lambda p: str(math.perm(len(p["digits"]), 3)),
    "solution_template": {"steps": ["Выбираем 3 цифры из {n} с учётом порядка", "A({n}, 3) = {n}·{n1}·{n2} = {answer}"]},
    "difficulty_base": 0.25,
})

def _gen_digit_perm():
    from random import sample as _sample
    digits = "".join(_sample("123456789", P.int_range(4, 7)))
    return {"digits": digits, "n": len(digits)}


TEMPLATES.append({
    "id": "comb_003",
    "topic_code": "combinatorics",
    "content_template": {"text": "В группе {n} человек. Сколькими способами можно выбрать старосту и его заместителя?"},
    "generate_params": lambda: {"n": P.int_range(8, 25)},
    "compute_answer": lambda p: str(p["n"] * (p["n"] - 1)),
    "solution_template": {"steps": ["Староста — {n} вариантов", "Заместитель — {n1} вариантов", "Всего: {n} × {n1} = {answer}"]},
    "difficulty_base": 0.2,
})


TEMPLATES.append({
    "id": "comb_004",
    "topic_code": "combinatorics",
    "content_template": {"text": "Сколько существует флагов из {n} горизонтальных полос {colors} цветов (цвета могут повторяться)?"},
    "generate_params": lambda: {"n": P.int_range(3, 5), "colors": P.int_range(3, 6)},
    "compute_answer": lambda p: str(p["colors"] ** p["n"]),
    "solution_template": {"steps": ["Каждая полоса: {colors} вариантов", "Всего: {colors}^{n} = {answer}"]},
    "difficulty_base": 0.25,
})

# ═══════════════════════════════════════════
# 10. Статистика (3 шаблона)
# ═══════════════════════════════════════════

def _gen_stats():
    n = P.int_range(5, 8)
    nums = [P.int_range(1, 20) for _ in range(n)]
    return {"data": ", ".join(str(x) for x in nums), "n": n, "nums": nums}

TEMPLATES.append({
    "id": "stat_001",
    "topic_code": "statistics",
    "content_template": {"text": "Дан ряд чисел: {data}. Найдите среднее арифметическое."},
    "generate_params": _gen_stats,
    "compute_answer": lambda p: str(round(sum(p["nums"]) / len(p["nums"]), 2)),
    "solution_template": {"steps": ["Сумма: {sum_}", "Количество чисел: {n}", "Среднее = {sum_}/{n} = {answer}"]},
    "difficulty_base": 0.15,
})


TEMPLATES.append({
    "id": "stat_002",
    "topic_code": "statistics",
    "content_template": {"text": "Дан ряд чисел: {data}. Найдите медиану."},
    "generate_params": _gen_stats,
    "compute_answer": lambda p: _compute_median(p["nums"]),
    "solution_template": {"steps": ["Упорядочиваем ряд", "Медиана — средний элемент (или среднее двух средних)"]},
    "difficulty_base": 0.2,
})

def _compute_median(nums):
    s = sorted(nums)
    n = len(s)
    if n % 2:
        return str(s[n // 2])
    return str((s[n // 2 - 1] + s[n // 2]) / 2)


TEMPLATES.append({
    "id": "stat_003",
    "topic_code": "statistics",
    "content_template": {"text": "Дан ряд чисел: {data}. Найдите размах (разность максимального и минимального)."},
    "generate_params": _gen_stats,
    "compute_answer": lambda p: str(max(p["nums"]) - min(p["nums"])),
    "solution_template": {"steps": ["max = {max_}, min = {min_}", "Размах = {answer}"]},
    "difficulty_base": 0.1,
})

# ═══════════════════════════════════════════
# 11. Рациональные уравнения (4 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "rat_001",
    "topic_code": "rational_equations",
    "content_template": {"text": "Решите уравнение: $(x + {a})/(x - {b}) = {c}$"},
    "generate_params": lambda: {"a": P.int_range(1, 10), "b": P.int_range(1, 8), "c": P.int_range(2, 6)},
    "compute_answer": lambda p: str(round((p["c"] * p["b"] + p["a"]) / (p["c"] - 1), 2)) if p["c"] != 1 else "нет решений",
    "solution_template": {"steps": ["x + {a} = {c}(x - {b})", "ОДЗ: x ≠ {b}", "x = (cb + a)/(c - 1) = {answer}"]},
    "difficulty_base": 0.35,
})

TEMPLATES.append({
    "id": "rat_002",
    "topic_code": "rational_equations",
    "content_template": {"text": "Решите уравнение: ${a}/(x - {m}) = {b}/(x + {n})$"},
    "generate_params": lambda: {"a": P.int_range(2, 8), "b": P.int_range(2, 8), "m": P.int_range(1, 5), "n": P.int_range(1, 5)},
    "compute_answer": lambda p: str(round((p["a"] * p["n"] + p["b"] * p["m"]) / (p["b"] - p["a"]), 2)) if p["b"] != p["a"] else "нет решений",
    "solution_template": {"steps": ["ОДЗ: x ≠ {m}, x ≠ -{n}", "{a}(x+{n}) = {b}(x-{m})", "x = {answer}"]},
    "difficulty_base": 0.4,
})

TEMPLATES.append({
    "id": "rat_003",
    "topic_code": "rational_equations",
    "content_template": {"text": "Решите: $(x^2 - {k})/(x - {r}) = x + {r}$ при x ≠ {r}"},
    "generate_params": lambda: {"k": P.choice([4, 9, 16, 25]), "r": P.int_range(1, 4)},
    "compute_answer": lambda p: "тождество верно при всех x ≠ {r}" if p["k"] == p["r"] ** 2 else "x = {answer}",
    "solution_template": {"steps": ["x² - {k} = (x - {r})(x + {r}) = x² - {r}²", "Верно при всех допустимых x" if "тождество" in "тождество" else ""]},
    "difficulty_base": 0.45,
})

TEMPLATES.append({
    "id": "rat_004",
    "topic_code": "rational_equations",
    "content_template": {"text": "Решите: $1/(x-{a}) + 1/(x+{a}) = {b}/{c}$"},
    "generate_params": lambda: {"a": P.int_range(2, 5), "b": P.int_range(1, 3), "c": P.int_range(2, 5)},
    "compute_answer": lambda p: str(round(math.sqrt(p["a"]**2 + 2*p["a"]*p["c"]/p["b"]) if p["b"] != 0 else 0, 2)),
    "solution_template": {"steps": ["Приводим к общему знаменателю", "(2x)/(x²-a²) = b/c", "Решаем полученное уравнение"]},
    "difficulty_base": 0.55,
})

# ═══════════════════════════════════════════
# 12. Системы уравнений (4 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "sys_001",
    "topic_code": "systems_equations",
    "content_template": {"text": "Решите систему: x + y = {s}, x - y = {d}. Найдите x + y."},
    "generate_params": lambda: {"s": P.int_range(5, 20), "d": P.int_range(1, 8)},
    "compute_answer": lambda p: str(p["s"]),
    "solution_template": {"steps": ["Складываем: 2x = {s} + {d} = {sum}", "x = {x}", "y = {s} - {x} = {y}", "x + y = {s}"]},
    "difficulty_base": 0.2,
})

TEMPLATES.append({
    "id": "sys_002",
    "topic_code": "systems_equations",
    "content_template": {"text": "Решите систему: ${a}x + {b}y = {c}$, ${d}x - {e}y = {f}$. Найдите x."},
    "generate_params": lambda: {
        "a": P.int_range(1, 4), "b": P.int_range(1, 4), "c": P.int_range(5, 30),
        "d": P.int_range(1, 4), "e": P.int_range(1, 4), "f": P.int_range(1, 15),
    },
    "compute_answer": lambda p: str(round((p["c"] * p["e"] + p["b"] * p["f"]) / (p["a"] * p["e"] + p["b"] * p["d"]), 2)),
    "solution_template": {"steps": ["Умножаем первое на {e}, второе на {b}", "Складываем, исключаем y", "x = {answer}"]},
    "difficulty_base": 0.35,
})

TEMPLATES.append({
    "id": "sys_003",
    "topic_code": "systems_equations",
    "content_template": {"text": "Решите: $x^2 + y^2 = {r2}$, $x + y = {s}$. Найдите xy."},
    "generate_params": lambda: {"s": P.int_range(3, 8), "r2": P.int_range(10, 50)},
    "compute_answer": lambda p: str((p["s"]**2 - p["r2"]) // 2),
    "solution_template": {"steps": ["(x+y)² = x² + 2xy + y²", "{s}² = {r2} + 2xy", "xy = ({s}² - {r2})/2 = {answer}"]},
    "difficulty_base": 0.4,
})

TEMPLATES.append({
    "id": "sys_004",
    "topic_code": "systems_equations",
    "content_template": {"text": "Решите: $x/y = {a}/{b}$, $x + y = {s}$. Найдите x."},
    "generate_params": lambda: {"a": P.int_range(1, 4), "b": P.int_range(1, 4), "s": P.int_range(10, 30)},
    "compute_answer": lambda p: str(round(p["s"] * p["a"] / (p["a"] + p["b"]), 1)),
    "solution_template": {"steps": ["x = {a}k, y = {b}k", "{a}k + {b}k = {s}", "k = {s}/({a}+{b})", "x = {a}k = {answer}"]},
    "difficulty_base": 0.35,
})

# ═══════════════════════════════════════════
# 13. Неравенства (4 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "ineq_001",
    "topic_code": "inequalities",
    "content_template": {"text": "Решите неравенство: ${a}x + {b} > {c}$"},
    "generate_params": lambda: {"a": P.int_range_not_zero(2, 8), "b": P.int_range(-10, 10), "c": P.int_range(0, 20)},
    "compute_answer": lambda p: f"x > {round((p['c'] - p['b']) / p['a'], 2)}" if p['a'] > 0 else f"x < {round((p['c'] - p['b']) / p['a'], 2)}",
    "solution_template": {"steps": ["{a}x > {c} - {b} = {diff}", "x > {diff}/{a} = {answer}"]},
    "difficulty_base": 0.2,
})

TEMPLATES.append({
    "id": "ineq_002",
    "topic_code": "inequalities",
    "content_template": {"text": "Решите неравенство: $(x - {x1})(x - {x2}) < 0$"},
    "generate_params": lambda: {"x1": P.int_range(-5, 3), "x2": P.int_range(2, 8)},
    "compute_answer": lambda p: f"x ∈ ({min(p['x1'], p['x2'])}; {max(p['x1'], p['x2'])})",
    "solution_template": {"steps": ["Корни: x = {x1}, x = {x2}", "Парабола вверх, < 0 между корнями"]},
    "difficulty_base": 0.25,
})

TEMPLATES.append({
    "id": "ineq_003",
    "topic_code": "inequalities",
    "content_template": {"text": "Решите: ${a}^x > {val}$"},
    "generate_params": lambda: {"a": P.choice([2, 3, 5]), "exp": P.int_range(1, 5), "val": 0},
    "compute_answer": lambda p: f"x > {int(math.log(p['val'], p['a']))}" if p['val'] > 1 else "x — любое",
    "solution_template": {"steps": ["{a}^x > {a}^{exp}", "x > {exp}"]},
    "difficulty_base": 0.3,
})

TEMPLATES.append({
    "id": "ineq_004",
    "topic_code": "inequalities",
    "content_template": {"text": "Решите: $|x - {a}| < {b}$"},
    "generate_params": lambda: {"a": P.int_range(1, 10), "b": P.int_range(2, 8)},
    "compute_answer": lambda p: f"x ∈ ({p['a'] - p['b']}; {p['a'] + p['b']})",
    "solution_template": {"steps": ["|x - {a}| < {b} ⇔ -{b} < x - {a} < {b}", "{a}-{b} < x < {a}+{b}"]},
    "difficulty_base": 0.25,
})

# ═══════════════════════════════════════════
# 14. Первообразные и интегралы (3 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "int_001",
    "topic_code": "integrals",
    "content_template": {"text": "Найдите первообразную $f(x) = x^{n}$"},
    "generate_params": lambda: {"n": P.int_range(1, 5)},
    "compute_answer": lambda p: f"x^{p['n']+1}/{p['n']+1} + C",
    "solution_template": {"steps": ["∫x^n dx = x^(n+1)/(n+1)", "F(x) = x^{n_plus}/{n_plus} + C"]},
    "difficulty_base": 0.2,
})

TEMPLATES.append({
    "id": "int_002",
    "topic_code": "integrals",
    "content_template": {"text": "Вычислите интеграл: $∫_{{{lo}}}^{{{hi}}} {a}x dx$"},
    "generate_params": lambda: {"a": P.int_range(1, 5), "lo": P.int_range(0, 3), "hi": P.int_range(3, 6)},
    "compute_answer": lambda p: str(p["a"] * (p["hi"]**2 - p["lo"]**2) // 2),
    "solution_template": {"steps": ["∫ax dx = ax²/2", "Подставляем пределы: {a}·{hi}²/2 - {a}·{lo}²/2 = {answer}"]},
    "difficulty_base": 0.3,
})

TEMPLATES.append({
    "id": "int_003",
    "topic_code": "integrals",
    "content_template": {"text": "Найдите площадь под $f(x) = {k}x$ на [0; {b}]"},
    "generate_params": lambda: {"k": P.int_range(1, 4), "b": P.int_range(2, 6)},
    "compute_answer": lambda p: str(p["k"] * p["b"]**2 // 2),
    "solution_template": {"steps": ["S = ∫₀ᵇ kx dx = kx²/2|₀ᵇ", "S = {k}·{b}²/2 = {answer}"]},
    "difficulty_base": 0.3,
})

# ═══════════════════════════════════════════
# 15. Планиметрия (4 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "geom1_001",
    "topic_code": "geometry_planimetry",
    "content_template": {"text": "В прямоугольном треугольнике катеты {a} и {b}. Найдите гипотенузу."},
    "generate_params": lambda: {"a": P.int_range(3, 8), "b": P.int_range(4, 12)},
    "compute_answer": lambda p: str(round(math.sqrt(p["a"]**2 + p["b"]**2), 1)),
    "solution_template": {"steps": ["c² = a² + b²", "c = √({a}² + {b}²) = √{sumsq} = {answer}"]},
    "difficulty_base": 0.2,
})

TEMPLATES.append({
    "id": "geom1_002",
    "topic_code": "geometry_planimetry",
    "content_template": {"text": "Найдите площадь треугольника с основанием {b} и высотой {h}."},
    "generate_params": lambda: {"b": P.int_range(4, 15), "h": P.int_range(3, 10)},
    "compute_answer": lambda p: str(p["b"] * p["h"] // 2) if (p["b"] * p["h"]) % 2 == 0 else str(round(p["b"] * p["h"] / 2, 1)),
    "solution_template": {"steps": ["S = (b · h) / 2", "S = {b} · {h} / 2 = {answer}"]},
    "difficulty_base": 0.15,
})

TEMPLATES.append({
    "id": "geom1_003",
    "topic_code": "geometry_planimetry",
    "content_template": {"text": "Найдите площадь круга с радиусом $R = {r}$."},
    "generate_params": lambda: {"r": P.int_range(2, 8)},
    "compute_answer": lambda p: str(round(math.pi * p["r"]**2, 1)),
    "solution_template": {"steps": ["S = πR²", "S = π · {r}² ≈ {answer}"]},
    "difficulty_base": 0.15,
})

TEMPLATES.append({
    "id": "geom1_004",
    "topic_code": "geometry_planimetry",
    "content_template": {"text": "В треугольнике ABC угол C = 90°, sin A = {num}/{den}. Найдите cos A."},
    "generate_params": lambda: {"num": P.int_range(1, 4), "den": P.int_range(3, 5)},
    "compute_answer": lambda p: simplify_fraction(int(math.sqrt(p["den"]**2 - p["num"]**2)), p["den"]),
    "solution_template": {"steps": ["sin²A + cos²A = 1", "cos²A = 1 - {num}²/{den}²", "cos A = √(...)/{den} = {answer}"]},
    "difficulty_base": 0.3,
})

# ═══════════════════════════════════════════
# 16. Стереометрия (3 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "geom2_001",
    "topic_code": "geometry_stereometry",
    "content_template": {"text": "Найдите объём куба с ребром {a}."},
    "generate_params": lambda: {"a": P.int_range(2, 10)},
    "compute_answer": lambda p: str(p["a"] ** 3),
    "solution_template": {"steps": ["V = a³", "V = {a}³ = {answer}"]},
    "difficulty_base": 0.1,
})

TEMPLATES.append({
    "id": "geom2_002",
    "topic_code": "geometry_stereometry",
    "content_template": {"text": "Найдите объём цилиндра с радиусом основания $R = {r}$ и высотой $h = {h}$."},
    "generate_params": lambda: {"r": P.int_range(2, 5), "h": P.int_range(3, 10)},
    "compute_answer": lambda p: str(round(math.pi * p["r"]**2 * p["h"], 1)),
    "solution_template": {"steps": ["V = πR²h", "V = π · {r}² · {h} ≈ {answer}"]},
    "difficulty_base": 0.2,
})

TEMPLATES.append({
    "id": "geom2_003",
    "topic_code": "geometry_stereometry",
    "content_template": {"text": "Найдите площадь поверхности шара радиуса $R = {r}$."},
    "generate_params": lambda: {"r": P.int_range(2, 6)},
    "compute_answer": lambda p: str(round(4 * math.pi * p["r"]**2, 1)),
    "solution_template": {"steps": ["S = 4πR²", "S = 4π · {r}² ≈ {answer}"]},
    "difficulty_base": 0.15,
})

# ═══════════════════════════════════════════
# 17. Графики функций (3 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "graph_001",
    "topic_code": "graphs",
    "content_template": {"text": "Найдите координаты вершины параболы $y = x^2 - {b}x + {c}$."},
    "generate_params": lambda: {"b": P.int_range(2, 10), "c": P.int_range(1, 15)},
    "compute_answer": lambda p: f"x₀ = {p['b']/2}, y₀ = {p['c'] - p['b']**2/4}",
    "solution_template": {"steps": ["x₀ = -b/2a = {b}/2 = {bx}", "y₀ = c - b²/4a = {c} - {b}²/4 = {by}"]},
    "difficulty_base": 0.25,
})

TEMPLATES.append({
    "id": "graph_002",
    "topic_code": "graphs",
    "content_template": {"text": "Найдите точки пересечения $y = {k}x + {m}$ с осью OX."},
    "generate_params": lambda: {"k": P.int_range_not_zero(1, 5), "m": P.int_range(-10, 10)},
    "compute_answer": lambda p: str(round(-p["m"] / p["k"], 2)),
    "solution_template": {"steps": ["y = 0: {k}x + {m} = 0", "x = -{m}/{k} = {answer}"]},
    "difficulty_base": 0.15,
})

TEMPLATES.append({
    "id": "graph_003",
    "topic_code": "graphs",
    "content_template": {"text": "Функция задана графиком. $f({a}) = {fa}$, $f({b}) = {fb}$. Найдите $f({a}) + f({b})$."},
    "generate_params": lambda: {"a": P.int_range(1, 5), "fa": P.int_range(1, 10), "b": P.int_range(6, 10), "fb": P.int_range(1, 10)},
    "compute_answer": lambda p: str(p["fa"] + p["fb"]),
    "solution_template": {"steps": ["f({a}) = {fa}, f({b}) = {fb}", "Сумма = {fa} + {fb} = {answer}"]},
    "difficulty_base": 0.2,
})

# ═══════════════════════════════════════════
# 18. Финансовая математика (3 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "fin_001",
    "topic_code": "financial_math",
    "content_template": {"text": "Вклад {sum_} руб. под {pct}% годовых. Сколько будет через год?"},
    "generate_params": lambda: {"sum_": P.int_range(10000, 100000), "pct": P.choice([5, 8, 10, 12, 15])},
    "compute_answer": lambda p: str(int(p["sum_"] * (1 + p["pct"] / 100))),
    "solution_template": {"steps": ["S = S₀(1 + r)", "S = {sum_} · (1 + {pct}/100) = {answer}"]},
    "difficulty_base": 0.15,
})

TEMPLATES.append({
    "id": "fin_002",
    "topic_code": "financial_math",
    "content_template": {"text": "Кредит {sum_} руб. на {n} года под {pct}% годовых. Найдите переплату (простые проценты)."},
    "generate_params": lambda: {"sum_": P.int_range(50000, 300000), "n": P.choice([2, 3, 5]), "pct": P.choice([10, 12, 15])},
    "compute_answer": lambda p: str(int(p["sum_"] * p["pct"] / 100 * p["n"])),
    "solution_template": {"steps": ["Переплата = S₀ · r · n", "= {sum_} · {pct}/100 · {n} = {answer}"]},
    "difficulty_base": 0.2,
})

TEMPLATES.append({
    "id": "fin_003",
    "topic_code": "financial_math",
    "content_template": {"text": "Цена товара {price} руб. Снизили на {d1}%, потом ещё на {d2}%. Найдите конечную цену."},
    "generate_params": lambda: {"price": P.int_range(1000, 10000), "d1": P.choice([10, 20, 30]), "d2": P.choice([5, 10, 15])},
    "compute_answer": lambda p: str(int(p["price"] * (1 - p["d1"]/100) * (1 - p["d2"]/100))),
    "solution_template": {"steps": [
        "После первого снижения: {price} · (1 - {d1}/100) = {p1}",
        "После второго: {p1} · (1 - {d2}/100) = {answer}",
    ]},
    "difficulty_base": 0.25,
})

# ═══════════════════════════════════════════
# 19. Оптимизация (3 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "opt_001",
    "topic_code": "optimization",
    "content_template": {"text": "Найдите максимум функции $f(x) = -x^2 + {b}x + {c}$ на отрезке [0; {end}]."},
    "generate_params": lambda: {"b": P.int_range(4, 12), "c": P.int_range(1, 10), "end": P.int_range(5, 10)},
    "compute_answer": lambda p: str(max(p["c"], -p["end"]**2 + p["b"]*p["end"] + p["c"], -0.25*(p["b"]**2) + p["b"]*p["b"]/2 + p["c"])),
    "solution_template": {"steps": ["Вершина: x₀ = {b}/2 = {bx}", "f(x₀) = -{bx}² + {b}·{bx} + {c} = {fv}", "Сравниваем с концами отрезка"]},
    "difficulty_base": 0.4,
})

TEMPLATES.append({
    "id": "opt_002",
    "topic_code": "optimization",
    "content_template": {"text": "Найдите минимум $f(x) = x^2 - {b}x + {c}$."},
    "generate_params": lambda: {"b": P.int_range(4, 12), "c": P.int_range(5, 20)},
    "compute_answer": lambda p: str(p["c"] - p["b"]**2 // 4),
    "solution_template": {"steps": ["Вершина параболы: x₀ = {b}/2", "f(x₀) = {c} - {b}²/4 = {answer}"]},
    "difficulty_base": 0.3,
})

TEMPLATES.append({
    "id": "opt_003",
    "topic_code": "optimization",
    "content_template": {"text": "Периметр прямоугольника {p} см. Найдите максимальную площадь."},
    "generate_params": lambda: {"p": P.int_range(20, 60)},
    "compute_answer": lambda p: str((p["p"] // 4) ** 2),
    "solution_template": {"steps": ["При фиксированном периметре макс. площадь у квадрата", "Сторона = {p}/4 = {side}", "S = {side}² = {answer}"]},
    "difficulty_base": 0.3,
})

# ═══════════════════════════════════════════
# 20. Задачи с параметром (3 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "par_001",
    "topic_code": "parameters",
    "content_template": {"text": "При каких $a$ уравнение ${k}x + a = {m}$ имеет корень $x = {x0}$?"},
    "generate_params": lambda: {"k": P.int_range_not_zero(2, 5), "m": P.int_range(5, 20), "x0": P.int_range(1, 5)},
    "compute_answer": lambda p: str(p["m"] - p["k"] * p["x0"]),
    "solution_template": {"steps": ["При x = {x0}: {k}·{x0} + a = {m}", "a = {m} - {k}·{x0} = {answer}"]},
    "difficulty_base": 0.35,
})

TEMPLATES.append({
    "id": "par_002",
    "topic_code": "parameters",
    "content_template": {"text": "При каких $a$ уравнение $x^2 + {a_val}x + 1 = 0$ имеет один корень?"},
    "generate_params": lambda: {"a_val": 0},
    "compute_answer": lambda p: "a = 2 или a = -2",
    "solution_template": {"steps": ["D = a² - 4 = 0", "a² = 4", "a = ±2"]},
    "difficulty_base": 0.4,
})

TEMPLATES.append({
    "id": "par_003",
    "topic_code": "parameters",
    "content_template": {"text": "При каких $a$ система $x + y = a$, $x - y = {d}$ имеет решение $(x,y)$, где $x > 0$, $y > 0$?"},
    "generate_params": lambda: {"d": P.int_range(2, 8)},
    "compute_answer": lambda p: f"a > {p['d']}",
    "solution_template": {"steps": ["x = (a + {d})/2, y = (a - {d})/2", "x > 0: a > -{d}", "y > 0: a > {d}", "Ответ: a > {d}"]},
    "difficulty_base": 0.5,
})

# ═══════════════════════════════════════════
# 21. Теория чисел (3 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "num_001",
    "topic_code": "number_theory",
    "content_template": {"text": "Найдите наибольший общий делитель (НОД) чисел {a} и {b}."},
    "generate_params": lambda: {"a": P.int_range(12, 96), "b": P.int_range(12, 96)},
    "compute_answer": lambda p: str(math.gcd(p["a"], p["b"])),
    "solution_template": {"steps": ["Разложение: {a} = ..., {b} = ...", "Наибольший общий делитель = {answer}"]},
    "difficulty_base": 0.2,
})

TEMPLATES.append({
    "id": "num_002",
    "topic_code": "number_theory",
    "content_template": {"text": "Найдите наименьшее общее кратное (НОК) чисел {a} и {b}."},
    "generate_params": lambda: {"a": P.int_range(6, 36), "b": P.int_range(6, 36)},
    "compute_answer": lambda p: str(p["a"] * p["b"] // math.gcd(p["a"], p["b"])),
    "solution_template": {"steps": ["НОК(a,b) = a·b / НОД(a,b)", "Наименьшее общее кратное = {a}·{b}/{gcd} = {answer}"]},
    "difficulty_base": 0.2,
})

TEMPLATES.append({
    "id": "num_003",
    "topic_code": "number_theory",
    "content_template": {"text": "Найдите остаток от деления {a} на {b}."},
    "generate_params": lambda: {"a": P.int_range(50, 200), "b": P.int_range(3, 12)},
    "compute_answer": lambda p: str(p["a"] % p["b"]),
    "solution_template": {"steps": ["{a} ÷ {b} = {div} (ост. {answer})"]},
    "difficulty_base": 0.1,
})

# ═══════════════════════════════════════════
# 22. Последовательности (3 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "seq_001",
    "topic_code": "sequences",
    "content_template": {"text": "Арифметическая прогрессия: $a_1 = {a1}$, $d = {d}$. Найдите $a_{{{n}}}$."},
    "generate_params": lambda: {"a1": P.int_range(1, 10), "d": P.int_range(1, 5), "n": P.int_range(5, 15)},
    "compute_answer": lambda p: str(p["a1"] + (p["n"] - 1) * p["d"]),
    "solution_template": {"steps": ["aₙ = a₁ + (n-1)d", "a_{n} = {a1} + {n1}·{d} = {answer}"]},
    "difficulty_base": 0.2,
})

TEMPLATES.append({
    "id": "seq_002",
    "topic_code": "sequences",
    "content_template": {"text": "Геометрическая прогрессия: $b_1 = {b1}$, $q = {q}$. Найдите $b_{{{n}}}$."},
    "generate_params": lambda: {"b1": P.int_range(1, 3), "q": P.int_range(2, 4), "n": P.int_range(3, 7)},
    "compute_answer": lambda p: str(p["b1"] * (p["q"] ** (p["n"] - 1))),
    "solution_template": {"steps": ["bₙ = b₁ · q^(n-1)", "b_{n} = {b1} · {q}^{n1} = {answer}"]},
    "difficulty_base": 0.25,
})

TEMPLATES.append({
    "id": "seq_003",
    "topic_code": "sequences",
    "content_template": {"text": "Арифметическая прогрессия: $a_3 = {a3}$, $a_7 = {a7}$. Найдите $d$."},
    "generate_params": lambda: {"a3": P.int_range(5, 15), "a7": P.int_range(15, 35)},
    "compute_answer": lambda p: str((p["a7"] - p["a3"]) / 4),
    "solution_template": {"steps": ["a₇ = a₃ + 4d", "4d = {a7} - {a3} = {diff}", "d = {diff}/4 = {answer}"]},
    "difficulty_base": 0.3,
})

# ═══════════════════════════════════════════
# 23. Векторы (3 шаблона)
# ═══════════════════════════════════════════

TEMPLATES.append({
    "id": "vec_001",
    "topic_code": "vectors",
    "content_template": {"text": "Даны векторы $\\vec{{a}}({x1};{y1})$ и $\\vec{{b}}({x2};{y2})$. Найдите их скалярное произведение."},
    "generate_params": lambda: {"x1": P.int_range(1, 5), "y1": P.int_range(1, 5), "x2": P.int_range(1, 5), "y2": P.int_range(1, 5)},
    "compute_answer": lambda p: str(p["x1"] * p["x2"] + p["y1"] * p["y2"]),
    "solution_template": {"steps": ["a·b = x₁x₂ + y₁y₂", "= {x1}·{x2} + {y1}·{y2} = {answer}"]},
    "difficulty_base": 0.15,
})

TEMPLATES.append({
    "id": "vec_002",
    "topic_code": "vectors",
    "content_template": {"text": "Найдите длину вектора $\\vec{{a}}({x};{y})$."},
    "generate_params": lambda: {"x": P.int_range(3, 8), "y": P.int_range(4, 12)},
    "compute_answer": lambda p: str(round(math.sqrt(p["x"]**2 + p["y"]**2), 1)),
    "solution_template": {"steps": ["|a| = √(x² + y²)", "= √({x}² + {y}²) = √{sumsq} = {answer}"]},
    "difficulty_base": 0.15,
})

TEMPLATES.append({
    "id": "vec_003",
    "topic_code": "vectors",
    "content_template": {"text": "Найдите сумму векторов $\\vec{{a}}({x1};{y1})$ и $\\vec{{b}}({x2};{y2})$."},
    "generate_params": lambda: {"x1": P.int_range(1, 5), "y1": P.int_range(1, 5), "x2": P.int_range(1, 5), "y2": P.int_range(1, 5)},
    "compute_answer": lambda p: f"({p['x1']+p['x2']}; {p['y1']+p['y2']})",
    "solution_template": {"steps": ["a + b = (x₁+x₂; y₁+y₂)", "= ({x1}+{x2}; {y1}+{y2}) = {answer}"]},
    "difficulty_base": 0.1,
})
