from django import test

from hexa.core.string import (
    Token,
    TokenType,
    generate_filename,
    remove_whitespace,
    tokenize,
)


class StringTest(test.TestCase):
    def test_remove_whitespace(self):
        self.assertEqual("", remove_whitespace("\t \n \r \t"))

    def test_generate_filename(self):
        self.assertEqual("test_file.csv", generate_filename("TeST __  - file.csv"))


class TokenizeTest(test.TestCase):
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
            tokenize(' type:s3_object keyword "exact search a"  '),
            [
                Token(value="type:s3_object", type=TokenType.FILTER),
                Token(value="keyword", type=TokenType.WORD),
                Token(value="exact search a", type=TokenType.EXACT_WORD),
            ],
        )
