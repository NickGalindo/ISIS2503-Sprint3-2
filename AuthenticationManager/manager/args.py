import argparse

def readArguments():
    """
    Read all command line arguments
    """

    parser = argparse.ArgumentParser(description="DEFAULT DESCRIPTION")
    parser.add_argument(
        "-example",
        required=False,
        action="store_true",
        help="Example store true argument"
    )
    parser.add_argument(
        "-secondexample",
        required=False,
        type=str,
        help="Example string argument"
    )

    args = parser.parse_args()

    return args
