import sys
from types import SimpleNamespace
import pandas as pd

def test_dry_run_does_not_send(monkeypatch, tmp_path):
    import main
    import db
    import email_sender
    monkeypatch.setattr(db, "buscar_registros", lambda dias=None: pd.DataFrame(columns=[
        "funcionario_id", "nome", "data", "horario_entrada_esperado",
        "horario_saida_esperado", "hora_entrada", "hora_saida"]))
    def forbidden(*a, **kw):
        raise AssertionError("SMTP should not be used during dry-run")
    monkeypatch.setattr(email_sender, "enviar_relatorio", forbidden)
    assert main.executar(["--output", str(tmp_path)]) == 0
    assert (tmp_path / "runs.jsonl").is_file()
