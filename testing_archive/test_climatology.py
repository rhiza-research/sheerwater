#!/usr/bin/env python
# coding: utf-8

"""Test file for climatology data validation."""
import pytest

from sheerwater.climatology import climatology_raw


@pytest.mark.remote
def test_climatology(dask_cluster):  # noqa: ARG001
    """Test the climatology data for validity."""
    # Configurations of climatology
    first_year = 1991
    last_year = 2020
    variable = "tmp2m"

    ds = climatology_raw(variable, first_year, last_year, grid="global1_5")
    assert ds.sizes["dayofyear"] == 366
