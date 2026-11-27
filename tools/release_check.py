"""Checklist verificavel do checkout/demo; nao declara QA humano aprovado."""
import json
import re
import subprocess

from demo import ROOT, STATE, cli, compose, salvar


def verificar_segredos():
    arquivos = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT,
    ).decode().split("\0")
    padroes = [r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
               r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
               r"\bAKIA[A-Z0-9]{16}\b"]
    falhas = []
    for nome in filter(None, arquivos):
        path = ROOT / nome
        if path.name == ".env" or nome.startswith(".demo/"):
            falhas.append(nome)
        if path.suffix.lower() in (".png", ".jpg", ".pdf", ".zip"):
            continue
        texto = path.read_text(encoding="utf-8", errors="replace")
        if any(re.search(p, texto) for p in padroes):
            falhas.append(nome)
    if falhas:
        # Somente nomes; nunca imprimir o segredo encontrado.
        raise RuntimeError("RELEASE_SEGREDO_DETECTADO: " + ", ".join(falhas))


def main():
    verificar_segredos()
    # Confere configuracao efetivamente carregada, sem exibir seus valores.
    php = '''
    echo json_encode([
        'debug_off' => !WP_DEBUG && !WP_DEBUG_DISPLAY && !WP_DEBUG_LOG,
        'file_edit_off' => DISALLOW_FILE_EDIT,
        'preview_off' => !AgroTracer_Bridge::allow_offline_preview(),
        'secret_set' => strlen(getenv('AGROTRACER_API_HMAC_SECRET')) >= 32,
        'php_display_off' => !filter_var(
            ini_get('display_errors'), FILTER_VALIDATE_BOOLEAN),
    ]);
    '''
    resultado = json.loads(cli("eval", php).stdout)
    assert all(resultado.values()), "RELEASE_CONFIG_INVALID"
    uid = compose("exec", "-T", "api", "id", "-u").stdout.strip()
    assert uid != b"0", "RELEASE_API_ROOT"
    resultado.update({
        "api_non_root": True, "checkout_secret_patterns": True,
        "qa_humano": "PENDENTE", "tag_autorizada": False,
        "limite": "Demo local/padroes selecionados; exclui historico Git",
    })
    salvar(STATE / "release-check.json", json.dumps(resultado, indent=2))
    print(json.dumps(resultado))


if __name__ == "__main__":
    main()
