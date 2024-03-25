# Copyright 2024 Hartmut Häntze

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os


def assert_namespace(namespace):

    # required
    assert os.path.isfile(namespace.image), f"Image {namespace.image} not found"

    # optional
    if namespace.mask is not None:
        assert os.path.isfile(namespace.mask), f"Mask {namespace.mask} not found"

    # values
    assert namespace.duration >= 1, f"Duration{namespace.duration} must be a positiv integer"
    assert namespace.figsize >= 1, f"Figure size{namespace.figsize} must be a positiv integer"
    assert namespace.alpha > 0 and namespace.alpha <= 1, f"Alpha {namespace.alpha} must be between 0 and 1"


def initialize():
    name = "nifti2gif"

    epilog = "Hartmut Häntze - 2024"

    parser = argparse.ArgumentParser(prog=name, epilog=epilog)

    # positional arguments
    parser.add_argument("image", type=str, help="nifti image")

    # options
    parser.add_argument("--mask", type=str, required=False, help="nifti segmentation mask")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default="output.gif",
        help="output name",
    )
    parser.add_argument("--duration", type=int, required=False, default=80, help="frame duration in ms")
    parser.add_argument(
        "--no_edges",
        type=bool,
        required=False,
        default=False,
        help="do not highlight edges",
    )
    parser.add_argument("--figsize", type=int, required=False, default=4, help="figure size")
    parser.add_argument("--cmap", type=str, required=False, default="bone", help="color map")
    parser.add_argument("--alpha", type=float, required=False, default=0.3, help="color transparency")
    parser.add_argument("--orientation", type=str, required=False, default="LPI", help="image orientation")
    parser.add_argument(
        "--n_rot90", type=int, required=False, default=1, help="number of times image should be turned by 90°"
    )

    args = parser.parse_args()
    assert_namespace(args)

    return args
