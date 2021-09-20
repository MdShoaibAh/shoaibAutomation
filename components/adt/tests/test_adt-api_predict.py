from components.adt.src.utils.helpers import assert_valid_schema
from components.adt.src.utils.variables import question_schema
from components.adt.src.request_handler import RequestHandler
from alef_ml_utilities import get_config
import requests
from assertpy import assert_that
import random
import pytest
import uuid

source = RequestHandler()
config = get_config('../../adt/src/config.yml')


@pytest.mark.parametrize("response_value", [1, 0])
def test_initialization_validations(response_value):
    """ Getting and validation response by changing default response parameter null to 0 or 1
    parameter= "response":1/0/null
    """
    sess_id = str(uuid.uuid1())
    response = source.get_question_response(response_value=response_value, session_id=sess_id)
    assert_that(response.json()["error"]).is_equal_to("Session was not initialized.")


def test_invalid_response_value():
    """
    This test is basically check if user input invalid response value like any other number except 0,1 and null
    then it should raise an error
    """

    sess_id = str(uuid.uuid1())
    response_invalid_value = random.randint(2, 1000)
    response = source.get_question_response(response_invalid_value, session_id=sess_id)
    assert_that(response.json()["error"]).is_equal_to("Response should be null, 0 or 1.")


def test_reinitializing_validations():
    """ Getting and validation response by providing response as None 2nd time to get validation error,
     that session already initialized
    """
    sess_id = str(uuid.uuid1())
    response = source.get_question_response(response_value=None, session_id=sess_id)
    assert_that(response.json()["error"]).is_none()
    response = source.get_question_response(response_value=None, session_id=sess_id)
    assert_that(response.json()["error"]).is_equal_to("Session already initialized.")


def test_if_response_is_valid():
    """ Checking valid status code and verifying the response is not empty by check some required fields
    e.g id and code
    """
    sess_id = str(uuid.uuid1())
    response = source.get_question_response(response_value=None, session_id=sess_id)
    assert_that(response.status_code).is_equal_to(requests.codes.ok)
    assert_that(response.json()["next_item"]["id"]).is_not_empty()
    assert_that(response.json()["next_item"]["code"]).is_not_empty()


def test_if_response_schema_is_correct():
    """ Validation the response schema if it is correct and response types is correct e.g string, integer
     """
    sess_id = str(uuid.uuid1())
    response = source.get_question_response(response_value=None, session_id=sess_id)
    assert_valid_schema(response.json(), question_schema)


def test_finish_functionality_and_validations():
    """ Attempting the test with random options number e.g 1,0.
    Scenario 1. Check if student should not be able to continue the test beyond
    threshold which is by default set as 30 times, error should comes
    Scenario 2. Check every next question is unique and should not equal to previous one
    """
    sess_id = str(uuid.uuid1())
    response = source.get_question_response(response_value=None, session_id=sess_id)
    code_prev = response.json()["next_item"]["code"]
    for attempt in range(30):
        response = source.get_question_response(response_value=random.randint(0, 1), session_id=sess_id)
        if attempt < 29:
            code_next = response.json()["next_item"]["code"]
            assert_that(code_next).is_not_equal_to(code_prev)
            code_prev = code_next
        else:
            break
    assert_that(response.json()["error"]).is_equal_to("Test reached stopping criteria")
