"""Ensaio destrutivo somente em containers novos, com nomes aleatorios."""

import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.main import app
from app.models import Base
from test_s2_t01_api import ambiente_api  # noqa: F401
from test_s4_t02_fechamento import fechamento_api  # noqa: F401
from test_s5_t01_certificacao import emitir
from test_s3_t03_api import assinar


class Laboratorio:
    def __init__(self):
        self.prefixo = "agrotracer-s6-" + uuid4().hex
        self.containers = []
        self.volumes = []
        self.env = dict(os.environ)
        self.senha = secrets.token_hex(24)
        self.env.update({
            "POSTGRES_PASSWORD": self.senha,
            "MARIADB_ROOT_PASSWORD": self.senha,
            "MARIADB_PASSWORD": self.senha,
            "WORDPRESS_DB_PASSWORD": self.senha,
        })
        self.run("network", "create", self.prefixo)

    def run(self, *args, entrada=None):
        resultado = subprocess.run(
            ["docker", *args], input=entrada, capture_output=True,
            env=self.env, timeout=240,
        )
        if resultado.returncode:
            # Nao imprimir argv, dumps, senhas, token ou saida do processo.
            raise RuntimeError(f"Docker {args[0]} falhou; saida suprimida")
        return resultado.stdout

    def iniciar(self, nome, imagem, opcoes):
        nome = self.prefixo + "-" + nome
        self.containers.append(nome)
        self.run("run", "-d", "--name", nome,
                 "--network", self.prefixo, *opcoes, imagem)
        return nome

    def porta(self, nome, porta):
        saida = self.run("port", nome, str(porta)).decode().splitlines()[0]
        return int(saida.rsplit(":", 1)[1])

    def volume(self, nome):
        nome = self.prefixo + "-" + nome
        self.volumes.append(nome)
        self.run("volume", "create", nome)
        return nome

    def cli(self, wp, mysql, *args, entrada=None):
        return self.run(
            "run", "--rm", "-i", "--network", self.prefixo,
            "--volumes-from", wp, "--user", "33:33",
            "-e", f"WORDPRESS_DB_HOST={mysql}",
            "-e", "WORDPRESS_DB_USER=wordpress",
            "-e", "WORDPRESS_DB_NAME=wordpress",
            "-e", "WORDPRESS_DB_PASSWORD",
            "wordpress:cli-php8.3", *args, entrada=entrada,
        )

    def limpar(self):
        for tipo, nomes in (("container", self.containers),
                            ("volume", self.volumes)):
            for nome in reversed(nomes):
                assert nome.startswith(self.prefixo + "-")
                try:
                    self.run(tipo, "rm", "-f", nome)
                except RuntimeError:
                    pass
        self.run("network", "rm", self.prefixo)


def aguardar(funcao):
    limite = time.monotonic() + 120
    while time.monotonic() < limite:
        try:
            return funcao()
        except (RuntimeError, httpx.HTTPError, AssertionError):
            time.sleep(2)
    raise RuntimeError("Servico sintetico nao ficou pronto em 120 s")


def login(url, senha):
    with httpx.Client(follow_redirects=True, timeout=15) as cliente:
        cliente.get(url + "/wp-login.php").raise_for_status()
        resposta = cliente.post(url + "/wp-login.php", data={
            "log": "s6-sintetico", "pwd": senha,
            "wp-submit": "Log In", "testcookie": "1",
            "redirect_to": url + "/wp-admin/",
        })
        assert resposta.status_code == 200
        assert "/wp-admin/" in str(resposta.url)
        assert any(c.name.startswith("wordpress_logged_in_")
                   for c in cliente.cookies.jar)


@pytest.mark.skipif(os.getenv("AGROTRACER_RESTORE_DRILL") != "1",
                    reason="Ensaio opt-in requer Docker Linux")
def test_restore_postgresql_wordpress_pdf(request, monkeypatch):
    cenario = request.getfixturevalue("fechamento_api")
    lab = Laboratorio()
    engines = []
    relatorio = {"escopo": "Dados SYNTHETIC; ambientes Docker descartaveis"}
    try:
        ambientes = {}
        for lado in ("origem", "destino"):
            pg = lab.iniciar(lado + "-pg", "postgres:16", [
                "-e", "POSTGRES_PASSWORD", "-e", "POSTGRES_USER=drill",
                "-e", "POSTGRES_DB=drill", "-p", "127.0.0.1::5432",
            ])
            aguardar(lambda: lab.run(
                "exec", pg, "pg_isready", "-U", "drill", "-d", "drill",
            ))
            db = lab.iniciar(lado + "-mysql", "mariadb:11.4", [
                "-e", "MARIADB_ROOT_PASSWORD", "-e", "MARIADB_PASSWORD",
                "-e", "MARIADB_DATABASE=wordpress",
                "-e", "MARIADB_USER=wordpress",
            ])
            aguardar(lambda: lab.run(
                "exec", db, "healthcheck.sh", "--connect",
                "--innodb_initialized",
            ))
            volume = lab.volume(lado + "-wp")
            wp = lab.iniciar(lado + "-wp", "wordpress:6.8.3-php8.3-apache", [
                "-e", f"WORDPRESS_DB_HOST={db}",
                "-e", "WORDPRESS_DB_USER=wordpress",
                "-e", "WORDPRESS_DB_NAME=wordpress",
                "-e", "WORDPRESS_DB_PASSWORD",
                "-v", volume + ":/var/www/html", "-p", "127.0.0.1::80",
            ])
            url_wp = f"http://127.0.0.1:{lab.porta(wp, 80)}"
            aguardar(lambda: lab.run(
                "exec", wp, "test", "-f", "/var/www/html/wp-config.php",
            ))
            url_pg = (f"postgresql+psycopg://drill:{lab.senha}"
                      f"@127.0.0.1:{lab.porta(pg, 5432)}/drill")
            engine = create_engine(url_pg, hide_parameters=True)
            engines.append(engine)
            ambientes[lado] = (pg, db, wp, url_wp, url_pg, engine)

        pg, mysql, wp, url_wp, url_pg, origem = ambientes["origem"]
        # Schema real, com triggers e constraints, criado pelas migrations.
        migracao = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            env={**os.environ, "DATABASE_URL": url_pg},
            capture_output=True, timeout=60,
        )
        assert migracao.returncode == 0, "Migration do laboratorio falhou"
        with cenario[1]() as sqlite, origem.begin() as destino:
            for tabela in Base.metadata.sorted_tables:
                linhas = [dict(r) for r in sqlite.execute(
                    select(tabela)).mappings()]
                if tabela.name == "parametro_sets":
                    for linha in linhas:
                        linha["status"] = "RASCUNHO"
                if linhas:
                    destino.execute(tabela.insert(), linhas)
            destino.execute(text(
                "UPDATE parametro_sets SET status='ATIVO'"
            ))

        def apontar(engine):
            fabrica = sessionmaker(bind=engine)

            def obter_teste():
                with fabrica() as db:
                    yield db

            app.dependency_overrides[obter_db] = obter_teste

        apontar(origem)
        emitido = emitir(cenario)
        assert emitido.status_code == 201
        certificado = emitido.json()
        caminho = f'/api/v1/certificados/{certificado["id"]}/pdf'
        pdf = cenario[0].get(caminho)
        assert pdf.status_code == 200
        digest = hashlib.sha256(pdf.content).hexdigest()

        lab.cli(wp, mysql, "core", "install", "--url=" + url_wp,
                "--title=AgroTracer SYNTHETIC", "--admin_user=s6-sintetico",
                "--admin_password=" + lab.senha,
                "--admin_email=s6@example.invalid", "--skip-email")
        plugin = Path("../wordpress/agrotracer-bridge").resolve()
        lab.run("cp", str(plugin), wp + ":/var/www/html/wp-content/plugins/")
        lab.cli(wp, mysql, "plugin", "activate", "agrotracer-bridge")
        lab.run("exec", wp, "sh", "-c",
                "mkdir -p /var/www/html/wp-content/uploads; "
                "printf SYNTHETIC > "
                "/var/www/html/wp-content/uploads/s6.txt")
        login(url_wp, lab.senha)

        # Sem escritores concorrentes: banco e arquivos consistentes.
        dump_pg = lab.run("exec", pg, "pg_dump", "-U", "drill",
                          "-d", "drill", "-Fc", "--no-owner")
        dump_wp = lab.cli(wp, mysql, "db", "export", "-", "--quiet")
        arquivos = lab.run("exec", wp, "tar", "czf", "-", "-C",
                           "/var/www/html", "wp-content")
        relatorio["backups_bytes"] = {
            "postgresql_inclui_pdfs": len(dump_pg),
            "wordpress_sql": len(dump_wp), "wp_content": len(arquivos),
        }
        # Provar independencia: a origem nao participa da validacao.
        lab.run("stop", pg, mysql, wp)
        pg2, mysql2, wp2, url_wp2, _, destino = ambientes["destino"]
        inicio = time.perf_counter()
        lab.run("exec", "-i", pg2, "pg_restore", "-U", "drill",
                "-d", "drill", "--no-owner", "--exit-on-error",
                entrada=dump_pg)
        lab.cli(wp2, mysql2, "db", "import", "-", entrada=dump_wp)
        lab.run("exec", "-i", wp2, "tar", "xzf", "-", "-C",
                "/var/www/html", entrada=arquivos)
        for opcao in ("home", "siteurl"):
            lab.cli(wp2, mysql2, "option", "update", opcao, url_wp2)
        login(url_wp2, lab.senha)
        assert lab.run("exec", wp2, "cat",
                       "/var/www/html/wp-content/uploads/s6.txt"
                       ) == b"SYNTHETIC"
        lab.cli(wp2, mysql2, "plugin", "is-active", "agrotracer-bridge")
        apontar(destino)
        # Validacao autenticada real HMAC + Redis no destino restaurado.
        app.dependency_overrides.pop(exigir_usuario_wordpress)
        monkeypatch.setenv("AGROTRACER_BRIDGE_SECRET",
                           "segredo_ficticio_exclusivamente_para_testes")
        monkeypatch.setenv("AGROTRACER_REDIS_URL",
                           os.environ["AGROTRACER_TEST_REDIS_URL"])
        with TestClient(app) as cliente:
            resposta = cliente.get(caminho, headers=assinar(
                "GET", caminho, b"",
            ))
            assert resposta.status_code == 200
            assert hashlib.sha256(resposta.content).hexdigest() == digest
            publico = cliente.get("/api/v1/certificados/publico", params={
                "token": certificado["token"],
            })
            assert publico.status_code == 200
            assert publico.json()["pdf_sha256"] == digest
            assert publico.json()["certificado_id"] == certificado["id"]
        with destino.connect() as conn:
            assert conn.scalar(text(
                "SELECT version_num FROM alembic_version"
            ))
        relatorio.update({
            "rto_academico_segundos": round(time.perf_counter() - inicio, 3),
            "rto_inicio": "pg_restore em destino vazio pre-provisionado",
            "rto_fim": "login WP, arquivo/plugin, PDF HMAC e publico OK",
            "origem_desligada": True, "login_wp_restaurado": True,
            "wp_content_restaurado": True, "bridge_ativo": True,
            "pdf_sha256_igual": True, "consulta_publica_ok": True,
            "hmac_redis_real": True,
            "imagens": ["postgres:16", "mariadb:11.4",
                        "wordpress:6.8.3-php8.3-apache",
                        "wordpress:cli-php8.3"],
            "limites": "Exclui provisionamento/download, DNS, TLS e producao",
        })
        Path("restore-ci.json").write_text(
            json.dumps(relatorio, indent=2), encoding="utf-8",
        )
        print(json.dumps(relatorio))
    finally:
        for engine in engines:
            engine.dispose()
        lab.limpar()
