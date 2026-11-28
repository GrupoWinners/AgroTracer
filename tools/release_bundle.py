"""Empacota um commit candidato; nunca cria tag nem declara aceite humano."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bundle(root, commit, output):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("RELEASE_COMMIT_INVALIDO")
    resolved = git(root, "rev-parse", commit + "^{commit}").decode().strip()
    if resolved != commit:
        raise ValueError("RELEASE_COMMIT_INVALIDO")
    source = git(root, "archive", "--format=zip", commit)
    files = {}
    with zipfile.ZipFile(io.BytesIO(source)) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            path = PurePosixPath(info.filename)
            if (path.is_absolute() or ".." in path.parts
                    or any(p in (".git", ".demo", ".venv", "node_modules")
                           for p in path.parts)
                    or (path.name.startswith(".env")
                        and path.name != ".env.example")):
                raise ValueError("RELEASE_ARQUIVO_PRIVADO")
            data = archive.read(info)
            if re.search(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
                         rb"|\bgh[pousr]_[A-Za-z0-9]{30,}\b"
                         rb"|\bAKIA[A-Z0-9]{16}\b", data):
                raise ValueError("RELEASE_SEGREDO_DETECTADO")
            files[info.filename] = data
        required = ["backend/Dockerfile", "ops/demo/compose.yaml",
                    "docs/evidencias/sprint-7/aceite-interno.json"]
        if any(name not in files for name in required):
            raise ValueError("RELEASE_EVIDENCIA_AUSENTE")
        evidence_buffer = io.BytesIO()
        with zipfile.ZipFile(evidence_buffer, "w") as evidence:
            for info in archive.infolist():
                if not info.is_dir() and info.filename.startswith("docs/"):
                    evidence.writestr(info, files[info.filename])
    docker = files["backend/Dockerfile"].decode()
    compose = files["ops/demo/compose.yaml"].decode()
    artifacts = {
        "agrotracer-candidato.zip": source,
        "agrotracer-documentacao.zip": evidence_buffer.getvalue(),
    }
    manifest = {
        "versao_alvo": "v1.0.0", "tipo": "CANDIDATO_NAO_PUBLICADO",
        "commit": commit,
        "tree": git(root, "rev-parse", commit + "^{tree}").decode().strip(),
        "imagens_declaradas": re.findall(r"^FROM\s+(\S+)", docker, re.M)
        + re.findall(r"^\s*image:\s*(\S+)", compose, re.M),
        "limite_versoes": "Tags declaradas, nao digests de imagens em runtime",
        "tag_criada": False, "aceite_interno": "PENDENTE_VALIDACAO_HUMANA",
        "board": ("https://losel.atlassian.net/jira/software/"
                  "projects/AG/boards/2"),
        "arquivos": {name: digest(data)
                     for name, data in sorted(files.items())},
        "artefatos": {name: digest(data) for name, data in artifacts.items()},
    }
    artifacts["manifesto.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    artifacts["SHA256SUMS.txt"] = "".join(
        f"{digest(data)}  {name}\n" for name, data in artifacts.items()
    ).encode()
    # Diretorio novo: nunca sobrescrever evidencia ou pacote existente.
    output.mkdir(parents=True, exist_ok=False)
    for name, data in artifacts.items():
        (output / name).write_bytes(data)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True,
                        help="SHA completo revisado")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = bundle(Path(__file__).resolve().parents[1],
                          args.commit, args.output)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        code = (str(error) if isinstance(error, ValueError)
                else "RELEASE_FALHOU")
        parser.exit(1, code + "\n")
    print(json.dumps({"commit": manifest["commit"],
                      "tipo": manifest["tipo"],
                      "artefatos": manifest["artefatos"]}))


if __name__ == "__main__":
    main()
