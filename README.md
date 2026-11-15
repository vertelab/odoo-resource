# odoo-resource — gren 19.0

> **Denna gren är avsiktligt tom.** Modulerna är INTE portade till Odoo 19.
> Grenen finns så att dev-miljöer (`hansolo19`) kan klona den utan att falla,
> men den påstår ingenting om att koden är portad.

## Baseline

| | |
|---|---|
| Källa | `20.0` |
| Moduler | **2** |
| Grenar i repot | `18.0`, `18.0-object-code`, `20.0` |

## Moduler

- `resource_planning`
- `resource_planning_account_period`

## Blockerare

**3 externa beroenden saknas** i Odoo 19-kärnan och OCA 19.0:

| Beroende | Behövs av |
|---|---|
| `account_accountant_ce` | `resource_planning_account_period` |
| `hr_contract` | `resource_planning` |
| `web_timeline` | `resource_planning` |

### Prioritering

Ett beroende som blockerar många moduler ger mest nytta att lösa först:

- `account_accountant_ce` — frisläpper **1** modul(er)
- `hr_contract` — frisläpper **1** modul(er)
- `web_timeline` — frisläpper **1** modul(er)

## Nästa steg

Portering sker på `*-pfile`-maskin med versionsagnostisk kod
(`.p.py` / `.p.xml`). Se `/skill:odoo-pfiles`.
