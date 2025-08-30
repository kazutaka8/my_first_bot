import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# テスト対象のモジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import find_prefecture, get_news_for_prefecture

class TestPrefectureBot(unittest.TestCase):
    
    def test_find_prefecture_exact_match(self):
        """正確な都道府県名のマッチングテスト"""
        self.assertEqual(find_prefecture("東京都"), "東京都")
        self.assertEqual(find_prefecture("大阪府"), "大阪府")
        self.assertEqual(find_prefecture("北海道"), "北海道")
        
    def test_find_prefecture_partial_match(self):
        """部分一致のテスト"""
        self.assertEqual(find_prefecture("東京都のニュース"), "東京都")
        self.assertEqual(find_prefecture("大阪府について"), "大阪府")
        self.assertEqual(find_prefecture("今日の北海道"), "北海道")
        
    def test_find_prefecture_no_match(self):
        """都道府県名がない場合のテスト"""
        self.assertIsNone(find_prefecture("こんにちは"))
        self.assertIsNone(find_prefecture("天気はどうですか"))
        self.assertIsNone(find_prefecture("123"))
        
    def test_find_prefecture_multiple_match(self):
        """複数の都道府県名がある場合（最初のものを返す）"""
        result = find_prefecture("東京都から大阪府")
        self.assertIn(result, ["東京都", "大阪府"])
        
    @patch.dict(os.environ, {}, clear=True)
    def test_get_news_no_api_key(self):
        """APIキーがない場合のテスト"""
        result = get_news_for_prefecture("東京都")
        self.assertEqual(result, "ニュースAPI設定が見つかりません。")
        
    @patch.dict(os.environ, {"NEWS_API_KEY": "test_key"})
    @patch('app.requests.get')
    def test_get_news_success(self, mock_get):
        """ニュース取得成功のテスト"""
        # モックレスポンスを設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "東京都のニュース1",
                    "url": "https://example.com/news1"
                },
                {
                    "title": "東京都のニュース2", 
                    "url": "https://example.com/news2"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = get_news_for_prefecture("東京都")
        
        # APIが正しく呼ばれているかチェック
        mock_get.assert_called_once()
        
        # レスポンスの内容をチェック
        self.assertIn("東京都の最新ニュース", result)
        self.assertIn("東京都のニュース1", result)
        self.assertIn("https://example.com/news1", result)
        
    @patch.dict(os.environ, {"NEWS_API_KEY": "test_key"})
    @patch('app.requests.get')
    def test_get_news_no_articles(self, mock_get):
        """ニュースが見つからない場合のテスト"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"articles": []}
        mock_get.return_value = mock_response
        
        result = get_news_for_prefecture("東京都")
        self.assertEqual(result, "東京都に関するニュースが見つかりませんでした。")
        
    @patch.dict(os.environ, {"NEWS_API_KEY": "test_key"})
    @patch('app.requests.get')
    def test_get_news_api_error(self, mock_get):
        """API呼び出しエラーのテスト"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response
        
        result = get_news_for_prefecture("東京都")
        self.assertEqual(result, "ニュースの取得に失敗しました。")
        
    @patch.dict(os.environ, {"NEWS_API_KEY": "test_key"})
    @patch('app.requests.get')
    def test_get_news_exception(self, mock_get):
        """例外発生のテスト"""
        mock_get.side_effect = Exception("Network error")
        
        result = get_news_for_prefecture("東京都")
        self.assertIn("エラーが発生しました", result)
        self.assertIn("Network error", result)

if __name__ == "__main__":
    unittest.main()