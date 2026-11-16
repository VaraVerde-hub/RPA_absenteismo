"""CLI orchestration. Default is dry-run; no SMTP traffic unless --send."""
import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

def executar(argv=None):
    parser = argparse.ArgumentParser(description="Daily absence report")
    parser.add_argument("--send", action="store_true", help="Explicitly allow SMTP delivery")
    parser.add_argument("--days", type=int, default=None)
    parser.add_argument("--output", default="output", help="Local, private CSV output folder")
    args = parser.parse_args(argv)
    load_dotenv()
    import db
    import absenteismo
    import email_sender
    from reports import salvar_relatorios
    logger = logging.getLogger("absenteismo")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    inicio = datetime.now(timezone.utc)
    status = "error"
    total = 0
    try:
        df = db.buscar_registros(dias=args.days)
        calculado = absenteismo.calcular_absenteismo(df)
        resumo = absenteismo.resumir_por_funcionario(calculado)
        total = len(calculado)
        caminhos = salvar_relatorios(resumo, calculado, args.output)
        logger.info("Report generated: records=%s files=%s", total, list(caminhos))
        if args.send:
            email_sender.enviar_relatorio(resumo, calculado)
            logger.info("SMTP delivery succeeded")
        else:
            logger.info("Dry-run: no email sent")
        status = "success"
        return 0
    except Exception:
        logger.exception("Report execution failed")
        return 1
    finally:
        # No names, emails, DB URLs or employee-level data in log.
        out = Path(args.output)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "runs.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"started_utc": inicio.isoformat(), "status": status,
                                "rows": total, "smtp_requested": args.send}) + "\n")

if __name__ == "__main__":
    sys.exit(executar())
