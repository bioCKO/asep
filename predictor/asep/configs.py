#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""configs module"""

import numpy

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier

from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import SelectKBest
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import make_scorer
from sklearn.metrics import f1_score

from imblearn.ensemble import BalancedRandomForestClassifier

class Config:
    """configs module for the ASEPredictor

    Attributes:
        estimators_list (list): required, no default
            A list of 2D-tuple, where tuple is (NAME, sklearn_estimator)
        optim_params (dict): options, default dict()
            A `dict` form built-in `collections` module

    Methods:
        get_configs(self):
        dump_configs(self, fn=None): dump configurations into a pickle file
        load_configs(self, fn=None):

    Examples:
        >>> from configs import Config
        >>> config = Config()
        >>> config.init()
    """
    def __init__(self):
        """Initializing configuration metrics"""
        self.estimators_list = None
        self.optim_params = dict()

        self.searcher_params = None
        self.init_params = None
        self.classifier = None
        self.scorers = None

    def set_init_params(self, classifier="rfc"):
        """A mathod get initial params for classifier"""
        if classifier == "abc": # For AdaboostClassifier
            self.init_params = dict(
                abc__n_stimators=list(range(50, 1000, 50)),
                abc__learning_rate=numpy.linspace(.01, 1., 50),
                abc__algorithm=["SAMME", "SAMME.R"],
            )
        elif classifier == "gbc": # For GradientBoostingClassifier
            self.init_params = dict(
                gbc__leaning_rate=numpy.linspace(.01, 1., 50),
                gbc__n_estimators=list(range(50, 1000, 50)),
                gbc__min_samples_split=range(2, 12),
                gbc__min_samples_leaf=range(1, 11),
                gbc__max_depth=list(range(3, 11)),
                gbc__max_features=['sqrt', 'log2', None],
            )
        elif classifier == 'rfc': # For RandomForestClassifier
            self.init_params = dict(
                rfc__n_stimators=list(range(50, 1000, 50)),
                rfc__min_samples_split=range(2, 10),
                rfc__min_samples_leaf=range(2, 10),
                rfc__max_depth=list(range(10, 111, 10)),
                rfc__bootstrap=[False, True],
                rfc__class_weight=['balanced'],
                rfc__max_features=['sqrt', 'log2', None],
            )
        elif classifier == 'brfc': # For RandomForestClassifier
            self.init_params = dict(
                brfc__n_stimators=list(range(50, 1000, 50)),
                brfc__min_samples_split=range(2, 10),
                brfc__min_samples_leaf=range(2, 10),
                brfc__max_depth=list(range(10, 111, 10)),
                brfc__bootstrap=[False, True],
                brfc__class_weight=['balanced'],
                brfc__max_features=['sqrt', 'log2', None],
            )
        else:
            raise ValueError(
                "Unknow classifier, possible choice: abc, gbc, rfc, brfc."
            )

    def set_classifier(self, classifier="rfc"):
        """Set classifier"""
        self.set_init_params(classifier=classifier)

        if classifier == "abc": # For AdaboostClassifier
            self.classifier = ('abc', AdaBoostClassifier())
        elif classifier == "gbc": # For GradientBoostingClassifier
            self.classifier = ('gbc', GradientBoostingClassifier())
        elif classifier == 'rfc': # For RandomForestClassifier
            self.classifier = ('rfc', RandomForestClassifier())
        elif classifier == 'brfc': # For BalancedRandomForestClassifier
            self.classifier = ('brfc', BalancedRandomForestClassifier())
        else:
            raise ValueError(
                "Unknow type of classifier, possible choice [abc, gbc, rfc, brfc]"
            )

    def set_scorers(self, extra_scorer=None):
        """Set scorer"""
        basic_scorers = dict(
            roc_auc_score=make_scorer(roc_auc_score, needs_proba=True),
            precision=make_scorer(precision_score, average="micro"),
            f1_score=make_scorer(f1_score, needs_proba=True),
            accuracy=make_scorer(accuracy_score),
        )

        if extra_scorer:
            basic_scorers['extra_scorer'] = extra_scorer
        self.scorers = basic_scorers

    def set_searcher_params(self, cv=None, ncvs=10, n_jobs=5, n_iter=25,
                            refit=None):
        """Set params for the searcher"""
        if cv is None:
            cv = StratifiedKFold(n_splits=ncvs, shuffle=True)

        if refit is None:
            refit = True

        self.searcher_params = dict(
            cv=cv, iid=False, n_jobs=n_jobs, n_iter=n_iter, refit=refit,
            return_train_score=True,
        )

    def assembly(self):
        """Set up default configuration"""

        if self.classifier is None:
            self.set_classifier()

        if self.init_params is None:
            self.set_init_params()

        if self.scorers is None:
            self.set_scorers()

        if self.searcher_params is None:
            self.set_searcher_params()

        self.estimators_list = [self.classifier]
        self.optim_params['param_distributions'] = self.init_params
        self.optim_params['scoring'] = self.scorers
        self.optim_params.update(self.searcher_params)
