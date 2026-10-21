import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from citation_members import citation_orcids, merge_sources, has_verified_metadata


class CitationMemberTests(unittest.TestCase):
    def test_only_complete_verified_metadata_skips_network(self):
        source = dict(title="Title", publisher="Journal", date="2026-10-18",
                      link="https://doi.org/10.1234/test", authors=["Chuxiong Hu"],
                      metadata_verified=True, verification={"sources": ["https://api.crossref.org/works/10.1234/test"]})
        self.assertTrue(has_verified_metadata(source))
        for key in ["authors", "title", "date", "publisher", "link", "metadata_verified", "verification"]:
            incomplete = dict(source)
            del incomplete[key]
            self.assertFalse(has_verified_metadata(incomplete), key)

    def test_shared_paper_keeps_both_members_and_manual_metadata(self):
        sources = [
            {"id": "doi:10.1234/ABC", "orcid": "0000-0002-1825-0097", "title": "API title"},
            {"id": "doi:10.1234/abc", "orcids": ["0000-0001-5121-2677"]},
            {"id": "doi:10.1234/ABC", "title": "Manual title", "image": "manual.jpg"},
        ]
        papers = merge_sources(sources)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]["orcids"], ["0000-0002-1825-0097", "0000-0001-5121-2677"])
        self.assertEqual(papers[0]["title"], "Manual title")
        self.assertEqual(papers[0]["image"], "manual.jpg")
        self.assertNotIn("orcids", sources[0])

    def test_no_identifier_papers_are_not_merged(self):
        self.assertEqual(len(merge_sources([{"title": "One"}, {"title": "Two"}])), 2)

    def test_membership_is_exact_and_deduplicated(self):
        self.assertEqual(citation_orcids({"orcids": [" id-x ", "ID-X", "ID-Y"], "orcid": "id-y"}),
                         ["ID-X", "ID-Y"])
        self.assertEqual(citation_orcids({}), [])

    def test_manual_entry_can_associate_a_member(self):
        papers = merge_sources([{"id": "doi:10.1234/abc", "orcids": ["0000-0001-5121-2677"]}])
        self.assertEqual(papers[0]["orcids"], ["0000-0001-5121-2677"])


if __name__ == "__main__":
    unittest.main()
