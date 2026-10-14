# integracao_v1

Projeto Maven preparado para uso no IntelliJ IDEA.

## Requisitos
- JDK 17
- Maven 3.9+ (o IntelliJ pode usar o Maven integrado)

## Abrir no IntelliJ IDEA
1. Extraia o arquivo ZIP.
2. No IntelliJ, escolha **File > Open**.
3. Selecione a pasta `integracao_v1` (ou diretamente o `pom.xml`).
4. Aguarde a importação/sincronização do Maven.
5. Confirme o **Project SDK = Java 17** em **File > Project Structure > Project**.

## Testes
Os testes usam JUnit 5 (Jupiter).

```bash
mvn test
```

## Relatório JaCoCo
Execute:

```bash
mvn verify
```

Depois abra:

`target/site/jacoco/index.html`

No PowerShell:

```powershell
Invoke-Item .\target\site\jacoco\index.html
```
