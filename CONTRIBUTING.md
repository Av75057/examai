# Contributing to ExamAI

## Как начать

1. Форкните репозиторий → `git clone`
2. Установите зависимости: `make install`
3. Запустите: `make dev`
4. Найдите задачу с лейблом `good first issue`

## Правила

- **1 PR = 1 логическое изменение**
- Ветки живут ≤ 3 дней
- Merge только через PR
- Ветка удаляется после merge

### Ветвление

```
main (protected)
 ├── feat/xxx        # новая фича
 ├── fix/xxx         # багфикс
 ├── chore/xxx       # инфра, зависимости
 ├── docs/xxx        # документация
 └── refactor/xxx    # рефакторинг
```

### Conventional Commits

```
feat(exam): add FIPI scoring scale
fix(ai): handle DeepSeek timeout with retry
chore(infra): add GitHub Actions CI
docs(readme): add deployment checklist
```

**Формат:** `<type>(<scope>): <description>`

| Тип | Когда |
|-----|-------|
| `feat` | Новая функциональность |
| `fix` | Исправление бага |
| `docs` | Только документация |
| `refactor` | Рефакторинг |
| `chore` | Сборка, CI, зависимости |

**Scope:** `backend`, `frontend`, `bot`, `infra`, `docs`, `admin`, `exam`, `ai`

## Code Style

- **Python:** ruff (line-length 100), type hints обязательны
- **TypeScript:** ESLint + Prettier, `strict: true`

## Перед пушем

```bash
make lint    # ruff + eslint
```

## Вопросы

Открывайте [Discussion](https://github.com/Av75057/examai/discussions) или Issue с лейблом `question`.
