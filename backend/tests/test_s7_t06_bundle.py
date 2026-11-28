"""Contrato real do pacote Git: snapshot, hashes e recusas."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import zipfile

import pytest


spec = importlib.util.spec_from_file_location(
    "release_bundle", Path(__file__).parents[2] / "tools/release_bundle.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for name, content in {
        "backend/Dockerfile": "FROM python:3.14.7-slim\n",
        "ops/demo/compose.yaml": (
            "services:\n  wp:\n    image: wordpress:6.8.3\n"),
        "docs/evidencias/sprint-7/aceite-interno.json": (
            '{"status":"PENDENTE"}'),
    }.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def commit(root):
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.name=Teste", "-c",
                    "user.email=test@example.invalid",
                    "commit", "-qm", "test"],
                   cwd=root, check=True)
    return module.git(root, "rev-parse", "HEAD").decode().strip()


def test_snapshot_hashes_e_repetibilidade(repo, tmp_path):
    sha = commit(repo)
    (repo / "nao-versionado.txt").write_text("privado")
    (repo / "backend/Dockerfile").write_text("alteracao local")
    out = tmp_path / "pacote"
    result = module.bundle(repo, sha, out)
    assert result["commit"] == sha
    assert result["tag_criada"] is False
    assert "python:3.14.7-slim" in result["imagens_declaradas"]
    with zipfile.ZipFile(out / "agrotracer-candidato.zip") as archive:
        assert "nao-versionado.txt" not in archive.namelist()
        for name, digest in result["arquivos"].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
    for line in (out / "SHA256SUMS.txt").read_text().splitlines():
        digest, name = line.split("  ")
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == digest
    second = tmp_path / "segundo"
    module.bundle(repo, sha, second)
    for path in out.iterdir():
        assert path.read_bytes() == (second / path.name).read_bytes()
    assert json.loads((out / "manifesto.json").read_text())["commit"] == sha
    with pytest.raises(FileExistsError):
        module.bundle(repo, sha, out)


@pytest.mark.parametrize("name,content,code", [
    (".env", "local", "ARQUIVO_PRIVADO"),
    (".demo/acesso.json", "{}", "ARQUIVO_PRIVADO"),
    ("key.txt", "ghp_" + "x" * 40, "SEGREDO_DETECTADO"),
])
def test_recusa_privados_sem_gerar_pacote(repo, tmp_path, name, content, code):
    path = repo / name
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_text(content)
    sha = commit(repo)
    out = tmp_path / "saida"
    with pytest.raises(ValueError, match=code):
        module.bundle(repo, sha, out)
    assert not out.exists()


def test_exige_commit_completo_e_evidencia(repo, tmp_path):
    with pytest.raises(ValueError, match="COMMIT_INVALIDO"):
        module.bundle(repo, "HEAD", tmp_path / "saida")
    (repo / "docs/evidencias/sprint-7/aceite-interno.json").unlink()
    sha = commit(repo)
    with pytest.raises(ValueError, match="EVIDENCIA_AUSENTE"):
        module.bundle(repo, sha, tmp_path / "saida")
