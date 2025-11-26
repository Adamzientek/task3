import unittest
from project.books.models import Book
from project.books.views import create_book
from project import db, app

class Tests(unittest.TestCase):
    """
    name = db.Column(db.String(64), unique=True, index=True)
    author = db.Column(db.String(64))
    year_published = db.Column(db.Integer)
    book_type = db.Column(db.String(20))
    status = db.Column(db.String(20), default='available')"""

    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    correct_values = [
        {"name": "It", "author": "Stephen King", "year_published": 1989, "book_type": "horror"},
        {"name": "Wuthering Heights", "author": "Emily Bronte", "year_published": 1890, "book_type": "romance"},
        {"name": "Lord of The Rings", "author": "J.R.R. Tolkien", "year_published": 1940, "book_type": "fantasy"},
        {"name": "Lincoln", "author": "Emil Ludvig", "year_published": 2008, "book_type": "biography"},
        {"name": "Why Nations Fail", "author": "Daron Acemoglu, James Robinson", "year_published": 2018, "book_type": "economics"}
    ]

    wrong_values = [
        {"name": None, "author": "Stephen King", "year_published": 1989, "book_type": "horror"},
        {"name": "Wuthering Heights", "author": "A"*600, "year_published": 1890, "book_type": "romance"},
        {"name": "Lord of The Rings", "author": "J.R.R. Tolkien", "year_published": 999988888888888888777666666666677777777555551940, "book_type": "fantasy"},
        {"name": "Lincoln", "author": "Emil Ludvig", "year_published": 2008, "book_type": 24},
        {"name": "Why Nations Fail", "author": "None", "year_published": "mighty", "book_type": "economics"},
    ]

    attack_values = [
        {"name": "' or '1'=='1", "author": "<script>alert(1)</script>", "year_published": "javascript:alert(1)", "book_type": "union join"},
        {"name": "''", "author": "<img src=1 onerror=alert(2)/>", "year_published": ";#", "book_type": ";--"},
        {"name": "' or '1'=='2';--", "author": "<script>alert(document.cookie)</script>", "year_published": -12, "book_type": "'"},
    ]

    extreme_values_good = [
        {"name": "A"*64, "author": "Jim Jay", "year_published": 1234, "book_type": "weird"},
        {"name": "John", "author": "B"*64, "year_published": 444, "book_type": "super specifiv"},
        {"name": "Galinda", "author": "Munchkin", "year_published":  9223372036854775807, "book_type": "123"},
        {"name": "Car Repairs", "author": "Jacky K", "year_published": 1984, "book_type": "C"*20},
    ]

    extreme_values_bad = [
        {"name": "A" * 65, "author": "Jimy", "year_published": 1234, "book_type": "weird"},
        {"name": "John", "author": "B" * 65, "year_published": 444, "book_type": "super specifiv"},
        {"name": "", "author": "", "year_published": 922337203685477580790, "book_type": "123"},
        {"name": "", "author": "", "year_published": "", "book_type": "C" * 21},
    ]

    def test_correct(self):
        for book_info in self.correct_values:
            test_book = Book(**book_info)
            db.session.add(test_book)
            db.session.commit()
            search_test_book = Book.query.filter_by(name=book_info["name"]).first()
            self.assertEqual(search_test_book.name, book_info["name"])
            self.assertEqual(search_test_book.author, book_info["author"])
            self.assertEqual(search_test_book.year_published, book_info["year_published"])
            self.assertEqual(search_test_book.book_type, book_info["book_type"])
            self.assertEqual(search_test_book.status, "available")

    def test_incorrect(self):
        for book_info in self.wrong_values:
            test_book = Book(**book_info)
            db.session.add(test_book)
            with self.assertRaises(Exception):
                db.session.commit()

    def test_attack1(self):
        test_book = Book("Wicked", "<script>alert(1)</script>", "javascript:alert(1)","' union join")
        db.session.add(test_book)
        db.session.commit()
        search_test_book = Book.query.filter_by(name="Wicked").first()
        self.assertNotIn("<script>", search_test_book.author)
        self.assertNotIn(":alert", search_test_book.year_published)
        self.assertNotIn("'", search_test_book.book_type)

    def test_attack2(self):
        test_book = Book("' or '1'==", "James Joyce", "javascript:alert(1)","' union join")
        db.session.add(test_book)
        db.session.commit()
        search_test_book = Book.query.filter_by(author="James Joyce").first()
        self.assertNotIn("' or '1'==", search_test_book.name)
        self.assertNotIn(":alert", search_test_book.year_published)
        self.assertNotIn("'", search_test_book.book_type)

    def test_extreme_allowed(self):
        for book_info in self.extreme_values_good:
            test_book = Book(**book_info)
            db.session.add(test_book)
            db.session.commit()
            search_test_book = Book.query.filter_by(name=book_info["name"]).first()
            self.assertEqual(search_test_book.name, book_info["name"])
            self.assertEqual(search_test_book.author, book_info["author"])
            self.assertEqual(search_test_book.year_published, book_info["year_published"])
            self.assertEqual(search_test_book.book_type, book_info["book_type"])
            self.assertEqual(search_test_book.status, "available")

    def test_extreme_not_allowed(self):
        for book_info in self.extreme_values_bad:
            test_book = Book(**book_info)
            db.session.add(test_book)
            with self.assertRaises(Exception):
                db.session.commit()

if __name__ == "__main__":
    unittest.main()