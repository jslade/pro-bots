from pathlib import Path

import structlog

from probots.app import APP
from probots.db import DB
from probots.models.all import Program, User

LOGGER = structlog.stdlib.get_logger(__name__)


def main():
    with APP.app_context():
        load_fixtures()


def load_fixtures():
    try:
        load_users()

        DB.session.commit()
        print("Fixtures loaded successfully.")
    except Exception as e:
        DB.session.rollback()
        print(f"Error loading fixtures: {e}")
    finally:
        DB.session.close()


def load_users():
    users = [
        User(
            name="admin",
            access_code="admin",
            admin=True,
            color_head="#2d2d2d",
            color_tail="#131313",
            color_body="#black",
            programs=[
                Program(
                    name="bot-giver",
                    content=Path("fixtures/admin.probot").read_text(),
                ),
            ],
        ),
        User(
            name="bot-giver",
            access_code="admin",
            color_head="purple",
            color_tail="#131313",
            color_body="darkgrey",
            programs=[
                Program(
                    name="bot-giver",
                    content=Path("fixtures/bot-giver.probot").read_text(),
                ),
            ],
        ),
        User(
            name="bot-tagger",
            access_code="admin",
            color_head="darkred",
            color_tail="#131313",
            color_body="darkgrey",
            programs=[
                Program(
                    name="bot-tagger",
                    content=Path("fixtures/bot-tagger.probot").read_text(),
                ),
            ],
        ),
        User(
            name="bot-walker",
            access_code="admin",
            color_head="blue",
            color_tail="#131313",
            color_body="darkgrey",
            programs=[
                Program(
                    name="bot-walker",
                    content=Path("fixtures/bot-walker.probot").read_text(),
                ),
            ],
        ),
    ]

    for user in users:
        found = User.with_name(user.name)
        if found:
            LOGGER.warning("Fixture User already exists", name=user.name)
            if found.current_program.content == user.current_program.content:
                LOGGER.info("Program already matches", name=user.name)
            else:
                LOGGER.info("Updating program", name=user.name)
                found.current_program.content = user.current_program.content

            found.color_body = user.color_body
            found.color_head = user.color_head
            found.color_tail = user.color_tail
        else:
            DB.session.add(user)


if __name__ == "__main__":
    main()
