from skyportal.tests import api
import datetime


def test_sharing_photometry(
    upload_data_token_two_groups,
    public_source_two_groups,
    public_group,
    public_group2,
    view_only_token,
    ztf_camera,
):
    upload_data_token = upload_data_token_two_groups
    public_source = public_source_two_groups
    status, data = api(
        "POST",
        "photometry",
        data={
            "obj_id": str(public_source.id),
            "mjd": 58000.0,
            "instrument_id": ztf_camera.id,
            "flux": 12.24,
            "fluxerr": 0.031,
            "zp": 25.0,
            "magsys": "ab",
            "filter": "ztfg",
            "group_ids": [public_group2.id],
        },
        token=upload_data_token,
    )
    assert status == 200
    assert data["status"] == "success"

    photometry_id = data["data"]["ids"][0]
    status, data = api(
        "GET", f"photometry/{photometry_id}?format=flux", token=upload_data_token
    )
    assert status == 200
    assert data["status"] == "success"

    status, data = api(
        "GET", f"photometry/{photometry_id}?format=flux", token=view_only_token
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    assert status == 400
    assert data["status"] == "error"
    assert "Insufficient permissions" in data["message"]

    status, data = api(
        "POST",
        "sharing",
        data={"photometryIDs": [photometry_id], "groupIDs": [public_group.id]},
        token=upload_data_token,
    )

    assert status == 200
    assert data['status'] == 'success'

    status, data = api(
        "GET", f"photometry/{photometry_id}?format=flux", token=view_only_token
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    assert status == 200
    assert data["status"] == "success"
    assert data["data"]["obj_id"] == public_source.id


def test_sharing_photometry_with_foreign_group(
    upload_data_token,
    public_source_two_groups,
    public_group,
    public_group2,
    view_only_token2,
    ztf_camera,
):
    public_source = public_source_two_groups
    status, data = api(
        "POST",
        "photometry",
        data={
            "obj_id": str(public_source.id),
            "mjd": 58000.0,
            "instrument_id": ztf_camera.id,
            "flux": 12.24,
            "fluxerr": 0.031,
            "zp": 25.0,
            "magsys": "ab",
            "filter": "ztfg",
            "group_ids": [public_group2.id],
        },
        token=upload_data_token,
    )
    assert status == 200
    assert data["status"] == "success"

    photometry_id = data["data"]["ids"][0]
    status, data = api(
        "GET", f"photometry/{photometry_id}?format=flux", token=upload_data_token
    )
    assert status == 200
    assert data["status"] == "success"

    status, data = api(
        "GET", f"photometry/{photometry_id}?format=flux", token=view_only_token2
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    assert status == 400
    assert data["status"] == "error"
    assert "Insufficient permissions" in data["message"]

    status, data = api(
        "POST",
        "sharing",
        data={"photometryIDs": [photometry_id], "groupIDs": [public_group.id]},
        token=upload_data_token,
    )

    assert status == 200
    assert data['status'] == 'success'

    status, data = api(
        "GET", f"photometry/{photometry_id}?format=flux", token=view_only_token2
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    assert status == 200
    assert data["status"] == "success"
    assert data["data"]["obj_id"] == public_source.id


def test_sharing_photometry_shares_source(
    upload_data_token,
    public_source,
    public_group,
    public_group2,
    view_only_token_group2,
    ztf_camera,
):

    status, data = api(
        "GET", f"sources/{public_source.id}", token=view_only_token_group2
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    # so the photometry is invisible to it
    assert status == 400
    assert data["status"] == "error"
    assert 'permissions' in data['message'].lower()

    status, data = api(
        "POST",
        "photometry",
        data={
            "obj_id": str(public_source.id),
            "mjd": 58000.0,
            "instrument_id": ztf_camera.id,
            "flux": 12.24,
            "fluxerr": 0.031,
            "zp": 25.0,
            "magsys": "ab",
            "filter": "ztfg",
            "group_ids": [public_group.id],
        },
        token=upload_data_token,
    )
    assert status == 200
    assert data["status"] == "success"

    photometry_id = data["data"]["ids"][0]
    status, data = api(
        "GET", f"photometry/{photometry_id}?format=flux", token=upload_data_token
    )
    assert status == 200
    assert data["status"] == "success"

    status, data = api(
        "POST",
        "sharing",
        data={"photometryIDs": [photometry_id], "groupIDs": [public_group2.id]},
        token=upload_data_token,
    )

    assert status == 200
    assert data['status'] == 'success'

    status, data = api(
        "GET", f"sources/{public_source.id}", token=view_only_token_group2
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    # so the photometry is invisible to it
    assert status == 200
    assert data["status"] == "success"


def test_sharing_spectroscopy_does_not_share_source(
    upload_data_token,
    public_source,
    public_group,
    public_group2,
    view_only_token_group2,
    lris,
):

    status, data = api(
        "GET", f"sources/{public_source.id}", token=view_only_token_group2
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    # so the photometry is invisible to it
    assert status == 400
    assert data["status"] == "error"
    assert 'permissions' in data['message'].lower()

    status, data = api(
        "POST",
        "spectrum",
        data={
            'obj_id': str(public_source.id),
            'observed_at': str(datetime.datetime.now()),
            'wavelengths': [664, 665, 666],
            'fluxes': [234.2, 232.1, 235.3],
            'group_ids': [public_group.id],
            'instrument_id': lris.id,
        },
        token=upload_data_token,
    )
    assert status == 200
    assert data["status"] == "success"

    spectrum_id = data["data"]["id"]
    status, data = api("GET", f"spectrum/{spectrum_id}", token=upload_data_token)
    assert status == 200
    assert data["status"] == "success"

    status, data = api(
        "POST",
        "sharing",
        data={"spectrumIDs": [spectrum_id], "groupIDs": [public_group2.id]},
        token=upload_data_token,
    )

    assert status == 200
    assert data['status'] == 'success'

    status, data = api(
        "GET", f"sources/{public_source.id}", token=view_only_token_group2
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    # so the photometry is invisible to it
    assert status == 400
    assert data["status"] == "error"


def test_cannot_share_unowned_photometry(
    upload_data_token,
    upload_data_token_two_groups,
    public_source,
    public_group,
    public_group2,
    view_only_token_group2,
    ztf_camera,
):

    status, data = api(
        "GET", f"sources/{public_source.id}", token=view_only_token_group2
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    # so the photometry is invisible to it
    assert status == 400
    assert data["status"] == "error"
    assert 'permissions' in data['message'].lower()

    status, data = api(
        "POST",
        "photometry",
        data={
            "obj_id": str(public_source.id),
            "mjd": 58000.0,
            "instrument_id": ztf_camera.id,
            "flux": 12.24,
            "fluxerr": 0.031,
            "zp": 25.0,
            "magsys": "ab",
            "filter": "ztfg",
            "group_ids": [public_group.id],
        },
        token=upload_data_token,
    )
    assert status == 200
    assert data["status"] == "success"

    photometry_id = data["data"]["ids"][0]
    status, data = api(
        "GET", f"photometry/{photometry_id}?format=flux", token=upload_data_token
    )
    assert status == 200
    assert data["status"] == "success"

    status, data = api(
        "POST",
        "sharing",
        data={"photometryIDs": [photometry_id], "groupIDs": [public_group2.id]},
        token=upload_data_token_two_groups,
    )

    assert status == 400
    assert data['status'] == 'error'
    assert 'owner' in data['message'].lower()


def test_system_admin_can_share_unowned_photometry(
    upload_data_token,
    super_admin_token,
    public_source,
    public_group,
    public_group2,
    view_only_token_group2,
    ztf_camera,
):

    status, data = api(
        "GET", f"sources/{public_source.id}", token=view_only_token_group2
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    # so the photometry is invisible to it
    assert status == 400
    assert data["status"] == "error"
    assert 'permissions' in data['message'].lower()

    status, data = api(
        "POST",
        "photometry",
        data={
            "obj_id": str(public_source.id),
            "mjd": 58000.0,
            "instrument_id": ztf_camera.id,
            "flux": 12.24,
            "fluxerr": 0.031,
            "zp": 25.0,
            "magsys": "ab",
            "filter": "ztfg",
            "group_ids": [public_group.id],
        },
        token=upload_data_token,
    )
    assert status == 200
    assert data["status"] == "success"

    photometry_id = data["data"]["ids"][0]
    status, data = api(
        "GET", f"photometry/{photometry_id}?format=flux", token=upload_data_token
    )
    assert status == 200
    assert data["status"] == "success"

    status, data = api(
        "POST",
        "sharing",
        data={"photometryIDs": [photometry_id], "groupIDs": [public_group2.id]},
        token=super_admin_token,
    )

    assert status == 200
    assert data['status'] == 'success'

    status, data = api(
        "GET", f"photometry/{photometry_id}?format=flux", token=view_only_token_group2
    )
    # `view_only_token only` belongs to `public_group`, but not `public_group2`
    assert status == 200
    assert data["status"] == "success"
