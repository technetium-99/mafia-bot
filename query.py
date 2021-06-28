import sqlalchemy as sql
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
DB_PASSWORD = os.getenv("DB_PASSWORD")
ENGINE = sql.create_engine("postgresql://postgres:{password}@localhost/postgres".format(password=DB_PASSWORD))
METADATA = sql.MetaData()

SETUP = sql.Table("setup", METADATA, autoload_with=ENGINE)
ROLE = sql.Table("role", METADATA, autoload_with=ENGINE)
SR_MAP = sql.Table("setup_role_map", METADATA, autoload_with=ENGINE)
ALIGNMENT = sql.Table("alignment", METADATA, autoload_with=ENGINE)
ACTION = sql.Table("action", METADATA, autoload_with=ENGINE)
RESULT = sql.Table("role_based_result", METADATA, autoload_with=ENGINE)
ROLE_TYPE = sql.Table("role_type", METADATA, autoload_with=ENGINE)
ACTION_TYPE = sql.Table("action_type", METADATA, autoload_with=ENGINE)


def query_setups():
    # Queries DB for all setups
    setups_query = sql.select(SETUP.c.name, SETUP.c.version).order_by(SETUP.c.date_added.desc(), SETUP.c.name)

    with ENGINE.begin() as connection:
        setups = connection.execute(setups_query).all()

    # Retrieves name and version of default setup for reference
    with open("default_setup.txt") as file:
        name = file.readline().strip()
        version = float(file.readline().strip())

    msg = "========= SETUPS ========="
    msg += "\n"

    for setup in setups:
        # Ignores test setup
        if setup.name == "Test":
            continue

        msg += "\n" + setup.name + " v" + str(setup.version)

        # Marks the setup currently set as default
        if setup.name == name and setup.version == version:
            msg += " (DEFAULT)"

    return create_multiline_block(msg)


def query_setup(name, version):
    # Sets the setup name and version from a file if default values were passed
    if name == "default":
        with open("default_setup.txt") as file:
            name = file.readline().strip()
            version = float(file.readline().strip())

    # Returns error message if a default value for the version was passed, but one for the name wasn't
    elif name != "default" and version == -1.0:
        return create_multiline_block("[ERROR] Version omitted")

    # Queries setup info for the setup with the given name and version
    setup_query = sql.select(SETUP.c.id, SETUP.c.name).where((SETUP.c.name == name) & (SETUP.c.version == version))

    with ENGINE.begin() as connection:
        setup = connection.execute(setup_query).first()

    if setup is None:
        return create_multiline_block("[ERROR] Could not find setup " + name + " v" + str(version))

    # Queries tha name and alignment of every role in the setup
    roles_query = sql.select(ROLE.c.name, ALIGNMENT.c.name.label("alignment"))\
        .join(ROLE, SR_MAP.c.role_id == ROLE.c.id)\
        .join(ALIGNMENT, ROLE.c.alignment_id == ALIGNMENT.c.id)\
        .join(ROLE_TYPE, ROLE.c.type == ROLE_TYPE.c.name, isouter=True)\
        .where(SR_MAP.c.setup_id == setup.id)\
        .order_by(ROLE_TYPE.c.priority)\
        .order_by(ROLE.c.name)
    roles = dict()

    with ENGINE.begin() as connection:
        # Maps each role in the setup to its alignment
        for role in connection.execute(roles_query):
            if role.alignment not in roles:
                roles[role.alignment] = list()

            roles[role.alignment].append(role.name)

    msg = "========= {name} {version} =========".format(name=name.upper(), version="V" + str(version))

    for alignment in roles:
        msg += "\n\n" + alignment.upper() + ":"
        msg += "\n"

        for i in range(len(roles[alignment])):
            if i == len(roles[alignment]) - 1:
                msg += roles[alignment][i]
            else:
                msg += roles[alignment][i] + ", "

    return create_multiline_block(msg)


def query_setup_doc(name, version):
    # Sets the setup name and version from a file if default values were passed
    if name == "default":
        with open("default_setup.txt") as file:
            name = file.readline().strip()
            version = float(file.readline().strip())

    # Returns error message if a default value for the version was passed, but one for the name wasn't
    elif name != "default" and version == -1.0:
        return create_multiline_block("[ERROR] Version omitted"), None

    # Queries filename of documentation for the setup with the given name and version
    doc_query = sql.select(SETUP.c.documentation).where((SETUP.c.name == name) & (SETUP.c.version == version))

    with ENGINE.begin() as connection:
        doc = connection.execute(doc_query).first()

    if doc is None:
        return create_multiline_block("[ERROR] Could not find setup " + name + " v" + str(version)), None

    # Checks if file exists at filename path
    if not Path(doc.documentation).is_file():
        return create_multiline_block("[ERROR] Could not find documentation for " + name + " v" + str(version)), None

    msg = "========= {name} {version} =========".format(name=name.upper(), version="V" + str(version))

    return create_multiline_block(msg), doc.documentation


def set_default_setup(name, version):
    # Checks if the setup being set as default exists in the DB
    setup_query = sql.select(SETUP.c.id).where((SETUP.c.name == name) & (SETUP.c.version == version))

    with ENGINE.begin() as connection:
        setup = connection.execute(setup_query).first()

    if setup is None:
        return create_multiline_block("[ERROR] Could not find setup " + name + " v" + str(version))

    # Read current default setup on file
    with open("default_setup.txt") as file:
        old_name = file.readline().strip()
        old_version = float(file.readline().strip())

    # Returns an error if the new setup is already the default
    if name == old_name and version == old_version:
        return create_multiline_block("[ERROR] Default setup is already " + name + " v" + str(version))

    # Writes new default setup to file
    with open("default_setup.txt", "w") as file:
        file.write(name + "\n")
        file.write(str(version) + "\n")

    return create_multiline_block("Default setup changed from {old_name} v{old_version} -> {name} v{version}".format(
        old_name=old_name,
        old_version=str(old_version),
        name=name,
        version=str(version)
    ))


def query_role(name, setup_name, setup_version):
    # Sets the setup name and version from a file if default values were passed
    if setup_name == "default":
        with open("default_setup.txt") as file:
            setup_name = file.readline().strip()
            setup_version = float(file.readline().strip())

    # Returns error message if a default value for the version was passed, but one for the name wasn't
    elif setup_name != "default" and setup_version == -1.0:
        return create_multiline_block("[ERROR] Version omitted")

    setup_query = sql.select(SETUP.c.id).where((SETUP.c.name == setup_name) & (SETUP.c.version == setup_version))

    with ENGINE.begin() as connection:
        setup = connection.execute(setup_query).first()

    if setup is None:
        return create_multiline_block("[ERROR] Could not find setup " + setup_name + " v" + str(setup_version))

    # Queries DB for role data corresponding to name
    role_query = sql.select(ROLE.c.id, ROLE.c.name, ALIGNMENT.c.name.label("alignment"), ROLE.c.variant_of, ROLE.c.type, ROLE.c.value, ROLE.c.description)\
        .join(SR_MAP, SR_MAP.c.role_id == ROLE.c.id)\
        .join(ALIGNMENT, ROLE.c.alignment_id == ALIGNMENT.c.id)\
        .where((SR_MAP.c.setup_id == setup.id) & (ROLE.c.name == name))

    with ENGINE.begin() as connection:
        # Any role within a setup should have a unique name
        role = connection.execute(role_query).first()

    # Returns error message if no role with name is found
    if role is None:
        return create_multiline_block("[ERROR] Could not find role {name} in {setup_name} v{setup_version}".format(
            name=name,
            setup_name=setup_name,
            setup_version=str(setup_version)
        ))

    # If this role is a variant, query DB for the base role
    if role.variant_of is not None:
        base_role_query = sql.select(ROLE.c.name, ROLE.c.type, ROLE.c.value, ROLE.c.description)\
            .where(ROLE.c.id == role.variant_of)

        with ENGINE.begin() as connection:
            base_role = connection.execute(base_role_query).first()
    else:
        base_role = None

    # Queries DB for action data corresponding to role
    action_query = sql.select(ACTION.c.id, ACTION.c.type, ACTION.c.shots, ACTION.c.description)\
        .join(ACTION_TYPE, ACTION.c.type == ACTION_TYPE.c.name, isouter=True)\
        .where(ACTION.c.role_id == role.id)\
        .order_by(ACTION_TYPE.c.priority)

    with ENGINE.begin() as connection:
        actions = connection.execute(action_query).all()

    # Message header
    if role.alignment is None and role.type is None:
        msg = "========= {name} =========".format(name=role.name.upper())
    elif role.alignment is not None and role.type is None:
        msg = "========= {name} [{alignment}] =========".format(name=role.name.upper(), alignment=role.alignment)
    else:
        msg = "========= {name} [{alignment} {type}] =========".format(name=role.name.upper(), alignment=role.alignment, type=role.type)

    # Message body
    # If no value or description exists and this role is a variant, try to use the value or description of the base role
    msg += "\n\n" + base_role.name.upper() + " Variant" if base_role is not None else ""
    msg += "\n\nVALUE: " + str(role.value) if role.value is not None else ("\n\nVALUE: " + str(base_role.value) if base_role is not None else "")
    msg += "\nINFO: " + role.description if role.description is not None else ("\nINFO: " + base_role.description if base_role is not None else "")
    msg += "\n\n=== ACTIONS ==="

    for action in actions:
        msg += "\n"

        if action.type is not None and action.shots is not None:
            msg += "\n[{type}] SHOTS: {shots}".format(type=action.type.upper(), shots=action.shots)
        elif action.type is not None:
            msg += "\n[{type}]".format(type=action.type.upper())

        msg += "\n" + action.description

        # Queries the results for each action
        results_query = sql.select(ROLE.c.name.label("target"), RESULT.c.result)\
            .join(ROLE, RESULT.c.role_id == ROLE.c.id)\
            .where(RESULT.c.action_id == action.id)\
            .order_by(ROLE.c.alignment_id)
        results = dict()

        with ENGINE.begin() as connection:
            # Maps each role to a result
            for result in connection.execute(results_query).all():
                if result.result not in results:
                    results[result.result] = list()

                results[result.result].append(result.target)

        if len(results) > 0:
            msg += "\n\n=== RESULTS ==="
            msg += "\n"

            for result in sorted(results.keys()):
                msg += "\n" + result + " <- "

                for i in range(len(results[result])):
                    if i == len(results[result]) - 1:
                        msg += results[result][i]
                    else:
                        msg += results[result][i] + ", "

    return create_multiline_block(msg)


def query_clarification():
    return create_multiline_block("Command still in dev")


# Surrounds the given text with the markdown necessary to turn it into a multiline code block
def create_multiline_block(text):
    return "```\n" + text + "\n```"
