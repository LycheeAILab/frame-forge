import unittest
from unittest.mock import patch
import tempfile
from pathlib import Path
import lab_auth
import lab_image

class ClientTests(unittest.TestCase):
    def test_token_file_and_no_disclosure(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(lab_auth,'token_path',return_value=Path(folder)/'token.json'):
            lab_auth.save_token('lych_live_test')
            self.assertEqual(lab_auth.load_token(),'lych_live_test')
            with patch.object(lab_auth,'validate_token',return_value=True):
                self.assertEqual(lab_auth.authorized_token(),'lych_live_test')
            with patch.object(lab_auth,'validate_token',return_value=False):
                self.assertRaises(lab_auth.AuthError,lab_auth.authorized_token)
    def test_multipart_contains_real_file(self):
        body,kind=lab_image.multipart({'prompt':'测试'},b'image-bytes')
        self.assertIn(b'image-bytes',body)
        self.assertIn(b'name="image"',body)
        self.assertIn('boundary=',kind)
    def test_download_rejects_untrusted_or_local_target(self):
        for url in ['http://localhost/a','https://evil.example/a','file:///a']:
            self.assertRaises(ValueError,lab_image.download,url,Path('unused'))
    def test_state_survives_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'state.json';state={'requestId':'same','jobId':'job'}
            lab_image.write_state(file,state)
            import json
            self.assertEqual(json.loads(file.read_text()),state)

if __name__=='__main__':unittest.main()
