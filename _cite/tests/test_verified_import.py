import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from import_verified_library import author_name, publication_date, from_crossref


class VerifiedImportTests(unittest.TestCase):
    def test_real_repeated_name_is_not_a_duplicate_full_name(self):
        self.assertEqual(author_name({'given': 'Lu', 'family': 'Lu'}), 'Lu Lu')
        self.assertEqual(author_name({'given': 'Na', 'family': 'Na'}), 'Na Na')
        self.assertEqual(author_name({'given': 'Chuxiong Hu', 'family': 'Chuxiong Hu'}), 'Chuxiong Hu')
        self.assertEqual(author_name({'family': 'and Chuxiong Hu'}), 'Chuxiong Hu')

    def test_online_date_precedes_future_print_issue(self):
        message = {'published': {'date-parts': [[2026, 9, 2]]},
                   'published-print': {'date-parts': [[2027]]}}
        self.assertEqual(publication_date(message), ('2026-09-02', 'day', 'published'))
        self.assertEqual(publication_date({'issued': {'date-parts': [[2016]]}}),
                         ('2016-01-01', 'year', 'issued'))

    def test_journal_named_proceedings_is_not_a_conference(self):
        message = dict(DOI='10.1234/TEST', title=['A title'], type='journal-article',
                       author=[{'given': 'Chuxiong', 'family': 'Hu'}],
                       publisher='SAGE', **{'container-title': ['Proceedings of the Institution of Mechanical Engineers'],
                                            'issued': {'date-parts': [[2014]]}})
        self.assertEqual(from_crossref(message, {}, '2026-10-18')['publication_type'], 'journal')
        message['type'] = 'book-chapter'
        self.assertEqual(from_crossref(message, {}, '2026-10-18')['publication_type'], 'conference')


if __name__ == '__main__':
    unittest.main()
