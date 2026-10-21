require 'liquid'

module Jekyll
  module CitationMemberFilters
    # Read both current multi-member records and older generated citations.
    def citation_orcids(citation)
      return [] if citation.nil?
      (Array(citation['orcids']) + Array(citation['orcid']))
        .compact.map { |value| value.to_s.strip.upcase }
        .reject(&:empty?).uniq
    end

    def citations_for_orcid(citations, orcid)
      orcid = orcid.to_s.strip.upcase
      return [] if orcid.empty?
      Array(citations).select { |citation| citation_orcids(citation).include?(orcid) }
    end
  end
end

Liquid::Template.register_filter(Jekyll::CitationMemberFilters)
