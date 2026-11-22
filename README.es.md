# wk-skill-forge

<!-- README-I18N:START -->

[English](./README.md) | **Español**

<!-- README-I18N:END -->

Skill global de agente, solo por comando, que **crea, audita, mejora y evalúa** skills de agente LLM-first, para que cada una funcione sola en cualquier agente de línea de comandos.

Versiones y notas: [Releases](https://github.com/LCubero/wk-skill-forge/releases).

## Qué hace

| Modo | Sirve para | ¿Escribe archivos? |
|---|---|---|
| Create | Redactar una skill nueva a partir de su propósito | Solo después de que apruebes el borrador |
| Audit | Revisar problemas de seguridad y calidad de una skill | No, solo lectura |
| Improve | Auditar una skill y proponer el cambio más pequeño | Solo después de que apruebes el diff |
| Evaluate | Decidir si vale la pena adoptar una skill externa: rechazar, posponer, adoptar tal cual o recrear | Solo su carpeta de ejecución aprobada |

## Instalación

1. Copia la carpeta `wk-skill-forge/` en la carpeta global de skills de tu agente, por ejemplo `<global-skills-dir>/wk-skill-forge/`.
2. Recarga el agente.

## Uso

Invoca `wk-skill-forge` por su nombre, con el modo y la skill objetivo. Nunca se activa sola y pregunta lo que falte.

## Seguro por defecto

- Las skills revisadas no son de confianza: nunca las instala, las sigue ni las ejecuta.
- Toda escritura y toda llamada de red necesitan tu aprobación.
- Nunca escribe en una carpeta de skills instaladas; los resultados los copias tú.
- Nunca inventa autor, licencia ni versión.

## Qué contiene

| Archivo | Función |
|---|---|
| `wk-skill-forge/SKILL.md` | La skill |
| `wk-skill-forge/references/style-guide.md` | Reglas con las que se revisa cada skill |
| `wk-skill-forge/references/topic-sources.md` | Guía de investigación para Create profesional |
| `wk-skill-forge/references/intake.md` | Proceso de Evaluate |

Revisa el contrato: `python -B -m unittest tests.test_skill_forge_skill_contract`. Son pruebas estáticas, no una ejecución real del agente.

## Sobre este repositorio

- Un repositorio, una skill. El nombre de la carpeta y el `name` de la frontmatter son ambos `wk-skill-forge`.
- Desarrolla la skill; no la instala ni la distribuye.
- La skill se recreó etapa por etapa a partir del original `wk-skill-forge-ld9`, guardado en un clon local de solo lectura (`<original-repo>`). Las 12 etapas están terminadas; la historia está en el [roadmap](docs/repo-harness/roadmap.md) y el [CHANGELOG](CHANGELOG.md), ambos en inglés.
- Convención de nombres para las skills del dueño: `wk-<name>`, en minúsculas con guiones, sin el sufijo `-ld9`. La autoría se ve en el prefijo `wk` y en el `author` de la frontmatter.
- Contribuir: [CONTRIBUTING.md](CONTRIBUTING.md). Licencia: [MIT](LICENSE).
