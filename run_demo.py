import csv
import json
from pyflow import Task, Workflow, run

def read_csv_task(inputs, params):
    file_path = params["file_path"]
    rows = []
    # utf-8-sig automatycznie usuwa BOM z pliku CSV
    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print("[1] Odczytano wiersze z CSV:", rows)
    return rows

def clean_data_task(inputs, params):
    raw_data = inputs["read_csv"]
    cleaned = []
    for row in raw_data:
        try:
            # Pobieramy wartość id bez względu na ewentualne białe znaki czy BOM w nazwie kolumny
            row_clean = {k.strip().replace("\ufeff", ""): v for k, v in row.items()}
            val = float(row_clean["value"])
            cleaned.append({
                "id": int(row_clean["id"]),
                "category": row_clean["category"],
                "value": val
            })
        except (ValueError, KeyError):
            pass
    print("[2] Oczyszczono dane:", cleaned)
    return cleaned

def aggregate_task(inputs, params):
    cleaned_data = inputs["clean_data"]
    summary = {}
    for row in cleaned_data:
        cat = row["category"]
        summary[cat] = summary.get(cat, 0.0) + row["value"]
    print("[3] Zaggregowano dane:", summary)
    return summary

def report_json_task(inputs, params):
    summary = inputs["aggregate"]
    report = {
        "status": "SUCCESS",
        "summary": summary
    }
    json_output = json.dumps(report, indent=4, ensure_ascii=False)
    print("[4] Wygenerowano raport JSON:")
    print(json_output)
    return json_output

if __name__ == "__main__":
    wf = Workflow()
    wf.add_task(Task(name="read_csv", function=read_csv_task, params={"file_path": "data.csv"}))
    wf.add_task(Task(name="clean_data", function=clean_data_task, dependencies=frozenset(["read_csv"])))
    wf.add_task(Task(name="aggregate", function=aggregate_task, dependencies=frozenset(["clean_data"])))
    wf.add_task(Task(name="report", function=report_json_task, dependencies=frozenset(["aggregate"])))

    print("--- URUCHOMIENIE WORKFLOW END-TO-END ---")
    result = run(wf)
    print("--- WYNIK WYKONANIA ---")
    print(f"Sukces całego workflow: {result.succeeded}")
    print("Czasy i statusy zadań:", result.task_states)

