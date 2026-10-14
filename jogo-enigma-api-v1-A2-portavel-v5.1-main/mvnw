#!/bin/sh
set -eu

# Maven Wrapper portavel para macOS/Linux.
# Nao depende de Maven instalado globalmente; requer apenas JDK 17+.
MAVEN_VERSION=3.9.11
MAVEN_DIST="apache-maven-${MAVEN_VERSION}"
MAVEN_HOME_LOCAL="${HOME}/.m2/wrapper/dists/${MAVEN_DIST}"
MAVEN_CMD="${MAVEN_HOME_LOCAL}/bin/mvn"
MAVEN_URL="https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/${MAVEN_VERSION}/${MAVEN_DIST}-bin.zip"

if ! command -v java >/dev/null 2>&1; then
  echo "[ERRO] Java nao encontrado no PATH. Instale/configure JDK 17 ou superior." >&2
  exit 1
fi

if [ ! -x "$MAVEN_CMD" ]; then
  echo "[INFO] Maven ${MAVEN_VERSION} nao encontrado no cache do Wrapper."
  echo "[INFO] Baixando Maven ${MAVEN_VERSION} do Maven Central..."
  TMP_DIR="$(mktemp -d)"
  trap 'rm -rf "$TMP_DIR"' EXIT INT TERM
  ZIP="$TMP_DIR/${MAVEN_DIST}-bin.zip"

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$MAVEN_URL" -o "$ZIP"
  elif command -v wget >/dev/null 2>&1; then
    wget -q "$MAVEN_URL" -O "$ZIP"
  else
    cat > "$TMP_DIR/Download.java" <<'JAVA'
import java.net.URI;
import java.nio.file.*;
public class Download {
  public static void main(String[] a) throws Exception {
    try (var in = URI.create(a[0]).toURL().openStream()) {
      Files.copy(in, Path.of(a[1]), StandardCopyOption.REPLACE_EXISTING);
    }
  }
}
JAVA
    java "$TMP_DIR/Download.java" "$MAVEN_URL" "$ZIP"
  fi

  command -v unzip >/dev/null 2>&1 || { echo "[ERRO] comando unzip nao encontrado." >&2; exit 1; }
  mkdir -p "$(dirname "$MAVEN_HOME_LOCAL")"
  unzip -q "$ZIP" -d "$TMP_DIR"
  rm -rf "$MAVEN_HOME_LOCAL"
  mv "$TMP_DIR/$MAVEN_DIST" "$MAVEN_HOME_LOCAL"
  echo "[OK] Maven ${MAVEN_VERSION} preparado pelo Wrapper."
else
  echo "[OK] Maven ${MAVEN_VERSION} encontrado no cache do Wrapper."
fi

exec "$MAVEN_CMD" "$@"
