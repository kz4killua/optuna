from optuna.study import create_study
from optuna.study import Study
from optuna.terminator.callback import TerminatorCallback
from optuna.terminator.terminator import BaseTerminator
from optuna.trial import TrialState


class _StaticTerminator(BaseTerminator):
    def __init__(self, return_value: bool) -> None:
        self._return_value = return_value

    def should_terminate(self, study: Study) -> bool:
        return self._return_value


class _DeterministicTerminator(BaseTerminator):
    def __init__(self, termination_trial_number: int) -> None:
        self._termination_trial_number = termination_trial_number

    def should_terminate(self, study: Study) -> bool:
        trials = study.get_trials(states=[TrialState.COMPLETE])
        latest_number = max([t.number for t in trials])

        if latest_number >= self._termination_trial_number:
            return True
        else:
            return False


def test_terminator_callback_terminator() -> None:
    # This test case validates that the study is stopped when the `should_terminate` method of the
    # terminator returns `True` for the first time.
    termination_trial_number = 10

    callback = TerminatorCallback(
        terminator=_DeterministicTerminator(termination_trial_number),
        min_n_trials=10,
    )

    study = create_study()
    study.optimize(lambda t: 0.0, callbacks=[callback], n_trials=100)

    assert len(study.trials) == termination_trial_number + 1


def test_terminator_callback_min_n_trials() -> None:
    # This test case validates that the study is not stopped while the number of trials is less
    # than `min_n_trials`, even if the terminator's `should_terminate` method returns `True`.
    min_n_trials = 3

    callback = TerminatorCallback(
        terminator=_StaticTerminator(return_value=True),
        min_n_trials=min_n_trials,
    )

    study = create_study()
    study.optimize(lambda t: 0.0, callbacks=[callback], n_trials=100)

    assert len(study.trials) == min_n_trials
