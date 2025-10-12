test = {
    "name": "check_TD",
    "points": 3,
    "suites": [ 
        {
            "cases": [ 
                {
                    "code": r"""
                    >>> import pickle
                    >>> import numpy as np
                    >>> from ece4078.Utility import _eval_timeout_print_str
                    >>> exec(_eval_timeout_print_str())
                    >>> with open("Practical11_Support/pickle/q2.pkl", "rb") as f:
                    ...     episodes, V_loaded, env_, alpha = pickle.load(f)
                    >>> V = eval_timeout_print("temporal_learning_policy_evaluation(env_, episodes, alpha = alpha)") # doctest:+ELLIPSIS
                    skip ...
                    >>> np.all(np.isclose(np.array(list(V.values())), np.array(list(V_loaded.values()))))
                    True
                    """,
                    "hidden": False,
                    "locked": False,
                    "success_message": "Good Job",
                    "failure_message": "Wrong implementation of TD algo.",
                }
            ],
            "scored": False,
            "setup": "",
            "teardown": "",
            "type": "doctest"
        }
    ]
}