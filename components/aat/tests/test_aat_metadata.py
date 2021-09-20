import requests
from tqdm.auto import tqdm
import numpy as np
import pprint
import pandas as pd
import json
from assertpy import assert_that
from alef_ml_utilities import get_config
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix

config = get_config('../../adt/src/config.yml')

np.random.seed(123456789)

def get_http_response(question_body: str, question_code: str) -> dict:
    """Get Question-Dimension as an HTTP response

    Args:
        - question_body [str]: question text
        - question_code [str]: question code

    Return:
        [dict]: Http response attached with the basic information

    """
    base_url = config["tests"]["aat"]["aat_host"] + config["tests"]["aat"]["aat_api"]

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + config["tests"]["aat"]["aat_jwt_token"]
    }

    payload = {
        "question": question_body,
        "subject": "MATH"
    }

    response = requests.post(base_url, json=payload, headers=headers)
    assert_that(response.status_code).is_equal_to(requests.codes.ok)

    return {
        "question_code": question_code,
        "question_body": question_body,
        "http_response": response.json()
    }


# create binary vector for a cognitive-dim
def _create_cogn_dim_binary_vector(lables: list, targeted_dim: str, ref_dimensions: list) -> list:
    """Creating binary vector for cognitive dimension predictions

    Args:
        - lables [list]: list of labels
        - targeted_dim [str]: the targeted dimension lable to build a vector for
        - ref_dimensions [str]: lis of all cognitive dimensions

    Return:
        [list]: a binary vector for the targeted cognitive dimension
    """

    targeted_dim = targeted_dim.strip().lower()
    lables_dims = []
    for values in lables:
        dims = [val['value'].lower().strip() for val in values if 'value' in val]
        lables_dims.append(dims)

    lables_vec = [1 if targeted_dim in dims else 0 for dims in lables_dims]
    return lables_vec


def test_get_metadata_response() -> bool:
    """Test the data again the API endpoint

    Return:
        [bool]: status flag
    """

    df = pd.read_csv("../../../test_data/test_data.csv")
    responses = []

    for i in tqdm(range(0, df.shape[0])):
        row = df.iloc[i]
        resp = get_http_response(row["question_body_and_desc"], row["code"])
        with open('../../../test_data/aat_output_meta_data.jsonl', 'a', encoding="utf8") as dest:
            dest.write(json.dumps(resp) + "\n")

    return True


def test_evaluate_dimentions() -> tuple:
    """ Evaluation the cognitive dimentions and knowledge dimentions

    Return:
        [tuple]: (cogn_dim_scores, knowledge_dim_score)
    """
    all_cogn_dims = ['ANALYZING', 'APPLYING', 'CREATING', 'UNDERSTANDING', 'REMEMBERING', 'EVALUATING']
    all_knowledge_dims = ['CONCEPTUAL', 'FACTUAL', 'PROCEDURAL']

    # load reference testing data
    test_data = pd.read_csv("../../../test_data/reviewed-with-body-and-desc.csv")

    # load predicted data
    pred_data = []
    for line in open("../../../test_data/aat_output_meta_data.jsonl", encoding="utf8"):
        if line.strip() == "":
            continue
        rec = json.loads(line.strip())
        rec["http_response"]["question_code"] = rec["question_code"]
        pred_data.append(rec["http_response"])

    assert_that(len(pred_data)).is_equal_to(test_data.shape[0])

    # create test/pred vectors
    true_cognitive_dims = {}
    for cd in all_cogn_dims:
        true_cognitive_dims[cd] = np.array([int(v) if not np.isnan(v) else 0 for v in test_data[cd].values])

    pred_cognitive_dims = {}
    all_pred_cognitive_dims = [rec["cognitive_dimensions"] for rec in pred_data]
    for cd in all_cogn_dims:
        pred_vector = _create_cogn_dim_binary_vector(all_pred_cognitive_dims, cd, all_cogn_dims)
        pred_cognitive_dims[cd] = np.array(pred_vector)

    # evaluate cognitive dimensions
    cogn_dim_scores = {}
    for cd in all_cogn_dims:
        cogn_dim_scores[cd] = {
            "f1-score": f1_score(true_cognitive_dims[cd], pred_cognitive_dims[cd]),
             "precision": precision_score(true_cognitive_dims[cd], pred_cognitive_dims[cd]),
            "recall": recall_score(true_cognitive_dims[cd], pred_cognitive_dims[cd]),
            "support": int(sum(true_cognitive_dims[cd]))
        }
    # evaluate knowledge dimensions
    true_knowledge_dims = test_data["knowledgeDimensions"].values
    pred_knowledge_dims = [rec["knowledge_dimension"]["value"] if len(rec["knowledge_dimension"]) > 0 else "UNK" for rec in
                           pred_data]

    knowledge_dim_score = {
        "f1-score": f1_score(true_knowledge_dims, pred_knowledge_dims, average="weighted"),
        "precision": precision_score(true_knowledge_dims, pred_knowledge_dims, average="weighted"),
        "recall": recall_score(true_knowledge_dims, pred_knowledge_dims, average="weighted"),
        "support": {k: sum([1 for c in true_knowledge_dims if c == k]) for k in all_knowledge_dims},
        "confusion_matrix": confusion_matrix(true_knowledge_dims, pred_knowledge_dims)
    }

    return cogn_dim_scores, knowledge_dim_score
