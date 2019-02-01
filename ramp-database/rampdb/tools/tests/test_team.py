import datetime
import os
import shutil

import pytest

from ramputils import read_config
from ramputils import generate_ramp_config
from ramputils.testing import database_config_template
from ramputils.testing import ramp_config_template

from rampdb.model import EventTeam
from rampdb.model import Model
from rampdb.model import Submission
from rampdb.model import SubmissionOnCVFold

from rampdb.utils import setup_db
from rampdb.utils import session_scope

from rampdb.testing import add_events
from rampdb.testing import add_problems
from rampdb.testing import add_users
from rampdb.testing import create_test_db

from rampdb.tools.team import ask_sign_up_team
from rampdb.tools.team import sign_up_team


@pytest.fixture
def session_scope_function():
    database_config = read_config(database_config_template())
    ramp_config = read_config(ramp_config_template())
    try:
        create_test_db(database_config, ramp_config)
        with session_scope(database_config['sqlalchemy']) as session:
            add_users(session)
            add_problems(session, ramp_config['ramp'])
            add_events(session, ramp_config['ramp'])
            yield session
    finally:
        shutil.rmtree(
            ramp_config['ramp']['deployment_dir'], ignore_errors=True
        )
        db, _ = setup_db(database_config['sqlalchemy'])
        Model.metadata.drop_all(db)


def test_ask_sign_up_team(session_scope_function):
    event_name, username = 'iris_test', 'test_user'

    ask_sign_up_team(session_scope_function, event_name, username)
    event_team = session_scope_function.query(EventTeam).all()
    assert len(event_team) == 1
    event_team = event_team[0]
    assert event_team.event.name == event_name
    assert event_team.team.name == username
    assert event_team.is_active is True
    assert event_team.last_submission_name is None
    current_datetime = datetime.datetime.now()
    assert event_team.signup_timestamp.year == current_datetime.year
    assert event_team.signup_timestamp.month == current_datetime.month
    assert event_team.signup_timestamp.day == current_datetime.day
    assert event_team.approved is False


def test_sign_up_team(session_scope_function):
    event_name, username = 'iris_test', 'test_user'

    sign_up_team(session_scope_function, event_name, username)
    event_team = session_scope_function.query(EventTeam).all()
    assert len(event_team) == 1
    event_team = event_team[0]

    # when signing up a team, the team is approved and the sandbox is setup:
    # the starting kit is submitted without training it.
    assert event_team.last_submission_name == 'starting_kit'
    assert event_team.approved is True
    # check the status of the sandbox submission
    submission = session_scope_function.query(Submission).all()
    assert len(submission) == 1
    submission = submission[0]
    assert submission.name == 'starting_kit'
    assert submission.event_team == event_team
    submission_file = submission.files[0]
    assert submission_file.name == 'classifier'
    assert submission_file.extension == 'py'
    assert (os.path.join('submission_000000001',
                         'classifier.py') in submission_file.path)
    # check the submission on cv fold
    cv_folds = session_scope_function.query(SubmissionOnCVFold).all()
    for fold in cv_folds:
        assert fold.state == 'new'
        assert fold.best is False
        assert fold.contributivity == pytest.approx(0)