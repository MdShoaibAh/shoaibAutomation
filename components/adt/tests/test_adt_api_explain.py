import sys
import os
from components.adt.src.request_handler import RequestHandler
from components.adt.src.utils.helpers import assert_valid_schema
from components.adt.src.utils.variables import map_schema, no_map_schema
import requests
from alef_ml_utilities import get_config
from assertpy import assert_that

config = get_config('../../adt/src/config.yml')
source = RequestHandler()


def test_student_report_with_no_mapping_info():
    """ fetch and verify report for specific student, with no mapping infos if it is showing correctly
     and there should not be a mapping info
     """
    specific_student_report = source.get_student_report_response("AllReports_no_MappingInfo", None)
    assert_that(specific_student_report.status_code).is_equal_to(requests.codes.ok)
    session_id = specific_student_report.json()["instances"][0]["reports"][0]["session_id"]
    assert_that(specific_student_report.json()["instances"][0]["mapping"]).is_empty()
    assert_that(specific_student_report.json()["instances"][0]["reports"][0]["final_score"]).is_between(80, 230)
    assert_that(specific_student_report.json()["instances"][0]["reports"][0]["final_cefr"]).is_not_empty()

    """ fetch and verify report for specific session, with no mapping info if it is showing correctly
     and there should not be a mapping info
        """
    session_report = source.get_student_report_response("SessionReport_no_MappingInfo", session_id)
    assert_that(session_report.status_code).is_equal_to(requests.codes.ok)
    assert_that(specific_student_report.json()["instances"][0]["reports"][0]["final_score"]).is_between(80, 230)
    assert_that(session_report.json()["instances"][0]["reports"][0]["final_cefr"]).is_not_empty()
    assert_that(session_report.json()["instances"][0]["mapping"]).is_empty()


def test_student_report_with_mapping_info():
    """ fetch and verify report for specific student, with no mapping info if it is showing correctly
       and there should be showing mapping info
          """
    student_report = source.get_student_report_response("AllReports_with_MappingInfo", None)
    assert_that(student_report.status_code).is_equal_to(requests.codes.ok)
    session_id = student_report.json()["instances"][0]["reports"][0]["session_id"]
    assert_that(student_report.json()["instances"][0]["mapping"]).is_not_empty()
    assert_that(student_report.json()["instances"][0]["mapping"]["curriculum"]).is_equal_to("MOE")
    assert_that(student_report.json()["instances"][0]["mapping"]["subject"]).is_equal_to("English")
    assert_that(student_report.json()["instances"][0]["mapping"]["k12_grade"]).is_not_empty()

    """ fetch and verify report for specific session, with no mapping info if it is showing correctly
    and there should be showing mapping info
    """
    specific_session_report = source.get_student_report_response("SessionReport_with_MappingInfo", session_id)
    assert_that(specific_session_report.status_code).is_equal_to(requests.codes.ok)
    assert_that(specific_session_report.json()["instances"][0]["mapping"]).is_not_empty()
    assert_that(specific_session_report.json()["instances"][0]["mapping"]["curriculum"]).is_equal_to("MOE")
    assert_that(student_report.json()["instances"][0]["mapping"]["k12_grade"]).is_not_empty()
    assert_that(specific_session_report.json()["instances"][0]["mapping"]["subject"]).is_equal_to("English")


def test_only_mapping_info():
    """Test if report coming out while providing only mapping infos like
    request parameters:
    {"k12Grade":int,"curriculum":str,"curriculumGrade":int,"curriculumSubject":str,"academicYear":int }
    """
    mapping_report = source.get_student_report_response("Fetch_Only_MappingInfo", None)
    assert_that(mapping_report.status_code).is_equal_to(requests.codes.ok)
    assert_that(mapping_report.json()["instances"][0]["reports"]).is_empty()
    assert_that(mapping_report.json()["instances"][0]["mapping"]).is_not_empty()
    assert_that(mapping_report.json()["instances"][0]["mapping"]["subject"]).is_equal_to("English")
    assert_that(mapping_report.json()["instances"][0]["mapping"]["curriculum"]).is_equal_to("MOE")


def test_report_mapping_schema():
    """ Validation the response schema with mapping info report if
    it is correct and response types is correct e.g string, integer
    """
    student_report = source.get_student_report_response("AllReports_with_MappingInfo", None)
    assert_valid_schema(student_report.json(), map_schema)


def test_report_no_mapping_schema():
    """ Validation the response schema with no mapping infos report
    if it is correct and response types is correct e.g string, integer """
    student_report = source.get_student_report_response("SessionReport_no_MappingInfo", None)
    assert_valid_schema(student_report.json(), no_map_schema)

