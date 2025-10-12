test = {
    "name": "check_MC",
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
                    >>> with open("Practical11_Support/pickle/q1.pkl", "rb") as f:
                    ...     episodes, expected, env_ = pickle.load(f)
                    >>> A = eval_timeout_print("monte_carlo_first_visit_policy_evaluation(env_, episodes)") # doctest:+ELLIPSIS
                    skip ...
                    >>> np.all(np.isclose(np.array(list(A[1].values())), np.array(list(expected[1].values()))))
                    True
                    """,
                    "hidden": False,
                    "locked": False,
                    "success_message": "Correct Implementation of state_visits",
                    "failure_message": "Wrong implementation of state_visits.",
                },
                {
                    "code": r"""
                    >>> import pickle
                    >>> import numpy as np
                    >>> from ece4078.Utility import _eval_timeout_print_str
                    >>> exec(_eval_timeout_print_str())
                    >>> with open("Practical11_Support/pickle/q1.pkl", "rb") as f:
                    ...     episodes, expected, env_ = pickle.load(f)
                    >>> A = eval_timeout_print("monte_carlo_first_visit_policy_evaluation(env_, episodes)") # doctest:+ELLIPSIS
                    skip ...
                    >>> np.all(np.isclose(np.array(list(A[2].values())), np.array(list(expected[2].values()))))
                    True
                    """,
                    "hidden": False,
                    "locked": False,
                    "success_message": "Correct Implementation of state_returns",
                    "failure_message": "Wrong implementation of state_returns.",
                },
                {
                    "code": r"""
                    >>> import pickle
                    >>> import numpy as np
                    >>> from ece4078.Utility import _eval_timeout_print_str
                    >>> exec(_eval_timeout_print_str())
                    >>> with open("Practical11_Support/pickle/q1.pkl", "rb") as f:
                    ...     episodes, expected, env_ = pickle.load(f)
                    >>> A = eval_timeout_print("monte_carlo_first_visit_policy_evaluation(env_, episodes)") # doctest:+ELLIPSIS
                    skip ...
                    >>> np.all(np.isclose(np.array(list(A[2].values())), np.array(list(expected[2].values()))))
                    True
                    """,
                    "hidden": False,
                    "locked": False,
                    "success_message": "Correct Implementation of visited",
                    "failure_message": "Wrong implementation of visited.",
                },
                {
                    "code": r"""
                    >>> import pickle
                    >>> import numpy as np
                    >>> from ece4078.Utility import _eval_timeout_print_str
                    >>> exec(_eval_timeout_print_str())
                    >>> with open("Practical11_Support/pickle/q1.pkl", "rb") as f:
                    ...     episodes, expected, env_ = pickle.load(f)
                    >>> A = eval_timeout_print("monte_carlo_first_visit_policy_evaluation(env_, episodes)") # doctest:+ELLIPSIS
                    skip ...
                    >>> np.all(np.isclose(np.array(list(A[0].values())), np.array(list(expected[0].values()))))
                    True
                    """,
                    "hidden": False,
                    "locked": False,
                    "success_message": "Good Job",
                    "failure_message": "Wrong implementation of MC algo.",
                }
            ],
            "scored": False,
            "setup": "",
            "teardown": "",
            "type": "doctest"
        }
    ]
}