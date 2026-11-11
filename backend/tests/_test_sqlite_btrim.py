import sqlite3
c = sqlite3.connect(':memory:')
c.create_function('btrim', 1, lambda s: s.strip() if s else '')
r = c.execute("SELECT btrim(' hello ')").fetchone()
print("btrim result:", r)

# Now test: does btrim work in CHECK constraints during CREATE TABLE?
c.execute("""
CREATE TABLE test_tbl (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    CONSTRAINT ck_nome_obrigatoria CHECK (btrim(nome) <> '')
)
""")
print("CREATE TABLE with btrim CHECK OK")

