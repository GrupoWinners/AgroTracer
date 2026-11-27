"""Do clone a demo local: somente stdlib Python e Docker Compose."""
import argparse
import hashlib
import hmac
import http.cookiejar
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
import urllib.parse
import urllib.request
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".demo"


def salvar(path, valor):
    with path.open("w", encoding="utf-8") as arquivo:
        os.chmod(path, 0o600)
        arquivo.write(valor)


def compose(*args, permitido=False):
    comando = ["docker", "compose", "--env-file", str(STATE / ".env"),
               "-p", "agrotracer-s7-demo", "-f",
               str(ROOT / "ops/demo/compose.yaml"), *args]
    retorno = subprocess.run(comando, capture_output=True, timeout=900)
    if retorno.returncode and not permitido:
        raise RuntimeError("DEMO_COMPOSE_FALHOU: " + args[0]
                           + "; confira Docker/portas, sem publicar .demo")
    return retorno


def cli(*args, permitido=False):
    return compose("run", "--rm", "-T", "cli", *args, permitido=permitido)


def esperar(funcao):
    for _ in range(60):
        try:
            return funcao()
        except Exception:
            time.sleep(2)
    raise RuntimeError("DEMO_SERVICO_INDISPONIVEL")


def carregar():
    return dict(linha.split("=", 1) for linha in
                (STATE / ".env").read_text().splitlines() if "=" in linha)


def preparar():
    STATE.mkdir(mode=0o700, exist_ok=True)
    if not (STATE / ".env").exists():
        valores = {k: secrets.token_hex(32) for k in (
            "DEMO_DB_PASSWORD", "DEMO_WP_DB_PASSWORD",
            "DEMO_WP_ROOT_PASSWORD", "DEMO_HMAC", "DEMO_LOGIN_PASSWORD",
        )}
        valores.update(DEMO_API_PORT="18000", DEMO_WP_PORT="18080")
        salvar(STATE / ".env", "\n".join(
            f"{k}={v}" for k, v in valores.items()) + "\n")
    env = carregar()
    print("Preparando containers isolados da demo (primeiro build pode demorar).",
          flush=True)
    compose("up", "-d", "--build", "--wait", "--wait-timeout", "180")
    compose("exec", "-T", "api", "python", "-m", "alembic", "upgrade", "head")
    wp = "http://127.0.0.1:" + env["DEMO_WP_PORT"]
    esperar(lambda: compose("exec", "-T", "wordpress", "test", "-f",
                            "/var/www/html/wp-config.php"))
    if cli("core", "is-installed", permitido=True).returncode:
        cli("core", "install", "--url=" + wp, "--title=AgroTracer SYNTHETIC",
            "--admin_user=agro_demo", "--admin_password="
            + env["DEMO_LOGIN_PASSWORD"], "--admin_email=demo@example.invalid",
            "--skip-email")
    cli("plugin", "activate", "agrotracer-bridge")
    cli("rewrite", "structure", "/%postname%/", "--hard")
    usuario = int(cli("user", "get", "agro_demo", "--field=ID").stdout)
    resultado = compose("exec", "-T", "api", "python", "-m", "app.demo_seed",
                        "--wp-user-id", str(usuario))
    seed = json.loads(resultado.stdout)
    acesso = STATE / "acesso.json"
    if seed["criado"]:
        salvar(acesso, json.dumps({"wordpress": wp, "usuario": "agro_demo",
                                  "senha": env["DEMO_LOGIN_PASSWORD"],
                                   "wp_user_id": usuario, **seed}, indent=2))
    elif not acesso.exists():
        raise RuntimeError(
            "DEMO_ACESSO_AUSENTE: token nao e recuperavel do banco")
    print("Demo pronta: " + wp + "/agrotracer/")
    print("Acesso e token sinteticos somente no arquivo privado .demo/acesso.json")


def verificar():
    env = carregar()
    acesso = json.loads((STATE / "acesso.json").read_text())
    wp = acesso["wordpress"]
    cookies = http.cookiejar.CookieJar()
    cliente = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies))
    cliente.open(wp + "/wp-login.php", timeout=20).read()
    cliente.open(wp + "/wp-login.php", data=urllib.parse.urlencode({
        "log": acesso["usuario"], "pwd": acesso["senha"], "testcookie": "1",
        "redirect_to": wp + "/wp-admin/",
    }).encode(), timeout=20).read()
    assert any(c.name.startswith("wordpress_logged_in_") for c in cookies)
    # WordPress real -> cliente PHP da Bridge -> HMAC -> API -> PostgreSQL.
    php = (f'wp_set_current_user({acesso["wp_user_id"]}); '
           '$r=rest_do_request(new WP_REST_Request("GET", '
           '"/agrotracer/v1/fazendas")); '
           'echo json_encode(["status"=>$r->get_status(),'
           '"data"=>$r->get_data()]);')
    bridge = json.loads(cli("eval", php).stdout)
    assert bridge["status"] == 200
    assert "Fazenda SYNTHETIC S7" in json.dumps(bridge["data"])
    api = "http://127.0.0.1:" + env["DEMO_API_PORT"]
    token = urllib.parse.urlencode({"token": acesso["token"]})
    publico = json.load(cliente.open(
        api + "/api/v1/certificados/publico?" + token))
    assert publico["certificado_id"] == acesso["certificado_id"]
    caminho = f'/api/v1/certificados/{acesso["certificado_id"]}/pdf'
    timestamp, nonce = str(int(time.time())), uuid4().hex
    canonical = "\n".join(["GET", caminho, timestamp, nonce,
                           str(acesso["wp_user_id"]),
                           hashlib.sha256(b"").hexdigest()])
    headers = {"X-AgroTracer-Timestamp": timestamp,
               "X-AgroTracer-Nonce": nonce,
               "X-AgroTracer-User-Id": str(acesso["wp_user_id"]),
               "X-Correlation-ID": str(uuid4()),
               "X-AgroTracer-Signature": hmac.new(
                   env["DEMO_HMAC"].encode(), canonical.encode(),
                   hashlib.sha256).hexdigest()}
    pdf = cliente.open(urllib.request.Request(
        api + caminho, headers=headers)).read()
    assert hashlib.sha256(pdf).hexdigest() == acesso["pdf_sha256"]
    relatorio = {"login_wordpress": True, "bridge_hmac_fazenda": True,
                 "certificado_publico": True, "pdf_hash": True,
                 "dados": "SYNTHETIC", "sem_ajuste_manual": True}
    salvar(STATE / "verificacao.json", json.dumps(relatorio, indent=2))
    print(json.dumps(relatorio))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("acao", choices=["up", "verify", "stop"])
    args = parser.parse_args()
    if args.acao == "up":
        preparar()
    elif args.acao == "verify":
        verificar()
    else:
        compose("stop")  # Mantem todos os volumes e credenciais.


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        if isinstance(erro, RuntimeError) and str(erro).startswith("DEMO_"):
            print(str(erro))
        # Nao expor command lines, URLs com token, senhas ou resposta bruta.
        print("DEMO_FALHOU: consulte README (diagnostico local); "
              "nao publique .demo nem dumps.")
        raise SystemExit(1) from None
