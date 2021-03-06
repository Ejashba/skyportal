from skyportal.tests import api


def test_add_and_retrieve_comment_group_id(comment_token, public_source, public_group):
    status, data = api(
        'POST',
        'comment',
        data={
            'obj_id': public_source.id,
            'text': 'Comment text',
            'group_ids': [public_group.id],
        },
        token=comment_token,
    )
    assert status == 200
    comment_id = data['data']['comment_id']

    status, data = api('GET', f'comment/{comment_id}', token=comment_token)

    assert status == 200
    assert data['data']['text'] == 'Comment text'


def test_add_and_retrieve_comment_no_group_id(comment_token, public_source):
    status, data = api(
        'POST',
        'comment',
        data={'obj_id': public_source.id, 'text': 'Comment text'},
        token=comment_token,
    )
    assert status == 200
    comment_id = data['data']['comment_id']

    status, data = api('GET', f'comment/{comment_id}', token=comment_token)

    assert status == 200
    assert data['data']['text'] == 'Comment text'


def test_add_and_retrieve_comment_group_access(
    comment_token_two_groups,
    public_source_two_groups,
    public_group2,
    public_group,
    comment_token,
):
    status, data = api(
        'POST',
        'comment',
        data={
            'obj_id': public_source_two_groups.id,
            'text': 'Comment text',
            'group_ids': [public_group2.id],
        },
        token=comment_token_two_groups,
    )
    assert status == 200
    comment_id = data['data']['comment_id']

    # This token belongs to public_group2
    status, data = api('GET', f'comment/{comment_id}', token=comment_token_two_groups)
    assert status == 200
    assert data['data']['text'] == 'Comment text'

    # This token does not belnog to public_group2
    status, data = api('GET', f'comment/{comment_id}', token=comment_token)
    assert status == 400
    assert data["message"] == "Insufficient permissions."

    # Both tokens should be able to view this comment
    status, data = api(
        'POST',
        'comment',
        data={
            'obj_id': public_source_two_groups.id,
            'text': 'Comment text',
            'group_ids': [public_group.id, public_group2.id],
        },
        token=comment_token_two_groups,
    )
    assert status == 200
    comment_id = data['data']['comment_id']

    status, data = api('GET', f'comment/{comment_id}', token=comment_token_two_groups)
    assert status == 200
    assert data['data']['text'] == 'Comment text'

    status, data = api('GET', f'comment/{comment_id}', token=comment_token)
    assert status == 200
    assert data['data']['text'] == 'Comment text'


def test_update_comment_group_list(
    comment_token_two_groups,
    public_source_two_groups,
    public_group2,
    public_group,
    comment_token,
):
    status, data = api(
        'POST',
        'comment',
        data={
            'obj_id': public_source_two_groups.id,
            'text': 'Comment text',
            'group_ids': [public_group2.id],
        },
        token=comment_token_two_groups,
    )
    assert status == 200
    comment_id = data['data']['comment_id']

    # This token belongs to public_group2
    status, data = api('GET', f'comment/{comment_id}', token=comment_token_two_groups)
    assert status == 200
    assert data['data']['text'] == 'Comment text'

    # This token does not belnog to public_group2
    status, data = api('GET', f'comment/{comment_id}', token=comment_token)
    assert status == 400
    assert data["message"] == "Insufficient permissions."

    # Both tokens should be able to view comment after updating group list
    status, data = api(
        'PUT',
        f'comment/{comment_id}',
        data={
            'text': 'Comment text new',
            'group_ids': [public_group.id, public_group2.id],
        },
        token=comment_token_two_groups,
    )
    assert status == 200

    status, data = api('GET', f'comment/{comment_id}', token=comment_token_two_groups)
    assert status == 200
    assert data['data']['text'] == 'Comment text new'

    status, data = api('GET', f'comment/{comment_id}', token=comment_token)
    assert status == 200
    assert data['data']['text'] == 'Comment text new'


def test_cannot_add_comment_without_permission(view_only_token, public_source):
    status, data = api(
        'POST',
        'comment',
        data={'obj_id': public_source.id, 'text': 'Comment text'},
        token=view_only_token,
    )
    assert status == 400
    assert data['status'] == 'error'


def test_delete_comment(comment_token, public_source):
    status, data = api(
        'POST',
        'comment',
        data={'obj_id': public_source.id, 'text': 'Comment text'},
        token=comment_token,
    )
    assert status == 200
    comment_id = data['data']['comment_id']

    status, data = api('GET', f'comment/{comment_id}', token=comment_token)
    assert status == 200
    assert data['data']['text'] == 'Comment text'

    status, data = api('DELETE', f'comment/{comment_id}', token=comment_token)
    assert status == 200

    status, data = api('GET', f'comment/{comment_id}', token=comment_token)
    assert status == 400


def test_problematic_put_comment_attachment_1275(
    super_admin_token, public_source, public_group
):

    status, data = api(
        'POST',
        'comment',
        data={
            'obj_id': public_source.id,
            'text': 'asdf',
            'group_ids': [public_group.id],
        },
        token=super_admin_token,
    )
    assert status == 200
    assert data['status'] == 'success'

    # need to specify both comment name and bytes
    status2, data2 = api(
        'PUT',
        f'comment/{data["data"]["comment_id"]}',
        data={
            "attachment_bytes": "eyJ0aW1lc3RhbXAiOiAiMjAyMC0xMS0wNFQxMjowMDowMyIsICJydW4iOiAxODM5LCAiZHVyYXRpb24iOiAwLjE0NiwgInJlc3VsdCI6IHsibW9kZWwiOiAic2FsdDIiLCAiZml0X2xjX3BhcmFtZXRlcnMiOiB7ImJvdW5kcyI6IHsiYyI6IFstMiwgNV0sICJ4MSI6IFstNSwgNV0sICJ6IjogWzAsIDAuMl19fSwgImZpdF9hY2NlcHRhYmxlIjogZmFsc2UsICJwbG90X2luZm8iOiAic2FsdDIgY2hpc3EgMjAuMjkgbmRvZiAxIG9rIGZpdCBGYWxzZSIsICJtb2RlbF9hbmFseXNpcyI6IHsiaGFzX3ByZW1heF9kYXRhIjogdHJ1ZSwgImhhc19wb3N0bWF4X2RhdGEiOiBmYWxzZSwgIngxX2luX3JhbmdlIjogdHJ1ZSwgIl94MV9yYW5nZSI6IFstNCwgNF0sICJjX29rIjogdHJ1ZSwgIl9jX3JhbmdlIjogWy0xLCAyXX0sICJmaXRfcmVzdWx0cyI6IHsieiI6IDAuMTE3NDM5NTYwNTE3MDEwNjUsICJ0MCI6IDI0NTkxNTguODE5NzYyNTE2MywgIngwIjogMC4wMDA2MDg1NTg3NzI2MjI5NDY3LCAieDEiOiAtMC44NzM1ODM5NTY4MTk5NjczLCAiYyI6IC0wLjA1OTg1NTgxMTY2MDA2MzE1LCAibXdlYnYiOiAwLjA5OTU2MTk1NjAzOTAzMTEyLCAibXdyX3YiOiAzLjEsICJ6LmVyciI6IDAuMDIxNTUyNTQwMzEyMzk1NDI0LCAidDAuZXJyIjogMC45NTczNDkzNTY0OTY3MDY2LCAieDAuZXJyIjogNi43NDYwMTY5NDY3ODk5NDllLTA1LCAieDEuZXJyIjogMC42NDc4NTA5NzU5ODY5OTY2LCAiYy5lcnIiOiAwLjEzNDQxMzAzNjM5NjQxMzU1fSwgInNuY29zbW9faW5mbyI6IHsic3VjY2VzcyI6IHRydWUsICJjaGlzcSI6IDIwLjI5NDAxNzkxMDExMjMxMywgIm5kb2YiOiAxLCAiY2hpc3Fkb2YiOiAyMC4yOTQwMTc5MTAxMTIzMTN9LCAiZmx1eF9kaWN0IjogeyJ6dGZnIjogWzAuMCwgLTAuMDQyNjA1ODU1NzUwNDczMzYsIC0wLjE1OTc2MzYxMjQ2NDMxOTQyLCAtMC41MDU5ODM5ODUzNTUyNDg1LCAtMC4xMDU5NzkwNDU0NzgyOTA4MywgMy44MjIzMDg5NDc0ODQ1NzEsIDEyLjE5Njc1NDg2NzEwMDE0NywgMjMuODgzNTQ0OTEzNTM0MTUsIDM4LjIyMzIzMjgyMDM3NzUyLCA1NS4wMTU0NjcyNzgyNzMwOCwgNzQuMzQyNTQxNDE2MzQ5MjIsIDk2LjMyNzQ1MzkzMzE2MDA5LCAxMjEuMjMwODU1MjE3MTg2ODMsIDE0OS42NzE5NzMzNDU4Mzg4NiwgMTc4LjU4NzEzMzY3MjU1MDI3LCAyMDUuMDcyMDU1NjU4Nzg4NDYsIDIyOC4wNTUzMTYwNjg0MjQsIDI0Ny4zNTIzMjM5ODA4Nzg1NywgMjYyLjYwOTI1MTk2MzQ1NzMsIDI3My45NjAxOTExOTE4NTEsIDI4Mi4wMTYzOTE3NTE3NzMsIDI4Ni4zNzI2Mjg3NjU4NjE2MywgMjg2LjY4ODcwMTAxODEzNDQ1LCAyODMuNTU0NTY3MTE3MzQ4MSwgMjc3LjY5MjY0NTUyNDYwODgsIDI2OS40ODM1NDU5ODQ2MTMzLCAyNTkuMTAxNDEyMTkxMjIwOCwgMjQ2Ljk2OTEyOTQ0OTc2NTE1LCAyMzMuODk5MTY4NzM2OTE5MjgsIDIyMC4xMzIyNzI0NjI2MDgzNCwgMjA1LjcxNjY4NzM5MzQxMzE0LCAxOTAuNTk3MTUyMDAzOTQzODUsIDE3NS41NTM4NDE0NDAyMjYyMiwgMTYxLjE2NTk5Mzk2NDQ1NDMyLCAxNDcuNTEwNTE3ODIyNjI0MTcsIDEzNC40NDYyMjA0NjIxODY5NCwgMTIxLjg5NDI1MDE3MDAxNDM5LCAxMDkuOTA0OTI2NzQzMDg2NzIsIDk4Ljg1ODU4MjA1NTk5MDE0LCA4OC44MjIyNDkyNDQ5ODgwNiwgNzkuODU1NDY1Nzk5NzkzOTMsIDcyLjA5NTcyMzMzMTQ2NzIsIDY1LjMwMjgyMzM5NDQzNzU3LCA1OS4yNTMxMjgyMDM2MzYzNDQsIDUzLjkyNjI2NjAzMjI5NDUyLCA0OS40MTk3OTAzMTc3NTMyOCwgNDUuNjc4NTQ4MjU5MDMwNjQsIDQyLjMxMjkyMDczNTM0MDk3LCAzOS4xMzUwNDI0OTI2NjEzMSwgMzYuMTc1NTQ2NTcyMTI5NywgMzMuNDI4OTg3OTU4MTgzNDUsIDMwLjkyODcxOTcyNjIzMzE4NywgMjguNzUyMjgxODYxNTg1NjQsIDI2LjkwMjQ3ODU5MDAzMDA5NiwgMjUuMzMzOTc4MzQ4MzEyMzYsIDI0LjAxMTA1NjIzOTM4MjkzNSwgMjIuOTAzODgyMjIyNjQwNTU0LCAyMS45ODU1MjExMDM5NjA1NTgsIDIxLjE4MzYxNTc5ODI1OTE3MiwgMjAuNDUyMjYzMDY5MTMwNDY3LCAxOS43ODQ2NDgxNDA4MjM3NTUsIDE5LjE3NTU1OTc1NTQwMzQyNywgMTguNjIwMzc0ODc2NTc1MjksIDE4LjExNTA4NTAxNDE3MjMxNSwgMTcuNjU2MjcwMzk5NzY4MzIsIDE3LjI0MDMyMDg1NjEyNTk5LCAxNi44NTkxMTMwMzUwMTQ1NzcsIDE2LjQ4NjE4ODc2Njc0MTY5OCwgMTYuMTE4OTQwODAyOTc3MDQ3LCAxNS43NTg0NzM3NDM2NDc4NjIsIDE1LjQwNTc0NTcwNDAwMTI0NiwgMTUuMDYxNzIzMzM0MjQ2MDQzLCAxNC43MjczODEwMjI5Nzk4MDQsIDE0LjQwMzY5NTMxNTY1OTUzLCAxNC4wOTE2Mzk5MTExNzczNTMsIDEzLjc5MjE4MTE0NDkwNTA1OCwgMTMuNTA2MjczODY5OTM1ODA3LCAxMy4yMzQ4Njg0ODM3Njc1MzksIDEyLjk4MTU3MzMxODc4OTYyN10sICJ6dGZyIjogWzAuMCwgMC4yMDkwMjkyNzU5Mzc3MzQ5LCAwLjc4ODc0NjQ5ODgxMDcwMzksIDEuNzIyNTcyMDQ5MDAyNDYxNCwgMy42OTI5MjkzMjcwMDQxNDMyLCA4Ljc5MDcxNTY1MDg1NDgwNSwgMTcuNjMyNDU0MDIxMTYyMzM1LCAyOS4yNTAwMTgzNTEwOTI2MTcsIDQzLjA2OTYyOTQwMjAzMDcxLCA1OC44MjcyMTA3OTA5ODU1NywgNzYuNDg2NjMwNDI0MzgxMzksIDk2LjE5OTQ4Mzk4ODEwOTcyLCAxMTguMjA0MzUzMTc5NjA4NSwgMTQzLjAwNzYzODUwNjUxMDY2LCAxNjguMzEyOTYwNzk1NjcyMDQsIDE5MS45NDMxNTA1MTU0NTUwNywgMjEzLjExMjQ5MjAxODQ1MDMsIDIzMS43MDU4NjcwOTQ1MjU0MiwgMjQ3LjQ3Nzg0MDIwMzIxNTYsIDI2MC41NjYzOTUwNzY4NzIzNywgMjcxLjQ3ODE4NDY2MTkwMjcsIDI3OS44ODk5NTU4MjU4NTQ1NCwgMjg1LjUzNjM3MjA2NjA5NTA1LCAyODguNTYwNDMyMzQ4MTA3ODQsIDI4OS4yMDkxODAzODM0NjU1LCAyODcuNjUwMjExNzU1NDQxNywgMjg0LjAxMjM5MTM1MDM1NTcsIDI3OC40MDEyNzQyOTkwNjQ1LCAyNzAuNzQ3ODQ1MjM1ODM2MTcsIDI2MS4yMDkzMzY3NjQxOTcyLCAyNDkuOTY1NDI1MjA5MDkzNjQsIDIzNi45OTYwODA4NDE3NDY1NiwgMjIzLjgyMjE4ODMwMjU3MjMsIDIxMS42MDIyMzAxOTM5NTMzMiwgMjAwLjU3Njg4NDg1MTY3NjUsIDE5MC41OTQ5NzcwNDMxMDUzMywgMTgxLjU4NjIyMjIwNDI1NTUzLCAxNzMuNDE4MDQxNzE4Nzc0NzMsIDE2NS43MzA3MDQ1NzY4OTE4NCwgMTU4LjQ4MjI5NTMyNDg2NTAyLCAxNTEuNjk5NTg5MDg1MzM3ODYsIDE0NS40NTE4MTQ5NDI5MDg2NywgMTM5LjU4NDA3NTMzMzM1MzIsIDEzMy45NTkxODY4MzI4Njg3NywgMTI4LjU3MzUxMzA2ODM0MDUsIDEyMy41MTE2ODQ3MzA1NTI0LCAxMTguNzIxNzkwNTIxMTI0MTMsIDExMy44MDQ0MDc3MTY2NDgyOSwgMTA4LjYwODM1NTg2NDcxNzEzLCAxMDMuMjQxMzg2NjgzMDIxNDUsIDk3Ljc2NTI0NjgyMjU0MDA4LCA5Mi4zMzM3MTQxNjc3MjA4MSwgODcuMTk3NDkyMjAyMTk5MDQsIDgyLjQyODMxMDQ2NDc4ODMyLCA3Ny45Nzc5MjUyNzYzNzA4OCwgNzMuODEwMDcxNTY1NjgzNjMsIDY5Ljg5MTk0NDMyNjg0OSwgNjYuMTk5MzM4MTkxNjMwNCwgNjIuODE0MDY4Mjk4NzQ1Njk2LCA1OS43NzUwOTExMzk3MjA2MywgNTcuMDUxMDcyNjc2ODk3MTUsIDU0LjYxNDMxOTc2NDU2NTM0NCwgNTIuNDQxMzM3NjgzNjU1NjYsIDUwLjUxMTUyNzYyMjUyMDkyLCA0OC44MDY4ODUwNDEwMjEyMiwgNDcuMzA5MjE5ODg4NjkxNjE1LCA0NS45ODU1MTU2NDIxNDYxNywgNDQuNzQxNDAwNjkzNDQ3MDQsIDQzLjU2MjcwOTkyODYwOTE2NiwgNDIuNDQ3OTkwOTkzNDI2OTksIDQxLjM5NTQ1MDExNjg4MzUsIDQwLjQwMzQzMDc2MDk2MTY4LCAzOS40NzA0MDYxMjgyMjcyNCwgMzguNTk0OTYwNzIwNjY3NCwgMzcuNzc1Nzc3NzI1ODY5OTQsIDM3LjAxMTYzMDk2NDg1NDUyNSwgMzYuMzAxMzgwMzgzNDY1NjU2LCAzNS42NDM5NTk0MzY0NjcxNSwgMzUuMDQzODYwODA3MzQ5ODk0XSwgIm9ic2pkIjogWzI0NTkxMzYuNDcwOTcxMzA2LCAyNDU5MTM3LjQ3MDk3MTMwNiwgMjQ1OTEzOC40NzA5NzEzMDYsIDI0NTkxMzkuNDcwOTcxMzA2LCAyNDU5MTQwLjQ3MDk3MTMwNiwgMjQ1OTE0MS40NzA5NzEzMDYsIDI0NTkxNDIuNDcwOTcxMzA2LCAyNDU5MTQzLjQ3MDk3MTMwNiwgMjQ1OTE0NC40NzA5NzEzMDYsIDI0NTkxNDUuNDcwOTcxMzA2LCAyNDU5MTQ2LjQ3MDk3MTMwNiwgMjQ1OTE0Ny40NzA5NzEzMDYsIDI0NTkxNDguNDcwOTcxMzA2LCAyNDU5MTQ5LjQ3MDk3MTMwNiwgMjQ1OTE1MC40NzA5NzEzMDYsIDI0NTkxNTEuNDcwOTcxMzA2LCAyNDU5MTUyLjQ3MDk3MTMwNiwgMjQ1OTE1My40NzA5NzEzMDYsIDI0NTkxNTQuNDcwOTcxMzA2LCAyNDU5MTU1LjQ3MDk3MTMwNiwgMjQ1OTE1Ni40NzA5NzEzMDYsIDI0NTkxNTcuNDcwOTcxMzA2LCAyNDU5MTU4LjQ3MDk3MTMwNiwgMjQ1OTE1OS40NzA5NzEzMDYsIDI0NTkxNjAuNDcwOTcxMzA2LCAyNDU5MTYxLjQ3MDk3MTMwNiwgMjQ1OTE2Mi40NzA5NzEzMDYsIDI0NTkxNjMuNDcwOTcxMzA2LCAyNDU5MTY0LjQ3MDk3MTMwNiwgMjQ1OTE2NS40NzA5NzEzMDYsIDI0NTkxNjYuNDcwOTcxMzA2LCAyNDU5MTY3LjQ3MDk3MTMwNiwgMjQ1OTE2OC40NzA5NzEzMDYsIDI0NTkxNjkuNDcwOTcxMzA2LCAyNDU5MTcwLjQ3MDk3MTMwNiwgMjQ1OTE3MS40NzA5NzEzMDYsIDI0NTkxNzIuNDcwOTcxMzA2LCAyNDU5MTczLjQ3MDk3MTMwNiwgMjQ1OTE3NC40NzA5NzEzMDYsIDI0NTkxNzUuNDcwOTcxMzA2LCAyNDU5MTc2LjQ3MDk3MTMwNiwgMjQ1OTE3Ny40NzA5NzEzMDYsIDI0NTkxNzguNDcwOTcxMzA2LCAyNDU5MTc5LjQ3MDk3MTMwNiwgMjQ1OTE4MC40NzA5NzEzMDYsIDI0NTkxODEuNDcwOTcxMzA2LCAyNDU5MTgyLjQ3MDk3MTMwNiwgMjQ1OTE4My40NzA5NzEzMDYsIDI0NTkxODQuNDcwOTcxMzA2LCAyNDU5MTg1LjQ3MDk3MTMwNiwgMjQ1OTE4Ni40NzA5NzEzMDYsIDI0NTkxODcuNDcwOTcxMzA2LCAyNDU5MTg4LjQ3MDk3MTMwNiwgMjQ1OTE4OS40NzA5NzEzMDYsIDI0NTkxOTAuNDcwOTcxMzA2LCAyNDU5MTkxLjQ3MDk3MTMwNiwgMjQ1OTE5Mi40NzA5NzEzMDYsIDI0NTkxOTMuNDcwOTcxMzA2LCAyNDU5MTk0LjQ3MDk3MTMwNiwgMjQ1OTE5NS40NzA5NzEzMDYsIDI0NTkxOTYuNDcwOTcxMzA2LCAyNDU5MTk3LjQ3MDk3MTMwNiwgMjQ1OTE5OC40NzA5NzEzMDYsIDI0NTkxOTkuNDcwOTcxMzA2LCAyNDU5MjAwLjQ3MDk3MTMwNiwgMjQ1OTIwMS40NzA5NzEzMDYsIDI0NTkyMDIuNDcwOTcxMzA2LCAyNDU5MjAzLjQ3MDk3MTMwNiwgMjQ1OTIwNC40NzA5NzEzMDYsIDI0NTkyMDUuNDcwOTcxMzA2LCAyNDU5MjA2LjQ3MDk3MTMwNiwgMjQ1OTIwNy40NzA5NzEzMDYsIDI0NTkyMDguNDcwOTcxMzA2LCAyNDU5MjA5LjQ3MDk3MTMwNiwgMjQ1OTIxMC40NzA5NzEzMDYsIDI0NTkyMTEuNDcwOTcxMzA2LCAyNDU5MjEyLjQ3MDk3MTMwNiwgMjQ1OTIxMy40NzA5NzEzMDYsIDI0NTkyMTQuNDcwOTcxMzA2XX19fQ=="
        },
        token=super_admin_token,
    )

    assert status2 == 400
    assert data2['status'] == 'error'

    payload = {
        "attachment_bytes": "eyJ0aW1lc3RhbXAiOiAiMjAyMC0xMS0wNFQxMjowMDowMyIsICJydW4iOiAxODM5LCAiZHVyYXRpb24iOiAwLjE0NiwgInJlc3VsdCI6IHsibW9kZWwiOiAic2FsdDIiLCAiZml0X2xjX3BhcmFtZXRlcnMiOiB7ImJvdW5kcyI6IHsiYyI6IFstMiwgNV0sICJ4MSI6IFstNSwgNV0sICJ6IjogWzAsIDAuMl19fSwgImZpdF9hY2NlcHRhYmxlIjogZmFsc2UsICJwbG90X2luZm8iOiAic2FsdDIgY2hpc3EgMjAuMjkgbmRvZiAxIG9rIGZpdCBGYWxzZSIsICJtb2RlbF9hbmFseXNpcyI6IHsiaGFzX3ByZW1heF9kYXRhIjogdHJ1ZSwgImhhc19wb3N0bWF4X2RhdGEiOiBmYWxzZSwgIngxX2luX3JhbmdlIjogdHJ1ZSwgIl94MV9yYW5nZSI6IFstNCwgNF0sICJjX29rIjogdHJ1ZSwgIl9jX3JhbmdlIjogWy0xLCAyXX0sICJmaXRfcmVzdWx0cyI6IHsieiI6IDAuMTE3NDM5NTYwNTE3MDEwNjUsICJ0MCI6IDI0NTkxNTguODE5NzYyNTE2MywgIngwIjogMC4wMDA2MDg1NTg3NzI2MjI5NDY3LCAieDEiOiAtMC44NzM1ODM5NTY4MTk5NjczLCAiYyI6IC0wLjA1OTg1NTgxMTY2MDA2MzE1LCAibXdlYnYiOiAwLjA5OTU2MTk1NjAzOTAzMTEyLCAibXdyX3YiOiAzLjEsICJ6LmVyciI6IDAuMDIxNTUyNTQwMzEyMzk1NDI0LCAidDAuZXJyIjogMC45NTczNDkzNTY0OTY3MDY2LCAieDAuZXJyIjogNi43NDYwMTY5NDY3ODk5NDllLTA1LCAieDEuZXJyIjogMC42NDc4NTA5NzU5ODY5OTY2LCAiYy5lcnIiOiAwLjEzNDQxMzAzNjM5NjQxMzU1fSwgInNuY29zbW9faW5mbyI6IHsic3VjY2VzcyI6IHRydWUsICJjaGlzcSI6IDIwLjI5NDAxNzkxMDExMjMxMywgIm5kb2YiOiAxLCAiY2hpc3Fkb2YiOiAyMC4yOTQwMTc5MTAxMTIzMTN9LCAiZmx1eF9kaWN0IjogeyJ6dGZnIjogWzAuMCwgLTAuMDQyNjA1ODU1NzUwNDczMzYsIC0wLjE1OTc2MzYxMjQ2NDMxOTQyLCAtMC41MDU5ODM5ODUzNTUyNDg1LCAtMC4xMDU5NzkwNDU0NzgyOTA4MywgMy44MjIzMDg5NDc0ODQ1NzEsIDEyLjE5Njc1NDg2NzEwMDE0NywgMjMuODgzNTQ0OTEzNTM0MTUsIDM4LjIyMzIzMjgyMDM3NzUyLCA1NS4wMTU0NjcyNzgyNzMwOCwgNzQuMzQyNTQxNDE2MzQ5MjIsIDk2LjMyNzQ1MzkzMzE2MDA5LCAxMjEuMjMwODU1MjE3MTg2ODMsIDE0OS42NzE5NzMzNDU4Mzg4NiwgMTc4LjU4NzEzMzY3MjU1MDI3LCAyMDUuMDcyMDU1NjU4Nzg4NDYsIDIyOC4wNTUzMTYwNjg0MjQsIDI0Ny4zNTIzMjM5ODA4Nzg1NywgMjYyLjYwOTI1MTk2MzQ1NzMsIDI3My45NjAxOTExOTE4NTEsIDI4Mi4wMTYzOTE3NTE3NzMsIDI4Ni4zNzI2Mjg3NjU4NjE2MywgMjg2LjY4ODcwMTAxODEzNDQ1LCAyODMuNTU0NTY3MTE3MzQ4MSwgMjc3LjY5MjY0NTUyNDYwODgsIDI2OS40ODM1NDU5ODQ2MTMzLCAyNTkuMTAxNDEyMTkxMjIwOCwgMjQ2Ljk2OTEyOTQ0OTc2NTE1LCAyMzMuODk5MTY4NzM2OTE5MjgsIDIyMC4xMzIyNzI0NjI2MDgzNCwgMjA1LjcxNjY4NzM5MzQxMzE0LCAxOTAuNTk3MTUyMDAzOTQzODUsIDE3NS41NTM4NDE0NDAyMjYyMiwgMTYxLjE2NTk5Mzk2NDQ1NDMyLCAxNDcuNTEwNTE3ODIyNjI0MTcsIDEzNC40NDYyMjA0NjIxODY5NCwgMTIxLjg5NDI1MDE3MDAxNDM5LCAxMDkuOTA0OTI2NzQzMDg2NzIsIDk4Ljg1ODU4MjA1NTk5MDE0LCA4OC44MjIyNDkyNDQ5ODgwNiwgNzkuODU1NDY1Nzk5NzkzOTMsIDcyLjA5NTcyMzMzMTQ2NzIsIDY1LjMwMjgyMzM5NDQzNzU3LCA1OS4yNTMxMjgyMDM2MzYzNDQsIDUzLjkyNjI2NjAzMjI5NDUyLCA0OS40MTk3OTAzMTc3NTMyOCwgNDUuNjc4NTQ4MjU5MDMwNjQsIDQyLjMxMjkyMDczNTM0MDk3LCAzOS4xMzUwNDI0OTI2NjEzMSwgMzYuMTc1NTQ2NTcyMTI5NywgMzMuNDI4OTg3OTU4MTgzNDUsIDMwLjkyODcxOTcyNjIzMzE4NywgMjguNzUyMjgxODYxNTg1NjQsIDI2LjkwMjQ3ODU5MDAzMDA5NiwgMjUuMzMzOTc4MzQ4MzEyMzYsIDI0LjAxMTA1NjIzOTM4MjkzNSwgMjIuOTAzODgyMjIyNjQwNTU0LCAyMS45ODU1MjExMDM5NjA1NTgsIDIxLjE4MzYxNTc5ODI1OTE3MiwgMjAuNDUyMjYzMDY5MTMwNDY3LCAxOS43ODQ2NDgxNDA4MjM3NTUsIDE5LjE3NTU1OTc1NTQwMzQyNywgMTguNjIwMzc0ODc2NTc1MjksIDE4LjExNTA4NTAxNDE3MjMxNSwgMTcuNjU2MjcwMzk5NzY4MzIsIDE3LjI0MDMyMDg1NjEyNTk5LCAxNi44NTkxMTMwMzUwMTQ1NzcsIDE2LjQ4NjE4ODc2Njc0MTY5OCwgMTYuMTE4OTQwODAyOTc3MDQ3LCAxNS43NTg0NzM3NDM2NDc4NjIsIDE1LjQwNTc0NTcwNDAwMTI0NiwgMTUuMDYxNzIzMzM0MjQ2MDQzLCAxNC43MjczODEwMjI5Nzk4MDQsIDE0LjQwMzY5NTMxNTY1OTUzLCAxNC4wOTE2Mzk5MTExNzczNTMsIDEzLjc5MjE4MTE0NDkwNTA1OCwgMTMuNTA2MjczODY5OTM1ODA3LCAxMy4yMzQ4Njg0ODM3Njc1MzksIDEyLjk4MTU3MzMxODc4OTYyN10sICJ6dGZyIjogWzAuMCwgMC4yMDkwMjkyNzU5Mzc3MzQ5LCAwLjc4ODc0NjQ5ODgxMDcwMzksIDEuNzIyNTcyMDQ5MDAyNDYxNCwgMy42OTI5MjkzMjcwMDQxNDMyLCA4Ljc5MDcxNTY1MDg1NDgwNSwgMTcuNjMyNDU0MDIxMTYyMzM1LCAyOS4yNTAwMTgzNTEwOTI2MTcsIDQzLjA2OTYyOTQwMjAzMDcxLCA1OC44MjcyMTA3OTA5ODU1NywgNzYuNDg2NjMwNDI0MzgxMzksIDk2LjE5OTQ4Mzk4ODEwOTcyLCAxMTguMjA0MzUzMTc5NjA4NSwgMTQzLjAwNzYzODUwNjUxMDY2LCAxNjguMzEyOTYwNzk1NjcyMDQsIDE5MS45NDMxNTA1MTU0NTUwNywgMjEzLjExMjQ5MjAxODQ1MDMsIDIzMS43MDU4NjcwOTQ1MjU0MiwgMjQ3LjQ3Nzg0MDIwMzIxNTYsIDI2MC41NjYzOTUwNzY4NzIzNywgMjcxLjQ3ODE4NDY2MTkwMjcsIDI3OS44ODk5NTU4MjU4NTQ1NCwgMjg1LjUzNjM3MjA2NjA5NTA1LCAyODguNTYwNDMyMzQ4MTA3ODQsIDI4OS4yMDkxODAzODM0NjU1LCAyODcuNjUwMjExNzU1NDQxNywgMjg0LjAxMjM5MTM1MDM1NTcsIDI3OC40MDEyNzQyOTkwNjQ1LCAyNzAuNzQ3ODQ1MjM1ODM2MTcsIDI2MS4yMDkzMzY3NjQxOTcyLCAyNDkuOTY1NDI1MjA5MDkzNjQsIDIzNi45OTYwODA4NDE3NDY1NiwgMjIzLjgyMjE4ODMwMjU3MjMsIDIxMS42MDIyMzAxOTM5NTMzMiwgMjAwLjU3Njg4NDg1MTY3NjUsIDE5MC41OTQ5NzcwNDMxMDUzMywgMTgxLjU4NjIyMjIwNDI1NTUzLCAxNzMuNDE4MDQxNzE4Nzc0NzMsIDE2NS43MzA3MDQ1NzY4OTE4NCwgMTU4LjQ4MjI5NTMyNDg2NTAyLCAxNTEuNjk5NTg5MDg1MzM3ODYsIDE0NS40NTE4MTQ5NDI5MDg2NywgMTM5LjU4NDA3NTMzMzM1MzIsIDEzMy45NTkxODY4MzI4Njg3NywgMTI4LjU3MzUxMzA2ODM0MDUsIDEyMy41MTE2ODQ3MzA1NTI0LCAxMTguNzIxNzkwNTIxMTI0MTMsIDExMy44MDQ0MDc3MTY2NDgyOSwgMTA4LjYwODM1NTg2NDcxNzEzLCAxMDMuMjQxMzg2NjgzMDIxNDUsIDk3Ljc2NTI0NjgyMjU0MDA4LCA5Mi4zMzM3MTQxNjc3MjA4MSwgODcuMTk3NDkyMjAyMTk5MDQsIDgyLjQyODMxMDQ2NDc4ODMyLCA3Ny45Nzc5MjUyNzYzNzA4OCwgNzMuODEwMDcxNTY1NjgzNjMsIDY5Ljg5MTk0NDMyNjg0OSwgNjYuMTk5MzM4MTkxNjMwNCwgNjIuODE0MDY4Mjk4NzQ1Njk2LCA1OS43NzUwOTExMzk3MjA2MywgNTcuMDUxMDcyNjc2ODk3MTUsIDU0LjYxNDMxOTc2NDU2NTM0NCwgNTIuNDQxMzM3NjgzNjU1NjYsIDUwLjUxMTUyNzYyMjUyMDkyLCA0OC44MDY4ODUwNDEwMjEyMiwgNDcuMzA5MjE5ODg4NjkxNjE1LCA0NS45ODU1MTU2NDIxNDYxNywgNDQuNzQxNDAwNjkzNDQ3MDQsIDQzLjU2MjcwOTkyODYwOTE2NiwgNDIuNDQ3OTkwOTkzNDI2OTksIDQxLjM5NTQ1MDExNjg4MzUsIDQwLjQwMzQzMDc2MDk2MTY4LCAzOS40NzA0MDYxMjgyMjcyNCwgMzguNTk0OTYwNzIwNjY3NCwgMzcuNzc1Nzc3NzI1ODY5OTQsIDM3LjAxMTYzMDk2NDg1NDUyNSwgMzYuMzAxMzgwMzgzNDY1NjU2LCAzNS42NDM5NTk0MzY0NjcxNSwgMzUuMDQzODYwODA3MzQ5ODk0XSwgIm9ic2pkIjogWzI0NTkxMzYuNDcwOTcxMzA2LCAyNDU5MTM3LjQ3MDk3MTMwNiwgMjQ1OTEzOC40NzA5NzEzMDYsIDI0NTkxMzkuNDcwOTcxMzA2LCAyNDU5MTQwLjQ3MDk3MTMwNiwgMjQ1OTE0MS40NzA5NzEzMDYsIDI0NTkxNDIuNDcwOTcxMzA2LCAyNDU5MTQzLjQ3MDk3MTMwNiwgMjQ1OTE0NC40NzA5NzEzMDYsIDI0NTkxNDUuNDcwOTcxMzA2LCAyNDU5MTQ2LjQ3MDk3MTMwNiwgMjQ1OTE0Ny40NzA5NzEzMDYsIDI0NTkxNDguNDcwOTcxMzA2LCAyNDU5MTQ5LjQ3MDk3MTMwNiwgMjQ1OTE1MC40NzA5NzEzMDYsIDI0NTkxNTEuNDcwOTcxMzA2LCAyNDU5MTUyLjQ3MDk3MTMwNiwgMjQ1OTE1My40NzA5NzEzMDYsIDI0NTkxNTQuNDcwOTcxMzA2LCAyNDU5MTU1LjQ3MDk3MTMwNiwgMjQ1OTE1Ni40NzA5NzEzMDYsIDI0NTkxNTcuNDcwOTcxMzA2LCAyNDU5MTU4LjQ3MDk3MTMwNiwgMjQ1OTE1OS40NzA5NzEzMDYsIDI0NTkxNjAuNDcwOTcxMzA2LCAyNDU5MTYxLjQ3MDk3MTMwNiwgMjQ1OTE2Mi40NzA5NzEzMDYsIDI0NTkxNjMuNDcwOTcxMzA2LCAyNDU5MTY0LjQ3MDk3MTMwNiwgMjQ1OTE2NS40NzA5NzEzMDYsIDI0NTkxNjYuNDcwOTcxMzA2LCAyNDU5MTY3LjQ3MDk3MTMwNiwgMjQ1OTE2OC40NzA5NzEzMDYsIDI0NTkxNjkuNDcwOTcxMzA2LCAyNDU5MTcwLjQ3MDk3MTMwNiwgMjQ1OTE3MS40NzA5NzEzMDYsIDI0NTkxNzIuNDcwOTcxMzA2LCAyNDU5MTczLjQ3MDk3MTMwNiwgMjQ1OTE3NC40NzA5NzEzMDYsIDI0NTkxNzUuNDcwOTcxMzA2LCAyNDU5MTc2LjQ3MDk3MTMwNiwgMjQ1OTE3Ny40NzA5NzEzMDYsIDI0NTkxNzguNDcwOTcxMzA2LCAyNDU5MTc5LjQ3MDk3MTMwNiwgMjQ1OTE4MC40NzA5NzEzMDYsIDI0NTkxODEuNDcwOTcxMzA2LCAyNDU5MTgyLjQ3MDk3MTMwNiwgMjQ1OTE4My40NzA5NzEzMDYsIDI0NTkxODQuNDcwOTcxMzA2LCAyNDU5MTg1LjQ3MDk3MTMwNiwgMjQ1OTE4Ni40NzA5NzEzMDYsIDI0NTkxODcuNDcwOTcxMzA2LCAyNDU5MTg4LjQ3MDk3MTMwNiwgMjQ1OTE4OS40NzA5NzEzMDYsIDI0NTkxOTAuNDcwOTcxMzA2LCAyNDU5MTkxLjQ3MDk3MTMwNiwgMjQ1OTE5Mi40NzA5NzEzMDYsIDI0NTkxOTMuNDcwOTcxMzA2LCAyNDU5MTk0LjQ3MDk3MTMwNiwgMjQ1OTE5NS40NzA5NzEzMDYsIDI0NTkxOTYuNDcwOTcxMzA2LCAyNDU5MTk3LjQ3MDk3MTMwNiwgMjQ1OTE5OC40NzA5NzEzMDYsIDI0NTkxOTkuNDcwOTcxMzA2LCAyNDU5MjAwLjQ3MDk3MTMwNiwgMjQ1OTIwMS40NzA5NzEzMDYsIDI0NTkyMDIuNDcwOTcxMzA2LCAyNDU5MjAzLjQ3MDk3MTMwNiwgMjQ1OTIwNC40NzA5NzEzMDYsIDI0NTkyMDUuNDcwOTcxMzA2LCAyNDU5MjA2LjQ3MDk3MTMwNiwgMjQ1OTIwNy40NzA5NzEzMDYsIDI0NTkyMDguNDcwOTcxMzA2LCAyNDU5MjA5LjQ3MDk3MTMwNiwgMjQ1OTIxMC40NzA5NzEzMDYsIDI0NTkyMTEuNDcwOTcxMzA2LCAyNDU5MjEyLjQ3MDk3MTMwNiwgMjQ1OTIxMy40NzA5NzEzMDYsIDI0NTkyMTQuNDcwOTcxMzA2XX19fQ==",
        "attachment_name": "ampel_test.json",
    }

    status2, data2 = api(
        'PUT',
        f'comment/{data["data"]["comment_id"]}',
        data=payload,
        token=super_admin_token,
    )

    assert status2 == 200
    assert data2['status'] == 'success'

    status3, data3 = api(
        'GET', f'comment/{data["data"]["comment_id"]}', token=super_admin_token
    )
    assert status3 == 200
    assert data3["status"] == 'success'
    assert data3["data"]["attachment_bytes"] == payload['attachment_bytes']
    assert data3['data']['attachment_name'] == payload['attachment_name']


def test_problematic_post_comment_attachment_1275(
    super_admin_token, public_source, public_group
):

    status, data = api(
        'POST',
        'comment',
        data={
            'obj_id': public_source.id,
            'text': 'asdf',
            'group_ids': [public_group.id],
            "attachment": {
                'body': "eyJ0aW1lc3RhbXAiOiAiMjAyMC0xMS0wNFQxMjowMDowMyIsICJydW4iOiAxODM5LCAiZHVyYXRpb24iOiAwLjE0NiwgInJlc3VsdCI6IHsibW9kZWwiOiAic2FsdDIiLCAiZml0X2xjX3BhcmFtZXRlcnMiOiB7ImJvdW5kcyI6IHsiYyI6IFstMiwgNV0sICJ4MSI6IFstNSwgNV0sICJ6IjogWzAsIDAuMl19fSwgImZpdF9hY2NlcHRhYmxlIjogZmFsc2UsICJwbG90X2luZm8iOiAic2FsdDIgY2hpc3EgMjAuMjkgbmRvZiAxIG9rIGZpdCBGYWxzZSIsICJtb2RlbF9hbmFseXNpcyI6IHsiaGFzX3ByZW1heF9kYXRhIjogdHJ1ZSwgImhhc19wb3N0bWF4X2RhdGEiOiBmYWxzZSwgIngxX2luX3JhbmdlIjogdHJ1ZSwgIl94MV9yYW5nZSI6IFstNCwgNF0sICJjX29rIjogdHJ1ZSwgIl9jX3JhbmdlIjogWy0xLCAyXX0sICJmaXRfcmVzdWx0cyI6IHsieiI6IDAuMTE3NDM5NTYwNTE3MDEwNjUsICJ0MCI6IDI0NTkxNTguODE5NzYyNTE2MywgIngwIjogMC4wMDA2MDg1NTg3NzI2MjI5NDY3LCAieDEiOiAtMC44NzM1ODM5NTY4MTk5NjczLCAiYyI6IC0wLjA1OTg1NTgxMTY2MDA2MzE1LCAibXdlYnYiOiAwLjA5OTU2MTk1NjAzOTAzMTEyLCAibXdyX3YiOiAzLjEsICJ6LmVyciI6IDAuMDIxNTUyNTQwMzEyMzk1NDI0LCAidDAuZXJyIjogMC45NTczNDkzNTY0OTY3MDY2LCAieDAuZXJyIjogNi43NDYwMTY5NDY3ODk5NDllLTA1LCAieDEuZXJyIjogMC42NDc4NTA5NzU5ODY5OTY2LCAiYy5lcnIiOiAwLjEzNDQxMzAzNjM5NjQxMzU1fSwgInNuY29zbW9faW5mbyI6IHsic3VjY2VzcyI6IHRydWUsICJjaGlzcSI6IDIwLjI5NDAxNzkxMDExMjMxMywgIm5kb2YiOiAxLCAiY2hpc3Fkb2YiOiAyMC4yOTQwMTc5MTAxMTIzMTN9LCAiZmx1eF9kaWN0IjogeyJ6dGZnIjogWzAuMCwgLTAuMDQyNjA1ODU1NzUwNDczMzYsIC0wLjE1OTc2MzYxMjQ2NDMxOTQyLCAtMC41MDU5ODM5ODUzNTUyNDg1LCAtMC4xMDU5NzkwNDU0NzgyOTA4MywgMy44MjIzMDg5NDc0ODQ1NzEsIDEyLjE5Njc1NDg2NzEwMDE0NywgMjMuODgzNTQ0OTEzNTM0MTUsIDM4LjIyMzIzMjgyMDM3NzUyLCA1NS4wMTU0NjcyNzgyNzMwOCwgNzQuMzQyNTQxNDE2MzQ5MjIsIDk2LjMyNzQ1MzkzMzE2MDA5LCAxMjEuMjMwODU1MjE3MTg2ODMsIDE0OS42NzE5NzMzNDU4Mzg4NiwgMTc4LjU4NzEzMzY3MjU1MDI3LCAyMDUuMDcyMDU1NjU4Nzg4NDYsIDIyOC4wNTUzMTYwNjg0MjQsIDI0Ny4zNTIzMjM5ODA4Nzg1NywgMjYyLjYwOTI1MTk2MzQ1NzMsIDI3My45NjAxOTExOTE4NTEsIDI4Mi4wMTYzOTE3NTE3NzMsIDI4Ni4zNzI2Mjg3NjU4NjE2MywgMjg2LjY4ODcwMTAxODEzNDQ1LCAyODMuNTU0NTY3MTE3MzQ4MSwgMjc3LjY5MjY0NTUyNDYwODgsIDI2OS40ODM1NDU5ODQ2MTMzLCAyNTkuMTAxNDEyMTkxMjIwOCwgMjQ2Ljk2OTEyOTQ0OTc2NTE1LCAyMzMuODk5MTY4NzM2OTE5MjgsIDIyMC4xMzIyNzI0NjI2MDgzNCwgMjA1LjcxNjY4NzM5MzQxMzE0LCAxOTAuNTk3MTUyMDAzOTQzODUsIDE3NS41NTM4NDE0NDAyMjYyMiwgMTYxLjE2NTk5Mzk2NDQ1NDMyLCAxNDcuNTEwNTE3ODIyNjI0MTcsIDEzNC40NDYyMjA0NjIxODY5NCwgMTIxLjg5NDI1MDE3MDAxNDM5LCAxMDkuOTA0OTI2NzQzMDg2NzIsIDk4Ljg1ODU4MjA1NTk5MDE0LCA4OC44MjIyNDkyNDQ5ODgwNiwgNzkuODU1NDY1Nzk5NzkzOTMsIDcyLjA5NTcyMzMzMTQ2NzIsIDY1LjMwMjgyMzM5NDQzNzU3LCA1OS4yNTMxMjgyMDM2MzYzNDQsIDUzLjkyNjI2NjAzMjI5NDUyLCA0OS40MTk3OTAzMTc3NTMyOCwgNDUuNjc4NTQ4MjU5MDMwNjQsIDQyLjMxMjkyMDczNTM0MDk3LCAzOS4xMzUwNDI0OTI2NjEzMSwgMzYuMTc1NTQ2NTcyMTI5NywgMzMuNDI4OTg3OTU4MTgzNDUsIDMwLjkyODcxOTcyNjIzMzE4NywgMjguNzUyMjgxODYxNTg1NjQsIDI2LjkwMjQ3ODU5MDAzMDA5NiwgMjUuMzMzOTc4MzQ4MzEyMzYsIDI0LjAxMTA1NjIzOTM4MjkzNSwgMjIuOTAzODgyMjIyNjQwNTU0LCAyMS45ODU1MjExMDM5NjA1NTgsIDIxLjE4MzYxNTc5ODI1OTE3MiwgMjAuNDUyMjYzMDY5MTMwNDY3LCAxOS43ODQ2NDgxNDA4MjM3NTUsIDE5LjE3NTU1OTc1NTQwMzQyNywgMTguNjIwMzc0ODc2NTc1MjksIDE4LjExNTA4NTAxNDE3MjMxNSwgMTcuNjU2MjcwMzk5NzY4MzIsIDE3LjI0MDMyMDg1NjEyNTk5LCAxNi44NTkxMTMwMzUwMTQ1NzcsIDE2LjQ4NjE4ODc2Njc0MTY5OCwgMTYuMTE4OTQwODAyOTc3MDQ3LCAxNS43NTg0NzM3NDM2NDc4NjIsIDE1LjQwNTc0NTcwNDAwMTI0NiwgMTUuMDYxNzIzMzM0MjQ2MDQzLCAxNC43MjczODEwMjI5Nzk4MDQsIDE0LjQwMzY5NTMxNTY1OTUzLCAxNC4wOTE2Mzk5MTExNzczNTMsIDEzLjc5MjE4MTE0NDkwNTA1OCwgMTMuNTA2MjczODY5OTM1ODA3LCAxMy4yMzQ4Njg0ODM3Njc1MzksIDEyLjk4MTU3MzMxODc4OTYyN10sICJ6dGZyIjogWzAuMCwgMC4yMDkwMjkyNzU5Mzc3MzQ5LCAwLjc4ODc0NjQ5ODgxMDcwMzksIDEuNzIyNTcyMDQ5MDAyNDYxNCwgMy42OTI5MjkzMjcwMDQxNDMyLCA4Ljc5MDcxNTY1MDg1NDgwNSwgMTcuNjMyNDU0MDIxMTYyMzM1LCAyOS4yNTAwMTgzNTEwOTI2MTcsIDQzLjA2OTYyOTQwMjAzMDcxLCA1OC44MjcyMTA3OTA5ODU1NywgNzYuNDg2NjMwNDI0MzgxMzksIDk2LjE5OTQ4Mzk4ODEwOTcyLCAxMTguMjA0MzUzMTc5NjA4NSwgMTQzLjAwNzYzODUwNjUxMDY2LCAxNjguMzEyOTYwNzk1NjcyMDQsIDE5MS45NDMxNTA1MTU0NTUwNywgMjEzLjExMjQ5MjAxODQ1MDMsIDIzMS43MDU4NjcwOTQ1MjU0MiwgMjQ3LjQ3Nzg0MDIwMzIxNTYsIDI2MC41NjYzOTUwNzY4NzIzNywgMjcxLjQ3ODE4NDY2MTkwMjcsIDI3OS44ODk5NTU4MjU4NTQ1NCwgMjg1LjUzNjM3MjA2NjA5NTA1LCAyODguNTYwNDMyMzQ4MTA3ODQsIDI4OS4yMDkxODAzODM0NjU1LCAyODcuNjUwMjExNzU1NDQxNywgMjg0LjAxMjM5MTM1MDM1NTcsIDI3OC40MDEyNzQyOTkwNjQ1LCAyNzAuNzQ3ODQ1MjM1ODM2MTcsIDI2MS4yMDkzMzY3NjQxOTcyLCAyNDkuOTY1NDI1MjA5MDkzNjQsIDIzNi45OTYwODA4NDE3NDY1NiwgMjIzLjgyMjE4ODMwMjU3MjMsIDIxMS42MDIyMzAxOTM5NTMzMiwgMjAwLjU3Njg4NDg1MTY3NjUsIDE5MC41OTQ5NzcwNDMxMDUzMywgMTgxLjU4NjIyMjIwNDI1NTUzLCAxNzMuNDE4MDQxNzE4Nzc0NzMsIDE2NS43MzA3MDQ1NzY4OTE4NCwgMTU4LjQ4MjI5NTMyNDg2NTAyLCAxNTEuNjk5NTg5MDg1MzM3ODYsIDE0NS40NTE4MTQ5NDI5MDg2NywgMTM5LjU4NDA3NTMzMzM1MzIsIDEzMy45NTkxODY4MzI4Njg3NywgMTI4LjU3MzUxMzA2ODM0MDUsIDEyMy41MTE2ODQ3MzA1NTI0LCAxMTguNzIxNzkwNTIxMTI0MTMsIDExMy44MDQ0MDc3MTY2NDgyOSwgMTA4LjYwODM1NTg2NDcxNzEzLCAxMDMuMjQxMzg2NjgzMDIxNDUsIDk3Ljc2NTI0NjgyMjU0MDA4LCA5Mi4zMzM3MTQxNjc3MjA4MSwgODcuMTk3NDkyMjAyMTk5MDQsIDgyLjQyODMxMDQ2NDc4ODMyLCA3Ny45Nzc5MjUyNzYzNzA4OCwgNzMuODEwMDcxNTY1NjgzNjMsIDY5Ljg5MTk0NDMyNjg0OSwgNjYuMTk5MzM4MTkxNjMwNCwgNjIuODE0MDY4Mjk4NzQ1Njk2LCA1OS43NzUwOTExMzk3MjA2MywgNTcuMDUxMDcyNjc2ODk3MTUsIDU0LjYxNDMxOTc2NDU2NTM0NCwgNTIuNDQxMzM3NjgzNjU1NjYsIDUwLjUxMTUyNzYyMjUyMDkyLCA0OC44MDY4ODUwNDEwMjEyMiwgNDcuMzA5MjE5ODg4NjkxNjE1LCA0NS45ODU1MTU2NDIxNDYxNywgNDQuNzQxNDAwNjkzNDQ3MDQsIDQzLjU2MjcwOTkyODYwOTE2NiwgNDIuNDQ3OTkwOTkzNDI2OTksIDQxLjM5NTQ1MDExNjg4MzUsIDQwLjQwMzQzMDc2MDk2MTY4LCAzOS40NzA0MDYxMjgyMjcyNCwgMzguNTk0OTYwNzIwNjY3NCwgMzcuNzc1Nzc3NzI1ODY5OTQsIDM3LjAxMTYzMDk2NDg1NDUyNSwgMzYuMzAxMzgwMzgzNDY1NjU2LCAzNS42NDM5NTk0MzY0NjcxNSwgMzUuMDQzODYwODA3MzQ5ODk0XSwgIm9ic2pkIjogWzI0NTkxMzYuNDcwOTcxMzA2LCAyNDU5MTM3LjQ3MDk3MTMwNiwgMjQ1OTEzOC40NzA5NzEzMDYsIDI0NTkxMzkuNDcwOTcxMzA2LCAyNDU5MTQwLjQ3MDk3MTMwNiwgMjQ1OTE0MS40NzA5NzEzMDYsIDI0NTkxNDIuNDcwOTcxMzA2LCAyNDU5MTQzLjQ3MDk3MTMwNiwgMjQ1OTE0NC40NzA5NzEzMDYsIDI0NTkxNDUuNDcwOTcxMzA2LCAyNDU5MTQ2LjQ3MDk3MTMwNiwgMjQ1OTE0Ny40NzA5NzEzMDYsIDI0NTkxNDguNDcwOTcxMzA2LCAyNDU5MTQ5LjQ3MDk3MTMwNiwgMjQ1OTE1MC40NzA5NzEzMDYsIDI0NTkxNTEuNDcwOTcxMzA2LCAyNDU5MTUyLjQ3MDk3MTMwNiwgMjQ1OTE1My40NzA5NzEzMDYsIDI0NTkxNTQuNDcwOTcxMzA2LCAyNDU5MTU1LjQ3MDk3MTMwNiwgMjQ1OTE1Ni40NzA5NzEzMDYsIDI0NTkxNTcuNDcwOTcxMzA2LCAyNDU5MTU4LjQ3MDk3MTMwNiwgMjQ1OTE1OS40NzA5NzEzMDYsIDI0NTkxNjAuNDcwOTcxMzA2LCAyNDU5MTYxLjQ3MDk3MTMwNiwgMjQ1OTE2Mi40NzA5NzEzMDYsIDI0NTkxNjMuNDcwOTcxMzA2LCAyNDU5MTY0LjQ3MDk3MTMwNiwgMjQ1OTE2NS40NzA5NzEzMDYsIDI0NTkxNjYuNDcwOTcxMzA2LCAyNDU5MTY3LjQ3MDk3MTMwNiwgMjQ1OTE2OC40NzA5NzEzMDYsIDI0NTkxNjkuNDcwOTcxMzA2LCAyNDU5MTcwLjQ3MDk3MTMwNiwgMjQ1OTE3MS40NzA5NzEzMDYsIDI0NTkxNzIuNDcwOTcxMzA2LCAyNDU5MTczLjQ3MDk3MTMwNiwgMjQ1OTE3NC40NzA5NzEzMDYsIDI0NTkxNzUuNDcwOTcxMzA2LCAyNDU5MTc2LjQ3MDk3MTMwNiwgMjQ1OTE3Ny40NzA5NzEzMDYsIDI0NTkxNzguNDcwOTcxMzA2LCAyNDU5MTc5LjQ3MDk3MTMwNiwgMjQ1OTE4MC40NzA5NzEzMDYsIDI0NTkxODEuNDcwOTcxMzA2LCAyNDU5MTgyLjQ3MDk3MTMwNiwgMjQ1OTE4My40NzA5NzEzMDYsIDI0NTkxODQuNDcwOTcxMzA2LCAyNDU5MTg1LjQ3MDk3MTMwNiwgMjQ1OTE4Ni40NzA5NzEzMDYsIDI0NTkxODcuNDcwOTcxMzA2LCAyNDU5MTg4LjQ3MDk3MTMwNiwgMjQ1OTE4OS40NzA5NzEzMDYsIDI0NTkxOTAuNDcwOTcxMzA2LCAyNDU5MTkxLjQ3MDk3MTMwNiwgMjQ1OTE5Mi40NzA5NzEzMDYsIDI0NTkxOTMuNDcwOTcxMzA2LCAyNDU5MTk0LjQ3MDk3MTMwNiwgMjQ1OTE5NS40NzA5NzEzMDYsIDI0NTkxOTYuNDcwOTcxMzA2LCAyNDU5MTk3LjQ3MDk3MTMwNiwgMjQ1OTE5OC40NzA5NzEzMDYsIDI0NTkxOTkuNDcwOTcxMzA2LCAyNDU5MjAwLjQ3MDk3MTMwNiwgMjQ1OTIwMS40NzA5NzEzMDYsIDI0NTkyMDIuNDcwOTcxMzA2LCAyNDU5MjAzLjQ3MDk3MTMwNiwgMjQ1OTIwNC40NzA5NzEzMDYsIDI0NTkyMDUuNDcwOTcxMzA2LCAyNDU5MjA2LjQ3MDk3MTMwNiwgMjQ1OTIwNy40NzA5NzEzMDYsIDI0NTkyMDguNDcwOTcxMzA2LCAyNDU5MjA5LjQ3MDk3MTMwNiwgMjQ1OTIxMC40NzA5NzEzMDYsIDI0NTkyMTEuNDcwOTcxMzA2LCAyNDU5MjEyLjQ3MDk3MTMwNiwgMjQ1OTIxMy40NzA5NzEzMDYsIDI0NTkyMTQuNDcwOTcxMzA2XX19fQ==",
                'name': "ampel_test.json",
            },
        },
        token=super_admin_token,
    )
    assert status == 200
    assert data['status'] == 'success'
