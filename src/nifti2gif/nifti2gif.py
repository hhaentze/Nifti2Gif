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


import io
from typing import List, NoReturn, Tuple

import imageio
import matplotlib as mpl
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from scipy import ndimage
from tqdm import tqdm

from nifti2gif import parser


# https://stackoverflow.com/questions/7821518/save-plot-to-numpy-array
def fig2numpy(fig: plt.figure) -> np.ndarray:

    io_buf = io.BytesIO()
    fig.savefig(io_buf, format="raw")
    io_buf.seek(0)
    img_arr = np.reshape(
        np.frombuffer(io_buf.getvalue(), dtype=np.uint8),
        newshape=(int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1),
    )
    io_buf.close()

    return img_arr


def stack_slices(
    x: np.ndarray,
    y: np.ndarray = None,
    cmap: str = "bone",
    highlight_edges=True,
    figsize: Tuple[int, int] = (4, 4),
    alpha: float = 0.3,
    px_range: Tuple[int, int] = None,
) -> List[np.ndarray]:

    # initialise
    if px_range is None:
        px_range = (x.min(), x.max())
    im_list: List[np.ndarray] = []

    # plot each slice
    for i in tqdm(range(x.shape[2])):

        fig, ax = plt.subplots(1, 1, figsize=figsize)

        # plot ground image
        ax.imshow(
            x[:, :, i],
            cmap=cmap,
            vmin=px_range[0],
            vmax=px_range[1],
        )

        # plot labels
        if y is not None:
            alpha_map = np.zeros(y[:, :, i].shape)
            alpha_map[y[:, :, i] > 0] = alpha
            ax.imshow(
                y[:, :, i],
                cmap="jet",
                alpha=alpha_map,
                vmin=0,
                vmax=y.max(),
            )

        # highlight edges
        if highlight_edges:

            # calculate edges with laplace filter
            edge_slice = np.zeros(y[:, :, i].shape)
            for _class in np.unique(y[:, :, i]):
                _slice = y[:, :, i].copy()
                _slice[_slice != _class] = 0
                edges = ndimage.laplace(_slice)
                edge_slice[edges != 0] = _class

            alpha_map = np.zeros(edge_slice.shape)
            alpha_map[edge_slice > 0] = 0.9

            # create darker colormap
            edge_cmap = mpl.cm.jet(np.linspace(0, 1, int(y.max())))
            edge_cmap -= 0.4
            edge_cmap = edge_cmap.clip(0, 1)
            edge_cmap = mpl.colors.ListedColormap(edge_cmap)

            ax.imshow(
                edge_slice,
                alpha=alpha_map,
                cmap=edge_cmap,
                vmin=y.min(),
                vmax=y.max(),
            )

        plt.axis("off")
        im_list += [fig2numpy(fig)]
        plt.close()

    return im_list


def save_as_gif(
    im_list: List[np.ndarray],
    filename: str,
    duration: int = 80,
) -> NoReturn:

    imageio.mimsave(
        filename,  # output gif
        im_list,  # array of input frames
        duration=duration,  # duration in ms for each frame
        loop=0,  # loop gif indefinitely
    )


def readImage(filepath: str, orientation: str, n_turn90: int) -> np.ndarray:

    axcodes = nib.orientations.axcodes2ornt("LPI")
    img = nib.load(filepath).get_fdata()
    img = nib.orientations.apply_orientation(img, axcodes)
    for _ in range(n_turn90):
        img = np.rot90(img)
    return img


def main():

    namespace = parser.initialize()
    image = readImage(namespace.image, namespace.orientation, namespace.n_rot90)

    if namespace.mask is not None:
        mask = readImage(namespace.mask, namespace.orientation, namespace.n_rot90)
    else:
        mask = None

    slices = stack_slices(
        image,
        mask,
        cmap=namespace.cmap,
        highlight_edges=not namespace.no_edges,
        figsize=(namespace.figsize, namespace.figsize),
        alpha=namespace.alpha,
    )

    save_as_gif(slices, namespace.output, namespace.duration)


if __name__ == "__main__":
    main()
