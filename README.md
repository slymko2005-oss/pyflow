# PyFlow - Model workflowu i planowanie grafu

PyFlow to biblioteka do definiowania oraz planowania przepływów danych (DAG).

## Instalacja

`ash
python -m venv .venv
source .venv/bin/activate  # Lub .venv\Scripts\Activate.ps1 na Windows
pip install -e '.[dev]'
``n
## Uruchamianie testów

`ash
python -m pytest
``n
## Wybór algorytmu i złożoność
- **Porządek topologiczny:** Algorytm Kahna z posortowaną listą gotowych węzłów zapewniający deterministyczną (alfabetyczną) kolejność. Złożoność: (V + E \log V)$.
- **Wykrywanie cykli i walidacja:** Przeszukiwanie w głąb (DFS) z użyciem 3 stanów. Złożoność: (V + E)$.
