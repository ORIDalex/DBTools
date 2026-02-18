import unicodedata

entrada = "dump.sql"
salida = "dump_utf8.sql"

with open(entrada, "rb") as f:
    raw = f.read()

reemplazando bytes inválidos
# ==========================
# REEMPLAZAR BYTES CP1252 INVALIDOS
# ==========================
texto = raw.decode("cp1252", errors="replace")


# ==========================
# GUARDAR ARCHIVO COMO UTF-8 LIMPIO
# ==========================
with open(salida, "w", encoding="utf-8") as out:
    out.write(texto)

print("✅ Archivo reparado y convertido a UTF-8 → dump_utf8_fixed.sql")

entrada = "dump_utf8.sql"
schema_out = "schema_clean.sql"
data_out = "data_clean.sql"

in_copy = False
in_comment_on = False
in_alter_table = False
in_create_index = False
string_open = False

with open(entrada, "r", encoding="utf-8", errors="ignore") as f, \
    open(schema_out, "w", encoding="utf-8") as schema, \
    open(data_out, "w", encoding="utf-8") as data:

    data.write("SET client_encoding = 'UTF8';\n\n")

    for n, line in enumerate(f, 1):
        stripped = line.strip()

# ==========================
# BLOQUE COPY
# ==========================
        if stripped.startswith("COPY "):
            in_copy = True

        if in_copy:
            data.write(line)

            if stripped == r"\.":
                in_copy = False
            continue

# ==========================
# BLOQUE COMMENT ON (multilinea)
# ==========================
        if stripped.upper().startswith("COMMENT ON"):
            print(f"🧹 Eliminando COMMENT ON desde línea {n}")
            in_comment_on = True
            continue

        if in_comment_on:
            # terminar cuando encuentre ;
            if ";" in line:
                in_comment_on = False
            continue

# ==========================
# BLOQUE CREATE INDEX (multilinea)
# ==========================
        if stripped.upper().startswith("CREATE INDEX"):
            print(f"🧹 Eliminando CREATE INDEX desde línea {n}")
            in_create_index = True
            continue

        if in_create_index:
            # terminar cuando encuentre ;
            if ";" in line:
                in_create_index = False
            continue

# ==========================
# BLOQUE ALTER TABLE (multilinea)
# ==========================
        if stripped.upper().startswith("ALTER TABLE"):
            print(f"🧹 Eliminando ALTER TABLE desde línea {n}")
            in_alter_table = True
            continue

        if in_alter_table:
            # terminar cuando encuentre ;
            if ";" in line:
                in_alter_table = False
            continue

# ==========================
# ELIMINAR LÍNEAS METADATA PREVIAS
# ==========================
        if stripped.startswith("--") and "Type: COMMENT" in stripped:
            print(f"🧹 Eliminando metadata COMMENT línea {n}")
            continue

# ==========================
# ELIMINAR BASURA )';
# ==========================
        if stripped.startswith(")';"):
            print(f"🧹 Línea corrupta eliminada {n}")
            continue

# ==========================
# NORMALIZAR ASCII SOLO EN SCHEMA
# ==========================
        clean = unicodedata.normalize("NFKD", line)
        clean = clean.encode("ascii", "ignore").decode("ascii")

# ==========================
# DETECTAR STRING ABIERTO
# ==========================
        quote_count = clean.count("'")
        if quote_count % 2 == 1:
            string_open = not string_open
            print(f"⚠ Toggle string en línea {n}")

        schema.write(clean)

# ==========================
# CERRAR CADENAS ABIERTAS
# ==========================
    if string_open:
        print("⚠ String abierto detectado → cerrando automáticamente")
        schema.write("';\n")

print("✅ Dump procesado correctamente")
print("📄 Generados:")
print("   - schema_clean.sql")
print("   - data_clean.sql")
