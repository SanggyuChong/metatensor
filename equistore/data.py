import numpy as np
import ctypes
from typing import Union, NewType


from ._c_lib import _get_library
from ._c_api import eqs_array_t, eqs_data_origin_t, c_uintptr_t

from .utils import _call_with_growing_buffer, catch_exceptions

try:
    import torch

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


_NUMPY_STORAGE_ORIGIN = None
_TORCH_STORAGE_ORIGIN = None

if HAS_TORCH:
    # This NewType is only used for typechecking and documentation purposes
    Array = NewType("Array", Union[np.ndarray, torch.Tensor])
    """
    An ``Array`` contains the actual data stored in a
    :py:class:`equistore.TensorBlock`.

    This data is manipulated by ``equistore`` in a completely opaque way: this
    library does not know what's inside the arrays appart from a small set of
    constrains:

    - array contains numeric data;
    - they are stored as row-major, n-dimensional arrays with at least 2
      dimensions;
    - it is possible to create new arrays and move data from one array to
      another.

    The actual type of an ``Array`` depends on how the
    :py:class:`equistore.TensorBlock` was created. Currently, numpy ``ndarray``
    and torch ``Tensor`` are supported.
    """

else:
    Array = NewType("Array", np.ndarray)


def _is_numpy_array(array):
    return isinstance(array, np.ndarray)


def _numpy_origin():
    global _NUMPY_STORAGE_ORIGIN
    if _NUMPY_STORAGE_ORIGIN is None:
        _NUMPY_STORAGE_ORIGIN = ctypes.c_uint64(0)
        lib = _get_library()

        origin_name = __name__ + ".numpy"
        lib.eqs_register_data_origin(origin_name.encode("utf8"), _NUMPY_STORAGE_ORIGIN)
        _NUMPY_STORAGE_ORIGIN = _NUMPY_STORAGE_ORIGIN.value

    return _NUMPY_STORAGE_ORIGIN


def _is_torch_array(array):
    if not HAS_TORCH:
        return False

    return isinstance(array, torch.Tensor)


def _torch_origin():
    global _TORCH_STORAGE_ORIGIN
    if _TORCH_STORAGE_ORIGIN is None:
        _TORCH_STORAGE_ORIGIN = ctypes.c_uint64(0)
        lib = _get_library()

        origin_name = __name__ + ".torch"
        lib.eqs_register_data_origin(origin_name.encode("utf8"), _TORCH_STORAGE_ORIGIN)
        _TORCH_STORAGE_ORIGIN = _TORCH_STORAGE_ORIGIN.value

    return _TORCH_STORAGE_ORIGIN


def eqs_array_to_python_object(data):
    origin = data_origin(data)
    if origin in [_NUMPY_STORAGE_ORIGIN, _TORCH_STORAGE_ORIGIN]:
        return _object_from_ptr(data.ptr)
    else:
        raise ValueError(
            f"unable to handle data coming from '{data_origin_name(origin)}'"
        )


def data_origin(eqs_array):
    origin = eqs_data_origin_t()
    eqs_array.origin(eqs_array.ptr, origin)
    return origin.value


def data_origin_name(origin):
    lib = _get_library()

    return _call_with_growing_buffer(
        lambda buffer, bufflen: lib.eqs_get_data_origin(origin, buffer, bufflen)
    )


class ArrayWrapper:
    """Small wrapper making Python arrays compatible with ``eqs_array_t``."""

    def __init__(self, array):
        self.array = array
        self._shape = ctypes.ARRAY(c_uintptr_t, len(array.shape))(*array.shape)

        self._children = []
        if _is_numpy_array(array):
            array_origin = _numpy_origin()
        elif _is_torch_array(array):
            array_origin = _torch_origin()
        else:
            raise ValueError(f"unknown array type: {type(array)}")

        self.eqs_array = eqs_array_t()

        # `eqs_data.eqs_array.ptr` is a pointer to the PyObject `self`
        self.eqs_array.ptr = ctypes.cast(
            ctypes.pointer(ctypes.py_object(self)), ctypes.c_void_p
        )

        @catch_exceptions
        def eqs_array_origin(this, origin):
            origin[0] = array_origin

        # use storage.XXX.__class__ to get the right type for all functions
        self.eqs_array.origin = self.eqs_array.origin.__class__(eqs_array_origin)

        self.eqs_array.shape = self.eqs_array.shape.__class__(_eqs_array_shape)
        self.eqs_array.reshape = self.eqs_array.reshape.__class__(_eqs_array_reshape)
        self.eqs_array.swap_axes = self.eqs_array.swap_axes.__class__(
            _eqs_array_swap_axes
        )

        self.eqs_array.create = self.eqs_array.create.__class__(_eqs_array_create)
        self.eqs_array.copy = self.eqs_array.copy.__class__(_eqs_array_copy)
        self.eqs_array.destroy = self.eqs_array.destroy.__class__(_eqs_array_destroy)

        self.eqs_array.move_samples_from = self.eqs_array.move_samples_from.__class__(
            _eqs_array_move_samples_from
        )


def _object_from_ptr(ptr):
    """Extract the Python object from a pointer to the PyObject"""
    return ctypes.cast(ptr, ctypes.POINTER(ctypes.py_object)).contents.value


@catch_exceptions
def _eqs_array_shape(this, shape_ptr, shape_count):
    storage = _object_from_ptr(this)

    shape_ptr[0] = storage._shape
    shape_count[0] = len(storage._shape)


@catch_exceptions
def _eqs_array_reshape(this, shape_ptr, shape_count):
    storage = _object_from_ptr(this)

    shape = []
    for i in range(shape_count):
        shape.append(shape_ptr[i])

    storage.array = storage.array.reshape(shape)
    storage._shape = ctypes.ARRAY(c_uintptr_t, len(shape))(*shape)


@catch_exceptions
def _eqs_array_swap_axes(this, axis_1, axis_2):
    storage = _object_from_ptr(this)
    storage.array = storage.array.swapaxes(axis_1, axis_2)

    shape = storage.array.shape
    storage._shape = ctypes.ARRAY(c_uintptr_t, len(shape))(*shape)


@catch_exceptions
def _eqs_array_create(this, shape_ptr, shape_count, data_storage):
    storage = _object_from_ptr(this)

    shape = []
    for i in range(shape_count):
        shape.append(shape_ptr[i])
    dtype = storage.array.dtype

    if _is_numpy_array(storage.array):
        array = np.zeros(shape, dtype=dtype)
    elif _is_torch_array(storage.array):
        array = torch.zeros(shape, dtype=dtype, device=storage.array.device)

    wrapper = ArrayWrapper(array)
    storage._children.append(wrapper)

    data_storage[0] = wrapper.eqs_array


@catch_exceptions
def _eqs_array_copy(this, data_storage):
    storage = _object_from_ptr(this)

    if _is_numpy_array(storage.array):
        array = storage.array.copy()
    elif _is_torch_array(storage.array):
        array = storage.array.clone()

    wrapper = ArrayWrapper(array)
    data_storage[0] = wrapper.eqs_array


@catch_exceptions
def _eqs_array_destroy(this):
    storage = _object_from_ptr(this)
    storage.array = None


@catch_exceptions
def _eqs_array_move_samples_from(
    this,
    input,
    samples_ptr,
    samples_count,
    property_start,
    property_end,
):
    input = _object_from_ptr(input).array
    output = _object_from_ptr(this).array

    input_samples = []
    output_samples = []
    for i in range(samples_count):
        input_samples.append(samples_ptr[i].input)
        output_samples.append(samples_ptr[i].output)

    properties = slice(property_start, property_end)
    output[output_samples, ..., properties] = input[input_samples, ..., :]