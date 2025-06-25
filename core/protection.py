from flask import request, jsonify
from graphql import parse

# Configura tus límites
MAX_BATCH_SIZE = 5
MAX_DEPTH = 3
MAX_FIELD_DUPLICATION = 2

FIELD_COSTS = {
    "systemUpdate": 10, 
}
MAX_TOTAL_COST = 5

def get_fields_and_depth(query):
    try:
        ast = parse(query)
        fields = []
        max_depth = 0
        def walk(selection_set, depth):
            nonlocal max_depth
            if depth > max_depth:
                max_depth = depth
            for selection in selection_set.selections:
                if hasattr(selection, "name"):
                    fields.append(selection.name.value)
                if hasattr(selection, "selection_set") and selection.selection_set:
                    walk(selection.selection_set, depth + 1)
        for definition in ast.definitions:
            if hasattr(definition, "selection_set") and definition.selection_set:
                walk(definition.selection_set, 1)
        return fields, max_depth
    except Exception:
        return [], 0

def cost_exceeded(fields):
    total_cost = 0
    for field in fields:
        total_cost += FIELD_COSTS.get(field, 1)  # Por defecto, cada campo cuesta 1
        if total_cost > MAX_TOTAL_COST:
            return True
    return False

def graphql_protection():
    if request.path == "/graphql" and request.method == "POST":
        data = request.get_json(force=True)
        # Batch check
        if isinstance(data, list):
            if len(data) > MAX_BATCH_SIZE:
                return jsonify({"error": f"Batch size too large. Max allowed is {MAX_BATCH_SIZE}."}), 429
            queries = [q.get('query', '') for q in data]
        else:
            queries = [data.get('query', '')]

        for q in queries:
            fields, depth = get_fields_and_depth(q)
            # Depth check
            if depth > MAX_DEPTH:
                return jsonify({"error": f"Query depth too high. Max allowed is {MAX_DEPTH}."}), 429
            # Field duplication check
            for field in set(fields):
                if fields.count(field) > MAX_FIELD_DUPLICATION:
                    return jsonify({"error": f"Field '{field}' duplicated too many times."}), 429
            # Cost check
            if cost_exceeded(fields):
                return jsonify({"error": "Query cost too high. One or more operations exceed the allowed weight."}), 430