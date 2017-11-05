import unittest
import config
import WPTDownloader
import os


class TestDownloadDef(unittest.TestCase):

    def test_stress(self):
        urls = []

        for x in range(0, 100):
            urls.append(r'http://barbarella.deadendthrills.com/imagestore/DET3/streetfighterv/large/kenishment.png')

        WPTDownloader.download(urls)

    def test_image_exists(self):
        urls = [r'http://barbarella.deadendthrills.com/imagestore/DET3/streetfighterv/large/kenishment.png']

        WPTDownloader.create_directory()
        WPTDownloader.download(urls)

        unittest.assertTrue(os.path.isfile(config.download_location + r'/IMG1.png'))


if __name__ == '__main__':
    unittest.main()
