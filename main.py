import re, html, feedparser, resend, os
from config import subscribers, domains, resend_key, num_emails

class ArxivDigest:
    def __init__(self, feed_urls, resend_key, subs, num_emails):
        self.feed_urls = feed_urls
        self.resend_key = resend_key
        self.resend = resend
        self.resend.api_key = self.resend_key
        self.subs = subs
        self.num_emails = num_emails
        self.css = """
            body {
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #333;
                background-color: #f8f8f8;
                padding: 20px;
            }
            .paper {
                padding: 20px;
                margin-bottom: 20px;
            }
            .title {
                font-size: 22px;
                color: #b31b1b; /* Cornell Red */
                margin-bottom: 5px;
            }
            .title a {
                text-decoration: none;
                color: inherit;
            }
            .title a:hover {
                color: #7f1111; /* Darker Cornell Red */
            }
            .authors {
                font-size: 16px;
                color: #6c757d;
                margin-bottom: 10px;
            }
            .abstract {
                font-size: 16px;
                color: #333;
                text-align: justify;
            }
            ol {
                padding-left: 20px;
                margin-bottom: 20px;
            }

            li {
                margin-bottom: 10px;
            }

            li a {
                text-decoration: none;
                color: #333;
            }

            li a:hover {
                color: #b31b1b; /* Cornell Red */
            }
        """


    def _extract_authors(self, authors_html):
        author_regex = re.compile('<a href=".*?">(.*?)</a>')
        authors = set(html.unescape(match.group(1)) for match in author_regex.finditer(authors_html))
        return authors

    def extract_paper_info(self, entry):
        title = entry.title.split('. (arXiv')[0]
        link = entry.link
        abstract = entry.summary
        authors = self._extract_authors(entry.authors[0]['name'])

        return {
            "title": title,
            "link": link,
            "abstract": abstract,
            "authors": authors
        }

    def extract_feed_info(self, feed):
        date = feed.feed.updated.split('T')[0]
        paper_info = [self.extract_paper_info(entry) for entry in feed.entries]
        return {
            "date": date,
            "paper_info": paper_info
        }

    def render_html(self, data, part):
        html_str = f"""
        <html>
            <head>
                <style>
                    {self.css}
                </style>
            </head>
            <body>
                <a name="toc"></a>
                <h1>Arxiv Papers for {data['date']} - Part {part}</h1>
                {self.render_toc(data['paper_info'])}
        """

        for i, paper in enumerate(data['paper_info'], 1):
            html_str += f"""
            <a name="paper{i}"></a>
            <div class="paper">
                <div class="title">
                    <a href="{paper['link']}">{paper['title']}</a>
                    <a href="#toc" style="font-size:0.8em; text-decoration: none; color: #333; margin-left: 10px;">[Back to TOC]</a>
                </div>
                <div class="authors">Authors: {', '.join(paper['authors'])}</div>
                <div class="abstract">{paper['abstract']}</div>
            </div>
            """
            
        html_str += "</body></html>"
        return html_str

    def render_toc(self, paper_info):
        toc_html = '<div class="toc" style="margin-bottom:20px;"><h2 style="font-size:1.5em; margin-bottom:10px;">Table of Contents</h2><ul style="list-style-type: none;">'
        for i, paper in enumerate(paper_info, 1):
            toc_html += f'<li style="margin-bottom:5px;"><a href="#paper{i}" style="font-size:0.9em; color: #b31b1b;">{paper["title"]}</a></li>'
        toc_html += '</ul></div>'
        return toc_html


    def send_emails(self):
        feed_data_list = []
        for feed_url in self.feed_urls:
            feed = feedparser.parse(feed_url)
            feed_data = self.extract_feed_info(feed)
            feed_data_list.append(feed_data)

        # avoid sending duplicate papers
        paper_dict = {}
        for paper in [paper for data in feed_data_list for paper in data['paper_info']]:
            if paper['title'] not in paper_dict:
                paper_dict[paper['title']] = paper

        feed_data = {
            "date": feed_data_list[0]['date'],
            "paper_info": list(paper_dict.values())
        }

        # splitting the papers into self.num_emails roughly equal parts
        papers = feed_data['paper_info']
        n = len(papers)
        chunk_size = n // self.num_emails

        chunks = [papers[i:i + chunk_size] for i in range(0, n, chunk_size)]

        if len(chunks) > self.num_emails and len(chunks[-1]) < chunk_size:
            chunks[-2].extend(chunks[-1])
            chunks.pop()

        # send each part of the papers
        for i, chunk in enumerate(chunks):
            data_chunk = feed_data.copy()
            data_chunk['paper_info'] = chunk

            html_str = self.render_html(data_chunk, i+1)

            params = {
                "from": "Arxiv Daily <arxiv_daily@updates.jiayipan.me>",
                "to": self.subs,
                "subject": f"Arxiv Papers at {feed_data['date']} - Part {i+1}",
                "html": html_str,
            }

            email = self.resend.Emails.send(params)

def main():
    sub_urls = [f'http://export.arxiv.org/rss/{domain}' for domain in domains]
    arxiv = ArxivDigest(sub_urls, resend_key, subscribers, num_emails)
    arxiv.send_emails()

if __name__ == "__main__":
    main()