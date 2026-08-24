def test_vote_on_post(authorized_client, test_posts):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[0].post_id, "dir": 1})
    assert response.status_code == 201


def test_vote_twice_conflict(authorized_client, test_posts):
    authorized_client.post("/vote/", json={"post_id": test_posts[0].post_id, "dir": 1})
    response = authorized_client.post("/vote/", json={"post_id": test_posts[0].post_id, "dir": 1})
    assert response.status_code == 409


def test_delete_vote(authorized_client, test_posts):
    authorized_client.post("/vote/", json={"post_id": test_posts[0].post_id, "dir": 1})
    response = authorized_client.post("/vote/", json={"post_id": test_posts[0].post_id, "dir": 0})
    assert response.status_code == 201


def test_delete_vote_not_found(authorized_client, test_posts):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[0].post_id, "dir": 0})
    assert response.status_code == 404


def test_vote_post_not_found(authorized_client):
    response = authorized_client.post("/vote/", json={"post_id": 88888, "dir": 1})
    assert response.status_code == 404


def test_vote_unauthenticated(client, test_posts):
    response = client.post("/vote/", json={"post_id": test_posts[0].post_id, "dir": 1})
    assert response.status_code == 401
