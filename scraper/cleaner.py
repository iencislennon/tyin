def clean(products: list[dict]) -> list[dict]:
    cleaned = []
    seen = set()

    for p in products:
        # Убираем дубли по имени
        key = f"{p['bank']}_{p['name']}"
        if key in seen:
            continue
        seen.add(key)

        # Убираем продукты без имени
        if not p.get("name"):
            continue

        # Убираем продукты где вообще нет числовых данных
        has_data = any([
            p.get("annual_rate_min"),
            p.get("max_sum"),
            p.get("max_months"),
        ])
        if not has_data:
            continue

        cleaned.append(p)

    return cleaned