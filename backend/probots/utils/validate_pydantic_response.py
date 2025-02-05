from contextlib import contextmanager
import pydantic
import structlog

LOGGER = structlog.stdlib.get_logger(__name__)

@contextmanager
def validate_pydantic_response():
    try:
        yield
    except pydantic.ValidationError as e:
        errors = get_validation_errors(e)
        LOGGER.exception("Error in pydantic response model", errors=errors)
        raise ValueError(f"Invalid pydantic response model: {e}: {errors}")

def get_validation_errors(ex: pydantic.ValidationError) -> dict[str, list[str]]:
    """
    Given a pydantic ValidationError, return errors in the format we are used to.
    pydantic's errors are in a different format that will break our web clients.
    """
    errors: dict[str, list[str]] = {}
    for error in ex.errors():
        loc = ".".join(str(x) for x in error["loc"])
        assert isinstance(loc, str)
        msg = error["msg"]
        err_type = error["type"]
        if msg == "field required":
            msg = "is required"
        if err_type == "value_error":
            msg = msg.removeprefix("Value error, ")
        try:
            errors[loc].append(msg)
        except KeyError:
            errors[loc] = [msg]
    return errors
