test = {
    "name": "check_extract_patches",
    "points": 2,
    "suites": [ 
        {
            "cases": [ 
                {
                    "code": r"""
                    >>> import pickle
                    >>> from ece4078.Utility import _eval_timeout_print_str
                    >>> exec(_eval_timeout_print_str())
                    >>> with open("Practical10_Support/pickle/q1.pkl", "rb") as f:
                    ...     xs_loaded, outs_loaded, pss_loaded = pickle.load(f)
                    >>> result = True
                    >>> for (x, patch_size, out_loaded) in zip(xs_loaded, pss_loaded, outs_loaded):
                    ...     out = eval_timeout_print("extract_patches(x, patch_size = patch_size)") # doctest:+ELLIPSIS
                    ...     result = result and torch.equal(out[0], out_loaded[0]) and (out[1] == out_loaded[1]) and (out[2] == out_loaded[2])
                    skip ...
                    >>> result
                    True
                    """,
                    "hidden": False,
                    "locked": False,
                    "success_message": "Good Job",
                    "failure_message": "Wrong implementation of extract_patches",
                }
            ],
            "scored": False,
            "setup": "",
            "teardown": "",
            "type": "doctest"
        }
    ]
}