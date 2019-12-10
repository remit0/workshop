from workshop.io import get_data, save_submission
from workshop.models import baseline, random_pick
from workshop.classes import init


if __name__ == "__main__":

    data = get_data()
    submission = baseline(data)
    save_submission(submission, "baseline")

    data = get_data()
    submission = random_pick(data)
    save_submission(submission, "random")
