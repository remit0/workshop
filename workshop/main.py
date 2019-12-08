from workshop.io import get_data, save_submission
from workshop.models import baseline


SUBMISSION_NAME = "baseline"


if __name__ == "__main__":

    data = get_data()
    submission = baseline(data)
    save_submission(submission, SUBMISSION_NAME)
