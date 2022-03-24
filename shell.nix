with import <nixpkgs> {};
ruby.withPackages (ps: with ps; [ github-pages jekyll jekyll-gist jekyll-sitemap jekyll-seo-tag ])
