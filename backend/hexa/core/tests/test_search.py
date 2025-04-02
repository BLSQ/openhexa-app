from hexa.core.search_utils import Token, TokenType, tokenize
from hexa.core.test import TestCase


class TokenizeTest(TestCase):
    def test_tokenize(self):
        self.assertEqual(
            tokenize("bonjour le  monde"),
            [
                Token(value="bonjour", type=TokenType.WORD),
                Token(value="le", type=TokenType.WORD),
                Token(value="monde", type=TokenType.WORD),
            ],
        )
        self.assertEqual(
            tokenize('bonjour "le  monde"'),
            [
                Token(value="bonjour", type=TokenType.WORD),
                Token(value="le  monde", type=TokenType.EXACT_WORD),
            ],
        )
        self.assertEqual(
            tokenize('  bonj"our le"   monde  '),
            [
                Token(value="bonj", type=TokenType.WORD),
                Token(value="our le", type=TokenType.EXACT_WORD),
                Token(value="monde", type=TokenType.WORD),
            ],
        )
        self.assertEqual(
            tokenize(' type:s3_object keyword "exact search a"  ', ["type"]),
            [
                Token(value="type:s3_object", type=TokenType.FILTER),
                Token(value="keyword", type=TokenType.WORD),
                Token(value="exact search a", type=TokenType.EXACT_WORD),
            ],
        )
        self.assertEqual(
            tokenize(' foo:bar keyword "exact search a"  '),
            [
                Token(value="foo:bar", type=TokenType.WORD),
                Token(value="keyword", type=TokenType.WORD),
                Token(value="exact search a", type=TokenType.EXACT_WORD),
            ],
        )
