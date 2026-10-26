require 'jekyll'

module LabI18n
  def self.zh?(locale)
    locale.to_s.start_with?('zh')
  end

  module Filters
    def t(key, locale = 'en')
      dictionaries = @context.registers[:site].data['i18n'] || {}
      keys = key.to_s.split('.')
      primary = keys.reduce(dictionaries[LabI18n.zh?(locale) ? 'zh' : 'en']) { |value, part| value.is_a?(Hash) ? value[part] : nil }
      fallback = keys.reduce(dictionaries['en']) { |value, part| value.is_a?(Hash) ? value[part] : nil }
      primary || fallback || key
    end

    def localized_field(object, field, locale = 'en')
      return nil unless object.respond_to?(:[])
      translated = object["#{field}_zh"] if LabI18n.zh?(locale)
      translated.nil? || translated.to_s.empty? ? object[field] : translated
    end

    # Translate page links only. Images, scripts, email, and external URLs stay shared.
    def localized_url(value, locale = 'en')
      value = value.to_s
      return value if value.empty? || value.match?(%r{\A(?:[a-z][a-z0-9+.-]*:|//|#)}i)
      path, suffix = value.split(/(?=[?#])/, 2)
      path = "/#{path}" unless path.start_with?('/')
      routes = @context.registers[:site].data['language_routes'] || {}
      english = routes.key(path) || path
      english = "#{english}/" if !routes.key?(english) && routes.key?("#{english}/")
      target = LabI18n.zh?(locale) ? (routes[english] || path) : english
      "#{target}#{suffix}"
    end

    def localized_tag(value, locale = 'en')
      translations = @context.registers[:site].data.dig('i18n', 'zh', 'tags') || {}
      LabI18n.zh?(locale) ? (translations[value.to_s] || value) : value
    end

    def localized_button_text(value, locale = 'en')
      translations = @context.registers[:site].data.dig('i18n', 'zh', 'button_labels') || {}
      LabI18n.zh?(locale) ? (translations[value.to_s] || value) : value
    end
  end

  class Generator < Jekyll::Generator
    safe true
    priority :low

    def generate(site)
      english_pages = site.pages.select do |page|
        !page.url.start_with?('/zh/') && page.output_ext == '.html'
      end
      chinese_pages = site.pages.select { |page| page.url.start_with?('/zh/') }
      chinese_by_url = chinese_pages.to_h { |page| [page.url, page] }
      routes = {}

      english_pages.each do |page|
        target = "/zh#{page.url}"
        chinese = chinese_by_url[target] || translated_page(site, page, target)
        pair(page, chinese, routes)
      end

      (site.collections['members'].docs + site.posts.docs).each do |document|
        target = "/zh#{document.url}"
        chinese = translated_page(site, document, target)
        # Page navigation needs the original post references, with translated links.
        if document.collection.label == 'posts'
          chinese.data['previous'] = document.previous_doc
          chinese.data['next'] = document.next_doc
        end
        if document.collection.label == 'members'
          document.data['profile_name'] = document.data['name']
          chinese.data['profile_name'] = document.data['name_zh'] || document.data['name']
        end
        pair(document, chinese, routes)
      end
      site.data['language_routes'] = routes
    end

    private

    def translated_page(site, original, target)
      path = target.sub(%r{\A/}, '')
      directory = File.dirname(path)
      filename = File.basename(path).sub(/\.html\z/, '')
      filename = 'index' if filename.empty?
      page = Jekyll::PageWithoutAFile.new(site, site.source, directory, "#{filename}.md")
      page.data = Jekyll::Utils.deep_merge_hashes({}, original.data)
      page.data['permalink'] = target
      page.data['slug'] = original.data['slug'] || (original.respond_to?(:basename_without_ext) ? original.basename_without_ext : nil)
      %w[name title description affiliation].each do |field|
        value = original.data["#{field}_zh"]
        page.data[field] = value unless value.nil? || value.to_s.empty?
      end
      translated = original.data['content_zh']
      page.content = translated.nil? || translated.to_s.strip.empty? ? original.content : translated
      page.data['translation_fallback'] = translated.nil? || translated.to_s.strip.empty?
      page.data['date'] = original.date if original.respond_to?(:date)
      site.pages << page
      page
    end

    def pair(english, chinese, routes)
      routes[english.url] = chinese.url
      [[english, 'en', 'en'], [chinese, 'zh', 'zh-CN']].each do |page, locale, lang|
        page.data['locale'] = locale
        page.data['lang'] = lang
        page.data['english_url'] = english.url
        page.data['chinese_url'] = chinese.url
      end
    end
  end
end

Liquid::Template.register_filter(LabI18n::Filters)
