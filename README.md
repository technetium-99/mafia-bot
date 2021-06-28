# Mafia Bot

### Description

TO BE WRITTEN

### Commands
`!setups`

Lists all setups, ordered by date added to the database

Marks the setup set as default

`!default-setup` `<name>` `<version>`

Changes the default setup used in all commands that accept a setup name and version argument

* `name:` setup name
* `version` setup version (a decimal number)

`!setup` `[<name> <version>]`

Displays the roles contained in a setup, grouped by alignment and ordered by role type - Investigative, Protective, Communicative - than alphabetically

* `name:` *optional* setup name, uses name of the default setup if omitted
* `version` *optional* setup version (a decimal number), uses version of the default setup if omitted
* **NOTE:** `name` and `version` is either both omitted or both specified

`!setup-doc` `[<name> <version>]`

Fetches the documentation for a setup

* `name:` *optional* setup name, uses name of the default setup if omitted
* `version` *optional* setup version (a decimal number), uses version of the default setup if omitted
* **NOTE:** `name` and `version` is either both omitted or both specified

`!role` `<name>` `[<setup-name> <setup-version>]`

Displays information about of role, including its alignment, type, point value, description, actions, and results (for each action if said action has them)

* `name:` role name (not case sensitive)
* `setup-name:` *optional* setup name, uses name of the default setup if omitted
* `setup-version` *optional* setup version (a decimal number), uses version of the default setup if omitted
* **NOTE:** `name` and `version` is either both omitted or both specified