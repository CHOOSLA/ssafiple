import unittest
from fastapi.testclient import TestClient
from app.main import app


class PostImageUploadTests(unittest.TestCase):
    def test_upload_image_returns_public_url(self):
        client = TestClient(app)
        response = client.post(
            "/posts/upload-image",
            files={"file": ("sample.png", b"fake-image-bytes", "image/png")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("image_url", response.json())
        self.assertTrue(response.json()["image_url"].startswith("/uploads/"))


if __name__ == "__main__":
    unittest.main()
