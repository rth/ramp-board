import datetime
from sklearn.cross_validation import StratifiedShuffleSplit
from databoard.specific.problems.HEP_detector_anomalies import problem_name  # noqa

event_name = 'HEP_detector_anomalies'  # should be the same as the file name

# Unmutable config parameters that we always read from here

event_title = 'Detecting anomalies in the LHC ATLAS detector'

random_state = 57
cv_test_size = 0.5
n_cv = 8
score_type_descriptors = [
    {'name': 'auc', 'precision': 3},
    {'name': 'accuracy', 'precision': 3},
    {'name': 'negative_log_likelihood', 'precision': 3, 'new_name': 'nll'},
]
# if not specified, the first score_type_descriptor is the official score
official_score_name = 'auc'


def get_cv(y_train_array):
    cv = StratifiedShuffleSplit(
        y_train_array, n_iter=n_cv, test_size=cv_test_size,
        random_state=random_state)
    return cv

# Mutable config parameters to initialize database fields

max_members_per_team = 1
max_n_ensemble = 80  # max number of submissions in greedy ensemble
is_send_trained_mails = True
is_send_submitted_mails = True
min_duration_between_submissions = 15 * 60  # sec
opening_timestamp = datetime.datetime(2000, 1, 1, 0, 0, 0)
# before links to submissions in leaderboard are not alive
public_opening_timestamp = datetime.datetime(2000, 1, 1, 0, 0, 0)
closing_timestamp = datetime.datetime(4000, 1, 1, 0, 0, 0)
is_public = True
