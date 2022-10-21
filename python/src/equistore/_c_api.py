# -*- coding: utf-8 -*-
# fmt: off
# flake8: noqa
"""
This file declares the C-API corresponding to equistore.h, in a way compatible
with the ctypes Python module.

This file is automatically generated from the header by `scripts/generate-declarations.py`,
do not edit it manually!
"""

import ctypes
import enum
import platform
from ctypes import CFUNCTYPE, POINTER

arch = platform.architecture()[0]
if arch == "32bit":
    c_uintptr_t = ctypes.c_uint32
elif arch == "64bit":
    c_uintptr_t = ctypes.c_uint64

EQS_SUCCESS = 0
EQS_INVALID_PARAMETER_ERROR = 1
EQS_IO_ERROR = 2
EQS_SERIALIZATION_ERROR = 3
EQS_BUFFER_SIZE_ERROR = 254
EQS_INTERNAL_ERROR = 255


eqs_status_t = ctypes.c_int32
eqs_data_origin_t = ctypes.c_uint64


class eqs_block_t(ctypes.Structure):
    pass


class eqs_tensormap_t(ctypes.Structure):
    pass


class eqs_labels_t(ctypes.Structure):
    pass

eqs_labels_t._fields_ = [
    ("labels_ptr", ctypes.c_void_p),
    ("names", POINTER(ctypes.c_char_p)),
    ("values", POINTER(ctypes.c_int32)),
    ("size", c_uintptr_t),
    ("count", c_uintptr_t),
]


class eqs_sample_mapping_t(ctypes.Structure):
    pass

eqs_sample_mapping_t._fields_ = [
    ("input", c_uintptr_t),
    ("output", c_uintptr_t),
]


class eqs_array_t(ctypes.Structure):
    pass

eqs_array_t._fields_ = [
    ("ptr", ctypes.c_void_p),
    ("origin", CFUNCTYPE(eqs_status_t, ctypes.c_void_p, POINTER(eqs_data_origin_t))),
    ("data", CFUNCTYPE(eqs_status_t, ctypes.c_void_p, POINTER(POINTER(ctypes.c_double)))),
    ("shape", CFUNCTYPE(eqs_status_t, ctypes.c_void_p, POINTER(POINTER(c_uintptr_t)), POINTER(c_uintptr_t))),
    ("reshape", CFUNCTYPE(eqs_status_t, ctypes.c_void_p, POINTER(c_uintptr_t), c_uintptr_t)),
    ("swap_axes", CFUNCTYPE(eqs_status_t, ctypes.c_void_p, c_uintptr_t, c_uintptr_t)),
    ("create", CFUNCTYPE(eqs_status_t, ctypes.c_void_p, POINTER(c_uintptr_t), c_uintptr_t, POINTER(eqs_array_t))),
    ("copy", CFUNCTYPE(eqs_status_t, ctypes.c_void_p, POINTER(eqs_array_t))),
    ("destroy", CFUNCTYPE(None, ctypes.c_void_p)),
    ("move_samples_from", CFUNCTYPE(eqs_status_t, ctypes.c_void_p, ctypes.c_void_p, POINTER(eqs_sample_mapping_t), c_uintptr_t, c_uintptr_t, c_uintptr_t)),
]


def setup_functions(lib):
    from .status import _check_status

    lib.eqs_disable_panic_printing.argtypes = [
    ]
    lib.eqs_disable_panic_printing.restype = None

    lib.eqs_last_error.argtypes = [
    ]
    lib.eqs_last_error.restype = ctypes.c_char_p

    lib.eqs_labels_position.argtypes = [
        eqs_labels_t,
        POINTER(ctypes.c_int32),
        c_uintptr_t,
        POINTER(ctypes.c_int64),
    ]
    lib.eqs_labels_position.restype = _check_status

    lib.eqs_register_data_origin.argtypes = [
        ctypes.c_char_p,
        POINTER(eqs_data_origin_t),
    ]
    lib.eqs_register_data_origin.restype = _check_status

    lib.eqs_get_data_origin.argtypes = [
        eqs_data_origin_t,
        ctypes.c_char_p,
        c_uintptr_t,
    ]
    lib.eqs_get_data_origin.restype = _check_status

    lib.eqs_get_rust_array.argtypes = [
        POINTER(eqs_array_t),
        POINTER(POINTER(ctypes.c_double)),
        POINTER(POINTER(c_uintptr_t)),
        POINTER(c_uintptr_t),
    ]
    lib.eqs_get_rust_array.restype = _check_status

    lib.eqs_block.argtypes = [
        eqs_array_t,
        eqs_labels_t,
        POINTER(eqs_labels_t),
        c_uintptr_t,
        eqs_labels_t,
    ]
    lib.eqs_block.restype = POINTER(eqs_block_t)

    lib.eqs_block_free.argtypes = [
        POINTER(eqs_block_t),
    ]
    lib.eqs_block_free.restype = _check_status

    lib.eqs_block_copy.argtypes = [
        POINTER(eqs_block_t),
    ]
    lib.eqs_block_copy.restype = POINTER(eqs_block_t)

    lib.eqs_block_labels.argtypes = [
        POINTER(eqs_block_t),
        ctypes.c_char_p,
        c_uintptr_t,
        POINTER(eqs_labels_t),
    ]
    lib.eqs_block_labels.restype = _check_status

    lib.eqs_block_data.argtypes = [
        POINTER(eqs_block_t),
        ctypes.c_char_p,
        POINTER(eqs_array_t),
    ]
    lib.eqs_block_data.restype = _check_status

    lib.eqs_block_add_gradient.argtypes = [
        POINTER(eqs_block_t),
        ctypes.c_char_p,
        eqs_array_t,
        eqs_labels_t,
        POINTER(eqs_labels_t),
        c_uintptr_t,
    ]
    lib.eqs_block_add_gradient.restype = _check_status

    lib.eqs_block_gradients_list.argtypes = [
        POINTER(eqs_block_t),
        POINTER(POINTER(ctypes.c_char_p)),
        POINTER(c_uintptr_t),
    ]
    lib.eqs_block_gradients_list.restype = _check_status

    lib.eqs_tensormap.argtypes = [
        eqs_labels_t,
        POINTER(POINTER(eqs_block_t)),
        c_uintptr_t,
    ]
    lib.eqs_tensormap.restype = POINTER(eqs_tensormap_t)

    lib.eqs_tensormap_free.argtypes = [
        POINTER(eqs_tensormap_t),
    ]
    lib.eqs_tensormap_free.restype = _check_status

    lib.eqs_tensormap_keys.argtypes = [
        POINTER(eqs_tensormap_t),
        POINTER(eqs_labels_t),
    ]
    lib.eqs_tensormap_keys.restype = _check_status

    lib.eqs_tensormap_block_by_id.argtypes = [
        POINTER(eqs_tensormap_t),
        POINTER(POINTER(eqs_block_t)),
        c_uintptr_t,
    ]
    lib.eqs_tensormap_block_by_id.restype = _check_status

    lib.eqs_tensormap_blocks_matching.argtypes = [
        POINTER(eqs_tensormap_t),
        POINTER(c_uintptr_t),
        POINTER(c_uintptr_t),
        eqs_labels_t,
    ]
    lib.eqs_tensormap_blocks_matching.restype = _check_status

    lib.eqs_tensormap_keys_to_properties.argtypes = [
        POINTER(eqs_tensormap_t),
        eqs_labels_t,
        ctypes.c_bool,
    ]
    lib.eqs_tensormap_keys_to_properties.restype = _check_status

    lib.eqs_tensormap_components_to_properties.argtypes = [
        POINTER(eqs_tensormap_t),
        POINTER(ctypes.c_char_p),
        c_uintptr_t,
    ]
    lib.eqs_tensormap_components_to_properties.restype = _check_status

    lib.eqs_tensormap_keys_to_samples.argtypes = [
        POINTER(eqs_tensormap_t),
        eqs_labels_t,
        ctypes.c_bool,
    ]
    lib.eqs_tensormap_keys_to_samples.restype = _check_status

    lib.eqs_tensormap_load.argtypes = [
        ctypes.c_char_p,
    ]
    lib.eqs_tensormap_load.restype = POINTER(eqs_tensormap_t)

    lib.eqs_tensormap_save.argtypes = [
        ctypes.c_char_p,
        POINTER(eqs_tensormap_t),
    ]
    lib.eqs_tensormap_save.restype = _check_status