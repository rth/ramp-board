import re
import shutil

import pytest

from ramputils import read_config
from ramputils.testing import database_config_template
from ramputils.testing import ramp_config_template

from rampdb.model import EventTeam
from rampdb.model import Model

from rampdb.utils import setup_db
from rampdb.utils import session_scope
from rampdb.testing import create_toy_db

from rampdb.tools.user import get_team_by_name


@pytest.fixture(scope='module')
def session_scope_module():
    database_config = read_config(database_config_template())
    ramp_config = read_config(ramp_config_template())
    try:
        create_toy_db(database_config, ramp_config)
        with session_scope(database_config['sqlalchemy']) as session:
            yield session
    finally:
        shutil.rmtree(
            ramp_config['ramp']['deployment_dir'], ignore_errors=True
        )
        db, _ = setup_db(database_config['sqlalchemy'])
        Model.metadata.drop_all(db)


def test_team_model(session_scope_module):
    team = get_team_by_name(session_scope_module, 'test_user')
    assert re.match(r'Team\(name=.*test_user.*, admin_name=.*test_user.*\)',
                    repr(team))
    assert re.match(r'Team\(.*test_user.*\)', str(team))


@pytest.mark.parametrize(
    'backref, expected_type',
    [('team_events', EventTeam)]
)
def test_event_model_backref(session_scope_module, backref, expected_type):
    team = get_team_by_name(session_scope_module, 'test_user')
    backref_attr = getattr(team, backref)
    assert isinstance(backref_attr, list)
    # only check if the list is not empty
    if backref_attr:
        assert isinstance(backref_attr[0], expected_type)