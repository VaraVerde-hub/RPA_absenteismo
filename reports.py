"""Local CSV reports. Output folder must stay outside version control."""
from pathlib import Path
from datetime import datetime, timezone

def salvar_relatorios(resumo, detalhado, pasta):
    target = Path(pasta)
    target.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    paths = [target / ("resumo_" + timestamp + ".csv"),
             target / ("detalhado_" + timestamp + ".csv")]
    resumo.to_csv(paths[0], index=False, encoding="utf-8-sig")
    detalhado.to_csv(paths[1], index=False, encoding="utf-8-sig")
    return paths
