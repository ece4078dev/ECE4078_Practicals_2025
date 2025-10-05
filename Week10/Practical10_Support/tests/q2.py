test = {
    "name": "check_PatchEmbedding",
    "points": 2,
    "suites": [ 
        {
            "cases": [ 
                {
                    "code": r"""
                    >>> import pickle
                    >>> from ece4078.Utility import _eval_timeout_print_str
                    >>> exec(_eval_timeout_print_str())
                    >>> test_PatchEmbedding = PatchEmbedding()
                    >>> with open("Practical10_Support/pickle/q2.pkl", "rb") as f:
                    ...     x_loaded, a_loaded, sd = pickle.load(f)
                    >>> _ = test_PatchEmbedding.load_state_dict(sd)
                    >>> a = eval_timeout_print("test_PatchEmbedding(x_loaded)") # doctest:+ELLIPSIS
                    skip ...
                    >>> torch.equal(a, a_loaded)
                    True
                    """,
                    "hidden": False,
                    "locked": False,
                    "success_message": "Good Job",
                    "failure_message": "Wrong implementation of PatchEmbedding",
                }
            ],
            "scored": False,
            "setup": "",
            "teardown": "",
            "type": "doctest"
        }
    ]
}