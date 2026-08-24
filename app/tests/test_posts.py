from .. import oauth2, schemas


def test_get_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts/")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == len(test_posts)
    for post in posts:
        schemas.PostResponse(**post)


def test_get_posts_unauthenticated(client, test_posts):
    response = client.get("/posts/")
    assert response.status_code == 401


def test_get_one_post(authorized_client, test_posts):
    post = test_posts[0]
    response = authorized_client.get(f"/posts/{post.post_id}")
    assert response.status_code == 200
    fetched_post = schemas.PostResponse(**response.json())
    assert fetched_post.post_id == post.post_id
    assert fetched_post.title == post.title


def test_get_one_post_not_found(authorized_client):
    response = authorized_client.get("/posts/88888")
    assert response.status_code == 404


def test_create_post(authorized_client, test_user):
    response = authorized_client.post(
        "/posts/", json={"title": "new title", "content": "new content"}
    )
    assert response.status_code == 201
    new_post = schemas.PostResponse(**response.json())
    assert new_post.title == "new title"
    assert new_post.content == "new content"
    assert new_post.user.user_id == test_user["user_id"]
    assert new_post.votes == 0


def test_create_post_unauthenticated(client):
    response = client.post("/posts/", json={"title": "new title", "content": "new content"})
    assert response.status_code == 401


def test_delete_post(authorized_client, test_posts):
    post = test_posts[0]
    response = authorized_client.delete(f"/posts/{post.post_id}")
    assert response.status_code == 204
    assert authorized_client.get(f"/posts/{post.post_id}").status_code == 404


def test_delete_post_not_found(authorized_client):
    response = authorized_client.delete("/posts/88888")
    assert response.status_code == 404


def test_delete_other_users_post(client, test_posts, test_user2):
    token = oauth2.create_access_token({"sub": test_user2["email"]})
    response = client.delete(
        f"/posts/{test_posts[0].post_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_update_post(authorized_client, test_posts):
    post = test_posts[0]
    response = authorized_client.put(
        f"/posts/{post.post_id}",
        json={"title": "updated title", "content": "updated content"},
    )
    assert response.status_code == 200
    updated_post = schemas.PostResponse(**response.json())
    assert updated_post.title == "updated title"
    assert updated_post.content == "updated content"


def test_update_post_not_found(authorized_client):
    response = authorized_client.put(
        "/posts/88888", json={"title": "updated title", "content": "updated content"}
    )
    assert response.status_code == 404


def test_update_other_users_post(client, test_posts, test_user2):
    token = oauth2.create_access_token({"sub": test_user2["email"]})
    response = client.put(
        f"/posts/{test_posts[0].post_id}",
        json={"title": "updated title", "content": "updated content"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
