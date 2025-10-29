test = {
    "name": "check_ViTBlock",
    "points": 2,
    "suites": [ 
        {
            "cases": [ 
                {
                    "code": r"""
                    >>> import pickle
                    >>> from ece4078.Utility import _eval_timeout_print_str
                    >>> exec(_eval_timeout_print_str())
                    >>> test_ViTBlock = ViTBlock()
                    >>> with open("Practical10_Support/pickle/q3.pkl", "rb") as f:
                    ...     x_loaded, a_loaded, sd = pickle.load(f)
                    >>> _ = test_ViTBlock.load_state_dict(sd)
                    >>> a = eval_timeout_print("test_ViTBlock.eval()(x_loaded)") # doctest:+ELLIPSIS
                    skip ...
                    >>> torch.allclose(a, a_loaded, atol=1e-5)
                    True
                    """,
                    "hidden": False,
                    "locked": False,
                    "success_message": "Good Job",
                    "failure_message": "Wrong implementation of test_ViTBlock",
                }
            ],
            "scored": False,
            "setup": "",
            "teardown": "",
            "type": "doctest"
        }
    ]
}
